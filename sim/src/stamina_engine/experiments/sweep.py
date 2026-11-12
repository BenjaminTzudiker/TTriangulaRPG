"""Sweeps and comparisons.

A sweep is the product of scenarios x RuleSets x agent pairings:

```toml
[sweep]
name = "surcharge"
scenarios = ["duel.toml"]        # relative to this file
trials = 500                     # optional; overrides each scenario's

[[ruleset]]                      # optional; default: each scenario's own
label = "v0.10.0"
spec = "v0.10.0"                  # a preset, a .toml file, or a table like a scenario's ruleset

[[ruleset]]
label = "steep"
spec = { base = "v0.10.0", surcharge = { slope = 2 } }

[[agents]]                       # optional; agent spec by combatant id
label = "chip"
A = "chipkill"
B = "chipkill"
```

Seeds key on the scenario and agent pairing, not the RuleSet, so every RuleSet in a sweep
fights on the same dice and differences between them are paired.
"""

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, replace
from pathlib import Path

from stamina_engine.core.errors import ConfigError
from stamina_engine.experiments.runner import RunResult, run_scenario
from stamina_engine.experiments.scenario import (
    AgentSpec,
    Scenario,
    load_scenario,
    ruleset_from_spec,
)
from stamina_engine.experiments.stats import Interval, mean_interval, paired_difference, wilson
from stamina_engine.rules.ruleset import BASELINE, RuleSet


@dataclass(frozen=True)
class Cell:
    seed_key: str  # scenario and agents: shared across RuleSets
    label: str  # scenario | ruleset | agents
    scenario: Scenario


def load_sweep(path: str | Path) -> tuple[str, list[Cell]]:
    p = Path(path)
    data = tomllib.loads(p.read_text())
    head = data.get("sweep", {})
    scenarios = [load_scenario(p.parent / s) for s in head.get("scenarios", [])]
    if not scenarios:
        raise ConfigError("a sweep needs at least one scenario")
    trials = head.get("trials")
    rulesets: list[tuple[str, RuleSet | None]] = [
        (str(r.get("label", f"ruleset{i}")), ruleset_from_spec(r.get("spec", BASELINE), p.parent))
        for i, r in enumerate(data.get("ruleset", []))
    ] or [("own", None)]
    agent_sets: list[tuple[str, Mapping[str, AgentSpec] | None]] = [
        (str(a.get("label", f"agents{i}")), {k: v for k, v in a.items() if k != "label"})
        for i, a in enumerate(data.get("agents", []))
    ] or [("own", None)]
    cells = []
    for s in scenarios:
        if trials is not None:
            s = replace(s, trials=int(trials))
        for agents_label, agents in agent_sets:
            with_agents = s.with_agents(agents) if agents is not None else s
            for rules_label, rules in rulesets:
                cell_s = with_agents.with_rules(rules) if rules is not None else with_agents
                shown = rules_label if rules is not None else cell_s.rules.name
                label = f"{s.name}|{shown}|{agents_label}"
                cells.append(Cell(f"{s.name}|{agents_label}", label, cell_s))
    return str(head.get("name", p.stem)), cells


def run_sweep(cells: list[Cell], workers: int = 1, trials: int | None = None) -> list[RunResult]:
    return [run_scenario(c.scenario, trials, workers, cell=c.seed_key) for c in cells]


@dataclass(frozen=True)
class Difference:
    metric: str
    a: Interval
    b: Interval
    diff: Interval  # b - a, paired by trial


def compare(
    scenario: Scenario,
    rules_a: RuleSet,
    rules_b: RuleSet,
    trials: int | None = None,
    workers: int = 1,
) -> tuple[RunResult, RunResult, list[Difference]]:
    """Run one scenario under two RuleSets on the same trial seeds and pair the results."""
    key = scenario.name
    run_a = run_scenario(scenario.with_rules(rules_a), trials, workers, cell=key)
    run_b = run_scenario(scenario.with_rules(rules_b), trials, workers, cell=key)
    fa, fb = run_a.fights, run_b.fights
    teams = sorted({k[4:] for f in fa for k in f if k.startswith("win:")})
    metrics: list[tuple[str, list[float], list[float], bool]] = []
    for t in teams:
        metrics.append(
            (
                f"{t} wins",
                [float(f[f"win:{t}"]) for f in fa],
                [float(f[f"win:{t}"]) for f in fb],
                True,
            )
        )
    metrics.append(
        (
            "draws",
            [float(f["winner"] is None) for f in fa],
            [float(f["winner"] is None) for f in fb],
            True,
        )
    )
    metrics.append(
        ("rounds", [float(f["rounds"]) for f in fa], [float(f["rounds"]) for f in fb], False)
    )
    metrics.append(
        ("attacks", [float(f["attacks"]) for f in fa], [float(f["attacks"]) for f in fb], False)
    )
    metrics.append(
        ("deaths", [float(f["dead"]) for f in fa], [float(f["dead"]) for f in fb], False)
    )
    out = []
    for name, xs, ys, is_rate in metrics:
        if is_rate:
            ia, ib = wilson(int(sum(xs)), len(xs)), wilson(int(sum(ys)), len(ys))
        else:
            ia, ib = mean_interval(xs), mean_interval(ys)
        out.append(Difference(name, ia, ib, paired_difference(xs, ys)))
    return run_a, run_b, out
