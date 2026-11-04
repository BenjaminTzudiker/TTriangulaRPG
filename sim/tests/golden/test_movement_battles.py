"""Movement and opportunity attacks played as battles, with scripted dice and answers.

Packet: Triggers, Avoiding Opportunity Attacks, Making Opportunity Attacks, On-Turn
Movement; Review F9. Readings C6-C9 and C14-C18 in the Assumptions register.
"""

from dataclasses import dataclass

import pytest

from stamina_engine.agents.decisions import Attack, Avoid, Move, OATake
from stamina_engine.agents.listed import Listed
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.core.errors import RulesError
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import (
    DebtPaid,
    Event,
    Moved,
    OpportunityDeclared,
    OpportunityProvoked,
    Recovered,
    Spent,
)
from stamina_engine.grid.battlefield import Cell, parse_map
from stamina_engine.model.build import Attributes, Build, Loadout, load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import RuleSet, preset

RULES = preset("v0.9")
OPEN = parse_map("\n".join(["........"] * 8))


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources[name]


@dataclass
class Who:
    id: str
    team: str
    profile: CombatProfile
    pos: Cell
    agent: Listed
    initiative: tuple[int, int]  # its 2d12 faces


def sample(rules: RuleSet = RULES) -> CombatProfile:
    return derive(load_build("l1_sample"), rules)


def spearman(fin: int) -> CombatProfile:
    build = Build(
        f"spear{fin}",
        1,
        Attributes(STR=2, AGI=1, FIN=fin),
        (("m", Loadout(armor="medium", weapon="spear", grip="one", off_hand="shield")),),
        ("fighter",),
    )
    return derive(build, RULES)


def fight(
    roster: list[Who],
    attacks: dict[str, list[int]] | None = None,
    rules: RuleSet = RULES,
    rounds: int = 1,
) -> BattleResult:
    faces = {"initiative": [f for w in roster for f in w.initiative], "dying": [6] * 10}
    faces.update({f"attack:{k}": v for k, v in (attacks or {}).items()})
    entrants = [Entrant(w.id, w.team, w.profile, w.agent, "", w.pos) for w in roster]
    return Battle(
        rules, entrants, Dice(faces), seed=0, round_cap=rounds, check=True, field=OPEN
    ).run()


def spent(log: tuple[Event, ...], who: str, category: str) -> list[Spent]:
    return [e for e in log if isinstance(e, Spent) and e.who == who and e.category == category]


def kinds(result: BattleResult, kind: str) -> list[str]:
    return [d.who for d in result.decisions if d.kind == kind]


def test_avoiding_opportunity_attacks_example() -> None:
    """Leave a square threatened by A and B: 2. The next, threatened only by C: 1. The next,
    also threatened by C: 1 more, though C was already paid once."""
    mover = Listed(
        turns=[Move(((3, 2), (4, 2), (5, 2)))],
        avoids=[Avoid(("B", "A")), Avoid(("C",)), Avoid(("C",))],
    )
    result = fight(
        [
            Who("M", "red", sample(), (2, 2), mover, (12, 12)),
            Who("A", "blue", sample(), (1, 1), Listed(), (2, 2)),
            Who("B", "blue", sample(), (1, 3), Listed(), (1, 2)),
            Who("C", "blue", sample(), (4, 3), Listed(), (1, 1)),
        ]
    )
    paid = spent(result.log, "M", "avoid")
    assert [s.amount for s in paid] == [2, 1, 1]
    provoked = [e.enemies for e in result.log if isinstance(e, OpportunityProvoked)]
    assert provoked == [("B", "A"), ("C",), ("C",)]  # lowest initiative asked first
    assert result.state.get("M").pos == (5, 2)
    assert not kinds(result, "take_oa")  # everyone was paid off


def test_triggers() -> None:
    """Entering reach doesn't provoke; moving sideways within reach and leaving it do."""
    mover = Listed(turns=[Move(((4, 5),)), Move(((4, 4),)), Move(((3, 3),))])
    result = fight(
        [
            Who("M", "red", sample(), (3, 5), mover, (12, 12)),
            Who("E", "blue", sample(), (5, 5), Listed(), (1, 1)),
        ]
    )
    squares = [e.square for e in result.log if isinstance(e, OpportunityProvoked)]
    assert squares == [(4, 5), (4, 4)]
    assert kinds(result, "take_oa") == ["E", "E"]  # offered both times; declined both


def test_stepping_closer_to_a_spear_provokes() -> None:
    mover = Listed(turns=[Move(((5, 2),)), Move(((5, 1),))])
    result = fight(
        [
            Who("M", "red", sample(), (5, 3), mover, (12, 12)),
            Who("S", "blue", spearman(1), (5, 0), Listed(), (1, 1)),
        ]
    )
    assert [e.square for e in result.log if isinstance(e, OpportunityProvoked)] == [(5, 2)]


