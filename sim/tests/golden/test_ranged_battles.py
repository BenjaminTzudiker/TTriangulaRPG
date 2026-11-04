"""Ranged attacks played as battles (Packet: Ranged Attacks, Aim, Range Bands, Cover, Drawing
Weapons; Opportunity Attacks: shooting in melee). Readings in the Assumptions register."""

from dataclasses import replace

from stamina_engine.agents.decisions import (
    AimRequest,
    AvoidOA,
    BlocksRequest,
    DiveRequest,
    Draw,
    EndTurn,
    Move,
    OATake,
    OffTurnMove,
    Shoot,
    TakeOA,
    TurnCommand,
)
from stamina_engine.agents.listed import Listed
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import (
    AttackRolled,
    Dived,
    Drew,
    OpportunityProvoked,
    ShotDeclared,
    ShotMissed,
    Spent,
)
from stamina_engine.grid.battlefield import Battlefield, Cell, parse_map
from stamina_engine.model.build import Loadout, load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import preset

RULES = preset("v0.9")
WIDE = parse_map("\n".join(["." * 30] * 5))


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources[name]


def archer() -> CombatProfile:
    return derive(load_build("l1_archer"), RULES)


def sample() -> CombatProfile:
    return derive(load_build("l1_sample"), RULES)


def fight(
    roster: list[tuple[str, str, CombatProfile, Cell, Listed]],
    attacks: dict[str, list[int]] | None = None,
    field: Battlefield = WIDE,
    rounds: int = 1,
) -> BattleResult:
    faces = {"initiative": [12, 12] + [1, 1] * (len(roster) - 1), "dying": [6] * 10}
    faces.update({f"attack:{k}": v for k, v in (attacks or {}).items()})
    entrants = [Entrant(cid, team, p, a, "", pos) for cid, team, p, pos, a in roster]
    return Battle(
        RULES, entrants, Dice(faces), seed=0, round_cap=rounds, check=True, field=field
    ).run()


def spent(result: BattleResult, who: str, category: str) -> list[int]:
    return [
        e.amount
        for e in result.log
        if isinstance(e, Spent) and e.who == who and e.category == category
    ]


def of(agent: Listed, kind: type) -> list:
    return [r for r in agent.requests if isinstance(r, kind)]


def test_two_aimed_longbow_shots() -> None:
    """5 + 1 + 2, then 5 + 3 + 4: 20 stamina (a level 99 archer, to afford both)."""
    a = Listed(turns=[Shoot("T"), Shoot("T")], aims=[2, 2])
    t = Listed(block_answers=[Blocks(3, 1), Blocks(3, 1)])
    veteran = replace(load_build("l1_archer"), name="archer99", level=99, budget="ignore")
    result = fight(
        [("A", "red", derive(veteran, RULES), (0, 2), a), ("T", "blue", sample(), (6, 2), t)],
        attacks={"A": [1, 1, 1, 1, 1, 1]},
    )
    assert spent(result, "A", "shot") == [8, 12]
    assert [e.band for e in result.log if isinstance(e, ShotDeclared)] == ["short", "short"]


def test_medium_and_long_range() -> None:
    """Medium: no aims misses; the first aim adds only Finesse (no die). Long: two."""
    for distance, aims, missed, faces in (
        (12, 0, True, 0),
        (12, 1, False, 1),
        (20, 1, True, 0),
        (20, 2, False, 1),
    ):
        a = Listed(turns=[Shoot("T")], aims=[aims])
        result = fight(
            [("A", "red", archer(), (0, 2), a), ("T", "blue", sample(), (distance, 2), Listed())],
            attacks={"A": [4]},
        )
        assert bool([e for e in result.log if isinstance(e, ShotMissed)]) is missed, (
            distance,
            aims,
        )
        rolled = [e for e in result.log if isinstance(e, AttackRolled)]
        if not missed:
            assert len(rolled[0].faces) == faces
            assert rolled[0].total == 4 + 3 + 2 * aims  # d8 + FIN + STR, + FIN per dropped aim
        (req,) = of(a, AimRequest)
        assert req.required == (1 if distance == 12 else 2)


def test_out_of_range_and_total_cover_are_not_targets() -> None:
    a = Listed()
    fight([("A", "red", archer(), (0, 2), a), ("T", "blue", sample(), (25, 2), Listed())])
    assert of(a, TurnCommand)[0].shots == ()
    walled = parse_map("\n".join(["...#....", "...#....", "...#...."]))
    a = Listed()
    fight(
        [("A", "red", archer(), (1, 1), a), ("T", "blue", sample(), (6, 1), Listed())], field=walled
    )
    assert of(a, TurnCommand)[0].shots == ()


