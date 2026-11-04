"""se: the engine's command line.

se table (exact static tables), se run (one scenario), se sweep (scenarios x RuleSets x
agents), se compare (one scenario under two RuleSets on the same seeds), se map (show maps).
Every result is followed by its provenance (RuleSet, code and plugins).
"""

from pathlib import Path
from typing import Annotated

import typer

from stamina_engine.analysis.tables import (
    Rounding,
    render_table1,
    render_table8,
    table1,
    table8,
)
from stamina_engine.core.errors import ConfigError
from stamina_engine.experiments.metrics import summarize
from stamina_engine.experiments.runner import RunResult, run_scenario
from stamina_engine.experiments.scenario import load_scenario
from stamina_engine.experiments.sweep import compare as compare_rules
from stamina_engine.experiments.sweep import load_sweep, run_sweep
from stamina_engine.grid.battlefield import library_maps, load_map
from stamina_engine.provenance import collect
from stamina_engine.rules.plugins import PluginInfo, load_plugin
from stamina_engine.rules.ruleset import RuleSet, load_ruleset

app = typer.Typer(no_args_is_help=True, add_completion=False)
map_app = typer.Typer(no_args_is_help=True, help="Maps: list them, or show one with coordinates.")
app.add_typer(map_app, name="map")

RulesetOption = Annotated[
    str, typer.Option(help="A preset name (v0.9, review-candidate, review-sim) or a .toml file.")
]
PluginOption = Annotated[
    list[Path] | None,
    typer.Option("--plugin", help="A Python file of extra rule variants. Repeatable."),
]


@app.callback()
def main() -> None:
    """Rules engine for the stamina TTRPG (see sim/docs/ENGINE_PLAN.md)."""


def _setup(ruleset: str, plugins: list[Path] | None) -> tuple[RuleSet, list[PluginInfo]]:
    """Plugins load first, so a RuleSet file can name their variants."""
    try:
        infos = [load_plugin(p) for p in plugins or []]
        return load_ruleset(ruleset), infos
    except ConfigError as exc:
        raise typer.BadParameter(str(exc)) from exc


@app.command()
def table(
    number: Annotated[int, typer.Argument(help="Review table number: 1, 5 or 8.")],
    ruleset: RulesetOption = "v0.9",
    rounding: Annotated[
        Rounding, typer.Option(help="half-even reproduces the review's printed tables.")
    ] = Rounding.HALF_UP,
    plugin: PluginOption = None,
    equipment: Annotated[
        str, typer.Option(help="Equipment table: v0_9, or a variant in data/equipment.")
    ] = "v0_9",
) -> None:
    """Print one of the review's exact static tables."""
    from stamina_engine.model.equipment import load_table

    rules, infos = _setup(ruleset, plugin)
    try:
        gear = load_table(equipment)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc)) from exc
    if equipment != "v0_9":
        typer.echo(f"Equipment: {equipment}")
    if number == 1:
        typer.echo(render_table1(table1(rules, rounding, gear), rounding))
    elif number == 8:
        typer.echo(render_table8(table8(rules, gear), rounding))
    elif number == 5:
        from stamina_engine.analysis.ranged import render_table5

        typer.echo("Target spends / takes / downed, exactly (review Table 5's static part):")
        typer.echo(render_table5(rules))
    else:
        raise typer.BadParameter("tables 1, 5 and 8", param_hint="NUMBER")
    typer.echo("")
    typer.echo(collect(rules, infos).text())


TrialsOption = Annotated[int | None, typer.Option(help="Override the scenario's trial count.")]
WorkersOption = Annotated[int, typer.Option(help="Processes to run trials across.")]
OutOption = Annotated[
    Path | None, typer.Option(help="Write Parquet tables (runs, fights, attacks, decisions) here.")
]


def _report(run: RunResult, title: str) -> None:
    typer.echo(title)
    for line in summarize(run.fights).lines():
        typer.echo(f"  {line}")


def _stamp(runs: list[RunResult]) -> None:
    typer.echo("")
    seen: set[str] = set()
    for run in runs:
        text = run.provenance.text()
        if text not in seen:
            seen.add(text)
            typer.echo(text)


@app.command()
def run(
    scenario: Annotated[Path, typer.Argument(help="A scenario TOML file.")],
    trials: TrialsOption = None,
    workers: WorkersOption = 1,
    out: OutOption = None,
    plugin: PluginOption = None,
) -> None:
    """Run one scenario and summarize it."""
    try:
        for p in plugin or []:
            load_plugin(p)
        s = load_scenario(scenario)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc)) from exc
    result = run_scenario(s, trials, workers)
    _report(result, f"Scenario {s.name} (seed {s.seed}, dice {s.dice})")
    if out is not None:
        from stamina_engine.experiments.results import write_results

        for path in write_results([result], out):
            typer.echo(f"  wrote {path}")
    _stamp([result])


@app.command()
def sweep(
    file: Annotated[Path, typer.Argument(help="A sweep TOML file.")],
    trials: TrialsOption = None,
    workers: WorkersOption = 1,
    out: OutOption = None,
    plugin: PluginOption = None,
) -> None:
    """Run every cell of a sweep: scenarios x RuleSets x agent pairings."""
    try:
        for p in plugin or []:
            load_plugin(p)
        name, cells = load_sweep(file)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc)) from exc
    results = run_sweep(cells, workers, trials)
    typer.echo(f"Sweep {name}: {len(cells)} cells")
    for cell, result in zip(cells, results, strict=True):
        _report(result, f"\n{cell.label}")
    if out is not None:
        from stamina_engine.experiments.results import write_results

        for path in write_results(results, out):
            typer.echo(f"wrote {path}")
    _stamp(results)


