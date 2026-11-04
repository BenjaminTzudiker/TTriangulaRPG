"""Rounds, initiative and the turn loop (Packet: Starting Combat and Turn Structure)."""

from stamina_engine.agents.decisions import EndTurn, TurnCommand
from stamina_engine.core.dice import roll
from stamina_engine.engine.battle import Battle, BattleResult
from stamina_engine.engine.events import BattleEnded, BattleStarted, InitiativeRolled, RoundStarted
from stamina_engine.engine.observe import observe
from stamina_engine.engine.procedures.melee import melee_attack
from stamina_engine.model.state import CombatantState, Status

cites = (
    "Packet: Starting Combat and Turn Structure",
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
            total = sum(roll(dying_dice, b.dice.dice("dying"))) + c.gear.attributes.STR
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
    """Move and act in any order until the agent ends the turn. M1 offers melee attacks."""
    while True:
        answer = b.broker.turn_command(
            TurnCommand(c.id, observe(b.state, b.rules, c.id), b.context.path(), targets(b, c))
        )
        if isinstance(answer, EndTurn):
            return
        melee_attack(b, c, b.state.get(answer.target))
        if b.outcome is not None:
            return


def targets(b: Battle, c: CombatantState) -> tuple[str, ...]:
    """Active enemies in reach (everyone, in the all-adjacent arena), if a step is affordable."""
    weapon = c.gear.weapon
    if weapon is None or weapon.ranged:
        return ()
    if b.pricing.melee_attack(weapon.base, 1, c.trackers).total > c.stamina:
        return ()
    return tuple(o.id for o in b.state.enemies_of(c) if o.active)


def off_turn_window(b: Battle, c: CombatantState) -> None:
    """After any creature's turn, anyone may buy off-turn movement. No arena in M1 gives
    movement anywhere to go, so the window offers nothing yet (M2)."""


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
    order = roll_initiative(b)
    b.check_end()  # a side with no one able to fight has already lost
    round_ = 0
    while b.outcome is None and round_ < b.round_cap:
        round_ += 1
        b.ops.set_round(round_)
        b.ops.emit(RoundStarted(round_))
        with b.context.frame(f"round {round_}"):
            for cid in order:
                c = b.state.get(cid)
                if c.status is Status.DEAD:
                    continue
                take_turn(b, c)
                if b.outcome is not None:
                    break
    winner, reason = b.outcome if b.outcome is not None else (None, "round_cap")
    b.ops.emit(BattleEnded(reason, winner, round_))
    return BattleResult(
        winner, reason, round_, order, b.state, tuple(b.log), tuple(b.broker.records)
    )
