"""The 0.10.0 ranged suite (`se suite ranged10`): the simulator requirements' scenarios S1-S6
under packet 0.10.0, by bow, distance, reaction package, crit rule and agent family (R9).

Each group varies one or two things from the same reference: tactical agents with the
behaviors for ranged fights on, crit rule A (0.10.0), reactions judged where the target ends
(0.10.0). The tactical reaction values a square closer to the shooter at 1 stamina, what
buying it on-turn costs; the last group shows how much that agent weight matters. Rows of
one scenario share trial seeds, so differences inside a group are paired.
The scripted family is the floor: archers shoot with 1 aim and never react, pursuers buy
squares only to keep their attack steps.

The archers other than the longbow's are over the level-1 Expertise budget, as the design
study's were (each at the attributes its bow wants); S6's beast is a stand-in (no stat
blocks, no size rule).
"""

from collections.abc import Mapping, Sequence

from stamina_engine.experiments.metrics import Row, summarize
from stamina_engine.experiments.positioning import Column, SuiteRow, _mean, _wins, render_rows
from stamina_engine.experiments.runner import RunResult
from stamina_engine.experiments.scenario import AgentSpec
from stamina_engine.experiments.stats import mean_interval, wilson
from stamina_engine.rules.ruleset import BASELINE

cites = (
    "Packet: Ranged Attacks",
    "Packet: Range Bands",
    "Packet: Cover",
    "Packet: Critical Hits",
    "Packet: Triggers",
)

TACTICAL: dict[str, object] = {
    "kind": "tactical",
    "commit": "chipkill",
    "aim": "reaction",
    "reaction": "position",
    "approach_weight": "1",  # a square closer is worth what buying it on-turn costs
    "close": "off_turn",
    "buy": "keep_steps",
}
SCRIPTED_ARCHER: AgentSpec = {"commit": "chipkill", "aims": 1}
SCRIPTED_MELEE: AgentSpec = {"commit": "chipkill", "buy": "keep_steps"}

BOWS = (
    ("shortbow", "l1_archer_shortbow"),
    ("longbow", "l1_archer"),
    ("warbow", "l1_archer_warbow"),
    ("superheavy", "l1_archer_superheavy"),
)
MELEE = (("sword and board", "l1_sample"), ("two-hander", "l1_twohand"))
PACKAGES: tuple[tuple[str, str], ...] = (
    ("reactions after (0.10.0)", BASELINE),
    ("cover only", "v0.10.0-cover-only"),
)
CRITS: tuple[tuple[str, str], ...] = (
    ("crit A (0.10.0)", BASELINE),
    ("crit C'", "v0.10.0-crit-c-prime"),
    ("crit C", "v0.10.0-crit-c"),
)


def _family(name: str, archers: Sequence[str], others: Sequence[str]) -> Mapping[str, AgentSpec]:
    if name == "tactical":
        return {cid: TACTICAL for cid in (*archers, *others)}
    return {**{a: SCRIPTED_ARCHER for a in archers}, **{o: SCRIPTED_MELEE for o in others}}


FAMILIES = ("tactical", "scripted")


def _s1() -> list[SuiteRow]:
    rows = []
    for melee, mbuild in MELEE:
        for gap in (4, 8, 12):
            for bow, abuild in BOWS[:3]:
                for fam in FAMILIES:
                    rows.append(
                        SuiteRow(
                            f"S1. Open ground, archer v {melee}",
                            f"{bow}, {gap} apart, {fam}",
                            "s1_archer_v_melee.toml",
                            agents=_family(fam, ["A"], ["F"]),
                            builds={"A": abuild, "F": mbuild},
                            side="archer",
                            spawns={"A": (4, 5), "F": (4 + gap, 5)},
                        )
                    )
    return rows


def _packages(group: str, scenario: str) -> list[SuiteRow]:
    return [
        SuiteRow(
            group,
            f"{melee}, {label}, {fam}",
            scenario,
            rules,
            agents=_family(fam, ["A"], ["F"]),
            builds={"F": mbuild},
            side="archer",
        )
        for melee, mbuild in MELEE
        for label, rules in PACKAGES
        for fam in FAMILIES
    ]


