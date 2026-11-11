"""Packet 0.10.0, the ranged package (rules/CHANGELOG.md), from the notes' own numbers: the
aimed longbow, range penalty, Precise and diving examples, the Sample Character, Piercing,
the reaction to a shot and the point-blank opportunity attacks. The bows and shield are the
v0_10 equipment table's."""

import itertools
from collections import Counter
from dataclasses import replace
from fractions import Fraction
from pathlib import Path

import pytest

from stamina_engine.agents.decisions import (
    BlocksRequest,
    DiveRequest,
    Move,
    OATake,
    Shoot,
    TakeOA,
    TurnCommand,
)
from stamina_engine.agents.listed import Listed
from stamina_engine.analysis.ranged import shot
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.core.errors import ConfigError
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import (
    AttackRolled,
    Injured,
    OpportunityProvoked,
    RangePenalized,
    Spent,
    log_lines,
)
from stamina_engine.experiments.runner import run_trial
from stamina_engine.experiments.scenario import load_scenario
from stamina_engine.grid.battlefield import Battlefield, Cell, parse_map
from stamina_engine.model.build import Build, Loadout, load_build
from stamina_engine.model.derive import CombatProfile, WeaponProfile, derive, equipment_for
from stamina_engine.model.equipment import load_table
from stamina_engine.rules.exchange import Blocks, resolve, roll_shot
from stamina_engine.rules.pricing import FRESH, Pricing
from stamina_engine.rules.ruleset import preset

V10 = preset("v0.10.0")
TABLE = load_table("v0_10")
WIDE = parse_map("\n".join(["." * 30] * 5))
SCENARIOS = Path(__file__).resolve().parents[2] / "src/stamina_engine/data/scenarios"


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources[name]


def archer(**attrs: int) -> Build:
    """The library archer (STR 1, AGI 1, FIN 2, longbow), with other attributes or bow."""
    b = load_build("l1_archer")
    bow = str(attrs.pop("bow", "longbow"))
    return replace(
        b,
        name=f"archer_{bow}",
        attributes=replace(b.attributes, **attrs),
        loadouts=(("bow", Loadout(armor="light", weapon=bow, grip="two")),),
        budget="ignore",
    )


def profile(build: Build) -> CombatProfile:
    return derive(build, V10, TABLE)


def bow(build: Build) -> WeaponProfile:
    w = profile(build).main.weapon
    assert w is not None
    return w


def sample() -> CombatProfile:
    return profile(load_build("l1_sample"))


def fight(
    roster: list[tuple[str, str, CombatProfile, Cell, Listed]],
    attacks: dict[str, list[int]] | None = None,
    field: Battlefield = WIDE,
) -> BattleResult:
    faces = {"initiative": [12, 12] + [1, 1] * (len(roster) - 1), "dying": [6] * 10}
    faces.update({f"attack:{k}": v for k, v in (attacks or {}).items()})
    entrants = [Entrant(cid, team, p, a, "", pos) for cid, team, p, pos, a in roster]
    return Battle(V10, entrants, Dice(faces), seed=0, round_cap=1, check=True, field=field).run()


def of(agent: Listed, kind: type) -> list:
    return [r for r in agent.requests if isinstance(r, kind)]


def spent(result: BattleResult, who: str, category: str) -> list[int]:
    return [
        e.amount
        for e in result.log
        if isinstance(e, Spent) and e.who == who and e.category == category
    ]


# --- costs, aim and the aim limit ------------------------------------------------------


def test_two_aimed_longbow_shots() -> None:
    """Packet: Aim, Example. Shot cost 4: 4 + 2, then 6 + 4: 16 stamina."""
    p = Pricing(V10)
    first = p.ranged_attack(4, 1)
    second = p.ranged_attack(4, 1, first.after(FRESH))
    assert first.parts == (4, 2) and second.parts == (6, 4)
    assert first.total + second.total == 16
    assert first.after(FRESH).actions_this_turn == 2  # the shot and its aim step


