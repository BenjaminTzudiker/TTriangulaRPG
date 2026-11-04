"""The cores suite (`se suite cores`): each class core and candidate ability priced in play,
by what using it buys (ENGINE_PLAN M5: "class cores priced in sims").

Each ability's build is the sample fighter's stats with that core (or no core and the
candidate ability). Every row pair plays the same trial seeds with the ability off (the
agent passes every window, and declines Riposte's OA) and on (agents/ability_policy.py), so
the difference is paired. Two settings:

- Equal duels on open ground, starting adjacent, against the sample fighter with abilities
  off (Heavy Swing against the heavy-armor build instead, since it's an anti-armor ability),
  chip-kill agents. The tactical agent plays these duels move for move as chip-kill does
  (one enemy engaging it, it never moves), so they run once.
- One against three on open ground, the attackers committing 2 steps each (Phase 3's
  layout), the ability on the defender, for both agent families.

Then the four class cores against each other, both sides using theirs (chip-kill duels).

A single fight starts at 0 strain (Packet: Strain recovers only overnight), so these are
upper bounds for a day of several fights.
"""

from collections.abc import Mapping, Sequence

from stamina_engine.experiments.metrics import Row, summarize
from stamina_engine.experiments.positioning import (
    Column,
    SuiteRow,
    _mean,
    _wins,
    render_rows,
    run_rows,
)
from stamina_engine.experiments.runner import RunResult
from stamina_engine.experiments.stats import paired_difference

cites = (
    "Packet: Core Abilities",
    "Packet: Candidate Abilities",
    "Packet: Strain",
    "Review F13",
)

ABILITIES: tuple[tuple[str, str, str], ...] = (
    # (label, build with it, duel opponent)
    ("Fighter core", "l1_sample", "l1_sample"),
    ("Barbarian core", "l1_barbarian", "l1_sample"),
    ("Monk core", "l1_monk", "l1_sample"),
    ("Rogue core", "l1_rogue", "l1_sample"),
    ("Heavy Swing (v heavy armor)", "l1_heavy_swing", "l1_heavy"),
    ("Tactical Withdrawal", "l1_withdrawal", "l1_sample"),
    ("Riposte", "l1_riposte", "l1_sample"),
)

DUELIST: Mapping[str, object] = {"commit": "chipkill"}
FAMILIES: tuple[tuple[str, Mapping[str, object]], ...] = (
    # (name, 1v3 defender agent)
    ("scripted", {"commit": "fixed:2", "target": "lowest_stamina"}),
    ("tactical", {"kind": "tactical", "commit": "fixed:2"}),
)

MODES = (("off", "none"), ("on", "use"))
CORES = ABILITIES[:4]
MATRIX = "Core against core (both sides use their cores)"


DUELS = "Duels, chip-kill agents (side A has the ability; B, its opponent, uses none)"


def _ovt_group(family: str) -> str:
    return f"One against three, {family} defender (the defender has the ability)"


def rows() -> list[SuiteRow]:
    out = []
    for label, build, opponent in ABILITIES:
        for mode, uses in MODES:
            out.append(
                SuiteRow(
                    DUELS,
                    f"{label}, {mode}",
                    "duel_open.toml",
                    "v0.9",
                    {"A": {**DUELIST, "abilities": uses}, "B": dict(DUELIST)},
                    {"A": build, "B": opponent},
                    side="A",
                )
            )
    for a_label, a_build, _ in CORES:
        for b_label, b_build, _ in CORES:
            use = {**DUELIST, "abilities": "use"}
            out.append(
                SuiteRow(
                    MATRIX,
                    f"{a_label} v {b_label}",
                    "duel_open.toml",
                    "v0.9",
                    {"A": use, "B": use},
                    {"A": a_build, "B": b_build},
                    side="A",
                )
            )
    for family, defender in FAMILIES:
        for label, build, _ in ABILITIES:
            for mode, uses in MODES:
                out.append(
                    SuiteRow(
                        _ovt_group(family),
                        f"{label}, {mode}",
                        "one_v_three_open.toml",
                        "v0.9",
                        {"D": {**defender, "abilities": uses}},
                        {"D": build},
                        side="defender",
                    )
                )
    return out


def _enemies_down(fights: Sequence[Row], row: SuiteRow) -> str:
    other = "B" if row.side == "A" else "attackers"
    return str(_mean(fights, f"down:{other}"))


