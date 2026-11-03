"""Block solver properties: affordable, and nothing affordable is strictly better."""

from fractions import Fraction

from hypothesis import given, settings
from hypothesis import strategies as st

from stamina_engine.rules.block_solver import BlockChoice, best_block, cheapest_zero_injury
from stamina_engine.rules.exchange import Blocks, resolve
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import RuleSet, review_candidate, v0_9

RULESETS = [v0_9(), review_candidate(), v0_9().override({"blocks": {"slope_den": 2}})]


@settings(max_examples=300)
@given(
    st.sampled_from(RULESETS),
    st.integers(0, 50),
    st.integers(0, 3),
    st.integers(0, 7),
    st.integers(0, 4),
    st.integers(0, 25),
    st.integers(1, 12),
    st.sampled_from([Fraction(3, 2), Fraction(3), Fraction(6)]),
)
def test_optimal_and_affordable(
    rules: RuleSet, d: int, c: int, v: int, a: int, s: int, hp: int, w: Fraction
) -> None:
    got = best_block(d, c, v, a, s, hp, rules, w)
    assert got.cost <= s
    pricing = Pricing(rules)
    for p in range(0, 12):
        for g in range(0, s + 1):
            cost = pricing.blocks(p, g).total
            if cost > s:
                break
            inj = resolve(d, c, v, a, Blocks(p, g), rules).injury
            other = BlockChoice(Blocks(p, g), cost, inj, inj >= hp, w * inj + cost)
            assert not other.key() < got.key()

    zero = cheapest_zero_injury(d, c, v, a, rules)
    if zero is not None:
        assert resolve(d, c, v, a, zero.blocks, rules).injury == 0
