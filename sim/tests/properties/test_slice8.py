"""Block-reset variants (review F6 option 2, both readings) and hidden stamina."""

from dataclasses import dataclass, field

import pytest

from stamina_engine.agents.decisions import (
    Attack,
    BlocksRequest,
    Commitment,
    EndTurn,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.agents.scripted import make_agent
from stamina_engine.core.errors import ConfigError
from stamina_engine.core.rng import Streams
from stamina_engine.engine.battle import Battle, Entrant
from stamina_engine.engine.events import AttackResolved, BlocksDeclared, Event, Spent
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import RuleSet, v0_9


@dataclass
class TwoAttacks:
    """Attacks twice a turn with one step; blocks with one perfect block every time."""

    steps: int = 1
    _attacks: int = field(default=0, init=False)
    _round: int = field(default=-1, init=False)

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        if request.observation.round != self._round:
            self._round, self._attacks = request.observation.round, 0
        if self._attacks < 2 and request.targets:
            self._attacks += 1
            return Attack(request.targets[0])
        return EndTurn()

    def commitment(self, request: Commitment) -> int:
        return 1

    def blocks(self, request: BlocksRequest) -> Blocks:
        cost = request.prior_perfect + 1  # the next perfect block's price
        return Blocks(1, 0) if request.stamina >= cost else Blocks()


def block_costs(reset: str, attackers: int) -> list[tuple[int, tuple[int, ...]]]:
    rules = v0_9().override({"blocks": {"reset": reset}}, name=reset)
    p = derive(load_build("l1_sample"), rules)
    entrants = [Entrant("d", "def", p, TwoAttacks())]
    entrants += [Entrant(f"a{i}", "att", p, TwoAttacks()) for i in range(attackers)]
    result = Battle(rules, entrants, Streams(5), seed=5, round_cap=1, check=True).run()
    blocks = [e for e in result.log if isinstance(e, BlocksDeclared) and e.defender == "d"]
    costs = [
        e for e in result.log if isinstance(e, Spent) and e.who == "d" and e.category == "block"
    ]
    return [(b.prior_perfect, c.parts) for b, c in zip(blocks, costs, strict=False)]


def test_v09_resets_every_attack() -> None:
    assert all(prior == 0 and parts == (1,) for prior, parts in block_costs("per_attack", 2))


def test_per_attacker_round_carries_within_an_attacker() -> None:
    by_attack = block_costs("per_attacker_round", 1)
    assert by_attack[:2] == [(0, (1,)), (1, (2,))]  # the attacker's second attack: 2


def test_per_round_shares_the_count() -> None:
    """Two attackers, two attacks each: one count for the round, across both attackers."""
    costs = block_costs("per_round", 2)
    assert [prior for prior, _ in costs] == list(range(len(costs)))
    assert len(costs) >= 3  # so attacks from both attackers share it
    per_attacker = block_costs("per_attacker_round", 2)
    assert [prior for prior, _ in per_attacker][:4] == [0, 1, 0, 1]


def test_bad_reset_rejected() -> None:
    with pytest.raises(ConfigError):
        v0_9().override({"blocks": {"reset": "never"}})


# --- hidden stamina ------------------------------------------------------------------


def duel(rules: RuleSet, seed: int) -> Battle:
    dice = Streams(seed)
    entrants = [
        Entrant(
            cid,
            cid,
            derive(load_build(b), rules),
            make_agent(
                {"commit": "chipkill", "target": "lowest_stamina"}, rules, dice.dice(f"agent:{cid}")
            ),
        )
        for cid, b in (("a", "l1_sample"), ("b", "l1_duelist"), ("c", "l1_heavy"))
    ]
    return Battle(rules, entrants, dice, seed=seed, check=True)


HIDDEN = v0_9().override({"information": {"stamina": "hidden"}}, name="hidden")


def test_ledger_reconstructs_hidden_stamina_exactly() -> None:
    for seed in range(15):
        battle = duel(HIDDEN, seed)
        assert battle.ledger is not None
        checked: list[Event] = []

        def compare(event: Event, battle: Battle = battle, checked: list[Event] = checked) -> None:
            assert battle.ledger is not None
            for c in battle.state.combatants:
                assert battle.ledger.estimate[c.id] == c.stamina, event
            checked.append(event)

        battle.ops.listeners.append(compare)
        battle.run()
        assert checked


def test_hidden_with_known_builds_plays_like_public() -> None:
    """Exact reconstruction means scripted agents decide the same: identical fights."""
    for seed in range(10):
        public = [e for e in duel(v0_9(), seed).run().log if isinstance(e, AttackResolved)]
        hidden = [e for e in duel(HIDDEN, seed).run().log if isinstance(e, AttackResolved)]
        assert public == hidden


def test_observations_mark_estimates() -> None:
    battle = duel(HIDDEN, 1)
    obs = battle.observe("a")
    assert obs.me.stamina_exact
    assert all(not v.stamina_exact for v in obs.others)


def test_unknown_builds_wait_for_phase_0() -> None:
    rules = v0_9().override({"information": {"stamina": "hidden", "builds": "unknown"}})
    with pytest.raises(ConfigError, match="Phase 0"):
        duel(rules, 1)
