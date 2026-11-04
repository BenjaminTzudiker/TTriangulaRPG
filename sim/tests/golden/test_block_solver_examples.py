"""Packet: Blocking, Example: Choosing Blocks, via the solver."""

from stamina_engine.rules.block_solver import best_block, cheapest_zero_injury
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import v0_9

RULES = v0_9()


def test_choosing_blocks_is_cheapest() -> None:
    choice = cheapest_zero_injury(9, 0, defense=4, armor=2, rules=RULES)
    assert choice is not None
    assert (choice.blocks, choice.cost) == (Blocks(1, 1), 2)
    full = best_block(9, 0, defense=4, armor=2, stamina=14, hp=8, rules=RULES)
    assert (full.blocks, full.cost, full.injury) == (Blocks(1, 1), 2, 0)


def test_never_accepts_avoidable_incapacitation() -> None:
    # 15 damage vs MD 4, armor 1, at 2 HP: 2p+1g (4 stamina) leaves 3 HP of injury, which
    # would take the defender down, so it pays for 3p+1g (7) instead.
    choice = best_block(15, 0, defense=4, armor=1, stamina=14, hp=2, rules=RULES)
    assert not choice.incapacitated
    assert choice.injury < 2
