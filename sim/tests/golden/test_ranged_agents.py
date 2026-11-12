"""The agent behaviors for testing 0.10.0's ranged rules (simulator requirements R6), each in
a constructed position where the right answer is known. All are opt-in agent spec fields,
so results without them are unchanged:
- buy (scripted and tactical): buying on-turn squares to reach its target this turn;
- close = off_turn (tactical): buying off-turn squares just before its turn;
- reaction = position (tactical): a reaction to a shot also values where it ends;
- aim = reaction (tactical archer): aim counts the target's best reaction."""

from dataclasses import dataclass, field, replace
from fractions import Fraction
from pathlib import Path
from typing import Any

from stamina_engine.agents.decisions import (
    AimRequest,
    Attack,
    DiveRequest,
    Move,
    Shoot,
)
from stamina_engine.agents.grid_view import Board
from stamina_engine.agents.listed import Listed
from stamina_engine.agents.scripted import make_agent
from stamina_engine.agents.tactical import TacticalAgent
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import log_lines
from stamina_engine.experiments.runner import run_trial
from stamina_engine.experiments.scenario import load_scenario
from stamina_engine.grid.battlefield import Battlefield, Cell, parse_map
from stamina_engine.grid.geometry import distance
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.model.equipment import load_table
from stamina_engine.rules.ruleset import preset

V10 = preset("v0.10.0")
TABLE = load_table("v0_10")
WIDE = parse_map("\n".join(["." * 30] * 5))
WALLED = parse_map("\n".join([".....#..", ".....#..", ".....#..", "........", "........"]))


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        if name not in self.sources:
            self.sources[name] = ScriptedDice([1] * 200)
        return self.sources[name]


@dataclass
class Recorder:
    """Wraps an agent and keeps every (method, answer)."""

    agent: Any
    answers: list[tuple[str, object]] = field(default_factory=list)

    def __getattr__(self, name: str) -> Any:
        inner = getattr(self.agent, name)

        def call(request: object) -> object:
            answer = inner(request)
            self.answers.append((name, answer))
            return answer

        return call

    def of(self, name: str) -> list[object]:
        return [a for n, a in self.answers if n == name]


def profile(name: str, **attrs: int) -> CombatProfile:
    b = load_build(name)
    if attrs:
        b = replace(b, attributes=replace(b.attributes, **attrs), budget="ignore")
    return derive(b, V10, TABLE)


def fight(
    roster: list[tuple[str, str, CombatProfile, Cell, Any]],
    field: Battlefield = WIDE,
    attacks: dict[str, list[int]] | None = None,
) -> BattleResult:
    """The first listed acts first (initiative dice 12 + 12 against 1 + 1)."""
    faces = {"initiative": [12, 12] + [1, 1] * (len(roster) - 1), "dying": [6] * 10}
    faces.update({f"attack:{k}": v for k, v in (attacks or {}).items()})
    entrants = [Entrant(cid, team, p, a, "", pos) for cid, team, p, pos, a in roster]
    return Battle(V10, entrants, Dice(faces), seed=0, round_cap=1, check=True, field=field).run()


# --- buy ----------------------------------------------------------------------------


def _charge(spec: dict[str, object]) -> Recorder:
    """A Strength-1 sample fighter (HP 8, stamina 14) 8 squares from an archer: free
    movement (6) leaves it one square short, so reaching it takes one purchase (1 stamina).
    With alpha, 14 stamina buys 4 steps (2+3+4+5) and 13 only 3."""
    f = Recorder(make_agent(spec, V10))
    fight(
        [
            ("F", "blue", profile("l1_sample", STR=1), (8, 2), f),
            ("A", "red", profile("l1_archer"), (0, 2), Listed()),
        ]
    )
    return f


def test_scripted_pursuers_buy_only_when_told() -> None:
    never = _charge({"commit": "alpha"})
    assert not [a for a in never.of("turn_command") if isinstance(a, Attack)]
    bought = _charge({"commit": "alpha", "buy": "any"})
    (move, *_) = [a for a in bought.of("turn_command") if isinstance(a, Move)]
    assert isinstance(move, Move) and len(move.path) == 7
    assert [a for a in bought.of("turn_command") if isinstance(a, Attack)]


def test_keep_steps_wont_buy_a_square_that_costs_a_step() -> None:
    kept = _charge({"commit": "alpha", "buy": "keep_steps"})
    assert not [a for a in kept.of("turn_command") if isinstance(a, Attack)]
    fixed = _charge({"commit": "fixed:2", "buy": "keep_steps"})  # 2 steps either way
    assert [a for a in fixed.of("turn_command") if isinstance(a, Attack)]


def test_tactical_keep_steps() -> None:
    plain = _charge({"kind": "tactical", "commit": "alpha"})  # buy = any, as before
    assert [a for a in plain.of("turn_command") if isinstance(a, Attack)]
    kept = _charge({"kind": "tactical", "commit": "alpha", "buy": "keep_steps"})
    assert not [a for a in kept.of("turn_command") if isinstance(a, Attack)]


# --- close = off_turn ---------------------------------------------------------------


