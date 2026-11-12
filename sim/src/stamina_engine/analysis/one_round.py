"""One round of shooting at one target, solved exactly: archers shoot in turn, each choosing
how many shots and how many aim steps per shot, and the target blocks each shot knowing
what it faces (Packet: Ranged Attacks, Aim, Range Bands, Blocking).

It's the static, one-round question the design study's solver answered (simulator
requirements R7.5), built from the engine's own parts:
- each shot's exact distribution from analysis.ranged.shot (range penalty at a fixed
  distance, aim limit, crit switches);
- its price from Pricing.ranged_attack, with the on-turn surcharge carried across shots;
- the target's block choices from block_solver.block_frontier;
- the target's maximum stamina falling with its HP (resources.max_stamina).

It's a zero-sum game on value = down x [the target goes down] + w x HP lost + stamina the
target spends: archers maximize it, the target minimizes it. There's no movement: the
target doesn't react to shots, and nobody recovers. Ties go as in the study's solver
(bows5.py): an archer keeps the fewest aim steps (stopping beats shooting), the target the
cheapest block, so tests/parity/test_bows_solver.py can compare every figure. Values within
TIE of each other count as tied, so floating-point noise doesn't break a tie.

This isn't a fight: whole fights, with reactions and later rounds, come from the engine.
"""

from collections.abc import Sequence
from dataclasses import dataclass
from functools import cache

from stamina_engine.analysis.ranged import ShotJoint, shot
from stamina_engine.model.derive import WeaponProfile
from stamina_engine.rules.block_solver import block_frontier
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Ranged Attacks",
    "Packet: Aim",
    "Packet: Range Bands",
    "Packet: Blocking",
    "Packet: Actions and the On-Turn Surcharge",
    "Packet: Stamina",
)


@dataclass(frozen=True)
class Archer:
    weapon: WeaponProfile
    finesse: int
    stamina: int
    max_aims: int = 6


@dataclass(frozen=True)
class Target:
    defense: int  # the defense it blocks with, cover included
    armor: int  # before the weapon's Piercing
    hp: int
    stamina: int
    level: int = 1


@dataclass(frozen=True)
class RoundResult:
    value: float
    p_down: float
    hp_lost: float
    stamina_spent: float  # the target's
    shots: float
    aims: float


_ZERO = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
TIE = 1e-9


def solve_round(
    archers: Sequence[Archer],
    target: Target,
    rules: RuleSet,
    distance: int = 0,
    w: int = 3,
    down: int = 100,
) -> RoundResult:
    """The value of the round, with each archer and the target playing it best."""
    pricing = Pricing(rules)
    r = rules.ranged
    shooters = tuple(archers)

    @cache
    def joint(si: int, aims: int) -> tuple[tuple[float, int, int, int | None], ...]:
        a = shooters[si]
        wpn = a.weapon
        band = r.band(distance, wpn.ranges, wpn.band_width)
        if aims < r.required_aims(band):
            return ((1.0, 0, 0, None),)
        penalty = r.range_penalty(distance, wpn.band_width)
        dist: ShotJoint = shot(wpn, aims, a.finesse, band, rules, penalty)
        return tuple((float(p), t, c, lim) for (t, c, lim), p in dist.items())

    @cache
    def value(
        si: int, left: int, actions: int, stamina: int, hp: int
    ) -> tuple[float, float, float, float, float, float]:
        if si >= len(shooters):
            return _ZERO
        nxt = shooters[si + 1].stamina if si + 1 < len(shooters) else 0
        best = value(si + 1, nxt, 0, stamina, hp)
        a = shooters[si]
        armor = max(0, target.armor - a.weapon.piercing)
        before = Trackers(actions_this_turn=actions)
        for aims in range(a.max_aims + 1):
            quote = pricing.ranged_attack(a.weapon.base, aims, before)
            if quote.total > left:
                break
            after = quote.after(before).actions_this_turn
            acc = [0.0] * 6
            for p, total, crits, limit in joint(si, aims):
                reply: tuple[float, ...] | None = None
                frontier = block_frontier(
                    total, crits, target.defense, armor, stamina, rules, True, limit
                )
                for cost, injury in frontier:
                    hp_after = hp - injury
                    if hp_after <= 0:
                        v: tuple[float, ...] = (down + w * hp + cost, 1.0, hp, cost, 1.0, aims)
                    else:
                        most = rules.resources.max_stamina(hp_after, target.level)
                        cont = value(
                            si, left - quote.total, after, min(stamina - cost, most), hp_after
                        )
                        v = (
                            w * injury + cost + cont[0],
                            cont[1],
                            injury + cont[2],
                            cost + cont[3],
                            1 + cont[4],
                            aims + cont[5],
                        )
                    if reply is None or v[0] < reply[0] - TIE:
                        reply = v
                assert reply is not None  # no blocks is always affordable
                for i in range(6):
                    acc[i] += p * reply[i]
            cand = (acc[0], acc[1], acc[2], acc[3], acc[4], acc[5])
            if cand[0] > best[0] + TIE:
                best = cand
        return best

    first = shooters[0].stamina if shooters else 0
    out = value(0, first, 0, target.stamina, target.hp)
    return RoundResult(*out)
