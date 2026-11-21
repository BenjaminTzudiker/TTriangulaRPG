"""Packet 0.11.4, shooting in melee (rules/CHANGELOG.md): the enemies threatening a shooter
when it declares the target make their opportunity attacks at once, before the shot."""

from pathlib import Path

from stamina_engine.agents.decisions import Move, OATake, Shoot, TakeOA
from stamina_engine.agents.listed import Listed
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import OpportunityProvoked, ShotDeclared, Spent
from stamina_engine.grid.battlefield import Cell, parse_map
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.model.equipment import load_table
from stamina_engine.rules.ruleset import preset

RULES = preset("exp-0.11.4")
TABLE = load_table("v0_10")
WIDE = parse_map("\n".join(["." * 30] * 5))
SCENARIOS = Path(__file__).resolve().parents[2] / "src/stamina_engine/data/scenarios"


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources[name]


def profile(name: str) -> CombatProfile:
    return derive(load_build(name), RULES, TABLE)


def fight(t: Listed, target_at: Cell, attacks: dict[str, list[int]]) -> BattleResult:
    faces = {"initiative": [12, 12, 1, 1], "dying": [6] * 10}
    faces.update({f"attack:{k}": v for k, v in attacks.items()})
    entrants = [
        Entrant("A", "red", profile("l1_archer"), Listed(turns=[Shoot("T")]), "", (2, 2)),
        Entrant("T", "blue", profile("l1_sample"), t, "", target_at),
    ]
    return Battle(RULES, entrants, Dice(faces), seed=0, round_cap=1, check=True, field=WIDE).run()


def _index(result: BattleResult, kind: type, **match: str) -> int:
    for i, e in enumerate(result.log):
        if isinstance(e, kind) and all(getattr(e, k) == v for k, v in match.items()):
            return i
    raise AssertionError(f"no {kind.__name__} {match}")


def test_point_blank_opportunity_attacks_come_before_the_shot() -> None:
    t = Listed(oas=[OATake("main", 1)])
    result = fight(t, (3, 2), {"A": [1, 1], "T": [1]})
    provoked = _index(result, OpportunityProvoked, mover="A")
    assert result.log[provoked].enemies == ("T",)
    assert provoked < _index(result, ShotDeclared, shooter="A")
    assert t.requests and [r for r in t.requests if isinstance(r, TakeOA)]
    assert [
        e.amount
        for e in result.log
        if isinstance(e, Spent) and e.who == "A" and e.category == "shot"
    ]


def test_backing_away_no_longer_dodges_the_opportunity_attack() -> None:
    """Under 0.10.0 to 0.11.3 a target that backed out of reach in reaction lost its
    opportunity attack. Now the attack has already happened when the target reacts."""
    t = Listed(dives=[Move(((4, 2), (5, 2)))], oas=[OATake("main", 1)])
    result = fight(t, (3, 2), {"A": [1, 1], "T": [1]})
    assert _index(result, OpportunityProvoked, mover="A") < _index(
        result, ShotDeclared, shooter="A"
    )


def test_closing_in_still_doesnt_provoke() -> None:
    """Only enemies threatening the shooter when it declares the target get an opportunity
    attack, so a target that closes in during the shot gets none."""
    t = Listed(dives=[Move(((3, 2),))], oas=[OATake("main", 1)])
    result = fight(t, (4, 2), {"A": [1, 1], "T": [1]})
    assert not [e for e in result.log if isinstance(e, OpportunityProvoked) and e.mover == "A"]
