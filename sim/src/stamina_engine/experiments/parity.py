"""The M1 parity suite: every configuration behind the review's published fight tables
(Tables 2, 3, 4, 7, 9 and the Addendum grid), run in lockstep with the review's simulator.

Each fight is played twice, by the oracle and by the engine under review-sim, on the same
seed. The gate is that every pair is identical. The report then sets the engine's figures
(fresh seeds, the review's trial counts) beside the review's printed ones. A printed figure
outside the engine's interval is flagged for investigation, not failed: the review's figures
are rounded, sampled, and some name no policy.
"""

import math
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from fractions import Fraction

from stamina_engine.analysis.strike import mirror_strike
from stamina_engine.core.rng import derive_seed
from stamina_engine.experiments.oracle_bridge import (
    ORACLE_FIGHTERS,
    FightRecord,
    Knobs,
    engine_duel,
    engine_one_v_three,
    oracle_duel,
    oracle_maker,
    oracle_one_v_three,
)
from stamina_engine.experiments.stats import Interval, mean_interval, median, wilson
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.ruleset import RuleSet, review_sim

cites = ("Packet: Melee Attacks", "Packet: Blocking", "Review F1", "Review F6")

MASTER_SEED = 20261103

Published = float | tuple[float, float] | str  # a figure, a range, or text to read by eye


@dataclass(frozen=True)
class Case:
    table: str
    label: str
    kind: str  # duel or swarm
    a: str  # duel: A's build; swarm: the defender's
    b: str  # duel: B's build; swarm: the attackers'
    pol_a: str  # duel: A's policy; swarm: the attackers' policy
    pol_b: str  # duel: B's policy; swarm: "attacks" or "never" for the defender
    knobs: Knobs
    trials: int
    review: tuple[tuple[str, Published], ...] = ()
    note: str = ""


def _k(spec: str) -> str:
    return {
        "k3": "fixed:3",
        "k2": "fixed:2",
        "k1": "fixed:1",
        "reserve5": "reserve:5",
        "chip-kill": "chipkill",
    }.get(spec, spec)


# --- the review's published figures --------------------------------------------------

TABLE2_POLICIES = ["alpha", "k3", "k2", "k1", "reserve5", "chip-kill"]
TABLE2 = [  # rows A's policy, columns B's: A win % / draw % / mean rounds
    [(49, 1, 6.3), (47, 1, 6.9), (54, 2, 7.5), (77, 23, 13.6), (77, 3, 8.6), (52, 2, 6.6)],
    [(53, 2, 6.8), (50, 2, 7.4), (54, 3, 8.3), (74, 26, 13.4), (79, 2, 8.5), (55, 2, 6.8)],
    [(45, 2, 7.1), (42, 1, 7.9), (51, 2, 9.2), (74, 26, 14.7), (73, 4, 10.6), (50, 2, 7.4)],
    [(0, 20, 12.6), (0, 21, 12.1), (0, 24, 13.7), (0, 100, 30), (0, 51, 21.9), (0, 25, 13.2)],
    [(22, 2, 8.3), (18, 4, 9.2), (22, 4, 10.6), (54, 46, 21), (50, 4, 11.3), (22, 3, 9.1)],
    [(50, 1, 6.8), (48, 2, 7.3), (50, 2, 7.5), (78, 22, 13.2), (76, 4, 9.2), (55, 2, 6.4)],
]

TABLE7 = [  # (label, armored, unarmored, armored win % for alpha, chip-kill, 2-step)
    ("L1 heavy+shield v duelist", "l1_heavy", "l1_duelist", (79, 88, 87)),
    ("L1 sample v duelist", "l1_sample", "l1_duelist", (80, 86, 85)),
    ("L1 sample v same-stats two-hander", "l1_sample", "l1_twohand", (73, 74, 86)),
    ("L1 sample v greatsword", "l1_sample", "l1_greatsword", (77, 78, 84)),
    ("L30 heavy+shield v duelist", "l30_heavy", "l30_duelist", (63, 64, 78)),
    ("L30 sample v duelist", "l30_sample", "l30_duelist", (70, 70, 82)),
]

