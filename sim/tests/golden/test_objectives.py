"""Scenario objectives (O1): reach, escape and hold, played as small battles with listed
answers. Packet: Running the Game; readings in the Assumptions register."""

from pathlib import Path

import pytest

from stamina_engine.agents.decisions import EndTurn, Flee, Move, Surrender
from stamina_engine.agents.listed import Listed
from stamina_engine.agents.objective_play import goal
from stamina_engine.agents.scripted import make_agent
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.core.errors import ConfigError
from stamina_engine.core.rng import Streams
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import ObjectiveProgress, ObjectiveReached, ObjectiveResolved
from stamina_engine.experiments.metrics import fight_row, summarize
from stamina_engine.experiments.runner import battle_for, run_trial
from stamina_engine.experiments.scenario import load_scenario, scenario_from_toml, scenario_to_toml
from stamina_engine.grid.battlefield import Cell, parse_map
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.model.objectives import ObjectiveSpec, Zone
from stamina_engine.rules.ruleset import preset

RULES = preset("v0.9")
FIELD = parse_map("\n".join(["........>", ".........", "........."]))
ZONE = Zone("z", ((5, 1), (6, 1)))
SCENARIOS = Path(__file__).resolve().parents[2] / "src" / "stamina_engine" / "data" / "scenarios"


class Dice:
    """Initiative in listed order (no ties); everything else from seeded streams."""

    def __init__(self, n: int) -> None:
        self.faces = [12, 12] + [f for i in range(n - 1) for f in (1, 1 + i)]
        self.streams = Streams(1)

    def dice(self, name: str):  # type: ignore[no-untyped-def]
        return ScriptedDice(self.faces) if name == "initiative" else self.streams.dice(name)


def sample() -> CombatProfile:
    return derive(load_build("l1_sample"), RULES)


def fight(
    roster: list[tuple[str, str, Cell, Listed]], objective: ObjectiveSpec, rounds: int = 3
) -> BattleResult:
    entrants = [Entrant(cid, team, sample(), a, "", pos) for cid, team, pos, a in roster]
    return Battle(
        RULES,
        entrants,
        Dice(len(roster)),
        seed=1,
        round_cap=rounds,
        check=True,
        field=FIELD,
        objectives=(objective,),
    ).run()


def spec(kind: str, who: tuple[str, ...], **kw: object) -> ObjectiveSpec:
    return ObjectiveSpec(id="obj", kind=kind, team="red", who=who, **kw)  # type: ignore[arg-type]


def events(result: BattleResult, kind: type) -> list:  # type: ignore[type-arg]
    return [e for e in result.log if isinstance(e, kind)]


# --- escape ------------------------------------------------------------------------------


def test_escape_counts_before_side_out() -> None:
    """The last red creature fleeing takes its side out, but it has escaped: red wins."""
    a = Listed(turns=[Move(((8, 0),)), Flee()])
    result = fight(
        [("A", "red", (7, 0), a), ("B", "blue", (1, 2), Listed())],
        spec("escape", ("A",), count=1, deadline=3),
    )
    assert (result.winner, result.reason) == ("red", "objective:obj")
    assert result.objective == "done"
    assert [e.who for e in events(result, ObjectiveReached)] == ["A"]


def test_escape_fails_once_too_few_can_make_it() -> None:
    a1, a2 = Listed(turns=[Surrender()]), Listed()
    result = fight(
        [("A1", "red", (1, 0), a1), ("A2", "red", (1, 1), a2), ("B", "blue", (1, 2), Listed())],
        spec("escape", ("A1", "A2"), count=2, deadline=3),
    )
    assert (result.winner, result.reason) == ("blue", "objective_failed:obj")
    assert result.rounds == 1 and result.objective == "failed"


# --- reach -------------------------------------------------------------------------------


