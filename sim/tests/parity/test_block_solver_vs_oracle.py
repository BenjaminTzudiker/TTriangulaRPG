"""Differential: best_block against tests/oracle/sim.py on random inputs.

Inputs keep w x injury + cost below 1000 for every option, where the oracle's +1000
incapacitation penalty and the engine's lexicographic rule agree (Assumptions register).
Block slopes are 1 and 1/2 only (see test_pricing_vs_oracle).
"""

import random
from fractions import Fraction
from typing import Any

import pytest

from stamina_engine.rules.block_solver import best_block
from stamina_engine.rules.ruleset import v0_9

CASES = 10_000
CRIT = {
    "double": {"kind": "double_once"},
    "linear1": {"kind": "per_die_bonus", "bonus": 1},
    "linear2": {"kind": "per_die_bonus", "bonus": 2},
    "none": {"kind": "none"},
}
SLOPES = {1.0: (1, 1), 0.5: (1, 2)}
WS = (Fraction(3, 2), Fraction(3), Fraction(6))


@pytest.mark.parametrize("slope", sorted(SLOPES))
@pytest.mark.parametrize("mode", sorted(CRIT))
def test_best_block(oracle: Any, mode: str, slope: float) -> None:
    oracle.CRIT_MODE, oracle.BLOCK_SLOPE = mode, slope
    num, den = SLOPES[slope]
    rules = v0_9().override({"crit": CRIT[mode], "blocks": {"slope_num": num, "slope_den": den}})
    rng = random.Random(f"{mode}-{slope}")
    for _ in range(CASES):
        d, crits = rng.randint(0, 60), rng.choice([0, 0, 0, 1, 1, 2, 3])
        v, a, s, hp = rng.randint(0, 7), rng.randint(0, 4), rng.randint(0, 30), rng.randint(1, 12)
        w = rng.choice(WS)
        assert w * 2 * (d + 3 * crits) + s < 1000
        expected = oracle.best_block(d, crits, v, a, s, hp, w=float(w))
        got = best_block(d, crits, v, a, s, hp, rules, w)
        assert (got.blocks.perfect, got.blocks.grazing, got.cost, got.injury) == expected, (
            d,
            crits,
            v,
            a,
            s,
            hp,
            w,
        )