def test_f9_fin_0_spearman_can_never_make_an_oa() -> None:
    """Review F9: the default cap of 1 can't pay a base-2 weapon. With FIN 1 (cap 2) the
    spearman gets one OA; the next would cost 3."""
    path = Move(((5, 2), (5, 3), (5, 4)))
    weak = fight(
        [
            Who("M", "red", sample(), (5, 1), Listed(turns=[path]), (12, 12)),
            Who("S", "blue", spearman(0), (5, 0), Listed(), (1, 1)),
        ]
    )
    assert len([e for e in weak.log if isinstance(e, OpportunityProvoked)]) == 2
    assert not kinds(weak, "take_oa")
    able = fight(
        [
            Who("M", "red", sample(), (5, 1), Listed(turns=[path]), (12, 12)),
            Who("S", "blue", spearman(1), (5, 0), Listed(oas=[OATake("main", 1)]), (1, 1)),
        ],
        attacks={"S": [4]},
    )
    assert kinds(able, "take_oa") == ["S"]
    (oa,) = spent(able.log, "S", "opportunity")
    assert (oa.amount, oa.track) == (2, "off_turn")
    assert able.state.get("M").pos == (5, 4)


def test_oa_after_attacking_on_your_own_turn() -> None:
    """An OA's steps go on the off-turn track, not the surcharge: after a 2-step attack on
    its turn, T's OA still costs base 2."""
    t = Listed(turns=[Attack("M")], commit=[2], oas=[OATake("main", 1)])
    m = Listed(turns=[Move(((1, 4),))], block_answers=[Blocks(1, 1), Blocks(1, 0)])
    result = fight(
        [
            Who("T", "blue", sample(), (3, 4), t, (12, 12)),
            Who("M", "red", sample(), (2, 4), m, (1, 1)),
        ],
        attacks={"T": [3, 3, 2]},
    )
    assert [s.amount for s in spent(result.log, "T", "attack")] == [5]
    (oa,) = spent(result.log, "T", "opportunity")
    assert (oa.amount, oa.parts, oa.track) == (2, (2,), "off_turn")
    assert any(isinstance(e, OpportunityDeclared) for e in result.log)


def test_mover_downed_by_an_oa_stops_where_it_was() -> None:
    """The first OA (lowest initiative first) drops the mover: it stays in the square it was
    leaving, the other enemy isn't asked, and the fight ends."""
    caster = derive(load_build("l1_caster_unarmed"), RULES)
    result = fight(
        [
            Who("M", "red", caster, (3, 3), Listed(turns=[Move(((2, 3), (1, 3)))]), (12, 12)),
            Who("H", "blue", sample(), (4, 3), Listed(oas=[OATake("main", 1)]), (6, 6)),
            Who("L", "blue", sample(), (4, 4), Listed(oas=[OATake("main", 1)]), (1, 1)),
        ],
        attacks={"L": [8]},
    )
    assert kinds(result, "take_oa") == ["L"]
    m = result.state.get("M")
    assert m.pos == (3, 3) and not m.active
    assert not any(isinstance(e, Moved) for e in result.log)
    assert result.reason == "side_out" and result.winner == "blue"


def test_extra_movement_on_your_turn() -> None:
    """Movement 6, then purchases of 2 squares at 1 stamina, paid when the move is declared;
    not an action and no off-turn cost."""
    path = tuple((x, 0) for x in range(1, 8)) + ((7, 1),)
    result = fight(
        [
            Who("M", "red", sample(), (0, 0), Listed(turns=[Move(path)]), (12, 12)),
            Who("E", "blue", sample(), (0, 7), Listed(), (1, 1)),
        ]
    )
    hows = [e.how for e in result.log if isinstance(e, Moved)]
    assert hows == ["free"] * 6 + ["extra"] * 2
    (bought,) = spent(result.log, "M", "extra_move")
    assert (bought.amount, bought.track) == (1, "extra_move")
    i = result.log.index(bought)
    assert not any(isinstance(e, Moved) for e in result.log[:i])  # paid before the first step


def test_leftover_squares() -> None:
    """A purchase's unused square is kept for the turn (C7), or lost under leftover = move."""
    turns = [Move(tuple((x, 0) for x in range(1, 8))), Move(((7, 1),))]
    for leftover, purchases in (("turn", 1), ("move", 2)):
        rules = RULES.override({"movement": {"leftover": leftover}})
        result = fight(
            [
                Who("M", "red", sample(rules), (0, 0), Listed(turns=list(turns)), (12, 12)),
                Who("E", "blue", sample(rules), (0, 7), Listed(), (1, 1)),
            ],
            rules=rules,
        )
        assert len(spent(result.log, "M", "extra_move")) == purchases, leftover


