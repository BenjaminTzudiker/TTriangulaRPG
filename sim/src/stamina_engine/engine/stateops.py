"""StateOps: the only code that writes battle state (ground rule 3).

Each op checks the rules' invariants, applies the change, and appends a typed event. With
check=True every op re-validates the whole state afterwards.
"""

from collections.abc import Callable
from dataclasses import replace

from stamina_engine.core.errors import EngineError, RulesError, Unaffordable
from stamina_engine.engine.events import (
    AbilityUsed,
    ControlChanged,
    DebtPaid,
    Drew,
    DyingRolled,
    Event,
    Fled,
    Indebted,
    Injured,
    Moved,
    ObjectiveProgress,
    ObjectiveReached,
    ObjectiveResolved,
    OrderChanged,
    Placed,
    Recovered,
    Spent,
    Surrendered,
    TurnEnded,
    TurnStarted,
)
from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.grid.geometry import step_allowed
from stamina_engine.grid.threat import Body, can_pass
from stamina_engine.model.state import (
    OBJECTIVE_DONE,
    OBJECTIVE_FAILED,
    OBJECTIVE_OPEN,
    BattleState,
    CombatantState,
)
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
        c.used_weapon = False
        c.bow_hands = False
        c.step_costs = []
        self.state.turn_of = c.id
        self.state.acted = self.state.acted | {c.id}
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

    # --- weapons -------------------------------------------------------------------

    def use_weapon(self, c: CombatantState, bow: bool = False) -> None:
        """An attack or shot uses a weapon: drawing on your turn stops being free, and a bow
        shot ties up its hands until the start of your next turn (Packet: Drawing Weapons)."""
        c.used_weapon = True
        if bow:
            c.bow_hands = True
        self._bump()

    def draw(self, c: CombatantState, loadout: str, cost: int) -> None:
        """Switch to another loadout (paid separately through spend)."""
        c.profile.loadout(loadout)  # raises if it doesn't exist
        if not c.active:
            raise RulesError(f"{c.id} is {c.status.value} and can't draw")
        c.loadout = loadout
        self._emit(Drew(c.id, loadout, cost))

    # --- abilities -----------------------------------------------------------------

    def ability_used(self, c: CombatantState, name: str, window: str, strain: int) -> None:
        """Record an ability's use and gain its strain (its stamina is a separate spend)."""
        if not c.active:
            raise RulesError(f"{c.id} is {c.status.value} and can't use abilities")
        c.strain += strain
        c.trackers = replace(c.trackers, strain=c.strain)
        self._emit(AbilityUsed(c.id, name, window, c.strain))

    def record_steps(self, c: CombatantState, parts: tuple[int, ...]) -> None:
        """Attack steps paid on your turn, for refunds (the Barbarian core)."""
        c.step_costs.extend(parts)
        self._bump()

    def refund_step(self, c: CombatantState) -> int:
        """Take back the biggest unrefunded attack step paid this turn; returns its cost."""
        if not c.step_costs:
            raise RulesError(f"{c.id} has no attack step to refund")
        biggest = max(c.step_costs)
        c.step_costs.remove(biggest)
        self._bump()
        return biggest

    def reorder(self, order: tuple[str, ...]) -> None:
        self.state.order = order
        self._emit(OrderChanged(order))

    def delay(self, c: CombatantState, waiting: bool) -> None:
        """A Rogue waits to take its turn after a later one (or stops waiting)."""
        self.state.delayed = self.state.delayed | {c.id} if waiting else self.state.delayed - {c.id}
        self._bump()

    # --- control effects (stub) ------------------------------------------------------

    def advance_control(self, target: CombatantState, effect: str, amount: int, by: str) -> None:
        """A control effect gains progress on target (Packet: Conditions and Control Effects:
        progressive and resistible with stamina). What the progress does is Phase 7's."""
        if amount < 0:
            raise EngineError("advance by a positive amount; resist_control pushes back")
        target.control[effect] = target.control.get(effect, 0) + amount
        self._emit(ControlChanged(target.id, effect, target.control[effect], by))

    def resist_control(self, c: CombatantState, effect: str, stamina: int) -> None:
        """Push a control effect back 1 per stamina spent (paid through spend separately)."""
        now = c.control.get(effect, 0)
        if stamina > now:
            raise RulesError(f"{c.id} can push {effect} back {now} at most")
        c.control[effect] = now - stamina
        if c.control[effect] == 0:
            del c.control[effect]
        self._emit(ControlChanged(c.id, effect, c.control.get(effect, 0), c.id))

    # --- scenario objectives (O1) -----------------------------------------------------

    def objective_reached(self, oid: str, who: str) -> None:
        """A creature counts toward a reach or escape objective, once."""
        o = self.state.objectives[oid]
        if o.status != OBJECTIVE_OPEN:
            raise EngineError(f"objective {oid} is already {o.status}")
        if who in o.reached:
            raise EngineError(f"{who} already counts toward {oid}")
        o.reached = o.reached | {who}
        o.progress = len(o.reached)
        self._emit(ObjectiveReached(oid, who, o.progress, self.state.round))

    def objective_scored(self, oid: str, controlled: bool) -> None:
        """A hold objective at the end of a round: a round of control adds to the total and
        the streak; a round without resets the streak."""
        o = self.state.objectives[oid]
        if o.status != OBJECTIVE_OPEN:
            raise EngineError(f"objective {oid} is already {o.status}")
        o.progress += int(controlled)
        o.streak = o.streak + 1 if controlled else 0
        self._emit(ObjectiveProgress(oid, controlled, o.progress, o.streak, self.state.round))

    def resolve_objective(self, oid: str, done: bool, team: str) -> None:
        o = self.state.objectives[oid]
        if o.status != OBJECTIVE_OPEN:
            raise EngineError(f"objective {oid} is already {o.status}")
        o.status = OBJECTIVE_DONE if done else OBJECTIVE_FAILED
        self._emit(ObjectiveResolved(oid, o.status, team, self.state.round))

    # --- leaving the fight ---------------------------------------------------------

    def surrender(self, c: CombatantState) -> None:
        if not c.active:
            raise RulesError(f"{c.id} is {c.status.value} and can't surrender")
        c.out = "surrendered"
        self._emit(Surrendered(c.id))

    def flee(self, c: CombatantState) -> None:
        """Leave the map from an exit square."""
        if not c.active:
            raise RulesError(f"{c.id} is {c.status.value} and can't flee")
        if self.field is None or c.pos is None or not self.field.is_exit(c.pos):
            raise RulesError(f"{c.id} isn't on an exit square")
        frm = c.pos
        c.out = "fled"
        c.pos = None
        self._emit(Fled(c.id, frm))

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
        self.state.acted = frozenset()
        self.state.delayed = frozenset()
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
        for oid, o in self.state.objectives.items():
            if o.status not in (OBJECTIVE_OPEN, OBJECTIVE_DONE, OBJECTIVE_FAILED):
                raise EngineError(f"objective {oid}: unknown status {o.status!r}")
            if not 0 <= o.streak <= o.progress or o.progress < len(o.reached):
                raise EngineError(f"objective {oid}: progress {o.progress}, streak {o.streak}")
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
