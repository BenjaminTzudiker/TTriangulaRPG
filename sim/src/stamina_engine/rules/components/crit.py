"""Critical hits (Packet: Critical Hits).

Switches for shots (Assumptions register; the defaults are the review's reading, and 0.10.0
sets aim_dice_can_crit = false):
- aim_dice_can_crit: aim dice (free or bought) can be critical.
- aim_dice_widen: if they can, Finesse widens their range as the weapon's (true), or they
  crit only on their maximum (false).
- per_shot_cap: the most critical dice one shot counts (0: no cap). Melee steps are never
  capped. The solver study's configurations: A = aim dice can't crit (0.10.0); B = every die
  can, each counts; C' = aim dice crit only on a 6, cap 1; C = every die can, cap 1.
"""

from dataclasses import dataclass

from stamina_engine.core.errors import ConfigError
from stamina_engine.core.mathx import odd_count
from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class CritRule(Component):
    """Shared crit range and armor ignore; variants differ in the crit effect (finalize)."""

    max_widen: int = 3
    armor_ignore_per_die: int = 1
    aim_dice_can_crit: bool = True  # packet TODO; Assumptions register
    aim_dice_widen: bool = True  # aim dice crit on the weapon's widened range, or only a 6
    per_shot_cap: int = 0  # the most critical dice one shot counts (0: no cap); not melee

    cites = ("Packet: Critical Hits", "Ledger CB-6")

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.per_shot_cap < 0:
            raise ConfigError("crit: per_shot_cap is >= 0 (0: no cap)")

    def aim_widen(self, weapon_widen: int) -> int:
        """The critical range widening an aim die gets, or -1 if aim dice can't be critical
        (0: only its maximum face)."""
        if not self.aim_dice_can_crit:
            return -1
        return weapon_widen if self.aim_dice_widen else 0

    def shot_crits(self, crit_dice: int) -> int:
        """The critical dice a shot counts, after the per-shot cap."""
        return min(crit_dice, self.per_shot_cap) if self.per_shot_cap else crit_dice

    def widen(self, finesse: int) -> int:
        """Critical range widening: +1 per odd Finesse value, up to max_widen."""
        return min(self.max_widen, odd_count(finesse))

    def is_crit(self, face: int, size: int, widen: int) -> bool:
        """A die is critical on its maximum, or within widen of it."""
        return face >= size - widen

    def armor_ignored(self, crit_dice: int) -> int:
        """Each critical die ignores 1 armor."""
        return crit_dice * self.armor_ignore_per_die

    def finalize(self, after_armor: int, crit_dice: int) -> int:
        """Injury from what remains after armor (residual and leaks together)."""
        raise NotImplementedError


@register("crit", "double_once")
@dataclass(frozen=True)
class DoubleOnce(CritRule):
    """v0.9: if any die was critical, double what remains after armor, once per attack."""

    def finalize(self, after_armor: int, crit_dice: int) -> int:
        return after_armor * 2 if crit_dice > 0 else after_armor


@register("crit", "per_die_bonus")
@dataclass(frozen=True)
class PerDieBonus(CritRule):
    """Parity only (review-sim): +bonus per critical die after armor.

    Dropped as a design candidate (Assumptions register, ruled 2026-11-03). As in the review's
    simulator, the bonus is added even when nothing gets past armor.
    """

    bonus: int = 2

    def finalize(self, after_armor: int, crit_dice: int) -> int:
        return after_armor + self.bonus * crit_dice if crit_dice > 0 else after_armor


@register("crit", "per_die_if_through")
@dataclass(frozen=True)
class PerDieIfThrough(CritRule):
    """0.9.2: if any damage is left after blocks and armor, +bonus (1) per critical die. If
    blocks and armor stop all of it, critical dice add nothing."""

    bonus: int = 1

    def finalize(self, after_armor: int, crit_dice: int) -> int:
        return after_armor + self.bonus * crit_dice if after_armor > 0 else after_armor


@register("crit", "none")
@dataclass(frozen=True)
class NoDoubling(CritRule):
    """No crit effect after armor. Critical dice still ignore armor (review Table 9, D)."""

    def finalize(self, after_armor: int, crit_dice: int) -> int:
        return after_armor
