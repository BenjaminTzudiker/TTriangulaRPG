"""Off-turn windows (Packet: Starting Combat and Turn Structure step 3, Off-Turn Movement).

After any creature's turn ends, including its own and an incapacitated creature's dying-roll
turn, anyone may buy off-turn movement (readings in the Assumptions register):
- every active creature is asked, in off_turn.order over initiative positions (lowest
  initiative first as written by default), whether to move or pass;
- a creature with nowhere it can reach and afford isn't asked;
- with repeat_until_all_pass, passes repeat until one in which nobody moves, and a creature
  that passed may move in a later pass;
- each move uses off-turn purchases on the mover's escalation track and provokes OAs like
  any other move.
"""

from stamina_engine.agents.decisions import Move, OffTurnMove
from stamina_engine.core.errors import EngineError
from stamina_engine.engine.battle import Battle
from stamina_engine.engine.procedures.movement import move, move_options
from stamina_engine.model.state import CombatantState

cites = (
    "Packet: Starting Combat and Turn Structure",
    "Packet: Off-Turn Movement",
    "Packet: Off-Turn Escalation",
    "Ledger MV-2",
    "Ledger MV-4",
    "Review F14",
)

MAX_PASSES = 100  # off-turn costs escalate, so a window settles long before this


def window_order(b: Battle) -> tuple[str, ...]:
    order = b.state.order
    if b.rules.off_turn.order_mode() == "ascending_initiative":
        return tuple(reversed(order))
    return order


def off_turn_window(b: Battle, ended: CombatantState) -> None:
    if b.field is None or b.outcome is not None or not b.rules.off_turn.windows_open():
        return
    with b.context.frame(f"off-turn after {ended.id}"):
        for _ in range(MAX_PASSES):
            moved = False
            for cid in window_order(b):
                c = b.state.get(cid)
                if not c.active:
                    continue
                options = move_options(b, c, on_turn=False)
                if options is None:
                    continue
                answer = b.broker.off_turn_move(
                    OffTurnMove(c.id, b.observe(c.id), b.context.path(), options)
                )
                if isinstance(answer, Move):
                    move(b, c, answer.path, on_turn=False)
                    moved = True
                if b.outcome is not None:
                    return
            if not moved or not b.rules.off_turn.repeats():
                return
        raise EngineError(
            f"the off-turn window after {ended.id} didn't settle in {MAX_PASSES} passes"
        )
