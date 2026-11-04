"""The opening full strike, exactly: an attacker commits every affordable step against a
defender who blocks optimally (w x injury + stamina, never an avoidable incapacitation).

This is review Table 3's strike column, the strike columns of Table 9 and the Addendum, and
F1's injury distribution, with no sampling error.
"""

from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction

from stamina_engine.analysis import dist
from stamina_engine.model.derive import LoadoutProfile
from stamina_engine.rules.block_solver import DEFAULT_W, best_block
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Blocking", "Packet: Critical Hits", "Packet: Melee Attacks", "Review F1")


@dataclass(frozen=True)
class Strike:
    steps: int
    cost: int
    injury: dict[int, Fraction]  # injury -> probability
    defender_cost: dict[int, Fraction]  # stamina the defender spends -> probability
    hp: int  # the defender's HP

    @property
    def mean_injury(self) -> Fraction:
        return sum((i * p for i, p in self.injury.items()), Fraction(0))

    @property
    def p_down(self) -> Fraction:
        return sum((p for i, p in self.injury.items() if i >= self.hp), Fraction(0))

    def p_injury(self, low: int, high: int | None = None) -> Fraction:
        """P(low <= injury <= high); high None means no upper bound."""
        return sum(
            (p for i, p in self.injury.items() if i >= low and (high is None or i <= high)),
            Fraction(0),
        )

    def p_defender_spends(self, low: int, high: int) -> Fraction:
        return sum((p for c, p in self.defender_cost.items() if low <= c <= high), Fraction(0))


def full_strike(
    attacker: LoadoutProfile,
    attacker_stamina: int,
    defense: int,
    armor: int,
    defender_stamina: int,
    defender_hp: int,
    rules: RuleSet,
    w: Fraction = DEFAULT_W,
    steps: int | None = None,
) -> Strike:
    weapon = attacker.weapon
    assert weapon is not None
    pricing = Pricing(rules)
    k = (
        steps
        if steps is not None
        else pricing.max_steps(weapon.base, attacker_stamina, light=weapon.light)
    )
    injury: defaultdict[int, Fraction] = defaultdict(Fraction)
    spend: defaultdict[int, Fraction] = defaultdict(Fraction)
    for (total, crits), p in dist.attack(weapon, k, rules.crit).items():
        bb = best_block(total, crits, defense, armor, defender_stamina, defender_hp, rules, w)
        injury[bb.injury] += p
        spend[bb.cost] += p
    return Strike(
        k,
        pricing.melee_attack(weapon.base, k, light=weapon.light).total,
        dict(injury),
        dict(spend),
        defender_hp,
    )


def mirror_strike(
    gear: LoadoutProfile,
    stamina: int,
    hp: int,
    rules: RuleSet,
    defender_stamina: int | None = None,
    defense_bonus: int = 0,
    w: Fraction = DEFAULT_W,
) -> Strike:
    """An identical defender at full (or at defender_stamina), optionally with +MD."""
    return full_strike(
        gear,
        stamina,
        gear.melee_defense + defense_bonus,
        gear.armor,
        stamina if defender_stamina is None else defender_stamina,
        hp,
        rules,
        w,
    )


def opening_split(
    gear: LoadoutProfile, stamina: int, rules: RuleSet, threshold: int = 30
) -> tuple[Fraction, Fraction]:
    """F1's conditioning: P(at least one crit and total >= threshold), P(no crit and total <
    threshold) for the full strike's roll."""
    weapon = gear.weapon
    assert weapon is not None
    k = Pricing(rules).max_steps(weapon.base, stamina, light=weapon.light)
    hot = cold = Fraction(0)
    for (total, crits), p in dist.attack(weapon, k, rules.crit).items():
        if crits > 0 and total >= threshold:
            hot += p
        elif crits == 0 and total < threshold:
            cold += p
    return hot, cold
