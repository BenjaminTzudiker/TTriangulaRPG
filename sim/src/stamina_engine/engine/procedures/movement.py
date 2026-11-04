"""Movement, square by square (Packet: On-Turn Movement, Off-Turn Movement, Triggers,
Avoiding Opportunity Attacks).

A move is a path the creature chose (readings in the Assumptions register):
- its purchases are paid when the move is declared, like an attack's steps: free squares
  first, then squares already bought this turn, then new purchases (flat on your turn,
  escalating off it). So nothing paid during the move (avoidance, blocks against OAs) and no
  injury can leave the mover short of a square it has already committed to;
- then, for each square: if the square being left is threatened, the mover decides which
  threatening enemies to pay off, before any of them says whether it would attack; each enemy
  not paid off may make an opportunity attack, in off_turn.order, each resolving before the
  next is asked, with the mover still in the square it is leaving; if the mover is still up
  and the fight goes on, it enters the next square.
"""

from stamina_engine.agents.decisions import AvoidOA, MoveOptions
from stamina_engine.engine.arena import bodies
from stamina_engine.engine.battle import Battle
from stamina_engine.engine.events import OpportunityAvoided, OpportunityProvoked
from stamina_engine.engine.procedures.opportunity import OAContext, opportunity_attack, reach_cap
from stamina_engine.grid.battlefield import Cell
from stamina_engine.grid.pathing import Passage, reachable
from stamina_engine.model.state import CombatantState

cites = (
    "Packet: On-Turn Movement",
    "Packet: Off-Turn Movement",
    "Packet: Off-Turn Escalation",
    "Packet: Triggers",
    "Packet: Avoiding Opportunity Attacks",
    "Ledger MV-1",
    "Ledger MV-2",
    "Ledger MV-3",
    "Ledger MV-4",
)


def _price_args(c: CombatantState, on_turn: bool) -> dict[str, int]:
    gear = c.gear
    return {
        "free_left": c.free_move_left if on_turn else 0,
        "banked": c.banked if on_turn else 0,
        "movement": gear.movement,
        "extra_squares": gear.extra_squares_per_purchase,
        "off_turn_squares": gear.squares_per_purchase,
    }


def move_options(b: Battle, c: CombatantState, on_turn: bool) -> MoveOptions | None:
    """Where c could move now, or None if nowhere (no map, no affordable square)."""
    field = b.field
    if field is None or c.pos is None or not c.active:
        return None
    args = _price_args(c, on_turn)
    limit = field.width * field.height
    prices = b.pricing.move_prices(
        on_turn=on_turn, trackers=c.trackers, stamina=c.stamina, limit=limit, **args
    )
    most = len(prices) - 1
    if most == 0:
        return None
    passage = Passage.for_mover(b.rules.grid, c.id, c.team, bodies(b.state))
    reach = reachable(field, b.rules.grid, c.pos, passage, most)
    destinations = reach.destinations()
    if not destinations:
        return None
    return MoveOptions(
        c.pos, on_turn, most, prices, destinations, passage.no_entry, passage.no_stop
    )


def free_move_options(b: Battle, c: CombatantState, limit: int) -> MoveOptions | None:
    """Up to `limit` squares already paid for (Tactical Withdrawal)."""
    if b.field is None or c.pos is None or not c.active or limit <= 0:
        return None
    passage = Passage.for_mover(b.rules.grid, c.id, c.team, bodies(b.state))
    reach = reachable(b.field, b.rules.grid, c.pos, passage, limit)
    destinations = reach.destinations()
    if not destinations:
        return None
    return MoveOptions(
        c.pos, False, limit, (0,) * (limit + 1), destinations, passage.no_entry, passage.no_stop
    )


