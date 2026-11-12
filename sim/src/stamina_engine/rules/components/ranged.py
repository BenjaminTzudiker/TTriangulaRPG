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

Packet 0.10.0 (all off by default, so v0.9's presets keep their rules and digests):
- bands = linear: each weapon has a band width (+1 square per odd Finesse, -1 per point of
  Strength below its requirement; at 0 or less it can't shoot). No penalty out to one band
  width, band_penalty (2) off the total for each further band, full or partial; no maximum
  range.
- shot_action: a shot is an action (shot cost + the on-turn surcharge), not a flat cost.
- aim_finesse = false: aim steps add their die only. free_aim_dice: dice every shot rolls
  as aim without being an action.
- aim_limit = damage_roll: the HP a shot takes can't exceed the weapon's damage roll (its
  dice plus its Strength terms; Precise weapons the higher of that and Finesse), applied
  after armor and before the critical bonus.
- range_measured = after_reaction: the range penalty is measured from where the target
  ends its reaction to the shot.
- reaction_bonus: Ranged Defense against a shot the target moved in reaction to.

Reaction switches the designer may weigh against 0.10.0 (defaults keep its rules):
- defense_timing: after_reaction (0.10.0) judges Melee vs Ranged Defense from where the
  target ends its reaction; declaration, from where it was when the shot was declared.
  Cover is always judged after the reaction.
- reaction_purchases: the most off-turn purchases a reaction to a shot may buy (0: no cap).
- swap_single_purchase: the defense swap (into or out of the shooter's being in reach)
  counts only if the reaction took a single purchase; otherwise the declaration's defense
  stands. Cover and range are unaffected.
- crit_inside_limit: the critical bonus counts toward the aim limit (0.10.0: it comes after).
"""

from dataclasses import dataclass

from stamina_engine.core.errors import ConfigError
from stamina_engine.core.mathx import odd_count
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
        "Packet: Actions and the On-Turn Surcharge",
        "Packet: Procedure",
        "Packet: Weapon Properties",
    )
    allowed = {
        "aim_mode": frozenset({"damage", "precision"}),
        "bands": frozenset({"v0_9", "minus_d6", "none", "linear"}),
        "dive": frozenset({"half_is_half"}),
        "point_blank_order": frozenset({"dive_oas_first"}),
        "aim_limit": frozenset({"none", "damage_roll"}),
        "range_measured": frozenset({"declaration", "after_reaction"}),
        "defense_timing": frozenset({"declaration", "after_reaction"}),
    }

    def aim_base(self) -> int:
        raise NotImplementedError

    def draw_cost(self, quick_draw: bool) -> int:
        raise NotImplementedError

    def band(self, distance: int, ranges: tuple[int, ...], band_width: int = 0) -> str:
        """short, medium, long or beyond, from the weapon's three ranges. With linear bands,
        "band N" (band 1 is short) from the wielder's band width, or beyond if it can't
        shoot at all."""
        if self.uses_band_width():
            if band_width <= 0:
                return "beyond"
            return f"band {self.band_number(distance, band_width)}"
        for name, limit in zip(BANDS, ranges, strict=False):
            if distance <= limit:
                return name
        return "beyond"

    def uses_band_width(self) -> bool:
        """Do ranged weapons use a band width (0.10.0) rather than three ranges?"""
        return False

    def band_number(self, distance: int, band_width: int) -> int:
        """Which band a distance falls in: 1 out to one band width, then 2, 3... (a partial
        band counts as a full one)."""
        return max(1, -(-distance // band_width))

    def band_width(self, weapon_width: int, finesse: int, strength: int, requirement: int) -> int:
        """The wielder's band width, in squares (0 or less: it can't shoot the weapon)."""
        raise NotImplementedError

    def range_penalty(self, distance: int, band_width: int) -> int:
        """Points off the shot's total at this distance (linear bands)."""
        raise NotImplementedError

    def shot_is_action(self) -> bool:
        raise NotImplementedError

    def aim_adds_finesse(self) -> bool:
        raise NotImplementedError

    def free_aims(self) -> int:
        """Aim dice every shot rolls without being an action."""
        raise NotImplementedError

    def limits_wounds(self) -> bool:
        """Is a shot's HP loss capped at the weapon's damage roll (the aim limit)?"""
        raise NotImplementedError

    def measures_after_reaction(self) -> bool:
        raise NotImplementedError

    def reaction_defense(self) -> int:
        """Ranged Defense against a shot the target moved in reaction to."""
        raise NotImplementedError

    def defense_after_reaction(self) -> bool:
        """Is Melee vs Ranged Defense judged from where the target ends its reaction?"""
        raise NotImplementedError

    def reaction_purchase_cap(self) -> int | None:
        """The most off-turn purchases a reaction to a shot may buy (None: no cap)."""
        raise NotImplementedError

    def swap_needs_single_purchase(self) -> bool:
        raise NotImplementedError

    def crit_inside_limit(self) -> bool:
        """Does the critical bonus count toward the aim limit?"""
        raise NotImplementedError

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
    band_penalty: int = 2
    shot_action: bool = False
    aim_finesse: bool = True
    free_aim_dice: int = 0
    aim_limit: str = "none"
    range_measured: str = "declaration"
    reaction_bonus: int = 0
    defense_timing: str = "after_reaction"
    reaction_purchases: int = 0
    swap_single_purchase: bool = False
    crit_in_limit: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()
        if min(self.free_aim_dice, self.band_penalty, self.reaction_bonus) < 0:
            raise ConfigError("ranged: free_aim_dice, band_penalty and reaction_bonus are >= 0")
        if self.reaction_purchases < 0:
            raise ConfigError("ranged: reaction_purchases is >= 0 (0: no cap)")

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

    def uses_band_width(self) -> bool:
        return self.bands == "linear"

    def band_width(self, weapon_width: int, finesse: int, strength: int, requirement: int) -> int:
        if not self.uses_band_width():
            return 0
        return weapon_width + odd_count(finesse) - max(0, requirement - strength)

    def range_penalty(self, distance: int, band_width: int) -> int:
        if not self.uses_band_width() or band_width <= 0:
            return 0
        return self.band_penalty * (self.band_number(distance, band_width) - 1)

    def shot_is_action(self) -> bool:
        return self.shot_action

    def aim_adds_finesse(self) -> bool:
        return self.aim_finesse

    def free_aims(self) -> int:
        return self.free_aim_dice

    def limits_wounds(self) -> bool:
        return self.aim_limit == "damage_roll"

    def measures_after_reaction(self) -> bool:
        return self.range_measured == "after_reaction"

    def reaction_defense(self) -> int:
        return self.reaction_bonus

    def defense_after_reaction(self) -> bool:
        return self.defense_timing == "after_reaction"

    def reaction_purchase_cap(self) -> int | None:
        return self.reaction_purchases or None

    def swap_needs_single_purchase(self) -> bool:
        return self.swap_single_purchase

    def crit_inside_limit(self) -> bool:
        return self.crit_in_limit
