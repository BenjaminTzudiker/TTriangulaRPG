"""Pricing: every stamina cost in one place. Agents quote with it; the engine charges with it.

Quotes are pure: they read the RuleSet and a Trackers snapshot and never change state. A
Quote says what it costs and how far it moves the on-turn or off-turn track.
"""

from collections.abc import Iterator, Sequence
from dataclasses import dataclass, replace
from enum import Enum
from typing import TYPE_CHECKING

from stamina_engine.core.errors import Unaffordable
from stamina_engine.rules.ruleset import RuleSet

if TYPE_CHECKING:
    from stamina_engine.model.derive import LoadoutProfile

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
    "Review F9",
    "Review F10",
    "Review F14",
)


class Track(Enum):
    NONE = "none"
    ON_TURN = "on_turn"  # the on-turn surcharge (actions)
    OFF_TURN = "off_turn"  # the off-turn escalation track
    EXTRA_MOVE = "extra_move"  # extra on-turn movement bought this turn (never escalates)


@dataclass(frozen=True)
class Trackers:
    """The counters costs depend on. The turn engine (M1) keeps these in CombatantState."""

    actions_this_turn: int = 0
    off_turn_costs: int = 0
    strain: int = 0
    extra_purchases: int = 0  # extra on-turn movement purchases this turn (F10's cap variant)


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
        n = self.advances
        if self.track is Track.ON_TURN:
            return replace(trackers, actions_this_turn=trackers.actions_this_turn + n)
        if self.track is Track.OFF_TURN:
            return replace(trackers, off_turn_costs=trackers.off_turn_costs + n)
        if self.track is Track.EXTRA_MOVE:
            return replace(trackers, extra_purchases=trackers.extra_purchases + n)
        return trackers


