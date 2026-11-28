"""Melee, Ranged and Dodge Defense (Packet: Defenses).

Packet 0.11.3 shelves Dodge Defense (Packet: Not in This Version). No fight the engine plays uses
it; it stays derived for the presets that read earlier packets."""

from dataclasses import dataclass

from stamina_engine.core.mathx import even_count
from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class DefenseRule(Component):
    allowed = {
        "ranged_mode": frozenset({"v0_9", "dodge_folded"}),
        "armor_agility_mode": frozenset({"step", "str_gate"}),
        "armor_penalty_mode": frozenset({"attribute", "action_tax"}),
    }
    cites = (
        "Packet: Defenses",
        "Packet: Melee Defense",
        "Packet: Ranged Defense",
        "Packet: Armor",
        "Packet: Dash",
        "Packet: Not in This Version",
        "Ledger DF-1",
        "Ledger DF-2",
        "Ledger DF-3",
        "Ledger EQ-1",
        "Ledger H-11",
        "Ledger H-12",
        "Review F3",
        "Review F4",
    )

    def requires_proficiency(self) -> bool:
        return True

    def uses_armor_action_tax(self) -> bool:
        return False

    def dash_cost_extra(self, armor_name: str) -> int:
        return 0

    def melee(
        self,
        agility: int,
        finesse: int,
        agility_step: int,
        proficient_melee: bool,
        second_weapon: bool,
        shield_bonus: int,
        two_handed: bool = False,
        armor_name: str = "none",
        strength: int = 0,
    ) -> int:
        raise NotImplementedError

    def ranged(
        self,
        agility: int,
        shield_bonus: int,
        agility_step: int = 2,
        armor_name: str = "none",
        strength: int = 0,
    ) -> int:
        raise NotImplementedError

    def dodge(
        self,
        agility: int,
        agility_step: int,
        armor_name: str = "none",
        strength: int = 0,
    ) -> int:
        raise NotImplementedError


@register("defenses", "v0_9")
@dataclass(frozen=True)
class V09Defenses(DefenseRule):
    """Defenses as written. Attributes passed in are already lowered by armor penalties under
    armor_penalty_mode="attribute" (v0.9–v0.12.0).

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
    # Review F4 option 2: +1 Melee Defense for a proficient two-handed melee grip (0 as
    # written), and Agility's Dodge and Ranged bonus one step finer than Melee's (every point
    # unarmored or in light armor, every 2nd in medium, every 3rd in heavy).
    two_hander_bonus: int = 0
    agility_split: bool = False
    # Packet 0.12.1 (Ledger H-11): weapon proficiencies shelved; any melee weapon grants
    # the weapon and even-Finesse Melee Defense bonuses. Default True keeps earlier digests.
    require_proficiency: bool = True
    # Packet 0.12.1 (Ledger EQ-1): Strength-gated even Agility in medium/heavy armor
    # ("str_gate": medium <= even STR, heavy <= max(0, even STR - 1)), +1 stamina per action
    # per point of Strength below armor's requirement ("action_tax", no attribute penalties),
    # and +1 stamina per dash in heavy armor (base 2 instead of 1). Defaults keep earlier digests.
    armor_agility_mode: str = "step"
    armor_penalty_mode: str = "attribute"
    heavy_dash_extra: int = 0

    def requires_proficiency(self) -> bool:
        return self.require_proficiency

    def uses_armor_action_tax(self) -> bool:
        return self.armor_penalty_mode == "action_tax"

    def dash_cost_extra(self, armor_name: str) -> int:
        return self.heavy_dash_extra if armor_name == "heavy" else 0

    def _agi_bonus(
        self, agility: int, agility_step: int, armor_name: str, strength: int, *, fine: bool = False
    ) -> int:
        if self.armor_agility_mode == "str_gate":
            e_agi = even_count(agility)
            e_str = even_count(strength)
            if armor_name == "medium":
                return min(e_agi, e_str)
            if armor_name == "heavy":
                return min(e_agi, max(0, e_str - 1))
            return e_agi
        step = self._fine_step(agility_step) if fine else agility_step
        return even_count(agility, step)

    def melee(
        self,
        agility: int,
        finesse: int,
        agility_step: int,
        proficient_melee: bool,
        second_weapon: bool,
        shield_bonus: int,
        two_handed: bool = False,
        armor_name: str = "none",
        strength: int = 0,
    ) -> int:
        value = self.base if agility >= 0 else 0
        if two_handed:
            value += self.two_hander_bonus
        if proficient_melee:
            if finesse >= 0:
                value += self.proficient_weapon
            value += even_count(finesse)
            if second_weapon and shield_bonus == 0:
                value += self.second_weapon_bonus
        value += shield_bonus
        value += self._agi_bonus(agility, agility_step, armor_name, strength)
        return value

    def _fine_step(self, agility_step: int) -> int:
        return max(1, agility_step - 1) if self.agility_split else agility_step

    def ranged(
        self,
        agility: int,
        shield_bonus: int,
        agility_step: int = 2,
        armor_name: str = "none",
        strength: int = 0,
    ) -> int:
        value = (self.base if agility >= 0 else 0) + shield_bonus
        if self.ranged_mode == "dodge_folded":
            value += self._agi_bonus(agility, agility_step, armor_name, strength, fine=True)
        return value

    def dodge(
        self,
        agility: int,
        agility_step: int,
        armor_name: str = "none",
        strength: int = 0,
    ) -> int:
        return (self.base if agility >= 0 else 0) + self._agi_bonus(
            agility, agility_step, armor_name, strength, fine=True
        )
