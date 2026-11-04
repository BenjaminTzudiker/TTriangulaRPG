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

Weights are data in the agent spec, which is the hook M4's NPC profiles fill. Cover seeking
and diving wait for ranged attacks (M3).
"""

from collections.abc import Callable
from dataclasses import dataclass, field, replace
from fractions import Fraction

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
from stamina_engine.agents.scripted import CommitPolicy, avoid_worth_it, largest_oa
from stamina_engine.core.errors import ConfigError
from stamina_engine.grid.battlefield import Cell
from stamina_engine.grid.geometry import distance, reach_cells
from stamina_engine.grid.los import Cover
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Positioning",
    "Packet: On-Turn Movement",
    "Packet: Off-Turn Movement",
    "Review F6",
)

TARGET_MODES = frozenset({"lowest_stamina", "nearest", "first", "focus"})


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
    _pending: int = field(default=0, init=False)
    _plan: tuple[int, str] = field(default=(-1, ""), init=False)  # (round, stage) this turn

    def __post_init__(self) -> None:
        if self.target_mode not in TARGET_MODES:
            raise ConfigError(f"tactical target must be one of {sorted(TARGET_MODES)}")
        self.pricing = Pricing(self.rules)

    # --- helpers ---------------------------------------------------------------------

    def _target(self, board: Board) -> str | None:
        enemies = board.enemies()
        if not enemies:
            return None
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
        if obs.field is None:  # the all-adjacent arena: attack, as a scripted agent would
            return self._attack_in_place(request)
        board = Board(obs, self.rules)
        me = obs.me
        assert me.trackers is not None and me.pos is not None
        stage = self._plan[1] if self._plan[0] == obs.round else ""
        leaving = self._leaving(board, request)
        if leaving is not None:
            return leaving
        if is_shooter(me):
            return self._archer_turn(board, request, stage)
        if me.trackers.actions_this_turn > 0:
            if stage != "after" and request.moves is not None:
                self._plan = (obs.round, "after")
                step = self._after_attack(board, request.moves)
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
        return EndTurn()

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
                band = self.rules.ranged.band(distance(c, there, self.rules.grid), weapon.ranges)
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
                if self._steps_with(board.obs, tid, int(price) + int(route.exposure)) <= 0:
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
            return blade if engaged >= 1 and blade is not None else Pass()
        moves = request.moves
        if moves is None:
            return blade if blade is not None else Pass()
        budget = Fraction(me.stamina, 2)
        best: tuple[tuple[int, Fraction | int, int], tuple[Cell, ...]] | None = None
        routes = board.routes(moves, moves.max_squares)
        for c in sorted(moves.destinations):
            route = routes.get(c)
            if route is None or route.total > budget:
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
        return largest_oa(request)

    def aim(self, request: AimRequest) -> int:
        """The aim count with the best expected value, exactly: w x injury + the stamina the
        target spends + 10w x P(down), minus the shot's cost (a miss is all cost)."""
        obs = request.observation
        me, target = obs.me, obs.view(request.target)
        weapon = me.gear.weapon
        assert weapon is not None
        defense = target.gear.ranged_defense
        if obs.field is not None and me.pos is not None and target.pos is not None:
            from stamina_engine.grid.threat import body, threatened_by

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

    def ability(self, request: AbilityRequest) -> UseAbility | Pass:
        return Pass()

    def dive(self, request: DiveRequest) -> MoveAnswer:
        """Dive if the roll, blocked from the best reachable cover, saves more than the move
        costs (its purchases, plus 1 per enemy threatening each square it leaves)."""
        obs = request.observation
        if obs.field is None:
            return Pass()
        board = Board(obs, self.rules)
        me = obs.me
        gear = me.gear
        shooter = obs.view(request.shooter)
        r = self.rules.ranged

        def defense_at(cell: Cell, level: int) -> int:
            assert shooter.pos is not None
            near = shooter.pos in board.attack_spots(cell)
            return (gear.melee_defense if near else gear.ranged_defense) + r.cover_bonus(level)

        assert me.pos is not None
        stay = block_score(
            request.damage,
            request.crit_dice,
            defense_at(me.pos, request.cover),
            gear.armor,
            me.stamina,
            me.hp,
            self.rules,
            self.w,
        )
        routes = board.routes(request.moves, request.moves.max_squares)
        best: tuple[Fraction, tuple[Cell, ...]] | None = None
        for c, level in request.cover_after.items():
            route = routes.get(c)
            if route is None or level <= request.cover:
                continue
            spend = route.total
            there = block_score(
                request.damage,
                request.crit_dice,
                defense_at(c, level),
                gear.armor,
                me.stamina - int(spend),
                me.hp,
                self.rules,
                self.w,
            )
            gain = stay - there - Fraction(spend)
            if gain > 0 and (best is None or gain > best[0]):
                best = (gain, route.path)
        return Move(best[1]) if best is not None else Pass()
