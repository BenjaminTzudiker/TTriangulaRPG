"""The phase suite (`se suite phase`): ENGINE_PLAN's eight items in one command, re-run at the
end of every fix-order phase, printed in the review's table layouts where it had one.

1. Exchange tables at L1, L30 and L99, exactly (Tables 1, 5 and 8, and Table 8 under F8's
   variants).
2. Equal duels at three levels on open ground: the policy matrix at L1 (Table 2's layout) and
   the level summary (Table 3's).
3. One against three on open ground and in a corridor, with the attackers' NPC profile as the
   lethality dial (Table 4's layout; Review F6).
4. Archer against an approaching fighter on three maps.
5. Reach control at a door.
6. Retreat to an allied line.
7. Armored against unarmored builds (Table 7's layout), as written and under F4's variants.
8. A 3v3 mixed party on a terrain map, by NPC profile.

Rows of one scenario share trial seeds, so comparisons within a section are paired.
"""

from collections.abc import Sequence
from dataclasses import dataclass

from stamina_engine.analysis.ranged import render_table5
from stamina_engine.analysis.tables import Rounding, render_table1, render_table8, table1, table8
from stamina_engine.experiments.metrics import Row, summarize
from stamina_engine.experiments.positioning import (
    POSITIONING_COLUMNS,
    Column,
    SuiteRow,
    _mean,
    render_rows,
    run_rows,
)
from stamina_engine.experiments.positioning import ROWS as POSITIONING_ROWS
from stamina_engine.experiments.ranged_suite import RANGED_COLUMNS
from stamina_engine.experiments.ranged_suite import ROWS as RANGED_ROWS
from stamina_engine.experiments.runner import RunResult
from stamina_engine.experiments.stats import wilson
from stamina_engine.model.equipment import load_table
from stamina_engine.rules.ruleset import BASELINE, preset

cites = (
    "Packet: Combat",
    "Review F1",
    "Review F4",
    "Review F6",
    "Review F8",
    "Review F9",
    "Review F10",
)

POLICIES = (
    ("alpha", "alpha"),
    ("k2", "fixed:2"),
    ("chip-kill", "chipkill"),
    ("look-ahead", "lookahead"),
)
LEVELS = (("L1", "l1_sample"), ("L30", "l30_sample"), ("L99", "l99_sample"))
TABLE7_PAIRS = (
    ("L1 heavy + shield v duelist", "l1_heavy", "l1_duelist"),
    ("L1 sample v duelist", "l1_sample", "l1_duelist"),
    ("L1 sample v two-hander", "l1_sample", "l1_twohand"),
    ("L1 sample v greatsword", "l1_sample", "l1_greatsword"),
    ("L30 heavy + shield v duelist", "l30_heavy", "l30_duelist"),
    ("L30 sample v duelist", "l30_sample", "l30_duelist"),
)
TABLE7_POLICIES = (("alpha", "alpha"), ("chip-kill", "chipkill"), ("2-step", "fixed:2"))
TABLE7_VARIANTS: tuple[tuple[str, object, str | None], ...] = (
    ("as written", BASELINE, None),
    ("F4 option 1: shield +1 Melee / +2 Ranged", BASELINE, "f4_shield_1"),
    (
        "F4 option 2: two-handers +1 Melee, Agility split",
        {"base": BASELINE, "defenses": {"two_hander_bonus": 1, "agility_split": True}},
        None,
    ),
)
NPC_DIAL = (
    ("minion (1 step, focus)", "minion"),
    ("disciplined (2; 3 against low stamina)", "disciplined_2step"),
    ("berserker (all in)", "berserker"),
    ("cautious (chip-kill, flees, surrenders)", "cautious"),
)
DEFENDERS = (
    ("scripted", {"commit": "fixed:2", "target": "lowest_stamina"}),
    ("tactical", {"kind": "tactical", "commit": "fixed:2"}),
)
ONE_V_THREE = (
    ("open ground, engaged", "one_v_three_engaged.toml"),
    ("corridor", "one_v_three_corridor.toml"),
)


@dataclass(frozen=True)
class Plan:
    duels: list[SuiteRow]
    levels: list[SuiteRow]
    dial: list[SuiteRow]
    ranged: list[SuiteRow]
    reach: list[SuiteRow]
    retreat: list[SuiteRow]
    table7: list[SuiteRow]
    party: list[SuiteRow]

    def rows(self) -> list[SuiteRow]:
        return [
            *self.duels,
            *self.levels,
            *self.dial,
            *self.ranged,
            *self.reach,
            *self.retreat,
            *self.table7,
            *self.party,
        ]


