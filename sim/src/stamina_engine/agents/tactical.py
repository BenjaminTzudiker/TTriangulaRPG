"""Tactical agent v1 (ENGINE_PLAN agent family 3): a grid-aware utility agent for melee.

It is built from small scorers in agents/grid_view.py:
- engagers: how many enemies could attack a square next turn;
- exposure: avoidance or OA cost along a path;
- oa_value: what an enemy's OA would cost it (block stamina + w x injury, exact).

What it does:
- **Its turn.** Pick a target with the target policy. Among the squares it can attack that
  target from, reachable this turn (free movement, plus purchases if enough stamina is left
  for its commitment), it takes the one with the fewest engagers, then the least exposure,
  then the shortest path, and attacks with its commitment policy. If it can't reach the
  target this turn, it approaches with free movement to the square that gets closest, again
  preferring fewer engagers.
- **After attacking.** With free movement left: a reach weapon steps back out of the target's
  reach while keeping it in its own (reach spacing); otherwise, if two or more enemies could
  engage it, it steps to a square with fewer, if that costs no avoidance.
- **Off-turn windows.** It retreats when at least `retreat_engaged` enemies could engage it,
  or when it is engaged at all with stamina below `low_stamina` of its maximum: to the
  affordable square with the fewest engagers, if that is strictly fewer and costs at most
  half its stamina. It never moves off-turn otherwise.
- **Avoidance.** It pays off an enemy when that enemy could make an OA and the OA's expected
  cost to it is more than the price.
- **Opportunity attacks.** It takes the largest one that fits.

Weights are data in the agent spec, which is the hook M4's NPC profiles fill.

For testing 0.10.0's ranged rules (opt-in spec fields; Assumptions register):
- buy = never | keep_steps | any (default any): buying squares to attack this turn;
- close = off_turn: buying off-turn squares, just before its turn, to attack on it;
- reaction = position, approach_weight: a reaction to a shot values where it ends;
- aim = reaction: an archer's aim counts the target's best reaction to each roll.
"""

from collections.abc import Callable
from dataclasses import dataclass, field, replace
from fractions import Fraction

from stamina_engine.agents.ability_policy import AbilityPolicy, is_riposte
from stamina_engine.agents.blocking import solver_blocks
from stamina_engine.agents.decisions import (
    AbilityRequest,
    AimRequest,
    Attack,
    Avoid,
    AvoidOA,
    BlocksRequest,
    CombatantView,
    Commitment,
    DiveRequest,
    Draw,
    EndTurn,
    Flee,
    Move,
    MoveAnswer,
    MoveOptions,
    OATake,
    Observation,
    OffTurnMove,
    Pass,
    Shoot,
    Surrender,
    TakeOA,
    TurnAnswer,
    TurnCommand,
    UseAbility,
)
from stamina_engine.agents.estimates import Target, exact_estimate
from stamina_engine.agents.grid_view import (
    Board,
    attack_squares,
    block_score,
    is_shooter,
    ranged_loadout,
    shot_value,
)
from stamina_engine.agents.objective_play import (
    Goal,
    closer_free,
    denier_order,
    goal,
    in_goal,
)
from stamina_engine.agents.scripted import BUY_MODES, CommitPolicy, avoid_worth_it, buys, sized_oa
from stamina_engine.analysis.ranged import shot
from stamina_engine.core.errors import ConfigError
from stamina_engine.grid.battlefield import Cell
from stamina_engine.grid.geometry import distance, reach_cells
from stamina_engine.grid.los import Cover, cover
from stamina_engine.grid.pathing import Passage, reachable
from stamina_engine.grid.threat import body, melee_weapons, threatened_by
from stamina_engine.rules.block_solver import block_frontier
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Positioning",
    "Packet: On-Turn Movement",
    "Packet: Off-Turn Movement",
    "Review F6",
)

TARGET_MODES = frozenset({"lowest_stamina", "nearest", "first", "focus"})
REACTION_MODES = frozenset({"shot", "position"})
AIM_MODES = frozenset({"stays", "reaction"})
CLOSE_MODES = frozenset({"none", "off_turn"})


