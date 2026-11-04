"""Scenarios: who fights, under which rules, how many times, from which seed.

```toml
[scenario]
name = "l1-duel"
ruleset = { base = "v0.9" }          # or "v0.9", or { file = "mine.toml" }, plus overrides
round_cap = 30
trials = 2000
seed = 1
dice = "named"                       # or "lockstep" (one shared stream, as the review did)
arena = "all_adjacent"               # the only arena until M2 adds maps
plugins = []                         # plugin files, relative to this file

[[combatant]]
id = "A"
team = "A"
build = "l1_sample"                  # a library build, or a .toml path relative to this file
agent = "chipkill"                   # or { commit = "chipkill", target = "first", w = "3" }
count = 1                            # several identical combatants: ids A0, A1...
```
"""

import json
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from stamina_engine.core.errors import ConfigError
from stamina_engine.model.build import Build, load_build
from stamina_engine.rules.plugins import PluginInfo, load_plugin
from stamina_engine.rules.ruleset import RuleSet, load_ruleset, preset

ARENAS = frozenset({"all_adjacent"})
DICE_MODES = frozenset({"named", "lockstep"})

AgentSpec = str | Mapping[str, object]


@dataclass(frozen=True)
class CombatantSpec:
    id: str
    team: str
    build: Build
    agent: AgentSpec
    loadout: str = ""


@dataclass(frozen=True)
class Scenario:
    name: str
    rules: RuleSet
    combatants: tuple[CombatantSpec, ...]
    round_cap: int = 30
    trials: int = 1000
    seed: int = 1
    dice: str = "named"
    arena: str = "all_adjacent"
    plugins: tuple[PluginInfo, ...] = ()
    plugin_paths: tuple[str, ...] = ()
    source: str = field(default="", compare=False)  # the TOML it came from, for the record

    def __post_init__(self) -> None:
        if self.arena not in ARENAS:
            raise ConfigError(f"arena {self.arena!r}: M1 has {sorted(ARENAS)}")
        if self.dice not in DICE_MODES:
            raise ConfigError(f"dice {self.dice!r}: expected one of {sorted(DICE_MODES)}")
        ids = [c.id for c in self.combatants]
        if len(set(ids)) != len(ids):
            raise ConfigError(f"duplicate combatant ids in {self.name}")
        if len({c.team for c in self.combatants}) < 2:
            raise ConfigError(f"scenario {self.name} needs at least two teams")

    def with_rules(self, rules: RuleSet) -> "Scenario":
        return replace(self, rules=rules)

    def with_agents(self, agents: Mapping[str, AgentSpec]) -> "Scenario":
        """Replace agents by combatant id, or by the id a counted group was declared with."""
        out = []
        for c in self.combatants:
            spec = agents.get(c.id, agents.get(c.id.rstrip("0123456789"), c.agent))
            out.append(replace(c, agent=spec))
        return replace(self, combatants=tuple(out))


def _resolve(base_dir: Path, name: str) -> Path:
    path = Path(name)
    return path if path.is_absolute() else base_dir / path


def ruleset_from_spec(spec: object, base_dir: Path) -> RuleSet:
    """A preset name, or a table with base (or file), an optional name and overrides."""
    if isinstance(spec, str):
        return (
            load_ruleset(str(_resolve(base_dir, spec))) if spec.endswith(".toml") else preset(spec)
        )
    if not isinstance(spec, Mapping):
        raise ConfigError("ruleset must be a preset name or a table")
    table = dict(spec)
    name = table.pop("name", None)
    if "file" in table:
        base = load_ruleset(str(_resolve(base_dir, str(table.pop("file")))))
    else:
        base = preset(str(table.pop("base", "v0.9")))
    if not table and name is None:
        return base
    return base.override(table, name=str(name) if name is not None else None)


def _build(name: str, base_dir: Path) -> Build:
    if name.endswith(".toml"):
        path = _resolve(base_dir, name)
        return Build.from_toml(path.stem, path.read_text())
    return load_build(name)