def plan() -> Plan:
    duels = [
        SuiteRow("duels L1", f"{a}|{b}", "duel_open.toml", agents={"A": sa, "B": sb}, side="A")
        for a, sa in POLICIES
        for b, sb in POLICIES
    ]
    levels = [
        SuiteRow(
            f"level {lv}",
            name,
            "duel_open.toml",
            agents={"A": spec, "B": spec},
            builds={"A": build, "B": build},
            side="A",
        )
        for lv, build in LEVELS
        for name, spec in (("alpha", "alpha"), ("chip-kill", "chipkill"))
    ]
    dial = [
        SuiteRow(
            f"1v3 {where}",
            f"{label}|{dname}",
            scenario,
            agents={"x": {"kind": "npc", "profile": p}, "D": dspec},
            side="defender",
        )
        for where, scenario in ONE_V_THREE
        for label, p in NPC_DIAL
        for dname, dspec in DEFENDERS
    ]
    ranged = [r for r in RANGED_ROWS if r.group.startswith("Archer v fighter")]
    reach = [r for r in POSITIONING_ROWS if r.group.startswith("Reach")]
    retreat = [r for r in POSITIONING_ROWS if r.group.startswith("Retreat")]
    table7 = [
        SuiteRow(
            f"table7 {vlabel}",
            f"{plabel}|{pol}",
            "duel_open.toml",
            rules,  # type: ignore[arg-type]
            agents={"A": spec, "B": spec},
            builds={"A": armored, "B": other},
            side="A",
            equipment=equipment,
        )
        for vlabel, rules, equipment in TABLE7_VARIANTS
        for plabel, armored, other in TABLE7_PAIRS
        for pol, spec in TABLE7_POLICIES
    ]
    party = [
        SuiteRow(
            "3v3 mixed party",
            f"NPCs {label}",
            "party_3v3.toml",
            agents={
                "npc": {"kind": "npc", "profile": p},
                "npc_archer": {"kind": "npc", "profile": p},
            },
            side="party",
        )
        for label, p in NPC_DIAL
    ]
    return Plan(duels, levels, dial, ranged, reach, retreat, table7, party)


# --- layouts ----------------------------------------------------------------------------


def _pct(fights: Sequence[Row], key: str) -> str:
    return f"{100 * sum(1 for f in fights if f.get(key)) / max(1, len(fights)):.0f}"


