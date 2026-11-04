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
        "Review F9",
        "Review F14",
    )
    allowed = {
        "timing": frozenset({"on_leave"}),
        # The cap: 1 + odd FIN (v0.9), or the OA weapon's base cost + odd FIN (F9 option 1).
        "cap_rule": frozenset({"flat", "weapon_base"}),
        # Price to deny one enemy for one square: flat (1), or that enemy's cap (F9 option 2).
        "avoid_price": frozenset({"flat", "attacker_cap"}),
        # Whether avoidance escalates and counts as an off-turn cost (F9 option 3): never,
        # always, or only when paid off-turn.
        "avoid_track": frozenset({"none", "off_turn", "off_turn_only"}),
    }

    def cap(self, finesse: int, weapon_base: int = 0) -> int:
        raise NotImplementedError

    def avoid_cost(self, enemies: int) -> int:
        raise NotImplementedError

    def avoid_part(self, enemy_cap: int) -> int:
        """The base price of denying one enemy whose cap is enemy_cap, before any escalation."""
        raise NotImplementedError

    def avoid_on_track(self, on_turn: bool) -> bool:
        raise NotImplementedError

    def allows_debt(self) -> bool:
        raise NotImplementedError

    def attacks_allowed(self) -> bool:
        """False reproduces the review's duels and 1v3 runs, which had no OAs."""
        raise NotImplementedError

    def per_square(self) -> bool:
        raise NotImplementedError

    def point_blank_avoid(self) -> bool:
        """Can the shooter pay to avoid the OAs a point-blank shot provokes? (Not for now.)"""
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
    cap_rule: str = "flat"
    avoid_price: str = "flat"
    avoid_track: str = "none"

    def cap(self, finesse: int, weapon_base: int = 0) -> int:
        base = weapon_base if self.cap_rule == "weapon_base" else self.cap_base
        return base + self.cap_per_odd_finesse * odd_count(finesse)

    def avoid_cost(self, enemies: int) -> int:
        return self.avoid_cost_each * enemies

    def avoid_part(self, enemy_cap: int) -> int:
        return enemy_cap if self.avoid_price == "attacker_cap" else self.avoid_cost_each

    def avoid_on_track(self, on_turn: bool) -> bool:
        return self.avoid_track == "off_turn" or (
            self.avoid_track == "off_turn_only" and not on_turn
        )

    def allows_debt(self) -> bool:
        return self.avoid_debt

    def attacks_allowed(self) -> bool:
        return self.enabled

    def per_square(self) -> bool:
        return self.per_square_cap

    def point_blank_avoid(self) -> bool:
        return self.point_blank_avoidable
