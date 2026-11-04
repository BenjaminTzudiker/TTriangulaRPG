"""On-turn and off-turn movement (Packet: On-Turn Movement, Off-Turn Movement)."""

from dataclasses import dataclass

from stamina_engine.core.mathx import odd_count
from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class MovementRule(Component):
    cites = (
        "Packet: On-Turn Movement",
        "Packet: Off-Turn Movement",
        "Ledger MV-1",
        "Ledger MV-2",
        "Review F10",
    )
    allowed = {
        # Squares per extra on-turn purchase: 1 + odd AGI (v0.9), or 1 (F10 option 1).
        "extra_squares": frozenset({"agility", "one"}),
        # Purchased on-turn squares per turn: unlimited (v0.9), or at most your Movement, the
        # last purchase cut short (F10 option 2).
        "extra_cap": frozenset({"none", "free_movement"}),
        # Unused squares of an on-turn purchase: kept for the rest of the turn, or lost when
        # that move ends. Off-turn squares always last only for their move.
        "leftover": frozenset({"turn", "move"}),
        # Extra on-turn purchases (Review F10, movement experiments): "flat" prices every
        # purchase at extra_cost (v0.9); "escalating" prices the nth purchase this turn at
        # extra_cost + extra_slope x (n - 1); "none" removes extra on-turn movement, so
        # moving beyond your free Movement before your next turn means off-turn purchases.
        "extra_mode": frozenset({"flat", "escalating", "none"}),
    }

    def free_movement(self, agility: int) -> int:
        raise NotImplementedError

    def squares_per_purchase(self, agility: int) -> int:
        """Squares per off-turn purchase."""
        raise NotImplementedError

    def extra_squares_per_purchase(self, agility: int) -> int:
        """Squares per extra on-turn purchase."""
        raise NotImplementedError

    def extra_cap_squares(self, movement: int) -> int | None:
        """The most squares you can buy on one turn, or None for no cap."""
        raise NotImplementedError

    def extra_movement_cost(self, purchases_made: int = 0) -> int:
        """Cost of the next extra on-turn purchase, given how many were made this turn."""
        raise NotImplementedError

    def extra_allowed(self) -> bool:
        """False removes extra on-turn movement altogether."""
        raise NotImplementedError

    def keeps_leftover(self) -> bool:
        raise NotImplementedError


@register("movement", "v0_9")
@dataclass(frozen=True)
class V09Movement(MovementRule):
    """Free movement 5 + odd AGI; each purchase (extra or off-turn) moves 1 + odd AGI."""

    free_base: int = 5
    purchase_base_squares: int = 1
    extra_cost: int = 1
    extra_squares: str = "agility"
    extra_cap: str = "none"
    leftover: str = "turn"
    extra_mode: str = "flat"
    extra_slope: int = 1

    def free_movement(self, agility: int) -> int:
        return self.free_base + odd_count(agility)

    def squares_per_purchase(self, agility: int) -> int:
        return self.purchase_base_squares + odd_count(agility)

    def extra_squares_per_purchase(self, agility: int) -> int:
        if self.extra_squares == "one":
            return 1
        return self.squares_per_purchase(agility)

    def extra_cap_squares(self, movement: int) -> int | None:
        return movement if self.extra_cap == "free_movement" else None

    def extra_movement_cost(self, purchases_made: int = 0) -> int:
        if self.extra_mode == "escalating":
            return self.extra_cost + self.extra_slope * purchases_made
        return self.extra_cost

    def extra_allowed(self) -> bool:
        return self.extra_mode != "none"

    def keeps_leftover(self) -> bool:
        return self.leftover == "turn"
