"""Scripted and tactical agents on a grid: behavior on hand-built positions, legality on random
maps, determinism, and agent specs."""

import random

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from stamina_engine.agents.decisions import EndTurn, Move, TurnAnswer, TurnCommand
from stamina_engine.agents.listed import Listed
from stamina_engine.agents.scripted import ScriptedAgent, make_agent
from stamina_engine.agents.tactical import TacticalAgent
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.core.errors import ConfigError
from stamina_engine.core.rng import SeededDice, Streams
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import Moved, OpportunityProvoked, Spent
from stamina_engine.grid.battlefield import Battlefield, Cell, parse_map
from stamina_engine.grid.geometry import distance
from stamina_engine.model.build import Attributes, Build, Loadout, load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import RuleSet, preset

RULES = preset("v0.9")


class Dice:
    """Scripted initiative (to fix who goes first), seeded streams for everything else."""

    def __init__(self, initiative: list[int], seed: int = 1) -> None:
        self.initiative = ScriptedDice(initiative)
        self.streams = Streams(seed)

    def dice(self, name: str) -> ScriptedDice | SeededDice:
        return self.initiative if name == "initiative" else self.streams.dice(name)


def sample() -> CombatProfile:
    return derive(load_build("l1_sample"), RULES)


def spearman(fin: int = 1) -> CombatProfile:
    b = Build(
        f"spear{fin}",
        1,
        Attributes(STR=2, AGI=1, FIN=fin),
        (("m", Loadout(armor="medium", weapon="spear", grip="one", off_hand="shield")),),
        ("fighter",),
    )
    return derive(b, RULES)


def battle(
    field: Battlefield,
    roster: list[tuple[str, str, CombatProfile, Cell, object]],
    initiative: list[int],
    rounds: int = 1,
    rules: RuleSet = RULES,
) -> BattleResult:
    entrants = [Entrant(cid, team, p, a, "", pos) for cid, team, p, pos, a in roster]  # type: ignore[arg-type]
    return Battle(
        rules, entrants, Dice(initiative), seed=1, round_cap=rounds, check=True, field=field
    ).run()


CORRIDOR = parse_map(
    """
############
#.....######
#..........#
#.....######
############
"""
)


def test_tactical_defender_retreats_into_a_corridor() -> None:
    """Three enemies can engage it in the open; one step into the corridor only one can."""
    d = make_agent({"kind": "tactical", "commit": "fixed:2"}, RULES)
    result = battle(
        CORRIDOR,
        [
            ("D", "pc", sample(), (5, 2), d),
            ("x0", "npc", sample(), (4, 1), Listed()),
            ("x1", "npc", sample(), (4, 2), Listed()),
            ("x2", "npc", sample(), (4, 3), Listed()),
        ],
        [12, 12, 1, 1, 1, 2, 2, 2],
    )
    end = result.state.get("D").pos
    assert end is not None and end[0] >= 7 and end[1] == 2
    assert any(isinstance(e, Moved) and e.who == "D" and e.how == "off_turn" for e in result.log)


def test_spearman_keeps_its_distance() -> None:
    """From 3 squares away, a tactical spearman steps to 2 (in its reach, out of the
    sword's) and attacks from there."""
    s = make_agent({"kind": "tactical", "commit": "fixed:1"}, RULES)
    w = Listed(block_answers=[Blocks(1, 1)])
    result = battle(
        parse_map("\n".join(["." * 10] * 5)),
        [("S", "red", spearman(), (2, 2), s), ("W", "blue", sample(), (5, 2), w)],
        [12, 12, 1, 1],
    )
    attack = next(e for e in result.log if type(e).__name__ == "AttackDeclared")
    assert attack.attacker == "S"
    moves = [e for e in result.log[: result.log.index(attack)] if isinstance(e, Moved)]
    assert moves and distance(moves[-1].to, (5, 2), RULES.grid) == 2
    s_moves = [e for e in result.log if isinstance(e, Moved) and e.who == "S"]
    assert s_moves[-1].to == moves[-1].to  # and it stays there


def test_approach_detours_around_a_reach() -> None:
    """The straight line runs through a spear's reach; a path just as short goes round it."""
    a = make_agent("alpha", RULES)
    result = battle(
        parse_map("\n".join(["." * 11] * 7)),
        [
            ("A", "red", sample(), (1, 2), a),
            ("T", "blue", sample(), (8, 2), Listed()),
            ("S", "blue", spearman(), (4, 4), Listed()),
        ],
        [12, 12, 1, 1, 1, 2],
    )
    first_attack = next(e for e in result.log if type(e).__name__ == "AttackDeclared")
    before = result.log[: result.log.index(first_attack)]
    assert not any(isinstance(e, OpportunityProvoked) for e in before)
    assert [e for e in before if isinstance(e, Moved)][-1].to == (7, 1)