def test_the_aim_limit_example() -> None:
    """The first shot rolls 3 on the d8, 5 and 6 on the aim dice: 3 + 1 + 5 + 6 = 15. Three
    perfect blocks at Ranged Defense 2 leave 9; the damage roll was 3 + 1, so 4 HP."""
    w = bow(archer(FIN=0))
    a = roll_shot(w, 1, 0, "band 1", V10, ScriptedDice([3, 5, 6]))
    assert (a.total, a.crit_dice, a.limit) == (15, 0, 4)
    out = resolve(a.total, a.crit_dice, 2, 0, Blocks(3, 0), V10, a.limit)
    assert (out.through_blocks, out.injury) == (9, 4)


def test_aim_dice_add_no_finesse_and_never_crit() -> None:
    w = bow(archer(FIN=5))
    a = roll_shot(w, 2, 5, "band 1", V10, ScriptedDice([1, 6, 6, 6]))
    assert a.total == 1 + 1 + 18 and a.crit_dice == 0


def test_critical_bonus_comes_after_the_limit() -> None:
    """Packet: Aim. The limit applies after armor and before the critical bonus."""
    out = resolve(20, 1, 2, 0, Blocks(1, 0), V10, limit=8)
    assert out.injury == 8 + 1


def test_a_precise_shot() -> None:
    """Packet: Weapon Properties, Example. Finesse 4, d4 rolls 1 (no crit: 2-4), aim die 3:
    8. Blocking 4 leaves 4, and the limit is the higher of 1 and Finesse 4: 4 HP. Blocking 6
    leaves 2: 2 HP."""
    w = bow(archer(FIN=4, bow="shortbow"))
    assert [f for f in range(1, 5) if V10.crit.is_crit(f, 4, w.crit_widen)] == [2, 3, 4]
    a = roll_shot(w, 0, 4, "band 1", V10, ScriptedDice([1, 3]))
    assert (a.total, a.crit_dice, a.limit) == (8, 0, 4)
    assert resolve(8, 0, 4, 0, Blocks(1, 0), V10, a.limit).injury == 4
    assert resolve(8, 0, 6, 0, Blocks(1, 0), V10, a.limit).injury == 2


def _enumerate(rules_build: Build, aims: int) -> dict[tuple[int, int, int | None], Fraction]:
    w = bow(rules_build)
    fin = profile(rules_build).main.attributes.FIN
    size = w.damage.dice[0].size
    out: Counter[tuple[int, int, int | None]] = Counter()
    for faces in itertools.product(range(1, size + 1), *[range(1, 7)] * (1 + aims)):
        a = roll_shot(w, aims, fin, "band 1", V10, ScriptedDice(list(faces)))
        out[(a.total, a.crit_dice, a.limit)] += 1
    n = sum(out.values())
    return {k: Fraction(v, n) for k, v in out.items()}


@pytest.mark.parametrize("aims", [0, 1, 2])
@pytest.mark.parametrize(
    "build",
    [archer(), archer(FIN=4, bow="shortbow"), archer(STR=3, bow="warbow")],
    ids=["longbow", "shortbow", "warbow"],
)
def test_exact_shot_matches_the_roller(build: Build, aims: int) -> None:
    """analysis.ranged.shot gives the roller's (total, crit dice, aim limit) exactly."""
    w = bow(build)
    fin = profile(build).main.attributes.FIN
    assert shot(w, aims, fin, "band 1", V10) == _enumerate(build, aims)


# --- range bands ----------------------------------------------------------------------


def test_range_penalty_example() -> None:
    """Packet: Range Bands, Example. Longbow at Finesse 1: band width 3 + 1 = 4. 10 squares is
    the third band: -4."""
    r = V10.ranged
    assert bow(archer(FIN=1)).band_width == 4
    assert [r.range_penalty(d, 4) for d in (1, 4, 5, 8, 9, 10, 12, 13, 40)] == [
        0, 0, 2, 2, 4, 4, 4, 6, 18,
    ]  # fmt: skip
    assert r.band(10, (), 4) == "band 3"


