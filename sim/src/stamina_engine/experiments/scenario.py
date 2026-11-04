"""Scenarios: who fights, under which rules, how many times, from which seed.

```toml
[scenario]
name = "l1-duel"
ruleset = { base = "v0.9" }          # or "v0.9", or { file = "mine.toml" }, plus overrides
round_cap = 30
trials = 2000
seed = 1
dice = "named"                       # or "lockstep" (one shared stream, as the review did)
map = "open_12x12"                   # a library map, or a .txt path relative to this file;
                                     # leave it out for the all-adjacent arena (M1)
legend = { "~" = "low" }             # optional extra map characters
plugins = []                         # plugin files, relative to this file

[[combatant]]
id = "A"
team = "A"
build = "l1_sample"                  # a library build, or a .toml path relative to this file
agent = "chipkill"                   # or { commit = "chipkill", target = "first", w = "3" }
count = 1                            # several identical combatants: ids A0, A1...
spawn = "A"                          # on a map: a spawn marker, or [x, y]; a counted group
                                     # takes a list, or a marker that repeats on the map
```

`map_text` (a multi-line TOML string) gives the map inline instead of `map`; scenario_to_toml
writes it that way, so a written scenario doesn't depend on files.
"""

import json
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

from stamina_engine.core.errors import ConfigError
from stamina_engine.grid.battlefield import Battlefield, Cell, load_map, parse_map
from stamina_engine.model.build import Build, load_build
from stamina_engine.rules.plugins import PluginInfo, load_plugin
from stamina_engine.rules.ruleset import RuleSet, load_ruleset, preset

ARENAS = frozenset({"all_adjacent", "map"})
DICE_MODES = frozenset({"named", "lockstep"})

AgentSpec = str | Mapping[str, object]


@dataclass(frozen=True)
class CombatantSpec:
    id: str
    team: str
    build: Build
    agent: AgentSpec
    loadout: str = ""
    pos: Cell | None = None  # starting square, on a map


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
    battlefield: Battlefield | None = None

    def __post_init__(self) -> None:
        if self.arena not in ARENAS:
            raise ConfigError(f"arena {self.arena!r}: expected one of {sorted(ARENAS)}")
        if (self.arena == "map") != (self.battlefield is not None):
            raise ConfigError("arena = 'map' needs a map, and a map needs arena = 'map'")
        if self.battlefield is not None:
            cells = [c.pos for c in self.combatants]
            if any(c is None for c in cells):
                raise ConfigError(f"scenario {self.name}: on a map every combatant needs a spawn")
            if len(set(cells)) != len(cells):
                raise ConfigError(f"scenario {self.name}: two combatants share a starting square")
            for c in self.combatants:
                assert c.pos is not None
                if not self.battlefield.walkable(c.pos):
                    raise ConfigError(f"{c.id} starts on {c.pos}, which isn't floor")
        elif any(c.pos is not None for c in self.combatants):
            raise ConfigError(f"scenario {self.name}: spawns need a map")
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


def _battlefield(table: dict[str, Any], base_dir: Path) -> Battlefield | None:
    legend = {str(k): str(v) for k, v in dict(table.pop("legend", {})).items()}
    name, text = table.pop("map", None), table.pop("map_text", None)
    if name is not None and text is not None:
        raise ConfigError("give map or map_text, not both")
    if text is not None:
        return parse_map(str(text), str(table.get("map_name", "inline")), legend)
    if name is not None:
        return load_map(str(name), base_dir, legend)
    return None


class _Spawns:
    """Hands out starting squares: markers in reading order, or explicit [x, y]."""

    def __init__(self, field: Battlefield | None) -> None:
        self.field = field
        self.used: dict[str, int] = {}

    def take(self, spec: object, who: str) -> Cell:
        if self.field is None:
            raise ConfigError(f"{who} has a spawn but the scenario has no map")
        if isinstance(spec, str):
            cells = self.field.spawn(spec)
            i = self.used.get(spec, 0)
            if i >= len(cells):
                raise ConfigError(f"spawn {spec!r} has {len(cells)} squares; {who} needs another")
            self.used[spec] = i + 1
            return cells[i]
        if (
            isinstance(spec, list)
            and len(spec) == 2
            and all(isinstance(v, int) and not isinstance(v, bool) for v in spec)
        ):
            return (spec[0], spec[1])
        raise ConfigError(f"{who}: spawn must be a marker or [x, y], not {spec!r}")

    def group(self, spec: object, cid: str, count: int) -> list[Cell | None]:
        if spec is None:
            return [None] * count
        ids = [cid if count == 1 else f"{cid}{i}" for i in range(count)]
        is_point = (
            isinstance(spec, list) and len(spec) == 2 and all(isinstance(v, int) for v in spec)
        )
        if isinstance(spec, list) and not is_point:
            if len(spec) != count:
                raise ConfigError(f"{cid}: {count} combatants but {len(spec)} spawns")
            return [self.take(s, who) for s, who in zip(spec, ids, strict=True)]
        if count > 1 and is_point:
            raise ConfigError(f"{cid}: {count} combatants can't share one square")
        return [self.take(spec, who) for who in ids]


def scenario_from_toml(text: str, base_dir: Path = Path(".")) -> Scenario:
    data = tomllib.loads(text)
    table: dict[str, Any] = dict(data.get("scenario", {}))
    if not table:
        raise ConfigError("missing [scenario] table")
    plugin_paths = tuple(str(_resolve(base_dir, p)) for p in table.pop("plugins", []))
    plugins = tuple(load_plugin(p) for p in plugin_paths)  # before the rules name them
    rules = ruleset_from_spec(table.pop("ruleset", "v0.9"), base_dir)
    battlefield = _battlefield(table, base_dir)
    table.pop("map_name", None)
    spawns = _Spawns(battlefield)
    combatants: list[CombatantSpec] = []
    for entry in data.get("combatant", []):
        entry = dict(entry)
        count = int(entry.pop("count", 1))
        unknown = set(entry) - {"id", "team", "build", "agent", "loadout", "spawn"}
        if unknown:
            raise ConfigError(f"unknown combatant fields {sorted(unknown)}")
        cid, team = str(entry["id"]), str(entry.get("team", entry["id"]))
        build = _build(str(entry["build"]), base_dir)
        agent: AgentSpec = entry.get("agent", "alpha")
        cells = spawns.group(entry.get("spawn"), cid, count)
        for i in range(count):
            combatants.append(
                CombatantSpec(
                    cid if count == 1 else f"{cid}{i}",
                    team,
                    build,
                    agent,
                    str(entry.get("loadout", "")),
                    cells[i],
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
        arena=str(table.get("arena", "map" if battlefield is not None else "all_adjacent")),
        plugins=plugins,
        plugin_paths=plugin_paths,
        source=text,
        battlefield=battlefield,
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
    ]
    if s.battlefield is not None:
        lines.append(f"map_name = {_toml(s.battlefield.name)}")
        lines.append('map_text = """\n' + "\n".join(s.battlefield.rows) + '\n"""')
        lines.append(
            "legend = " + _toml({ch: t for ch, t in s.battlefield.legend if ch not in ".#=o"})
        )
    lines.append("")
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
        if c.pos is not None:
            lines.append(f"spawn = {_toml(list(c.pos))}")
    return "\n".join(lines) + "\n"
