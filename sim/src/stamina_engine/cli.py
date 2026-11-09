"""se: the engine's command line.

se table (exact static tables), se run (one scenario), se sweep (scenarios x RuleSets x
agents), se compare (one scenario under two RuleSets on the same seeds), se suite (the
milestone reports), se map (show maps), se trace (one fight), se play and se load (a person's
decisions). Every result is followed by its provenance (RuleSet, code and plugins).

Standard library only (argparse), so it runs from a source checkout without installing
anything: `PYTHONPATH=src python3 -m stamina_engine table 1`. `invoke()` runs a command from
Python and returns its exit code and output.
"""

import argparse
import contextlib
import io
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

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

SUITES = ("parity", "positioning", "ranged", "phase", "cores", "objectives")


class UsageError(Exception):
    """A bad argument: reported with the command's usage, exit code 2."""


def _say(text: str = "") -> None:
    print(text)


def _write_or_print(report: str, out: Path | None) -> None:
    if out is None:
        _say(report)
    else:
        out.write_text(report)
        _say(f"wrote {out}")


def _setup(ruleset: str, plugins: list[Path] | None) -> tuple[RuleSet, list[PluginInfo]]:
    """Plugins load first, so a RuleSet file can name their variants."""
    infos = [load_plugin(p) for p in plugins or []]
    return load_ruleset(ruleset), infos


def _report(run: RunResult, title: str) -> None:
    _say(title)
    for line in summarize(run.fights).lines():
        _say(f"  {line}")


def _stamp(runs: list[RunResult]) -> None:
    _say()
    seen: set[str] = set()
    for run in runs:
        text = run.provenance.text()
        if text not in seen:
            seen.add(text)
            _say(text)


def _write_results(runs: list[RunResult], out: Path, indent: str) -> None:
    from stamina_engine.experiments.results import write_results

    try:
        paths = write_results(runs, out)
    except ModuleNotFoundError as exc:
        raise UsageError(f"--out needs pyarrow ({exc}): pip install pyarrow") from None
    for path in paths:
        _say(f"{indent}wrote {path}")


def table(args: argparse.Namespace) -> int:
    """Print one of the review's exact static tables."""
    from stamina_engine.model.equipment import load_table

    rules, infos = _setup(args.ruleset, args.plugin)
    rounding = Rounding(args.rounding)
    gear = load_table(args.equipment)
    if args.equipment != "v0_9":
        _say(f"Equipment: {args.equipment}")
    if args.number == 1:
        _say(render_table1(table1(rules, rounding, gear), rounding))
    elif args.number == 8:
        _say(render_table8(table8(rules, gear), rounding))
    else:
        from stamina_engine.analysis.ranged import render_table5

        _say("Target spends / takes / downed, exactly (review Table 5's static part):")
        _say(render_table5(rules))
    _say()
    _say(collect(rules, infos).text())
    return 0


def run(args: argparse.Namespace) -> int:
    """Run one scenario and summarize it."""
    for p in args.plugin or []:
        load_plugin(p)
    s = load_scenario(args.scenario)
    result = run_scenario(s, args.trials, args.workers)
    _report(result, f"Scenario {s.name} (seed {s.seed}, dice {s.dice})")
    if args.out is not None:
        _write_results([result], args.out, "  ")
    _stamp([result])
    return 0


def sweep(args: argparse.Namespace) -> int:
    """Run every cell of a sweep: scenarios x RuleSets x agent pairings."""
    for p in args.plugin or []:
        load_plugin(p)
    name, cells = load_sweep(args.file)
    results = run_sweep(cells, args.workers, args.trials)
    _say(f"Sweep {name}: {len(cells)} cells")
    for cell, result in zip(cells, results, strict=True):
        _report(result, f"\n{cell.label}")
    if args.out is not None:
        _write_results(results, args.out, "")
    _stamp(results)
    return 0


