"""Battle properties: determinism, ending mid-turn, invariants over random fights."""

from hypothesis import given, settings
from hypothesis import strategies as st

from stamina_engine.agents.decisions import (
    Attack,
    BlocksRequest,
    Commitment,
    EndTurn,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.core.rng import SharedStream, Streams
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import BattleEnded, Event, Recovered, TurnStarted
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.block_solver import best_block
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import RuleSet, review_candidate, review_sim, v0_9


class AllIn:
    """One all-in attack per turn on the first target; blocks with the solver."""

    def __init__(self, rules: RuleSet) -> None:
        self.rules = rules

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        me = request.observation.me
        assert me.trackers is not None
        if request.targets and me.trackers.actions_this_turn == 0:
            return Attack(request.targets[0])
        return EndTurn()

    def commitment(self, request: Commitment) -> int:
        return request.max_steps

    def blocks(self, request: BlocksRequest) -> Blocks:
        me = request.observation.me
        return best_block(
            request.damage,
            request.crit_dice,
            request.defense,
            request.armor,
            request.stamina,
            me.hp,
            self.rules,
            prior_perfect=request.prior_perfect,
        ).blocks


def fight(
    rules: RuleSet,
    seed: int,
    builds: tuple[str, ...] = ("l1_sample", "l1_sample"),
    lockstep: bool = False,
) -> BattleResult:
    entrants = [
        Entrant(f"c{i}", f"t{i % 2}", derive(load_build(b), rules), AllIn(rules))
        for i, b in enumerate(builds)
    ]
    dice = SharedStream(seed) if lockstep else Streams(seed)
    return Battle(rules, entrants, dice, seed=seed, check=True).run()


def test_same_seed_same_log() -> None:
    for lockstep in (False, True):
        a, b = fight(v0_9(), 11, lockstep=lockstep), fight(v0_9(), 11, lockstep=lockstep)
        assert a.log_sha256() == b.log_sha256()
        assert a.log_sha256() != fight(v0_9(), 12, lockstep=lockstep).log_sha256()


def test_fight_ends_mid_turn() -> None:
    for seed in range(40):
        result = fight(v0_9(), seed)
        assert isinstance(result.log[-1], BattleEnded)
        if result.reason == "side_out":
            # Nothing happens after the injury that ended it: the attacker doesn't recover.
            tail: list[Event] = []
            for e in reversed(result.log[:-1]):
                if isinstance(e, TurnStarted):
                    break
                tail.append(e)
            assert not any(isinstance(e, Recovered) for e in tail)
            losers = [c for c in result.state.combatants if c.team != result.winner]
            assert all(not c.active for c in losers)


@settings(max_examples=60, deadline=None)
@given(
    st.sampled_from([v0_9(), review_sim(), review_candidate()]),
    st.integers(0, 10_000),
    st.lists(
        st.sampled_from(
            ["l1_sample", "l1_duelist", "l1_heavy", "l1_greatsword", "l30_sample", "l30_duelist"]
        ),
        min_size=2,
        max_size=4,
    ),
)
def test_random_fights_keep_invariants(rules: RuleSet, seed: int, builds: list[str]) -> None:
    result = fight(rules, seed, tuple(builds))  # check=True validates after every op
    assert result.rounds <= 30
    assert result.reason in ("side_out", "round_cap")