@dataclass
class TacticalAgent:
    rules: RuleSet
    commit: CommitPolicy
    target_mode: str = "lowest_stamina"
    w: Fraction = Fraction(3)
    retreat_engaged: int = 2
    low_stamina: Fraction = Fraction(1, 3)
    reach_spacing: bool = True
    flee_below: Fraction = Fraction(0)  # at or below this fraction of max HP, head for an exit
    surrender_below: Fraction = Fraction(0)  # ...and surrender when engaged (0: never)
    abilities: AbilityPolicy | None = None  # None: pass every ability window
    objective: str = "kill"  # or "first" (agents/objective_play.py)
    buy: str = "any"  # buying on-turn squares to reach its target (scripted.buys)
    reaction: str = "shot"  # or "position": a reaction also values where it ends
    approach_weight: Fraction = Fraction(0)  # reaction = position: per square closed
    aim_mode: str = "stays"  # or "reaction": an archer weighs the target's best reaction
    close: str = "none"  # or "off_turn": buy off-turn squares to attack on its next turn
    _pending: int = field(default=0, init=False)
    _plan: tuple[int, str] = field(default=(-1, ""), init=False)  # (round, stage) this turn

    def __post_init__(self) -> None:
        if self.target_mode not in TARGET_MODES:
            raise ConfigError(f"tactical target must be one of {sorted(TARGET_MODES)}")
        for name, value, modes in (
            ("buy", self.buy, BUY_MODES),
            ("reaction", self.reaction, REACTION_MODES),
            ("aim", self.aim_mode, AIM_MODES),
            ("close", self.close, CLOSE_MODES),
        ):
            if value not in modes:
                raise ConfigError(f"tactical {name} must be one of {sorted(modes)}, not {value!r}")
        self.pricing = Pricing(self.rules)

    # --- helpers ---------------------------------------------------------------------

    def _target(self, board: Board) -> str | None:
        enemies = board.enemies()
        if not enemies:
            return None
        g = goal(board.obs) if self.objective == "first" else None
        if g is not None and not g.pursue:  # a denier: the pursuer closest to its goal
            return denier_order(board.obs, self.rules, g, tuple(v.id for v in enemies))[0]
        me = board.me
        assert me.pos is not None
        if self.target_mode == "nearest":
            return min(enemies, key=lambda v: distance(me.pos, v.pos, self.rules.grid)).id  # type: ignore[arg-type]
        if self.target_mode == "first":
            return enemies[0].id
        if self.target_mode == "focus":
            return min(enemies, key=lambda v: (-self._allies_on(board, v), v.stamina, v.hp)).id
        return min(enemies, key=lambda v: (v.stamina, v.hp)).id

    def _allies_on(self, board: Board, enemy: CombatantView) -> int:
        """How many of my allies threaten this enemy's square (focus fire)."""
        if enemy.pos is None:
            return 0
        me = board.me
        count = 0
        for v in board.obs.others:
            if v.team != me.team or v.status != "active" or v.pos is None:
                continue
            for w in (v.gear.weapon, v.gear.off_hand_weapon):
                if (
                    w is not None
                    and not w.ranged
                    and enemy.pos in reach_cells(board.field, v.pos, w.reach, self.rules.grid)
                ):
                    count += 1
                    break
        return count

    def _leaving(self, board: Board, request: TurnCommand) -> TurnAnswer | None:
        """Surrender or flee when hurt past the profile's thresholds (never by default)."""
        me = board.me
        assert me.pos is not None
        top = max(1, me.profile.hp_max)
        hurt = bool(self.surrender_below) and me.hp <= self.surrender_below * top
        if hurt and request.can_surrender and board.engagers(me.pos) > 0:
            return Surrender()
        if self.flee_below and me.hp <= self.flee_below * top:
            if request.can_flee:
                return Flee()
            exits = board.field.exits()
            if exits and request.moves is not None:
                route = board.route(request.moves, list(exits), request.moves.max_squares)
                if route is not None and int(route.total) <= me.stamina:
                    return Move(route.path)
                here = me.pos
                nearest = min(exits, key=lambda e: distance(here, e, self.rules.grid))
                step = self._approach(board, nearest, request.moves)
                if step is not None:
                    return step
        return None

    def _steps_with(self, obs: Observation, target: str, spend: int) -> int:
        """The commitment if `spend` stamina goes on movement first."""
        me = replace(obs.me, stamina=obs.me.stamina - spend)
        return self.commit.steps(me, obs.view(target))

    # --- its turn --------------------------------------------------------------------

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        obs = request.observation
        if self.abilities is not None and request.abilities:
            use = self.abilities.on_turn(obs, request.abilities)
            if use is not None:
                return use
        if obs.field is None:  # the all-adjacent arena: attack, as a scripted agent would
            return self._attack_in_place(request)
        board = Board(obs, self.rules)
        me = obs.me
        assert me.trackers is not None and me.pos is not None
        stage = self._plan[1] if self._plan[0] == obs.round else ""
        leaving = self._leaving(board, request)
        if leaving is not None:
            return leaving
        g = goal(obs) if self.objective == "first" else None
        if g is not None and g.pursue and g.counts:
            return self._pursue(board, request, g, stage)
        if is_shooter(me):
            return self._archer_turn(board, request, stage)
        if me.trackers.actions_this_turn > 0:
            if stage != "after" and request.moves is not None:
                self._plan = (obs.round, "after")
                step = self._contest(board, request.moves, g) or self._after_attack(
                    board, request.moves
                )
                if step is not None:
                    return step
            return EndTurn()
        tid = self._target(board)
        if tid is None:
            return EndTurn()
        if tid in request.targets and stage == "moved":
            return self._attack(obs, tid, request)
        if stage == "":
            self._plan = (obs.round, "moved")
            step = self._move_to_attack(board, tid, request)
            if step is not None:
                return step
        if tid in request.targets:
            return self._attack(obs, tid, request)
        if request.targets:  # the chosen target is out of reach but another isn't
            return self._attack(obs, request.targets[0], request)
        if stage != "after" and request.moves is not None:
            self._plan = (obs.round, "after")
            step = self._contest(board, request.moves, g)
            if step is not None:
                return step
        return EndTurn()

    # --- objectives (agents/objective_play.py) -------------------------------------------

    def _pursue(self, board: Board, request: TurnCommand, g: Goal, stage: str) -> TurnAnswer:
        """Head for the goal (buying movement up to half its stamina), flee from an exit when
        escaping, hold the zone once in it, and attack or shoot only what is in reach."""
        obs, me = board.obs, board.me
        assert me.trackers is not None
        if g.view.kind == "escape" and request.can_flee:
            return Flee()
        if me.trackers.actions_this_turn > 0 or stage == "shot":
            return EndTurn()
        holding = g.view.kind == "hold" and in_goal(obs, g)
        if stage == "" and request.moves is not None and not holding:
            self._plan = (obs.round, "moved")
            step = self._toward(board, request.moves, g)
            if step is not None:
                return step
        if request.shots:
            tid = self._target_of(board, request.shots)
            if tid is not None:
                self._plan = (obs.round, "shot")
                return Shoot(tid)
        if request.targets:
            pick = self._target(board)
            tid = pick if pick in request.targets else request.targets[0]
            return self._attack(obs, tid, request)
        return EndTurn()

    def _toward(self, board: Board, moves: MoveOptions, g: Goal) -> Move | None:
        me = board.me
        goals = [c for c in g.cells if c in moves.destinations]
        route = board.route(moves, goals, moves.max_squares) if goals else None
        if route is not None and route.path and route.total <= Fraction(me.stamina, 2):
            return Move(route.path)
        cell = closer_free(board.obs, self.rules, moves, g.cells)
        if cell is None:
            return None
        free = (me.free_move_left or 0) + (me.banked or 0)
        route = board.route(moves, [cell], free)
        return Move(route.path) if route is not None and route.path else None

    def _contest(self, board: Board, moves: MoveOptions, g: Goal | None) -> Move | None:
        """A denier in a contested hold steps into the zone when free movement gets it there
        without provoking anyone."""
        if g is None or g.pursue or g.view.kind != "hold" or g.view.control == "present":
            return None
        if in_goal(board.obs, g):
            return None
        me = board.me
        free = (me.free_move_left or 0) + (me.banked or 0)
        goals = [c for c in g.cells if moves.destinations.get(c, free + 1) <= free]
        route = board.route(moves, goals, free) if goals else None
        if route is None or not route.path or route.exposure:
            return None
        return Move(route.path)

    # --- shooters ----------------------------------------------------------------------

    def _archer_turn(self, board: Board, request: TurnCommand, stage: str) -> TurnAnswer:
        """Ready the bow (free before using a weapon), step out of reach if it can still shoot
        from there, shoot once, then step away with what free movement is left."""
        obs, me = board.obs, board.me
        assert me.pos is not None
        bow = ranged_loadout(me)
        weapon = me.gear.weapon
        holding_bow = weapon is not None and weapon.ranged
        if stage == "shot":
            if request.moves is not None:
                self._plan = (obs.round, "done")
                step = self._kite(board, request.moves, None)
                if step is not None:
                    return step
            return EndTurn()
        if stage == "done":
            return EndTurn()
        if not holding_bow:
            free_bow = [d for d in request.draws if d.loadout == bow and d.quote.total == 0]
            bow_weapon = me.profile.loadout(bow).weapon if bow is not None else None
            shot_base = bow_weapon.base if bow_weapon is not None else 0
            if free_bow and me.stamina >= shot_base:
                return Draw(free_bow[0].loadout)
            if request.targets and me.trackers is not None and not me.trackers.actions_this_turn:
                return self._attack(obs, request.targets[0], request)  # fight with the blade
            return EndTurn()
        shots = request.shots
        exposed = board.engagers(me.pos) > 0 or bool(board.threatening(me.pos))
        if stage == "" and request.moves is not None and exposed:
            self._plan = (obs.round, "kited")
            step = self._kite(board, request.moves, self._target_of(board, shots))
            if step is not None:
                return step
        tid = self._target_of(board, shots)
        if tid is None:
            if stage == "" and request.moves is not None:
                self._plan = (obs.round, "kited")
                enemy = self._target(board)
                goal = obs.view(enemy).pos if enemy is not None else None
                step = self._approach(board, goal, request.moves)
                if step is not None:
                    return step
            return EndTurn()
        self._plan = (obs.round, "shot")
        return Shoot(tid)

    def _target_of(self, board: Board, shots: tuple[str, ...]) -> str | None:
        if not shots:
            return None
        views = [board.obs.view(t) for t in shots]
        if self.target_mode == "nearest" and board.me.pos is not None:
            here = board.me.pos
            return min(views, key=lambda v: distance(here, v.pos, self.rules.grid)).id  # type: ignore[arg-type]
        if self.target_mode == "first":
            return views[0].id
        return min(views, key=lambda v: (v.stamina, v.hp)).id

    def _kite(self, board: Board, moves: MoveOptions, keep: str | None) -> Move | None:
        """Free movement only, at most 3 stamina in avoidance: out of every enemy's reach now
        (so a shot doesn't provoke, and is blocked with Ranged Defense), or to a square fewer
        enemies could engage next turn; keeping a shot at `keep` if given. Fewest engagers,
        then least exposure to shooters, then cheapest."""
        me = board.me
        assert me.pos is not None
        free = (me.free_move_left or 0) + (me.banked or 0)
        if free <= 0:
            return None
        weapon = me.gear.weapon
        now = board.engagers(me.pos)
        threatened_now = bool(board.threatening(me.pos))
        routes = board.routes(moves, free)
        best: tuple[tuple[bool, int, int, int, int], tuple[Cell, ...]] | None = None
        for c, route in routes.items():
            if route.total > 3:
                continue
            if keep is not None and weapon is not None:
                there = board.obs.view(keep).pos
                assert there is not None
                band = self.rules.ranged.band(
                    distance(c, there, self.rules.grid), weapon.ranges, weapon.band_width
                )
                if band == "beyond" or board.cover_at(c, there, (keep, me.id)) >= Cover.TOTAL:
                    continue
            threatened = bool(board.threatening(c))
            e = board.engagers(c, moved=True)
            if not (e < now or (threatened_now and not threatened)):
                continue
            key = (threatened, e, board.shot_exposure(c), int(route.total), len(route.path))
            if best is None or key < best[0]:
                best = (key, route.path)
        return Move(best[1]) if best is not None else None

    def _attack_in_place(self, request: TurnCommand) -> TurnAnswer:
        obs = request.observation
        assert obs.me.trackers is not None
        if obs.me.trackers.actions_this_turn > 0 or not request.targets:
            return EndTurn()
        return self._attack(
            obs, min(request.targets, key=lambda t: (obs.view(t).stamina, obs.view(t).hp)), request
        )

    def _attack(self, obs: Observation, tid: str, request: TurnCommand) -> TurnAnswer:
        steps = self.commit.steps(obs.me, obs.view(tid))
        if steps <= 0 or tid not in request.targets:
            return EndTurn()
        self._pending = steps
        return Attack(tid)

    def _move_to_attack(self, board: Board, tid: str, request: TurnCommand) -> Move | None:
        moves = request.moves
        me, target = board.me, board.obs.view(tid)
        weapon = me.gear.weapon
        if weapon is None or weapon.ranged or target.pos is None or me.pos is None:
            return None
        spots = attack_squares(board.field, self.rules, weapon.reach, target.pos)
        here = me.pos in spots
        best: tuple[tuple[int, Fraction | int, int], Cell | None, tuple[Cell, ...]] | None = None
        if here:
            best = ((board.engagers(me.pos), 0, 0), None, ())
        if moves is not None:
            for s in sorted(spots & set(moves.destinations)):
                route = board.route(moves, [s], moves.max_squares)
                if route is None:
                    continue
                price = moves.price_by_length[len(route.path)]
                spend = int(price) + int(route.exposure)
                after = self._steps_with(board.obs, tid, spend)
                if after <= 0:
                    continue
                if spend > 0 and not buys(self.buy, self._steps_with(board.obs, tid, 0), after):
                    continue
                key = (board.engagers(s, moved=True), route.exposure + price, len(route.path))
                if best is None or key < best[0]:
                    best = (key, s, route.path)
        if best is not None:
            return Move(best[2]) if best[2] else None
        return self._approach(board, target.pos, moves)

    def _approach(self, board: Board, goal: Cell | None, moves: MoveOptions | None) -> Move | None:
        """Free movement only, to the reachable square closest to goal."""
        me = board.me
        if moves is None or goal is None or me.pos is None:
            return None
        free = (me.free_move_left or 0) + (me.banked or 0)
        now = distance(me.pos, goal, self.rules.grid)
        options = [c for c, n in moves.destinations.items() if n <= free]
        if not options:
            return None
        closest = min(distance(c, goal, self.rules.grid) for c in options)
        nearest = [c for c in options if distance(c, goal, self.rules.grid) == closest]
        pick = min(
            nearest, key=lambda c: (board.shot_exposure(c), board.engagers(c, moved=True), c)
        )
        if distance(pick, goal, self.rules.grid) >= now:
            return None
        route = board.route(moves, [pick], free)
        return Move(route.path) if route is not None else None

    def _after_attack(self, board: Board, moves: MoveOptions) -> Move | None:
        me = board.me
        assert me.pos is not None
        free = (me.free_move_left or 0) + (me.banked or 0)
        if free <= 0:
            return None
        options = [c for c, n in moves.destinations.items() if n <= free]
        weapon = me.gear.weapon
        if self.reach_spacing and weapon is not None and not weapon.ranged and weapon.reach > 1:
            enemies = board.enemies()
            near = [
                e
                for e in enemies
                if e.pos is not None and distance(me.pos, e.pos, self.rules.grid) <= weapon.reach
            ]
            if near:
                foe = near[0]
                assert foe.pos is not None
                theirs = max(
                    (
                        w.reach
                        for w in (foe.gear.weapon, foe.gear.off_hand_weapon)
                        if w is not None and not w.ranged
                    ),
                    default=0,
                )
                d = distance(me.pos, foe.pos, self.rules.grid)
                if d <= theirs:
                    good = [
                        c
                        for c in options
                        if theirs < distance(c, foe.pos, self.rules.grid) <= weapon.reach
                    ]
                    if good:
                        pick = min(
                            good,
                            key=lambda c: (
                                board.engagers(c, moved=True),
                                moves.destinations[c],
                                c,
                            ),
                        )
                        route = board.route(moves, [pick], free)
                        if route is not None:
                            return Move(route.path)
        engaged = board.engagers(me.pos)
        if engaged >= 2:
            better = []
            routes = board.routes(moves, free)
            for c in options:
                route = routes.get(c)
                if route is None or route.exposure != 0:
                    continue
                e = board.engagers(c, moved=True)
                if e < engaged:
                    better.append(((e, len(route.path), c), route))
            if better:
                return Move(min(better, key=lambda b: b[0])[1].path)
        return None

    def commitment(self, request: Commitment) -> int:
        if not 0 < self._pending <= request.max_steps:
            self._pending = min(max(self._pending, 1), request.max_steps)
        return self._pending

    def blocks(self, request: BlocksRequest) -> Blocks:
        return solver_blocks(request, self.rules, self.w)

    # --- off its turn ----------------------------------------------------------------

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer:
        obs = request.observation
        board = Board(obs, self.rules)
        me = obs.me
        assert me.pos is not None
        engaged = board.engagers(me.pos)
        low = me.stamina < self.low_stamina * me.max_stamina
        blade = self._blade(request)
        if engaged < self.retreat_engaged and not (engaged >= 1 and low):
            if engaged == 0 and self.close == "off_turn" and request.moves is not None:
                step = self._close_in(board, request.context, request.moves)
                if step is not None:
                    return step
            return blade if engaged >= 1 and blade is not None else Pass()
        moves = request.moves
        if moves is None:
            return blade if blade is not None else Pass()
        g = goal(obs) if self.objective == "first" else None
        hold = g is not None and g.pursue and g.counts and g.view.kind == "hold"
        keep = g.cells if g is not None and hold and in_goal(obs, g) else None
        budget = Fraction(me.stamina, 2)
        best: tuple[tuple[int, Fraction | int, int], tuple[Cell, ...]] | None = None
        routes = board.routes(moves, moves.max_squares)
        for c in sorted(moves.destinations):
            route = routes.get(c)
            if route is None or route.total > budget or (keep is not None and c not in keep):
                continue
            e = board.engagers(c, moved=True)
            if e >= engaged:
                continue
            key = (e, route.total, len(route.path))
            if best is None or key < best[0]:
                best = (key, route.path)
        if best is not None:
            return Move(best[1])
        return blade if blade is not None else Pass()

    def _close_in(self, board: Board, context: tuple[str, ...], moves: MoveOptions) -> Move | None:
        """close = off_turn: in the window just before its own turn, if it couldn't reach a
        square to attack its target from with its next turn's free movement, buy off-turn
        squares to one from which it could, the cheapest (stamina plus 1 per threatening
        enemy on each square left), if the attack it would then make passes `buys` (the
        stamina is spent before its turn, and recovery comes after)."""
        obs, me = board.obs, board.me
        weapon = me.gear.weapon
        if weapon is None or weapon.ranged or is_shooter(me) or me.pos is None:
            return None
        if not _mine_next(obs, context):
            return None
        tid = self._target(board)
        if tid is None:
            return None
        target = obs.view(tid)
        if target.pos is None:
            return None
        spots = attack_squares(board.field, self.rules, weapon.reach, target.pos)

        def can_attack_from(cell: Cell) -> bool:
            if cell in spots:
                return True
            bodies = tuple(replace(b, pos=cell) if b.id == me.id else b for b in board.bodies)
            passage = Passage.for_mover(self.rules.grid, me.id, me.team, bodies)
            reach = reachable(board.field, self.rules.grid, cell, passage, me.gear.movement)
            return any(s in reach.steps and s not in reach.passage.no_stop for s in spots)

        if can_attack_from(me.pos):
            return None
        full = self._steps_with(obs, tid, 0)
        routes = board.routes(moves, moves.max_squares)
        for cell, route in sorted(
            routes.items(), key=lambda kv: (kv[1].total, len(kv[1].path), kv[0])
        ):
            if cell not in moves.destinations or not route.path:
                continue
            after = self._steps_with(obs, tid, int(route.total))
            if not buys(self.buy, full, after):
                continue
            far = distance(cell, target.pos, self.rules.grid) > me.gear.movement + weapon.reach
            if not far and can_attack_from(cell):
                return Move(route.path)
        return None

    def _blade(self, request: OffTurnMove) -> Draw | None:
        """A shooter holding its bow readies a free melee loadout (a quick-draw blade)."""
        weapon = request.observation.me.gear.weapon
        if weapon is None or not weapon.ranged:
            return None
        for d in request.draws:
            lo = request.observation.me.profile.loadout(d.loadout)
            if d.quote.total == 0 and lo.weapon is not None and not lo.weapon.ranged:
                return Draw(d.loadout)
        return None

    def avoid(self, request: AvoidOA) -> Avoid:
        return avoid_worth_it(request, self.rules, self.w)

    def take_oa(self, request: TakeOA) -> OATake:
        if self.abilities is None and is_riposte(request.context):
            return OATake()
        return sized_oa(request, self.commit)

    def aim(self, request: AimRequest) -> int:
        """The aim count with the best expected value, exactly: w x injury + the stamina the
        target spends + 10w x P(down), minus the shot's cost (a miss is all cost)."""
        obs = request.observation
        me, target = obs.me, obs.view(request.target)
        weapon = me.gear.weapon
        assert weapon is not None
        if self.aim_mode == "reaction" and obs.field is not None and target.pos is not None:
            return self._aim_against_reaction(request, Board(obs, self.rules), target)
        defense = target.gear.ranged_defense
        if obs.field is not None and me.pos is not None and target.pos is not None:
            reach = threatened_by(
                obs.field,
                self.rules.grid,
                body(target.id, target.team, target.pos, target.gear, True),
            )
            if me.pos in reach:
                defense = target.gear.melee_defense
        defense += self.rules.ranged.cover_bonus(request.cover)
        reply = self._reply_cost(obs) if obs.field is not None else None
        best = (Fraction(-(10**9)), 0)
        for k, quote in enumerate(request.quotes):
            value = Fraction(-quote.total)
            if reply is not None:
                value -= reply(me.stamina - quote.total)
            if k >= request.required:
                inj, drained, down = shot_value(
                    weapon,
                    k,
                    me.gear.attributes.FIN,
                    request.band,
                    defense,
                    target.gear.armor,
                    max(0, target.stamina),
                    target.hp,
                    self.rules,
                    self.w,
                    request.penalty,
                )
                value += self.w * inj + drained + 10 * self.w * down
            if value > best[0]:
                best = (value, k)
        return best[1]

    def _reply_cost(self, obs: Observation) -> "Callable[[int], Fraction] | None":
        """One ply, as the review's look-ahead: what the worst enemy reply next turn would
        cost me (w x injury + stamina + 10w x P(down)) if I keep `left` stamina now and
        recover before it. None if no enemy could engage me next turn."""
        board = Board(obs, self.rules)
        me = obs.me
        assert me.pos is not None
        foes = [
            e
            for e in board.enemies()
            if e.gear.weapon is not None
            and not e.gear.weapon.ranged
            and board.free_reach(e).steps.keys() & board.attack_squares_of(e, me.pos)
        ]
        if not foes:
            return None
        md = max(
            (
                lo.melee_defense
                for lo in me.profile.loadouts
                if lo.weapon is None or not lo.weapon.ranged
            ),
            default=me.gear.melee_defense,
        )
        w = self.w

        def cost(left: int) -> Fraction:
            mine = min(me.max_stamina, max(0, left) + me.profile.recovery)
            worst = Fraction(0)
            for e in foes:
                weapon = e.gear.weapon
                assert weapon is not None
                k = min(
                    2,
                    Pricing(self.rules).max_steps(
                        weapon.base, max(0, e.stamina), light=weapon.light
                    ),
                )
                if k == 0:
                    continue
                est = exact_estimate(
                    weapon, k, Target(md, me.gear.armor, mine, me.hp), self.rules, w
                )
                worst = max(
                    worst,
                    w * Fraction(est.injury) + Fraction(est.cost) + 10 * w * Fraction(est.p_down),
                )
            return worst

        return cost

    def _place_value(self, board: Board, shooter: CombatantView) -> Callable[[Cell], Fraction]:
        """reaction = position: what ending a reaction on a square is worth, beyond this
        shot's blocks, in stamina.
        - Contact: if its ready melee weapons would reach the shooter from there, the
          shooter's cheapest answer on its next turn (one reply): pay to leave its reach
          (avoidance, 1 a square as written), or stay and take its opportunity attack by
          shooting point blank, worth what that attack costs the shooter (block stamina +
          w x injury, exact, at up to 2 steps).
        - Approach: approach_weight per square closer to the shooter (Chebyshev), for a
          creature with no bow; 0 by default, a sensitivity knob."""
        me = board.me
        weapons = melee_weapons(me.gear)
        w = self.w
        contact = Fraction(0)
        if weapons and shooter.pos is not None:
            weapon = max(weapons, key=lambda x: x.base)
            fee = Fraction(self.pricing.avoid_opportunity(1).total)
            k = min(2, self.pricing.max_steps(weapon.base, max(0, me.stamina), light=weapon.light))
            oa = Fraction(10**9)
            if k > 0:
                est = exact_estimate(
                    weapon,
                    k,
                    Target(
                        shooter.gear.melee_defense,
                        shooter.gear.armor,
                        max(0, shooter.stamina),
                        shooter.hp,
                    ),
                    self.rules,
                    w,
                )
                oa = Fraction(est.cost) + w * Fraction(est.injury)
            contact = min(fee, oa)
        weight = self.approach_weight if not is_shooter(me) else Fraction(0)
        assert shooter.pos is not None and me.pos is not None
        start = distance(me.pos, shooter.pos, self.rules.grid)

        def value(cell: Cell) -> Fraction:
            near = contact if shooter.pos in board.attack_spots(cell) else Fraction(0)
            closer = start - distance(cell, shooter.pos, self.rules.grid)  # type: ignore[arg-type]
            return near + weight * closer

        return value

    def _reaction_options(
        self, board: Board, target: CombatantView, request: AimRequest
    ) -> list[tuple[int, int, int]]:
        """aim = reaction: what the target could make the shot face by reacting, as
        (defense with cover, range penalty, stamina it spends), the dominated ones dropped.
        From every square one off-turn move reaches (within any reaction cap), priced as if
        its off-turn track were fresh (the archer can't see it), judged as the engine judges
        the reaction (ranged.range_measured, defense_timing, the reaction bonus, cover from
        a dive). Staying is (its defense now, the penalty now, 0)."""
        me = board.me
        weapon = me.gear.weapon
        assert weapon is not None and me.pos is not None and target.pos is not None
        r = self.rules.ranged
        grid = self.rules.grid
        gear = target.gear

        def melee_from(cell: Cell) -> bool:
            b = body(target.id, target.team, cell, gear, True)
            return me.pos in threatened_by(board.field, grid, b)

        declared = melee_from(target.pos)
        stay_def = (gear.melee_defense if declared else gear.ranged_defense) + r.cover_bonus(
            request.cover
        )
        out = {(stay_def, request.penalty): 0}
        per = max(1, gear.squares_per_purchase)
        cap = r.reaction_purchase_cap()
        area = board.field.width * board.field.height
        prices = self.pricing.move_prices(
            on_turn=False,
            trackers=Trackers(),
            stamina=max(0, target.stamina),
            off_turn_squares=per,
            limit=area if cap is None else min(area, cap * per),
        )
        if len(prices) > 1:
            bodies = tuple(b for b in board.bodies if b.id != target.id)
            passage = Passage.for_mover(grid, target.id, target.team, board.bodies)
            reach = reachable(board.field, grid, target.pos, passage, len(prices) - 1)
            for cell, n in reach.destinations().items():
                others = [b.pos for b in bodies if b.id != me.id]
                level = r.dive_cover(int(cover(board.field, grid, me.pos, cell, others)))
                melee = declared
                if r.defense_after_reaction():
                    now = melee_from(cell)
                    single = -(-n // per) <= 1 or not r.swap_needs_single_purchase()
                    melee = now if (now == declared or single) else declared
                base = gear.melee_defense if melee else gear.ranged_defense + r.reaction_defense()
                d = distance(me.pos, cell, grid)
                pen = (
                    r.range_penalty(d, weapon.band_width)
                    if r.measures_after_reaction()
                    else request.penalty
                )
                key = (base + r.cover_bonus(level), pen)
                if key not in out or prices[n] < out[key]:
                    out[key] = prices[n]
        options = sorted((d, p, c) for (d, p), c in out.items())
        return [
            o
            for o in options
            if not any(q != o and q[0] >= o[0] and q[1] >= o[1] and q[2] <= o[2] for q in options)
        ]

    def _aim_against_reaction(
        self, request: AimRequest, board: Board, target: CombatantView
    ) -> int:
        """aim = reaction: the aim count with the best expected value when the target
        answers each roll with its best reaction (_reaction_options) and blocks, valued as
        aim's (w x injury + stamina it spends, moving included, + 10w x P(down), less the
        shot's cost and the reply look-ahead)."""
        obs, me = request.observation, request.observation.me
        weapon = me.gear.weapon
        assert weapon is not None
        options = self._reaction_options(board, target, request)
        faced = max(0, target.gear.armor - weapon.piercing)
        hp, stamina, w = target.hp, max(0, target.stamina), self.w
        reply = self._reply_cost(obs)
        best = (Fraction(-(10**9)), 0)
        for k, quote in enumerate(request.quotes):
            value = Fraction(-quote.total)
            if reply is not None:
                value -= reply(me.stamina - quote.total)
            if k >= request.required:
                joint = shot(weapon, k, me.gear.attributes.FIN, request.band, self.rules)
                for (total, crits, limit), p in joint.items():
                    pick: tuple[tuple[bool, Fraction, int], Fraction] | None = None
                    for defense, pen, spend in options:
                        if spend > stamina:
                            continue
                        left = max(0, total - pen)
                        for cost, injury in block_frontier(
                            left, crits, defense, faced, stamina - spend, self.rules, True, limit
                        ):
                            down = injury >= hp
                            key = (down, cost + spend + w * injury, cost + spend)
                            got = w * injury + cost + spend + (10 * w if down else 0)
                            if pick is None or key < pick[0]:
                                pick = (key, got)
                    assert pick is not None
                    value += p * pick[1]
            if value > best[0]:
                best = (value, k)
        return best[1]

    def ability(self, request: AbilityRequest) -> UseAbility | Pass:
        if self.abilities is None:
            return Pass()
        return self.abilities.at_window(request, self._pending)

    def dive(self, request: DiveRequest) -> MoveAnswer:
        """React to a shot if blocking its roll from the best reachable square saves more
        than the move costs (its purchases, plus 1 per enemy threatening each square it
        leaves). Under v0.9 the agent looks only at squares with better cover. Where the
        request says what the shot would be from each square (0.10.0: range measured after
        the reaction, Ranged Defense for moving), every square counts: diving for cover,
        closing in to block with Melee Defense, or backing away into a further band. With
        reaction = shot it values only this shot's blocks; with reaction = position it adds
        what the square it ends on is worth (_place_value; Assumptions register)."""
        if self.abilities is not None:
            step = self.abilities.withdrawal_move(request)
            if step is not None:
                return step
        obs = request.observation
        if obs.field is None:
            return Pass()
        board = Board(obs, self.rules)
        me = obs.me
        gear = me.gear
        shooter = obs.view(request.shooter)
        r = self.rules.ranged
        armor = gear.armor if request.armor is None else request.armor
        given = request.defense is not None

        def defense_at(cell: Cell, level: int) -> int:
            assert shooter.pos is not None
            near = shooter.pos in board.attack_spots(cell)
            return (gear.melee_defense if near else gear.ranged_defense) + r.cover_bonus(level)

        def score(damage: int, defense: int, stamina: int) -> Fraction:
            return block_score(
                damage,
                request.crit_dice,
                defense,
                armor,
                stamina,
                me.hp,
                self.rules,
                self.w,
                request.limit,
            )

        assert me.pos is not None
        stay_defense = (
            request.defense if request.defense is not None else defense_at(me.pos, request.cover)
        )
        stay = score(request.damage, stay_defense, me.stamina)
        routes = board.routes(request.moves, request.moves.max_squares)
        place = self._place_value(board, shooter) if self.reaction == "position" else None
        here = place(me.pos) if place is not None else Fraction(0)
        best: tuple[Fraction, tuple[Cell, ...]] | None = None
        for c, level in request.cover_after.items():
            route = routes.get(c)
            if route is None or (not given and place is None and level <= request.cover):
                continue
            spend = route.total
            damage = request.damage_after.get(c, request.damage)
            defense = request.defense_after.get(c, defense_at(c, level))
            there = score(damage, defense, me.stamina - int(spend))
            gain = stay - there - Fraction(spend)
            if place is not None:
                gain += place(c) - here
            if gain > 0 and (best is None or gain > best[0]):
                best = (gain, route.path)
        return Move(best[1]) if best is not None else Pass()


def _mine_next(obs: Observation, context: tuple[str, ...]) -> bool:
    """Is this the off-turn window right before the observer's own turn? The next creature
    in initiative order after the one whose turn just ended, skipping any that can't act."""
    after = [f[len("off-turn after ") :] for f in context if f.startswith("off-turn after ")]
    if not after or after[-1] not in obs.order:
        return False
    order = obs.order
    i = order.index(after[-1])
    for k in range(1, len(order) + 1):
        cid = order[(i + k) % len(order)]
        if cid == obs.me.id:
            return True
        if obs.view(cid).status == "active":
            return False
    return False
