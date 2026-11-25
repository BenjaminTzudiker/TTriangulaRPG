"""Off-turn windows (Packet: Starting Combat and Turn Structure step 3, Dash).

After any creature's turn ends, including its own and an incapacitated creature's dying-roll
turn, anyone may buy off-turn movement or draw a weapon (readings in the Assumptions
register):
- every active creature is asked, in off_turn.order over initiative positions (lowest
  initiative first as written by default), whether to move or pass;
- a creature with nowhere it can reach and afford isn't asked;
- with repeat_until_all_pass, passes repeat until one in which nobody moves, and a creature
  that passed may move in a later pass;
- each move uses off-turn purchases on the mover's escalation track and provokes OAs like
  any other move.
"""

from stamina_engine.abilities import framework as abilities
from stamina_engine.agents.decisions import Attack, Draw, Move, OffTurnMove, Shoot, UseAbility
from stamina_engine.core.errors import EngineError
from stamina_engine.engine.battle import Battle
from stamina_engine.engine.procedures.melee import melee_attack
from stamina_engine.engine.procedures.movement import move, move_options
from stamina_engine.engine.procedures.ranged import draw, draw_options, shoot, shot_targets
from stamina_engine.model.state import CombatantState

cites = (
    "Packet: Starting Combat and Turn Structure",
    "Packet: Dash",
    "Packet: Actions and Escalation",
    "Packet: Core Abilities",
    "Ledger MV-2",
    "Ledger MV-4",
    "Review F14",
)

MAX_PASSES = 400  # off-turn costs escalate, so a window settles long before this


def window_order(b: Battle) -> tuple[str, ...]:
    order = b.state.order
    if b.rules.off_turn.order_mode() == "ascending_initiative":
        return tuple(reversed(order))
    return order


def _opportunist_options(
    b: Battle, c: CombatantState
) -> tuple[tuple[str, ...], tuple[str, ...], int | None]:
    """Rogue core (Opportunist, packet 0.12.0): once between each of your turns (including
    the opening dash phase), act in a dash phase to make a melee attack or ranged shot
    spending at most 1 + Cunning stamina in total."""
    if (
        b.rules.resources.core_abilities_mode() != "in_fight"
        or "rogue_core" not in c.profile.abilities
        or c.opportunist_used
        or not c.active
    ):
        return (), (), None
    from stamina_engine.engine.timeline import targets

    budget = 1 + c.gear.attributes.CUN
    melee = targets(b, c, max_spend=budget)
    ranged = shot_targets(b, c, max_spend=budget)
    if not melee and not ranged:
        return (), (), None
    return melee, ranged, budget


def off_turn_window(b: Battle, ended: CombatantState | None) -> None:
    """ended is None for the window before the first turn of the fight (0.11.0)."""
    if b.outcome is not None or not b.rules.off_turn.windows_open():
        return
    if b.field is None and b.rules.resources.core_abilities_mode() != "in_fight":
        return
    label = f"off-turn after {ended.id}" if ended is not None else "off-turn before the fight"
    with b.context.frame(label):
        for _ in range(MAX_PASSES):
            moved = False
            for cid in window_order(b):
                c = b.state.get(cid)
                if not c.active:
                    continue
                options = move_options(b, c, on_turn=False)
                draws = draw_options(b, c, on_turn=False) if b.field is not None else ()
                usable = abilities.options(b, c, "off_turn")
                opp_targets, opp_shots, budget = _opportunist_options(b, c)
                if (
                    options is None
                    and not draws
                    and not usable
                    and not opp_targets
                    and not opp_shots
                ):
                    continue
                answer = b.broker.off_turn_move(
                    OffTurnMove(
                        c.id,
                        b.observe(c.id),
                        b.context.path(),
                        options,
                        draws,
                        usable,
                        opp_targets,
                        opp_shots,
                        budget,
                    )
                )
                if isinstance(answer, Move):
                    move(b, c, answer.path, on_turn=False)
                    moved = True
                elif isinstance(answer, Draw):
                    draw(b, c, answer.loadout, on_turn=False)
                    moved = True
                elif isinstance(answer, UseAbility):
                    abilities.use(b, c, answer.name, "off_turn")
                    moved = True
                elif isinstance(answer, Attack):
                    def _mark_opp(actor: CombatantState = c) -> None:
                        b.ops.mark_opportunist(actor)
                        b.ops.ability_used(actor, "opportunist", "off_turn", 0)

                    if melee_attack(
                        b, c, b.state.get(answer.target), max_spend=budget, on_commit=_mark_opp
                    ):
                        moved = True
                elif isinstance(answer, Shoot):
                    def _mark_opp_shot(actor: CombatantState = c) -> None:
                        b.ops.mark_opportunist(actor)
                        b.ops.ability_used(actor, "opportunist", "off_turn", 0)

                    if shoot(
                        b, c, b.state.get(answer.target), max_spend=budget, on_commit=_mark_opp_shot
                    ):
                        moved = True
                if b.outcome is not None:
                    return
                if moved and b.rules.off_turn.restarts():
                    break  # 0.11.0: after a dash, the highest in initiative is asked first again
            if not moved or not b.rules.off_turn.repeats():
                return
        raise EngineError(f"the window ({label}) didn't settle in {MAX_PASSES} passes")