TABLE9 = {  # variant: (knobs, the review's duel columns, as printed)
    "Baseline v0.9": (
        Knobs(),
        "L1 duel 69% first mover / 1% draws; L30 draws 6% (alpha), 75% (k2)",
    ),
    "A: surcharge +2": (Knobs(step_slope=2), "L1 61% / 17%, 13 rounds; L30 draws 68–86%"),
    "B: blocks every 2nd": (Knobs(block_slope=0.5), "L1 67% / 24%, 13 rounds; L30 draws 94–100%"),
    "A + B": (Knobs(step_slope=2, block_slope=0.5), "L1 45% / 63%; L30 draws 100%"),
    "D: no crit doubling": (Knobs(crit_mode="none"), "L1 55% / 9%, 13 rounds"),
}

ADDENDUM = [  # (label, knobs, L1 strike, L1 duel, L30 strike, L30 duel) as printed
    ("v0.9 as written", Knobs(), (6.1, 35), "3–4, 69%, 0%", (5.2, 8), "9–11, 67%, 10%"),
    (
        "Crit +1 per crit die",
        Knobs(crit_mode="linear1"),
        (4.7, 16),
        "7, 59%, 0%",
        (5.6, 2),
        "7, 54%, 0%",
    ),
    ("Crit none", Knobs(crit_mode="none"), (3.8, 1), "13, 59%, 12%", (4.5, 0), "30, 51%, 49%"),
    (
        "Surcharge +2, crit x2",
        Knobs(step_slope=2),
        (2.3, 6),
        "12, 64%, 18%",
        (2.2, 0),
        "30, 57%, 83%",
    ),
    (
        "Surcharge +2, crit +2 per crit die",
        Knobs(step_slope=2, crit_mode="linear2"),
        (3.2, 6),
        "7, 55–64%, 0%",
        (4.6, 5),
        "5–7, 54–57%, 0% (MD 6) / 4, 46% (MD 5)",
    ),
    (
        "Surcharge +2, crit +1 per crit die",
        Knobs(step_slope=2, crit_mode="linear1"),
        (2.6, 0),
        "11, 54–61%, 3%",
        (3.7, 0),
        "11–15, 56%, 0%",
    ),
    (
        "Block slope 1/2, crit x2",
        Knobs(block_slope=0.5),
        (2.8, 17),
        "15–17, 64–70%, 27%",
        (0.9, 0),
        "30, 65%, 96%",
    ),
    (
        "Block slope 1/2, crit +2 per crit die",
        Knobs(block_slope=0.5, crit_mode="linear2"),
        (3.4, 18),
        "6–7, 63–68%, 0%",
        (4.0, 4),
        "5–7, 60%, 0%",
    ),
]


