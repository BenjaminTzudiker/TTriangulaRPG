"""Fleeing, surrendering and NPC profiles (Ledger GM-1, H-6; Review F6). The packet has no
rules for either end state; readings in the Assumptions register."""

import pytest

from stamina_engine.agents.decisions import Flee, Move, Surrender, TurnCommand
from stamina_engine.agents.listed import Listed
from stamina_engine.agents.profiles import library_profiles, load_profile
from stamina_engine.agents.scripted import Conditional, make_agent
from stamina_engine.agents.tactical import TacticalAgent
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.core.errors import ConfigError, RulesError
from stamina_engine.core.rng import Streams
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import Fled, Surrendered
from stamina_engine.experiments.metrics import fight_row
from stamina_engine.grid.battlefield import Battlefield, Cell, parse_map
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.model.state import Status
from stamina_engine.rules.ruleset import preset

RULES = preset("v0.9")
FIELD = parse_map("\n".join(["........>", ".........", "........."]))


class Dice:
    def __init__(self, n: int, seed: int = 1) -> None:
        self.faces = [12, 12] + [f for i in range(n - 1) for f in (1, 1 + i)]  # no ties
        self.streams = Streams(seed)

    def dice(self, name: str):  # type: ignore[no-untyped-def]
        return ScriptedDice(self.faces) if name == "initiative" else self.streams.dice(name)


def sample() -> CombatProfile:
    return derive(load_build("l1_sample"), RULES)


def fight(
    roster: list[tuple[str, str, CombatProfile, Cell, object]],
    rounds: int = 2,
    field: Battlefield = FIELD,
) -> BattleResult:
    entrants = [Entrant(cid, team, p, a, "", pos) for cid, team, p, pos, a in roster]  # type: ignore[arg-type]
    return Battle(
        RULES, entrants, Dice(len(roster)), seed=1, round_cap=rounds, check=True, field=field
    ).run()


def test_surrender_ends_a_side_and_takes_it_out() -> None:
    a = Listed(turns=[Surrender()])
    result = fight([("A", "red", sample(), (2, 1), a), ("B", "blue", sample(), (3, 1), Listed())])
    assert any(isinstance(e, Surrendered) for e in result.log)
    assert result.state.get("A").status is Status.SURRENDERED
    assert (result.winner, result.reason) == ("blue", "side_out")
    row = fight_row(result, 0, 0)
    assert row["surrendered:red"] == 1 and row["down:red"] == 1


def test_surrendered_creatures_are_not_targets_and_take_no_turns() -> None:
    a = Listed(turns=[Surrender()])
    b = Listed()
    c = Listed()
    fight(
        [
            ("A", "red", sample(), (2, 1), a),
            ("C", "red", sample(), (6, 2), c),
            ("B", "blue", sample(), (3, 1), b),
        ]
    )
    turns = [r for r in b.requests if isinstance(r, TurnCommand)]
    assert turns and all("A" not in r.targets for r in turns)
    assert len([r for r in a.requests if isinstance(r, TurnCommand)]) == 1


def test_flee_from_an_exit_square() -> None:
    a = Listed(turns=[Move(((8, 0),)), Flee()])
    result = fight([("A", "red", sample(), (7, 0), a), ("B", "blue", sample(), (0, 2), Listed())])
    (fled,) = [e for e in result.log if isinstance(e, Fled)]
    assert fled.frm == (8, 0)
    gone = result.state.get("A")
    assert gone.status is Status.FLED and gone.pos is None
    assert result.winner == "blue"
    assert fight_row(result, 0, 0)["fled:red"] == 1


def test_flee_only_from_an_exit() -> None:
    with pytest.raises(RulesError, match="can't flee"):
        fight(
            [
                ("A", "red", sample(), (2, 1), Listed(turns=[Flee()])),
                ("B", "blue", sample(), (5, 1), Listed()),
            ]
        )
    with pytest.raises(RulesError, match="can't surrender"):
        entrants = [
            Entrant("A", "red", sample(), Listed(turns=[Surrender()])),
            Entrant("B", "blue", sample(), Listed()),
        ]
        Battle(RULES, entrants, Dice(2), seed=1, round_cap=1).run()  # no map, no surrender


def test_profiles_load_and_configure_the_tactical_agent() -> None:
    assert {"disciplined_2step", "berserker", "cautious", "minion"} <= set(library_profiles())
    assert load_profile("cautious")["flee_below"] == "1/2"
    npc = make_agent({"kind": "npc", "profile": "disciplined_2step"}, RULES)
    assert isinstance(npc, TacticalAgent) and npc.target_mode == "focus"
    assert isinstance(npc.commit, Conditional)
    override = make_agent({"kind": "npc", "profile": "cautious", "flee_below": "1/3"}, RULES)
    assert isinstance(override, TacticalAgent) and float(override.flee_below) == pytest.approx(
        1 / 3
    )
    with pytest.raises(ConfigError, match="no NPC profile"):
        make_agent({"kind": "npc", "profile": "nope"}, RULES)


def test_conditional_commitment() -> None:
    npc = make_agent({"kind": "npc", "profile": "disciplined_2step"}, RULES)
    assert isinstance(npc, TacticalAgent)
    a = Listed()
    result = fight(
        [("N", "red", sample(), (2, 1), npc), ("T", "blue", sample(), (3, 1), a)], rounds=1
    )
    commits = [d.answer for d in result.decisions if d.who == "N" and d.kind == "commitment"]
    assert commits == ["2"]  # the target is at full stamina


def test_focus_fire_picks_the_enemy_allies_already_threaten() -> None:
    npc = make_agent({"kind": "npc", "profile": "minion"}, RULES)
    ally = Listed()
    # T1 is next to the NPC's ally; T2 isn't. Both are in the NPC's reach.
    result = fight(
        [
            ("N", "red", sample(), (4, 1), npc),
            ("M", "red", sample(), (2, 0), ally),
            ("T1", "blue", sample(), (3, 1), Listed()),
            ("T2", "blue", sample(), (5, 1), Listed()),
        ],
        rounds=1,
    )
    (first,) = [d.answer for d in result.decisions if d.who == "N" and d.kind == "turn_command"][:1]
    assert first == "attack T1"


def test_cautious_npc_flees_when_hurt() -> None:
    """At half HP or below, the cautious profile heads for the exit and leaves."""
    npc = make_agent({"kind": "npc", "profile": "cautious"}, RULES)
    hurt = sample()
    battle = Battle(
        RULES,
        [
            Entrant("N", "red", hurt, npc, "", (6, 0)),
            Entrant("E", "blue", hurt, Listed(), "", (0, 2)),
        ],
        Dice(2),
        seed=1,
        round_cap=2,
        check=True,
        field=FIELD,
    )
    n = battle.state.get("N")
    battle.ops.injure(n, 5)  # 8 HP -> 3, below half
    result = battle.run()
    assert result.state.get("N").status is Status.FLED
