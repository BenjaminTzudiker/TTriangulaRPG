"""Off-turn windows played as battles (Packet: Off-Turn Movement, Off-Turn Escalation;
Review Addendum 2, F14). Reading C12 in the Assumptions register."""

from dataclasses import dataclass, field

import pytest

from stamina_engine.agents.decisions import (
    Avoid,
    AvoidOA,
    BlocksRequest,
    Commitment,
    EndTurn,
    Move,
    MoveAnswer,
    OATake,
    OffTurnMove,
    Pass,
    TakeOA,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.agents.listed import Listed
from stamina_engine.agents.scripted import make_agent
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.core.errors import EngineError
from stamina_engine.core.rng import Streams
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import Event, Spent
from stamina_engine.grid.battlefield import Battlefield, Cell, parse_map
from stamina_engine.model.build import Attributes, Build, Loadout, load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import RuleSet, preset

RULES = preset("v0.9")
WIDE = parse_map("\n".join(["." * 20] * 9))


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources[name]


def built(name: str, agility: int, finesse: int, weapon: str, off_hand: str | None) -> Build:
    return Build(
        name,
        1,
        Attributes(STR=2, AGI=agility, FIN=finesse),
        (("m", Loadout(armor="medium", weapon=weapon, grip="one", off_hand=off_hand)),),
        ("fighter",),
        budget="ignore",  # illustrative builds, as in Addendum 2
    )


def run(
    roster: list[tuple[str, str, CombatProfile, Cell, object, tuple[int, int]]],
    attacks: dict[str, list[int]] | None = None,
    rules: RuleSet = RULES,
    field_: Battlefield = WIDE,
    rounds: int = 1,
) -> BattleResult:
    faces = {"initiative": [f for *_, ini in roster for f in ini]}
    faces.update({f"attack:{k}": v for k, v in (attacks or {}).items()})
    entrants = [Entrant(cid, team, p, a, "", pos) for cid, team, p, pos, a, _ in roster]  # type: ignore[arg-type]
    return Battle(
        rules, entrants, Dice(faces), seed=0, round_cap=rounds, check=True, field=field_
    ).run()


def spent(log: tuple[Event, ...], who: str) -> list[tuple[str, int]]:
    return [(e.category, e.amount) for e in log if isinstance(e, Spent) and e.who == who]


@pytest.mark.parametrize(
    ("agility", "purchases", "costs"),
    [(1, 4, [1, 2, 3, 4]), (3, 3, [1, 2, 3]), (5, 2, [1, 2])],
)
def test_addendum_2_played(agility: int, purchases: int, costs: list[int]) -> None:
    """The fleer backs 7 squares away off-turn right after its own turn (out of the chaser's
    free reach of 6 + 1), paying the escalation and 1 to avoid the OA; the chaser then closes
    on its turn for 1."""
    fleer = derive(built(f"fleer{agility}", agility, 1, "longsword", "shield"), RULES)
    away = tuple((x, 4) for x in range(3, 10))
    f = Listed(off_turn=[Move(away)], avoids=[Avoid(("C",))])
    c = Listed(turns=[Move(tuple((x, 4) for x in range(2, 9)))])
    result = run(
        [
            ("F", "red", fleer, (2, 4), f, (12, 12)),
            ("C", "blue", derive(load_build("l1_sample"), RULES), (1, 4), c, (1, 1)),
        ]
    )
    assert spent(result.log, "F") == [("off_turn_move", k) for k in costs] + [("avoid", 1)]
    assert spent(result.log, "C") == [("extra_move", 1)]
    assert result.state.get("F").pos == (9, 4)
    assert result.state.get("C").pos == (8, 4)


def test_off_turn_escalation_example() -> None:
    """Between your turns: move 1 square (1), move 1 square (2), a dagger OA (3), move 1
    square (4): 10 stamina. The OA needs a cap of at least 3, such as Finesse 3."""
    x_profile = derive(built("x", 0, 3, "dagger", "shield"), RULES)
    assert x_profile.main.oa_cap == 3 and x_profile.main.squares_per_purchase == 1
    x = Listed(
        off_turn=[Move(((6, 4),)), Move(((7, 4),)), Pass(), Move(((8, 4),))],
        oas=[OATake("main", 1)],
    )
    e = Listed(turns=[Move(((9, 4),))], block_answers=[Blocks(1, 0)])
    result = run(
        [
            ("X", "red", x_profile, (5, 4), x, (12, 12)),
            ("E", "blue", derive(load_build("l1_sample"), RULES), (8, 4), e, (1, 1)),
        ],
        attacks={"X": [1]},  # no crit: E blocks it and stays up
    )
    assert spent(result.log, "X") == [
        ("off_turn_move", 1),
        ("off_turn_move", 2),
        ("opportunity", 3),
        ("off_turn_move", 4),
    ]


@dataclass
class Grab:
    """Moves to `spot` in the first off-turn window it can, otherwise does nothing."""

    spot: Cell
    asked: list[int] = field(default_factory=list)

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        return EndTurn()

    def commitment(self, request: Commitment) -> int:
        return 0

    def blocks(self, request: BlocksRequest) -> Blocks:
        return Blocks()

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer:
        if self.spot in request.moves.destinations and request.moves.start != self.spot:
            dx = self.spot[0] - request.moves.start[0]
            dy = self.spot[1] - request.moves.start[1]
            if max(abs(dx), abs(dy)) == 1:
                return Move((self.spot,))
        return Pass()

    def avoid(self, request: AvoidOA) -> Avoid:
        return Avoid()

    def take_oa(self, request: TakeOA) -> OATake:
        return OATake()

    def ability(self, request: object) -> Pass:
        return Pass()


def test_window_order_decides_who_gets_the_square() -> None:
    """Both creatures want the square between them; whoever is asked first takes it."""
    sample = derive(load_build("l1_sample"), RULES)
    for order, winner in (("ascending_initiative", "L"), ("descending_initiative", "H")):
        rules = RULES.override({"off_turn": {"order": order}})
        result = run(
            [
                ("H", "red", sample, (4, 4), Grab((5, 4)), (12, 12)),
                ("L", "blue", sample, (6, 4), Grab((5, 4)), (1, 1)),
            ],
            rules=rules,
        )
        assert result.state.get(winner).pos == (5, 4), order


def test_no_windows_without_a_map_or_under_review_sim() -> None:
    sample = derive(load_build("l1_sample"), RULES)
    dice = Streams(3)
    entrants = [
        Entrant(cid, cid, sample, make_agent("alpha", RULES, dice.dice(f"agent:{cid}")))
        for cid in ("a", "b")
    ]
    plain = Battle(RULES, entrants, dice, seed=3).run()
    assert not [d for d in plain.decisions if d.kind == "off_turn_move"]
    sim = preset("review-sim")
    on_map = run(
        [
            ("a", "a", derive(load_build("l1_sample"), sim), (2, 2), Listed(), (12, 12)),
            ("b", "b", derive(load_build("l1_sample"), sim), (8, 2), Listed(), (1, 1)),
        ],
        rules=sim,
    )
    assert not [d for d in on_map.decisions if d.kind == "off_turn_move"]
    with_windows = run(
        [
            ("a", "a", sample, (2, 2), Listed(), (12, 12)),
            ("b", "b", sample, (8, 2), Listed(), (1, 1)),
        ]
    )
    # Two turns, each followed by a window asking both creatures once.
    assert len([d for d in with_windows.decisions if d.kind == "off_turn_move"]) == 4


@dataclass
class Pacer(Grab):
    """Steps back and forth forever in every window."""

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer:
        x, y = request.moves.start
        nxt = (x + 1, y) if (x + 1, y) in request.moves.destinations else (x - 1, y)
        return Move((nxt,))


def test_a_window_that_never_settles_raises() -> None:
    """With free off-turn movement (base 0, no escalation) nothing stops a pacer."""
    rules = RULES.override({"off_turn": {"movement_base": 0, "slope": 0}})
    sample = derive(load_build("l1_sample"), rules)
    with pytest.raises(EngineError, match="didn't settle"):
        run(
            [
                ("a", "a", sample, (2, 2), Pacer((0, 0)), (12, 12)),
                ("b", "b", sample, (8, 2), Listed(), (1, 1)),
            ],
            rules=rules,
        )