def compare(args: argparse.Namespace) -> int:
    """Run a scenario under two RuleSets on the same seeds; report paired differences."""
    rules_a, _ = _setup(args.a, args.plugin)
    rules_b, _ = _setup(args.b, None)
    s = load_scenario(args.scenario)
    run_a, run_b, diffs = compare_rules(s, rules_a, rules_b, args.trials, args.workers)
    _say(f"Scenario {s.name}: B ({rules_b.name}) minus A ({rules_a.name}), paired by seed")
    _say(f"{'metric':<12} {'A':<26} {'B':<26} B - A")
    for d in diffs:
        _say(f"{d.metric:<12} {d.a!s:<26} {d.b!s:<26} {d.diff}")
    _stamp([run_a, run_b])
    return 0


def suite(args: argparse.Namespace) -> int:
    """Run a suite and print or write its report. parity: every published review
    configuration in lockstep with the review's simulator, beside the review's figures.
    positioning (M2), ranged (M3), phase (M4) and cores (M5): the milestone suites;
    objectives (O1): the objective scenarios, pursuers ignoring or playing the objective."""
    if args.name == "parity":
        return _parity(args.scale, args.workers, args.out)
    from stamina_engine.rules.ruleset import preset

    rules = preset("v0.9")
    stamp = collect(rules).text()  # before running: the code that runs
    trials, workers = args.trials, args.workers
    if args.name == "positioning":
        from stamina_engine.experiments.positioning import ROWS, render, run_rows

        report = render(run_rows(ROWS, trials, workers), stamp, trials)
    elif args.name == "ranged":
        from stamina_engine.analysis.ranged import render_table5
        from stamina_engine.experiments.positioning import run_rows
        from stamina_engine.experiments.ranged_suite import ROWS as RANGED_ROWS
        from stamina_engine.experiments.ranged_suite import render as render_ranged

        rows = run_rows(RANGED_ROWS, trials, workers)
        report = render_ranged(rows, stamp, trials, render_table5(rules))
    elif args.name == "phase":
        from stamina_engine.experiments import phase_suite

        report = phase_suite.render(phase_suite.run(trials, workers), stamp, trials)
    elif args.name == "objectives":
        from stamina_engine.experiments import objectives_suite

        report = objectives_suite.render(objectives_suite.run(trials, workers), stamp, trials)
    else:
        from stamina_engine.experiments import cores_suite

        report = cores_suite.render(cores_suite.run(trials, workers), stamp, trials)
    _write_or_print(report, args.out)
    return 0


def _parity(scale: float, workers: int, out: Path | None) -> int:
    from stamina_engine.experiments.oracle_bridge import Knobs
    from stamina_engine.experiments.parity import cases, render, rules_for, run_cases

    stamp = collect(rules_for(Knobs())).text()  # before running: the code that runs
    results = run_cases(cases(), scale, workers)
    _write_or_print(render(results, stamp, scale), out)
    bad = sum(len(r.mismatches) for r in results)
    _say(f"{sum(len(r.records) for r in results)} fights, {bad} mismatches with the oracle")
    return 1 if bad else 0


def map_list(args: argparse.Namespace) -> int:
    """The library maps (data/maps)."""
    for name in library_maps():
        _say(name)
    return 0


def map_show(args: argparse.Namespace) -> int:
    """Print a map with column and row numbers, its spawn markers and its legend."""
    field = load_map(args.name, Path.cwd())
    _say(f"{field.name}: {field.width} x {field.height}")
    _say(field.render())
    for marker, cells in sorted(field.spawns.items()):
        _say(f"spawn {marker}: " + ", ".join(f"({x}, {y})" for x, y in cells))
    _say("legend: " + ", ".join(f"{ch!r} {terrain}" for ch, terrain in field.legend))
    return 0