def cases() -> list[Case]:
    out: list[Case] = []
    for i, pa in enumerate(TABLE2_POLICIES):
        for j, pb in enumerate(TABLE2_POLICIES):
            win, draw, rounds = TABLE2[i][j]
            out.append(
                Case(
                    "Table 2",
                    f"{pa} v {pb}",
                    "duel",
                    "l1_sample",
                    "l1_sample",
                    _k(pa),
                    _k(pb),
                    Knobs(),
                    600,
                    (("A wins %", win), ("draws %", draw), ("rounds mean", rounds)),
                )
            )
    t3: list[tuple[str, str, str, str, str, tuple[tuple[str, Published], ...]]] = [
        (
            "L1 alpha v alpha",
            "l1_sample",
            "l1_sample",
            "alpha",
            "alpha",
            (("rounds median", 4), ("rounds mean", 6.5), ("first mover %", 69), ("loser HP", -3)),
        ),
        (
            "L1 k2 v k2",
            "l1_sample",
            "l1_sample",
            "fixed:2",
            "fixed:2",
            (
                ("rounds median", 6),
                ("rounds mean", 8.7),
                ("first mover %", 65),
                ("loser HP", -4),
                ("winner untouched %", 85),
            ),
        ),
        (
            "L1 chip-kill v chip-kill",
            "l1_sample",
            "l1_sample",
            "chipkill",
            "chipkill",
            (
                ("rounds median", 4),
                ("rounds mean", 6.3),
                ("first mover %", (69, 72)),
                ("loser HP", -3),
                ("winner untouched %", 63),
            ),
        ),
        (
            "L30 alpha v alpha",
            "l30_sample",
            "l30_sample",
            "alpha",
            "alpha",
            (
                ("draws %", 6),
                ("rounds median", 9),
                ("rounds mean", 11.5),
                ("first mover %", 64),
                ("loser HP", -3),
                ("winner untouched %", 59),
            ),
        ),
        (
            "L30 k2 v k2",
            "l30_sample",
            "l30_sample",
            "fixed:2",
            "fixed:2",
            (
                ("draws %", (75, 77)),
                ("rounds median", 30),
                ("rounds mean", 28),
                ("first mover %", 55),
            ),
        ),
        (
            "L30 STR-brute (MD 4) v sample (MD 6)",
            "l30_strbrute",
            "l30_sample",
            "alpha",
            "alpha",
            (("B wins %", 67), ("rounds median", 2), ("rounds mean", 3.4), ("first mover %", 77)),
        ),
        (
            "L99 alpha v alpha",
            "l99_sample",
            "l99_sample",
            "alpha",
            "alpha",
            (("rounds median", 1), ("rounds mean", 1.6), ("first mover %", 83)),
        ),
    ]
    out += [
        Case("Table 3", label, "duel", a, b, pa, pb, Knobs(), 2000, review)
        for label, a, b, pa, pb, review in t3
    ]
    t4 = [
        ("sample, 2-step attackers", "l1_sample", "fixed:2", "attacks", (1.5, 1)),
        ("sample, 1-step attackers", "l1_sample", "fixed:1", "attacks", (4.0, 4)),
        ("sample, chip-kill attackers", "l1_sample", "chipkill", "attacks", (1.0, 1)),
        ("sample never attacks, 2-step attackers", "l1_sample", "fixed:2", "never", (1.6, 2)),
        ("heavy armor + shield, 2-step attackers", "l1_heavy", "fixed:2", "attacks", (1.7, 2)),
    ]
    out += [
        Case(
            "Table 4",
            label,
            "swarm",
            d,
            "l1_sample",
            pol,
            def_mode,
            Knobs(),
            1000,
            (
                ("defender down %", 100),
                ("rounds to down mean", mean),
                ("rounds to down median", med),
                ("attackers downed per fight", (0.0, 0.01)),
            ),
        )
        for label, d, pol, def_mode, (mean, med) in t4
    ]
    for label, a, b, wins in TABLE7:
        for pol, win in zip(("alpha", "chipkill", "fixed:2"), wins, strict=True):
            out.append(
                Case(
                    "Table 7",
                    f"{label} ({pol})",
                    "duel",
                    a,
                    b,
                    pol,
                    pol,
                    Knobs(),
                    2000,
                    (("A wins %", win),),
                )
            )
    for variant, (knobs, printed) in TABLE9.items():
        l1 = [
            ("alpha", "alpha", 1500),
            ("fixed:2", "fixed:2", 1500),
            ("alpha", "fixed:2", 1500),
            ("alpha", "reserve:5", 1500),
            ("chipkill", "chipkill", 800),
        ]
        l30 = [
            ("alpha", "alpha", 1500),
            ("fixed:2", "fixed:2", 1500),
            ("chipkill", "chipkill", 800),
        ]
        for build, matchups in (("l1_sample", l1), ("l30_sample", l30)):
            for pa, pb, n in matchups:
                out.append(
                    Case(
                        "Table 9",
                        f"{variant}: {build[:3].upper()} {pa} v {pb}",
                        "duel",
                        build,
                        build,
                        pa,
                        pb,
                        knobs,
                        n,
                        (),
                        printed,
                    )
                )
    for label, knobs, _, l1_duel, _, l30_duel in ADDENDUM:
        builds = [("l1_sample", l1_duel), ("l30_sample", l30_duel)]
        if knobs == Knobs(step_slope=2, crit_mode="linear2"):
            builds.append(("parity/l30_md5", l30_duel))
        for build, printed in builds:
            for pol in ("chipkill", "alpha"):
                out.append(
                    Case(
                        "Addendum",
                        f"{label}: {build} {pol}",
                        "duel",
                        build,
                        build,
                        pol,
                        pol,
                        knobs,
                        400,
                        (),
                        f"printed: {printed}",
                    )
                )
    return out


# --- running -------------------------------------------------------------------------


def rules_for(knobs: Knobs) -> RuleSet:
    return review_sim().override(knobs.overrides(), name="review-sim")


