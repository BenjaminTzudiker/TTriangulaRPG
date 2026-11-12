"""Parity with the design study's exact ranged solver (tests/solver/bows5.py; simulator
requirements R7.1-R7.3 and R7.5): shot distributions, injury, costs and one round of
shooting, for the packet's bows under crit rules A (0.10.0), B, C' and C.

The solver's bows are written here as the engine's v0_10 bows: shot cost, damage die,
Strength or Finesse in the total, band width, Piercing, and Precise's limit (cap_mod 0 and
cap_floor = Finesse). Its free aim die and -2 per band are 0.10.0's. The slow marks run the
full grids the requirements list; the fast tests sample them.
"""

import itertools
from collections import Counter, defaultdict
from dataclasses import replace
from fractions import Fraction
from typing import Any

import pytest

from stamina_engine.analysis.one_round import Archer, Target, solve_round
from stamina_engine.analysis.ranged import shot
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.model.build import Loadout, load_build
from stamina_engine.model.derive import WeaponProfile, derive
from stamina_engine.rules.exchange import Blocks, resolve, roll_shot
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.ruleset import RuleSet, preset

V10 = preset("v0.10.0")
CRIT_RULES: dict[str, tuple[RuleSet, dict[str, Any]]] = {
    "A": (V10, {"crit_mode": "bow_w"}),
    "B": (V10.with_(crit=replace(V10.crit, aim_dice_can_crit=True)), {"crit_mode": "all"}),
    "C'": (preset("v0.10.0-crit-c-prime"), {"crit_mode": "all", "aim_widen": 0, "crit_cap": 1}),
    "C": (preset("v0.10.0-crit-c"), {"crit_mode": "all", "crit_cap": 1}),
}
# (bow, Strength, Finesse): the packet's four bows at their Strength, across Finesse.
BOWS = [
    ("shortbow", 0, 0),
    ("shortbow", 0, 3),
    ("shortbow", 0, 5),
    ("longbow", 1, 1),
    ("longbow", 3, 2),
    ("warbow", 3, 1),
    ("superheavy_warbow", 5, 3),
]
BOW_IDS = [f"{n}-s{s}f{f}" for n, s, f in BOWS]


def weapon(name: str, strength: int, finesse: int, rules: RuleSet = V10) -> WeaponProfile:
    b = load_build("l1_archer")
    b = replace(
        b,
        attributes=replace(b.attributes, STR=strength, FIN=finesse),
        loadouts=(("bow", Loadout(armor="light", weapon=name, grip="two")),),
        budget="ignore",
    )
    w = derive(b, rules).main.weapon
    assert w is not None
    return w


def solver_bow(solver: Any, w: WeaponProfile, finesse: int, crit: dict[str, Any]) -> Any:
    (dice,) = w.damage.dice
    kw: dict[str, Any] = dict(
        per_band=2, free_aims=1, widen=w.crit_widen, pierce=w.piercing, **crit
    )
    if w.precise:
        kw.update(cap_mod=0, cap_floor=finesse)
    return solver.Bow(w.name, dice.size, w.damage.flat, w.base, w.band_width, **kw)


