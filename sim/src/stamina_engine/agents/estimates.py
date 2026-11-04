"""What an attacker expects a k-step attack to do against a defender who blocks optimally:
mean injury, mean stamina the defender spends, and the chance the defender goes down.

Two estimators. exact sums over the attack's exact (total, crit dice) distribution. sampled(n)
rolls n attacks, as the review's simulator did, in its order (per sample, per step, per die),
and keeps its float arithmetic, so a lockstep run makes the same decisions it made.
"""

from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache

from stamina_engine.agents.blocking import cached_best_block
from stamina_engine.analysis import dist
from stamina_engine.core.dice import DiceSource
from stamina_engine.model.derive import WeaponProfile
from stamina_engine.rules.exchange import roll_attack
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Blocking", "Packet: Critical Hits", "Review F1")


@dataclass(frozen=True)
class Target:
    """What the estimate needs to know about the defender."""

    defense: int
    armor: int
    stamina: int
    hp: int


@dataclass(frozen=True)
class Estimate:
    injury: Fraction | float
    cost: Fraction | float
    p_down: Fraction | float


@lru_cache(maxsize=1 << 16)
def exact_estimate(
    weapon: WeaponProfile, steps: int, target: Target, rules: RuleSet, w: Fraction
) -> Estimate:
    injury, cost, down = Fraction(0), Fraction(0), Fraction(0)
    for (total, crits), p in dist.attack(weapon, steps, rules.crit).items():
        bb = cached_best_block(
            total, crits, target.defense, target.armor, target.stamina, target.hp, rules, w
        )
        injury += p * bb.injury
        cost += p * bb.cost
        if bb.injury >= target.hp:
            down += p
    return Estimate(injury, cost, down)


def sampled_estimate(
    weapon: WeaponProfile,
    steps: int,
    target: Target,
    rules: RuleSet,
    w: Fraction,
    samples: int,
    source: DiceSource,
) -> Estimate:
    injury = cost = downs = 0
    for _ in range(samples):
        attack = roll_attack(weapon, steps, rules.crit, source)
        bb = cached_best_block(
            attack.total,
            attack.crit_dice,
            target.defense,
            target.armor,
            target.stamina,
            target.hp,
            rules,
            w,
        )
        injury += bb.injury
        cost += bb.cost
        if bb.injury >= target.hp:
            downs += 1
    return Estimate(injury / samples, cost / samples, downs / samples)