def play(args: argparse.Namespace) -> int:
    """Play one fight as one combatant, at the keyboard; everyone else keeps the scenario's
    agent. Every decision is timed; --log keeps them for `se load --session`."""
    from stamina_engine.experiments.session import play as play_fight
    from stamina_engine.experiments.session import write_session

    s = load_scenario(args.scenario)
    try:
        result, seed = play_fight(s, args.who, args.trial)
    except (EOFError, KeyboardInterrupt):
        _say("\nsession abandoned; nothing logged")
        return 1
    _say(f"{result.reason}: winner {result.winner}, {result.rounds} rounds")
    if args.log is not None:
        write_session(args.log, s, args.who, args.trial, seed, result)
        _say(f"wrote {args.log}")
    return 0


def load(args: argparse.Namespace) -> int:
    """The load report (Review F11): requests per round by kind, their option counts, how
    many are non-trivial, dice per attack, and for sessions the seconds each took."""
    from stamina_engine.experiments.load import load_report

    scenario: Path | None = args.scenario
    sessions: list[Path] = args.session or []
    if (scenario is None) == (not sessions):
        raise UsageError("give a scenario or --session logs, not both")
    if scenario is not None:
        s = load_scenario(scenario)
        result = run_scenario(s, args.trials, args.workers)
        rounds = sum(int(f["rounds"]) for f in result.fights) * len(s.combatants)
        report = load_report(
            result.decisions,
            result.attacks,
            rounds,
            f"Load: {s.name}, engine agents, {args.trials} trials",
        )
    else:
        from stamina_engine.experiments.session import read_session

        decisions, attacks, rounds = [], [], 0
        for path in sessions:
            sess = read_session(path)
            who = str(sess.header["played_by_human"])
            decisions += [d for d in sess.decisions if d["who"] == who]
            attacks += [a for a in sess.attacks if a["attacker"] == who]
            rounds += int(sess.result.get("rounds", 0))
        title = f"Load: {len(sessions)} session(s), people's decisions"
        report = load_report(decisions, attacks, rounds, title)
    _write_or_print(report, args.out)
    return 0


def trace_cmd(args: argparse.Namespace) -> int:
    """Replay one fight of a scenario: every event, with the board at each turn."""
    from stamina_engine.experiments.trace import trace

    _say(trace(load_scenario(args.scenario), args.trial, args.cell))
    return 0


Handler = Callable[[argparse.Namespace], int]


def _command(
    commands: "argparse._SubParsersAction[argparse.ArgumentParser]", name: str, handler: Handler
) -> argparse.ArgumentParser:
    """A subcommand whose help is its handler's docstring."""
    doc = " ".join((handler.__doc__ or "").split())
    first = doc.split(". ")[0].rstrip(".") + "."
    p = commands.add_parser(name, help=first, description=doc)
    p.set_defaults(handler=handler, parser=p)
    return p


def _plugins(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--plugin",
        type=Path,
        action="append",
        help="A Python file of extra rule variants. Repeatable.",
    )


def _runs(p: argparse.ArgumentParser) -> None:
    p.add_argument("--trials", type=int, help="Override the scenario's trial count.")
    _workers(p)


def _workers(p: argparse.ArgumentParser) -> None:
    p.add_argument("--workers", type=int, default=1, help="Processes to run trials across.")


