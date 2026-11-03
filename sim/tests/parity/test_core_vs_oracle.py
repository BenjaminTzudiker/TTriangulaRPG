"""Differential: integer helpers against tests/oracle/sim.py."""

from fractions import Fraction
from typing import Any

from stamina_engine.core.mathx import even_count, odd_count, round_half_up

STEP = {"none": 2, "light": 2, "medium": 3, "heavy": 4}


def test_odd_even_counts(oracle: Any) -> None:
    for v in range(-3, 11):
        assert odd_count(v) == oracle.odd_count(v)
        assert even_count(v) == oracle.even_count(v)
        for armor, step in STEP.items():
            assert even_count(v, step) == oracle.even_count(v, armor)


def test_round_half_up(oracle: Any) -> None:
    for level in range(0, 100):
        assert round_half_up(Fraction(level, 5)) == oracle.round_half_up(level / 5)
        assert round_half_up(Fraction(level, 10)) == oracle.round_half_up(level / 10)
