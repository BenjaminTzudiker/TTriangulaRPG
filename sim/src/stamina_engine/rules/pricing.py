"""Pricing: every stamina cost in one place. Agents quote with it; the engine charges with it.

Quotes are pure: they read the RuleSet and a Trackers snapshot and never change state. A
Quote says what it costs and how far it moves the on-turn or off-turn track.
"""

from dataclasses import dataclass
from enum import Enum

from stamina_engine.core.errors import Unaffordable
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Actions and the On-Turn Surcharge",
    "Packet: Melee Attacks",
    "Packet: Aim",
    "Packet: On-Turn Movement",
    "Packet: Off-Turn Movement",
    "Packet: Off-Turn Escalation",
    "Packet: Avoiding Opportunity Attacks",
    "Packet: Making Opportunity Attacks",
    "Packet: Blocking",
    "Packet: Drawing Weapons",
    "Packet: Going Over Your Maximum Strain",
    "Packet: Stamina Costs",
    "Ledger CB-2",
    "Ledger CB-3",
    "Ledger CB-4",
    "Ledger RG-2",
    "Ledger MV-1",
    "Ledger MV-2",
    "Ledger MV-3",
    "Ledger MV-4",
    "Ledger MV-5",
    "Ledger EQ-3",
    "Ledger CR-5",
)


class Track(Enum):
    NONE = "none"
    ON_TURN = "on_turn"  # the on-turn surcharge (actions)
    OFF_TURN = "off_turn"  # the off-turn escalation track


@dataclass(frozen=True)
class Trackers:
    """The counters costs depend on. The turn engine (M1) keeps these in CombatantState."""

    actions_this_turn: int = 0
    off_turn_costs: int = 0
    strain: int = 0


@dataclass(frozen=True)
class Quote:
    parts: tuple[int, ...]
    track: Track = Track.NONE
    free_parts: int = 0  # leading parts that don't advance the track (a shot's base cost)

    @property
    def total(self) -> int:
        return sum(self.parts)

    @property
    def advances(self) -> int:
        """How many actions (or off-turn costs) this adds to its track."""
        return len(self.parts) - self.free_parts if self.track is not Track.NONE else 0

    def after(self, trackers: Trackers) -> Trackers:
        """The trackers once this has been paid."""
        if self.track is Track.ON_TURN:
            return Trackers(
                trackers.actions_this_turn + self.advances,
                trackers.off_turn_costs,
                trackers.strain,
            )
        if self.track is Track.OFF_TURN:
            return Trackers(
                trackers.actions_this_turn,
                trackers.off_turn_costs + self.advances,
                trackers.strain,
            )
        return trackers


FRESH = Trackers()  # start of turn, nothing spent off-turn, no strain


def _ensure(quote: Quote, stamina: int | None) -> Quote:
    if stamina is not None and quote.total > stamina:
        raise Unaffordable(f"costs {quote.total}, {stamina} stamina available")
    return quote


class Pricing:
    def __init__(self, rules: RuleSet) -> None:
        self.rules = rules

    # --- on-turn actions -------------------------------------------------------------

    def melee_step(self, base: int, prior_actions: int) -> int:
        """Weapon base + the on-turn surcharge."""
        return base + self.rules.surcharge.surcharge(prior_actions)

    def melee_attack(
        self, base: int, steps: int, trackers: Trackers = FRESH, stamina: int | None = None
    ) -> Quote:
        """k attack steps, declared and paid together. Raises if stamina is given and short."""
        prior = trackers.actions_this_turn
        parts = tuple(self.melee_step(base, prior + i) for i in range(steps))
        return _ensure(Quote(parts, Track.ON_TURN), stamina)

    def max_steps(self, base: int, stamina: int, trackers: Trackers = FRESH) -> int:
        k = 0
        while self.melee_attack(base, k + 1, trackers).total <= stamina:
            k += 1
        return k

    def aim_step(self, prior_actions: int) -> int:
        return self.rules.ranged.aim_base() + self.rules.surcharge.surcharge(prior_actions)

    def ranged_attack(
        self, shot_base: int, aims: int, trackers: Trackers = FRESH, stamina: int | None = None
    ) -> Quote:
        """The flat shot cost, then each aim step as an action. The shot itself isn't one, so
        only the aim steps advance the surcharge."""
        prior = trackers.actions_this_turn
        aim_parts = tuple(self.aim_step(prior + i) for i in range(aims))
        return _ensure(Quote((shot_base, *aim_parts), Track.ON_TURN, free_parts=1), stamina)

    # --- movement --------------------------------------------------------------------

    def extra_movement(self) -> Quote:
        """Always flat; not an action and not an off-turn cost."""
        return Quote((self.rules.movement.extra_movement_cost(),))

    def off_turn_purchase(self, trackers: Trackers, stamina: int | None = None) -> Quote:
        ot = self.rules.off_turn
        return _ensure(
            Quote((ot.cost(ot.purchase_base(), trackers.off_turn_costs),), Track.OFF_TURN),
            stamina,
        )

    # --- opportunity attacks ---------------------------------------------------------

    def opportunity_attack(
        self,
        base: int,
        steps: int,
        trackers: Trackers,
        cap: int,
        stamina: int | None = None,
    ) -> Quote:
        """Steps go on the off-turn track. The whole attack (base and escalation together)
        must fit the cap."""
        ot = self.rules.off_turn
        earlier = trackers.off_turn_costs
        parts = tuple(ot.cost(base, earlier + i) for i in range(steps))
        quote = Quote(parts, Track.OFF_TURN)
        if quote.total > cap:
            raise Unaffordable(f"opportunity attack costs {quote.total}, cap is {cap}")
        return _ensure(quote, stamina)

    def avoid_opportunity(self, enemies: int, stamina: int | None = None) -> Quote:
        """1 per enemy for the square being left. Doesn't escalate or touch any track."""
        return _ensure(Quote((self.rules.opportunity.avoid_cost(enemies),)), stamina)

    # --- blocks ----------------------------------------------------------------------

    def perfect_block(self, nth: int) -> int:
        return self.rules.blocks.perfect_cost(nth)

    def blocks(
        self, perfect: int, grazing: int, stamina: int | None = None, prior_perfect: int = 0
    ) -> Quote:
        """Escalation applies within this attack only; it isn't part of any track.

        prior_perfect is how many perfect blocks already count toward the escalation. It is
        0 in v0.9, where the count resets every attack; block-reset variants carry it over.
        """
        b = self.rules.blocks
        first = prior_perfect + 1
        perfect_parts = tuple(b.perfect_cost(i) for i in range(first, first + perfect))
        return _ensure(Quote(perfect_parts + (b.graze_cost,) * grazing), stamina)

    # --- other -----------------------------------------------------------------------

    def draw_between_turns(self, quick_draw: bool) -> Quote:
        return Quote((self.rules.ranged.draw_cost(quick_draw),))

    def strain_ability(
        self, stamina_cost: int, strain_cost: int, trackers: Trackers, strain_max: int
    ) -> Quote:
        """+1 stamina per point over maximum strain, counted after adding this ability's
        strain. Applies even when the ability costs no stamina (Assumptions register)."""
        over = max(0, trackers.strain + strain_cost - strain_max)
        return Quote((stamina_cost, over))
