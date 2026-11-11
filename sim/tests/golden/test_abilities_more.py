"""The Rogue core, the candidate abilities and the control-track stub (Packet: Core
Abilities, Candidate Abilities, Conditions and Control Effects). Readings in the register."""

from dataclasses import replace

import pytest

from stamina_engine.agents.decisions import Attack, BlocksRequest, Move, OATake, Pass, UseAbility
from stamina_engine.agents.listed import Listed
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.core.errors import RulesError
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import (
    AbilityUsed,
    AttackAvoided,
    AttackResolved,
    OpportunityDeclared,
    OrderChanged,
    Spent,
    TurnStarted,
)
from stamina_engine.engine.stateops import StateOps
from stamina_engine.grid.battlefield import parse_map
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.model.state import BattleState, new_combatant
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import preset

RULES = preset("v0.9")


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources[name]


def with_abilities(build: str, *names: str) -> CombatProfile:
    return derive(replace(load_build(build), abilities=names), RULES)


def battle(
    entrants: list[Entrant], faces: dict[str, list[int]], rounds: int = 1, field: object = None
) -> BattleResult:
    return Battle(
        RULES, entrants, Dice(faces), seed=0, round_cap=rounds, check=True, field=field
    ).run()  # type: ignore[arg-type]


def turns(result: BattleResult) -> list[str]:
    return [e.who for e in result.log if isinstance(e, TurnStarted)]


def test_rogue_jumps_in_ahead_and_keeps_the_slot() -> None:
    """Initiative A, B, R. Before B's turn the Rogue takes its turn now (3 strain); next
    round it acts in its new slot."""
    rogue = derive(load_build("l1_rogue"), RULES)
    r = Listed(uses=[Pass(), UseAbility("rogue_core")])  # not before A; before B
    entrants = [
        Entrant("A", "x", derive(load_build("l1_sample"), RULES), Listed()),
        Entrant("B", "y", derive(load_build("l1_sample"), RULES), Listed()),
        Entrant("R", "x", rogue, r),
    ]
    result = battle(entrants, {"initiative": [12, 12, 6, 6, 1, 1]}, rounds=2)
    assert turns(result) == ["A", "R", "B", "A", "R", "B"]
    (changed,) = [e for e in result.log if isinstance(e, OrderChanged)]
    assert changed.order == ("A", "R", "B")
    assert [e.strain_after for e in result.log if isinstance(e, AbilityUsed)] == [3]


def test_rogue_waits_and_comes_back_after_a_later_turn() -> None:
    """At its turn's start (first in initiative) the Rogue waits; it comes back for free
    after the next creature's turn."""
    rogue = derive(load_build("l1_rogue"), RULES)
    r = Listed(uses=[UseAbility("rogue_core"), Pass(), Pass()])  # wait; not before A
    entrants = [
        Entrant("R", "x", rogue, r),
        Entrant("A", "y", derive(load_build("l1_sample"), RULES), Listed()),
        Entrant("B", "y", derive(load_build("l1_sample"), RULES), Listed()),
    ]
    result = battle(entrants, {"initiative": [12, 12, 6, 6, 1, 1]})
    assert turns(result) == ["A", "R", "B"]
    assert [e.strain_after for e in result.log if isinstance(e, AbilityUsed)] == [3]


def test_heavy_swing_costs_a_step_more_and_pierces_two_armor() -> None:
    a = Listed(turns=[Attack("B")], commit=[2], uses=[UseAbility("heavy_swing")])
    b = Listed()
    entrants = [
        Entrant("A", "A", with_abilities("l1_sample", "heavy_swing"), a),
        Entrant("B", "B", derive(load_build("l1_heavy"), RULES), b),
    ]
    result = battle(entrants, {"initiative": [12, 12, 1, 1], "attack:A": [1, 1], "dying": [6] * 9})
    (paid,) = [e for e in result.log if isinstance(e, Spent) and e.category == "attack"]
    assert paid.parts == (3, 4)  # 2 + 1, 3 + 1
    (hit,) = [e for e in result.log if isinstance(e, AttackResolved)]
    assert hit.armor_applied == 1  # heavy armor 3, less 2
    # The defender blocks knowing the armor it faces, not its full 3.
    (asked,) = [r for r in b.requests if isinstance(r, BlocksRequest)]
    assert asked.armor == 1


def test_a_defender_against_heavy_swing_takes_no_unplanned_wound() -> None:
    """10 damage against Melee Defense 4 in heavy armor: told armor 3, the solver's 1 perfect +
    1 grazing block (3 left, soaked) would lose 2 HP to Heavy Swing's armor 1. Told the armor
    it faces, the defender's blocks give the injury it planned."""
    from stamina_engine.rules.block_solver import best_block
    from stamina_engine.rules.exchange import resolve

    told_full = best_block(10, 0, 4, 3, 10, 8, RULES)
    assert told_full.injury == 0 and resolve(10, 0, 4, 1, told_full.blocks, RULES).injury == 2
    told_faced = best_block(10, 0, 4, 1, 10, 8, RULES)
    assert resolve(10, 0, 4, 1, told_faced.blocks, RULES).injury == told_faced.injury


def test_riposte_after_a_perfect_block() -> None:
    a = Listed(turns=[Attack("B")], commit=[1])
    b = Listed(block_answers=[Blocks(1, 0)], oas=[OATake("main", 1)])
    entrants = [
        Entrant("A", "A", derive(load_build("l1_sample"), RULES), a),
        Entrant("B", "B", with_abilities("l1_sample", "riposte"), b),
    ]
    result = battle(entrants, {"initiative": [12, 12, 1, 1], "attack:A": [1], "attack:B": [1]})
    (oa,) = [e for e in result.log if isinstance(e, OpportunityDeclared)]
    assert (oa.attacker, oa.target) == ("B", "A")
    assert [
        e.amount for e in result.log if isinstance(e, Spent) and e.category == "opportunity"
    ] == [2]


def test_tactical_withdrawal_gets_out_of_reach() -> None:
    field = parse_map("\n".join(["......"] * 3))
    a = Listed(turns=[Attack("B")], commit=[1])
    b = Listed(uses=[UseAbility("tactical_withdrawal")], dives=[Move(((4, 1), (5, 1)))])
    entrants = [
        Entrant("A", "A", derive(load_build("l1_sample"), RULES), a, "", (2, 1)),
        Entrant("B", "B", with_abilities("l1_sample", "tactical_withdrawal"), b, "", (3, 1)),
    ]
    result = battle(entrants, {"initiative": [12, 12, 1, 1], "attack:A": [8]}, field=field)
    assert any(isinstance(e, AttackAvoided) for e in result.log)
    assert not any(isinstance(e, AttackResolved) for e in result.log)
    assert [e.amount for e in result.log if isinstance(e, Spent) and e.who == "B"] == [2]


def test_control_track_stub() -> None:
    c = new_combatant("c", "red", derive(load_build("l1_sample"), RULES))
    ops = StateOps(BattleState((c,)), RULES, [], check=True)
    ops.advance_control(c, "grappled", 3, "x")
    ops.resist_control(c, "grappled", 2)
    assert c.control == {"grappled": 1}
    ops.resist_control(c, "grappled", 1)
    assert c.control == {}
    with pytest.raises(RulesError):
        ops.resist_control(c, "grappled", 1)
