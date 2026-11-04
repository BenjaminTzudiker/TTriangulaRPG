"""Parity: review Appendix A, Tables 1 and 8, cell for cell; exact distribution checks."""

import random
import types
from fractions import Fraction
from typing import Any

from stamina_engine.analysis import dist
from stamina_engine.analysis.tables import Rounding, table1, table8
from stamina_engine.model.build import Attributes, Build, Loadout, load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.ruleset import review_sim, v0_9

REVIEW_TABLE1 = [
    (10, 36, 66, 120, 190),
    (5, 22, 47, 93, 155),
    (3, 8, 22, 38, 68),
    (2, 5, 12, 23, 38),
    (2, 4, 9, 18, 31),
    (2, 3, 8, 12, 23),
    (2, 4, 8, 17, 23),  # L30 sample, 9.5/step
    (2, 5, 12, 23, 38, 57, 80),  # L99, 11.5/step; the review prints k5 38 and k7 80
]

REVIEW_TABLE8 = [
    ("3.50", "2.33", "1.75", "1.40", "1.17"),
    ("4.50", "3.00", "2.25", "1.80", "1.50"),
    ("3.75", "3.00", "2.50", "2.14", "1.88"),
    ("4.25", "3.40", "2.83", "2.43", "2.12"),
    ("3.83", "3.29", "2.88", "2.56", "2.30"),
    ("4.33", "3.71", "3.25", "2.89", "2.60"),
]


def test_table1_matches_review() -> None:
    t = table1(review_sim(), Rounding.HALF_EVEN)
    assert t.attack_costs == (2, 5, 9, 14, 20)
    got = [r.costs for r in t.rows]
    assert got[:7] == REVIEW_TABLE1[:7]
    assert got[7][:5] == REVIEW_TABLE1[7][:5] and got[7][6] == 80
    assert [r.per_step for r in t.rows[6:]] == [Fraction(19, 2), Fraction(23, 2)]


def test_table1_half_up_differs_in_three_cells() -> None:
    """Assumptions register, mean rounding: the packet's half up moves three k=3 cells."""
    t = table1(v0_9(), Rounding.HALF_UP)
    diffs = {
        (i, k): (row.costs[k], REVIEW_TABLE1[i][k])
        for i, row in enumerate(t.rows)
        for k in range(5)
        if row.costs[k] != REVIEW_TABLE1[i][k]
    }
    assert diffs == {(0, 2): (78, 66), (1, 2): (56, 47), (2, 2): (23, 22)}


def test_table8_matches_review() -> None:
    rows = table8(v0_9())
    got = [tuple(Rounding.HALF_EVEN.fixed(x) for x in r.ratios) for r in rows]
    assert got == REVIEW_TABLE8
    # Exact values, so the match isn't a coincidence of rounding.
    assert [r.per_step for r in rows] == [
        Fraction(7, 2),
        Fraction(9, 2),
        Fraction(15, 2),
        Fraction(17, 2),
        Fraction(23, 2),
        Fraction(13),  # greataxe 2d6 + 6: 7 + 6
    ]
    assert rows[3].ratios[4] == Fraction(17, 8)  # 2.125: the review's 2.12 is half-even
    assert Rounding.HALF_UP.fixed(rows[3].ratios[4]) == "2.13"


def _sample_weapon(finesse: int = 1) -> Any:
    build = Build(
        "t",
        30,
        Attributes(STR=2, AGI=1, FIN=finesse),
        (("m", Loadout(weapon="longsword", grip="one")),),
        ("fighter",),
    )
    return derive(build, v0_9()).main.weapon


def test_distribution_basics() -> None:
    crit = v0_9().crit
    for name in ("l1_sample", "l1_greatsword", "l30_duelist"):
        w = derive(load_build(name), v0_9()).main.weapon
        assert w is not None
        for k in range(1, 5):
            j = dist.attack(w, k, crit)
            assert sum(j.values()) == 1
            assert dist.mean(j) == Fraction(w.damage.mean_x2 * k, 2)


def test_crit_chances_quoted_in_review() -> None:
    """FIN 1 on a d8 (25% per die): 2 dice 44%, 3 dice 58%, 4 dice 68%. FIN 3: 4 dice 85%."""
    crit = v0_9().crit
    w1, w3 = _sample_weapon(1), _sample_weapon(3)
    got = [round(100 * float(dist.p_any_crit(dist.attack(w1, k, crit)))) for k in (2, 3, 4)]
    assert got == [44, 58, 68]
    assert round(100 * float(dist.p_any_crit(dist.attack(w3, 4, crit)))) == 85


def test_greataxe_dice_crit_separately() -> None:
    build = Build(
        "t", 1, Attributes(STR=2), (("m", Loadout(weapon="greataxe", grip="two")),), ("fighter",)
    )
    axe = derive(build, v0_9()).main.weapon
    assert axe is not None
    j = dist.attack(axe, 1, v0_9().crit)
    assert j[(18, 2)] == Fraction(1, 36)  # 6 + 6 + 6: both dice critical


def test_monte_carlo_cross_check(oracle: Any, monkeypatch: Any) -> None:
    """Loose check of the exact distribution against the oracle's sampler."""
    rng = random.Random(7)
    monkeypatch.setattr(oracle, "random", types.SimpleNamespace(randint=rng.randint))
    ow = oracle.Weapon("ls", 2, 8, flat=3)
    n, k = 20_000, 4
    samples = [oracle.roll_damage(ow, k, 1) for _ in range(n)]
    j = dist.attack(_sample_weapon(1), k, v0_9().crit)
    mc_mean = sum(t for t, _ in samples) / n
    mc_crit = sum(1 for _, c in samples if c) / n
    assert abs(mc_mean - float(dist.mean(j))) < 0.15
    assert abs(mc_crit - float(dist.p_any_crit(j))) < 0.015