@dataclass(frozen=True)
class MoveQuote:
    """What moving some squares costs: free squares first, then squares already bought this
    turn, then new purchases (each with its own quote, in order)."""

    squares: int
    free: int
    banked: int
    purchases: tuple[Quote, ...]
    bought: tuple[int, ...]  # squares each purchase gives

    @property
    def total(self) -> int:
        return sum(q.total for q in self.purchases)

    @property
    def leftover(self) -> int:
        """Bought squares this move doesn't use."""
        return sum(self.bought) - (self.squares - self.free - self.banked)

    def after(self, trackers: Trackers) -> Trackers:
        for q in self.purchases:
            trackers = q.after(trackers)
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

    def melee_step(self, base: int, prior_actions: int, light: bool = False) -> int:
        """Weapon base + the on-turn surcharge (less light weapons' discount, a variant)."""
        s = self.rules.surcharge
        extra = s.surcharge(prior_actions)
        if light:
            extra = max(0, extra - s.light_discount())
        return base + extra

    def melee_attack(
        self,
        base: int,
        steps: int,
        trackers: Trackers = FRESH,
        stamina: int | None = None,
        light: bool = False,
        extra: int = 0,
    ) -> Quote:
        """k attack steps, declared and paid together. Raises if stamina is given and short.
        extra is added to every step (Heavy Swing's +1)."""
        prior = trackers.actions_this_turn
        parts = tuple(self.melee_step(base, prior + i, light) + extra for i in range(steps))
        return _ensure(Quote(parts, Track.ON_TURN), stamina)

    def max_steps(
        self, base: int, stamina: int, trackers: Trackers = FRESH, light: bool = False
    ) -> int:
        k = 0
        while self.melee_attack(base, k + 1, trackers, light=light).total <= stamina:
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

    def extra_movement(self, trackers: Trackers = FRESH) -> Quote:
        """Flat as written (v0.9); not an action and not an off-turn cost. Its track counts
        purchases, for the capped and escalating variants (movement.extra_cap, extra_mode)."""
        cost = self.rules.movement.extra_movement_cost(trackers.extra_purchases)
        return Quote((cost,), Track.EXTRA_MOVE)

    def extra_purchase_squares(self, trackers: Trackers, movement: int, per_purchase: int) -> int:
        """Squares the next extra on-turn purchase gives; 0 once the cap (if any) is reached,
        and 0 under movement.extra_mode = none."""
        if not self.rules.movement.extra_allowed():
            return 0
        cap = self.rules.movement.extra_cap_squares(movement)
        if cap is None:
            return per_purchase
        return max(0, min(per_purchase, cap - trackers.extra_purchases * per_purchase))

    def off_turn_purchase(self, trackers: Trackers, stamina: int | None = None) -> Quote:
        ot = self.rules.off_turn
        return _ensure(
            Quote((ot.cost(ot.purchase_base(), trackers.off_turn_costs),), Track.OFF_TURN),
            stamina,
        )

    def move(
        self,
        squares: int,
        *,
        on_turn: bool,
        trackers: Trackers,
        free_left: int = 0,
        banked: int = 0,
        movement: int = 0,
        extra_squares: int = 1,
        off_turn_squares: int = 1,
        stamina: int | None = None,
    ) -> MoveQuote:
        """The price of moving `squares` squares now. On your turn: free movement, then
        squares already bought, then extra purchases (flat). Off your turn: off-turn
        purchases (escalating). Raises if a cap stops it or stamina (when given) is short."""
        if squares < 0:
            raise ValueError("squares must be at least 0")
        free = min(squares, free_left) if on_turn else 0
        use_bank = min(squares - free, banked) if on_turn else 0
        rest = squares - free - use_bank
        purchases: list[Quote] = []
        bought: list[int] = []
        t = trackers
        cap = self.rules.off_turn.max_purchases()
        while rest > 0:
            if on_turn:
                give = self.extra_purchase_squares(t, movement, extra_squares)
                if give <= 0:
                    raise Unaffordable(f"purchased movement is capped at {movement} squares")
                q = self.extra_movement(t)
            else:
                if cap and len(purchases) >= cap:
                    raise Unaffordable(f"at most {cap} off-turn purchases in one move")
                give = off_turn_squares
                q = self.off_turn_purchase(t)
            purchases.append(q)
            bought.append(give)
            t = q.after(t)
            rest -= give
        quote = MoveQuote(squares, free, use_bank, tuple(purchases), tuple(bought))
        if stamina is not None and quote.total > stamina:
            raise Unaffordable(f"moving {squares} squares costs {quote.total}, {stamina} available")
        return quote

    def _purchases(
        self,
        *,
        on_turn: bool,
        trackers: Trackers,
        movement: int,
        extra_squares: int,
        off_turn_squares: int,
    ) -> Iterator[tuple[Quote, int]]:
        """The purchases a move would make, in order: (quote, squares it gives), until a cap
        stops them."""
        t = trackers
        cap = self.rules.off_turn.max_purchases()
        made = 0
        while True:
            if on_turn:
                give = self.extra_purchase_squares(t, movement, extra_squares)
                if give <= 0:
                    return
                q = self.extra_movement(t)
            else:
                if cap and made >= cap:
                    return
                give = off_turn_squares
                q = self.off_turn_purchase(t)
            yield q, give
            made += 1
            t = q.after(t)

    def max_move(
        self,
        *,
        on_turn: bool,
        trackers: Trackers,
        stamina: int,
        free_left: int = 0,
        banked: int = 0,
        movement: int = 0,
        extra_squares: int = 1,
        off_turn_squares: int = 1,
        limit: int = 200,
    ) -> int:
        """The most squares affordable now (stopping at limit)."""
        return (
            len(
                self.move_prices(
                    on_turn=on_turn,
                    trackers=trackers,
                    stamina=stamina,
                    free_left=free_left,
                    banked=banked,
                    movement=movement,
                    extra_squares=extra_squares,
                    off_turn_squares=off_turn_squares,
                    limit=limit,
                )
            )
            - 1
        )

    def move_prices(
        self,
        *,
        on_turn: bool,
        trackers: Trackers,
        stamina: int,
        free_left: int = 0,
        banked: int = 0,
        movement: int = 0,
        extra_squares: int = 1,
        off_turn_squares: int = 1,
        limit: int = 200,
    ) -> tuple[int, ...]:
        """[n] = the stamina for moving n squares now, for every affordable n up to limit
        (the same totals as move(n).total, computed in one pass)."""
        prices = [0] * (min(limit, free_left + banked if on_turn else 0) + 1)
        paid = 0
        for q, give in self._purchases(
            on_turn=on_turn,
            trackers=trackers,
            movement=movement,
            extra_squares=extra_squares,
            off_turn_squares=off_turn_squares,
        ):
            if len(prices) > limit or paid + q.total > stamina:
                break
            paid += q.total
            prices.extend([paid] * min(give, limit + 1 - len(prices)))
        return tuple(prices)

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

    def oa_cap(self, finesse: int, weapon_base: int) -> int:
        """The most stamina one opportunity attack may cost (before the per-square rule)."""
        return self.rules.opportunity.cap(finesse, weapon_base)

    def avoid_opportunity(
        self,
        enemies: int,
        stamina: int | None = None,
        *,
        caps: Sequence[int] | None = None,
        trackers: Trackers = FRESH,
        on_turn: bool = True,
    ) -> Quote:
        """Deny `enemies` enemies their OA for the square being left: one part each. As
        written, 1 each, never escalating and on no track. Variants price each at that
        enemy's cap (caps, in the same order) and put avoidance on the off-turn track.
        With avoid_debt, a shortfall is allowed (StateOps takes it from the next recovery)."""
        rule = self.rules.opportunity
        bases = [rule.avoid_part(caps[i] if caps is not None else 0) for i in range(enemies)]
        if rule.avoid_on_track(on_turn):
            ot = self.rules.off_turn
            earlier = trackers.off_turn_costs
            quote = Quote(
                tuple(ot.cost(b, earlier + i) for i, b in enumerate(bases)), Track.OFF_TURN
            )
        else:
            quote = Quote(tuple(bases))
        if rule.allows_debt():
            return quote
        return _ensure(quote, stamina)

    # --- blocks ----------------------------------------------------------------------

    def perfect_block(self, nth: int, ranged: bool = False, flat: bool = False) -> int:
        """The nth perfect block's cost. flat: the Monk core (no escalation this attack)."""
        b = self.rules.blocks
        n = 1 if flat else nth
        return b.ranged_perfect_cost(n) if ranged else b.perfect_cost(n)

    def blocks(
        self,
        perfect: int,
        grazing: int,
        stamina: int | None = None,
        prior_perfect: int = 0,
        ranged: bool = False,
        flat: bool = False,
    ) -> Quote:
        """Escalation applies within this attack only; it isn't part of any track.

        prior_perfect is how many perfect blocks already count toward the escalation. It is
        0 in v0.9, where the count resets every attack; block-reset variants carry it over.
        """
        b = self.rules.blocks
        first = prior_perfect + 1
        perfect_parts = tuple(
            self.perfect_block(i, ranged, flat) for i in range(first, first + perfect)
        )
        return _ensure(Quote(perfect_parts + (b.graze_cost,) * grazing), stamina)

    # --- other -----------------------------------------------------------------------

    def draw_between_turns(self, quick_draw: bool) -> Quote:
        return Quote((self.rules.ranged.draw_cost(quick_draw),))

    def draw(
        self,
        current: "LoadoutProfile",
        new: "LoadoutProfile",
        *,
        on_turn: bool,
        used_weapon: bool,
        bow_hands: bool,
    ) -> Quote | None:
        """Switching loadouts (Packet: Drawing Weapons), or None if not allowed now. Each
        weapon or shield the new loadout holds that the current one doesn't is drawn:
        free on your turn until you use a weapon; otherwise 1 for a normal item and 0 for a
        quick-draw weapon. After a bow shot, no normal item can be drawn until your next
        turn. Armor can't change mid-fight, so loadouts with other armor aren't offered."""
        if new.name == current.name or new.armor_name != current.armor_name:
            return None
        held = {current.weapon.name if current.weapon else None, current.shield}
        if current.off_hand_weapon is not None:
            held.add(current.off_hand_weapon.name)
        drawn: list[bool] = []  # quick-draw?
        for w in (new.weapon, new.off_hand_weapon):
            if w is not None and w.name not in held:
                drawn.append(w.quick_draw)
        if new.shield is not None and new.shield not in held:
            drawn.append(False)
        if bow_hands and not all(drawn):
            return None
        if on_turn and not used_weapon:
            return Quote((0,) * len(drawn)) if drawn else Quote(())
        return Quote(tuple(self.rules.ranged.draw_cost(q) for q in drawn))

    def strain_ability(
        self, stamina_cost: int, strain_cost: int, trackers: Trackers, strain_max: int
    ) -> Quote:
        """+1 stamina per point over maximum strain, counted after adding this ability's
        strain. Applies even when the ability costs no stamina (Assumptions register)."""
        over = max(0, trackers.strain + strain_cost - strain_max)
        return Quote((stamina_cost, over))
