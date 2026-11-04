"""Ranged attacks, exactly: review Table 5's static part, the shot distribution against the
roller, and the M3 switches (Packet: Ranged Attacks, Aim, Range Bands, Cover; Review F3)."""

import itertools
from collections import Counter
from fractions import Fraction

import pytest

from stamina_engine.analysis.ranged import bows, check_table5, shot
from stamina_engine.cli import invoke
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.block_solver import best_block
from stamina_engine.rules.exchange import roll_shot
from stamina_engine.rules.pricing import FRESH, Pricing
from stamina_engine.rules.ruleset import RuleSet, preset

V09 = preset("v0.9")


def test_table5_matches_the_review() -> None:
    """Every printed figure (8 shots x 4 targets x stamina, injury, % down) agrees with the
    exact value within its rounding and three standard errors of 4000 rolls."""
    checks = check_table5(V09)
    assert len(checks) == 32
    bad = [(c.cell.bow, c.cell.aims, c.cell.defender, c.ok) for c in checks if not all(c.ok)]
    assert not bad, bad


def test_two_aimed_longbow_shots() -> None:
    """Packet example: 5 + 1 + 2, then 5 + 3 + 4: 20 stamina (the surcharge carries on)."""
    p = Pricing(V09)
    first = p.ranged_attack(5, 2)
    second = p.ranged_attack(5, 2, first.after(FRESH))
    assert first.parts == (5, 1, 2) and second.parts == (5, 3, 4)
    assert first.total + second.total == 20


def enumerate_shot(rules: RuleSet, aims: int, band: str) -> dict[tuple[int, int], Fraction]:
    """Every face sequence through the roller, equally weighted."""
    name, weapon, fin = bows(rules)[0]  # shortbow 1d6 + 2
    rolled = (
        1 + max(0, aims - rules.ranged.dropped_aim_dice(band))
        if not rules.ranged.precision_aim()
        else 1
    )
    rolled += rules.ranged.penalty_dice(band)
    out: Counter[tuple[int, int]] = Counter()
    for faces in itertools.product(range(1, 7), repeat=rolled):
        a = roll_shot(weapon, aims, fin, band, rules, ScriptedDice(faces))
        out[(a.total, a.crit_dice)] += 1
    n = 6**rolled
    return {k: Fraction(v, n) for k, v in out.items()}


@pytest.mark.parametrize(
    ("overrides", "aims", "band"),
    [
        ({}, 1, "short"),
        ({}, 2, "medium"),
        ({}, 2, "long"),
        ({"crit": {"aim_dice_can_crit": False}}, 2, "short"),
        ({"ranged": {"aim_mode": "precision"}}, 2, "short"),
        ({"ranged": {"bands": "minus_d6"}}, 1, "medium"),
    ],
)
def test_exact_shot_matches_the_roller(overrides: dict, aims: int, band: str) -> None:
    rules = V09.override(overrides) if overrides else V09
    name, weapon, fin = bows(rules)[0]
    assert shot(weapon, aims, fin, band, rules) == enumerate_shot(rules, aims, band)


def test_range_bands() -> None:
    r = V09.ranged
    assert [r.band(d, (6, 12, 18)) for d in (1, 6, 7, 12, 13, 18, 19)] == [
        "short",
        "short",
        "medium",
        "medium",
        "long",
        "long",
        "beyond",
    ]
    assert (r.required_aims("medium"), r.required_aims("long"), r.required_aims("short")) == (
        1,
        2,
        0,
    )
    flat = V09.override({"ranged": {"bands": "minus_d6"}}).ranged
    assert flat.required_aims("long") == 0 and flat.penalty_dice("long") == 2
    assert V09.override({"ranged": {"bands": "none"}}).ranged.dropped_aim_dice("long") == 0


def test_cover_and_dive_values() -> None:
    r = V09.ranged
    assert [r.cover_bonus(level) for level in (0, 1, 2)] == [0, 2, 5]
    assert [r.dive_cover(level) for level in (0, 1, 2, 3)] == [0, 1, 2, 2]


def test_f3_option_1_dodge_folded_into_ranged_defense() -> None:
    folded = V09.override({"defenses": {"ranged_mode": "dodge_folded"}})
    duelist = load_build("l1_duelist")  # AGI 2, unarmored: +1 from even Agility
    assert derive(duelist, V09).main.ranged_defense == 1
    assert derive(duelist, folded).main.ranged_defense == 2
    sample = load_build("l1_sample")  # medium armor: AGI 1 gives nothing either way
    assert (
        derive(sample, folded).main.ranged_defense == derive(sample, V09).main.ranged_defense == 3
    )


def test_f3_option_2_flat_ranged_blocks() -> None:
    flat = V09.override({"blocks": {"ranged_flat": 2}})
    p = Pricing(flat)
    assert p.blocks(3, 0, ranged=True).parts == (2, 2, 2)
    assert p.blocks(3, 0).parts == (1, 2, 3)  # melee unchanged
    # Against a 20-damage shot at RD 3, armor 2: perfect blocks now cost 2 each.
    choice = best_block(20, 0, 3, 2, 14, 8, flat, ranged=True)
    assert choice.cost == 2 * choice.blocks.perfect + choice.blocks.grazing


def test_se_table_5() -> None:
    out = invoke(["table", "5"])
    assert out.exit_code == 0, out.output
    assert "Shortbow, 0 aim (3 st)" in out.output and "✗" not in out.output
