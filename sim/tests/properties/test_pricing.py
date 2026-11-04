"""Pricing properties: quotes are non-negative, monotone in the trackers, and unaffordable
declarations are refused (Assumptions register: declaring what you can't pay for)."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from stamina_engine.core.errors import Unaffordable
from stamina_engine.rules.pricing import Pricing, Track, Trackers
from stamina_engine.rules.ruleset import review_candidate, v0_9

PRICINGS = [Pricing(v0_9()), Pricing(review_candidate())]
small = st.integers(0, 12)


@given(st.sampled_from(PRICINGS), st.integers(1, 5), small, small, small)
def test_monotone(p: Pricing, base: int, k: int, actions: int, off: int) -> None:
    t, t_more = Trackers(actions, off), Trackers(actions + 1, off + 1)
    melee = p.melee_attack(base, k, t)
    assert all(x >= 0 for x in melee.parts)
    assert melee.total <= p.melee_attack(base, k, t_more).total
    assert melee.total <= p.melee_attack(base, k + 1, t).total
    assert p.ranged_attack(base, k, t).total <= p.ranged_attack(base, k, t_more).total
    assert p.off_turn_purchase(t).total <= p.off_turn_purchase(t_more).total
    assert melee.after(t) == Trackers(actions + k, off)
    shot = p.ranged_attack(base, k, t)
    assert shot.track is Track.ON_TURN and shot.after(t) == Trackers(actions + k, off)


@given(st.sampled_from(PRICINGS), st.integers(1, 5), st.integers(1, 6), small)
def test_unaffordable_refused(p: Pricing, base: int, k: int, stamina: int) -> None:
    cost = p.melee_attack(base, k).total
    if cost > stamina:
        with pytest.raises(Unaffordable):
            p.melee_attack(base, k, stamina=stamina)
    else:
        assert p.melee_attack(base, k, stamina=stamina).total == cost
    assert p.melee_attack(base, p.max_steps(base, stamina)).total <= stamina
