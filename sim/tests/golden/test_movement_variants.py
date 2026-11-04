"""Movement experiment switches (design/… movement exploration): extra on-turn movement
modes (flat as written, escalating, none) and the off-turn window that restarts after each
move (the designer's "declare, tiebreak on initiative, respond" scheme)."""

from dataclasses import dataclass, field

from stamina_engine.agents.decisions import (
    Avoid,
    AvoidOA,
    BlocksRequest,
    Commitment,
    EndTurn,
    Move,
    MoveAnswer,
    OATake,
    OffTurnMove,
    Pass,
    TakeOA,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.grid.battlefield import Cell, parse_map
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.ruleset import preset
from tests.golden.test_off_turn_battles import run

RULES = preset("v0.9")


def test_extra_movement_modes_price_the_same_squares_differently() -> None:
    sample = derive(load_build("l1_sample"), RULES).main  # AGI 1: 6 free, 2 per purchase
    args = dict(
        on_turn=True,
        trackers=Trackers(),
        stamina=20,
        free_left=6,
        movement=6,
        extra_squares=sample.extra_squares_per_purchase,
        off_turn_squares=2,
        limit=14,
    )
    flat = Pricing(RULES).move_prices(**args)
    assert flat[6] == 0 and flat[8] == 1 and flat[10] == 2 and flat[12] == 3  # as written
    esc = Pricing(RULES.override({"movement": {"extra_mode": "escalating"}})).move_prices(**args)
    assert esc[8] == 1 and esc[10] == 3 and esc[12] == 6  # 1, then 2, then 3
    esc2 = Pricing(RULES.override({"movement": {"extra_mode": "escalating", "extra_slope": 2}}))
    assert esc2.move_prices(**args)[12] == 1 + 3 + 5
    none = Pricing(RULES.override({"movement": {"extra_mode": "none"}})).move_prices(**args)
    assert len(none) == 7  # free squares only
    # off-turn purchases are untouched by the on-turn mode
    off = Pricing(RULES.override({"movement": {"extra_mode": "none"}})).move_prices(
        on_turn=False, trackers=Trackers(), stamina=20, off_turn_squares=2, limit=8
    )
    assert off[2] == 1 and off[4] == 3 and off[6] == 6


@dataclass
class Chase:
    """Off-turn: step one square toward `goal` (a cell or a creature id) while it is more than
    `keep` squares away; count how many times it was asked."""

    goal: str | Cell
    keep: int = 1
    asked: list[Cell] = field(default_factory=list)

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        return EndTurn()

    def commitment(self, request: Commitment) -> int:
        return 0

    def blocks(self, request: BlocksRequest) -> Blocks:
        return Blocks()

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer:
        if request.moves is None:  # nothing affordable: still asked (abilities), so pass
            return Pass()
        me = request.moves.start
        goal = request.observation.view(self.goal).pos if isinstance(self.goal, str) else self.goal
        self.asked.append(me)
        if goal is None or abs(goal[0] - me[0]) <= self.keep:
            return Pass()
        step = (me[0] + (1 if goal[0] > me[0] else -1), me[1])
        return Move((step,)) if step in request.moves.destinations else Pass()

    def avoid(self, request: AvoidOA) -> Avoid:
        return Avoid(tuple(request.enemies))

    def take_oa(self, request: TakeOA) -> OATake:
        return OATake()

    def ability(self, request: object) -> Pass:
        return Pass()


def test_restart_after_move_lets_the_first_in_order_answer_every_move() -> None:
    """H (higher initiative) wants to stay 3 squares from L; L wants to be adjacent. Without
    restart, descending order asks H then L in each pass, so L closes and H answers in the
    next pass. With restart, every move hands the question back to H at once, so H is asked
    after each of L's steps and never after its own: a strictly alternating race."""
    sample = derive(load_build("l1_sample"), RULES)
    base = {"off_turn": {"order": "descending_initiative"}}
    for restart in (False, True):
        rules = RULES.override({"off_turn": {**base["off_turn"], "restart_after_move": restart}})
        h, lo = Chase((19, 4), keep=0), Chase("H")
        # H heads for the far edge one square at a time whenever asked; L chases H.
        result = run(
            [
                ("H", "red", sample, (6, 4), h, (12, 12)),
                ("L", "blue", sample, (4, 4), lo, (1, 1)),
            ],
            rules=rules,
            field_=parse_map("\n".join(["." * 20] * 9)),
        )
        # Both run until the escalation beats their stamina; who was asked when differs.
        order = [d.who for d in result.decisions if d.kind == "off_turn_move"]
        if restart:
            # after any L move the next question goes to H; after any H move, to H again,
            # so H is never asked twice in a row only when H itself passed
            assert order[0] == "H"
            for i in range(1, len(order)):
                if order[i - 1] == "L":
                    assert order[i] == "H"
        else:
            # plain descending: H, L, H, L ... within a pass
            assert order[:4] == ["H", "L", "H", "L"]
        assert result.state.get("H").pos[0] > 6  # H did run
