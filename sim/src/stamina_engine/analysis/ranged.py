"""Single ranged shots, exactly: the joint (total, critical dice) distribution of a shot with
its aim steps, and the defender's best response to it (review Table 5's static part).

Table 5 was Monte Carlo (4000 rolls a cell). check_table5() compares each printed figure
with the exact value, allowing for the printed rounding and three standard errors of a
4000-roll mean or rate.
"""

from collections import defaultdict
from dataclasses import dataclass, replace
from fractions import Fraction
from math import sqrt

from stamina_engine.analysis.dist import POINT, Joint, convolve, die
from stamina_engine.model.build import Loadout, load_build
from stamina_engine.model.derive import WeaponProfile, derive
from stamina_engine.rules.block_solver import DEFAULT_W, best_block
from stamina_engine.rules.exchange import shot_limit
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Ranged Attacks",
    "Packet: Aim",
    "Packet: Range Bands",
    "Packet: Cover",
    "Packet: Blocking",
    "Packet: Weapon Properties",
    "Review F3",
)


ShotJoint = dict[tuple[int, int, int | None], Fraction]
"""(total, critical dice, aim limit) -> probability; the limit is None when it's off."""


def _weapon_roll(weapon: WeaponProfile, widen: int, finesse: int, rules: RuleSet) -> ShotJoint:
    """The weapon's own damage roll, with the aim limit it sets."""
    faces: Joint = POINT  # (sum of faces, crit dice)
    for dice in weapon.damage.dice:
        for _ in range(dice.count):
            faces = convolve(faces, die(dice.size, widen, rules.crit))
    out: dict[tuple[int, int, int | None], Fraction] = defaultdict(Fraction)
    for (total, crits), p in faces.items():
        limit = shot_limit(weapon, (total,), finesse, rules)
        out[(max(weapon.damage.step_floor, total + weapon.damage.flat), crits, limit)] += p
    return dict(out)


def shot(
    weapon: WeaponProfile,
    aims: int,
    finesse: int,
    band: str,
    rules: RuleSet,
    penalty: int = 0,
) -> ShotJoint:
    """The exact (total, crit dice, aim limit) distribution of one shot, as
    exchange.roll_shot rolls it, less a known range penalty (linear bands)."""
    r = rules.ranged
    precision = r.precision_aim()
    widen = weapon.crit_widen + (aims if precision else 0)
    aim = POINT
    if not precision:
        aim_widen = weapon.crit_widen if rules.crit.aim_dice_can_crit else -1
        fin = finesse if r.aim_adds_finesse() else 0
        free = r.free_aims()
        for i in range(free + aims):
            if i >= free and i - free < r.dropped_aim_dice(band):
                aim = {(t + max(0, fin), c): p for (t, c), p in aim.items()}
                continue
            size = r.aim_dice()
            one: dict[tuple[int, int], Fraction] = defaultdict(Fraction)
            for f in range(1, size + 1):
                crit = int(aim_widen >= 0 and rules.crit.is_crit(f, size, aim_widen))
                one[(max(0, f + fin), crit)] += Fraction(1, size)
            aim = convolve(aim, dict(one))
    k = r.penalty_dice(band)
    if k:
        for _ in range(k):
            aim = convolve(aim, {(-t, 0): p for (t, _), p in die(6, -1, rules.crit).items()})
    out: dict[tuple[int, int, int | None], Fraction] = defaultdict(Fraction)
    for (t, c, limit), p in _weapon_roll(weapon, widen, finesse, rules).items():
        for (ta, ca), pa in aim.items():
            out[(max(0, t + ta - penalty), c + ca, limit)] += p * pa
    return dict(out)


def totals(joint: ShotJoint) -> Joint:
    """The (total, crit dice) marginal of a shot's distribution."""
    out: dict[tuple[int, int], Fraction] = defaultdict(Fraction)
    for (t, c, _), p in joint.items():
        out[(t, c)] += p
    return dict(out)


@dataclass(frozen=True)
class Response:
    """The defender's best blocks against a shot: means, P(down), and per-roll variances."""

    stamina: Fraction
    injury: Fraction
    p_down: Fraction
    var_stamina: Fraction
    var_injury: Fraction


def respond(
    joint: ShotJoint,
    defense: int,
    armor: int,
    stamina: int,
    hp: int,
    rules: RuleSet,
    w: Fraction = DEFAULT_W,
) -> Response:
    s = i = d = s2 = i2 = Fraction(0)
    for (total, crits, limit), p in joint.items():
        b = best_block(
            total, crits, defense, armor, stamina, hp, rules, w, ranged=True, limit=limit
        )
        s += p * b.cost
        i += p * b.injury
        s2 += p * b.cost * b.cost
        i2 += p * b.injury * b.injury
        if b.injury >= hp:
            d += p
    return Response(s, i, d, s2 - s * s, i2 - i * i)


# --- review Table 5 -----------------------------------------------------------------------


@dataclass(frozen=True)
class Defender:
    label: str
    defense: int
    armor: int
    stamina: int
    hp: int


def table5_defenders(rules: RuleSet) -> tuple[Defender, ...]:
    """The review's four targets, from library builds."""
    caster = derive(load_build("l1_caster_unarmed"), rules).main
    archer = derive(load_build("l1_archer"), rules)
    light = archer.loadout("blade")
    sample = derive(load_build("l1_sample"), rules)
    caster_p = derive(load_build("l1_caster_unarmed"), rules)
    cover = rules.ranged.cover_bonus(2)
    return (
        Defender(
            "Unarmored, no shield",
            caster.ranged_defense,
            caster.armor,
            caster_p.stamina_max,
            caster_p.hp_max,
        ),
        Defender(
            "Light armor, no shield",
            light.ranged_defense,
            light.armor,
            archer.stamina_max,
            archer.hp_max,
        ),
        Defender(
            "Shield + medium",
            sample.main.ranged_defense,
            sample.main.armor,
            sample.stamina_max,
            sample.hp_max,
        ),
        Defender(
            "Shield + medium + 3/4 cover",
            sample.main.ranged_defense + cover,
            sample.main.armor,
            sample.stamina_max,
            sample.hp_max,
        ),
    )