ROWS: list[SuiteRow] = [
    *_s1(),
    *_packages("Reaction packages, open ground, longbow 8 apart", "s1_archer_v_melee.toml"),
    *_packages("S2. Low walls near the fighter's path, longbow 8 apart", "s2_low_walls.toml"),
    *[
        SuiteRow(
            "S3. Two archers and a fighter v a fighter and a caster near cover",
            f"{label}, {fam}",
            "s3_focus_fire.toml",
            rules,
            agents=_family(fam, ["A1", "A2"], ["M", "F", "C"]),
            side="archers",
        )
        for label, rules in PACKAGES
        for fam in FAMILIES
    ],
    *[
        SuiteRow(
            "S4. Two archers v a caster and a shielded knight, 8-10 squares",
            f"{bow}, {clabel}, {fam}",
            "s4_two_archers.toml",
            crules,
            agents=_family(fam, ["A1", "A2"], ["C", "K"]),
            builds={"A1": abuild, "A2": abuild},
            side="archers",
        )
        for bow, abuild in BOWS
        for clabel, crules in CRITS
        for fam in FAMILIES
        if fam == "tactical" or crules == BASELINE
    ],
    *[
        SuiteRow(
            "S5. Archer v a knight in heavy armor (3), 8 apart",
            f"{bow}, {knight}",
            "s5_archer_v_plate.toml",
            agents=_family("tactical", ["A"], ["K"]),
            builds={"A": abuild, "K": kbuild},
            side="archer",
        )
        for bow, abuild in BOWS
        for knight, kbuild in (("shield", "l1_heavy"), ("no shield", "l1_heavy_twohand"))
    ],
    *[
        SuiteRow(
            "Agent sensitivity: what a square closer is worth to a reaction (S1, longbow, 8 apart)",
            f"approach_weight {weight}, sword and board",
            "s1_archer_v_melee.toml",
            agents={
                "A": TACTICAL,
                "F": {**TACTICAL, "approach_weight": weight},
            },
            side="archer",
        )
        for weight in ("0", "1/2", "1", "2")
    ],
    *[
        SuiteRow(
            "S6. Two archers v an armored beast (armor 4, HP 14), 10 apart",
            f"{bow}",
            "s6_archers_v_beast.toml",
            agents=_family("tactical", ["A1", "A2"], ["B"]),
            builds={"A1": abuild, "A2": abuild},
            side="archers",
        )
        for bow, abuild in BOWS
    ],
]


def _others(fights: Sequence[Row], row: SuiteRow) -> list[str]:
    teams = {k.split(":", 1)[1] for f in fights[:1] for k in f if k.startswith("win:")}
    return sorted(teams - {row.side})


def _down_r2(fights: Sequence[Row], row: SuiteRow) -> str:
    """Any of the other side down by the end of round 2 (the focus-fire measure)."""
    others = _others(fights, row)
    hits = sum(1 for f in fights if any(f.get(f"down_by_r2:{t}") for t in others))
    return wilson(hits, len(fights)).pct()


def _targets_down(fights: Sequence[Row], row: SuiteRow) -> str:
    """Each of the other side's creatures: how often it ends the fight down."""
    if not fights:
        return "—"
    first = fights[0]
    ids = sorted(
        k.split(":", 1)[1] for k in first if k.startswith("team:") and first[k] != row.side
    )
    n = len(fights)
    return ", ".join(
        f"{cid} {100 * sum(1 for f in fights if f.get(f'fell:{cid}') is not None) / n:.0f}%"
        for cid in ids
    )


def _hp_per_stamina(fights: Sequence[Row], row: SuiteRow) -> str:
    hp = sum(f.get(f"shot_hp:{row.side}", 0) for f in fights)
    st = sum(f.get(f"spent:{row.side}:shot", 0) for f in fights)
    return f"{hp / st:.2f}" if st else "—"


def _reactions(fights: Sequence[Row], row: SuiteRow) -> str:
    """Shots by the target's answer: stay / close / cover / back / shift, %."""
    shots = sum(f.get("shots", 0) for f in fights)
    if not shots:
        return "—"
    kinds = [sum(f.get(f"reactions:{k}", 0) for f in fights) for k in REACTIONS]
    stay = shots - sum(kinds)
    return " / ".join(f"{100 * n / shots:.0f}" for n in (stay, *kinds))