OUT_PARQUET = "Write Parquet tables (runs, fights, attacks, decisions) here; needs pyarrow."
OUT_REPORT = "Write the report here (markdown)."


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="se", description="Rules engine for the stamina TTRPG (see sim/docs/ENGINE_PLAN.md)."
    )
    commands = parser.add_subparsers(dest="command", metavar="COMMAND")

    def command(name: str, handler: Handler) -> argparse.ArgumentParser:
        return _command(commands, name, handler)

    p = command("table", table)
    p.add_argument("number", type=int, choices=(1, 5, 8), help="Review table number: 1, 5 or 8.")
    p.add_argument(
        "--ruleset",
        default="v0.9",
        help="A preset name (v0.9, review-candidate, review-sim) or a .toml file.",
    )
    p.add_argument(
        "--rounding",
        choices=[r.value for r in Rounding],
        default=Rounding.HALF_UP.value,
        help="half-even reproduces the review's printed tables.",
    )
    _plugins(p)
    p.add_argument(
        "--equipment", default="v0_9", help="Equipment table: v0_9, or a variant in data/equipment."
    )

    p = command("run", run)
    p.add_argument("scenario", type=Path, help="A scenario TOML file.")
    _runs(p)
    p.add_argument("--out", type=Path, help=OUT_PARQUET)
    _plugins(p)

    p = command("sweep", sweep)
    p.add_argument("file", type=Path, help="A sweep TOML file.")
    _runs(p)
    p.add_argument("--out", type=Path, help=OUT_PARQUET)
    _plugins(p)

    p = command("compare", compare)
    p.add_argument("scenario", type=Path, help="A scenario TOML file.")
    p.add_argument("--a", required=True, help="RuleSet A: a preset or a .toml file.")
    p.add_argument("--b", required=True, help="RuleSet B: a preset or a .toml file.")
    _runs(p)
    _plugins(p)

    p = command("suite", suite)
    p.add_argument("name", choices=SUITES, help="Suite to run: " + ", ".join(SUITES) + ".")
    _workers(p)
    p.add_argument("--scale", type=float, default=1.0, help="Parity: share of the review's trials.")
    p.add_argument("--trials", type=int, default=500, help="The other suites: trials per row.")
    p.add_argument("--out", type=Path, help=OUT_REPORT)

    p = commands.add_parser("map", help="Maps: list them, or show one with coordinates.")
    maps = p.add_subparsers(dest="map_command", metavar="COMMAND", required=True)
    _command(maps, "list", map_list)
    p = _command(maps, "show", map_show)
    p.add_argument("name", help="A library map name, or a .txt file.")

    p = command("play", play)
    p.add_argument("scenario", type=Path, help="A scenario TOML file.")
    p.add_argument("--as", dest="who", required=True, help="The combatant id you play.")
    p.add_argument("--trial", type=int, default=0, help="Which trial's dice to fight with.")
    p.add_argument("--log", type=Path, help="Write the session log here (JSONL).")

    p = command("load", load)
    p.add_argument(
        "scenario", type=Path, nargs="?", help="A scenario to run with its engine agents."
    )
    p.add_argument(
        "--session", type=Path, action="append", help="Session logs from se play (repeatable)."
    )
    p.add_argument("--trials", type=int, default=200, help="Trials, for a scenario.")
    _workers(p)
    p.add_argument("--out", type=Path, help=OUT_REPORT)

    p = command("trace", trace_cmd)
    p.add_argument("scenario", type=Path, help="A scenario TOML file.")
    p.add_argument("--trial", type=int, default=0, help="Which trial to replay.")
    p.add_argument("--cell", default="", help="Cell key, if the trial came from a sweep.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """The `se` entry point. Returns the exit code: 0 done, 1 a failed check or an
    abandoned session, 2 a bad argument or configuration."""
    parser = build_parser()
    args = parser.parse_args(argv)
    handler: Handler | None = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 0
    try:
        return handler(args)
    except (UsageError, ConfigError) as exc:
        sub: argparse.ArgumentParser = args.parser
        sub.print_usage(sys.stderr)
        print(f"{sub.prog}: error: {exc}", file=sys.stderr)
        return 2


@dataclass(frozen=True)
class CliResult:
    exit_code: int
    output: str


def invoke(args: Sequence[str], stdin: str = "") -> CliResult:
    """Run one `se` command in this process, with `stdin` as its input; stdout and stderr
    come back together as `output`."""
    buffer = io.StringIO()
    saved = sys.stdin
    sys.stdin = io.StringIO(stdin)
    try:
        with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
            try:
                code = main(list(args))
            except SystemExit as exc:  # argparse: --help, or a malformed command line
                code = exc.code if isinstance(exc.code, int) else int(exc.code is not None)
    finally:
        sys.stdin = saved
    return CliResult(code, buffer.getvalue())
