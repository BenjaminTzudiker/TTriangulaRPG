"""RuleSet: presets, overrides, TOML round trip, digest, registry errors."""

import dataclasses
import subprocess
import sys

import pytest
from hypothesis import given
from hypothesis import strategies as st

from stamina_engine.core.errors import ConfigError
from stamina_engine.rules.registry import KINDS, params, registered
from stamina_engine.rules.ruleset import PRESETS, from_toml, preset


@pytest.mark.parametrize("name", sorted(PRESETS))
def test_preset_round_trip(name: str) -> None:
    rules = preset(name)
    assert from_toml(rules.to_toml()) == rules
    assert rules.name == name


def test_presets_differ_where_intended() -> None:
    v09, cand, sim = preset("v0.9"), preset("review-candidate"), preset("review-sim")
    assert v09.digest() != cand.digest() != sim.digest()
    assert {k for k in KINDS if getattr(v09, k) != getattr(cand, k)} == {"surcharge"}
    assert cand.crit == v09.crit  # per-die crit bonus dropped (ruled 2026-11-03)
    assert {k for k in KINDS if getattr(v09, k) != getattr(sim, k)} == {
        "turn_order",
        "off_turn",
        "opportunity",
        "dying",
    }


def test_override_with_base() -> None:
    rules = from_toml(
        """
        [ruleset]
        base = "v0.9"
        name = "half-blocks"
        blocks = { slope_den = 2 }
        crit = { kind = "none" }
        """
    )
    assert rules.name == "half-blocks"
    assert [rules.blocks.perfect_cost(i) for i in range(1, 7)] == [1, 1, 2, 2, 3, 3]
    assert rules.crit.variant == "none"


def test_digest_ignores_name_and_is_stable_across_processes() -> None:
    rules = preset("v0.9")
    assert rules.with_(name="renamed").digest() == rules.digest()
    code = "from stamina_engine.rules.ruleset import v0_9; print(v0_9().digest())"
    other = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert other.stdout.strip() == rules.digest()


def test_every_parameter_changes_the_digest() -> None:
    base = preset("v0.9")
    for kind, component in base.components().items():
        for name, value in params(component).items():
            if isinstance(value, bool):
                new: object = not value
            elif isinstance(value, int):
                new = value + 1
            else:
                allowed = component.allowed.get(name)
                options = sorted((allowed or frozenset({value + "x"})) - {value})
                if not options:
                    continue
                new = options[0]
            changed = base.with_(**{kind: dataclasses.replace(component, **{name: new})})
            assert changed.digest() != base.digest(), (kind, name)


@pytest.mark.parametrize(
    "text",
    [
        '[ruleset]\nbase = "v0.9"\nnope = { x = 1 }',
        '[ruleset]\nbase = "v0.9"\ncrit = { kind = "triple" }',
        '[ruleset]\nbase = "v0.9"\nsurcharge = { slope = "two" }',
        '[ruleset]\nbase = "v0.9"\nsurcharge = { slope = true }',
        '[ruleset]\nbase = "v0.9"\nsurcharge = { pace = 2 }',
        '[ruleset]\nbase = "v0.9"\nturn_order = { tiebreak = "coin" }',
        '[ruleset]\nbase = "v9"',
        '[ruleset]\nname = "partial"\ncrit = { kind = "none" }',
    ],
)
def test_bad_config_raises(text: str) -> None:
    with pytest.raises(ConfigError):
        from_toml(text)


def test_registry_covers_every_kind() -> None:
    kinds = {kind for kind, _ in registered()}
    assert kinds == set(KINDS)


@given(
    slope=st.integers(0, 5),
    num=st.integers(0, 4),
    den=st.integers(1, 4),
    crit=st.sampled_from(["double_once", "per_die_bonus", "none"]),
    stamina=st.sampled_from(["public", "hidden"]),
)
def test_random_overrides_round_trip(
    slope: int, num: int, den: int, crit: str, stamina: str
) -> None:
    rules = preset("v0.9").override(
        {
            "surcharge": {"slope": slope},
            "blocks": {"slope_num": num, "slope_den": den},
            "crit": {"kind": crit},
            "information": {"stamina": stamina},
        },
        name="random",
    )
    assert from_toml(rules.to_toml()) == rules