def bows(rules: RuleSet) -> tuple[tuple[str, WeaponProfile, int], ...]:
    """The review's archer (STR 1, AGI 1, FIN 2): its longbow, and the same archer with a
    shortbow. Returns (name, weapon, finesse)."""
    archer = load_build("l1_archer")
    short = replace(
        archer,
        name="l1_archer_shortbow",
        loadouts=(("bow", Loadout(armor="light", weapon="shortbow", grip="two")),),
    )
    out = []
    for name, build in (("Shortbow", short), ("Longbow", archer)):
        gear = derive(build, rules).loadout("bow")
        assert gear.weapon is not None
        out.append((name, gear.weapon, gear.attributes.FIN))
    return tuple(out)


@dataclass(frozen=True)
class Cell5:
    bow: str
    aims: int
    cost: int
    defender: str
    response: Response


def table5(rules: RuleSet, max_aims: int = 3) -> list[Cell5]:
    pricing = Pricing(rules)
    out = []
    for name, weapon, finesse in bows(rules):
        for aims in range(max_aims + 1):
            joint = shot(weapon, aims, finesse, "short", rules)
            cost = pricing.ranged_attack(weapon.base, aims).total
            for d in table5_defenders(rules):
                r = respond(joint, d.defense, d.armor, d.stamina, d.hp, rules)
                out.append(Cell5(name, aims, cost, d.label, r))
    return out


# Review Table 5 as printed: (stamina spent, HP taken, % down), None where it printed "—".
REVIEW_TABLE5: dict[tuple[str, int], tuple[tuple[float | None, float | None, int], ...]] = {
    ("Shortbow", 0): ((5.3, 4.0, 33), (5.3, 3.3, 17), (2.0, 0.0, 0), (1.0, 0.0, 0)),
    ("Shortbow", 1): ((8.0, 12.4, 72), (7.6, 12.1, 59), (6.2, 0.3, 0), (1.8, 0.0, 0)),
    ("Shortbow", 2): ((7.9, 22.7, 100), (8.1, 22.3, 95), (10.5, 2.3, 5), (3.3, 0.0, 0)),
    ("Shortbow", 3): ((None, None, 100), (None, None, 100), (12.2, 6.2, 41), (5.4, 0.0, 0)),
    ("Longbow", 0): ((6.0, 6.2, 25), (4.7, 5.8, 25), (3.2, 0.0, 0), (1.3, 0.0, 0)),
    ("Longbow", 1): ((7.1, 15.3, 88), (7.3, 14.9, 73), (7.7, 0.6, 0), (2.2, 0.0, 0)),
    ("Longbow", 2): ((None, None, 100), (None, None, 99), (11.0, 3.4, 16), (3.8, 0.0, 0)),
    ("Longbow", 3): ((None, None, 100), (None, None, 100), (12.3, 7.7, 50), (6.1, 0.0, 0)),
}

ROLLS = 4000  # Table 5's sample size per cell


@dataclass(frozen=True)
class Check:
    cell: Cell5
    printed: tuple[float | None, float | None, int]
    ok: tuple[bool, bool, bool]


def _close(exact: Fraction, var: Fraction, printed: float, half_unit: float) -> bool:
    se = sqrt(float(var) / ROLLS)
    return abs(float(exact) - printed) <= half_unit + 3 * se + 1e-9


def check_table5(rules: RuleSet) -> list[Check]:
    cells = table5(rules)
    out = []
    for c in cells:
        defenders = [d.label for d in table5_defenders(rules)]
        printed = REVIEW_TABLE5[(c.bow, c.aims)][defenders.index(c.defender)]
        st, inj, down = printed
        r = c.response
        p = float(r.p_down)
        ok = (
            st is None or _close(r.stamina, r.var_stamina, st, 0.05),
            inj is None or _close(r.injury, r.var_injury, inj, 0.05),
            abs(100 * p - down) <= 0.5 + 300 * sqrt(p * (1 - p) / ROLLS) + 1e-9,
        )
        out.append(Check(c, printed, ok))
    return out


def render_table5(rules: RuleSet, against_review: bool = True) -> str:
    """Table 5's layout: target spends / takes / downed, exactly; with the review's printed
    figures beside each cell (a check mark where they agree within sampling error)."""
    labels = [d.label for d in table5_defenders(rules)]
    lines = [
        "| Shot | " + " | ".join(labels) + " |",
        "|---" * (len(labels) + 1) + "|",
    ]
    checks = check_table5(rules) if against_review else None
    cells = table5(rules)
    for k in range(0, len(cells), len(labels)):
        row = cells[k : k + len(labels)]
        head = f"{row[0].bow}, {row[0].aims} aim ({row[0].cost} st)"
        parts = []
        for j, c in enumerate(row):
            r = c.response
            text = f"{float(r.stamina):.1f} / {float(r.injury):.1f} / {100 * float(r.p_down):.0f}%"
            if checks is not None:
                chk = checks[k + j]
                st, inj, down = chk.printed
                shown = f"{'—' if st is None else st} / {'—' if inj is None else inj} / {down}%"
                mark = "✓" if all(chk.ok) else "✗"
                text += f" (review {shown} {mark})"
            parts.append(text)
        lines.append(f"| {head} | " + " | ".join(parts) + " |")
    return "\n".join(lines)
