"""The RuleSet digest leaves out parameters at their default, so these tests keep that safe.

- **Released defaults never change.** A RuleSet that leaves a parameter at its default would
  keep its digest while its rules changed. `component_defaults.json` pins every built-in
  component's defaults. To change a rule, keep the old default and set the new value where
  it applies (in a preset for the baseline), so the digest changes with it.
- **New switches are free.** Adding a parameter whose default keeps today's rule changes no
  digest. Record its default with `uv run python tests/golden/test_component_defaults.py`,
  which adds new entries and never rewrites pinned ones.
- **The presets' digests are pinned.** If one moves, the commit must say why.
"""

import dataclasses
import json
from pathlib import Path

from stamina_engine.rules import components as _components  # noqa: F401  (registers variants)
from stamina_engine.rules.components.surcharge import LinearSurcharge
from stamina_engine.rules.registry import Scalar, defaults, registered
from stamina_engine.rules.ruleset import preset

SNAPSHOT = Path(__file__).with_name("component_defaults.json")

PRESET_DIGESTS = {
    "v0.9": "3bf6fc070dbf",
    "v0.9.1": "af236ed0cda0",
    "v0.9.2": "8dd5547b5abe",
    "v0.9.3": "8dd5547b5abe",  # 0.9.3 changes nothing inside a fight
    "v0.10.0": "a89fed59543d",
    "v0.10.1": "50a73c176f63",  # 0.10.0 with blocks.graze_needs_stop
    "v0.10.0-cover-only": "820505340da8",
    "v0.10.0-crit-c-prime": "b7690db2f629",
    "v0.10.0-crit-c": "6a1c7e8b7971",
    "review-candidate": "d99bdcba96f4",
    "review-sim": "4179c8ac37bc",
}

Defaults = dict[str, dict[str, Scalar | None]]


def current() -> Defaults:
    """Every built-in component's defaults, keyed "kind/variant" (plugins excluded)."""
    return {
        f"{kind}/{variant}": defaults(cls)
        for (kind, variant), cls in sorted(registered().items())
        if cls.__module__.startswith("stamina_engine.")
    }


def _same(a: object, b: object) -> bool:
    return type(a) is type(b) and a == b  # True == 1, but a bool default isn't an int one


def test_released_defaults_never_change() -> None:
    pinned: Defaults = json.loads(SNAPSHOT.read_text())
    now = current()
    changed = [
        f"{key}.{name}: {old!r} -> {now[key][name]!r}"
        if key in now and name in now[key]
        else f"{key}.{name}: removed"
        for key, params in pinned.items()
        for name, old in params.items()
        if not (key in now and name in now[key] and _same(now[key][name], old))
    ]
    assert not changed, (
        "A released default changed or was removed, which would change rules under an "
        "unchanged digest. Keep the old default and set the new value where it applies "
        "(in a preset for the baseline). " + "; ".join(changed)
    )
    added = [
        f"{key}.{name}" for key, params in now.items() for name in params
        if name not in pinned.get(key, {})
    ]
    assert not added, (
        "New parameters or variants; record their defaults with "
        f"`uv run python tests/golden/test_component_defaults.py`: {', '.join(added)}"
    )


def test_preset_digests_are_pinned() -> None:
    got = {name: preset(name).short_digest() for name in PRESET_DIGESTS}
    assert got == PRESET_DIGESTS


def test_a_new_defaulted_switch_keeps_every_digest() -> None:
    @dataclasses.dataclass(frozen=True)
    class WithNewSwitch(LinearSurcharge):  # same kind and variant, one more parameter
        new_switch: str = "today"

    base = preset("v0.9")
    assert base.with_(surcharge=WithNewSwitch()).digest() == base.digest()
    assert base.with_(surcharge=WithNewSwitch(new_switch="other")).digest() != base.digest()
    cand = preset("review-candidate")
    widened = cand.with_(surcharge=WithNewSwitch(slope=cand.surcharge.slope))
    assert widened.digest() == cand.digest()


def test_a_parameter_set_to_its_default_matches_leaving_it_out() -> None:
    base = preset("v0.9")
    explicit = base.override({"surcharge": {"slope": 1}, "off_turn": {"enabled": True}})
    assert explicit.digest() == base.digest()


if __name__ == "__main__":
    pinned = json.loads(SNAPSHOT.read_text()) if SNAPSHOT.exists() else {}
    for key, params in current().items():
        for name, value in params.items():
            pinned.setdefault(key, {}).setdefault(name, value)  # adds; never rewrites
    SNAPSHOT.write_text(json.dumps(pinned, indent=2, sort_keys=True) + "\n")
    print(f"wrote {SNAPSHOT}")
