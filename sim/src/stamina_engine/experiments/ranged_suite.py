"""The ranged suite (`se suite ranged`): review Table 5's static part exactly, Review F3's
options on single shots, and archers against approaching melee on three maps across agent
families (Review Table 6 on a grid)."""

from collections.abc import Sequence

from stamina_engine.analysis.ranged import (
    Defender,
    Response,
    bows,
    respond,
    shot,
    table5_defenders,
)
from stamina_engine.experiments.metrics import Row, summarize
from stamina_engine.experiments.positioning import (
    SCENARIOS,
    Column,
    SuiteRow,
    _mean,
    _wins,
    render_rows,
)
from stamina_engine.experiments.runner import RunResult
from stamina_engine.experiments.scenario import ruleset_from_spec
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Ranged Attacks", "Packet: Cover", "Review F3", "Review F10")

TACTICAL_FIGHTER = {"kind": "tactical", "commit": "chipkill"}
SCRIPTED_ARCHER = {"commit": "chipkill", "aims": 3}

MAPS = (
    ("open ground", "archer_open.toml"),
    ("scattered cover", "archer_cover.toml"),
    ("a wall line with gaps", "archer_wall.toml"),
)

F3_VARIANTS: tuple[tuple[str, object], ...] = (
    ("v0.9", "v0.9"),
    (
        "F3 option 1: Dodge folded into RD",
        {"base": "v0.9", "defenses": {"ranged_mode": "dodge_folded"}},
    ),
    (
        "F3 option 2: ranged perfect blocks cost a flat 2",
        {"base": "v0.9", "blocks": {"ranged_flat": 2}},
    ),
    ("F3 option 3: aim as precision", {"base": "v0.9", "ranged": {"aim_mode": "precision"}}),
    ("F11 (b): range bands as -1d6 / -2d6", {"base": "v0.9", "ranged": {"bands": "minus_d6"}}),
)

ROWS: list[SuiteRow] = [
    *[
        row
        for label, scenario in MAPS
        for row in (
            SuiteRow(
                f"Archer v fighter, {label}",
                "scripted archer (3 aims, stands), scripted fighter",
                scenario,
                agents={"A": SCRIPTED_ARCHER},
                side="archer",
            ),
            SuiteRow(
                f"Archer v fighter, {label}",
                "tactical archer, scripted fighter",
                scenario,
                side="archer",
            ),
            SuiteRow(
                f"Archer v fighter, {label}",
                "tactical archer, tactical fighter",
                scenario,
                agents={"F": TACTICAL_FIGHTER},
                side="archer",
            ),
        )
    ],
    *[
        SuiteRow(
            "Archer v unshielded duelist, open ground (F3)",
            f"{label}, both tactical",
            "archer_duelist_open.toml",
            rules,  # type: ignore[arg-type]
            agents={"F": TACTICAL_FIGHTER},
            side="archer",
        )
        for label, rules in F3_VARIANTS
    ],
]

RANGED_COLUMNS: list[Column] = [
    ("Archer wins", _wins),
    ("Draws", lambda f, r: summarize(f).draws.pct()),
    ("First mover wins", lambda f, r: summarize(f).first_mover.pct()),
    ("Rounds", lambda f, r: str(summarize(f).rounds)),
    ("Shots per fight", lambda f, r: str(_mean(f, "shots"))),
    ("Aims per shot", lambda f, r: _ratio(f, "aims", "shots")),
    ("Dives per fight", lambda f, r: str(_mean(f, "dives"))),
    ("OAs per fight", lambda f, r: str(_mean(f, "oa_taken"))),
]


def _ratio(fights: Sequence[Row], top: str, bottom: str) -> str:
    b = sum(f.get(bottom, 0) for f in fights)
    return f"{sum(f.get(top, 0) for f in fights) / b:.2f}" if b else "—"


def _cell(r: Response) -> str:
    return f"{float(r.stamina):.1f} / {float(r.injury):.1f} / {100 * float(r.p_down):.0f}%"


def f3_static(variants: Sequence[tuple[str, RuleSet]]) -> str:
    """One longbow shot from the review's archer, exactly, under each variant, at short and
    medium range: spends / takes / downed for the review's unshielded and shielded targets
    and an Agility-2 duelist (the only one F3 option 1 helps)."""
    lines = [
        "| Variant | Shot | Unarmored, no shield | Light armor, no shield | Shield + medium "
        "| Duelist (AGI 2, no armor or shield) |",
        "|---|---|---|---|---|---|",
    ]
    for label, rules in variants:
        defenders = list(table5_defenders(rules)[:3])
        duelist = derive(load_build("l1_duelist"), rules)
        defenders.append(
            Defender(
                "duelist",
                duelist.main.ranged_defense,
                duelist.main.armor,
                duelist.stamina_max,
                duelist.hp_max,
            )
        )
        name, weapon, fin = bows(rules)[1]
        for band in ("short", "medium"):
            for aims in (1, 2):
                joint = shot(weapon, aims, fin, band, rules)
                cells = []
                for d in defenders:
                    r = respond(joint, d.defense, d.armor, d.stamina, d.hp, rules)
                    cells.append(_cell(r))
                lines.append(
                    f"| {label} | {name}, {aims} aim, {band} | " + " | ".join(cells) + " |"
                )
    return "\n".join(lines)


def render(
    results: Sequence[tuple[SuiteRow, RunResult]], stamp: str, trials: int, table5: str
) -> str:
    variants = [(label, ruleset_from_spec(spec, SCENARIOS)) for label, spec in F3_VARIANTS]
    head = render_rows(results, stamp, trials, "M3 ranged suite", RANGED_COLUMNS, "se suite ranged")
    return (
        head
        + "\n## Review Table 5's static part, exactly\n\n"
        + "Target spends / takes / downed against one shot at short range, exactly, with the "
        + "review's Monte Carlo figures beside each (a check mark where they agree within the "
        + "printed rounding and three standard errors of 4000 rolls).\n\n"
        + table5
        + "\n\n## Review F3's options on one shot, exactly\n\n"
        + "Spends / takes / downed against one longbow shot, by variant and range band.\n\n"
        + f3_static(variants)
        + "\n"
    )
