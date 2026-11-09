"""Plugins: external rule variants, loaded at run time without touching the baseline."""

from pathlib import Path

import pytest

from stamina_engine.core.errors import ConfigError
from stamina_engine.rules.plugins import load_plugin
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.registry import registered
from stamina_engine.rules.ruleset import load_ruleset, v0_9, v0_9_2

EXAMPLES = Path(__file__).resolve().parents[2] / "examples"
EXAMPLE = EXAMPLES / "exp_quadratic_surcharge.py"

PLUGIN = """
from dataclasses import dataclass

from stamina_engine.rules.components.blocks import BlockRule
from stamina_engine.rules.registry import register


@register("blocks", "{variant}")
@dataclass(frozen=True)
class Flat(BlockRule):
    cost: int = 2

    def perfect_cost(self, nth: int) -> int:
        return self.cost
{extra}
"""


def write(tmp_path: Path, name: str, variant: str, extra: str = "") -> Path:
    path = tmp_path / f"{name}.py"
    path.write_text(PLUGIN.format(variant=variant, extra=extra))
    return path


def test_example_plugin() -> None:
    info = load_plugin(EXAMPLE)
    assert info.components == (("surcharge", "exp_quadratic"),)
    assert load_plugin(EXAMPLE) is info  # unchanged file: no-op
    rules = load_ruleset(str(EXAMPLES / "exp_quadratic_surcharge.toml"))
    assert rules.name == "exp-quadratic-surcharge"
    assert Pricing(rules).melee_attack(2, 4).parts == (2, 3, 6, 11)
    assert rules.digest() != v0_9_2().digest()
    assert {k for k, c in rules.components().items() if c != v0_9_2().components()[k]} == {
        "surcharge"
    }


def test_plugin_variant_through_override(tmp_path: Path) -> None:
    load_plugin(write(tmp_path, "flat", "exp_flat_two"))
    rules = v0_9().override({"blocks": {"kind": "exp_flat_two", "cost": 3}})
    assert rules.name == "v0.9+modified"  # unnamed changes can't pass for the base preset
    assert Pricing(rules).blocks(3, 0).parts == (3, 3, 3)


SHADOW = """
from dataclasses import dataclass

from stamina_engine.rules.components.crit import DoubleOnce
from stamina_engine.rules.registry import register


@register("crit", "exp_registered_first")
@dataclass(frozen=True)
class First(DoubleOnce):
    pass


@register("crit", "double_once")
@dataclass(frozen=True)
class Shadow(DoubleOnce):
    pass
"""


def test_shadowing_a_rule_is_refused_and_rolled_back(tmp_path: Path) -> None:
    """The file registers a new variant, then tries to take v0.9's name. The load fails and
    the new variant is removed too, so nothing half-loaded is left behind."""
    before = set(registered())
    path = tmp_path / "shadow.py"
    path.write_text(SHADOW)
    with pytest.raises(ConfigError, match="registered twice"):
        load_plugin(path)
    assert set(registered()) == before


def test_plugin_errors(tmp_path: Path) -> None:
    empty = tmp_path / "empty.py"
    empty.write_text("X = 1\n")
    with pytest.raises(ConfigError, match="registered no components"):
        load_plugin(empty)
    broken = tmp_path / "broken.py"
    broken.write_text("raise RuntimeError('boom')\n")
    with pytest.raises(ConfigError, match="boom"):
        load_plugin(broken)
    with pytest.raises(ConfigError):
        load_plugin(tmp_path / "missing.py")
    changing = write(tmp_path, "changing", "exp_changing")
    load_plugin(changing)
    changing.write_text(changing.read_text() + "\n# edited\n")
    with pytest.raises(ConfigError, match="changed since"):
        load_plugin(changing)


def test_unknown_plugin_variant_names_the_known_ones() -> None:
    with pytest.raises(ConfigError, match="known"):
        v0_9().override({"surcharge": {"kind": "exp_not_loaded"}})