def _seed(case: Case, trial: int) -> int:
    return derive_seed(MASTER_SEED, f"{case.table}|{case.label}|{trial}")


def _play(case: Case, trial: int) -> tuple[FightRecord, FightRecord]:
    seed = _seed(case, trial)
    rules = rules_for(case.knobs)
    if case.kind == "duel":
        oracle = oracle_duel(
            oracle_maker(case.a), oracle_maker(case.b), case.pol_a, case.pol_b, case.knobs, seed
        )
        engine = engine_duel(
            rules, load_build(case.a), load_build(case.b), case.pol_a, case.pol_b, seed
        )
        return oracle, engine
    variant = str(oracle_maker_variant(case.a))
    attacks = case.pol_b == "attacks"
    oracle = oracle_one_v_three(variant, case.pol_a, attacks, case.knobs, seed)
    engine = engine_one_v_three(
        rules, load_build(case.a), case.pol_a, attacks, seed, load_build(case.b)
    )
    if oracle.winner is None:  # the oracle plays a defender who won out to round 20
        engine = FightRecord(
            engine.winner, oracle.rounds, engine.first, engine.attacks, engine.final
        )
    return oracle, engine


def oracle_maker_variant(build: str) -> str:
    how, _, variant = ORACLE_FIGHTERS[build]
    assert how == "make"
    return str(variant)


@dataclass
class CaseResult:
    case: Case
    records: list[FightRecord] = field(default_factory=list)
    mismatches: list[int] = field(default_factory=list)  # trials where oracle != engine


def _chunk(job: tuple[Case, Sequence[int]]) -> tuple[list[FightRecord], list[int]]:
    case, trials = job
    records, mismatches = [], []
    for t in trials:
        oracle, engine = _play(case, t)
        records.append(engine)
        if oracle != engine:
            mismatches.append(t)
    return records, mismatches


def run_cases(selected: Sequence[Case], scale: float = 1.0, workers: int = 1) -> list[CaseResult]:
    jobs: list[tuple[int, tuple[Case, list[int]]]] = []
    for i, case in enumerate(selected):
        n = max(2, math.ceil(case.trials * scale))
        jobs += [(i, (case, list(range(s, min(n, s + 100))))) for s in range(0, n, 100)]
    if workers > 1:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            parts = list(pool.map(_chunk, [j for _, j in jobs]))
    else:
        parts = [_chunk(j) for _, j in jobs]
    results = [CaseResult(c) for c in selected]
    for (i, _), (records, mismatches) in zip(jobs, parts, strict=True):
        results[i].records += records
        results[i].mismatches += mismatches
    return results


# --- metrics -------------------------------------------------------------------------


def metrics(result: CaseResult) -> dict[str, Interval | float]:
    case, recs = result.case, result.records
    n = len(recs)
    out: dict[str, Interval | float] = {}
    if case.kind == "duel":
        hp_max = {
            "A": derive(load_build(case.a), rules_for(case.knobs)).hp_max,
            "B": derive(load_build(case.b), rules_for(case.knobs)).hp_max,
        }
        decisive = [r for r in recs if r.winner is not None]
        final = [{cid: hp for cid, hp, _ in r.final} for r in recs]
        out["A wins %"] = wilson(sum(r.winner == "A" for r in recs), n)
        out["B wins %"] = wilson(sum(r.winner == "B" for r in recs), n)
        out["draws %"] = wilson(sum(r.winner is None for r in recs), n)
        out["first mover %"] = wilson(sum(r.winner == r.first for r in decisive), len(decisive))
        out["winner untouched %"] = wilson(
            sum(
                f[r.winner] == hp_max[r.winner]
                for r, f in zip(recs, final, strict=True)
                if r.winner is not None
            ),
            len(decisive),
        )
        out["loser HP"] = mean_interval(
            [
                float(f["B" if r.winner == "A" else "A"])
                for r, f in zip(recs, final, strict=True)
                if r.winner is not None
            ]
        )
    else:
        down = [r for r in recs if r.winner == "attackers"]
        out["defender down %"] = wilson(len(down), n)
        out["rounds to down mean"] = mean_interval([float(r.rounds) for r in recs])
        out["rounds to down median"] = median([float(r.rounds) for r in recs])
        out["attackers downed per fight"] = mean_interval(
            [float(sum(1 for cid, hp, _ in r.final if cid != "D" and hp <= 0)) for r in recs]
        )
    rounds = [float(r.rounds) for r in recs]
    out["rounds mean"] = mean_interval(rounds)
    out["rounds median"] = median(rounds)
    return out


