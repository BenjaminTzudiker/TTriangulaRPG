"""The objectives suite (`se suite objectives`, O1): each objective scenario under both agent
families, with the pursuing side ignoring the objective (`kill`, the control) and pursuing
it (`first`). Deniers always play the objective.

Rows of one scenario share trial seeds (the cell key is the scenario name), so the
first-minus-kill difference is a paired comparison on the same dice. If `first` does no
better than `kill`, the objective adds nothing a straight fight doesn't already decide
(OBJECTIVES_PLAN.md).
"""

import tomllib
from collections.abc import Mapping, Sequence

from stamina_engine.experiments.metrics import ENDINGS, Row
from stamina_engine.experiments.positioning import SCENARIOS, SuiteRow, run_rows
from stamina_engine.experiments.runner import RunResult
from stamina_engine.experiments.scenario import AgentSpec, load_scenario
from stamina_engine.experiments.stats import mean_interval, paired_difference, wilson
from stamina_engine.rules.ruleset import BASELINE

cites = (
    "Packet: Running the Game",
    "Review F6",
    "Review F9",
    "Review F10",
    "Review Addendum 2",
)

SCENARIO_FILES = (
    ("Escape: break contact, 2 of 3 out through one gap by round 6", "extraction_3v3.toml"),
    ("Reach: 2 of 3 through two held gaps to the back row by round 8", "breakthrough_3v3.toml"),
    ("Hold: the walled hill, uncontested 2 rounds running by round 10", "hold_hill_3v3.toml"),
    ("Hold: the walled hill, uncontested at the end of round 6", "hold_hill_final_3v3.toml"),
    ("Hold the door: 1v3, still in the corridor at the end of round 4", "hold_the_door_1v3.toml"),
)
MODES = ("kill", "first")


def _scripted(mode: str) -> AgentSpec:
    return {"commit": "fixed:2", "target": "lowest_stamina", "objective": mode}


def _agents(scenario: str, family: str, mode: str) -> Mapping[str, AgentSpec]:
    """Scripted: everyone scripted, deniers in first mode. Tactical: the scenario's own
    agents (tactical, or NPC profiles), with the pursuers' objective mode set."""
    s = load_scenario(SCENARIOS / scenario)
    team = s.objectives[0].team
    out: dict[str, AgentSpec] = {}
    for c in s.combatants:
        m = mode if c.team == team else "first"
        if family == "scripted":
            out[c.id] = _scripted(m)
        else:
            spec = dict(c.agent) if not isinstance(c.agent, str) else {"commit": c.agent}
            spec.setdefault("kind", "tactical")
            out[c.id] = {**spec, "objective": m}
    return out


def scenario_ruleset(scenario: str) -> str | Mapping[str, object]:
    """The RuleSet spec the scenario file names (the baseline if it names none)."""
    table = tomllib.loads((SCENARIOS / scenario).read_text()).get("scenario", {})
    spec = table.get("ruleset", BASELINE)
    return spec if isinstance(spec, str) else dict(spec)


def rows() -> list[SuiteRow]:
    out = []
    for group, scenario in SCENARIO_FILES:
        team = load_scenario(SCENARIOS / scenario).objectives[0].team
        rules = scenario_ruleset(scenario)
        for family in ("scripted", "tactical"):
            for mode in MODES:
                out.append(
                    SuiteRow(
                        group,
                        f"{family}, pursuers {mode}",
                        scenario,
                        rules,
                        agents=_agents(scenario, family, mode),
                        side=team,
                    )
                )
    return out


def run(trials: int, workers: int = 1) -> list[tuple[SuiteRow, RunResult]]:
    return run_rows(rows(), trials, workers)


def _done(fights: Sequence[Row]) -> list[float]:
    return [1.0 if f["objective"] == "done" else 0.0 for f in fights]


def _cells(fights: Sequence[Row], row: SuiteRow) -> list[str]:
    n = len(fights)
    endings = [wilson(sum(1 for f in fights if f["ending"] == how), n).pct() for how in ENDINGS]
    return [
        wilson(int(sum(_done(fights))), n).pct(),
        *endings,
        str(mean_interval([float(f["rounds"]) for f in fights])),
        str(mean_interval([float(f["dead"]) for f in fights])),
    ]


HEADER = (
    "| Row | Objective done | Ended: objective | Ended: objective failed | Ended: side out "
    "| Ended: round cap | Rounds | Deaths per fight |"
)

INTRO = (
    "Each scenario gives one side (the pursuers) an objective; the other side denies it. "
    "Rows run each scenario under both agent families with the pursuers ignoring the "
    "objective (`kill`, the control: today's agents) or playing it (`first`); deniers always "
    "play it. {trials} trials per row. Rows of one scenario share trial seeds, so "
    "first − kill is a paired difference on the same dice. 95% intervals: Wilson for rates, "
    "normal for means and the paired difference. How fights ended: the objective was done, "
    "it failed (deadline passed, or too few pursuers left to do it), one side was out "
    "before either, or the round cap. Objective readings (control, scoring, counts, "
    "deadlines) are stated in each scenario file. The stamp below is the code; each section "
    "names the RuleSet its scenario runs."
)


def render(results: Sequence[tuple[SuiteRow, RunResult]], stamp: str, trials: int) -> str:
    lines = [
        "# Objectives suite (O1)",
        "",
        "Generated by `se suite objectives`. " + INTRO.format(trials=trials),
        "",
        "```text",
        stamp,
        "```",
    ]
    by_group: dict[str, list[tuple[SuiteRow, RunResult]]] = {}
    for row, run_ in results:
        by_group.setdefault(row.group, []).append((row, run_))
    for group, items in by_group.items():
        rules = items[0][1].scenario.rules
        digest = rules.digest()[:12]
        where = f"Scenario `{items[0][0].scenario}`, RuleSet `{rules.name}` digest `{digest}`."
        lines += ["", f"## {group}", "", where, "", HEADER]
        lines.append("|---" * 8 + "|")
        for row, run_ in items:
            lines.append(f"| {row.label} | " + " | ".join(_cells(run_.fights, row)) + " |")
        lines.append("")
        for family in ("scripted", "tactical"):
            pair = {r.label.split()[-1]: run_ for r, run_ in items if r.label.startswith(family)}
            if set(pair) == set(MODES):
                diff = paired_difference(_done(pair["kill"].fights), _done(pair["first"].fights))
                lines.append(f"- {family}: objective done, first − kill: {diff}")
    return "\n".join(lines) + "\n"
