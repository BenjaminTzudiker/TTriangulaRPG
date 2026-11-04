"""Retreat economics on open ground, exactly (Review Addendum 2).

A fleer starts `start` squares from a chaser and backs straight away with off-turn
purchases, paying to avoid the chaser's OA on every square it leaves inside the chaser's
reach. The chaser then closes on its turn with free movement and extra purchases. Every
price comes from Pricing, so a variant RuleSet changes the table the way it changes play.

Addendum 2's figures are the fleer's cheapest escape out of the chaser's free reach (the
chaser's free movement + reach, plus one), stopping as soon as it is out. A fleer that uses
every square it bought ends farther away, and the chaser can pay more: `retreat()` with
stop=False gives that case, and `table()` lists both by number of purchases.
"""

from dataclasses import dataclass
from fractions import Fraction

from stamina_engine.rules.pricing import FRESH, Pricing
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: On-Turn Movement",
    "Packet: Off-Turn Movement",
    "Packet: Off-Turn Escalation",
    "Packet: Avoiding Opportunity Attacks",
    "Ledger MV-1",
    "Ledger MV-2",
    "Ledger MV-3",
    "Review Addendum 2",
)


@dataclass(frozen=True)
class Retreat:
    fleer_agility: int
    purchases: int
    squares: int  # squares moved
    distance: int  # from the chaser, afterwards
    movement_cost: int  # the off-turn purchases
    avoid_cost: int  # avoiding the chaser's OAs on the way out
    chaser_cost: int  # what the chaser pays to get back in reach on its turn

    @property
    def fleer_cost(self) -> int:
        return self.movement_cost + self.avoid_cost

    @property
    def ratio(self) -> Fraction:
        """Fleer stamina per chaser stamina (infinite chaser cost shows as 0)."""
        return Fraction(self.fleer_cost, self.chaser_cost) if self.chaser_cost else Fraction(0)


def chaser_cost(
    rules: RuleSet, distance: int, chaser_agility: int = 1, chaser_reach: int = 1
) -> int:
    """Stamina the chaser spends on its turn to get within reach (0 if free movement does)."""
    mv = rules.movement
    movement = mv.free_movement(chaser_agility)
    need = max(0, distance - chaser_reach)
    quote = Pricing(rules).move(
        need,
        on_turn=True,
        trackers=FRESH,
        free_left=movement,
        movement=movement,
        extra_squares=mv.extra_squares_per_purchase(chaser_agility),
    )
    return quote.total


def free_reach(rules: RuleSet, chaser_agility: int = 1, chaser_reach: int = 1) -> int:
    """The farthest distance the chaser can attack from with free movement alone."""
    return rules.movement.free_movement(chaser_agility) + chaser_reach


def retreat(
    rules: RuleSet,
    fleer_agility: int,
    purchases: int,
    *,
    chaser_agility: int = 1,
    chaser_reach: int = 1,
    start: int = 1,
    stop: bool = True,
) -> Retreat:
    """`purchases` off-turn purchases straight away from the chaser. With stop, the fleer
    stops as soon as it is out of the chaser's free reach (if these purchases get it there)."""
    pricing = Pricing(rules)
    per = rules.movement.squares_per_purchase(fleer_agility)
    squares = purchases * per
    if stop:
        squares = min(squares, max(0, free_reach(rules, chaser_agility, chaser_reach) + 1 - start))
    quote = pricing.move(squares, on_turn=False, trackers=FRESH, off_turn_squares=per)
    # Moving straight away, the squares left at distance start .. reach are threatened.
    threatened_left = max(0, min(squares, chaser_reach - start + 1))
    avoid = pricing.avoid_opportunity(1).total * threatened_left
    distance = start + squares
    return Retreat(
        fleer_agility,
        len(quote.purchases),
        squares,
        distance,
        quote.total,
        avoid,
        chaser_cost(rules, distance, chaser_agility, chaser_reach),
    )


def escape(
    rules: RuleSet,
    fleer_agility: int,
    *,
    chaser_agility: int = 1,
    chaser_reach: int = 1,
    start: int = 1,
) -> Retreat:
    """The fewest purchases that end out of the chaser's free reach, stopping there."""
    per = rules.movement.squares_per_purchase(fleer_agility)
    need = max(0, free_reach(rules, chaser_agility, chaser_reach) + 1 - start)
    purchases = -(-need // per)
    return retreat(
        rules,
        fleer_agility,
        purchases,
        chaser_agility=chaser_agility,
        chaser_reach=chaser_reach,
        start=start,
    )


def table(
    rules: RuleSet,
    fleer_agility: int,
    *,
    chaser_agility: int = 1,
    chaser_reach: int = 1,
    start: int = 1,
    max_purchases: int = 6,
) -> list[tuple[Retreat, Retreat]]:
    """For 1..max_purchases purchases: (stopping once out of free reach, using every square)."""
    return [
        (
            retreat(
                rules,
                fleer_agility,
                k,
                chaser_agility=chaser_agility,
                chaser_reach=chaser_reach,
                start=start,
                stop=True,
            ),
            retreat(
                rules,
                fleer_agility,
                k,
                chaser_agility=chaser_agility,
                chaser_reach=chaser_reach,
                start=start,
                stop=False,
            ),
        )
        for k in range(1, max_purchases + 1)
    ]
