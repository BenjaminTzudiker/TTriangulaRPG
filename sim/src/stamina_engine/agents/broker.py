"""The broker routes every decision to its creature's agent, refuses illegal answers, and
logs each decision. It never substitutes an answer (ground rule 5)."""

from collections.abc import Mapping

from stamina_engine.agents.decisions import (
    Agent,
    Attack,
    BlocksRequest,
    Commitment,
    DecisionRecord,
    EndTurn,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.core.errors import RulesError
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Pricing

cites = ("Packet: Commitment", "Packet: Blocking", "Review F11")


class Broker:
    def __init__(self, agents: Mapping[str, Agent], pricing: Pricing) -> None:
        self.agents = agents
        self.pricing = pricing
        self.records: list[DecisionRecord] = []

    def turn_command(self, req: TurnCommand) -> TurnAnswer:
        answer = self.agents[req.who].turn_command(req)
        if isinstance(answer, Attack):
            if answer.target not in req.targets:
                raise RulesError(f"{req.who} can't attack {answer.target}; options {req.targets}")
            text, acted = f"attack {answer.target}", True
        elif isinstance(answer, EndTurn):
            text, acted = "end turn", False
        else:
            raise RulesError(f"{req.who} gave {answer!r} to a TurnCommand")
        self._record(
            req.observation.round,
            req.who,
            "turn_command",
            req.option_count,
            None,
            text,
            acted,
            req.context,
        )
        return answer

    def commitment(self, req: Commitment) -> int:
        steps = self.agents[req.who].commitment(req)
        if not isinstance(steps, int) or isinstance(steps, bool) or not 0 <= steps <= req.max_steps:
            raise RulesError(f"{req.who} committed {steps!r}; options 0..{req.max_steps}")
        self._record(
            req.observation.round,
            req.who,
            "commitment",
            req.option_count,
            None,
            str(steps),
            steps > 0,
            req.context,
        )
        return steps

    def blocks(self, req: BlocksRequest) -> Blocks:
        answer = self.agents[req.who].blocks(req)
        if not isinstance(answer, Blocks) or answer.perfect < 0 or answer.grazing < 0:
            raise RulesError(f"{req.who} gave {answer!r} to a Blocks request")
        cost = self.pricing.blocks(answer.perfect, answer.grazing, prior_perfect=req.prior_perfect)
        if cost.total > req.stamina:
            raise RulesError(f"{req.who}'s blocks cost {cost.total}, has {req.stamina}")
        self._record(
            req.observation.round,
            req.who,
            "blocks",
            req.option_count,
            req.nondominated,
            f"{answer.perfect}p{answer.grazing}g",
            answer.count > 0,
            req.context,
        )
        return answer

    def _record(
        self,
        round_: int,
        who: str,
        kind: str,
        options: int,
        nondominated: int | None,
        answer: str,
        acted: bool,
        context: tuple[str, ...],
    ) -> None:
        self.records.append(
            DecisionRecord(round_, who, kind, options, nondominated, answer, acted, context)
        )
