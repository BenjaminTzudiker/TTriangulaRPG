"""Build validation and derivation properties."""

from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from stamina_engine.core.errors import BudgetError, ConfigError
from stamina_engine.core.mathx import round_half_up
from stamina_engine.data import list_names
from stamina_engine.model.build import Attributes, Build, Loadout, load_build, validate
from stamina_engine.model.derive import derive
from stamina_engine.model.equipment import DamageExpr, load_table
from stamina_engine.rules.ruleset import v0_9

RULES = v0_9()
TABLE = load_table()


@pytest.mark.parametrize("name", list_names("builds"))
def test_library_builds_validate(name: str) -> None:
    validate(load_build(name), RULES, TABLE)


def test_budgets() -> None:
    res = RULES.resources
    assert [res.expertise_budget(lv) for lv in (1, 30, 99)] == [5, 16, 44]
    assert [res.ability_budget(lv) for lv in (1, 30, 99)] == [1, 10, 30]
    # The digit table produces round(L/5) and round(L/10) (Packet: Character Advancement).
    for level in range(100):
        stamina_digits = sum(1 for lv in range(1, level + 1) if lv % 10 in (3, 8))
        recovery_digits = sum(1 for lv in range(1, level + 1) if lv % 10 == 5)
        assert stamina_digits == round_half_up(Fraction(level, 5))
        assert recovery_digits == round_half_up(Fraction(level, 10))


def _build(level: int = 1, cores: tuple[str, ...] = ("fighter",), **attrs: int) -> Build:
    return Build("t", level, Attributes(**attrs), (("main", Loadout(armor="none")),), cores)


def test_over_budget_rejected() -> None:
    with pytest.raises(BudgetError):
        validate(_build(STR=3), RULES, TABLE)  # costs 6 of 5
    with pytest.raises(BudgetError):
        validate(_build(level=99, STR=7), RULES, TABLE)
    with pytest.raises(BudgetError):
        validate(_build(cores=("fighter", "rogue")), RULES, TABLE)  # 3 AP of 1
    validate(_build(level=12, cores=("fighter", "rogue")), RULES, TABLE)


def test_bad_loadouts_rejected() -> None:
    def lo(**kw: str) -> Build:
        return Build("t", 1, Attributes(STR=2), (("main", Loadout(**kw)),), ("fighter",))

    with pytest.raises(ConfigError):
        validate(lo(weapon="greatsword", grip="one"), RULES, TABLE)
    with pytest.raises(ConfigError):
        validate(lo(weapon="longsword", grip="two", off_hand="shield"), RULES, TABLE)
    with pytest.raises(ConfigError):
        validate(lo(weapon="dagger", off_hand="greatsword"), RULES, TABLE)


def test_dual_wield_and_proficiency() -> None:
    def md(off: str | None, cores: tuple[str, ...] = ("fighter",)) -> int:
        b = Build(
            "t", 1, Attributes(STR=2), (("m", Loadout(weapon="dagger", off_hand=off)),), cores
        )
        return derive(b, RULES).main.melee_defense

    assert md(None) == 2
    assert md("shortsword") == 3  # second proficient one-handed weapon
    assert md("shield") == 4
    assert md("shortsword", cores=()) == 1  # not proficient: base only


def test_damage_parse_round_trip() -> None:
    for weapon in TABLE.weapons:
        for _, expr in weapon.grips:
            assert DamageExpr.parse(str(expr)) == expr
    assert str(DamageExpr.parse("2d6 + 3×STR")) == "2d6 + 3*STR"
    with pytest.raises(ConfigError):
        DamageExpr.parse("1d6 + LUCK")


@given(
    st.integers(1, 99),
    st.integers(0, 6),
    st.integers(0, 6),
    st.integers(0, 6),
    st.sampled_from(["none", "light", "medium", "heavy"]),
)
def test_stamina_formula(level: int, s: int, a: int, f: int, armor: str) -> None:
    b = Build("t", level, Attributes(STR=s, AGI=a, FIN=f), (("m", Loadout(armor=armor)),))
    try:
        p = derive(b, RULES)
    except BudgetError:
        return
    assert p.hp_max == 6 + s
    assert p.stamina_max == 6 + p.hp_max + round_half_up(Fraction(level, 5))
    lo = p.main
    deficit = max(0, {"none": 0, "light": 0, "medium": 1, "heavy": 3}[armor] - s)
    effective = (lo.attributes.AGI, lo.attributes.FIN)
    assert effective == (a - deficit, f - deficit)
