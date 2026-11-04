"""Packet worked examples about cost: Melee Attacks, Aim, Off-Turn Escalation, Avoiding
Opportunity Attacks, Going Over Your Maximum Strain."""

import pytest

from stamina_engine.core.errors import Unaffordable
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.ruleset import v0_9

P = Pricing(v0_9())


def test_attack_step_table() -> None:
    """Steps (base-2 weapon, first actions this turn): 2, 2+3, 2+3+4."""
    assert [P.melee_attack(2, k).parts for k in (1, 2, 3)] == [(2,), (2, 3), (2, 3, 4)]
    assert [P.melee_attack(2, k).total for k in (1, 2, 3)] == [2, 5, 9]
    assert P.melee_attack(3, 2).total == 7  # greatsword


def test_attacking_again() -> None:
    """Melee Attack example: after two steps, the next attack's steps cost 4, then 5."""
    first = P.melee_attack(2, 2)
    again = P.melee_attack(2, 2, first.after(Trackers()))
    assert first.total == 5
    assert again.parts == (4, 5)


def test_two_aimed_longbow_shots() -> None:
    first = P.ranged_attack(5, 2)
    second = P.ranged_attack(5, 2, first.after(Trackers()))
    assert first.parts == (5, 1, 2)
    assert second.parts == (5, 3, 4)
    assert first.total + second.total == 20


def test_off_turn_escalation() -> None:
    """Move 1, move 1, dagger OA, move 1: 1 + 2 + 3 + 4 = 10; the OA needs a cap of 3."""
    t = Trackers()
    paid = []
    q = P.off_turn_purchase(t)
    paid.append(q.total)
    t = q.after(t)
    q = P.off_turn_purchase(t)
    paid.append(q.total)
    t = q.after(t)
    with pytest.raises(Unaffordable):
        P.opportunity_attack(base=1, steps=1, trackers=t, cap=2)
    q = P.opportunity_attack(base=1, steps=1, trackers=t, cap=3)
    paid.append(q.total)
    t = q.after(t)
    q = P.off_turn_purchase(t)
    paid.append(q.total)
    assert paid == [1, 2, 3, 4]
    assert sum(paid) == 10
    assert v0_9().opportunity.cap(3) == 3  # "such as Finesse 3"


def test_default_oa_cap() -> None:
    """At the default cap, only a base-1 weapon, and only before any other off-turn cost."""
    cap = v0_9().opportunity.cap(0)
    assert cap == 1
    P.opportunity_attack(1, 1, Trackers(), cap)
    with pytest.raises(Unaffordable):
        P.opportunity_attack(2, 1, Trackers(), cap)
    with pytest.raises(Unaffordable):
        P.opportunity_attack(1, 1, Trackers(off_turn_costs=1), cap)


def test_avoiding_opportunity_attacks() -> None:
    assert [P.avoid_opportunity(n).total for n in (2, 1, 1)] == [2, 1, 1]
    assert P.avoid_opportunity(2).after(Trackers()) == Trackers()  # no track


def test_strain_example() -> None:
    """Max strain 8, at 10, casting a 5-stamina, 2-strain spell: 5 + 4 = 9."""
    assert P.strain_ability(5, 2, Trackers(strain=10), strain_max=8).total == 9


def test_quick_reference_costs() -> None:
    assert P.extra_movement().total == 1
    after = P.extra_movement().after(Trackers(3, 2))
    assert (after.actions_this_turn, after.off_turn_costs) == (3, 2)  # not an action, no escalation
    assert [P.perfect_block(i) for i in range(1, 6)] == [1, 2, 3, 4, 5]
    assert P.blocks(3, 2).total == 1 + 2 + 3 + 1 + 1
    assert P.draw_between_turns(quick_draw=False).total == 1
    assert P.draw_between_turns(quick_draw=True).total == 0
