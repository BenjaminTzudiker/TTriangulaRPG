"""Packet worked examples: Melee Attack, Choosing Blocks, Critical Range Table."""

from stamina_engine.core.dice import ScriptedDice
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.exchange import Blocks, resolve, roll_attack
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import v0_9

RULES = v0_9()


def test_melee_attack_example() -> None:
    weapon = derive(load_build("l1_sample"), RULES).main.weapon
    assert weapon is not None
    attack = roll_attack(weapon, 2, RULES.crit, ScriptedDice([6, 3]))
    assert attack.total == 15
    assert attack.crit_dice == 0
    assert Pricing(RULES).melee_attack(weapon.base, 2).total == 5

    # The orc: Melee Defense 4, armor 1. (blocks, stamina, through blocks, after armor)
    lines = [
        (Blocks(4, 0), 10, 0, 0),
        (Blocks(3, 1), 7, 1, 0),
        (Blocks(2, 2), 5, 2, 1),
        (Blocks(2, 1), 4, 4, 3),
    ]
    for blocks, stamina, through, after_armor in lines:
        out = resolve(15, 0, defense=4, armor=1, blocks=blocks, rules=RULES)
        assert Pricing(RULES).blocks(blocks.perfect, blocks.grazing).total == stamina
        assert out.through_blocks + out.leaked == through
        assert out.after_armor == after_armor == out.injury


def test_choosing_blocks_example() -> None:
    """9 damage vs MD 4, armor 2: one perfect, one graze: 2 stamina, no injury."""
    out = resolve(9, 0, defense=4, armor=2, blocks=Blocks(1, 1), rules=RULES)
    assert (out.through_blocks, out.leaked, out.injury) == (1, 1, 0)
    assert Pricing(RULES).blocks(1, 1).total == 2


CRITICAL_RANGE_TABLE = {
    # die: lowest critical face at Finesse 0, 1-2, 3-4, 5-6 (1 = "Always" on a d4)
    4: (4, 3, 2, 1),
    6: (6, 5, 4, 3),
    8: (8, 7, 6, 5),
    10: (10, 9, 8, 7),
    12: (12, 11, 10, 9),
}


def test_critical_range_table() -> None:
    crit = RULES.crit
    for size, lows in CRITICAL_RANGE_TABLE.items():
        for finesse in range(7):
            low = lows[(finesse + 1) // 2]
            faces = [f for f in range(1, size + 1) if crit.is_crit(f, size, crit.widen(finesse))]
            assert faces == list(range(low, size + 1)), (size, finesse)


def test_crits_double_once_and_ignore_armor() -> None:
    # 2 crit dice: armor 2 is fully ignored, and the remainder is doubled once, not twice.
    out = resolve(10, 2, defense=4, armor=2, blocks=Blocks(2, 0), rules=RULES)
    assert (out.armor_applied, out.after_armor, out.injury) == (0, 2, 4)
