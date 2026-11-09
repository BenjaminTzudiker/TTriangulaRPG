"""Rounds, initiative and the turn loop (Packet: Starting Combat and Turn Structure)."""

import hashlib

from stamina_engine.abilities import framework as abilities
from stamina_engine.agents.decisions import (
    Attack,
    Draw,
    EndTurn,
    Flee,
    Move,
    Shoot,
    Surrender,
    TurnCommand,
    UseAbility,
)
from stamina_engine.core.dice import roll
from stamina_engine.engine.battle import Battle, BattleResult
from stamina_engine.engine.events import (
    BattleEnded,
    BattleStarted,
    InitiativeRolled,
    MapLoaded,
    RoundStarted,
)
from stamina_engine.engine.procedures.melee import melee_attack
from stamina_engine.engine.procedures.movement import move, move_options
from stamina_engine.engine.procedures.off_turn import off_turn_window
from stamina_engine.engine.procedures.ranged import draw, draw_options, shoot, shot_targets
from stamina_engine.model.state import CombatantState, Status

cites = (
    "Packet: Starting Combat and Turn Structure",
    "Packet: On-Turn Movement",
    "Packet: Off-Turn Movement",
    "Packet: Stamina",
    "Packet: Dying and Death",
    "Ledger CB-9",
    "Ledger CR-3",
    "Ledger IN-1",
)


def roll_initiative(b: Battle) -> tuple[str, ...]:
    """2d12 (placeholder) + 1 per odd Agility + 1 per odd Cunning, rolled once per fight.

    The packet has no tiebreaker; turn_order.tiebreak picks one (Assumptions register).
    """
    rule = b.rules.turn_order
    dice = rule.initiative_dice()
    source = b.dice.dice("initiative")
    rolls: list[tuple[str, int]] = []

    def roll_for(c: CombatantState) -> int:
        total = sum(roll(dice, source)) + c.gear.initiative_bonus
        rolls.append((c.id, total))
        return total

    def ordered(group: list[CombatantState], totals: dict[str, int]) -> list[CombatantState]:
        # sorted() is stable: equal totals keep listed order.
        ranked = sorted(group, key=lambda c: -totals[c.id])
        tiebreak = rule.tiebreak_mode()
        if tiebreak == "list_order":
            return ranked
        out: list[CombatantState] = []
        i = 0
        while i < len(ranked):
            tied = [c for c in ranked[i:] if totals[c.id] == totals[ranked[i].id]]
            if len(tied) > 1 and tiebreak == "higher_agility":
                by_agi = sorted(tied, key=lambda c: -c.gear.attributes.AGI)
                agis = [c.gear.attributes.AGI for c in by_agi]
                if len(set(agis)) == len(agis):
                    out.extend(by_agi)
                    i += len(tied)
                    continue
            if len(tied) > 1:  # reroll among the tied creatures until they separate
                out.extend(ordered(tied, {c.id: roll_for(c) for c in tied}))
            else:
                out.extend(tied)
            i += len(tied)
        return out

    first = {c.id: roll_for(c) for c in b.state.combatants}
    order = tuple(c.id for c in ordered(list(b.state.combatants), first))
    b.ops.set_order(order)
    b.ops.emit(InitiativeRolled(tuple(rolls), order))
    return order


def take_turn(b: Battle, c: CombatantState) -> None:
    with b.context.frame(f"turn {c.id}"):
        b.ops.start_turn(c)
        dying_dice = b.rules.dying.roll_dice()
        if c.dying.in_shock and dying_dice is not None:
            attrs = c.gear.attributes
            bonus = b.rules.dying.roll_bonus(attrs.STR, attrs.WIL)
            total = sum(roll(dying_dice, b.dice.dice("dying"))) + bonus
            b.ops.dying_roll(c, total)
        if c.active:
            command_loop(b, c)
            if b.outcome is not None:
                return  # the fight ended mid-turn
        b.ops.end_turn(c)
        if c.active or b.rules.resources.recovers_while_incapacitated():
            b.ops.recover(c, c.profile.recovery)
        off_turn_window(b, c)


