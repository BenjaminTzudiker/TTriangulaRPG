"""Packet 0.10.1 (rules/CHANGELOG.md). Its one change inside a fight: a grazing block leaks 1
of the damage it stopped, so one with nothing left to stop leaks nothing, with perfect blocks
counted first (Packet: Blocking; blocks.graze_needs_stop). Everything else plays as 0.10.0."""

from fractions import Fraction

from stamina_engine.rules.block_solver import best_block
from stamina_engine.rules.exchange import Blocks, resolve
from stamina_engine.rules.ruleset import preset

V100 = preset("v0.10.0")
V101 = preset("v0.10.1")


def test_only_the_grazing_leak_differs_from_0_10_0() -> None:
    changed = {kind for kind, new in V101.components().items() if new != V100.components()[kind]}
    assert changed == {"blocks"}
    assert V101.blocks.graze_needs_stop and not V100.blocks.graze_needs_stop


def test_the_worked_examples_are_unchanged() -> None:
    """Packet: Blocking, Example: Choosing Blocks; Attack Procedure, Example: Melee Attack.
    A grazing block that stops less than a full defense value still leaks 1."""
    out = resolve(9, 0, defense=4, armor=2, blocks=Blocks(1, 1), rules=V101)
    assert (out.through_blocks, out.leaked, out.injury) == (1, 1, 0)
    # The orc: Melee Defense 4, armor 1. (blocks, leaks, HP lost)
    for blocks, leaked, injury in [
        (Blocks(4, 0), 0, 0),
        (Blocks(3, 1), 1, 0),  # the graze stops the last 3 and leaks 1 of it
        (Blocks(2, 2), 2, 1),
        (Blocks(2, 1), 1, 3),
    ]:
        out = resolve(15, 0, defense=4, armor=1, blocks=blocks, rules=V101)
        assert (out.leaked, out.injury) == (leaked, injury)
    # With the critical die: 16 damage, armor 0, two perfect and two grazing: 2 + 1 = 3 HP.
    assert resolve(16, 1, 4, 0, Blocks(2, 2), V101).injury == 3


def test_a_grazing_block_with_nothing_left_to_stop_leaks_nothing() -> None:
    # (damage, defense, perfect, grazing): leaks under 0.10.0, leaks under 0.10.1
    cases = {
        (16, 4, 5, 1): (1, 0),  # the perfect blocks already stop everything
        (9, 4, 2, 2): (2, 1),  # perfect blocks count first: 1 left, so one graze stops it
        (15, 4, 0, 5): (5, 4),  # four grazes stop 15; the fifth has nothing left
        (0, 4, 0, 1): (1, 0),  # nothing to stop at all
        (1, 4, 0, 1): (1, 1),  # stops 1 and leaks it
        (5, 0, 0, 2): (2, 0),  # a defense of 0 stops nothing
    }
    for (damage, defense, perfect, grazing), (before, after) in cases.items():
        blocks = Blocks(perfect, grazing)
        assert resolve(damage, 0, defense, 0, blocks, V100).leaked == before
        assert resolve(damage, 0, defense, 0, blocks, V101).leaked == after


def test_over_blocking_never_adds_damage() -> None:
    """The designer's intent: an extra grazing block can't make the result worse."""
    for damage in range(0, 25):
        for defense in range(0, 6):
            for armor in range(0, 4):
                for perfect in range(0, 5):
                    hurt = [
                        resolve(damage, 0, defense, armor, Blocks(perfect, g), V101).injury
                        for g in range(0, 8)
                    ]
                    assert hurt == sorted(hurt, reverse=True), (damage, defense, armor, perfect)


def test_the_block_solver_chooses_the_same_blocks() -> None:
    """A grazing block that stops nothing costs stamina and helps under neither rule, so
    the solver never chose one: 0.10.1 changes no fight the engine's agents play."""
    for damage in range(0, 31):
        for crit_dice in (0, 1):
            for defense in range(0, 6):
                for armor in range(0, 4):
                    for stamina in (0, 3, 7, 16):
                        for w in (Fraction(3, 2), Fraction(3), Fraction(6)):
                            args = (damage, crit_dice, defense, armor, stamina, 10)
                            old = best_block(*args, V100, w)
                            new = best_block(*args, V101, w)
                            assert (old.blocks, old.cost, old.injury) == (
                                new.blocks,
                                new.cost,
                                new.injury,
                            ), args
