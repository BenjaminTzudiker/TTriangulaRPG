"""When the engine's agents use abilities: the spec field abilities = "use" turns these on
("none", the default, passes every ability window, so results without abilities stay
comparable). Small, documented heuristics; agent conventions, not rules.

- Fighter core: before blocks, when recovering now lowers what blocking the roll costs
  (stamina + w x injury, overage included) by at least w (one HP's worth); on its own turn,
  before attacking, when it can't afford two attack steps. Never in an off-turn window:
  before blocks it sees the roll, so recovering earlier is dominated.
- Barbarian core: after attacking, refund the biggest step while the strain stays within
  the maximum (greedy: a single fight starts at 0 strain and nothing else spends it).
- Monk core: flat perfect blocks when that saves at least 2 (stamina + w x injury), within
  the strain maximum.
- Rogue core: between turns, jump in ahead of an active enemy, within the strain maximum. It
  never waits.
- Heavy Swing: against a target with armor 2 or more, if the planned steps still fit.
- Tactical Withdrawal: when blocking the roll would cost more than its 2 stamina plus the
  OAs it risks, and a square one off-turn purchase away is out of the attacker's reach.
  The move then goes to the cheapest such square.
- Riposte isn't a window: it's offered as an opportunity attack (TakeOA). With abilities
  on, the agent's oa policy answers it; with them off, it declines.
"""

from dataclasses import dataclass
from fractions import Fraction
from functools import cached_property

from stamina_engine.agents.decisions import (
    AbilityOption,
    AbilityRequest,
    DiveRequest,
    Move,
    Observation,
    Pass,
    UseAbility,
)
from stamina_engine.agents.grid_view import Board
from stamina_engine.core.errors import ConfigError, Unaffordable
from stamina_engine.grid.battlefield import Cell
from stamina_engine.grid.geometry import reach_cells
from stamina_engine.grid.pathing import Passage, reachable
from stamina_engine.grid.threat import melee_weapons
from stamina_engine.rules.block_solver import best_block
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Core Abilities",
    "Packet: Candidate Abilities",
    "Packet: Strain",
    "Packet: Going Over Your Maximum Strain",
)

MODES = frozenset({"none", "use"})


def _strain_now(obs: Observation) -> int:
    return obs.me.trackers.strain if obs.me.trackers is not None else 0


def fits(obs: Observation, option: AbilityOption) -> bool:
    """Using it keeps the strain within the maximum (no overage)."""
    return _strain_now(obs) + option.strain <= obs.me.profile.strain_max


