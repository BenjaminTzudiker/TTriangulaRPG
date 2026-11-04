"""Melee, Ranged and Dodge Defense (Packet: Defenses)."""

from dataclasses import dataclass

from stamina_engine.core.mathx import even_count
from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class DefenseRule(Component):
    allowed = {"ranged_mode": frozenset({"v0_9", "dodge_folded"})}
    cites = (
        "Packet: Defenses",
        "Packet: Melee Defense",
        "Packet: Ranged Defense",
        "Packet: Dodge Defense",
        "Ledger DF-1",
        "Ledger DF-2",
        "Ledger DF-3",
        "Review F3",
    )

    def melee(
        self,
        agility: int,
        finesse: int,
        agility_step: int,
        proficient_melee: bool,
        second_weapon: bool,
        shield_bonus: int,
    ) -> int:
        raise NotImplementedError

    def ranged(self, agility: int, shield_bonus: int, agility_step: int = 2) -> int:
        raise NotImplementedError

    def dodge(self, agility: int, agility_step: int) -> int:
        raise NotImplementedError


@register("defenses", "v0_9")
@dataclass(frozen=True)
class V09Defenses(DefenseRule):
    """Defenses as written. Attributes passed in are already lowered by armor penalties.

    proficient_melee: wielding a proficient melee weapon. Without one, only the base and a
    held shield count (Assumptions register: Melee Defense with no melee weapon wielded).
    second_weapon: a proficient one-handed melee weapon in the off hand, no shield.
    """

    base: int = 1
    proficient_weapon: int = 1
    second_weapon_bonus: int = 1
    # Review F3 option 1: fold Dodge into Ranged Defense (RD = 1 + even AGI, armor-adjusted,
    # + shield). v0_9 is as written: 1 + shield.
    ranged_mode: str = "v0_9"

    def melee(
        self,
        agility: int,
        finesse: int,
        agility_step: int,
        proficient_melee: bool,
        second_weapon: bool,
        shield_bonus: int,
    ) -> int:
        value = self.base if agility >= 0 else 0
        if proficient_melee:
            if finesse >= 0:
                value += self.proficient_weapon
            value += even_count(finesse)
            if second_weapon and shield_bonus == 0:
                value += self.second_weapon_bonus
        value += shield_bonus
        value += even_count(agility, agility_step)
        return value

    def ranged(self, agility: int, shield_bonus: int, agility_step: int = 2) -> int:
        value = (self.base if agility >= 0 else 0) + shield_bonus
        if self.ranged_mode == "dodge_folded":
            value += even_count(agility, agility_step)
        return value

    def dodge(self, agility: int, agility_step: int) -> int:
        return (self.base if agility >= 0 else 0) + even_count(agility, agility_step)
