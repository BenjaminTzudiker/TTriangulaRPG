"""The positioning suite (`se suite positioning`): the M2 scenarios across agent families and
the RuleSet variants Phases 3 and 4 ask about, reported with 95% intervals.

Rows of one scenario share trial seeds (the cell key is the scenario name), so differences
between agents or RuleSets within a scenario are paired comparisons on the same dice.
"""

from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path

from stamina_engine.experiments.metrics import Row, summarize
from stamina_engine.experiments.runner import RunResult, run_scenario
from stamina_engine.experiments.scenario import (
    AgentSpec,
    Scenario,
    load_scenario,
    ruleset_from_spec,
)
from stamina_engine.experiments.stats import Interval, mean_interval, wilson
from stamina_engine.model.build import load_build
from stamina_engine.rules.ruleset import BASELINE

cites = ("Packet: Positioning", "Review F6", "Review F9", "Review F10", "Review Addendum 2")

SCENARIOS = Path(__file__).resolve().parent.parent / "data" / "scenarios"

SCRIPTED_DEFENDER: AgentSpec = {"commit": "fixed:2", "target": "lowest_stamina"}
TACTICAL_CHASER: AgentSpec = {"kind": "tactical", "commit": "alpha", "target": "first"}
TACTICAL_CHASERS: Mapping[str, AgentSpec] = {"C": TACTICAL_CHASER, "B": TACTICAL_CHASER}
TACTICAL_DEFENDER: AgentSpec = {"kind": "tactical", "commit": "fixed:2"}


@dataclass(frozen=True)
class SuiteRow:
    """One line of the report: a scenario under one RuleSet with one set of agents."""

    group: str
    label: str
    scenario: str  # file in data/scenarios
    ruleset: str | Mapping[str, object] = BASELINE
    agents: Mapping[str, AgentSpec] | None = None
    builds: Mapping[str, str] | None = None  # combatant id -> library build
    side: str = ""  # the team whose result the row reports
    equipment: str | None = None  # an equipment table instead of the scenario's
    spawns: Mapping[str, tuple[int, int]] | None = None  # combatant id -> starting square


# The baseline and the review's candidate fix (+2 surcharge per prior action) on top of it.
SURCHARGE_RULES: tuple[tuple[str, str | Mapping[str, object]], ...] = (
    (BASELINE, BASELINE),
    ("+2 surcharge", {"base": BASELINE, "name": "surcharge+2", "surcharge": {"slope": 2}}),
)


def _one_v_three(group: str, scenario: str) -> list[SuiteRow]:
    out = []
    for rules_label, rules in SURCHARGE_RULES:
        for name, spec in (("scripted", SCRIPTED_DEFENDER), ("tactical", TACTICAL_DEFENDER)):
            out.append(
                SuiteRow(
                    group,
                    f"{rules_label}, {name} defender",
                    scenario,
                    rules,
                    {"D": spec},
                    side="defender",
                )
            )
    return out


ROWS: list[SuiteRow] = [
    *[
        SuiteRow(
            "1v3, all-adjacent (M1)",
            f"{label}, scripted defender",
            "one_v_three.toml",
            r,
            side="defender",
        )
        for label, r in SURCHARGE_RULES
    ],
    *_one_v_three("1v3, open ground, starting engaged", "one_v_three_engaged.toml"),
    *_one_v_three("1v3, open ground, starting 6 apart", "one_v_three_open.toml"),
    *_one_v_three("1v3, corridor behind the defender", "one_v_three_corridor.toml"),
    SuiteRow(
        "Reach at a door (F9)", f"{BASELINE}, FIN 1 spear", "reach_chokepoint.toml", side="spear"
    ),
    SuiteRow(
        "Reach at a door (F9)",
        f"{BASELINE}, FIN 0 spear",
        "reach_chokepoint.toml",
        builds={"S": "l1_spear_fin0"},
        side="spear",
    ),
    SuiteRow(
        "Reach at a door (F9)",
        "cap = weapon base + odd FIN, FIN 0 spear",
        "reach_chokepoint.toml",
        {"base": BASELINE, "opportunity": {"cap_rule": "weapon_base"}},
        builds={"S": "l1_spear_fin0"},
        side="spear",
    ),
    SuiteRow(
        "Reach at a door (F9)",
        f"{BASELINE}, FIN 1 spear, tactical sword",
        "reach_chokepoint.toml",
        agents={"W": {"kind": "tactical", "commit": "chipkill"}},
        side="spear",
    ),
    SuiteRow(
        "Retreat to a line (Addendum 2)",
        f"{BASELINE}, fleer stands and fights (scripted), scripted chasers",
        "retreat_economics.toml",
        agents={"F": "fixed:2"},
        side="line",
    ),
    SuiteRow(
        "Retreat to a line (Addendum 2)",
        f"{BASELINE}, tactical fleer, scripted chasers",
        "retreat_economics.toml",
        side="line",
    ),
    SuiteRow(
        "Retreat to a line (Addendum 2)",
        f"{BASELINE}, fleer stands and fights (scripted), tactical chasers",
        "retreat_economics.toml",
        agents={"F": "fixed:2", **TACTICAL_CHASERS},
        side="line",
    ),
    *[
        SuiteRow(
            "Retreat to a line (Addendum 2)",
            f"{label}, tactical fleer, tactical chasers",
            "retreat_economics.toml",
            rules,
            agents=TACTICAL_CHASERS,
            side="line",
        )
        for label, rules in (
            (BASELINE, BASELINE),
            (
                "v0.9's extra purchases (1 + odd AGI squares each; 1 square from 0.9.1)",
                {"base": BASELINE, "movement": {"extra_squares": "agility"}},
            ),
            (
                "F10 option 2 (purchased squares capped at Movement)",
                {"base": BASELINE, "movement": {"extra_cap": "free_movement"}},
            ),
        )
    ],
    SuiteRow(
        "L1 duel, open ground, 8 apart",
        f"{BASELINE}, chip-kill v chip-kill",
        "l1_duel_open.toml",
        side="A",
    ),
    SuiteRow(
        "L1 duel, open ground, 8 apart",
        f"{BASELINE}, tactical v tactical",
        "l1_duel_open.toml",
        agents={"A": {"kind": "tactical"}, "B": {"kind": "tactical"}},
        side="A",
    ),
]


