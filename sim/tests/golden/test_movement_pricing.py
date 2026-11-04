"""Movement and OA prices: the packet's numbers, Review F9/F10/F14 and the variant switches
(readings C6-C8, C11, C20-C24)."""

import pytest

from stamina_engine.core.errors import RulesError, Unaffordable
from stamina_engine.engine.events import DebtPaid, Indebted
from stamina_engine.engine.stateops import StateOps
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.model.state import BattleState, new_combatant
from stamina_engine.rules.pricing import FRESH, Pricing, Track, Trackers
from stamina_engine.rules.ruleset import RuleSet, preset

V09 = preset("v0.9")
P = Pricing(V09)


def variant(**kinds: dict[str, object]) -> RuleSet:
    return V09.override(dict(kinds))


def test_f10_extra_movement_arithmetic() -> None:
    """Review F10: AGI 1 with 10 spare stamina covers 26 squares; AGI 5 covers 48."""
    for agility, movement, per, squares in ((1, 6, 2, 26), (5, 8, 4, 48)):
        assert V09.movement.free_movement(agility) == movement
        assert V09.movement.extra_squares_per_purchase(agility) == per
        reach = P.max_move(
            on_turn=True,
            trackers=FRESH,
            stamina=10,
            free_left=movement,
            movement=movement,
            extra_squares=per,
        )
        assert reach == squares


def test_free_squares_first_then_banked_then_purchases() -> None:
    q = P.move(9, on_turn=True, trackers=FRESH, free_left=4, banked=1, movement=6, extra_squares=2)
    assert (q.free, q.banked, q.total, q.bought, q.leftover) == (4, 1, 2, (2, 2), 0)
    q = P.move(5, on_turn=True, trackers=FRESH, free_left=4, movement=6, extra_squares=2)
    assert (q.total, q.leftover) == (1, 1)  # one purchase, one square left over (C7)
    after = q.after(FRESH)
    assert (after.actions_this_turn, after.off_turn_costs, after.extra_purchases) == (0, 0, 1)
    with pytest.raises(Unaffordable):
        P.move(9, on_turn=True, trackers=FRESH, free_left=6, movement=6, stamina=1)


def test_off_turn_movement_escalates() -> None:
    """Off-turn: no free squares; purchases cost 1, 2, 3, 4 (Addendum 2's AGI-1 fleer)."""
    q = P.move(7, on_turn=False, trackers=FRESH, off_turn_squares=2)
    assert [p.total for p in q.purchases] == [1, 2, 3, 4]
    assert q.total == 10 and q.leftover == 1
    assert q.after(FRESH).off_turn_costs == 4
    assert all(p.track is Track.OFF_TURN for p in q.purchases)
    # Your own on-turn movement never makes it pricier (Packet: Off-Turn Movement).
    later = P.move(
        2,
        on_turn=False,
        trackers=Trackers(actions_this_turn=3, extra_purchases=5),
        off_turn_squares=2,
    )
    assert later.total == 1
    capped = Pricing(variant(off_turn={"purchase_cap": 2}))
    with pytest.raises(Unaffordable, match="at most 2"):
        capped.move(7, on_turn=False, trackers=FRESH, off_turn_squares=2)


def test_f10_option_1_one_square_per_extra_purchase() -> None:
    rules = variant(movement={"extra_squares": "one"})
    assert rules.movement.extra_squares_per_purchase(5) == 1
    assert rules.movement.squares_per_purchase(5) == 4  # off-turn keeps 1 + odd AGI (C23)
    assert derive(load_build("l1_sample"), rules).main.extra_squares_per_purchase == 1