def scenario_from_toml(text: str, base_dir: Path = Path(".")) -> Scenario:
    data = tomllib.loads(text)
    table: dict[str, Any] = dict(data.get("scenario", {}))
    if not table:
        raise ConfigError("missing [scenario] table")
    plugin_paths = tuple(str(_resolve(base_dir, p)) for p in table.pop("plugins", []))
    plugins = tuple(load_plugin(p) for p in plugin_paths)  # before the rules name them
    rules = ruleset_from_spec(table.pop("ruleset", "v0.9"), base_dir)
    combatants: list[CombatantSpec] = []
    for entry in data.get("combatant", []):
        entry = dict(entry)
        count = int(entry.pop("count", 1))
        unknown = set(entry) - {"id", "team", "build", "agent", "loadout"}
        if unknown:
            raise ConfigError(f"unknown combatant fields {sorted(unknown)}")
        cid, team = str(entry["id"]), str(entry.get("team", entry["id"]))
        build = _build(str(entry["build"]), base_dir)
        agent: AgentSpec = entry.get("agent", "alpha")
        for i in range(count):
            combatants.append(
                CombatantSpec(
                    cid if count == 1 else f"{cid}{i}",
                    team,
                    build,
                    agent,
                    str(entry.get("loadout", "")),
                )
            )
    known = {"name", "round_cap", "trials", "seed", "dice", "arena"}
    unknown = set(table) - known
    if unknown:
        raise ConfigError(f"unknown scenario fields {sorted(unknown)}")
    return Scenario(
        name=str(table.get("name", "scenario")),
        rules=rules,
        combatants=tuple(combatants),
        round_cap=int(table.get("round_cap", 30)),
        trials=int(table.get("trials", 1000)),
        seed=int(table.get("seed", 1)),
        dice=str(table.get("dice", "named")),
        arena=str(table.get("arena", "all_adjacent")),
        plugins=plugins,
        plugin_paths=plugin_paths,
        source=text,
    )


def load_scenario(path: str | Path) -> Scenario:
    p = Path(path)
    try:
        text = p.read_text()
    except OSError as exc:
        raise ConfigError(f"can't read scenario {path}: {exc}") from exc
    return scenario_from_toml(text, p.parent)


def _toml(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value)
    if isinstance(value, Mapping):
        return "{ " + ", ".join(f"{k} = {_toml(v)}" for k, v in value.items()) + " }"
    if isinstance(value, list | tuple):
        return "[" + ", ".join(_toml(v) for v in value) + "]"
    raise ConfigError(f"can't write {value!r} to TOML")


def scenario_to_toml(s: Scenario) -> str:
    """A self-contained TOML: the full RuleSet is written out, so it doesn't depend on presets.
    Builds are written by name, so they must be library builds."""
    lines = [
        "[scenario]",
        f"name = {_toml(s.name)}",
        f"round_cap = {s.round_cap}",
        f"trials = {s.trials}",
        f"seed = {s.seed}",
        f"dice = {_toml(s.dice)}",
        f"arena = {_toml(s.arena)}",
        f"plugins = {_toml(list(s.plugin_paths))}",
        "",
    ]
    rules = tomllib.loads(s.rules.to_toml())["ruleset"]
    lines.append("[scenario.ruleset]")
    lines.append(f"base = {_toml('v0.9')}")
    lines.append(f"name = {_toml(rules.pop('name'))}")
    lines.extend(f"{kind} = {_toml(params)}" for kind, params in rules.items())
    for c in s.combatants:
        lines += [
            "",
            "[[combatant]]",
            f"id = {_toml(c.id)}",
            f"team = {_toml(c.team)}",
            f"build = {_toml(c.build.name)}",
            f"agent = {_toml(c.agent)}",
        ]
        if c.loadout:
            lines.append(f"loadout = {_toml(c.loadout)}")
    return "\n".join(lines) + "\n"
