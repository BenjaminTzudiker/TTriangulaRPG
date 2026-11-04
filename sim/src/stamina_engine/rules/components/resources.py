"""HP, stamina, strain and character budgets (Packet: HP, Stamina, Strain, Costs)."""

from dataclasses import dataclass
from fractions import Fraction

from stamina_engine.core.mathx import round_half_up
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
        "Ledger CR-1",
        "Ledger CR-2",
        "Ledger CR-3",
        "Ledger CR-4",
        "Ledger CR-5",
        "Ledger CP-1",
        "Ledger CP-4",
        "Ledger CP-5",
    )
    allowed = {"start_stamina": frozenset({"max"})}

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

    def ability_budget(self, level: int) -> int:
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

    def hp_max(self, strength: int) -> int:
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

    def ability_budget(self, level: int) -> int:
        """Levels 0..L whose last digit grants an Ability Point (L1 gives 1, from level 0)."""
        return sum(1 for lv in range(0, level + 1) if str(lv % 10) in self.ability_digits)