class Leaver(ScriptedAgent):
    """Steps straight down one square on its turn, then behaves as scripted."""

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        me = request.observation.me
        if me.free_move_left == me.gear.movement and me.pos is not None:
            return Move(((me.pos[0], me.pos[1] + 1),))
        return EndTurn()


@pytest.mark.parametrize("mode", ["worth_it", "always"])
def test_no_paying_off_an_enemy_that_cannot_oa(mode: str) -> None:
    """A FIN-0 spearman can't afford an OA at the default cap; a FIN-1 swordsman can, and its
    OA would cost the mover more than 1."""
    for enemy, pays in ((spearman(0), False), (sample(), True)):
        base = make_agent({"commit": "never", "avoid": mode}, RULES)
        assert isinstance(base, ScriptedAgent)
        leaver = Leaver(RULES, base.commit, avoid_mode=mode)
        result = battle(
            parse_map("\n".join(["." * 8] * 6)),
            [("M", "red", sample(), (2, 2), leaver), ("E", "blue", enemy, (2, 1), Listed())],
            [12, 12, 1, 1],
        )
        assert any(isinstance(e, OpportunityProvoked) for e in result.log)
        paid = [e for e in result.log if isinstance(e, Spent) and e.category == "avoid"]
        assert bool(paid) is pays, (enemy.build, mode)


# --- legality on random maps --------------------------------------------------------

SPECS = [
    "alpha",
    "chipkill",
    {"commit": "fixed:2", "avoid": "always", "oa": "never"},
    "tactical",
    {"kind": "tactical", "commit": "alpha", "target": "nearest", "retreat_engaged": 1},
]
BUILDS = ["l1_sample", "l1_duelist", "l1_heavy", "l1_greatsword", "l1_caster_dagger"]
VARIANTS = [
    {},
    {"opportunity": {"per_square_cap": True, "cap_rule": "weapon_base"}},
    {"opportunity": {"avoid_track": "off_turn", "avoid_debt": True}},
    {"movement": {"extra_squares": "one", "extra_cap": "free_movement"}},
]


@settings(max_examples=30, deadline=None)
@given(
    st.integers(0, 10**6),
    st.lists(st.text(alphabet=".....#=", min_size=8, max_size=8), min_size=7, max_size=7),
    st.integers(0, len(VARIANTS) - 1),
)
def test_engine_agents_are_always_legal(seed: int, rows: list[str], v: int) -> None:
    field = parse_map("\n".join(rows))
    rng = random.Random(seed)
    floor = [c for c in field.cells() if field.walkable(c)]
    if len(floor) < 4:
        return
    rules = RULES.override(VARIANTS[v]) if VARIANTS[v] else RULES
    spots = rng.sample(floor, 4)
    streams = Streams(seed)
    entrants = [
        Entrant(
            f"c{i}",
            "red" if i % 2 else "blue",
            derive(load_build(rng.choice(BUILDS)), rules),
            make_agent(rng.choice(SPECS), rules, streams.dice(f"agent:c{i}")),
            "",
            spots[i],
        )
        for i in range(4)
    ]
    Battle(rules, entrants, streams, seed=seed, round_cap=5, check=True, field=field).run()


def test_tactical_battles_are_deterministic() -> None:
    def once() -> str:
        streams = Streams(9)
        entrants = [
            Entrant(
                cid,
                team,
                sample(),
                make_agent("tactical", RULES, streams.dice(f"agent:{cid}")),
                "",
                pos,
            )
            for cid, team, pos in (
                ("D", "pc", (5, 2)),
                ("x0", "npc", (1, 1)),
                ("x1", "npc", (1, 2)),
                ("x2", "npc", (1, 3)),
            )
        ]
        return (
            Battle(RULES, entrants, streams, seed=9, round_cap=8, check=True, field=CORRIDOR)
            .run()
            .log_sha256()
        )

    assert once() == once()


def test_agent_specs() -> None:
    assert isinstance(make_agent("tactical", RULES), TacticalAgent)
    t = make_agent({"kind": "tactical", "commit": "fixed:2", "low_stamina": "1/2"}, RULES)
    assert isinstance(t, TacticalAgent) and t.low_stamina == pytest.approx(0.5)
    s = make_agent({"commit": "alpha", "avoid": "never", "oa": "never"}, RULES)
    assert isinstance(s, ScriptedAgent) and (s.avoid_mode, s.oa_mode) == ("never", "never")
    with pytest.raises(ConfigError, match="unknown agent fields"):
        make_agent({"commit": "alpha", "retreat_engaged": 2}, RULES)
    with pytest.raises(ConfigError, match="avoid must be"):
        make_agent({"commit": "alpha", "avoid": "sometimes"}, RULES)
    with pytest.raises(ConfigError, match="kind must be"):
        make_agent({"kind": "clever"}, RULES)
    with pytest.raises(ConfigError, match="tactical target"):
        make_agent({"kind": "tactical", "target": "biggest"}, RULES)