def test_band_width_and_strength() -> None:
    """Band width: the weapon's, +1 per odd Finesse, -1 per point of Strength short; at 0 or
    less you can't shoot it."""
    assert bow(archer(FIN=0, STR=1)).band_width == 3
    assert bow(archer(FIN=5, STR=1)).band_width == 6
    assert bow(archer(FIN=0, STR=1, bow="warbow")).band_width == 2
    heavy = archer(FIN=0, STR=0, bow="superheavy_warbow")
    assert bow(heavy).band_width == 0
    a = Listed()
    fight([("A", "red", profile(heavy), (0, 2), a), ("T", "blue", sample(), (3, 2), Listed())])
    assert of(a, TurnCommand)[0].shots == ()


def test_no_maximum_range() -> None:
    a = Listed()
    fight([("A", "red", profile(archer()), (0, 2), a), ("T", "blue", sample(), (29, 2), Listed())])
    assert of(a, TurnCommand)[0].shots == ("T",)


def test_the_bows_need_their_table() -> None:
    """Each RuleSet's range bands pick the packet's table by default; mixing them is refused."""
    assert equipment_for(V10) == "v0_10" and equipment_for(preset("v0.9.3")) == "v0_9"
    assert derive(load_build("l1_archer"), V10).main.weapon == bow(archer())
    with pytest.raises(ConfigError, match="band width"):
        derive(load_build("l1_archer"), V10, load_table("v0_9"))
    with pytest.raises(ConfigError, match="ranges"):
        derive(load_build("l1_archer"), preset("v0.9.3"), TABLE)


# --- defenses, cover and Piercing -----------------------------------------------------


def test_sample_character() -> None:
    """Packet: Quick Reference, Sample Character (0.10.0): Melee Defense 3, Ranged Defense 2,
    HP 10, stamina 16."""
    p = sample()
    assert (p.hp_max, p.stamina_max) == (10, 16)
    assert (p.main.melee_defense, p.main.ranged_defense, p.main.dodge_defense) == (3, 2, 1)


def test_ranged_defense_from_even_agility() -> None:
    """+1 per even Agility value, at medium armor's step (every 3rd point)."""
    assert profile(archer(AGI=2)).main.ranged_defense == 2
    medium = replace(
        archer(AGI=3, STR=1),
        loadouts=(("bow", Loadout(armor="medium", weapon="longbow", grip="two")),),
    )
    assert profile(medium).main.ranged_defense == 2


def test_cover_values() -> None:
    assert [V10.ranged.cover_bonus(level) for level in (0, 1, 2)] == [0, 1, 2]


def test_diving_for_cover_example() -> None:
    """Packet: Cover, Example. Diving behind a wall counts as three-quarters (+2), and moving
    in reaction to the shot adds +1: Ranged Defense 3 higher."""
    walled = parse_map("\n".join([".....#..", ".....#..", ".....#..", "........", "........"]))
    t = Listed(dives=[Move(((6, 3), (6, 2)))])
    a = Listed(turns=[Shoot("T")])
    fight(
        [("A", "red", profile(archer()), (0, 1), a), ("T", "blue", sample(), (6, 4), t)],
        attacks={"A": [1, 1]},
        field=walled,
    )
    (blocks,) = of(t, BlocksRequest)
    assert (blocks.cover, blocks.defense) == (2, 2 + 3)


def test_piercing_and_critical_dice() -> None:
    """A warbow (Piercing 1) against medium armor 2: the target blocks knowing it faces armor
    1, and a critical die takes off the last point."""
    t = Listed(block_answers=[Blocks()])
    result = fight(
        [
            ("A", "red", profile(archer(STR=3, bow="warbow")), (0, 2), Listed(turns=[Shoot("T")])),
            ("T", "blue", sample(), (3, 2), t),
        ],
        attacks={"A": [10, 1]},  # 10 crits at Finesse 2
    )
    (blocks,) = of(t, BlocksRequest)
    assert (blocks.armor, blocks.crit_dice, blocks.limit) == (1, 1, 13)
    (rolled,) = [e for e in result.log if isinstance(e, AttackRolled)]
    assert rolled.total == 10 + 3 + 1
    (hurt,) = [e for e in result.log if isinstance(e, Injured) and e.who == "T"]
    assert hurt.damage == 13 + 1  # capped at the damage roll 10 + 3, then +1


