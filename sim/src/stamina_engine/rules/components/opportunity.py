"""Opportunity attacks: cap and avoidance (Packet: Opportunity Attacks)."""

from dataclasses import dataclass

from stamina_engine.core.mathx import odd_count
from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class OpportunityRule(Component):
    cites = (
        "Packet: Avoiding Opportunity Attacks",
        "Packet: Making Opportunity Attacks",
        "Ledger MV-3",
        "Ledger MV-5",
    )
    allowed = {"timing": frozenset({"on_leave"})}

    def cap(self, finesse: int) -> int:
        raise NotImplementedError

    def avoid_cost(self, enemies: int) -> int:
        raise NotImplementedError


@register("opportunity", "v0_9")
@dataclass(frozen=True)
class V09Opportunity(OpportunityRule):
    """Cap 1 + 1 per odd Finesse; avoiding costs 1 per enemy per square, never escalating."""

    cap_base: int = 1
    cap_per_odd_finesse: int = 1
    avoid_cost_each: int = 1
    avoid_debt: bool = False
    per_square_cap: bool = False  # the packet's optional rule
    point_blank_avoidable: bool = False
    timing: str = "on_leave"
    enabled: bool = True

    def cap(self, finesse: int) -> int:
        return self.cap_base + self.cap_per_odd_finesse * odd_count(finesse)

    def avoid_cost(self, enemies: int) -> int:
        return self.avoid_cost_each * enemies
