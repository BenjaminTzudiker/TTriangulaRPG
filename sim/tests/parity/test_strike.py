"""The exact full strike against the review's Monte Carlo figures (Table 3, F1, Table 9).

Each printed figure is rounded (0.1 HP, 1%) and sampled, so a match means: within half a
rounding unit plus four standard errors of the review's sample size.
"""

import math
from fractions import Fraction

import pytest

from stamina_engine.analysis.strike import Strike, mirror_strike, opening_split
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.ruleset import RuleSet, review_sim

BUILDS = ("l1_sample", "l30_sample", "l99_sample")


def strike(
    rules: RuleSet, build: str, defense_bonus: int = 0, stamina: int | None = None
) -> Strike:
    p = derive(load_build(build), rules)
    return mirror_strike(p.main, p.stamina_max, p.hp_max, rules, stamina, defense_bonus)


def close_mean(s: Strike, printed: float, n: int) -> bool:
    mean = s.mean_injury
    var = sum((i - mean) ** 2 * p for i, p in s.injury.items())
    return abs(float(mean) - printed) <= 0.05 + 4 * math.sqrt(float(var) / n)


def close_p(p: Fraction, printed_pct: float, n: int) -> bool:
    x = float(p)
    return abs(100 * x - printed_pct) <= 0.5 + 400 * math.sqrt(x * (1 - x) / n) + 1e-9


def test_table3_opening_strike() -> None:
    """L1 4 steps/14 st: 6.1 HP, 34% down; L30 5/20: 5.3 of 9, 9%; L99 7/35: 14.0 of 12, 69%."""
    rules = review_sim()
    expected = {
        "l1_sample": (4, 14, 6.1, 34),
        "l30_sample": (5, 20, 5.3, 9),
        "l99_sample": (7, 35, 14.0, 69),
    }
    for build, (steps, cost, mean, down) in expected.items():
        s = strike(rules, build)
        assert (s.steps, s.cost) == (steps, cost)
        assert close_mean(s, mean, 20_000), build
        assert close_p(s.p_down, down, 20_000), build


def test_f1_alpha_strike_distribution() -> None:
    """F1: injury 0 HP 2%, 1-3 HP 31%, 4 HP 12%, 6 HP 20%, down 34%; the defender spends
    12-14 stamina 69% of the time; at 13 stamina it dies 50%, at 9, 65%."""
    rules = review_sim()
    s = strike(rules, "l1_sample")
    n = 20_000
    assert close_p(s.p_injury(0, 0), 2, n)
    assert close_p(s.p_injury(1, 3), 31, n)
    assert close_p(s.p_injury(4, 4), 12, n)
    assert close_p(s.p_injury(6, 6), 20, n)
    assert close_p(s.p_defender_spends(12, 14), 69, n)
    assert close_p(strike(rules, "l1_sample", stamina=13).p_down, 50, n)
    assert close_p(strike(rules, "l1_sample", stamina=9).p_down, 65, n)
    # Table 3's conditioning: crit and roll >= 30 in 48% of strikes; no crit, < 30 in 26%.
    p = derive(load_build("l1_sample"), rules)
    hot, cold = opening_split(p.main, 14, rules)
    assert close_p(hot, 48, 2_000) and close_p(cold, 26, 2_000)


TABLE9 = {  # variant: overrides, MD bonus, (L1, L30, L99) as (mean HP, % down)
    "baseline": ({}, 0, ((6.1, 34), (5.3, 9), (14.0, 69))),
    "A": ({"surcharge": {"slope": 2}}, 0, ((2.3, 6), (2.2, 0), (6.6, 0))),
    "B": ({"blocks": {"slope_den": 2}}, 0, ((2.8, 18), (0.9, 0), (6.4, 5))),
    "A+B": (
        {"surcharge": {"slope": 2}, "blocks": {"slope_den": 2}},
        0,
        ((0.4, 0), (0.0, 0), (0.4, 0)),
    ),
    "C": ({}, 2, ((1.6, 0), (1.5, 0), (7.8, 0))),
    "D": ({"crit": {"kind": "none"}}, 0, ((3.8, 1), (4.5, 0), (10.0, 0))),
}


@pytest.mark.parametrize("variant", sorted(TABLE9))
def test_table9_strikes(variant: str) -> None:
    overrides, bonus, cells = TABLE9[variant]
    rules = review_sim().override(overrides, name=variant) if overrides else review_sim()
    n = 6_000 if variant == "D" else 8_000
    for build, (mean, down) in zip(BUILDS, cells, strict=True):
        s = strike(rules, build, bonus)
        assert close_mean(s, mean, n), (variant, build, float(s.mean_injury))
        assert close_p(s.p_down, down, n), (variant, build, float(s.p_down))