def build_scenario(row: SuiteRow) -> Scenario:
    s = load_scenario(SCENARIOS / row.scenario)
    s = s.with_rules(ruleset_from_spec(row.ruleset, SCENARIOS))
    if row.agents:
        s = s.with_agents(row.agents)
    if row.equipment is not None:
        s = replace(s, equipment=row.equipment)
    if row.builds:
        s = replace(
            s,
            combatants=tuple(
                replace(c, build=load_build(row.builds[c.id])) if c.id in row.builds else c
                for c in s.combatants
            ),
        )
    if row.spawns:
        spawns = row.spawns
        s = replace(
            s,
            combatants=tuple(
                replace(c, pos=spawns[c.id]) if c.id in spawns else c for c in s.combatants
            ),
        )
    return s


def _run(args: tuple[SuiteRow, int]) -> tuple[SuiteRow, RunResult]:
    row, trials = args
    s = build_scenario(row)
    return row, run_scenario(s, trials, cell=s.name)


def run_rows(
    rows: Sequence[SuiteRow], trials: int, workers: int = 1
) -> list[tuple[SuiteRow, RunResult]]:
    jobs = [(r, trials) for r in rows]
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(_run, jobs))
    return [_run(j) for j in jobs]


def _mean(fights: Sequence[Row], key: str) -> Interval:
    return mean_interval([float(f[key]) for f in fights if f.get(key) is not None])


def _off_turn(fights: Sequence[Row]) -> Interval:
    return mean_interval(
        [
            float(sum(v for k, v in f.items() if k.startswith("moved:") and k.endswith(":off")))
            for f in fights
        ]
    )


Column = tuple[str, Callable[[Sequence[Row], SuiteRow], str]]


def _wins(fights: Sequence[Row], row: SuiteRow) -> str:
    return wilson(sum(1 for f in fights if f.get(f"win:{row.side}")), len(fights)).pct()


POSITIONING_COLUMNS: list[Column] = [
    ("Side wins", _wins),
    ("Draws", lambda f, r: summarize(f).draws.pct()),
    ("First mover wins", lambda f, r: summarize(f).first_mover.pct()),
    ("Side down at the end", lambda f, r: str(_mean(f, f"down:{r.side}"))),
    ("Side deaths", lambda f, r: str(_mean(f, f"dead:{r.side}"))),
    ("Rounds", lambda f, r: str(summarize(f).rounds)),
    ("OAs per fight", lambda f, r: str(_mean(f, "oa_taken"))),
    ("Off-turn squares per fight", lambda f, r: str(_off_turn(f))),
]

INTRO = (
    "Each row is one scenario under one RuleSet with one set of agents, {trials} trials. Rows "
    "in a group share trial seeds, so their differences are paired comparisons on the same "
    'dice. 95% intervals: Wilson for rates, normal for means. "Side" is the team the row '
    "reports: its win rate, and how many of its creatures are down (incapacitated or dead) "
    "and dead when the fight ends. First mover is the first in initiative, over decisive "
    "fights. Per-fight counts (OAs, off-turn squares, shots, dives) include both sides."
)


def render_rows(
    results: Sequence[tuple[SuiteRow, RunResult]],
    stamp: str,
    trials: int,
    title: str,
    columns: Sequence[Column] = POSITIONING_COLUMNS,
    command: str = "se suite positioning",
) -> str:
    lines = [f"# {title}", "", f"Generated by `{command}`. " + INTRO.format(trials=trials), ""]
    lines += ["```text", stamp, "```"]
    header = "| Row | " + " | ".join(name for name, _ in columns) + " |"
    group = None
    for row, run in results:
        if row.group != group:
            group = row.group
            lines += ["", f"## {group}", "", header, "|---" * (len(columns) + 1) + "|"]
        cells = [fn(run.fights, row) for _, fn in columns]
        lines.append(f"| {row.label} | " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def render(results: Sequence[tuple[SuiteRow, RunResult]], stamp: str, trials: int) -> str:
    return render_rows(results, stamp, trials, "M2 positioning suite")