def test_f10_option_2_purchases_capped_at_movement() -> None:
    p = Pricing(variant(movement={"extra_cap": "free_movement"}))
    # AGI 1: Movement 6, 2 squares a purchase, so 6 bought squares at most (3 purchases).
    q = p.move(12, on_turn=True, trackers=FRESH, free_left=6, movement=6, extra_squares=2)
    assert q.total == 3
    with pytest.raises(Unaffordable, match="capped"):
        p.move(13, on_turn=True, trackers=FRESH, free_left=6, movement=6, extra_squares=2)
    # AGI 3: Movement 7, 3 a purchase: 3 + 3 + 1, the last purchase cut short.
    q = p.move(14, on_turn=True, trackers=FRESH, free_left=7, movement=7, extra_squares=3)
    assert q.bought == (3, 3, 1)


def test_f9_option_1_cap_from_weapon_base() -> None:
    rules = variant(opportunity={"cap_rule": "weapon_base"})
    assert rules.opportunity.cap(0, 2) == 2  # a FIN-0 spearman can now make an OA
    assert rules.opportunity.cap(1, 2) == 3
    assert V09.opportunity.cap(0, 2) == 1  # as written: base 2 never fits the cap of 1
    spear = derive(load_build("l1_sample"), rules).main
    assert spear.oa_cap == 3  # longsword base 2 + odd FIN 1


def test_f9_option_2_avoidance_costs_the_attackers_cap() -> None:
    p = Pricing(variant(opportunity={"avoid_price": "attacker_cap"}))
    assert p.avoid_opportunity(2, caps=[2, 3]).parts == (2, 3)
    assert P.avoid_opportunity(2, caps=[2, 3]).parts == (1, 1)


def test_f9_option_3_avoidance_on_the_off_turn_track() -> None:
    p = Pricing(variant(opportunity={"avoid_track": "off_turn"}))
    q = p.avoid_opportunity(3, trackers=FRESH, on_turn=False)
    assert q.parts == (1, 2, 3) and q.track is Track.OFF_TURN  # the third enemy costs 3
    assert p.avoid_opportunity(1, trackers=q.after(FRESH), on_turn=True).total == 4
    only = Pricing(variant(opportunity={"avoid_track": "off_turn_only"}))
    assert only.avoid_opportunity(3, on_turn=True).parts == (1, 1, 1)
    assert only.avoid_opportunity(3, on_turn=False).parts == (1, 2, 3)


def test_f14_avoidance_debt() -> None:
    with pytest.raises(Unaffordable):
        P.avoid_opportunity(2, stamina=1)
    rules = variant(opportunity={"avoid_debt": True})
    q = Pricing(rules).avoid_opportunity(2, stamina=1)
    assert q.total == 2
    c = new_combatant("a", "red", derive(load_build("l1_sample"), rules))
    ops = StateOps(BattleState((c,)), rules, [], check=True)
    c.stamina = 1
    with pytest.raises(Unaffordable):
        ops.spend(c, q, "avoid")
    ops.spend(c, q, "avoid", allow_debt=True)
    assert (c.stamina, c.debt) == (0, 1)
    ops.recover(c, 4)  # debt first, then stamina
    assert (c.stamina, c.debt) == (3, 0)
    assert [type(e) for e in ops.log if isinstance(e, Indebted | DebtPaid)] == [Indebted, DebtPaid]
    c.debt = 0
    with pytest.raises(RulesError):
        c.dying = rules.dying.take_damage(c.dying, 100)
        ops.spend(c, q, "avoid", allow_debt=True)


def test_move_prices_match_move_quotes() -> None:
    for on_turn in (True, False):
        for rules in (V09, variant(movement={"extra_cap": "free_movement"})):
            p = Pricing(rules)
            args = {
                "free_left": 3,
                "banked": 1,
                "movement": 6,
                "extra_squares": 2,
                "off_turn_squares": 3,
            }
            prices = p.move_prices(on_turn=on_turn, trackers=FRESH, stamina=9, **args)
            for n, price in enumerate(prices):
                assert p.move(n, on_turn=on_turn, trackers=FRESH, **args).total == price
            n = len(prices)
            with pytest.raises(Unaffordable):
                p.move(n, on_turn=on_turn, trackers=FRESH, stamina=9, **args)
            assert p.max_move(on_turn=on_turn, trackers=FRESH, stamina=9, **args) == n - 1