def move(
    b: Battle,
    mover: CombatantState,
    path: tuple[Cell, ...],
    on_turn: bool,
    prepaid: bool = False,
) -> None:
    """Carry out a path the broker has already checked. prepaid: its squares were paid for
    already (an ability's move), so no purchases."""
    with b.context.frame(f"move {mover.id}"):
        if not prepaid:
            quote = b.pricing.move(
                len(path), on_turn=on_turn, trackers=mover.trackers, **_price_args(mover, on_turn)
            )
            for purchase in quote.purchases:
                b.ops.spend(mover, purchase, "extra_move" if on_turn else "off_turn_move")
            if on_turn and quote.bought:
                b.ops.bank(mover, sum(quote.bought))
        oa = OAContext()  # per-square cap accrual, for this move only
        stopped = False
        for nxt in path:
            if b.outcome is not None or not mover.active:
                stopped = True
                break
            how = "off_turn"
            if on_turn:
                how = "free" if mover.free_move_left > 0 else "extra"
            assert mover.pos is not None
            leave(b, mover, mover.pos, on_turn, oa)
            if b.outcome is not None or not mover.active:
                stopped = True
                break
            b.ops.move_to(mover, nxt, how)
        b.ops.end_move(mover, stopped)
        if on_turn and not b.rules.movement.keeps_leftover() and mover.banked:
            b.ops.bank(mover, -mover.banked)


def leave(b: Battle, mover: CombatantState, square: Cell, on_turn: bool, oa: OAContext) -> None:
    """Leaving a threatened square provokes an OA from every enemy threatening it."""
    if not b.rules.opportunity.attacks_allowed():
        return
    threatening = b.arena.threatening(b.state, mover, square)
    if not threatening:
        return
    if b.rules.off_turn.order_mode() == "ascending_initiative":
        threatening = tuple(reversed(threatening))  # lowest initiative first
    b.ops.emit(OpportunityProvoked(mover.id, square, threatening))
    caps = tuple(reach_cap(b, b.state.get(e), square) for e in threatening)
    paid = avoid(b, mover, square, threatening, caps, on_turn)
    for eid, cap in zip(threatening, caps, strict=True):
        oa.left_within(eid, cap, paid=eid in paid)
    for eid in threatening:
        if eid in paid:
            continue
        if b.outcome is not None or not mover.active:
            return
        enemy = b.state.get(eid)
        if enemy.active:
            opportunity_attack(b, enemy, mover, square, oa)


def avoid(
    b: Battle,
    mover: CombatantState,
    square: Cell,
    enemies: tuple[str, ...],
    caps: tuple[int, ...],
    on_turn: bool,
) -> tuple[str, ...]:
    """Ask the mover which enemies to pay off; charge it. Not asked if it can pay no one."""
    debt = b.rules.opportunity.allows_debt()
    affordable = _affordable_subsets(b, mover, caps, on_turn)
    if affordable <= 1 and not debt:
        return ()
    request = AvoidOA(
        mover.id,
        b.observe(mover.id),
        b.context.path(),
        square,
        enemies,
        caps,
        on_turn,
        mover.trackers,
        mover.stamina,
        (2 ** len(enemies)) if debt else affordable,
    )
    answer = b.broker.avoid(request)
    if not answer.enemies:
        return ()
    paid_caps = [caps[enemies.index(e)] for e in answer.enemies]
    quote = b.pricing.avoid_opportunity(
        len(paid_caps), caps=paid_caps, trackers=mover.trackers, on_turn=on_turn
    )
    b.ops.emit(OpportunityAvoided(mover.id, square, answer.enemies))
    b.ops.spend(mover, quote, "avoid", allow_debt=debt)
    return answer.enemies


def _affordable_subsets(
    b: Battle, mover: CombatantState, caps: tuple[int, ...], on_turn: bool
) -> int:
    """How many subsets of the threatening enemies the mover could pay off (F11). Prices
    don't depend on which enemies, only on their caps, so this checks every subset."""
    n = len(caps)
    count = 0
    for mask in range(2**n):
        chosen = [caps[i] for i in range(n) if mask >> i & 1]
        quote = b.pricing.avoid_opportunity(
            len(chosen), caps=chosen, trackers=mover.trackers, on_turn=on_turn
        )
        if quote.total <= mover.stamina:
            count += 1
    return count
