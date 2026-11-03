"""Packet: Dying and Death, Example: System Shock."""

from stamina_engine.rules.components.dying import DyingState
from stamina_engine.rules.ruleset import v0_9

SHOCK = v0_9().dying


def test_system_shock_example() -> None:
    s = SHOCK.take_damage(DyingState(hp=3), 5)
    assert (s.hp, s.shock, s.in_shock) == (-2, 2, True)  # 1. -2 HP, 2 Shock

    s = SHOCK.dying_roll(s, total=5)  # rolls low: below 10 + 2
    assert (s.hp, s.shock) == (-2, 3)  # 2.

    s = SHOCK.take_damage(s, 3)
    assert (s.hp, s.shock) == (-5, 6)  # 3.

    for _ in range(6):
        s = SHOCK.dying_roll(s, total=30)  # stabilizing rolls
    assert (s.hp, s.shock, s.in_shock, s.incapacitated) == (-5, 0, False, True)  # 4.
    assert SHOCK.dying_roll(s, total=1) == s  # no longer rolling

    s = SHOCK.take_damage(s, 1)
    assert (s.hp, s.shock, s.in_shock) == (-6, 1, True)  # 5.


def test_odds_at_nine_shock() -> None:
    """At 9 Shock you need 24 or more to drop to 8; below 19 you reach 10 and die."""
    nine = DyingState(hp=-9, shock=9, in_shock=True)
    assert SHOCK.dying_roll(nine, 24).shock == 8
    assert SHOCK.dying_roll(nine, 23).shock == 9
    assert SHOCK.dying_roll(nine, 19).shock == 9
    assert SHOCK.dying_roll(nine, 18).dead


def test_zero_hp_and_death_by_hp() -> None:
    zero = SHOCK.take_damage(DyingState(hp=4), 4)
    assert (zero.hp, zero.in_shock, zero.incapacitated) == (0, False, True)
    assert SHOCK.take_damage(zero, 2).shock == 2
    assert SHOCK.take_damage(DyingState(hp=2), 12).dead  # -10 HP
    assert SHOCK.stabilize(DyingState(hp=-3, shock=3, in_shock=True)).in_shock is False
