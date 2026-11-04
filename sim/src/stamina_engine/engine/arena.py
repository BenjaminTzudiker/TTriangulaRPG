"""The arena answers spatial questions for the engine: who can attack whom, who threatens a
square, who may pass where. It belongs to the scenario (the map), not to the RuleSet.

- AllAdjacent is M1's arena, the review's setup: everyone is in reach of everyone and there
  is nowhere to move, so no square is ever left and no OA is ever provoked.
- GridArena reads a Battlefield and positions, under the RuleSet's grid readings.
"""

from typing import Protocol

from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.grid.geometry import reach_cells
from stamina_engine.grid.threat import Body, body, threatening
from stamina_engine.model.derive import WeaponProfile
from stamina_engine.model.state import BattleState, CombatantState
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Positioning", "Packet: Triggers", "Packet: Weapon Table", "Ledger MV-3")


class Arena(Protocol):
    field: Battlefield | None

    def in_reach(
        self,
        state: BattleState,
        attacker: CombatantState,
        target: CombatantState,
        weapon: WeaponProfile,
    ) -> bool: ...

    def threatening(
        self, state: BattleState, mover: CombatantState, cell: Cell
    ) -> tuple[str, ...]: ...


class AllAdjacent:
    field: Battlefield | None = None

    def in_reach(
        self,
        state: BattleState,
        attacker: CombatantState,
        target: CombatantState,
        weapon: WeaponProfile,
    ) -> bool:
        return not weapon.ranged

    def threatening(self, state: BattleState, mover: CombatantState, cell: Cell) -> tuple[str, ...]:
        return ()


def bodies(state: BattleState) -> tuple[Body, ...]:
    """Every placed creature, in initiative order once rolled (listed order before)."""
    order = {cid: i for i, cid in enumerate(state.order)}
    ranked = sorted(state.combatants, key=lambda c: order.get(c.id, len(order)))
    return tuple(body(c.id, c.team, c.pos, c.gear, c.active) for c in ranked if c.pos is not None)


class GridArena:
    def __init__(self, field: Battlefield, rules: RuleSet) -> None:
        self.field: Battlefield | None = field
        self._field = field
        self.rules = rules

    def in_reach(
        self,
        state: BattleState,
        attacker: CombatantState,
        target: CombatantState,
        weapon: WeaponProfile,
    ) -> bool:
        if weapon.ranged or attacker.pos is None or target.pos is None:
            return False
        return target.pos in reach_cells(self._field, attacker.pos, weapon.reach, self.rules.grid)

    def threatening(self, state: BattleState, mover: CombatantState, cell: Cell) -> tuple[str, ...]:
        """Enemies of the mover that threaten cell, in initiative order."""
        return threatening(self._field, self.rules.grid, bodies(state), mover.team, cell)
