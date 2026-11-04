"""The defender's block choice: an exact search over (perfect, grazing) pairs.

Minimizes w x injury + stamina, never accepting an avoidable incapacitation; w is the
stamina value of 1 HP (3 by default; 1.5 and 6 for sensitivity, as in the review). Ties go
to the cheaper pair, then the one with fewer perfect blocks, which is the review
simulator's order. Costs come from Pricing and injury from exchange.resolve, so the solver
prices blocks exactly as the engine charges them.
"""

from dataclasses import dataclass
from fractions import Fraction

from stamina_engine.rules.exchange import Blocks, resolve
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Blocking", "Ledger CB-3", "Ledger CB-4", "Ledger GM-1")

DEFAULT_W = Fraction(3)


@dataclass(frozen=True)
class BlockChoice:
    blocks: Blocks
    cost: int
    injury: int
    incapacitated: bool
    score: Fraction  # w x injury + cost

    def key(self) -> tuple[bool, Fraction, int]:
        return (self.incapacitated, self.score, self.cost)


def _needed(damage: int, defense: int) -> int | None:
    """Blocks needed to stop all of damage before leaks, or None if blocks stop nothing."""
    if defense <= 0:
        return None if damage > 0 else 0
    return -(-damage // defense)


def best_block(
    damage: int,
    crit_dice: int,
    defense: int,
    armor: int,
    stamina: int,
    hp: int,
    rules: RuleSet,
    w: Fraction = DEFAULT_W,
) -> BlockChoice:
    pricing = Pricing(rules)
    graze = rules.blocks.graze_cost
    needed = _needed(damage, defense)
    best: BlockChoice | None = None
    p = 0
    perfect_cost = 0
    while perfect_cost <= stamina:
        g = 0
        while perfect_cost + g * graze <= stamina:
            blocks = Blocks(p, g)
            out = resolve(damage, crit_dice, defense, armor, blocks, rules)
            cost = perfect_cost + g * graze  # == pricing.blocks(p, g).total
            choice = BlockChoice(blocks, cost, out.injury, out.injury >= hp, w * out.injury + cost)
            if best is None or choice.key() < best.key():
                best = choice
            # Once everything is stopped and soaked, more grazes only cost more.
            if needed is not None and p + g >= needed and out.after_armor == 0:
                break
            g += 1
        p += 1
        perfect_cost += pricing.perfect_block(p)
    assert best is not None  # (0, 0) is always affordable
    return best


def cheapest_zero_injury(
    damage: int,
    crit_dice: int,
    defense: int,
    armor: int,
    rules: RuleSet,
    stamina: int | None = None,
) -> BlockChoice | None:
    """The cheapest blocks that leave no injury, or None if none exist (within stamina)."""
    pricing = Pricing(rules)
    needed = _needed(damage, defense)
    limit = needed if needed is not None else 0
    best: BlockChoice | None = None
    for p in range(limit + 1):
        for g in range(limit - p + 1):
            cost = pricing.blocks(p, g).total
            if stamina is not None and cost > stamina:
                continue
            out = resolve(damage, crit_dice, defense, armor, Blocks(p, g), rules)
            if out.injury == 0 and (best is None or cost < best.cost):
                best = BlockChoice(Blocks(p, g), cost, 0, False, Fraction(cost))
    return best