def test_a_creature_that_reached_the_zone_stays_counted() -> None:
    a1 = Listed(turns=[Move(((4, 1), (5, 1))), Move(((4, 1), (3, 1)))])
    a2 = Listed(turns=[Move(((5, 2), (6, 1)))])
    result = fight(
        [("A1", "red", (3, 1), a1), ("A2", "red", (4, 2), a2), ("B", "blue", (0, 2), Listed())],
        spec("reach", ("A1", "A2"), zone=ZONE, count=2, deadline=3),
    )
    assert [e.who for e in events(result, ObjectiveReached)] == ["A1", "A2"]
    assert (result.winner, result.reason, result.rounds) == ("red", "objective:obj", 1)


def test_passing_through_the_zone_does_not_count_and_the_deadline_fails_it() -> None:
    a = Listed(turns=[Move(((4, 1), (5, 1), (6, 1), (7, 1)))])
    result = fight(
        [("A", "red", (3, 1), a), ("B", "blue", (0, 2), Listed())],
        spec("reach", ("A",), zone=ZONE, count=1, deadline=1),
    )
    assert not events(result, ObjectiveReached)
    assert (result.winner, result.reason, result.rounds) == ("blue", "objective_failed:obj", 1)


# --- hold --------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("control", "status"), [("present", "done"), ("uncontested", "failed"), ("majority", "failed")]
)
def test_hold_streak_under_each_control_reading(control: str, status: str) -> None:
    """Red holds the zone alone in round 1; blue steps in during round 2."""
    b = Listed(turns=[EndTurn(), Move(((7, 1), (6, 1)))])
    result = fight(
        [("A", "red", (5, 1), Listed()), ("B", "blue", (8, 1), b)],
        spec("hold", ("A",), zone=ZONE, control=control, score="consecutive", rounds=2, deadline=2),
    )
    scored = [(e.round, e.controlled, e.streak) for e in events(result, ObjectiveProgress)]
    second = control == "present"
    assert scored == [(1, True, 1), (2, second, 2 if second else 0)]
    assert result.objective == status and result.rounds == 2
    assert result.winner == ("red" if second else "blue")


def test_cumulative_hold_counts_rounds_not_streaks() -> None:
    b = Listed(turns=[Move(((7, 1), (6, 1))), EndTurn(), Move(((7, 1), (8, 1)))])
    result = fight(
        [("A", "red", (5, 1), Listed()), ("B", "blue", (8, 1), b)],
        spec(
            "hold",
            ("A",),
            zone=ZONE,
            control="uncontested",
            score="cumulative",
            rounds=2,
            deadline=3,
        ),
    )
    scored = [(e.round, e.controlled, e.progress) for e in events(result, ObjectiveProgress)]
    assert scored == [(1, False, 0), (2, True, 1), (3, True, 2)]
    assert (result.winner, result.reason) == ("red", "objective:obj")


def test_final_hold_is_scored_only_at_the_deadline() -> None:
    result = fight(
        [("A", "red", (5, 1), Listed()), ("B", "blue", (0, 2), Listed())],
        spec("hold", ("A",), zone=ZONE, control="uncontested", score="final", deadline=2),
        rounds=5,
    )
    assert [e.round for e in events(result, ObjectiveProgress)] == [2]
    assert [(e.status, e.round) for e in events(result, ObjectiveResolved)] == [("done", 2)]
    assert (result.winner, result.rounds) == ("red", 2)


# --- metrics and agents ------------------------------------------------------------------


def test_fight_rows_and_summary_report_the_objective() -> None:
    a = Listed(turns=[Move(((8, 0),)), Flee()])
    result = fight(
        [("A", "red", (7, 0), a), ("B", "blue", (1, 2), Listed())],
        spec("escape", ("A",), count=1, deadline=3),
    )
    row = fight_row(result, 0, 0)
    assert (row["objective"], row["objective_round"], row["ending"]) == ("done", 1, "objective")
    s = summarize([row])
    assert s.objective is not None and s.objective.estimate == 1
    assert s.endings is not None and s.endings["objective"].estimate == 1
    assert any(line.startswith("Objective done") for line in s.lines())