def test_half_cover_adds_to_ranged_defense() -> None:
    pillar = parse_map("\n".join(["........", "....o...", "........"]))
    a = Listed(turns=[Shoot("T")])
    t = Listed()
    fight(
        [("A", "red", archer(), (0, 1), a), ("T", "blue", sample(), (7, 1), t)],
        attacks={"A": [1]},
        field=pillar,
    )
    (blocks,) = of(t, BlocksRequest)
    assert (blocks.defense, blocks.cover, blocks.ranged) == (3 + 2, 2, True)


def test_point_blank_uses_melee_defense_and_provokes() -> None:
    """Within the target's reach it blocks with Melee Defense; then every enemy threatening the
    shooter, the target included, may take an OA, which can't be paid off."""
    a = Listed(turns=[Shoot("T")])
    t = Listed(oas=[OATake("main", 1)])
    result = fight(
        [("A", "red", archer(), (2, 2), a), ("T", "blue", sample(), (3, 2), t)],
        attacks={"A": [1], "T": [1]},
    )
    (blocks,) = of(t, BlocksRequest)
    assert blocks.defense == 4  # the sample fighter's Melee Defense
    provoked = [e for e in result.log if isinstance(e, OpportunityProvoked)]
    assert provoked and provoked[0].mover == "A" and provoked[0].enemies == ("T",)
    assert of(t, TakeOA) and not of(a, AvoidOA)


def test_dive_behind_a_wall_counts_as_three_quarters() -> None:
    """In the open, the target dives two squares behind a wall: total cover from the shooter,
    which counts as three-quarters (+5) for a shot already rolled."""
    walled = parse_map("\n".join([".....#..", ".....#..", ".....#..", "........", "........"]))
    t = Listed(dives=[Move(((6, 3), (6, 2)))])
    a = Listed(turns=[Shoot("T")])
    result = fight(
        [("A", "red", archer(), (0, 1), a), ("T", "blue", sample(), (6, 4), t)],
        attacks={"A": [1]},
        field=walled,
    )
    (dive,) = of(t, DiveRequest)
    assert dive.cover == 0 and dive.cover_after[(6, 2)] == 2 and dive.cover_after[(6, 3)] == 1
    (dived,) = [e for e in result.log if isinstance(e, Dived)]
    assert dived.cover == 2
    (blocks,) = of(t, BlocksRequest)
    assert (blocks.cover, blocks.defense) == (5, 3 + 5)
    assert spent(result, "T", "off_turn_move") == [1]


def test_drawing_weapons() -> None:
    """After a bow shot, a quick-draw blade is free between turns (even into the bow hands);
    on your next turn the bow comes back free, before you use a weapon."""
    a = Listed(turns=[Shoot("T"), EndTurn(), Draw("bow"), EndTurn()], off_turn=[Draw("blade")])
    result = fight(
        [("A", "red", archer(), (0, 2), a), ("T", "blue", sample(), (6, 2), Listed())],
        attacks={"A": [1]},
        rounds=2,
    )
    drew = [(e.loadout, e.cost) for e in result.log if isinstance(e, Drew)]
    assert drew == [("blade", 0), ("bow", 0)]


def test_no_normal_weapon_into_bow_hands() -> None:
    """A normal weapon can't be drawn after a bow shot until your next turn; between turns a
    normal weapon costs 1."""
    b = replace(
        load_build("l1_archer"),
        name="archer_sword",
        loadouts=(
            ("bow", Loadout(armor="light", weapon="longbow", grip="two")),
            ("sword", Loadout(armor="light", weapon="longsword", grip="two")),
        ),
    )
    profile = derive(b, RULES)
    a = Listed(turns=[Shoot("T")])
    fight(
        [("A", "red", profile, (0, 2), a), ("T", "blue", sample(), (6, 2), Listed())],
        attacks={"A": [1]},
    )
    after_shot = [r for r in of(a, TurnCommand)][1]
    assert after_shot.draws == ()
    assert all(not r.draws for r in of(a, OffTurnMove))
    # Without having shot, drawing the sword between turns costs 1.
    c = Listed(off_turn=[Draw("sword")])
    result = fight([("A", "red", profile, (0, 2), c), ("T", "blue", sample(), (6, 2), Listed())])
    assert [(e.loadout, e.cost) for e in result.log if isinstance(e, Drew)] == [("sword", 1)]
    assert spent(result, "A", "draw") == [1]
