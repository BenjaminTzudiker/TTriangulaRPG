"""The broker routes every decision to its creature's agent, refuses illegal answers, and
logs each decision. It never substitutes an answer (ground rule 5)."""

from collections.abc import Mapping

from stamina_engine.agents.decisions import (
    Agent,
    AimRequest,
    Attack,
    Avoid,
    AvoidOA,
    BlocksRequest,
    Commitment,
    DecisionRecord,
    DiveRequest,
    Draw,
    DrawOption,
    EndTurn,
    Flee,
    Move,
    MoveAnswer,
    MoveOptions,
    OATake,
    OffTurnMove,
    Pass,
    Shoot,
    Surrender,
    TakeOA,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.core.errors import RulesError
from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.grid.geometry import neighbours
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Pricing

cites = (
    "Packet: Commitment",
    "Packet: Blocking",
    "Packet: On-Turn Movement",
    "Packet: Off-Turn Movement",
    "Packet: Avoiding Opportunity Attacks",
    "Packet: Making Opportunity Attacks",
    "Review F11",
)


def path_text(path: tuple[Cell, ...]) -> str:
    return "move " + " ".join(f"{x},{y}" for x, y in path)


class Broker:
    def __init__(self, agents: Mapping[str, Agent], pricing: Pricing) -> None:
        self.agents = agents
        self.pricing = pricing
        self.records: list[DecisionRecord] = []

    def check_path(
        self, who: str, field: Battlefield | None, moves: MoveOptions | None, path: object
    ) -> None:
        """A path must be legal step by step, end on a destination, and fit max_squares."""
        if moves is None or field is None:
            raise RulesError(f"{who} can't move now")
        if not isinstance(path, tuple) or not path:
            raise RulesError(f"{who} gave an empty or malformed path {path!r}")
        if len(path) > moves.max_squares:
            raise RulesError(
                f"{who}'s path is {len(path)} squares; it can afford {moves.max_squares}"
            )
        rule = self.pricing.rules.grid
        prev = moves.start
        for cell in path:
            if cell not in neighbours(field, prev, rule) or cell in moves.no_entry:
                raise RulesError(f"{who} can't step from {prev} to {cell}")
            prev = cell
        if prev not in moves.destinations:
            raise RulesError(f"{who} can't end a move on {prev}")

    def turn_command(self, req: TurnCommand) -> TurnAnswer:
        answer = self.agents[req.who].turn_command(req)
        if isinstance(answer, Attack):
            if answer.target not in req.targets:
                raise RulesError(f"{req.who} can't attack {answer.target}; options {req.targets}")
            text, acted = f"attack {answer.target}", True
        elif isinstance(answer, Move):
            self.check_path(req.who, req.observation.field, req.moves, answer.path)
            text, acted = path_text(answer.path), True
        elif isinstance(answer, Shoot):
            if answer.target not in req.shots:
                raise RulesError(f"{req.who} can't shoot {answer.target}; options {req.shots}")
            text, acted = f"shoot {answer.target}", True
        elif isinstance(answer, Draw):
            self._check_draw(req.who, req.draws, answer)
            text, acted = f"draw {answer.loadout}", True
        elif isinstance(answer, Flee):
            if not req.can_flee:
                raise RulesError(f"{req.who} can't flee from here")
            text, acted = "flee", True
        elif isinstance(answer, Surrender):
            if not req.can_surrender:
                raise RulesError(f"{req.who} can't surrender here")
            text, acted = "surrender", True
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
        cost = self.pricing.blocks(
            answer.perfect, answer.grazing, prior_perfect=req.prior_perfect, ranged=req.ranged
        )
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

    def _check_draw(self, who: str, draws: tuple[DrawOption, ...], answer: Draw) -> None:
        if answer.loadout not in {d.loadout for d in draws}:
            raise RulesError(
                f"{who} can't draw {answer.loadout!r} now; options {[d.loadout for d in draws]}"
            )

    def off_turn_move(self, req: OffTurnMove) -> MoveAnswer:
        answer = self.agents[req.who].off_turn_move(req)
        if isinstance(answer, Move):
            self.check_path(req.who, req.observation.field, req.moves, answer.path)
            text, acted = path_text(answer.path), True
        elif isinstance(answer, Draw):
            self._check_draw(req.who, req.draws, answer)
            text, acted = f"draw {answer.loadout}", True
        elif isinstance(answer, Pass):
            text, acted = "pass", False
        else:
            raise RulesError(f"{req.who} gave {answer!r} to an off-turn move request")
        self._record(
            req.observation.round,
            req.who,
            "off_turn_move",
            req.option_count,
            None,
            text,
            acted,
            req.context,
        )
        return answer

    def avoid(self, req: AvoidOA) -> Avoid:
        answer = self.agents[req.who].avoid(req)
        if not isinstance(answer, Avoid) or not isinstance(answer.enemies, tuple):
            raise RulesError(f"{req.who} gave {answer!r} to an avoid request")
        if len(set(answer.enemies)) != len(answer.enemies) or not set(answer.enemies) <= set(
            req.enemies
        ):
            raise RulesError(f"{req.who} can't pay off {answer.enemies}; options {req.enemies}")
        ordered = tuple(e for e in req.enemies if e in answer.enemies)
        if ordered != answer.enemies:
            raise RulesError(f"{req.who}: list enemies in the request's order, {req.enemies}")
        if answer.enemies:
            caps = [req.caps[req.enemies.index(e)] for e in answer.enemies]
            quote = self.pricing.avoid_opportunity(
                len(caps), caps=caps, trackers=req.trackers, on_turn=req.on_turn
            )
            if quote.total > req.stamina and not self.pricing.rules.opportunity.allows_debt():
                raise RulesError(f"{req.who} can't pay {quote.total} to avoid; has {req.stamina}")
        self._record(
            req.observation.round,
            req.who,
            "avoid",
            req.option_count,
            None,
            "avoid " + ",".join(answer.enemies) if answer.enemies else "avoid none",
            bool(answer.enemies),
            req.context,
        )
        return answer

    def take_oa(self, req: TakeOA) -> OATake:
        answer = self.agents[req.who].take_oa(req)
        if not isinstance(answer, OATake) or isinstance(answer.steps, bool):
            raise RulesError(f"{req.who} gave {answer!r} to an OA request")
        if answer.steps:
            option = next((o for o in req.options if o.weapon == answer.weapon), None)
            if option is None or not 0 < answer.steps <= len(option.quotes):
                raise RulesError(f"{req.who} can't take {answer.steps} steps with {answer.weapon}")
        elif answer.steps != 0:
            raise RulesError(f"{req.who} gave {answer.steps} steps")
        self._record(
            req.observation.round,
            req.who,
            "take_oa",
            req.option_count,
            None,
            f"oa {answer.weapon} {answer.steps}" if answer.steps else "decline",
            answer.steps > 0,
            req.context,
        )
        return answer

    def aim(self, req: AimRequest) -> int:
        aims = self.agents[req.who].aim(req)
        if not isinstance(aims, int) or isinstance(aims, bool) or not 0 <= aims <= req.max_aims:
            raise RulesError(f"{req.who} aimed {aims!r}; options 0..{req.max_aims}")
        self._record(
            req.observation.round,
            req.who,
            "aim",
            req.option_count,
            None,
            str(aims),
            True,
            req.context,
        )
        return aims

    def dive(self, req: DiveRequest) -> MoveAnswer:
        answer = self.agents[req.who].dive(req)
        if isinstance(answer, Move):
            self.check_path(req.who, req.observation.field, req.moves, answer.path)
            text, acted = path_text(answer.path), True
        elif isinstance(answer, Pass):
            text, acted = "stay", False
        else:
            raise RulesError(f"{req.who} gave {answer!r} to a dive request")
        self._record(
            req.observation.round,
            req.who,
            "dive",
            req.option_count,
            None,
            text,
            acted,
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