def test_fights_without_an_objective_report_none() -> None:
    result = run_trial(load_scenario(SCENARIOS / "party_3v3.toml"), 0)
    assert result.objective is None and "objective" not in fight_row(result, 0, 0)
    assert summarize([fight_row(result, 0, 0)]).objective is None


def test_agents_reject_an_unknown_objective_mode() -> None:
    with pytest.raises(ConfigError):
        make_agent({"kind": "tactical", "objective": "maybe"}, RULES)


@pytest.mark.parametrize(
    "name", ["extraction_3v3", "breakthrough_3v3", "hold_hill_3v3", "hold_the_door_1v3"]
)
def test_agents_see_the_objective_and_their_role(name: str) -> None:
    s = load_scenario(SCENARIOS / f"{name}.toml")
    b = battle_for(s, 1)
    pursuer = next(c.id for c in s.combatants if c.team == s.objectives[0].team)
    denier = next(c.id for c in s.combatants if c.team != s.objectives[0].team)
    gp, gd = goal(b.observe(pursuer)), goal(b.observe(denier))
    assert gp is not None and gp.pursue and gp.counts and gp.cells
    assert gd is not None and not gd.pursue


# --- scenario files ----------------------------------------------------------------------

BASE = """
[scenario]
name = "t"
map_text = \"\"\"
....>
.HH..
.....
\"\"\"

[[combatant]]
id = "A"
team = "red"
build = "l1_sample"
spawn = [0, 0]

[[combatant]]
id = "B"
team = "blue"
build = "l1_sample"
spawn = [0, 2]
"""


def test_zones_and_objectives_round_trip() -> None:
    text = (
        BASE
        + """
[[zone]]
id = "hill"
marker = "H"

[[objective]]
id = "o"
kind = "hold"
team = "red"
zone = "hill"
control = "majority"
score = "cumulative"
rounds = 2
deadline = 5
"""
    )
    s = scenario_from_toml(text)
    assert s.zones == (Zone("hill", ((1, 1), (2, 1))),)
    assert s.objectives[0].who == ("A",) and s.objectives[0].deadline == 5
    again = scenario_from_toml(scenario_to_toml(s))
    assert again.zones == s.zones and again.objectives == s.objectives


def test_escape_defaults_count_and_deadline() -> None:
    s = scenario_from_toml(BASE + '\n[[objective]]\nid = "o"\nkind = "escape"\nteam = "red"\n')
    o = s.objectives[0]
    assert (o.count, o.deadline, o.who) == (1, 30, ("A",))


@pytest.mark.parametrize(
    "extra",
    [
        '[[zone]]\nid = "z"\ncells = [[9, 9]]',  # off the map
        '[[objective]]\nid = "o"\nkind = "fly"\nteam = "red"',
        '[[objective]]\nid = "o"\nkind = "escape"\nteam = "green"',
        '[[objective]]\nid = "o"\nkind = "escape"\nteam = "red"\nwho = ["B"]',
        '[[objective]]\nid = "o"\nkind = "escape"\nteam = "red"\ncount = 2',
        '[[objective]]\nid = "o"\nkind = "escape"\nteam = "red"\ndeadline = 31',
        '[[objective]]\nid = "o"\nkind = "reach"\nteam = "red"',
        '[[zone]]\nid = "z"\nmarker = "H"\n[[objective]]\nid = "o"\nkind = "hold"\n'
        'team = "red"\nzone = "z"\nscore = "final"\ndeadline = 3',  # no control reading
        '[[zone]]\nid = "z"\nmarker = "H"\n[[objective]]\nid = "o"\nkind = "hold"\n'
        'team = "red"\nzone = "z"\ncontrol = "present"\nscore = "final"',  # no deadline
        '[[objective]]\nid = "o"\nkind = "escape"\nteam = "red"\nspeed = 2',
    ],
)
def test_bad_objective_configs_are_refused(extra: str) -> None:
    with pytest.raises(ConfigError):
        scenario_from_toml(BASE + "\n" + extra + "\n")
