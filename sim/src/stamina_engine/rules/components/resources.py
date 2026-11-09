"""HP, stamina, strain and character budgets (Packet: HP, Stamina, Strain, Costs)."""

from dataclasses import dataclass
from fractions import Fraction

from stamina_engine.core.mathx import even_count, odd_count, round_half_up
from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class ResourceRule(Component):
    cites = (
        "Packet: HP",
        "Packet: Stamina",
        "Packet: Strain",
        "Packet: Going Over Your Maximum Strain",
        "Packet: Costs",
        "Packet: Character Advancement",
        "Packet: Strength",
        "Packet: Intelligence",
        "Packet: Class Trees",
        "Ledger CR-1",
        "Ledger CR-2",
        "Ledger CR-3",
        "Ledger CR-4",
        "Ledger CR-5",
        "Ledger CP-1",
        "Ledger CP-4",
        "Ledger CP-5",
    )
    allowed = {
        "start_stamina": frozenset({"max"}),
        # Maximum HP from Strength: + every point (v0.9), or + hp_per_even per even value (0.9.1).
        "hp_strength": frozenset({"every_point", "per_even"}),
        # Core ability cost: 1 + cores owned (v0.9), leaving out one per odd INT (0.9.1).
        "core_discount": frozenset({"none", "odd_intelligence"}),
        # Extra Ability Points from even Intelligence at levels 10/40/70, 20/50/80, 30/60/90.
        "bonus_ap": frozenset({"none", "even_intelligence"}),
    }

    def hp_max(self, strength: int) -> int:
        raise NotImplementedError

    def max_stamina(self, hp: int, level: int) -> int:
        raise NotImplementedError

    def recovery(self, level: int) -> int:
        raise NotImplementedError

    def strain_max(self, level: int) -> int:
        raise NotImplementedError

    def expertise_budget(self, level: int) -> int:
        raise NotImplementedError

    def ability_budget(self, level: int, intelligence: int = 0) -> int:
        raise NotImplementedError

    def core_cost(self, owned: int, intelligence: int = 0) -> int:
        """The AP price of a core ability when `owned` core abilities are already owned."""
        raise NotImplementedError

    def recovers_while_incapacitated(self) -> bool:
        raise NotImplementedError


@register("resources", "v0_9")
@dataclass(frozen=True)
class V09Resources(ResourceRule):
    """Formulas as written; budgets per the Assumptions register (pending designer)."""

    hp_base: int = 6
    stamina_base: int = 6
    stamina_level_div: int = 5
    floor_hp_term: bool = True  # max stamina at negative HP
    recovery_base: int = 4
    recovery_level_div: int = 10
    recover_while_incapacitated: bool = False
    strain_base: int = 6
    strain_level_div: int = 5
    start_stamina: str = "max"
    start_strain: int = 0
    attribute_max: int = 6
    expertise_base: int = 4
    expertise_digits: str = "1469"
    ability_digits: str = "027"
    hp_strength: str = "every_point"
    hp_per_even: int = 2
    core_discount: str = "none"
    bonus_ap: str = "none"

    def hp_max(self, strength: int) -> int:
        """v0.9: 6 + Strength. 0.9.1: 6 + 2 per even Strength; 0.9.2: 8 + 2 per even."""
        if self.hp_strength == "per_even":
            return self.hp_base + self.hp_per_even * even_count(strength)
        return self.hp_base + strength

    def max_stamina(self, hp: int, level: int) -> int:
        hp_term = max(hp, 0) if self.floor_hp_term else hp
        return self.stamina_base + hp_term + round_half_up(Fraction(level, self.stamina_level_div))

    def recovery(self, level: int) -> int:
        return self.recovery_base + round_half_up(Fraction(level, self.recovery_level_div))

    def strain_max(self, level: int) -> int:
        return self.strain_base + round_half_up(Fraction(level, self.strain_level_div))

    def expertise_budget(self, level: int) -> int:
        """4 + levels 1..L whose last digit grants Expertise (L1 gives 5)."""
        gained = sum(1 for lv in range(1, level + 1) if str(lv % 10) in self.expertise_digits)
        return self.expertise_base + gained

    def recovers_while_incapacitated(self) -> bool:
        return self.recover_while_incapacitated

    def ability_budget(self, level: int, intelligence: int = 0) -> int:
        """Levels 0..L whose last digit grants an Ability Point (L1 gives 1, from level 0).
        With bonus_ap, +1 at each of levels 10/40/70 (INT 2+), 20/50/80 (4+) and 30/60/90 (6),
        counted from the current Intelligence, so a raise applies retroactively."""
        base = sum(1 for lv in range(0, level + 1) if str(lv % 10) in self.ability_digits)
        if self.bonus_ap == "none":
            return base
        tens = range(1, even_count(intelligence) + 1)  # INT 2 -> 1, 4 -> 2, 6 -> 3
        bonus = sum(1 for t in tens for lv in (10 * t, 10 * t + 30, 10 * t + 60) if lv <= level)
        return base + bonus

    def core_cost(self, owned: int, intelligence: int = 0) -> int:
        """1, +1 per core already owned; with core_discount, one owned core per odd
        Intelligence value isn't counted (Packet: Intelligence's table)."""
        discount = odd_count(intelligence) if self.core_discount == "odd_intelligence" else 0
        return 1 + max(0, owned - discount)