def table2(results: dict[tuple[str, str], RunResult]) -> str:
    """Review Table 2's layout: A's policy by row, B's by column; A wins / draws (%)."""
    names = [n for n, _ in POLICIES]
    lines = ["| A \\ B | " + " | ".join(names) + " |", "|---" * (len(names) + 1) + "|"]
    for a in names:
        cells = []
        for b in names:
            f = results[("duels L1", f"{a}|{b}")].fights
            draws = sum(1 for x in f if x["winner"] is None)
            cells.append(f"{_pct(f, 'win:A')} / {100 * draws / max(1, len(f)):.0f}")
        lines.append(f"| {a} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def table3(results: dict[tuple[str, str], RunResult]) -> str:
    """Review Table 3's layout, by level: first mover, rounds, winner untouched, loser's HP."""
    lines = [
        "| Level | Policies | First mover wins | Rounds | Winner untouched "
        "| Loser ends at (HP) | Draws |",
        "|---|---|---|---|---|---|---|",
    ]
    for lv, _ in LEVELS:
        for name in ("alpha", "chip-kill"):
            s = summarize(results[(f"level {lv}", name)].fights)
            lines.append(
                f"| {lv} | {name} v {name} | {s.first_mover.pct()} | {s.rounds} | "
                f"{s.winner_untouched.pct()} | {s.loser_hp} | {s.draws.pct()} |"
            )
    return "\n".join(lines)


def table4(results: dict[tuple[str, str], RunResult]) -> str:
    """Review Table 4's layout for 1v3, with the attackers' NPC profile as the dial: the
    defender down / its deaths / rounds, by where it stands and its agent."""
    heads = [f"{where}, {d} defender" for where, _ in ONE_V_THREE for d, _ in DEFENDERS]
    lines = ["| Attackers' profile | " + " | ".join(heads) + " |", "|---" * (len(heads) + 1) + "|"]
    for label, _ in NPC_DIAL:
        cells = []
        for where, _ in ONE_V_THREE:
            for d, _ in DEFENDERS:
                f = results[(f"1v3 {where}", f"{label}|{d}")].fights
                down = wilson(sum(1 for x in f if x.get("down:defender")), len(f))
                dead = _mean(f, "dead:defender").estimate
                rounds = summarize(f).rounds.estimate
                cells.append(f"{100 * down.estimate:.0f}% / {dead:.2f} / {rounds:.1f}")
        lines.append(f"| {label} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def table7(results: dict[tuple[str, str], RunResult]) -> str:
    """Review Table 7's layout: the armored side's win %, alpha / chip-kill / 2-step."""
    out = []
    for vlabel, _, _ in TABLE7_VARIANTS:
        lines = [
            f"**{vlabel}**",
            "",
            "| Pairing | alpha | chip-kill | 2-step |",
            "|---|---|---|---|",
        ]
        for plabel, _, _ in TABLE7_PAIRS:
            cells = [
                _pct(results[(f"table7 {vlabel}", f"{plabel}|{pol}")].fights, "win:A")
                for pol, _ in TABLE7_POLICIES
            ]
            lines.append(f"| {plabel} | " + " | ".join(cells) + " |")
        out.append("\n".join(lines))
    return "\n\n".join(out)


def exact_tables() -> str:
    rules = preset(BASELINE)
    parts = [
        "### Table 1 (attack against full-block cost by k, exact; packet rounding)",
        render_table1(table1(rules, Rounding.HALF_UP), Rounding.HALF_UP),
        "### Table 5 (single shots, exact, beside the review's figures)",
        render_table5(rules),
        "### Table 8 (damage per stamina by commitment, exact)",
        render_table8(table8(rules), Rounding.HALF_UP),
    ]
    for label, table_name, override in (
        ("F8 option 1, die upgrades", "f8_die_upgrades", None),
        (
            "F8 option 2, light weapons skip a surcharge point",
            "v0_9",
            {"surcharge": {"light_exempt": 1}},
        ),
        ("F8 option 3, Strength capped at die size", "f8_str_cap", None),
    ):
        r = rules.override(override) if override else rules
        parts += [
            f"### Table 8 under {label}",
            render_table8(table8(r, load_table(table_name)), Rounding.HALF_UP),
        ]
    return "\n\n".join(parts)


def render(results: Sequence[tuple[SuiteRow, RunResult]], stamp: str, trials: int) -> str:
    by = {(r.group, r.label): run for r, run in results}
    p = plan()

    def sub(rows: list[SuiteRow], columns: Sequence[Column] = POSITIONING_COLUMNS) -> str:
        got = [(r, by[(r.group, r.label)]) for r in rows]
        text = render_rows(got, stamp, trials, "", columns, "se suite phase")
        return text.split("```", 2)[2].lstrip("\n")  # drop the per-section stamp

    sections = [
        "# Phase suite",
        "",
        f"Generated by `se suite phase`: ENGINE_PLAN's eight phase-suite items in one run, "
        f"{trials} trials a fight row, in the review's layouts where it had one. Rows of one "
        "scenario share trial seeds (paired comparisons). Fights are on maps with movement, "
        "off-turn windows and opportunity attacks; duels start adjacent on open ground.",
        "",
        "```text",
        stamp,
        "```",
        "",
        "## 1. Exchange tables, exactly",
        "",
        exact_tables(),
        "",
        "## 2. Equal duels",
        "",
        "### The L1 policy matrix (Table 2's layout): A wins / draws, %",
        "",
        table2(by),
        "",
        "### By level (Table 3's layout)",
        "",
        table3(by),
        "",
        "## 3. One against three, with the attackers' NPC profile as the dial (Table 4's layout)",
        "",
        "Each cell: the defender down at the end / its deaths per fight / rounds.",
        "",
        table4(by),
        "",
        "## 4. Archer against an approaching fighter",
        "",
        sub(p.ranged, RANGED_COLUMNS),
        "## 5-6. Reach at a door; retreat to a line",
        "",
        sub(p.reach + p.retreat),
        "## 7. Armored against unarmored (Table 7's layout): the armored side's win %",
        "",
        table7(by),
        "",
        "## 8. A 3v3 mixed party on a terrain map",
        "",
        sub(p.party),
    ]
    return "\n".join(sections) + "\n"


def run(trials: int, workers: int) -> list[tuple[SuiteRow, RunResult]]:
    return run_rows(plan().rows(), trials, workers)
