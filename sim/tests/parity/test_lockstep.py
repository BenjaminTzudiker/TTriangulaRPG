"""Lockstep parity: the engine under review-sim and the review's simulator, fed the same
seed, fight identical fights (every attack's steps, roll, crit dice, blocks, block cost and
injury; the winner, rounds and first mover; final HP and stamina).

These are the configurations behind the review's published tables. The default run uses a
few fights each; `pytest -m slow` runs 200.
"""

from collections.abc import Callable
from typing import Any

import pytest

from stamina_engine.experiments.oracle_bridge import (
    Knobs,
    engine_duel,
    engine_one_v_three,
    oracle_duel,
    oracle_one_v_three,
)
from stamina_engine.model.build import load_build
from stamina_engine.rules.ruleset import review_sim

FAST, FULL = 4, 200
COUNTS = [FAST, pytest.param(FULL, marks=pytest.mark.slow)]

BUILDS = {  # library build -> make_fighter(level, variant)
    "l1_sample": (1, "sample"),
    "l1_twohand": (1, "twohand"),
    "l1_greatsword": (1, "greatsword"),
    "l1_heavy": (1, "heavy"),
    "l1_duelist": (1, "duelist"),
    "l30_sample": (30, "sample"),
    "l30_strbrute": (30, "strbrute"),
    "l30_duelist": (30, "duelist"),
    "l30_heavy": (30, "heavy"),
    "l99_sample": (99, "sample"),
}

TABLE2 = ["alpha", "fixed:3", "fixed:2", "fixed:1", "reserve:5", "chipkill"]

DUELS: list[tuple[str, str, str, str, Knobs]] = [
    # Table 2: the level-1 strategy matrix.
    *[("l1_sample", "l1_sample", a, b, Knobs()) for a in TABLE2 for b in TABLE2],
    # Table 3: levels 30 and 99, and the look-ahead.
    ("l1_sample", "l1_sample", "lookahead", "lookahead", Knobs()),
    ("l30_sample", "l30_sample", "alpha", "alpha", Knobs()),
    ("l30_sample", "l30_sample", "fixed:2", "fixed:2", Knobs()),
    ("l30_sample", "l30_sample", "chipkill", "chipkill", Knobs()),
    ("l30_sample", "l30_sample", "alpha", "fixed:2", Knobs()),
    ("l30_strbrute", "l30_sample", "alpha", "alpha", Knobs()),
    ("l99_sample", "l99_sample", "alpha", "alpha", Knobs()),
    ("l99_sample", "l99_sample", "chipkill", "chipkill", Knobs()),
    # Table 7: armored vs unarmored.
    *[
        (a, b, p, p, Knobs())
        for a, b in [
            ("l1_heavy", "l1_duelist"),
            ("l1_sample", "l1_twohand"),
            ("l1_sample", "l1_greatsword"),
            ("l30_heavy", "l30_duelist"),
            ("l30_sample", "l30_duelist"),
        ]
        for p in ("chipkill", "alpha", "fixed:2")
    ],
    # Table 9 and the Addendum: surcharge, block-slope and crit variants.
    *[
        ("l1_sample", "l1_sample", p, p, knobs)
        for knobs in [
            Knobs(step_slope=2),
            Knobs(block_slope=0.5),
            Knobs(step_slope=2, block_slope=0.5),
            Knobs(crit_mode="none"),
            Knobs(crit_mode="linear1"),
            Knobs(crit_mode="linear2"),
            Knobs(step_slope=2, crit_mode="linear2"),
        ]
        for p in ("alpha", "chipkill")
    ],
    ("l30_sample", "l30_sample", "fixed:2", "fixed:2", Knobs(step_slope=2)),
]

ONE_V_THREE = [  # Table 4
    ("l1_sample", "fixed:2", True),
    ("l1_sample", "fixed:1", True),
    ("l1_sample", "chipkill", True),
    ("l1_sample", "fixed:2", False),
    ("l1_heavy", "fixed:2", True),
]


def maker(build: str) -> Callable[[Any], Any]:
    level, variant = BUILDS[build]
    return lambda sim: sim.make_fighter(level, variant)


def _id(case: tuple[str, str, str, str, Knobs]) -> str:
    a, b, pa, pb, k = case
    return f"{a}-{pa}_vs_{b}-{pb}_s{k.step_slope}b{k.block_slope}{k.crit_mode}"


@pytest.mark.parametrize("fights", COUNTS)
@pytest.mark.parametrize("case", DUELS, ids=[_id(c) for c in DUELS])
def test_duels_match_the_oracle(case: tuple[str, str, str, str, Knobs], fights: int) -> None:
    a, b, pa, pb, knobs = case
    rules = review_sim().override(knobs.overrides(), name="review-sim")
    ba, bb = load_build(a), load_build(b)
    for seed in range(fights):
        expected = oracle_duel(maker(a), maker(b), pa, pb, knobs, seed)
        assert engine_duel(rules, ba, bb, pa, pb, seed) == expected, seed


@pytest.mark.parametrize("fights", COUNTS)
@pytest.mark.parametrize("case", ONE_V_THREE, ids=lambda c: f"{c[0]}-{c[1]}-{c[2]}")
def test_one_v_three_matches_the_oracle(case: tuple[str, str, bool], fights: int) -> None:
    defender, policy, def_attacks = case
    rules = review_sim()
    variant = BUILDS[defender][1]
    for seed in range(fights):
        expected = oracle_one_v_three(variant, policy, def_attacks, Knobs(), seed)
        got = engine_one_v_three(rules, load_build(defender), policy, def_attacks, seed)
        if expected.winner is None:
            # The oracle plays a defender who downed all three out to round 20; the engine
            # ends the fight when the attackers' side is out. Everything else matches.
            got = type(got)(got.winner, expected.rounds, got.first, got.attacks, got.final)
        assert got == expected, seed
