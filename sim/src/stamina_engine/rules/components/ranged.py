"""Ranged attacks, aim, cover and drawing weapons (Packet: Ranged Attacks).

M0 uses only the aim cost and the draw cost; the rest is data for M3.
"""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class RangedRule(Component):
    cites = (
        "Packet: Ranged Attacks",
        "Packet: Aim",
        "Packet: Cover",
        "Packet: Drawing Weapons",
        "Ledger RG-1",
        "Ledger RG-2",
        "Ledger RG-3",
        "Ledger RG-4",
        "Ledger EQ-3",
    )
    allowed = {
        "aim_mode": frozenset({"damage"}),
        "dive": frozenset({"half_is_half"}),
        "point_blank_order": frozenset({"dive_oas_first"}),
    }

    def aim_base(self) -> int:
        raise NotImplementedError

    def draw_cost(self, quick_draw: bool) -> int:
        raise NotImplementedError


@register("ranged", "v0_9")
@dataclass(frozen=True)
class V09Ranged(RangedRule):
    """Aim adds 1d6 + FIN and costs 1 + surcharge; drawing between turns costs 1."""

    aim_mode: str = "damage"
    aim_cost_base: int = 1
    aim_die: int = 6
    half_cover: int = 2
    three_quarter_cover: int = 5
    dive: str = "half_is_half"
    point_blank_order: str = "dive_oas_first"
    draw_between_turns: int = 1

    def aim_base(self) -> int:
        return self.aim_cost_base

    def draw_cost(self, quick_draw: bool) -> int:
        return 0 if quick_draw else self.draw_between_turns