def solver_penalty(b: Any, distance: int) -> int:
    """bows5.solve's range penalty, as it computes `pens`."""
    return b.per_band * max(0, (distance - 1) // b.band) if distance > 0 else 0


def engine_shot(
    w: WeaponProfile, aims: int, finesse: int, distance: int, rules: RuleSet
) -> dict[tuple[int, int, int], float]:
    r = rules.ranged
    joint = shot(
        w,
        aims,
        finesse,
        r.band(distance, w.ranges, w.band_width),
        rules,
        r.range_penalty(distance, w.band_width),
    )
    out: dict[tuple[int, int, int], float] = defaultdict(float)
    for (t, c, limit), p in joint.items():
        assert limit is not None
        out[(t, c if t > 0 else 0, limit)] += float(p)  # a total of 0 has no crits to count
    return dict(out)


def solver_shot(solver: Any, b: Any, aims: int, distance: int) -> dict[tuple[int, int, int], float]:
    return {
        (t, c, cap): p for p, t, c, cap in solver.shot_dist(b, aims, solver_penalty(b, distance))
    }


def same(a: dict[Any, float], b: dict[Any, float]) -> bool:
    keys = {k for k in a.keys() | b.keys() if a.get(k, 0) > 1e-15 or b.get(k, 0) > 1e-15}
    return all(abs(a.get(k, 0.0) - b.get(k, 0.0)) < 1e-12 for k in keys)


# --- R7.1: the shot distribution ------------------------------------------------------


def test_range_penalty(bows_solver: Any) -> None:
    for width in range(1, 9):
        b = bows_solver.Bow("x", 8, 0, 4, width, per_band=2)
        got = [V10.ranged.range_penalty(d, width) for d in range(41)]
        assert got == [solver_penalty(b, d) for d in range(41)]


def _check_shots(solver: Any, aims_range: range, distances: list[int]) -> None:
    for (name, s, f), (crit, (rules, kw)) in itertools.product(BOWS, CRIT_RULES.items()):
        w = weapon(name, s, f, rules)
        b = solver_bow(solver, w, f, kw)
        for aims, d in itertools.product(aims_range, distances):
            eng = engine_shot(w, aims, f, d, rules)
            assert same(eng, solver_shot(solver, b, aims, d)), (name, s, f, crit, aims, d)


def test_shot_distribution(bows_solver: Any) -> None:
    _check_shots(bows_solver, range(0, 4), [0, 3, 9, 25])


@pytest.mark.slow
def test_shot_distribution_full(bows_solver: Any) -> None:
    """R7.1's grid: aims 0-6, distance 0-40."""
    _check_shots(bows_solver, range(0, 7), list(range(41)))


def _enumerate(w: WeaponProfile, aims: int, finesse: int, rules: RuleSet) -> dict[Any, Fraction]:
    size = w.damage.dice[0].size
    out: Counter[tuple[int, int, int | None]] = Counter()
    for faces in itertools.product(range(1, size + 1), *[range(1, 7)] * (1 + aims)):
        a = roll_shot(w, aims, finesse, "band 1", rules, ScriptedDice(list(faces)))
        out[(a.total, a.crit_dice, a.limit)] += 1
    n = sum(out.values())
    return {k: Fraction(v, n) for k, v in out.items()}


@pytest.mark.parametrize("crit", list(CRIT_RULES))
def test_the_roller_matches_the_exact_shot(crit: str) -> None:
    """exchange.roll_shot rolls what analysis.ranged.shot computes, under every crit rule."""
    rules = CRIT_RULES[crit][0]
    for name, s, f in (("longbow", 1, 3), ("shortbow", 0, 5)):
        w = weapon(name, s, f, rules)
        for aims in range(3):
            assert shot(w, aims, f, "band 1", rules) == _enumerate(w, aims, f, rules)


# --- R7.2: injury ---------------------------------------------------------------------


def _check_injury(solver: Any, totals: range, blocks: range, caps: tuple[int, ...]) -> None:
    for inside in (False, True):
        rules = V10.with_(ranged=replace(V10.ranged, crit_in_limit=inside))
        solver.INCAP[0] = inside
        for total, crits, d, armor, pierce, cap in itertools.product(
            totals, range(4), range(1, 6), range(5), range(3), caps
        ):
            faced = max(0, armor - pierce)
            for p, g in itertools.product(blocks, blocks):
                want = solver.injury(total, crits, d, faced, p, g, cap)
                got = resolve(total, crits, d, faced, Blocks(p, g), rules, cap).injury
                assert got == want, (inside, total, crits, d, armor, pierce, cap, p, g)


def test_injury(bows_solver: Any) -> None:
    _check_injury(bows_solver, range(0, 41, 6), range(0, 9, 3), (0, 3, 8))


@pytest.mark.slow
def test_injury_full(bows_solver: Any) -> None:
    """R7.2's grid: totals 0-40, crit dice 0-3, D 1-5, armor 0-4, Piercing 0-2, perfect and
    grazing blocks 0-8, both crit_in_limit settings; wound caps 0-13."""
    _check_injury(bows_solver, range(41), range(9), tuple(range(14)))


# --- R7.3: costs ----------------------------------------------------------------------


def solver_cost(draw: int, aims: int, k: int) -> tuple[int, int]:
    """bows5.solve's price of a shot with `aims` aim steps after k actions (draw_action,
    no aim reset), and the action count after it."""
    kk, cost = k, draw + k
    kk += 1
    for _ in range(aims):
        cost += 1 + kk
        kk += 1
    return cost, kk


def test_costs() -> None:
    pricing = Pricing(V10)
    for draw, k, aims in itertools.product((3, 4, 6, 8), range(4), range(7)):
        q = pricing.ranged_attack(draw, aims, Trackers(actions_this_turn=k))
        after = q.after(Trackers(actions_this_turn=k)).actions_this_turn
        assert (q.total, after) == solver_cost(draw, aims, k)


def test_cost_sequences() -> None:
    """Two and three shots in a row: the count carries across shots, free aim dice add none."""
    pricing = Pricing(V10)
    for seq in itertools.product(range(4), repeat=3):
        t, k, total, want = Trackers(), 0, 0, 0
        for aims in seq:
            q = pricing.ranged_attack(4, aims, t)
            t = q.after(t)
            total += q.total
            cost, k = solver_cost(4, aims, k)
            want += cost
        assert (total, t.actions_this_turn) == (want, k)


# --- R7.5: one round ------------------------------------------------------------------

# (Tgt, Target): the study's targets.
TARGETS = [
    ("caster D2", dict(D=2), Target(2, 0, 8, 14)),
    ("caster D3", dict(D=3), Target(3, 0, 8, 14)),
    ("mail D2 A2", dict(D=2, armor=2, hp=10, st=16), Target(2, 2, 10, 16)),
    ("plate D2 A3", dict(D=2, armor=3, hp=12, st=18), Target(2, 3, 12, 18)),
]


# A Finesse-5 shortbow downs the caster whether or not it aims, so the aim count is a tie
# the solver's floating-point noise breaks either way; every other figure still matches.
TIED_AIMS = ([("shortbow", 0, 5)], 0)


def _compare_round(
    solver: Any, bows: list[tuple[str, int, int]], crit: str, target: int, distance: int
) -> None:
    rules, kw = CRIT_RULES[crit]
    archers, sb = [], []
    for name, s, f in bows:
        w = weapon(name, s, f, rules)
        archers.append(Archer(w, f, 14))
        sb.append(solver_bow(solver, w, f, kw))
    _, tkw, t = TARGETS[target]
    want = solver.solve(tuple(sb), solver.Tgt(**tkw), distance)
    got = solve_round(archers, t, rules, distance)
    pairs = [
        (got.value, want["U"]),
        (got.p_down, want["P_down"]),
        (got.hp_lost, want["HP"]),
        (got.stamina_spent, want["St"]),
        (got.shots, want["shots"]),
    ]
    if (bows, target) != TIED_AIMS:
        pairs.append((got.aims, want["aims"]))
    assert all(abs(a - b) < 1e-9 for a, b in pairs), (bows, crit, target, distance, pairs)


@pytest.mark.parametrize(
    ("bow", "target", "distance"),
    [
        (("shortbow", 0, 3), 0, 0),
        (("shortbow", 0, 3), 3, 0),
        (("longbow", 1, 1), 0, 8),
        (("warbow", 3, 1), 2, 0),
        (("superheavy_warbow", 5, 3), 3, 10),
    ],
)
def test_one_round_single_archer(
    bows_solver: Any, bow: tuple[str, int, int], target: int, distance: int
) -> None:
    _compare_round(bows_solver, [bow], "A", target, distance)


@pytest.mark.parametrize("crit", ["B", "C'", "C"])
def test_one_round_crit_rules(bows_solver: Any, crit: str) -> None:
    _compare_round(bows_solver, [("longbow", 1, 1)], crit, 0, 0)


def test_one_round_focus_fire(bows_solver: Any) -> None:
    """Two archers in a row: the target's stamina carries from one to the next."""
    _compare_round(bows_solver, [("longbow", 1, 1)] * 2, "A", 2, 0)


@pytest.mark.slow
@pytest.mark.parametrize("crit", list(CRIT_RULES))
def test_one_round_full(bows_solver: Any, crit: str) -> None:
    for bow, target, distance in itertools.product(BOWS, range(len(TARGETS)), (0, 4, 10)):
        _compare_round(bows_solver, [bow], crit, target, distance)


def test_reference_numbers() -> None:
    """R7.5: one archer, point blank, rule A (0.10.0), 14 stamina. Longbow 1d8+1 (FIN 1)
    against a caster (D2, HP 8): 38% down, 6.2 HP (i1.txt). Warbow 1d10+3 (FIN 1, Piercing
    1) against plate (D2, armor 3, HP 12): 4% down, 4.2 HP (h.txt)."""
    lb = solve_round([Archer(weapon("longbow", 1, 1), 1, 14)], TARGETS[0][2], V10)
    assert (round(100 * lb.p_down), round(lb.hp_lost, 1)) == (38, 6.2)
    wb = solve_round([Archer(weapon("warbow", 3, 1), 1, 14)], TARGETS[3][2], V10)
    assert (round(100 * wb.p_down), round(wb.hp_lost, 1)) == (4, 4.2)
