"""Class cores as written (Packet: Core Abilities, Strain, Going Over Your Maximum Strain)."""

import pytest

from stamina_engine.abilities.framework import known
from stamina_engine.agents.decisions import AbilityRequest, Attack, EndTurn, UseAbility
from stamina_engine.agents.listed import Listed
from stamina_engine.core.dice import ScriptedDice
from stamina_engine.core.errors import RulesError
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import AbilityUsed, BlocksDeclared, Recovered, Spent
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.ruleset import preset

RULES = preset("v0.9")


class Dice:
    def __init__(self, faces: dict[str, list[int]]) -> None:
        self.sources = {k: ScriptedDice(v) for k, v in faces.items()}

    def dice(self, name: str) -> ScriptedDice:
        return self.sources[name]


def profile(build: str) -> CombatProfile:
    return derive(load_build(build), RULES)


def duel(
    a: Listed, b: Listed, a_build: str, b_build: str, attacks: dict[str, list[int]], rounds: int = 1
) -> BattleResult:
    faces = {"initiative": [12, 12, 1, 1], "dying": [6] * 10}
    faces.update({f"attack:{k}": v for k, v in attacks.items()})
    entrants = [Entrant("A", "A", profile(a_build), a), Entrant("B", "B", profile(b_build), b)]
    return Battle(RULES, entrants, Dice(faces), seed=0, round_cap=rounds, check=True).run()


def test_builds_bring_their_core() -> None:
    assert profile("l1_sample").abilities == ("fighter_core",)
    assert profile("l1_barbarian").abilities == ("barbarian_core",)
    assert known("monk_core").strain == 1 and known("fighter_core").strain == 3


def test_strain_example() -> None:
    """Max strain 8, at 10, a spell for 5 stamina and 2 strain: 5 + 4 = 9 stamina."""
    q = Pricing(RULES).strain_ability(5, 2, Trackers(strain=10), 8)
    assert q.total == 9


def test_fighter_core_before_blocks() -> None:
    """B spent stamina on its own attack first; A's attack on it is rolled, and before
    blocking B uses the Fighter core: it recovers its normal recovery for 3 strain."""
    a = Listed(turns=[Attack("B")], commit=[2], block_answers=[Blocks(3, 0)])
    b = Listed(
        turns=[Attack("A")],
        commit=[3],
        uses=[UseAbility("fighter_core")],
        block_answers=[Blocks(2, 1)],
    )
    entrants = [
        Entrant("B", "B", profile("l1_sample"), b),
        Entrant("A", "A", profile("l1_heavy"), a),
    ]
    faces = {
        "initiative": [12, 12, 1, 1],
        "attack:B": [1, 1, 1],
        "attack:A": [3, 3],
        "dying": [6] * 10,
    }
    result = Battle(RULES, entrants, Dice(faces), seed=0, round_cap=1, check=True).run()
    asked = [r for r in b.requests if isinstance(r, AbilityRequest)]
    rolled = [e for e in result.log if type(e).__name__ == "AttackRolled" and e.attacker == "A"]
    assert asked and asked[0].window == "before_blocks"
    assert asked[0].facts["damage"] == rolled[0].total
    used = [e for e in result.log if isinstance(e, AbilityUsed)]
    assert [(u.who, u.ability, u.strain_after) for u in used] == [("B", "fighter_core", 3)]
    i = result.log.index(used[0])
    assert (
        isinstance(result.log[i + 1], Recovered)
        and result.log[i + 1].amount == profile("l1_sample").recovery
    )
    assert isinstance(result.log[i + 2], BlocksDeclared)


def test_fighter_core_recovers_and_overage_costs_stamina() -> None:
    """Three uses at L1 (max strain 6): the third takes strain to 9, 3 over: 3 stamina."""
    a = Listed(
        turns=[
            Attack("B"),
            UseAbility("fighter_core"),
            UseAbility("fighter_core"),
            UseAbility("fighter_core"),
            EndTurn(),
        ],
        commit=[4],
    )
    result = duel(
        a, Listed(block_answers=[Blocks(4, 0)]), "l1_sample", "l1_heavy", {"A": [1, 1, 1, 1]}
    )
    used = [e for e in result.log if isinstance(e, AbilityUsed)]
    assert [u.strain_after for u in used] == [3, 6, 9]
    paid = [
        e.amount
        for e in result.log
        if isinstance(e, Spent) and e.category == "ability:fighter_core"
    ]
    assert paid == [3]  # only the third use goes over
    recovered = [e for e in result.log if isinstance(e, Recovered) and e.who == "A"]
    assert len(recovered) >= 3


def test_barbarian_refunds_its_biggest_step() -> None:
    a = Listed(
        turns=[Attack("B"), UseAbility("barbarian_core"), UseAbility("barbarian_core"), EndTurn()],
        commit=[3],
    )
    result = duel(
        a, Listed(block_answers=[Blocks(3, 0)]), "l1_barbarian", "l1_heavy", {"A": [1, 1, 1]}
    )
    gained = [e.amount for e in result.log if isinstance(e, Recovered) and e.who == "A"]
    assert gained[:2] == [4, 3]  # steps cost 2, 3, 4: the 4, then the 3


def test_monk_blocks_without_escalation() -> None:
    a = Listed(turns=[Attack("B")], commit=[3])
    b = Listed(uses=[UseAbility("monk_core")], block_answers=[Blocks(4, 0)])
    result = duel(a, b, "l1_sample", "l1_monk", {"A": [8, 8, 8]})
    blocks = [
        e for e in result.log if isinstance(e, Spent) and e.who == "B" and e.category == "block"
    ]
    assert blocks[0].parts == (1, 1, 1, 1)
    assert any(isinstance(e, BlocksDeclared) for e in result.log)


def test_unknown_or_unusable_abilities_are_refused() -> None:
    a = Listed(turns=[UseAbility("monk_core")])
    with pytest.raises(RulesError, match="can't use 'monk_core'"):
        duel(a, Listed(), "l1_sample", "l1_sample", {})
