"""StateOps: the only code that writes battle state (ground rule 3).

Each op checks the rules' invariants, applies the change, and appends a typed event. With
check=True every op re-validates the whole state afterwards.
"""

from collections.abc import Callable

from stamina_engine.core.errors import EngineError, RulesError, Unaffordable
from stamina_engine.engine.events import (
    DyingRolled,
    Event,
    Injured,
    Recovered,
    Spent,
    TurnEnded,
    TurnStarted,
)
from stamina_engine.model.state import BattleState, CombatantState
from stamina_engine.rules.pricing import Quote, Trackers
from stamina_engine.rules.ruleset import RuleSet

cites = (
    "Packet: Stamina",
    "Packet: Dying and Death",
    "Packet: Actions and the On-Turn Surcharge",
    "Packet: Off-Turn Escalation",
    "Ledger CR-2",
    "Ledger CR-3",
    "Ledger IN-1",
)


class StateOps:
    def __init__(
        self, state: BattleState, rules: RuleSet, log: list[Event], check: bool = False
    ) -> None:
        self.state = state
        self.rules = rules
        self.log = log
        self.check = check
        self.listeners: list[Callable[[Event], None]] = []  # e.g. the public ledger

    # --- reads used by the ops -------------------------------------------------------

    def max_stamina(self, c: CombatantState) -> int:
        """Maximum stamina uses current HP, so injuries lower it (Packet: Stamina)."""
        return self.rules.resources.max_stamina(c.hp, c.profile.level)

    # --- ops -------------------------------------------------------------------------

    def spend(self, c: CombatantState, quote: Quote, category: str) -> None:
        if not c.active:
            raise RulesError(f"{c.id} is {c.status.value} and can't spend stamina")
        if quote.total > c.stamina:
            raise Unaffordable(f"{c.id}: {category} costs {quote.total}, has {c.stamina}")
        c.stamina -= quote.total
        c.trackers = quote.after(c.trackers)
        self._emit(Spent(c.id, quote.total, category, quote.track.value, quote.parts, c.stamina))

    def recover(self, c: CombatantState, amount: int) -> None:
        """Recover up to maximum stamina; anything over the cap is wasted."""
        gained = max(0, min(amount, self.max_stamina(c) - c.stamina))
        c.stamina += gained
        self._emit(Recovered(c.id, gained, amount - gained, c.stamina))

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
        """The on-turn surcharge and the off-turn track both reset at the start of your turn."""
        c.trackers = Trackers(0, 0, c.trackers.strain)
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
            if c.dying.in_shock and c.dying.shock <= 0:
                raise EngineError(f"{c.id}: in System Shock with {c.dying.shock} Shock")
