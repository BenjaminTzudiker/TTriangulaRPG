"""StateOps: the only code that writes battle state (ground rule 3).

Each op checks the rules' invariants, applies the change, and appends a typed event. With
check=True every op re-validates the whole state afterwards.
"""

from collections.abc import Callable

from stamina_engine.core.errors import EngineError, RulesError, Unaffordable
from stamina_engine.engine.events import (
    DebtPaid,
    DyingRolled,
    Event,
    Indebted,
    Injured,
    Moved,
    Placed,
    Recovered,
    Spent,
    TurnEnded,
    TurnStarted,
)
from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.grid.geometry import step_allowed
from stamina_engine.grid.threat import Body, can_pass
from stamina_engine.model.state import BattleState, CombatantState
from stamina_engine.rules.pricing import Quote, Trackers
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Stamina",
    "Packet: Dying and Death",
    "Packet: Actions and the On-Turn Surcharge",
    "Packet: Off-Turn Escalation",
    "Packet: On-Turn Movement",
    "Packet: Off-Turn Movement",
    "Ledger MV-1",
    "Ledger MV-2",
    "Ledger CR-2",
    "Ledger CR-3",
    "Ledger IN-1",
)


class StateOps:
    def __init__(
        self,
        state: BattleState,
        rules: RuleSet,
        log: list[Event],
        check: bool = False,
        field: Battlefield | None = None,
    ) -> None:
        self.state = state
        self.rules = rules
        self.log = log
        self.check = check
        self.field = field  # None in the all-adjacent arena: nothing can move
        self.listeners: list[Callable[[Event], None]] = []  # e.g. the public ledger

    # --- reads used by the ops -------------------------------------------------------

    def max_stamina(self, c: CombatantState) -> int:
        """Maximum stamina uses current HP, so injuries lower it (Packet: Stamina)."""
        return self.rules.resources.max_stamina(c.hp, c.profile.level)

    # --- ops -------------------------------------------------------------------------

    def spend(
        self, c: CombatantState, quote: Quote, category: str, allow_debt: bool = False
    ) -> None:
        """Pay a quote. With allow_debt (avoidance under opportunity.avoid_debt only), a
        shortfall becomes debt instead of being refused; stamina never goes below 0."""
        if not c.active:
            raise RulesError(f"{c.id} is {c.status.value} and can't spend stamina")
        owed = max(0, quote.total - c.stamina)
        if owed and not allow_debt:
            raise Unaffordable(f"{c.id}: {category} costs {quote.total}, has {c.stamina}")
        c.stamina -= quote.total - owed
        c.trackers = quote.after(c.trackers)
        self._emit(Spent(c.id, quote.total, category, quote.track.value, quote.parts, c.stamina))
        if owed:
            c.debt += owed
            self._emit(Indebted(c.id, owed, c.debt))

    def recover(self, c: CombatantState, amount: int) -> None:
        """Recover up to maximum stamina; anything over the cap is wasted. Debt is paid
        first."""
        paid = min(c.debt, amount)
        if paid:
            c.debt -= paid
            self._emit(DebtPaid(c.id, paid, c.debt))
        gained = max(0, min(amount - paid, self.max_stamina(c) - c.stamina))
        c.stamina += gained
        self._emit(Recovered(c.id, gained, amount - paid - gained, c.stamina))

    def injure(self, c: CombatantState, damage: int) -> None:
        """Lose HP through the dying rule, then clamp stamina to the new maximum."""
        if damage <= 0:
            return
        c.dying = self.rules.dying.take_damage(c.dying, damage)
        c.damage_taken.append(damage)
        c.stamina = min(c.stamina, self.max_stamina(c))
        self._emit(Injured(c.id, damage, c.hp, c.dying.shock, c.stamina, c.status.value))

    def dying_roll(self, c: CombatantState, total: int) -> None:
        c.dying = self.rules.dying.dying_roll(c.dying, total)
        self._emit(DyingRolled(c.id, total, c.dying.shock, c.status.value))

    def start_turn(self, c: CombatantState) -> None:
        """The on-turn surcharge and the off-turn track both reset at the start of your turn,
        and your free movement is back. Squares bought last turn don't carry over."""
        c.trackers = Trackers(0, 0, c.trackers.strain)
        c.free_move_left = c.gear.movement
        c.banked = 0
        self.state.turn_of = c.id
        self._emit(TurnStarted(c.id, self.state.round))

    def end_turn(self, c: CombatantState) -> None:
        self.state.turn_of = None
        self._emit(TurnEnded(c.id))

    def count_perfect_blocks(
        self, defender: CombatantState, attacker: str, round_: int, count: int
    ) -> None:
        if count:
            key = (attacker, round_)
            defender.perfect_blocks[key] = defender.perfect_blocks.get(key, 0) + count
            self._bump()

    # --- positions -----------------------------------------------------------------

    def place(self, c: CombatantState, cell: Cell) -> None:
        """Put a creature on the map as the battle starts."""
        if self.field is None:
            raise EngineError("the all-adjacent arena has no squares")
        if not self.field.walkable(cell):
            raise RulesError(f"{c.id} can't start on {cell}: {self.field.terrain(cell).name}")
        if self.state.at(cell):
            raise RulesError(f"{c.id} can't start on {cell}: occupied")
        c.pos = cell
        self._emit(Placed(c.id, cell))

    def _body(self, o: CombatantState) -> Body:
        assert o.pos is not None
        return Body(o.id, o.team, o.pos, (), o.active)

    def move_to(self, c: CombatantState, cell: Cell, how: str) -> None:
        """One square. Free and bought squares are used here, so a move can never take
        squares it hasn't got. Paying for purchases is a separate spend (Pricing quotes it)."""
        if self.field is None or c.pos is None:
            raise EngineError("the all-adjacent arena has no squares")
        if not c.active:
            raise RulesError(f"{c.id} is {c.status.value} and can't move")
        if not step_allowed(self.field, c.pos, cell, self.rules.grid.corner_mode()):
            raise RulesError(f"{c.id} can't step from {c.pos} to {cell}")
        for o in self.state.at(cell):
            if o is not c and not can_pass(self.rules.grid, c.team, self._body(o)):
                raise RulesError(f"{c.id} can't move through {o.id} at {cell}")
        if how == "free":
            if c.free_move_left <= 0:
                raise RulesError(f"{c.id} has no free movement left")
            c.free_move_left -= 1
        elif how == "extra":
            if c.banked <= 0:
                raise RulesError(f"{c.id} has no bought squares left")
            c.banked -= 1
        elif how != "off_turn":
            raise EngineError(f"unknown movement kind {how!r}")
        frm = c.pos
        c.pos = cell
        self.state.moving = c.id
        self._emit(Moved(c.id, frm, cell, how))

    def bank(self, c: CombatantState, squares: int) -> None:
        """Squares an on-turn purchase bought, usable for the rest of the turn."""
        c.banked += squares
        self._bump()

    def end_move(self, c: CombatantState, stopped: bool = False) -> None:
        """A move may pass through an ally's square but never end in an occupied one. A move
        stopped early (the mover downed, or the fight over) ends where it is, even if that is
        an ally's square: a downed body can lie under an ally's feet."""
        self.state.moving = None
        if not stopped and c.pos is not None and len(self.state.at(c.pos)) > 1:
            others = [o.id for o in self.state.at(c.pos) if o is not c]
            raise RulesError(f"{c.id} can't end its move on {others[0]}'s square {c.pos}")
        self._bump()

    def set_round(self, round_: int) -> None:
        self.state.round = round_
        self._bump()

    def set_order(self, order: tuple[str, ...]) -> None:
        self.state.order = order
        self._bump()

    # --- bookkeeping -----------------------------------------------------------------

    def emit(self, event: Event) -> None:
        """Record an event that changes no state (declarations, rolls, outcomes)."""
        self.log.append(event)
        for listen in self.listeners:
            listen(event)

    def _emit(self, event: Event) -> None:
        self.emit(event)
        self._bump()

    def _bump(self) -> None:
        self.state.version += 1
        if self.check:
            self.validate()

    def validate(self) -> None:
        for c in self.state.combatants:
            top = self.max_stamina(c)
            if not 0 <= c.stamina <= top:
                raise EngineError(f"{c.id}: stamina {c.stamina} outside 0..{top}")
            if c.debt < 0:
                raise EngineError(f"{c.id}: debt {c.debt} below 0")
            if c.dying.in_shock and c.dying.shock <= 0:
                raise EngineError(f"{c.id}: in System Shock with {c.dying.shock} Shock")
        if self.field is not None:
            seen: dict[Cell, str] = {}
            for c in self.state.combatants:
                if c.pos is None:
                    continue
                if not self.field.walkable(c.pos):
                    raise EngineError(f"{c.id} stands on {self.field.terrain(c.pos).name}")
                shared = c.pos in seen and self.state.moving not in (c.id, seen[c.pos])
                if shared and all(o.active for o in self.state.at(c.pos)):
                    raise EngineError(f"{c.id} and {seen[c.pos]} share {c.pos}")
                seen[c.pos] = c.id