def test_avoidance_debt() -> None:
    """At 0 stamina the mover can't avoid as written (so it isn't asked); under avoid_debt it
    pays from its next recovery."""

    def roster(rules: RuleSet) -> list[Who]:
        m = Listed(turns=[Attack("E"), Move(((1, 2),))], commit=[4], avoids=[Avoid(("E",))])
        e = Listed(block_answers=[Blocks(2, 2)])
        return [
            Who("M", "red", sample(rules), (2, 2), m, (12, 12)),
            Who("E", "blue", sample(rules), (3, 2), e, (1, 1)),
        ]

    plain = fight(roster(RULES), attacks={"M": [1, 1, 1, 1]})
    assert not kinds(plain, "avoid") and kinds(plain, "take_oa") == ["E"]
    rules = RULES.override({"opportunity": {"avoid_debt": True}})
    owed = fight(roster(rules), attacks={"M": [1, 1, 1, 1]}, rules=rules)
    assert kinds(owed, "avoid") == ["M"] and not kinds(owed, "take_oa")
    (paid,) = [e for e in owed.log if isinstance(e, DebtPaid)]
    rec = [e for e in owed.log if isinstance(e, Recovered) and e.who == "M"][0]
    assert paid.amount == 1 and rec.amount == sample().recovery - 1


@pytest.mark.parametrize(
    ("answer", "message"),
    [
        # Movement 6 + 14 stamina of 2-square purchases is 34 squares; back and forth for 36.
        (Move(((1, 0), (0, 0)) * 18), "afford"),
        (Move(((2, 0),)), "can't step"),  # not adjacent
        (Move(((1, 1),)), "can't step"),  # through the enemy's square
        (Move(((0, 1),)), "can't end"),  # onto the ally
        (Move(()), "empty"),
    ],
)
def test_broker_refuses_illegal_paths(answer: Move, message: str) -> None:
    with pytest.raises(RulesError, match=message):
        fight(
            [
                Who("M", "red", sample(), (0, 0), Listed(turns=[answer]), (12, 12)),
                Who("A", "red", sample(), (0, 1), Listed(), (2, 2)),
                Who("E", "blue", sample(), (1, 1), Listed(), (1, 1)),
            ]
        )


def test_broker_refuses_illegal_avoid_and_oa_answers() -> None:
    def run(avoids: list[Avoid], oas: list[OATake]) -> None:
        fight(
            [
                Who(
                    "M",
                    "red",
                    sample(),
                    (3, 3),
                    Listed(turns=[Move(((2, 3),))], avoids=avoids),
                    (12, 12),
                ),
                Who("E", "blue", sample(), (4, 3), Listed(oas=oas), (1, 1)),
            ],
            attacks={"E": [1, 1]},
        )

    with pytest.raises(RulesError, match="can't pay off"):
        run([Avoid(("X",))], [])
    with pytest.raises(RulesError, match="can't take 2 steps"):
        run([], [OATake("main", 2)])
    with pytest.raises(RulesError, match="can't take 1 steps with off_hand"):
        run([], [OATake("off_hand", 1)])
    with pytest.raises(RulesError, match="can't move now"):
        profile = sample()
        entrants = [
            Entrant("M", "red", profile, Listed(turns=[Move(((1, 0),))])),
            Entrant("E", "blue", profile, Listed()),
        ]
        dice = Dice({"initiative": [12, 12, 1, 1]})
        Battle(RULES, entrants, dice, seed=0, round_cap=1).run()  # all-adjacent: no squares


def test_per_square_cap_pools_over_a_move() -> None:
    """The packet's optional rule (C19): a FIN-0 spearman's cap builds up 1 per square the
    mover leaves within reach, so it can't attack at the first square but can for 2 at the
    second."""
    rules = RULES.override({"opportunity": {"per_square_cap": True}})
    s0 = Build(
        "spear0",
        1,
        Attributes(STR=2, AGI=1, FIN=0),
        (("m", Loadout(armor="medium", weapon="spear", grip="one", off_hand="shield")),),
        ("fighter",),
    )
    result = fight(
        [
            Who(
                "M", "red", sample(rules), (5, 1), Listed(turns=[Move(((5, 2), (5, 3)))]), (12, 12)
            ),
            Who("S", "blue", derive(s0, rules), (5, 0), Listed(oas=[OATake("main", 1)]), (1, 1)),
        ],
        attacks={"S": [4]},
        rules=rules,
    )
    assert kinds(result, "take_oa") == ["S"]
    (oa,) = spent(result.log, "S", "opportunity")
    assert oa.amount == 2
    declared = [e for e in result.log if isinstance(e, OpportunityDeclared)]
    provoked = [e for e in result.log if isinstance(e, OpportunityProvoked)]
    assert result.log.index(declared[0]) > result.log.index(provoked[1])  # at the second square
