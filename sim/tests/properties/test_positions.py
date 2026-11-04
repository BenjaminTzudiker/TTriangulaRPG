"""Positions on a map: StateOps as the only writer, battles that start on squares, and
scenarios with spawns."""

import json

import pytest

from stamina_engine.agents.scripted import make_agent
from stamina_engine.core.errors import ConfigError, EngineError, RulesError
from stamina_engine.core.rng import Streams
from stamina_engine.engine.battle import Battle, Entrant
from stamina_engine.engine.events import MapLoaded, Placed
from stamina_engine.engine.stateops import StateOps
from stamina_engine.experiments.runner import battle_for
from stamina_engine.experiments.scenario import scenario_from_toml, scenario_to_toml
from stamina_engine.grid.battlefield import Battlefield, parse_map
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.model.state import BattleState, CombatantState, new_combatant
from stamina_engine.rules.ruleset import preset

RULES = preset("v0.9")
FIELD = parse_map(".....\n.#...\n#....\n.....")


def creatures(*specs: tuple[str, str]) -> tuple[CombatantState, ...]:
    profile = derive(load_build("l1_sample"), RULES)
    return tuple(new_combatant(cid, team, profile) for cid, team in specs)


def ops_on(field: Battlefield, *placed: tuple[str, str, tuple[int, int]]) -> StateOps:
    state = BattleState(creatures(*[(cid, team) for cid, team, _ in placed]))
    ops = StateOps(state, RULES, [], check=True, field=field)
    for cid, _, cell in placed:
        ops.place(state.get(cid), cell)
    return ops


def test_place_refuses_walls_and_occupied_squares() -> None:
    ops = ops_on(FIELD, ("a", "red", (0, 0)))
    b = creatures(("b", "red"))[0]
    with pytest.raises(RulesError, match="wall"):
        ops.place(b, (1, 1))
    with pytest.raises(RulesError, match="occupied"):
        ops.place(b, (0, 0))
    with pytest.raises(EngineError, match="all-adjacent"):
        StateOps(BattleState(creatures(("c", "red"))), RULES, []).place(b, (0, 0))


def test_moves_use_free_squares_and_respect_corners() -> None:
    ops = ops_on(FIELD, ("a", "red", (0, 1)))
    a = ops.state.get("a")
    ops.start_turn(a)
    assert a.free_move_left == 6  # the sample fighter's Movement
    with pytest.raises(RulesError, match="can't step"):
        ops.move_to(a, (1, 2), "free")  # squeezes between the walls at (1, 1) and (0, 2)
    ops.move_to(a, (0, 0), "free")
    ops.move_to(a, (1, 0), "free")
    ops.end_move(a)
    assert a.pos == (1, 0) and a.free_move_left == 4
    with pytest.raises(RulesError, match="no bought squares"):
        ops.move_to(a, (2, 0), "extra")
    ops.bank(a, 2)
    ops.move_to(a, (2, 0), "extra")
    assert a.banked == 1
    moved = [json.loads(e.to_json()) for e in ops.log if type(e).__name__ == "Moved"]
    assert [m["how"] for m in moved] == ["free", "free", "extra"]


def test_pass_through_allies_but_never_stop_on_them() -> None:
    ops = ops_on(FIELD, ("a", "red", (2, 0)), ("b", "red", (3, 0)), ("e", "blue", (3, 1)))
    a = ops.state.get("a")
    ops.start_turn(a)
    ops.move_to(a, (3, 0), "free")  # onto the ally, mid-move: allowed
    with pytest.raises(RulesError, match="end its move"):
        ops.end_move(a)
    ops.move_to(a, (4, 0), "free")
    ops.end_move(a)
    with pytest.raises(RulesError, match="through e"):
        ops.move_to(a, (3, 1), "free")


