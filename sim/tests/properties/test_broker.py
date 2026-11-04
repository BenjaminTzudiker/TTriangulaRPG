"""Broker: answers are validated and logged, never substituted; option counts are right."""

from dataclasses import dataclass, field

import pytest

from stamina_engine.agents.broker import Broker
from stamina_engine.agents.decisions import (
    Attack,
    BlocksRequest,
    Commitment,
    EndTurn,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.core.errors import RulesError
from stamina_engine.engine.observe import observe
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.model.state import BattleState, new_combatant
from stamina_engine.rules.block_solver import block_options
from stamina_engine.rules.exchange import Blocks, resolve
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import v0_9

RULES = v0_9()
PRICING = Pricing(RULES)


@dataclass
class Fixed:
    turn: TurnAnswer = field(default_factory=EndTurn)
    steps: int = 1
    block: Blocks = field(default_factory=Blocks)

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        return self.turn

    def commitment(self, request: Commitment) -> int:
        return self.steps

    def blocks(self, request: BlocksRequest) -> Blocks:
        return self.block


def setup() -> tuple[BattleState, TurnCommand, Commitment, BlocksRequest]:
    p = derive(load_build("l1_sample"), RULES)
    state = BattleState((new_combatant("a", "red", p), new_combatant("b", "blue", p)))
    obs_a, obs_b = observe(state, RULES, "a"), observe(state, RULES, "b")
    quotes = tuple(PRICING.melee_attack(2, k) for k in range(1, 4))
    opts = block_options(15, 0, 4, 2, 14, RULES)
    return (
        state,
        TurnCommand("a", obs_a, (), ("b",)),
        Commitment("a", obs_a, (), "b", quotes),
        BlocksRequest("b", obs_b, (), "a", 15, 0, 4, 2, 14, 0, opts.affordable, opts.nondominated),
    )


def test_legal_answers_are_logged() -> None:
    _, turn, commit, block = setup()
    broker = Broker(
        {"a": Fixed(turn=Attack("b"), steps=2), "b": Fixed(block=Blocks(2, 2))}, PRICING
    )
    assert broker.turn_command(turn) == Attack("b")
    assert broker.commitment(commit) == 2
    assert broker.blocks(block) == Blocks(2, 2)
    kinds = [(r.kind, r.option_count, r.answer, r.acted) for r in broker.records]
    assert kinds == [
        ("turn_command", 2, "attack b", True),
        ("commitment", 4, "2", True),
        ("blocks", block.affordable, "2p2g", True),
    ]


@pytest.mark.parametrize(
    "agent",
    [
        Fixed(turn=Attack("nobody")),
        Fixed(turn=Attack("a")),  # yourself
        Fixed(turn="end"),  # type: ignore[arg-type]
    ],
)
def test_illegal_turn_answers_raise(agent: Fixed) -> None:
    _, turn, _, _ = setup()
    with pytest.raises(RulesError):
        Broker({"a": agent}, PRICING).turn_command(turn)


@pytest.mark.parametrize("steps", [-1, 4, True])
def test_illegal_commitment_raises(steps: int) -> None:
    _, _, commit, _ = setup()
    with pytest.raises(RulesError):
        Broker({"a": Fixed(steps=steps)}, PRICING).commitment(commit)


@pytest.mark.parametrize("blocks", [Blocks(5, 0), Blocks(0, 15), Blocks(-1, 0)])
def test_unaffordable_blocks_raise(blocks: Blocks) -> None:
    _, _, _, block = setup()
    with pytest.raises(RulesError):
        Broker({"b": Fixed(block=blocks)}, PRICING).blocks(block)


def test_block_option_counts() -> None:
    # 2 stamina: (0,0) (0,1) (0,2) (1,0) (1,1) affordable; perfect 2 costs 3.
    opts = block_options(9, 0, 4, 2, 2, RULES)
    assert opts.affordable == 5
    # The frontier, by brute force over the same five pairs.
    by_hand = {}
    for p, g in [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]:
        by_hand[(p, g)] = (
            PRICING.blocks(p, g).total,
            resolve(9, 0, 4, 2, Blocks(p, g), RULES).injury,
        )
    frontier = [
        k
        for k, (c, i) in by_hand.items()
        if not any(c2 <= c and i2 <= i and (c2, i2) != (c, i) for c2, i2 in by_hand.values())
    ]
    assert opts.nondominated == len(frontier)


def test_prior_perfect_blocks_cost_more() -> None:
    assert PRICING.blocks(2, 1, prior_perfect=3).parts == (4, 5, 1)
    assert block_options(9, 0, 4, 2, 2, RULES, prior_perfect=3).affordable == 3


def test_observation_views() -> None:
    state, turn, _, _ = setup()
    obs = turn.observation
    assert obs.me.trackers is not None
    assert all(v.trackers is None for v in obs.others)  # only your own counters
    assert [v.id for v in obs.enemies()] == ["b"]
    assert obs.view("b").stamina == 14 and obs.view("b").stamina_exact