def check(value: Interval | float, published: Published, pct: bool) -> str:
    """✓ if the printed figure is consistent with the engine's, ✗ if not, · to read by eye.

    Allows for two independent samples of the same size, plus half the printed rounding unit:
    a figure printed as a whole number ("-3", "28", "54%") was rounded to 1, a figure printed
    with a decimal ("6.3") to 0.1.
    """
    if isinstance(published, str) or not isinstance(value, Interval) or value.n == 0:
        return "·"
    scale = 100.0 if pct else 1.0
    est = value.estimate * scale
    half = (value.high - value.low) / 2 * scale
    lo, hi = (published, published) if isinstance(published, int | float) else published
    whole = all(isinstance(x, int) for x in (lo, hi))
    slack = math.sqrt(2) * half + (0.5 if whole else 0.05)
    return "✓" if lo - slack <= est <= hi + slack else "✗"


def _fmt(value: Interval | float, pct: bool) -> str:
    if not isinstance(value, Interval):
        return f"{value:g}"
    return value.pct() if pct else str(value)


def _pub(published: Published) -> str:
    if isinstance(published, tuple):
        return f"{published[0]:g}–{published[1]:g}"
    return f"{published:g}" if isinstance(published, int | float) else published


# --- the report ----------------------------------------------------------------------


def strike_rows() -> list[tuple[str, str, str, str]]:
    """The Addendum's strike columns, computed exactly: (config, cell, engine, printed)."""
    rows = []
    for label, knobs, l1, _, l30, _ in ADDENDUM:
        rules = rules_for(knobs)
        for build, printed in (("l1_sample", l1), ("l30_sample", l30)):
            p = derive(load_build(build), rules)
            s = mirror_strike(p.main, p.stamina_max, p.hp_max, rules)
            hp, down = float(s.mean_injury), 100 * float(s.p_down)
            ok = _strike_ok(s.mean_injury, s.p_down, s.injury, printed, 4000)
            rows.append(
                (
                    label,
                    build,
                    f"{hp:.2f} HP, {down:.1f}%",
                    f"{printed[0]:g} HP, {printed[1]:g}% {ok}",
                )
            )
    return rows


def _strike_ok(
    mean: Fraction, p: Fraction, dist: dict[int, Fraction], printed: tuple[float, float], n: int
) -> str:
    var = float(sum((i - mean) ** 2 * q for i, q in dist.items()))
    ok_mean = abs(float(mean) - printed[0]) <= 0.05 + 4 * math.sqrt(var / n)
    x = float(p)
    ok_p = abs(100 * x - printed[1]) <= 0.5 + 400 * math.sqrt(x * (1 - x) / n) + 1e-9
    return "✓" if ok_mean and ok_p else "✗"