def command_loop(b: Battle, c: CombatantState) -> None:
    """Move and act in any order until the agent ends the turn (Packet: Starting Combat and
    Turn Structure: movement can be split up around actions)."""
    while c.active:
        answer = b.broker.turn_command(
            TurnCommand(
                c.id,
                b.observe(c.id),
                b.context.path(),
                targets(b, c),
                move_options(b, c, on_turn=True),
                shot_targets(b, c),
                draw_options(b, c, on_turn=True),
                b.field is not None and c.pos is not None and b.field.is_exit(c.pos),
                b.field is not None,
                abilities.options(b, c, "turn"),
            )
        )
        if isinstance(answer, EndTurn):
            return
        if isinstance(answer, Move):
            move(b, c, answer.path, on_turn=True)
        elif isinstance(answer, Attack):
            melee_attack(b, c, b.state.get(answer.target))
        elif isinstance(answer, Shoot):
            shoot(b, c, b.state.get(answer.target))
        elif isinstance(answer, Draw):
            draw(b, c, answer.loadout, on_turn=True)
        elif isinstance(answer, UseAbility):
            abilities.use(b, c, answer.name, "turn")
        elif isinstance(answer, Flee | Surrender):
            if isinstance(answer, Flee):
                b.ops.flee(c)
            else:
                b.ops.surrender(c)
            b.check_end()
            return
        if b.outcome is not None:
            return


def targets(b: Battle, c: CombatantState) -> tuple[str, ...]:
    """Active enemies in the main weapon's reach (everyone, in the all-adjacent arena), if a
    step is affordable. On-turn attacks use the main weapon, as in M1."""
    weapon = c.gear.weapon
    if weapon is None or weapon.ranged:
        return ()
    if b.pricing.melee_attack(weapon.base, 1, c.trackers, light=weapon.light).total > c.stamina:
        return ()
    return tuple(
        o.id for o in b.state.enemies_of(c) if o.active and b.arena.in_reach(b.state, c, o, weapon)
    )


def place_everyone(b: Battle) -> None:
    """On a map: record the map, then put each creature on its starting square."""
    if b.field is None:
        return
    rows = "\n".join(b.field.rows).encode()
    b.ops.emit(
        MapLoaded(b.field.name, b.field.width, b.field.height, hashlib.sha256(rows).hexdigest())
    )
    for e in b.entrants:
        assert e.pos is not None
        b.ops.place(b.state.get(e.id), e.pos)


OUT = (Status.DEAD, Status.FLED, Status.SURRENDERED)


def play_round(b: Battle) -> None:
    """Each creature's turn in initiative order. A Rogue may jump in between turns, or wait
    at its turn's start and come back after a later turn (Packet: Core Abilities); the order
    it actually took becomes its slot from the next round on (Assumptions register)."""
    queue = list(b.state.order)
    taken: list[str] = []
    while queue and b.outcome is None:
        _rogue_jump(b, queue)
        cid = queue.pop(0)
        c = b.state.get(cid)
        if c.status in OUT:
            continue
        if c.active and queue and abilities.window(b, c, "turn_start", {"later": len(queue)}):
            b.ops.delay(c, True)
            queue.insert(1, cid)  # after the next creature's turn
            continue
        if cid in b.state.delayed:
            b.ops.delay(c, False)
        take_turn(b, c)
        taken.append(cid)
    if b.outcome is None:
        new = tuple(taken) + tuple(cid for cid in b.state.order if cid not in taken)
        if new != b.state.order:
            b.ops.reorder(new)


def _rogue_jump(b: Battle, queue: list[str]) -> None:
    """Between turns: a Rogue later in the queue (or waiting) may take its turn now."""
    for rid in queue[1:]:
        r = b.state.get(rid)
        if not r.active or rid in b.state.acted:
            continue
        if abilities.window(b, r, "between_turns", {"next": queue[0]}) == "rogue_core":
            queue.remove(rid)
            queue.insert(0, rid)
            return


def run_battle(b: Battle) -> BattleResult:
    b.ops.emit(
        BattleStarted(
            b.seed,
            b.rules.name,
            b.rules.digest(),
            tuple(c.id for c in b.state.combatants),
            b.dice_mode,
        )
    )
    place_everyone(b)
    order = roll_initiative(b)
    b.check_end()  # a side with no one able to fight has already lost
    round_ = 0
    while b.outcome is None and round_ < b.round_cap:
        round_ += 1
        b.ops.set_round(round_)
        b.ops.emit(RoundStarted(round_))
        with b.context.frame(f"round {round_}"):
            play_round(b)
    winner, reason = b.outcome if b.outcome is not None else (None, "round_cap")
    b.ops.emit(BattleEnded(reason, winner, round_))
    return BattleResult(
        winner, reason, round_, order, b.state, tuple(b.log), tuple(b.broker.records)
    )
