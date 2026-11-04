"""Differential: crit_effect and roll_damage against tests/oracle/sim.py."""

import random
from collections.abc import Callable
from typing import Any

import pytest

from stamina_engine.core.dice import ScriptedDice
from stamina_engine.model.build import Attributes, Build, Loadout
from stamina_engine.model.derive import derive
from stamina_engine.rules.exchange import roll_attack
from stamina_engine.rules.ruleset import RuleSet, v0_9

# The oracle's CRIT_MODE -> the engine's crit override.
CRIT_MODES: dict[str, dict[str, object]] = {
    "double": {"kind": "double_once"},
    "linear1": {"kind": "per_die_bonus", "bonus": 1},
    "linear2": {"kind": "per_die_bonus", "bonus": 2},
    "none": {"kind": "none"},
}


def rules_for(mode: str) -> RuleSet:
    return v0_9().override({"crit": CRIT_MODES[mode]})


@pytest.mark.parametrize("mode", sorted(CRIT_MODES))
def test_crit_effect(oracle: Any, mode: str) -> None:
    oracle.CRIT_MODE = mode
    crit = rules_for(mode).crit
    for pre in range(0, 40):
        for crits in range(0, 8):
            assert crit.finalize(pre, crits) == oracle.crit_effect(pre, crits)


MELEE = [
    ("dagger", "one"),
    ("shortsword", "one"),
    ("longsword", "one"),
    ("longsword", "two"),
    ("spear", "one"),
    ("greatsword", "two"),
    ("greataxe", "two"),
]


@pytest.mark.parametrize(("weapon", "grip"), MELEE)
def test_roll_damage(
    oracle: Any, scripted_randint: Callable[[list[int]], None], weapon: str, grip: str
) -> None:
    rules = v0_9()
    rng = random.Random(weapon + grip)
    for finesse in range(7):
        build = Build(
            "t",
            99,
            Attributes(STR=2, AGI=1, FIN=finesse),
            (("m", Loadout(weapon=weapon, grip=grip)),),
            ("fighter",),
        )
        w = derive(build, rules).main.weapon
        assert w is not None
        (dice,) = w.damage.dice
        ow = oracle.Weapon(weapon, w.base, dice.size, ndice=dice.count, flat=w.damage.flat)
        for _ in range(200):
            k = rng.randint(1, 6)
            faces = [rng.randint(1, dice.size) for _ in range(k * dice.count)]
            scripted_randint(faces)
            expected = oracle.roll_damage(ow, k, w.crit_widen)
            got = roll_attack(w, k, rules.crit, ScriptedDice(faces))
            assert (got.total, got.crit_dice) == expected