def render(results: Sequence[CaseResult], stamp: str, scale: float) -> str:
    total = sum(len(r.records) for r in results)
    bad = sum(len(r.mismatches) for r in results)
    lines = [
        "# M1 parity report",
        "",
        "Every configuration behind the review's published fight tables, run in lockstep: the",
        "review's simulator (`sim/tests/oracle/sim.py`) and the engine under `review-sim` play",
        "each fight on the same seed. **The gate is that every pair of fights is identical.** The",
        "figures below are the engine's (identical to the oracle's), at the review's trial counts",
        f"× {scale:g}, beside the review's printed figures. ✓: consistent; ✗: outside the",
        "engine's interval allowing for the review's own sampling and rounding, to investigate;",
        "·: the review gives a range or text (or names no policy), so read by eye.",
        "",
        f"**Fights: {total}. Mismatches with the oracle: {bad}.**",
        "",
        "```text",
        stamp,
        "```",
        "",
    ]
    flagged: list[str] = []
    by_table: dict[str, list[CaseResult]] = {}
    for r in results:
        by_table.setdefault(r.case.table, []).append(r)

    if "Table 2" in by_table:
        rs = {r.case.label: r for r in by_table["Table 2"]}
        lines += [
            "## Table 2: level-1 strategy matrix",
            "",
            "A win % / draw % / mean rounds, engine (review). 600 fights per cell.",
            "",
            "| A \\ B | " + " | ".join(TABLE2_POLICIES) + " |",
            "|---" * (len(TABLE2_POLICIES) + 1) + "|",
        ]
        for pa in TABLE2_POLICIES:
            cells = []
            for pb in TABLE2_POLICIES:
                cr = rs.get(f"{pa} v {pb}")
                if cr is None:
                    cells.append("")
                    continue
                m = metrics(cr)
                review = dict(cr.case.review)
                marks = [
                    check(m["A wins %"], review["A wins %"], True),
                    check(m["draws %"], review["draws %"], True),
                    check(m["rounds mean"], review["rounds mean"], False),
                ]
                win, draw, rounds = m["A wins %"], m["draws %"], m["rounds mean"]
                assert isinstance(win, Interval) and isinstance(draw, Interval)
                assert isinstance(rounds, Interval)
                cell = (
                    f"{100 * win.estimate:.0f}/{100 * draw.estimate:.0f}/{rounds.estimate:.1f} "
                    f"({_pub(review['A wins %'])}/{_pub(review['draws %'])}/"
                    f"{_pub(review['rounds mean'])}) {''.join(marks)}"
                )
                if "✗" in marks:
                    flagged.append(f"Table 2 {pa} v {pb}: {cell}")
                cells.append(cell)
            lines.append(f"| {pa} | " + " | ".join(cells) + " |")
        lines.append("")

    for table in ("Table 3", "Table 4", "Table 7"):
        if table not in by_table:
            continue
        lines += [
            f"## {table}",
            "",
            "| Configuration | Metric | Engine (95% CI) | Review | |",
            "|---|---|---|---|---|",
        ]
        for r in by_table[table]:
            m = metrics(r)
            for name, published in r.case.review:
                pct = name.endswith("%")
                value = m[name]
                mark = check(value, published, pct)
                row = (
                    f"| {r.case.label} | {name} | {_fmt(value, pct)} | {_pub(published)} | {mark} |"
                )
                lines.append(row)
                if mark == "✗":
                    flagged.append(
                        f"{table} {r.case.label}, {name}: engine {_fmt(value, pct)}, "
                        f"review {_pub(published)}"
                    )
        lines.append("")

    for table, intro in (
        (
            "Table 9",
            "Duel rows of each variant. The review prints one figure per "
            "variant without naming the policy; read by eye.",
        ),
        (
            "Addendum",
            "Duel columns: rounds (median), first-mover win %, draws %, "
            "for chip-kill and alpha (the review doesn't say which it printed).",
        ),
    ):
        if table not in by_table:
            continue
        lines += [
            f"## {table}",
            "",
            intro,
            "",
            "| Configuration | Fights | Rounds median / mean | First mover % | Draws % | Review |",
            "|---|---|---|---|---|---|",
        ]
        for r in by_table[table]:
            m = metrics(r)
            fm, dr, rm = m["first mover %"], m["draws %"], m["rounds mean"]
            assert (
                isinstance(fm, Interval) and isinstance(dr, Interval) and isinstance(rm, Interval)
            )
            lines.append(
                f"| {r.case.label} | {len(r.records)} | {m['rounds median']:g} / "
                f"{rm.estimate:.1f} | {100 * fm.estimate:.0f} | {100 * dr.estimate:.0f} | "
                f"{r.case.note} |"
            )
        if table == "Addendum":
            lines += [
                "",
                "Strike columns, computed exactly (the review sampled 4,000):",
                "",
                "| Configuration | Build | Engine (exact) | Review |",
                "|---|---|---|---|",
            ]
            for label, build, engine, printed in strike_rows():
                lines.append(f"| {label} | {build} | {engine} | {printed} |")
                if "✗" in printed:
                    flagged.append(
                        f"Addendum strike {label} {build}: engine {engine}, review {printed}"
                    )
        lines.append("")

    lines += ["## Flagged for investigation", ""]
    lines += [f"- {f}" for f in flagged] or ["None."]
    if bad:
        lines += ["", "## Mismatches with the oracle", ""]
        lines += [
            f"- {r.case.table} {r.case.label}: trials {r.mismatches[:10]}"
            for r in results
            if r.mismatches
        ]
    return "\n".join(lines) + "\n"
