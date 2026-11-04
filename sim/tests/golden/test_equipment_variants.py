"""Equipment tables and the F4 / F8 variants (Review F4, F8; Packet: Weapons, Armor, Shields)."""

from dataclasses import replace

import pytest

from stamina_engine.cli import invoke
from stamina_engine.core.errors import ConfigError
from stamina_engine.experiments.runner import battle_for
from stamina_engine.experiments.scenario import scenario_from_toml, scenario_to_toml
from stamina_engine.model.build import Attributes, Build, Loadout, load_build
from stamina_engine.model.derive import derive
from stamina_engine.model.equipment import library_tables, load_table
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import preset

V09 = preset("v0.9")


def build(attrs: Attributes, lo: Loadout, name: str = "b") -> Build:
    return Build(name, 1, attrs, (("m", lo),), ("fighter",), budget="ignore")


def test_variant_tables_load_and_overlay() -> None:
    assert {"v0_9", "f8_die_upgrades", "f8_str_cap", "f4_shield_1", "f4_shield_str"} <= set(
        library_tables()
    )
    base, up = load_table(), load_table("f8_die_upgrades")
    assert [w.name for w in up.weapons] == [w.name for w in base.weapons]  # replaced in place
    assert str(up.weapon("greataxe").damage("two")) == "2d6 + STR + FIN"
    assert up.weapon("dagger") == base.weapon("dagger")
    with pytest.raises(ConfigError):
        load_table("nope")


def test_f8_option_1_die_upgrades() -> None:
    axe = build(
        Attributes(STR=2, AGI=1, FIN=1), Loadout(armor="medium", weapon="greataxe", grip="two")
    )
    assert derive(axe, V09).main.weapon.damage.flat == 6  # type: ignore[union-attr]  # 3 x STR
    assert derive(axe, V09, load_table("f8_die_upgrades")).main.weapon.damage.flat == 3  # type: ignore[union-attr]


def test_f8_option_3_strength_capped_at_die_size() -> None:
    table = load_table("f8_str_cap")
    strong = build(Attributes(STR=3), Loadout(armor="medium", weapon="greataxe", grip="two"))
    assert derive(strong, V09).main.weapon.damage.flat == 9  # type: ignore[union-attr]
    assert derive(strong, V09, table).main.weapon.damage.flat == 6  # type: ignore[union-attr]
    sword = load_build("l1_sample")  # 1d8 + STR + FIN: STR 2 is under the cap
    assert derive(sword, V09, table).main.weapon.damage == derive(sword, V09).main.weapon.damage  # type: ignore[union-attr]


def test_f8_option_2_light_weapons_skip_a_surcharge_point() -> None:
    rules = V09.override({"surcharge": {"light_exempt": 1}})
    p = Pricing(rules)
    assert p.melee_attack(1, 3, light=True).parts == (1, 1, 2)
    assert p.melee_attack(2, 3).parts == (2, 3, 4)  # others unchanged
    assert Pricing(V09).melee_attack(1, 3, light=True).parts == (1, 2, 3)  # as written
    dagger = derive(load_build("l1_caster_dagger"), rules).main.weapon
    assert dagger is not None and dagger.light


def test_f4_option_1_shields() -> None:
    sample = load_build("l1_sample")
    assert derive(sample, V09).main.melee_defense == 4
    light = derive(sample, V09, load_table("f4_shield_1")).main
    assert (light.melee_defense, light.ranged_defense) == (3, 3)
    weak = replace(sample, name="weak", attributes=Attributes(STR=1, AGI=1, FIN=1), budget="ignore")
    gated = derive(weak, V09, load_table("f4_shield_str")).main
    plain = derive(weak, V09).main
    assert (gated.attributes.AGI, gated.attributes.FIN) == (
        plain.attributes.AGI - 1,
        plain.attributes.FIN - 1,
    )


def test_f4_option_2_two_handers_and_agility_steps() -> None:
    rules = V09.override({"defenses": {"two_hander_bonus": 1, "agility_split": True}})
    two = load_build("l1_twohand")
    assert derive(two, rules).main.melee_defense == derive(two, V09).main.melee_defense + 1
    one = load_build("l1_sample")  # one-handed: no bonus
    assert derive(one, rules).main.melee_defense == derive(one, V09).main.melee_defense
    duelist = load_build("l1_duelist")  # AGI 2, unarmored: Dodge counts every point
    assert derive(duelist, V09).main.dodge_defense == 2
    assert derive(duelist, rules).main.dodge_defense == 3
    assert derive(duelist, rules).main.melee_defense == derive(duelist, V09).main.melee_defense + 1


def test_scenarios_select_a_table() -> None:
    text = """
[scenario]
name = "t"
equipment = "f4_shield_1"
trials = 1

[[combatant]]
id = "a"
build = "l1_sample"

[[combatant]]
id = "b"
build = "l1_sample"
"""
    s = scenario_from_toml(text)
    assert s.equipment == "f4_shield_1"
    assert scenario_from_toml(scenario_to_toml(s)).equipment == "f4_shield_1"
    b = battle_for(s, 1)
    assert b.state.get("a").gear.melee_defense == 3


def test_se_table_with_equipment() -> None:
    out = invoke(["table", "8", "--equipment", "f8_str_cap"])
    assert out.exit_code == 0 and "Equipment: f8_str_cap" in out.output
    assert invoke(["table", "8", "--equipment", "nope"]).exit_code != 0