def test_validate_catches_shared_squares() -> None:
    ops = ops_on(FIELD, ("a", "red", (2, 0)), ("b", "red", (3, 0)))
    a = ops.state.get("a")
    ops.start_turn(a)
    ops.move_to(a, (3, 0), "free")
    ops.state.moving = None  # simulate a bug: the move ended without end_move
    with pytest.raises(EngineError, match="share"):
        ops.validate()


def duel_on(
    field: Battlefield, a: tuple[int, int], b: tuple[int, int], spec: str = "alpha"
) -> Battle:
    profile = derive(load_build("l1_sample"), RULES)
    dice = Streams(5)
    entrants = [
        Entrant(cid, cid, profile, make_agent(spec, RULES, dice.dice(f"agent:{cid}")), "", pos)
        for cid, pos in (("a", a), ("b", b))
    ]
    return Battle(RULES, entrants, dice, seed=5, round_cap=3, check=True, field=field)


def test_battle_on_a_map_places_everyone_and_respects_reach() -> None:
    field = parse_map("\n".join(["........"] * 3))
    far = duel_on(field, (0, 1), (7, 1), "never").run()
    assert isinstance(far.log[1], MapLoaded) and far.log[1].width == 8
    assert [e.pos for e in far.log if isinstance(e, Placed)] == [(0, 1), (7, 1)]
    # Agents that won't attack don't approach: no movement, no attacks, a draw.
    assert far.reason == "round_cap"
    assert not any(type(e).__name__ in ("AttackDeclared", "Moved") for e in far.log)
    # Scripted attackers close with free movement (6 squares) and fight.
    closing = duel_on(field, (0, 1), (7, 1)).run()
    assert any(type(e).__name__ == "Moved" for e in closing.log)
    assert any(type(e).__name__ == "AttackDeclared" for e in closing.log)


def test_battle_needs_squares_and_a_map_together() -> None:
    profile = derive(load_build("l1_sample"), RULES)
    agent = make_agent("alpha", RULES)
    with pytest.raises(ConfigError, match="starting square"):
        Battle(RULES, [Entrant("a", "a", profile, agent)], Streams(1), seed=1, field=FIELD)
    with pytest.raises(ConfigError, match="need a map"):
        Battle(RULES, [Entrant("a", "a", profile, agent, "", (0, 0))], Streams(1), seed=1)


SCENARIO = """
[scenario]
name = "map-test"
map = "open_12x12"
trials = 2

[[combatant]]
id = "D"
team = "pc"
build = "l1_sample"
spawn = "A"

[[combatant]]
id = "x"
team = "npc"
build = "l1_sample"
count = 3
spawn = ["1", "2", [11, 11]]
"""


def test_scenario_spawns_and_round_trip() -> None:
    s = scenario_from_toml(SCENARIO)
    assert s.arena == "map" and s.battlefield is not None
    assert [c.pos for c in s.combatants] == [(4, 6), (10, 4), (10, 6), (11, 11)]
    again = scenario_from_toml(scenario_to_toml(s))
    assert again.battlefield is not None and again.battlefield.rows == s.battlefield.rows
    assert [c.pos for c in again.combatants] == [c.pos for c in s.combatants]
    result = battle_for(s, 1, check=True).run()
    assert sum(isinstance(e, Placed) for e in result.log) == 4


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (('spawn = "A"', ""), "needs a spawn"),
        (('map = "open_12x12"', ""), "spawns need a map|has no map"),
        (('spawn = "A"', "spawn = [10, 4]"), "share a starting square"),
        (('spawn = "A"', "spawn = [0, 0]"), "isn't floor"),
        (('spawn = "A"', 'spawn = "Q"'), "no spawn 'Q'"),
        (('spawn = ["1", "2", [11, 11]]', 'spawn = ["1", "2"]'), "3 combatants but 2 spawns"),
        (('spawn = ["1", "2", [11, 11]]', 'spawn = "1"'), "has 1 squares"),
    ],
)
def test_scenario_spawn_errors(edit: tuple[str, str], message: str) -> None:
    with pytest.raises(ConfigError, match=message):
        scenario_from_toml(SCENARIO.replace(*edit))
