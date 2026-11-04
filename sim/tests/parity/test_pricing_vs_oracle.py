"""Differential: attack_cost, max_steps and block_cost against tests/oracle/sim.py."""

import random
from typing import Any

import pytest

from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.ruleset import v0_9

CASES = 10_000


@pytest.mark.parametrize("slope", [1, 2])
def test_attack_cost_and_max_steps(oracle: Any, slope: int) -> None:
    oracle.STEP_SLOPE = slope
    pricing = Pricing(v0_9().override({"surcharge": {"slope": slope}}))
    rng = random.Random(slope)
    for _ in range(CASES):
        base, k, prior, stamina = (
            rng.randint(1, 5),
            rng.randint(0, 8),
            rng.randint(0, 6),
            rng.randint(0, 60),
        )
        t = Trackers(actions_this_turn=prior)
        assert pricing.melee_attack(base, k, t).total == oracle.attack_cost(base, k, prior)
        assert pricing.max_steps(base, stamina, t) == oracle.max_steps(base, stamina, prior)


@pytest.mark.parametrize(("oracle_slope", "num", "den"), [(1.0, 1, 1), (0.5, 1, 2)])
def test_block_cost(oracle: Any, oracle_slope: float, num: int, den: int) -> None:
    """Only slopes 1 and 1/2: the oracle floors a float with a 1e-9 epsilon, which differs
    from exact integer arithmetic at slopes like 1/3."""
    oracle.BLOCK_SLOPE = oracle_slope
    pricing = Pricing(v0_9().override({"blocks": {"slope_num": num, "slope_den": den}}))
    for p in range(60):
        assert pricing.blocks(p, 0).total == oracle.block_cost(p)
