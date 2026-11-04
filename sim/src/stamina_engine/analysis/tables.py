"""The review's static tables, computed exactly (review Appendix A, Tables 1 and 8)."""

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from enum import Enum
from fractions import Fraction

from stamina_engine.analysis import dist
from stamina_engine.core.mathx import round_half_even, round_half_up
from stamina_engine.model.build import Attributes, Build, Loadout, load_build
from stamina_engine.model.derive import WeaponProfile, derive
from stamina_engine.rules.block_solver import cheapest_zero_injury
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Blocking",
    "Packet: Melee Attacks",
    "Packet: Weapon Table",
    "Review F1",
    "Review F8",
)


class Rounding(Enum):
    """How a fractional mean becomes a whole roll or a printed figure (Assumptions register:
    analysis.mean_rounding). The review's simulator used Python's round(): half to even."""

    HALF_UP = "half-up"
    HALF_EVEN = "half-even"

    def to_int(self, x: Fraction) -> int:
        return round_half_up(x) if self is Rounding.HALF_UP else round_half_even(x)

    def fixed(self, x: Fraction, places: int = 2) -> str:
        mode = ROUND_HALF_UP if self is Rounding.HALF_UP else ROUND_HALF_EVEN
        exact = Decimal(x.numerator) / Decimal(x.denominator)
        return str(exact.quantize(Decimal(1).scaleb(-places), rounding=mode))


def _weapon(build: str, rules: RuleSet) -> tuple[WeaponProfile, int, int]:
    lo = derive(load_build(build), rules).main
    assert lo.weapon is not None
    return lo.weapon, lo.melee_defense, lo.armor


def mean_per_step(weapon: WeaponProfile, rules: RuleSet) -> Fraction:
    return dist.mean(dist.step(weapon.damage, weapon.crit_widen, rules.crit))


@dataclass(frozen=True)
class Table1Row:
    label: str
    defense: int
    armor: int
    per_step: Fraction
    costs: tuple[int | None, ...]  # cheapest zero-injury block for k = 1, 2, ...


@dataclass(frozen=True)
class Table1:
    attack_costs: tuple[int, ...]
    rows: tuple[Table1Row, ...]


TABLE1_DEFENDERS = ((2, 0), (2, 2), (3, 2), (4, 2), (4, 3), (5, 2))


def table1(rules: RuleSet, rounding: Rounding) -> Table1:
    """Stamina to fully block a longsword attack at its mean roll (no crit) vs attack cost.

    L1 rows: the sample fighter's longsword against each defense. L30 and L99 rows: the
    sample build against an identical defender (MD 6, armor 2), L99 out to k = 7.
    """
    pricing = Pricing(rules)

    def row(label: str, weapon: WeaponProfile, md: int, armor: int, ks: int) -> Table1Row:
        per_step = mean_per_step(weapon, rules)
        costs = []
        for k in range(1, ks + 1):
            choice = cheapest_zero_injury(rounding.to_int(per_step * k), 0, md, armor, rules)
            costs.append(choice.cost if choice else None)
        return Table1Row(label, md, armor, per_step, tuple(costs))

    l1, _, _ = _weapon("l1_sample", rules)
    rows = [row(f"MD {md}, armor {a}", l1, md, a, 5) for md, a in TABLE1_DEFENDERS]
    for build, level, ks in (("l30_sample", "L30 sample", 5), ("l99_sample", "L99", 7)):
        w, md, a = _weapon(build, rules)
        label = f"MD {md}, armor {a} ({level}, {_num(mean_per_step(w, rules))}/step)"
        rows.append(row(label, w, md, a, ks))
    costs = tuple(pricing.melee_attack(l1.base, k).total for k in range(1, 6))
    return Table1(costs, tuple(rows))


@dataclass(frozen=True)
class Table8Row:
    label: str
    base: int
    per_step: Fraction
    ratios: tuple[Fraction, ...]  # mean damage / stamina for k = 1..5


TABLE8_WEAPONS = (
    ("Dagger", "dagger", "one"),
    ("Shortsword", "shortsword", "one"),
    ("Longsword 1H", "longsword", "one"),
    ("Longsword 2H", "longsword", "two"),
    ("Greatsword", "greatsword", "two"),
    ("Greataxe", "greataxe", "two"),
)


def table8(rules: RuleSet) -> tuple[Table8Row, ...]:
    """Mean damage per stamina by commitment for STR 2, AGI 1, FIN 1."""
    pricing = Pricing(rules)
    rows = []
    for label, weapon, grip in TABLE8_WEAPONS:
        build = Build(
            "table8",
            1,
            Attributes(STR=2, AGI=1, FIN=1),
            (("m", Loadout(weapon=weapon, grip=grip)),),
            ("fighter",),
        )
        w = derive(build, rules).main.weapon
        assert w is not None
        per_step = mean_per_step(w, rules)
        ratios = tuple(per_step * k / pricing.melee_attack(w.base, k).total for k in range(1, 6))
        rows.append(Table8Row(f"{label} {w.damage} (base {w.base})", w.base, per_step, ratios))
    return tuple(rows)


def _num(x: Fraction) -> str:
    return str(x.numerator) if x.denominator == 1 else str(float(x))


def render_table1(t: Table1, rounding: Rounding) -> str:
    ks = max(len(r.costs) for r in t.rows)
    head = [f"k={k} (att {c})" for k, c in enumerate(t.attack_costs, 1)]
    head += [f"k={k}" for k in range(len(t.attack_costs) + 1, ks + 1)]
    lines = [
        "Table 1: stamina to fully block a longsword attack at its mean roll (no crit)",
        f"Mean roll rounded {rounding.value}",
        "",
        "| Defender | " + " | ".join(head) + " |",
        "|---" * (ks + 1) + "|",
    ]
    for r in t.rows:
        cells = ["—" if c is None else str(c) for c in r.costs]
        cells += [""] * (ks - len(cells))
        lines.append(f"| {r.label} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render_table8(rows: tuple[Table8Row, ...], rounding: Rounding) -> str:
    lines = [
        "Table 8: damage per stamina by commitment (STR 2, FIN 1, AGI 1)",
        f"Figures rounded {rounding.value}",
        "",
        "| Weapon | k=1 | k=2 | k=3 | k=4 | k=5 |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r.label} | " + " | ".join(rounding.fixed(x) for x in r.ratios) + " |")
    return "\n".join(lines)
