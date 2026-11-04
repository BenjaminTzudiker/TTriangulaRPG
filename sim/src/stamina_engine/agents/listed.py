"""An agent that answers from lists given in advance, one list per kind of decision. For
golden tests and worked examples: the fight goes exactly as written, or the broker refuses
an answer and says why.

When a list runs out the agent answers with the do-nothing choice: end the turn, block
nothing, pass, pay no one, decline the OA. A commitment takes the next entry of `commit`.
"""

from dataclasses import dataclass, field

from stamina_engine.agents.decisions import (
    Avoid,
    AvoidOA,
    BlocksRequest,
    Commitment,
    EndTurn,
    MoveAnswer,
    OATake,
    OffTurnMove,
    Pass,
    TakeOA,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.rules.exchange import Blocks

cites = ("Packet: Commitment", "Packet: Blocking", "Packet: Making Opportunity Attacks")


@dataclass
class Listed:
    turns: list[TurnAnswer] = field(default_factory=list)
    commit: list[int] = field(default_factory=list)
    block_answers: list[Blocks] = field(default_factory=list)
    off_turn: list[MoveAnswer] = field(default_factory=list)
    avoids: list[Avoid] = field(default_factory=list)
    oas: list[OATake] = field(default_factory=list)
    seen: list[str] = field(default_factory=list)  # each request's context, for tests

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        self.seen.append(" > ".join(request.context))
        return self.turns.pop(0) if self.turns else EndTurn()

    def commitment(self, request: Commitment) -> int:
        return self.commit.pop(0) if self.commit else 0

    def blocks(self, request: BlocksRequest) -> Blocks:
        return self.block_answers.pop(0) if self.block_answers else Blocks()

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer:
        self.seen.append(" > ".join(request.context))
        return self.off_turn.pop(0) if self.off_turn else Pass()

    def avoid(self, request: AvoidOA) -> Avoid:
        self.seen.append(" > ".join(request.context))
        return self.avoids.pop(0) if self.avoids else Avoid()

    def take_oa(self, request: TakeOA) -> OATake:
        self.seen.append(" > ".join(request.context))
        return self.oas.pop(0) if self.oas else OATake()
