"""The exact expected-outcome estimator against the oracle's sampled expected_block_outcome."""

import math
import random
import types
from fractions import Fraction
from typing import Any

import pytest

from stamina_engine.agents.estimates import Target, exact_estimate
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.ruleset import review_sim

CASES = [  # (attacker build, oracle variant, steps, defender stamina)
    ("l1_sample", (1, "sample"), 4, 14),
    ("l1_sample", (1, "sample"), 2, 9),
    ("l30_sample", (30, "sample"), 5, 21),
    ("l1_greatsword", (1, "greatsword"), 3, 14),
]


@pytest.mark.parametrize(("build", "variant", "steps", "stamina"), CASES)
def test_exact_matches_sampled(
    oracle: Any,
    monkeypatch: pytest.MonkeyPatch,
    build: str,
    variant: tuple[int, str],
    steps: int,
    stamina: int,
) -> None:
    rules = review_sim()
    me = derive(load_build(build), rules).main
    assert me.weapon is not None
    att = oracle.make_fighter(*variant)
    dfn = oracle.make_fighter(*variant)
    dfn.stamina = stamina
    target = Target(dfn.melee_defense(), dfn.armor_value(), stamina, dfn.hp)
    exact = exact_estimate(me.weapon, steps, target, rules, Fraction(3))
    n = 6000
    monkeypatch.setattr(oracle, "random", types.SimpleNamespace(randint=random.Random(1).randint))
    inj, cost, down = oracle.expected_block_outcome(att, dfn, steps, samples=n)
    sd_down = math.sqrt(float(exact.p_down) * (1 - float(exact.p_down)) / n) + 1e-9
    assert abs(down - float(exact.p_down)) < 5 * sd_down
    assert abs(inj - float(exact.injury)) < 0.25
    assert abs(cost - float(exact.cost)) < 0.25
