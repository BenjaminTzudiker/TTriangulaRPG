"""Dice sources, streams and rounding."""

import ast
from fractions import Fraction
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st

from stamina_engine.core.dice import Dice, ScriptedDice, roll
from stamina_engine.core.errors import ConfigError, ScriptExhausted
from stamina_engine.core.mathx import round_half_even, round_half_up
from stamina_engine.core.rng import Streams, derive_seed

SRC = Path(__file__).resolve().parents[2] / "src" / "stamina_engine"


def test_same_seed_same_sequence() -> None:
    a = Streams(42).dice("battle-1")
    b = Streams(42).dice("battle-1")
    assert [a.roll(12) for _ in range(200)] == [b.roll(12) for _ in range(200)]


def test_named_streams_differ() -> None:
    s = Streams(42)
    a, b = s.dice("one"), s.dice("two")
    assert [a.roll(1000) for _ in range(20)] != [b.roll(1000) for _ in range(20)]


def test_known_sequence_is_stable() -> None:
    """Pins the stream derivation, so a change to it (which would change every log) is caught."""
    assert derive_seed(20261101, "pin") == 2498739197329648439
    d = Streams(20261101).dice("pin")
    assert [d.roll(6) for _ in range(8)] == [3, 4, 2, 5, 3, 6, 4, 6]


def test_scripted_dice() -> None:
    s = ScriptedDice([6, 3])
    assert roll(Dice(2, 8), s) == (6, 3)
    with pytest.raises(ScriptExhausted):
        s.roll(8)
    with pytest.raises(ConfigError):
        ScriptedDice([9]).roll(8)


@given(st.integers(-1000, 1000), st.integers(1, 20))
def test_round_half_up(n: int, d: int) -> None:
    x = Fraction(n, d)
    r = round_half_up(x)
    assert r - Fraction(1, 2) <= x < r + Fraction(1, 2)


def test_round_half_even_matches_python() -> None:
    for n in range(-50, 50):
        assert round_half_even(Fraction(n, 2)) == round(n / 2)


def test_no_global_random_in_engine() -> None:
    """Ground rule 7: engine code uses seeded streams, never the global random module."""
    offenders = []
    for path in SRC.rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id == "random"
                and node.attr != "Random"
            ):
                offenders.append(f"{path.name}:{node.lineno} random.{node.attr}")
            if isinstance(node, ast.ImportFrom) and node.module == "random":
                offenders.append(f"{path.name}:{node.lineno} from random import ...")
    assert not offenders, offenders
