"""The positioning suite (`se suite positioning`): the M2 scenarios across agent families and
the RuleSet variants Phases 3 and 4 ask about, reported with 95% intervals.

Rows of one scenario share trial seeds (the cell key is the scenario name), so differences
between agents or RuleSets within a scenario are paired comparisons on the same dice.
"""

from collections.abc import Mapping, Sequence
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
    ruleset: str | Mapping[str, object] = "v0.9"
    agents: Mapping[str, AgentSpec] | None = None
    builds: Mapping[str, str] | None = None  # combatant id -> library build
    side: str = ""  # the team whose result the row reports


def _one_v_three(group: str, scenario: str) -> list[SuiteRow]:
    out = []
    for rules in ("v0.9", "review-candidate"):
        for name, spec in (("scripted", SCRIPTED_DEFENDER), ("tactical", TACTICAL_DEFENDER)):
            out.append(
                SuiteRow(
                    group,
                    f"{rules}, {name} defender",
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
            f"{r}, scripted defender",
            "one_v_three.toml",
            r,
            side="defender",
        )
        for r in ("v0.9", "review-candidate")
    ],
    *_one_v_three("1v3, open ground, starting engaged", "one_v_three_engaged.toml"),
    *_one_v_three("1v3, open ground, starting 6 apart", "one_v_three_open.toml"),
    *_one_v_three("1v3, corridor behind the defender", "one_v_three_corridor.toml"),
    SuiteRow("Reach at a door (F9)", "v0.9, FIN 1 spear", "reach_chokepoint.toml", side="spear"),
    SuiteRow(
        "Reach at a door (F9)",
        "v0.9, FIN 0 spear",
        "reach_chokepoint.toml",
        builds={"S": "l1_spear_fin0"},
        side="spear",
    ),
    SuiteRow(
        "Reach at a door (F9)",
        "cap = weapon base + odd FIN, FIN 0 spear",
        "reach_chokepoint.toml",
        {"base": "v0.9", "opportunity": {"cap_rule": "weapon_base"}},
        builds={"S": "l1_spear_fin0"},
        side="spear",
    ),
    SuiteRow(
        "Reach at a door (F9)",
        "v0.9, FIN 1 spear, tactical sword",
        "reach_chokepoint.toml",
        agents={"W": {"kind": "tactical", "commit": "chipkill"}},
        side="spear",
    ),
    SuiteRow(
        "Retreat to a line (Addendum 2)",
        "v0.9, fleer stands and fights (scripted), scripted chasers",
        "retreat_economics.toml",
        agents={"F": "fixed:2"},
        side="line",
    ),
    SuiteRow(
        "Retreat to a line (Addendum 2)",
        "v0.9, tactical fleer, scripted chasers",
        "retreat_economics.toml",
        side="line",
    ),
    SuiteRow(
        "Retreat to a line (Addendum 2)",
        "v0.9, fleer stands and fights (scripted), tactical chasers",
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
            ("v0.9", "v0.9"),
            (
                "F10 option 1 (extra purchases move 1 square)",
                {"base": "v0.9", "movement": {"extra_squares": "one"}},
            ),
            (
                "F10 option 2 (purchased squares capped at Movement)",
                {"base": "v0.9", "movement": {"extra_cap": "free_movement"}},
            ),
        )
    ],
    SuiteRow(
        "L1 duel, open ground, 8 apart",
        "v0.9, chip-kill v chip-kill",
        "l1_duel_open.toml",
        side="A",
    ),
    SuiteRow(
        "L1 duel, open ground, 8 apart",
        "v0.9, tactical v tactical",
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
    if row.builds:
        s = replace(
            s,
            combatants=tuple(
                replace(c, build=load_build(row.builds[c.id])) if c.id in row.builds else c
                for c in s.combatants
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


HEADER = (
    "| Row | Side wins | Draws | First mover wins | Side down at the end | Side deaths | Rounds "
    "| OAs per fight | Off-turn squares per fight |"
)


def render(results: Sequence[tuple[SuiteRow, RunResult]], stamp: str, trials: int) -> str:
    lines = [
        "# M2 positioning suite",
        "",
        "Generated by `se suite positioning`. Each row is one scenario under one RuleSet with "
        f"one set of agents, {trials} trials. Rows in a group share trial seeds, so their "
        "differences are paired comparisons on the same dice. 95% intervals: Wilson for rates, "
        'normal for means. "Side" is the team the row reports: its win rate, and how many of '
        "its creatures are down (incapacitated or dead) and dead when the fight ends. First "
        "mover is the first in initiative, over decisive fights. OAs per fight counts every "
        "opportunity attack made, by either side; off-turn squares counts both sides too. "
        "Every fight here has its first attack in round 1.",
        "",
        "```text",
        stamp,
        "```",
    ]
    group = None
    for row, run in results:
        if row.group != group:
            group = row.group
            lines += ["", f"## {group}", "", HEADER, "|---" * 9 + "|"]
        fights = run.fights
        s = summarize(fights)
        wins = wilson(sum(1 for f in fights if f.get(f"win:{row.side}")), len(fights))
        lines.append(
            f"| {row.label} | {wins.pct()} | {s.draws.pct()} | {s.first_mover.pct()} "
            f"| {_mean(fights, f'down:{row.side}')} | {_mean(fights, f'dead:{row.side}')} "
            f"| {s.rounds} | {_mean(fights, 'oa_taken')} | {_off_turn(fights)} |"
        )
    return "\n".join(lines) + "\n"
