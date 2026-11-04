"""Scripted agents: the review's five commitment policies, target choices and the block
solver (ENGINE_PLAN, agent family 2). Ported from tests/oracle/sim.py so that, in lockstep
with it, they make the same choices.

Each agent makes at most one attack per turn, as the review's policies did. On a map (M2)
it approaches its target by the cheapest path using free movement only, attacks if it can,
and otherwise stands still; it never moves off-turn. Its avoidance and OA policies are spec
fields: avoid = "worth_it" (pay off an enemy whose OA would cost more than the price),
"always" (pay off every enemy that could make one) or "never"; oa = "max" or "never".
"""

import math
from collections.abc import Callable
from dataclasses import dataclass, field
from fractions import Fraction
from typing import TYPE_CHECKING, Protocol

from stamina_engine.agents.blocking import solver_blocks
from stamina_engine.agents.decisions import (
    Attack,
    Avoid,
    AvoidOA,
    BlocksRequest,
    CombatantView,
    Commitment,
    EndTurn,
    Move,
    MoveAnswer,
    MoveOptions,
    OATake,
    Observation,
    OffTurnMove,
    Pass,
    TakeOA,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.agents.estimates import Estimate, Target, exact_estimate, sampled_estimate
from stamina_engine.agents.grid_view import Board, attack_squares
from stamina_engine.core.dice import DiceSource
from stamina_engine.core.errors import ConfigError
from stamina_engine.grid.geometry import distance
from stamina_engine.rules.block_solver import DEFAULT_W
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.ruleset import RuleSet

if TYPE_CHECKING:
    from stamina_engine.agents.tactical import TacticalAgent

cites = ("Packet: Commitment", "Packet: Melee Attacks", "Review F1", "Review F6")

Number = Fraction | float


class Estimator:
    """Expected outcome of an attack: exact, or sampled like the review's simulator."""

    def __init__(self, rules: RuleSet, mode: str, source: DiceSource | None) -> None:
        if mode not in ("exact", "sampled"):
            raise ConfigError(f"estimator must be exact or sampled, not {mode!r}")
        if mode == "sampled" and source is None:
            raise ConfigError("a sampled estimator needs a dice source")
        self.rules = rules
        self.mode = mode
        self.source = source

    @property
    def sampled(self) -> bool:
        return self.mode == "sampled"

    def estimate(
        self,
        attacker: CombatantView,
        defender: CombatantView,
        steps: int,
        samples: int,
        defender_stamina: int,
        w: Number,
    ) -> Estimate:
        weapon = attacker.gear.weapon
        assert weapon is not None
        target = Target(
            defender.gear.melee_defense, defender.gear.armor, defender_stamina, defender.hp
        )
        if self.mode == "exact":
            return exact_estimate(weapon, steps, target, self.rules, Fraction(w))
        assert self.source is not None
        return sampled_estimate(
            weapon, steps, target, self.rules, Fraction(w), samples, self.source
        )


# --- commitment policies -------------------------------------------------------------


class CommitPolicy(Protocol):
    def steps(self, me: CombatantView, target: CombatantView) -> int: ...


def _max_steps(pricing: Pricing, view: CombatantView, stamina: int) -> int:
    weapon = view.gear.weapon
    if weapon is None or weapon.ranged:
        return 0
    trackers = view.trackers if view.trackers is not None else Trackers()
    return pricing.max_steps(weapon.base, max(stamina, 0), trackers)


@dataclass
class Alpha:
    """Every affordable step."""

    pricing: Pricing

    def steps(self, me: CombatantView, target: CombatantView) -> int:
        return _max_steps(self.pricing, me, me.stamina)


@dataclass
class FixedK:
    """k steps, or as many as are affordable."""

    pricing: Pricing
    k: int

    def steps(self, me: CombatantView, target: CombatantView) -> int:
        return min(self.k, _max_steps(self.pricing, me, me.stamina))


@dataclass
class Reserve:
    """All affordable steps while keeping `keep` stamina back."""

    pricing: Pricing
    keep: int

    def steps(self, me: CombatantView, target: CombatantView) -> int:
        return _max_steps(self.pricing, me, max(0, me.stamina - self.keep))


@dataclass
class ChipKill:
    """2 steps, unless the full strike is expected to take half the target's HP or to put it
    down at least half the time."""

    pricing: Pricing
    estimator: Estimator
    w: Number = 3.0
    samples: int = 40

    def steps(self, me: CombatantView, target: CombatantView) -> int:
        kmax = _max_steps(self.pricing, me, me.stamina)
        if kmax == 0:
            return 0
        e = self.estimator.estimate(me, target, kmax, self.samples, target.stamina, self.w)
        if e.p_down >= 0.5 or e.injury >= target.hp / 2:
            return kmax
        return min(2, kmax)


@dataclass
class LookAhead:
    """One ply: maximize w x expected injury + expected stamina drained + 10w x P(down),
    minus own cost and the worse of the target's best replies (all-in or 2 steps)."""

    pricing: Pricing
    estimator: Estimator
    recovery: Callable[[CombatantView], int]
    w: Number = 3.0
    samples: int = 40
    reply_samples: int = 30

    def steps(self, me: CombatantView, target: CombatantView) -> int:
        w = self.w
        zero: Number = 0.0 if self.estimator.sampled else Fraction(0)
        kmax = _max_steps(self.pricing, me, me.stamina)
        best: tuple[Number, int] = (-1e9, 0)
        my_weapon = me.gear.weapon
        assert my_weapon is not None
        for k in range(0, kmax + 1):
            if k == 0:
                inj = cost = pk = zero
                own = 0
            else:
                e = self.estimator.estimate(me, target, k, self.samples, target.stamina, w)
                inj, cost, pk = e.injury, e.cost, e.p_down
                own = self.pricing.melee_attack(my_weapon.base, k).total
            my_left = min(me.max_stamina, me.stamina - own + self.recovery(me))
            reply_weapon = target.gear.weapon
            opp_k = 0
            if reply_weapon is not None and not reply_weapon.ranged:
                opp_k = self.pricing.max_steps(reply_weapon.base, math.floor(target.stamina - cost))
            exp_inj_me: Number = zero
            if opp_k > 0:
                worst: Number = zero
                # The oracle iterates set([opp_k, min(2, opp_k)]); keep CPython's set order.
                for kk in {opp_k, min(2, opp_k)}:
                    r = self.estimator.estimate(target, me, kk, self.reply_samples, my_left, w)
                    worst = max(worst, r.injury * w + r.cost + (r.p_down * 10 * w))
                exp_inj_me = worst
            score = inj * w + cost + pk * 10 * w - own - exp_inj_me
            if score > best[0]:
                best = (score, k)
        return best[1]


@dataclass
class NeverAttack:
    def steps(self, me: CombatantView, target: CombatantView) -> int:
        return 0


# --- target policies -----------------------------------------------------------------


def first_target(obs: Observation, targets: tuple[str, ...]) -> str | None:
    return targets[0] if targets else None


def lowest_stamina(obs: Observation, targets: tuple[str, ...]) -> str | None:
    """The target with the lowest (stamina, HP); ties go to the first listed."""
    if not targets:
        return None
    return min(targets, key=lambda t: (obs.view(t).stamina, obs.view(t).hp))


TARGETS: dict[str, Callable[[Observation, tuple[str, ...]], str | None]] = {
    "first": first_target,
    "lowest_stamina": lowest_stamina,
}


# --- avoidance and OA policies -------------------------------------------------------


def avoid_choice(request: AvoidOA, rules: RuleSet, w: Fraction, mode: str) -> Avoid:
    """Pay off enemies whose OA is worth avoiding (worth_it), every enemy that could make one
    (always), or nobody (never); then drop the least valuable until it's affordable."""
    if mode == "never" or request.observation.field is None:
        return Avoid()
    board = Board(request.observation, rules)
    pricing = Pricing(rules)
    rule = rules.opportunity
    chosen: list[tuple[Fraction, str, int]] = []
    for enemy, cap in zip(request.enemies, request.caps, strict=True):
        view = request.observation.view(enemy)
        if not board.oa_options(view, request.leaving):
            continue  # it couldn't make an OA anyway
        value = board.oa_value(view, request.leaving, w)
        if mode == "always" or value > rule.avoid_part(cap):
            chosen.append((value, enemy, cap))
    debt = rule.allows_debt()
    while chosen:
        caps = [c for _, e, c in sorted(chosen, key=lambda t: request.enemies.index(t[1]))]
        quote = pricing.avoid_opportunity(
            len(caps), caps=caps, trackers=request.trackers, on_turn=request.on_turn
        )
        if quote.total <= request.stamina or (debt and mode != "never"):
            break
        chosen.remove(min(chosen))
    names = {e for _, e, _ in chosen}
    return Avoid(tuple(e for e in request.enemies if e in names))


def avoid_worth_it(request: AvoidOA, rules: RuleSet, w: Fraction) -> Avoid:
    return avoid_choice(request, rules, w, "worth_it")


def largest_oa(request: TakeOA) -> OATake:
    """The most steps any weapon allows (the main weapon on ties)."""
    best = max(request.options, key=lambda o: len(o.quotes))
    return OATake(best.weapon, len(best.quotes))


def approach(obs: Observation, rules: RuleSet, moves: MoveOptions, target: str) -> Move | None:
    """Toward the target with free movement only: to a square it can attack from if one is
    in reach this turn (least exposure, then shortest), else to the square that gets
    closest. None if it can't get any closer."""
    me = obs.me
    view = obs.view(target)
    weapon = me.gear.weapon
    free = (me.free_move_left or 0) + (me.banked or 0)
    if obs.field is None or free <= 0 or weapon is None or weapon.ranged:
        return None
    if me.pos is None or view.pos is None:
        return None
    board = Board(obs, rules)
    spots = attack_squares(obs.field, rules, weapon.reach, view.pos)
    goals = [c for c in sorted(spots) if moves.destinations.get(c, free + 1) <= free]
    if not goals:
        there = view.pos
        now = distance(me.pos, there, rules.grid)
        options = sorted(c for c, n in moves.destinations.items() if n <= free)
        if not options:
            return None
        pick = min(options, key=lambda c: (distance(c, there, rules.grid), moves.destinations[c]))
        if distance(pick, there, rules.grid) >= now:
            return None
        goals = [pick]
    route = board.route(moves, goals, free)
    return Move(route.path) if route is not None else None


# --- the agent -----------------------------------------------------------------------


@dataclass
class ScriptedAgent:
    rules: RuleSet
    commit: CommitPolicy
    target: Callable[[Observation, tuple[str, ...]], str | None] = first_target
    w: Fraction = DEFAULT_W  # the block agent's value of 1 HP in stamina
    avoid_mode: str = "worth_it"
    oa_mode: str = "max"
    _pending: int = field(default=0, init=False)

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        """The policy is consulted every turn, even when no step is affordable, as the
        review's policies were: its look-ahead samples the target's replies even then."""
        obs = request.observation
        assert obs.me.trackers is not None
        if obs.me.trackers.actions_this_turn > 0:
            return EndTurn()  # one attack per turn
        candidates = request.targets or tuple(v.id for v in obs.enemies() if v.status == "active")
        tid = self.target(obs, candidates)
        if tid is None:
            return EndTurn()
        steps = self.commit.steps(obs.me, obs.view(tid))
        if steps > 0 and tid not in request.targets and request.moves is not None:
            step = approach(obs, self.rules, request.moves, tid)
            if step is not None:
                return step
        if steps <= 0 or tid not in request.targets:
            return EndTurn()
        self._pending = steps
        return Attack(tid)

    def commitment(self, request: Commitment) -> int:
        if not 0 < self._pending <= request.max_steps:
            raise ConfigError(f"policy chose {self._pending} steps of {request.max_steps}")
        return self._pending

    def blocks(self, request: BlocksRequest) -> Blocks:
        return solver_blocks(request, self.rules, self.w)

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer:
        return Pass()  # scripted agents never move off-turn

    def avoid(self, request: AvoidOA) -> Avoid:
        return avoid_choice(request, self.rules, self.w, self.avoid_mode)

    def take_oa(self, request: TakeOA) -> OATake:
        return largest_oa(request) if self.oa_mode == "max" else OATake()


# --- specs ---------------------------------------------------------------------------


AVOID_MODES = frozenset({"worth_it", "always", "never"})
OA_MODES = frozenset({"max", "never"})
SCRIPTED_FIELDS = {"kind", "commit", "target", "w", "estimator", "avoid", "oa"}
TACTICAL_FIELDS = {"retreat_engaged", "low_stamina", "reach_spacing"}


def make_agent(
    spec: str | dict[str, object], rules: RuleSet, source: DiceSource | None = None
) -> "ScriptedAgent | TacticalAgent":
    """Build an agent from a spec: "alpha", "fixed:2", "reserve:5", "chipkill", "lookahead",
    "never", "tactical", or a table {kind = "scripted" | "tactical", commit = "...",
    target = "first" | "lowest_stamina" (tactical: or "nearest"), w = "3",
    estimator = "exact" | "sampled", avoid = "worth_it" | "always" | "never",
    oa = "max" | "never"}; tactical also takes retreat_engaged = 2, low_stamina = "1/3",
    reach_spacing = true."""
    from stamina_engine.agents.tactical import TacticalAgent

    if spec == "tactical":
        spec = {"kind": "tactical"}
    table: dict[str, object] = {"commit": spec} if isinstance(spec, str) else dict(spec)
    kind = str(table.get("kind", "scripted"))
    if kind not in ("scripted", "tactical"):
        raise ConfigError(f"agent kind must be scripted or tactical, not {kind!r}")
    allowed = SCRIPTED_FIELDS | (TACTICAL_FIELDS if kind == "tactical" else set())
    unknown = set(table) - allowed
    if unknown:
        raise ConfigError(f"unknown agent fields {sorted(unknown)}")
    avoid_mode, oa_mode = str(table.get("avoid", "worth_it")), str(table.get("oa", "max"))
    if avoid_mode not in AVOID_MODES or oa_mode not in OA_MODES:
        raise ConfigError(
            f"avoid must be one of {sorted(AVOID_MODES)}, oa one of {sorted(OA_MODES)}"
        )
    commit = str(table.get("commit", "chipkill" if kind == "tactical" else "alpha"))
    target = str(table.get("target", "lowest_stamina" if kind == "tactical" else "first"))
    w = Fraction(str(table.get("w", "3")))
    estimator = Estimator(rules, str(table.get("estimator", "exact")), source)
    pricing = Pricing(rules)
    name, _, arg = commit.partition(":")
    policy: CommitPolicy
    if name == "alpha":
        policy = Alpha(pricing)
    elif name == "fixed":
        policy = FixedK(pricing, int(arg))
    elif name == "reserve":
        policy = Reserve(pricing, int(arg))
    elif name == "chipkill":
        policy = ChipKill(pricing, estimator, 3.0 if estimator.sampled else Fraction(3))
    elif name == "lookahead":
        policy = LookAhead(
            pricing,
            estimator,
            lambda v: v.profile.recovery,
            3.0 if estimator.sampled else Fraction(3),
        )
    elif name == "never":
        policy = NeverAttack()
    else:
        raise ConfigError(f"unknown commitment policy {commit!r}")
    if kind == "tactical":
        reach_spacing = table.get("reach_spacing", True)
        if not isinstance(reach_spacing, bool):
            raise ConfigError("reach_spacing must be true or false")
        return TacticalAgent(
            rules,
            policy,
            target,
            w,
            int(str(table.get("retreat_engaged", 2))),
            Fraction(str(table.get("low_stamina", "1/3"))),
            reach_spacing,
        )
    if target not in TARGETS:
        raise ConfigError(f"unknown target policy {target!r}; known: {sorted(TARGETS)}")
    return ScriptedAgent(rules, policy, TARGETS[target], w, avoid_mode, oa_mode)