CORES_COLUMNS: list[Column] = [
    ("Side wins", _wins),
    ("Draws", lambda f, r: summarize(f).draws.pct()),
    ("Rounds", lambda f, r: str(summarize(f).rounds)),
    ("Enemies down at the end", _enemies_down),
    ("Side deaths", lambda f, r: str(_mean(f, f"dead:{r.side}"))),
    ("Uses per fight", lambda f, r: str(_mean(f, f"abilities:{r.side}"))),
    ("OAs per fight", lambda f, r: str(_mean(f, "oa_taken"))),
    ("Strain at the end", lambda f, r: str(_mean(f, f"strain:{r.side}"))),
    ("Stamina on abilities", lambda f, r: str(_mean(f, f"spent:{r.side}:ability"))),
]


def _paired(off: Sequence[Row], on: Sequence[Row], key: str, scale: float = 1.0) -> str:
    """The mean per-trial difference on - off, with its 95% interval (shared seeds)."""
    by_trial = {f["trial"]: f for f in off}
    pairs = [(f, by_trial[f["trial"]]) for f in on if f["trial"] in by_trial]
    iv = paired_difference(  # b - a: on - off
        [scale * float(was[key] or 0) for _, was in pairs],
        [scale * float(now[key] or 0) for now, _ in pairs],
    )
    digits = 1 if scale != 1 else 2
    return f"{iv.estimate:+.{digits}f} [{iv.low:+.{digits}f}, {iv.high:+.{digits}f}]"


def headline(results: Sequence[tuple[SuiteRow, RunResult]]) -> str:
    """What turning each ability on buys: duel win rate (percentage points), and the rounds
    a lone defender lasts against three, each a paired difference with its 95% interval."""
    by = {(r.group, r.label): run.fights for r, run in results}
    head = ["Ability", "Duel win (pp)"] + [f"1v3 rounds, {family}" for family, _ in FAMILIES]
    lines = ["| " + " | ".join(head) + " |", "|---" * len(head) + "|"]
    for label, _, _ in ABILITIES:
        off, on = by[(DUELS, f"{label}, off")], by[(DUELS, f"{label}, on")]
        cells = [label, _paired(off, on, "win:A", 100.0)]
        for family, _ in FAMILIES:
            off = by[(_ovt_group(family), f"{label}, off")]
            on = by[(_ovt_group(family), f"{label}, on")]
            cells.append(_paired(off, on, "rounds"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def matrix(results: Sequence[tuple[SuiteRow, RunResult]]) -> str:
    """Side A's win rate with its core (rows) against B's (columns), both using them."""
    by = {(r.group, r.label): run.fights for r, run in results}
    names = [label.removesuffix(" core") for label, _, _ in CORES]
    lines = ["| A's core \\ B's core | " + " | ".join(names) + " |", "|---" * 5 + "|"]
    for (a_label, _, _), a_name in zip(CORES, names, strict=True):
        cells = []
        for b_label, _, _ in CORES:
            fights = by[(MATRIX, f"{a_label} v {b_label}")]
            wins = sum(1 for f in fights if f.get("win:A"))
            cells.append(f"{100 * wins / max(1, len(fights)):.0f}%")
        lines.append(f"| {a_name} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render(results: Sequence[tuple[SuiteRow, RunResult]], stamp: str, trials: int) -> str:
    body = render_rows(results, stamp, trials, "Cores suite", CORES_COLUMNS, "se suite cores")
    head, _, tables = body.partition("\n## ")
    intro = (
        "\n## What turning each ability on buys\n\n"
        "Paired differences, ability on minus off, over the same trial seeds, with 95% "
        "intervals. Duels: side A's win rate, in percentage points. One against three: "
        "the rounds the fight lasts, which is how long the defender holds out. The "
        "policies that decide when each ability is used are in "
        "`agents/ability_policy.py`.\n\n" + headline(results) + "\n\n"
        "### Core against core\n\n"
        "Side A's win rate, both sides using their cores (chip-kill duels, adjacent on open "
        "ground; draws are the rest). Each cell's interval is in its row below.\n\n"
        + matrix(results)
        + "\n"
    )
    return f"{head}{intro}\n## {tables}"


def run(trials: int, workers: int) -> list[tuple[SuiteRow, RunResult]]:
    return run_rows(rows(), trials, workers)
