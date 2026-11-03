"""On-turn movement (Packet: On-Turn Movement)."""

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
    )

    def free_movement(self, agility: int) -> int:
        raise NotImplementedError

    def squares_per_purchase(self, agility: int) -> int:
        raise NotImplementedError

    def extra_movement_cost(self) -> int:
        raise NotImplementedError


@register("movement", "v0_9")
@dataclass(frozen=True)
class V09Movement(MovementRule):
    """Free movement 5 + odd AGI; each purchase (extra or off-turn) moves 1 + odd AGI."""

    free_base: int = 5
    purchase_base_squares: int = 1
    extra_cost: int = 1

    def free_movement(self, agility: int) -> int:
        return self.free_base + odd_count(agility)

    def squares_per_purchase(self, agility: int) -> int:
        return self.purchase_base_squares + odd_count(agility)

    def extra_movement_cost(self) -> int:
        return self.extra_cost
