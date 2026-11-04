"""Ranged attacks, aim, range bands, cover and drawing weapons (Packet: Ranged Attacks).

Readings and variants (Assumptions register):
- bands: v0_9 as written (medium: the first aim step adds only Finesse and at least one aim
  is needed or the shot misses; long: the first two, and two aims needed; beyond long:
  misses). minus_d6 (Review F11 (b)): no minimum aims; the shot loses 1d6 at medium and
  2d6 at long, floored at 0. none: no band effects (beyond long still misses).
- aim_mode: damage as written (each aim step adds aim_die + Finesse). precision (Review F3
  option 3): aim steps add no damage; each widens the critical range of the shot's dice by 1.
- dive: a dive that ends fully behind cover counts as three-quarters, as written; ending in
  half cover gives half (half_is_half).
"""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register

BANDS = ("short", "medium", "long", "beyond")


@dataclass(frozen=True)
class RangedRule(Component):
    cites = (
        "Packet: Ranged Attacks",
        "Packet: Aim",
        "Packet: Range Bands",
        "Packet: Cover",
        "Packet: Drawing Weapons",
        "Ledger RG-1",
        "Ledger RG-2",
        "Ledger RG-3",
        "Ledger RG-4",
        "Ledger EQ-3",
        "Review F3",
        "Review F11",
    )
    allowed = {
        "aim_mode": frozenset({"damage", "precision"}),
        "bands": frozenset({"v0_9", "minus_d6", "none"}),
        "dive": frozenset({"half_is_half"}),
        "point_blank_order": frozenset({"dive_oas_first"}),
    }

    def aim_base(self) -> int:
        raise NotImplementedError

    def draw_cost(self, quick_draw: bool) -> int:
        raise NotImplementedError

    def band(self, distance: int, ranges: tuple[int, ...]) -> str:
        """short, medium, long or beyond, from the weapon's three ranges."""
        for name, limit in zip(BANDS, ranges, strict=False):
            if distance <= limit:
                return name
        return "beyond"

    def required_aims(self, band: str) -> int:
        raise NotImplementedError

    def aim_dice(self) -> int:
        """The die each aim step adds (with Finesse)."""
        raise NotImplementedError

    def precision_aim(self) -> bool:
        raise NotImplementedError

    def dropped_aim_dice(self, band: str) -> int:
        raise NotImplementedError

    def penalty_dice(self, band: str) -> int:
        raise NotImplementedError

    def cover_bonus(self, level: int) -> int:
        """Defense bonus for a cover level (0 none, 1 half, 2 three-quarters)."""
        raise NotImplementedError

    def dive_cover(self, level: int) -> int:
        """The cover a dive earns, from the level the target ends in (3 = total)."""
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
    bands: str = "v0_9"

    def aim_base(self) -> int:
        return self.aim_cost_base

    def draw_cost(self, quick_draw: bool) -> int:
        return 0 if quick_draw else self.draw_between_turns

    def aim_dice(self) -> int:
        return self.aim_die

    def precision_aim(self) -> bool:
        return self.aim_mode == "precision"

    def required_aims(self, band: str) -> int:
        if self.bands != "v0_9":
            return 0
        return {"medium": 1, "long": 2}.get(band, 0)

    def dropped_aim_dice(self, band: str) -> int:
        return self.required_aims(band)

    def penalty_dice(self, band: str) -> int:
        if self.bands != "minus_d6":
            return 0
        return {"medium": 1, "long": 2}.get(band, 0)

    def cover_bonus(self, level: int) -> int:
        return {1: self.half_cover, 2: self.three_quarter_cover}.get(level, 0)

    def dive_cover(self, level: int) -> int:
        return min(level, 2)  # total cover counts as three-quarters