@app.command()
def compare(
    scenario: Annotated[Path, typer.Argument(help="A scenario TOML file.")],
    a: Annotated[str, typer.Option("--a", help="RuleSet A: a preset or a .toml file.")],
    b: Annotated[str, typer.Option("--b", help="RuleSet B: a preset or a .toml file.")],
    trials: TrialsOption = None,
    workers: WorkersOption = 1,
    plugin: PluginOption = None,
) -> None:
    """Run a scenario under two RuleSets on the same seeds; report paired differences."""
    rules_a, _ = _setup(a, plugin)
    rules_b, _ = _setup(b, None)
    try:
        s = load_scenario(scenario)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc)) from exc
    run_a, run_b, diffs = compare_rules(s, rules_a, rules_b, trials, workers)
    typer.echo(f"Scenario {s.name}: B ({rules_b.name}) minus A ({rules_a.name}), paired by seed")
    typer.echo(f"{'metric':<12} {'A':<26} {'B':<26} B - A")
    for d in diffs:
        typer.echo(f"{d.metric:<12} {d.a!s:<26} {d.b!s:<26} {d.diff}")
    _stamp([run_a, run_b])


@app.command()
def suite(
    name: Annotated[
        str, typer.Argument(help="Suite to run: parity, positioning, ranged or phase.")
    ],
    workers: WorkersOption = 1,
    scale: Annotated[float, typer.Option(help="Fraction of the review's trial counts.")] = 1.0,
    trials: Annotated[int, typer.Option(help="Positioning: trials per row.")] = 500,
    out: Annotated[Path | None, typer.Option(help="Write the report here (markdown).")] = None,
) -> None:
    """Run a suite. parity: every published review configuration in lockstep with the
    review's simulator, reported beside the review's figures. positioning: the M2 grid
    scenarios across agent families and the Phase 3 and 4 RuleSet variants."""
    if name == "positioning":
        _positioning(workers, trials, out)
        return
    if name == "ranged":
        _ranged(workers, trials, out)
        return
    if name == "phase":
        _phase(workers, trials, out)
        return
    if name != "parity":
        raise typer.BadParameter("suites: parity, positioning, ranged, phase", param_hint="NAME")
    from stamina_engine.experiments.oracle_bridge import Knobs
    from stamina_engine.experiments.parity import cases, render, rules_for, run_cases

    stamp = collect(rules_for(Knobs())).text()  # before running: the code that runs
    results = run_cases(cases(), scale, workers)
    report = render(results, stamp, scale)
    if out is None:
        typer.echo(report)
    else:
        out.write_text(report)
        typer.echo(f"wrote {out}")
    bad = sum(len(r.mismatches) for r in results)
    typer.echo(f"{sum(len(r.records) for r in results)} fights, {bad} mismatches with the oracle")
    if bad:
        raise typer.Exit(1)


@map_app.command("list")
def map_list() -> None:
    """The library maps (data/maps)."""
    for name in library_maps():
        typer.echo(name)


@map_app.command("show")
def map_show(
    name: Annotated[str, typer.Argument(help="A library map name, or a .txt file.")],
) -> None:
    """Print a map with column and row numbers, its spawn markers and its legend."""
    try:
        field = load_map(name, Path.cwd())
    except ConfigError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"{field.name}: {field.width} x {field.height}")
    typer.echo(field.render())
    for marker, cells in sorted(field.spawns.items()):
        typer.echo(f"spawn {marker}: " + ", ".join(f"({x}, {y})" for x, y in cells))
    typer.echo("legend: " + ", ".join(f"{ch!r} {terrain}" for ch, terrain in field.legend))


def _positioning(workers: int, trials: int, out: Path | None) -> None:
    from stamina_engine.experiments.positioning import ROWS, render, run_rows
    from stamina_engine.rules.ruleset import preset

    stamp = collect(preset("v0.9")).text()  # before running: the code that runs
    report = render(run_rows(ROWS, trials, workers), stamp, trials)
    if out is None:
        typer.echo(report)
    else:
        out.write_text(report)
        typer.echo(f"wrote {out}")


@app.command(name="trace")
def trace_cmd(
    scenario: Annotated[Path, typer.Argument(help="A scenario TOML file.")],
    trial: Annotated[int, typer.Option(help="Which trial to replay.")] = 0,
    cell: Annotated[str, typer.Option(help="Cell key, if the trial came from a sweep.")] = "",
) -> None:
    """Replay one fight of a scenario: every event, with the board at each turn."""
    from stamina_engine.experiments.trace import trace

    try:
        s = load_scenario(scenario)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(trace(s, trial, cell))


def _ranged(workers: int, trials: int, out: Path | None) -> None:
    from stamina_engine.analysis.ranged import render_table5
    from stamina_engine.experiments.positioning import run_rows
    from stamina_engine.experiments.ranged_suite import ROWS, render
    from stamina_engine.rules.ruleset import preset

    rules = preset("v0.9")
    stamp = collect(rules).text()
    report = render(run_rows(ROWS, trials, workers), stamp, trials, render_table5(rules))
    if out is None:
        typer.echo(report)
    else:
        out.write_text(report)
        typer.echo(f"wrote {out}")


def _phase(workers: int, trials: int, out: Path | None) -> None:
    from stamina_engine.experiments.phase_suite import render, run
    from stamina_engine.rules.ruleset import preset

    stamp = collect(preset("v0.9")).text()
    report = render(run(trials, workers), stamp, trials)
    if out is None:
        typer.echo(report)
    else:
        out.write_text(report)
        typer.echo(f"wrote {out}")