# --- the reaction to a shot -----------------------------------------------------------


def test_backing_away_is_measured_after_the_reaction() -> None:
    """At 4 squares (band 1) the target backs away to 6 (band 2): -2, and +1 Ranged Defense
    for moving. The request said both before it moved."""
    t = Listed(dives=[Move(((5, 2), (6, 2)))])
    result = fight(
        [
            ("A", "red", profile(archer()), (0, 2), Listed(turns=[Shoot("T")])),
            ("T", "blue", sample(), (4, 2), t),
        ],
        attacks={"A": [4, 6]},
    )
    (dive,) = of(t, DiveRequest)
    assert (dive.damage, dive.defense, dive.armor, dive.limit) == (11, 2, 2, 5)
    assert (dive.damage_after[(6, 2)], dive.defense_after[(6, 2)]) == (9, 3)
    (pen,) = [e for e in result.log if isinstance(e, RangePenalized)]
    assert (pen.distance, pen.band, pen.penalty) == (6, "band 2", 2)
    (blocks,) = of(t, BlocksRequest)
    assert (blocks.damage, blocks.defense) == (9, 3)
    assert spent(result, "A", "shot") == [4]


def test_closing_in_blocks_with_melee_defense_and_doesnt_provoke() -> None:
    """The target closes from 3 squares into reach: it blocks with Melee Defense (the +1 for
    moving is Ranged Defense's), and it gets no opportunity attack: it wasn't in reach when
    the shot was declared."""
    t = Listed(dives=[Move(((2, 2), (1, 2)))], oas=[OATake("main", 1)])
    result = fight(
        [
            ("A", "red", profile(archer()), (0, 2), Listed(turns=[Shoot("T")])),
            ("T", "blue", sample(), (3, 2), t),
        ],
        attacks={"A": [1, 1], "T": [1]},
    )
    (blocks,) = of(t, BlocksRequest)
    assert blocks.defense == 3  # the sample fighter's Melee Defense
    assert not [e for e in result.log if isinstance(e, OpportunityProvoked) and e.mover == "A"]
    assert not of(t, TakeOA)


def test_backing_out_of_reach_loses_the_opportunity_attack() -> None:
    t = Listed(dives=[Move(((4, 2), (5, 2)))], oas=[OATake("main", 1)])
    result = fight(
        [
            ("A", "red", profile(archer()), (2, 2), Listed(turns=[Shoot("T")])),
            ("T", "blue", sample(), (3, 2), t),
        ],
        attacks={"A": [1, 1], "T": [1]},
    )
    assert not [e for e in result.log if isinstance(e, OpportunityProvoked) and e.mover == "A"]
    (blocks,) = of(t, BlocksRequest)
    assert blocks.defense == 2 + 1  # Ranged Defense, +1 for moving


def test_staying_in_reach_keeps_the_opportunity_attack() -> None:
    t = Listed(oas=[OATake("main", 1)])
    result = fight(
        [
            ("A", "red", profile(archer()), (2, 2), Listed(turns=[Shoot("T")])),
            ("T", "blue", sample(), (3, 2), t),
        ],
        attacks={"A": [1, 1], "T": [1]},
    )
    provoked = [e for e in result.log if isinstance(e, OpportunityProvoked) and e.mover == "A"]
    assert provoked and provoked[0].enemies == ("T",)
    (blocks,) = of(t, BlocksRequest)
    assert blocks.defense == 3  # point blank: Melee Defense, no reaction bonus
    assert of(t, TakeOA)


# --- whole fights ---------------------------------------------------------------------


def test_tactical_archer_fight_runs_and_repeats() -> None:
    """The archer-open scenario under 0.10.0 with its table: tactical agents play it, the
    invariant checks pass, and the same trial gives the same log."""
    s = replace(
        load_scenario(SCENARIOS / "archer_open.toml"), rules=V10, equipment="v0_10", trials=4
    )
    for trial in range(4):
        first = log_lines(run_trial(s, trial, check=True).log)
        assert first == log_lines(run_trial(s, trial, check=True).log)
    assert any('"RangePenalized"' in line for line in first)