def test_closing_off_turn_before_its_own_turn() -> None:
    """The archer acts first and ends its turn 10 squares away. In the window before the
    fighter's turn it buys two off-turn purchases (4 squares, 1 + 2 stamina), which puts the
    archer within its next turn's free movement, and then attacks on its turn."""

    def run(close: str) -> Recorder:
        f = Recorder(make_agent({"kind": "tactical", "close": close}, V10))
        fight(
            [
                ("A", "red", profile("l1_archer"), (0, 2), Listed()),
                ("F", "blue", profile("l1_sample"), (10, 2), f),
            ]
        )
        return f

    plain = run("none")
    assert not [a for a in plain.of("off_turn_move") if isinstance(a, Move)]
    closing = run("off_turn")
    (move, *_) = [a for a in closing.of("off_turn_move") if isinstance(a, Move)]
    assert isinstance(move, Move) and distance(move.path[-1], (1, 2), V10.grid) <= 6
    assert [a for a in closing.of("turn_command") if isinstance(a, Attack)]


# --- reaction = position ------------------------------------------------------------


def _dive_request(field: Battlefield = WIDE, target_at: Cell = (3, 2)) -> DiveRequest:
    t = Listed()
    fight(
        [
            ("A", "red", profile("l1_archer"), (0, 2), Listed(turns=[Shoot("T")])),
            ("T", "blue", profile("l1_sample"), target_at, t),
        ],
        field,
        attacks={"A": [4, 3]},
    )
    (request,) = [r for r in t.requests if isinstance(r, DiveRequest)]
    return request


def tactical(**spec: object) -> TacticalAgent:
    agent = make_agent({"kind": "tactical", **spec}, V10)
    assert isinstance(agent, TacticalAgent)
    return agent


def test_place_value() -> None:
    """Contact with the archer is worth the 1 stamina it pays to leave (cheaper than taking
    the opportunity attack); approach_weight adds a value per square closer."""
    request = _dive_request()
    obs = request.observation
    agent = tactical(reaction="position", approach_weight="1/2")
    place = agent._place_value(Board(obs, V10), obs.view("A"))
    assert place((1, 2)) == 1 + Fraction(1, 2) * 2
    assert place((3, 2)) == 0
    assert place((5, 2)) == Fraction(1, 2) * -2
    flat = tactical(reaction="position")._place_value(Board(obs, V10), obs.view("A"))
    assert flat((1, 2)) == 1 and flat((5, 2)) == 0


def test_a_reaction_that_closes_in() -> None:
    """Closing in gains nothing on this shot (Melee Defense 3 against Ranged Defense 2 + 1
    for moving) and costs 1, so the shot-only agent stays; with a value on the square it
    ends on, it closes to contact."""
    request = _dive_request()
    assert tactical().dive(request) == tactical(reaction="shot").dive(request)
    stay = tactical().dive(request)
    assert not isinstance(stay, Move) or distance(stay.path[-1], (0, 2), V10.grid) > 1
    close = tactical(reaction="position", approach_weight="1").dive(request)
    assert isinstance(close, Move) and distance(close.path[-1], (0, 2), V10.grid) == 1


# --- aim = reaction -----------------------------------------------------------------


def _aim_request(field: Battlefield, archer_at: Cell, target_at: Cell) -> AimRequest:
    a = Listed(turns=[Shoot("T")])
    fight(
        [
            ("A", "red", profile("l1_archer"), archer_at, a),
            ("T", "blue", profile("l1_sample"), target_at, Listed()),
        ],
        field,
    )
    (request,) = [r for r in a.requests if isinstance(r, AimRequest)]
    return request


def test_reaction_options_by_a_wall() -> None:
    """Next to a wall, the target can stay (Ranged Defense 2), step anywhere (+1), or dive
    behind the wall (+1 + three-quarters cover 2) for one purchase."""
    request = _aim_request(WALLED, (0, 1), (6, 4))
    obs = request.observation
    options = tactical(aim="reaction")._reaction_options(Board(obs, V10), obs.view("T"), request)
    assert (2, request.penalty, 0) in options
    assert any(d == 2 + 1 + 2 and spend == 1 for d, _, spend in options)
    assert all(
        not (q != o and q[0] >= o[0] and q[1] >= o[1] and q[2] <= o[2])
        for o in options
        for q in options
    )


def test_aim_against_a_target_that_cant_react_matches_aim() -> None:
    """With no stamina to move, the only reaction is to stay, and the two aims agree."""
    request = _aim_request(WIDE, (0, 2), (9, 2))
    obs = request.observation
    stuck = replace(obs, others=tuple(replace(v, stamina=0) for v in obs.others))
    req = replace(request, observation=stuck)
    assert tactical(aim="reaction").aim(req) == tactical().aim(req)


def test_the_new_agents_play_and_repeat() -> None:
    """The archer-open scenario with every new behavior on: invariants hold and the same
    trial gives the same log."""
    s = load_scenario(
        Path(__file__).resolve().parents[2] / "src/stamina_engine/data/scenarios/archer_open.toml"
    )
    spec = {"kind": "tactical", "reaction": "position", "aim": "reaction", "close": "off_turn"}
    combatants = tuple(replace(c, agent=spec) for c in s.combatants)
    s = replace(s, combatants=combatants, trials=3)
    for trial in range(3):
        first = log_lines(run_trial(s, trial, check=True).log)
        assert first == log_lines(run_trial(s, trial, check=True).log)