@dataclass(frozen=True)
class AbilityPolicy:
    rules: RuleSet
    w: Fraction

    @cached_property
    def pricing(self) -> Pricing:
        return Pricing(self.rules)

    # --- windows ---------------------------------------------------------------------

    def at_window(self, request: AbilityRequest, pending: int = 0) -> UseAbility | Pass:
        """pending: the attack steps the agent plans (for Heavy Swing's check)."""
        for option in request.options:
            if self._wants(request, option, pending):
                return UseAbility(option.name)
        return Pass()

    def _wants(self, request: AbilityRequest, option: AbilityOption, pending: int) -> bool:
        window, name = request.window, option.name
        if window == "before_blocks" and name == "fighter_core":
            return self._fighter_blocks(request, option)
        if window == "before_blocks" and name == "monk_core":
            return fits(request.observation, option) and self._monk(request, option)
        if window == "between_turns" and name == "rogue_core":
            return fits(request.observation, option) and self._rogue(request)
        if window == "declare_attack" and name == "heavy_swing":
            return self._heavy_swing(request, option, pending)
        if window == "reactions" and name == "tactical_withdrawal":
            return self._withdraw(request, option)
        return False

    def _score(self, request: AbilityRequest, stamina: int, flat: bool = False) -> Fraction:
        """Blocking the roll in the request: stamina + w x injury, plus a big penalty for
        going down (as the block solver ranks it)."""
        me, facts = request.observation.me, request.facts
        choice = best_block(
            int(facts.get("damage", 0)),
            int(facts.get("crit_dice", 0)),
            int(facts.get("defense", me.gear.melee_defense)),
            me.gear.armor,
            max(stamina, 0),
            me.hp,
            self.rules,
            self.w,
            0,
            bool(facts.get("ranged", 0)),
            flat,
        )
        return choice.score + (100 * self.w if choice.incapacitated else 0)

    def _fighter_blocks(self, request: AbilityRequest, option: AbilityOption) -> bool:
        me = request.observation.me
        gain = min(me.profile.recovery, me.max_stamina - me.stamina)
        now = self._score(request, me.stamina)
        after = self._score(request, me.stamina - option.quote.total + gain)
        return now - after >= self.w

    def _monk(self, request: AbilityRequest, option: AbilityOption) -> bool:
        me = request.observation.me
        now = self._score(request, me.stamina)
        flat = self._score(request, me.stamina - option.quote.total, flat=True)
        return now - flat >= 2

    def _rogue(self, request: AbilityRequest) -> bool:
        nxt = str(request.facts.get("next", ""))
        if not nxt:
            return False
        v = request.observation.view(nxt)
        return v.team != request.observation.me.team and v.status == "active"

    def _heavy_swing(self, request: AbilityRequest, option: AbilityOption, pending: int) -> bool:
        obs = request.observation
        target = obs.view(str(request.facts.get("target", "")))
        weapon = obs.me.gear.weapon
        if target.gear.armor < 2 or weapon is None or obs.me.trackers is None:
            return False
        steps = max(pending, 1)
        try:
            self.pricing.melee_attack(
                weapon.base,
                steps,
                obs.me.trackers,
                obs.me.stamina - option.quote.total,
                light=weapon.light,
                extra=1,
            )
        except Unaffordable:
            return False
        return True

    def _withdraw(self, request: AbilityRequest, option: AbilityOption) -> bool:
        obs = request.observation
        me = obs.me
        if obs.field is None or me.pos is None:
            return False
        board = Board(obs, self.rules)
        safe = self._out_of_reach(board, str(request.facts.get("attacker", "")))
        passage = Passage.for_mover(self.rules.grid, me.id, me.team, board.bodies)
        reach = reachable(obs.field, self.rules.grid, me.pos, passage, me.gear.squares_per_purchase)
        if not any(c in safe for c in reach.destinations()):
            return False
        risk = sum(
            (board.oa_value(obs.view(e), me.pos, self.w) for e in board.threatening(me.pos)),
            Fraction(0),
        )
        stay = self._score(request, me.stamina)
        return stay > option.quote.total + risk

    def _out_of_reach(self, board: Board, attacker: str) -> frozenset[Cell]:
        """Squares within one purchase of the observer that the attacker's ready melee
        weapons don't reach."""
        obs = board.obs
        a = obs.view(attacker)
        if a.pos is None or obs.me.pos is None:
            return frozenset()
        threatened: set[Cell] = set()
        for w in melee_weapons(a.gear):
            threatened |= reach_cells(board.field, a.pos, w.reach, self.rules.grid)
        limit = obs.me.gear.squares_per_purchase
        x, y = obs.me.pos
        return frozenset(
            (x + dx, y + dy)
            for dx in range(-limit, limit + 1)
            for dy in range(-limit, limit + 1)
            if (x + dx, y + dy) not in threatened
        )

    # --- its own turn ----------------------------------------------------------------

    def on_turn(self, obs: Observation, options: tuple[AbilityOption, ...]) -> UseAbility | None:
        me = obs.me
        weapon = me.gear.weapon
        acted = me.trackers.actions_this_turn if me.trackers is not None else 0
        for option in options:
            if not fits(obs, option):
                continue
            if option.name == "barbarian_core" and acted > 0:
                return UseAbility(option.name)
            if (
                option.name == "fighter_core"
                and acted == 0
                and weapon is not None
                and not weapon.ranged
                and me.trackers is not None
            ):
                two = self.pricing.max_steps(weapon.base, me.stamina, me.trackers, weapon.light)
                if two < 2:
                    return UseAbility(option.name)
        return None

    # --- Tactical Withdrawal's move --------------------------------------------------

    def withdrawal_move(self, request: DiveRequest) -> Move | Pass | None:
        """The move after paying for Tactical Withdrawal (a DiveRequest from a melee
        attacker): the cheapest square out of its reach. None if the request is a real dive
        (a shot), for the agent's own dive logic."""
        obs = request.observation
        weapon = obs.view(request.shooter).gear.weapon
        if obs.field is None or (weapon is not None and weapon.ranged):
            return None
        board = Board(obs, self.rules)
        safe = self._out_of_reach(board, request.shooter)
        routes = board.routes(request.moves, request.moves.max_squares)
        best: tuple[tuple[Fraction | int, int, Cell], tuple[Cell, ...]] | None = None
        for cell, route in routes.items():
            if cell in safe and cell in request.moves.destinations:
                key = (route.total, len(route.path), cell)
                if best is None or key < best[0]:
                    best = (key, route.path)
        return Move(best[1]) if best is not None else Pass()


def is_riposte(context: tuple[str, ...]) -> bool:
    """An OA request offered by Riposte (the procedure frames it "riposte <id>")."""
    return any(frame.startswith("riposte ") for frame in context)


def make_policy(mode: str, rules: RuleSet, w: Fraction) -> AbilityPolicy | None:
    if mode not in MODES:
        raise ConfigError(f"abilities must be one of {sorted(MODES)}, not {mode!r}")
    return AbilityPolicy(rules, w) if mode == "use" else None
