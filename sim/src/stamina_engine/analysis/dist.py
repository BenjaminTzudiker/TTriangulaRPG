"""Exact joint distributions of (damage total, critical dice) for k attack steps."""

from collections import defaultdict
from fractions import Fraction

from stamina_engine.model.derive import Damage, WeaponProfile
from stamina_engine.rules.components.crit import CritRule

cites = ("Packet: Critical Hits", "Packet: Melee Attacks", "Ledger CB-6")

Joint = dict[tuple[int, int], Fraction]  # (total, crit dice) -> probability

POINT: Joint = {(0, 0): Fraction(1)}


def convolve(a: Joint, b: Joint) -> Joint:
    out: defaultdict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for (ta, ca), pa in a.items():
        for (tb, cb), pb in b.items():
            out[(ta + tb, ca + cb)] += pa * pb
    return dict(out)


def die(size: int, widen: int, crit: CritRule) -> Joint:
    p = Fraction(1, size)
    return {(f, int(crit.is_crit(f, size, widen))): p for f in range(1, size + 1)}


def step(damage: Damage, widen: int, crit: CritRule) -> Joint:
    """One step: every die convolved separately (each can crit), plus flat, floored."""
    joint = POINT
    for dice in damage.dice:
        for _ in range(dice.count):
            joint = convolve(joint, die(dice.size, widen, crit))
    out: defaultdict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for (total, crits), p in joint.items():
        out[(max(damage.step_floor, total + damage.flat), crits)] += p
    return dict(out)


def attack(weapon: WeaponProfile, steps: int, crit: CritRule) -> Joint:
    one = step(weapon.damage, weapon.crit_widen, crit)
    joint = POINT
    for _ in range(steps):
        joint = convolve(joint, one)
    return joint


def mean(joint: Joint) -> Fraction:
    return sum((total * p for (total, _), p in joint.items()), Fraction(0))


def p_any_crit(joint: Joint) -> Fraction:
    return sum((p for (_, crits), p in joint.items() if crits > 0), Fraction(0))