REACTIONS = ("close", "cover", "back", "shift")


def _reaction_cost(fights: Sequence[Row], row: SuiteRow) -> str:
    n = sum(sum(f.get(f"reactions:{k}", 0) for k in REACTIONS) for f in fights)
    return f"{sum(f.get('reaction_cost', 0) for f in fights) / n:.1f}" if n else "—"


def _melee_round(fights: Sequence[Row], row: SuiteRow) -> str:
    rounds = [float(f["melee_round"]) for f in fights if f.get("melee_round") is not None]
    if not rounds:
        return "none"
    never = 100 * (len(fights) - len(rounds)) / len(fights)
    return f"{mean_interval(rounds)}" + (f"; none {never:.0f}%" if never else "")


def _t1(fights: Sequence[Row], row: SuiteRow) -> str:
    spend = [float(f["t1_shot_spend"]) for f in fights if f.get("t1_shot_spend") is not None]
    keep = [float(f["t1_shot_reserve"]) for f in fights if f.get("t1_shot_reserve") is not None]
    if not spend:
        return "—"
    return f"{sum(spend) / len(spend):.1f} / {sum(keep) / len(keep):.1f}"


def _bands(fights: Sequence[Row], row: SuiteRow) -> str:
    counts = [sum(f.get(f"shots_band{k}", 0) for f in fights) for k in ("1", "2", "3plus")]
    total = sum(counts)
    return " / ".join(f"{100 * n / total:.0f}" for n in counts) if total else "—"


def _crits(fights: Sequence[Row], row: SuiteRow) -> str:
    shots = sum(f.get("shots", 0) for f in fights)
    return f"{sum(f.get('shot_crits', 0) for f in fights) / shots:.2f}" if shots else "—"


def _pb(fights: Sequence[Row], row: SuiteRow) -> str:
    n = len(fights)
    provoked = sum(f.get("pb_provoked", 0) for f in fights) / n
    taken = sum(f.get("pb_taken", 0) for f in fights) / n
    return f"{provoked:.2f} / {taken:.2f}"


COLUMNS: list[Column] = [
    ("Archers win", _wins),
    ("Rounds", lambda f, r: str(summarize(f).rounds)),
    ("Targets down by round 2", _down_r2),
    ("Down at the end", _targets_down),
    ("Shots per fight", lambda f, r: str(_mean(f, "shots"))),
    ("HP per shot stamina", _hp_per_stamina),
    ("Answers to shots, % (stay / close / cover / back / shift)", _reactions),
    ("Stamina per reaction", _reaction_cost),
    ("First melee round", _melee_round),
    ("Turn-1 shooter spend / left", _t1),
    ("Shots by band, % (1 / 2 / 3+)", _bands),
    ("Crit dice per shot", _crits),
    ("Point-blank OAs provoked / made", _pb),
]

NOTES = """
## Reading the columns

- **Archers win:** the archers' side.
- **Targets down by round 2:** any creature of the other side down (incapacitated or dead) by
  the end of round 2: the focus-fire measure.
- **Down at the end:** each creature's rate.
- **HP per shot stamina:** HP the archers' shots took, per stamina they spent on shots and
  aim.
- **Answers to shots:** what the target did after the roll. Close: ended with the shooter in
  its reach. Cover: better cover. Back: farther away. Shift: anything else. Stay: no move.
  **Stamina per reaction** includes what the opportunity attacks it provoked cost.
- **First melee round:** the first round anyone made a melee attack, an OA included (mean;
  "none" is the share of fights with none).
- **Turn-1 shooter spend / left:** for creatures that shot in their first turn, that turn's
  stamina and what was left at its end, before recovery.
- **Shots by band:** where the target was when it blocked.
- **Point-blank OAs:** per fight, the enemies a point-blank shot provoked, and the
  opportunity attacks they made.
"""


def render(results: Sequence[tuple[SuiteRow, RunResult]], stamp: str, trials: int) -> str:
    head = render_rows(results, stamp, trials, "0.10.0 ranged suite", COLUMNS, "se suite ranged10")
    return head + NOTES
