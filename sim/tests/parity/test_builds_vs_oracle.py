"""Differential: derive() against make_fighter in tests/oracle/sim.py."""

from typing import Any

import pytest

from stamina_engine.core.mathx import odd_count
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.ruleset import v0_9

CASES = [
    (1, "sample", "l1_sample"),
    (1, "twohand", "l1_twohand"),
    (1, "greatsword", "l1_greatsword"),
    (1, "heavy", "l1_heavy"),
    (1, "duelist", "l1_duelist"),
    (30, "sample", "l30_sample"),
    (30, "strbrute", "l30_strbrute"),
    (30, "duelist", "l30_duelist"),
    (30, "heavy", "l30_heavy"),
    (99, "sample", "l99_sample"),
]


@pytest.mark.parametrize(("level", "variant", "build"), CASES)
def test_make_fighter(oracle: Any, level: int, variant: str, build: str) -> None:
    f = oracle.make_fighter(level, variant)
    p = derive(load_build(build), v0_9())
    lo = p.main
    w = lo.weapon
    assert w is not None
    assert p.hp_max == f.hp_max
    assert p.stamina_max == f.max_stamina()
    assert p.recovery == f.recovery()
    assert lo.melee_defense == f.melee_defense()
    assert lo.ranged_defense == f.ranged_defense()
    assert lo.armor == f.armor_value()
    assert w.crit_widen == f.crit_bonus()
    assert (lo.attributes.AGI, lo.attributes.FIN) == (f.AGI, f.FIN)  # heavy: penalties applied
    assert lo.initiative_bonus == odd_count(f.AGI) + odd_count(f.CUN)
    assert w.base == f.weapon.base
    assert [(d.count, d.size) for d in w.damage.dice] == [(f.weapon.ndice, f.weapon.die)]
    assert w.damage.flat == f.weapon.flat
