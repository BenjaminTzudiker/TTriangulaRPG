"""System Shock (Packet: Dying and Death).

Pure transitions on a DyingState. The turn engine (M1) rolls the dice and applies the
result through StateOps. Helping someone stabilize needs a Medicine roll, which is TODO in
the packet, so stabilize() only records the outcome.
"""

from dataclasses import dataclass, replace

from stamina_engine.core.dice import Dice
from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class DyingState:
    hp: int
    shock: int = 0
    in_shock: bool = False
    dead: bool = False

    @property
    def incapacitated(self) -> bool:
        return self.hp <= 0


@dataclass(frozen=True)
class DyingRule(Component):
    cites = ("Packet: Dying and Death", "Packet: Will", "Ledger IN-1")

    def roll_dice(self) -> Dice | None:
        """The dice of the start-of-turn dying roll, or None."""
        return None

    def roll_bonus(self, strength: int, will: int) -> int:
        """What the dying roll adds to its dice."""
        return 0

    def take_damage(self, state: DyingState, damage: int) -> DyingState:
        raise NotImplementedError

    def dying_roll(self, state: DyingState, total: int) -> DyingState:
        raise NotImplementedError

    def stabilize(self, state: DyingState) -> DyingState:
        raise NotImplementedError


@register("dying", "system_shock")
@dataclass(frozen=True)
class SystemShock(DyingRule):
    """Shock from negative HP; a 2d12 + STR (v0.9) or + WIL (0.9.1) roll each turn; death at
    10 Shock or -10 HP."""

    # The attribute the dying roll adds: Strength (v0.9) or Will (0.9.1).
    allowed = {"roll_attribute": frozenset({"strength", "will"})}

    roll_count: int = 2
    roll_size: int = 12
    bleed_below: int = 10  # roll below 10 + Shock: +1 Shock
    stabilize_at: int = 15  # roll of 15 + Shock or more: -1 Shock
    death_shock: int = 10
    death_hp: int = -10
    roll_attribute: str = "strength"

    def roll_dice(self) -> Dice | None:
        return Dice(self.roll_count, self.roll_size)

    def roll_bonus(self, strength: int, will: int) -> int:
        return will if self.roll_attribute == "will" else strength

    def _check_death(self, state: DyingState) -> DyingState:
        if state.shock >= self.death_shock or state.hp <= self.death_hp:
            return replace(state, dead=True)
        return state

    def take_damage(self, state: DyingState, damage: int) -> DyingState:
        if damage <= 0 or state.dead:
            return state
        hp = state.hp - damage
        if state.in_shock:
            shock = state.shock + damage
        elif state.hp <= 0:
            # At exactly 0 HP, or stabilized below 0: Shock equals the damage taken.
            shock = damage
        elif hp < 0:
            shock = -hp
        else:
            shock = 0
        return self._check_death(DyingState(hp=hp, shock=shock, in_shock=shock > 0))

    def dying_roll(self, state: DyingState, total: int) -> DyingState:
        """Apply a start-of-turn dying roll; total is the dice plus roll_bonus."""
        if not state.in_shock or state.dead:
            return state
        if total < self.bleed_below + state.shock:
            shock = state.shock + 1
        elif total >= self.stabilize_at + state.shock:
            shock = state.shock - 1
        else:
            shock = state.shock
        return self._check_death(replace(state, shock=shock, in_shock=shock > 0))

    def stabilize(self, state: DyingState) -> DyingState:
        """End System Shock: HP stays negative and the creature stays incapacitated."""
        if state.dead:
            return state
        return replace(state, shock=0, in_shock=False)


@register("dying", "none")
@dataclass(frozen=True)
class NoShock(DyingRule):
    """Parity only (review-sim): no System Shock. At 0 HP or below a creature is simply out,
    and never rolls or dies, as in the review's simulator."""

    def take_damage(self, state: DyingState, damage: int) -> DyingState:
        if damage <= 0:
            return state
        return replace(state, hp=state.hp - damage)

    def dying_roll(self, state: DyingState, total: int) -> DyingState:
        return state

    def stabilize(self, state: DyingState) -> DyingState:
        return state
