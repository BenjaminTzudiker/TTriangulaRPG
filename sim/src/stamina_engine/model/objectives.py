"""Scenario objectives (O1): zones, and what one side must do in them other than down every
opponent. These are scenario configuration, not rules: the packet only says that combat
usually ends when one side "achieves its objective" (Packet: Running the Game). Every reading
the packet doesn't give is stated per scenario or registered in ENGINE_PLAN's Assumptions
register.

Pure reads of battle state live here; StateOps writes ObjectiveState.
"""

from dataclasses import dataclass

from stamina_engine.grid.battlefield import Cell
from stamina_engine.model.state import OBJECTIVE_DONE as DONE
from stamina_engine.model.state import OBJECTIVE_FAILED as FAILED
from stamina_engine.model.state import OBJECTIVE_OPEN as OPEN
from stamina_engine.model.state import BattleState, CombatantState, ObjectiveState

cites = ("Packet: Running the Game",)

KINDS = frozenset({"reach", "escape", "hold"})
CONTROL = frozenset({"present", "uncontested", "majority"})
SCORE = frozenset({"consecutive", "cumulative", "final"})
__all__ = ["DONE", "FAILED", "OPEN", "ObjectiveSpec", "ObjectiveState", "Zone"]


@dataclass(frozen=True)
class Zone:
    id: str
    cells: tuple[Cell, ...]  # sorted, in reading order (y, then x)

    def __contains__(self, cell: object) -> bool:
        return cell in self.cells


@dataclass(frozen=True)
class ObjectiveSpec:
    """One side's objective, with every default already resolved at load.

    who: the creatures who count (the whole team unless the scenario names some).
    count: how many must reach the zone or escape (reach, escape).
    control, score, rounds: hold only. deadline: the round by whose end it must be done.
    """

    id: str
    kind: str
    team: str
    who: tuple[str, ...]
    deadline: int
    zone: Zone | None = None
    count: int = 0
    control: str = ""
    score: str = ""
    rounds: int = 0

    @property
    def needed(self) -> int:
        """Reach and escape: creatures; hold: rounds of control (1 for final scoring)."""
        if self.kind == "hold":
            return 1 if self.score == "final" else self.rounds
        return self.count


def members(state: BattleState, spec: ObjectiveSpec) -> tuple[CombatantState, ...]:
    return tuple(state.get(cid) for cid in spec.who)


def in_zone(state: BattleState, zone: Zone, team: str, *, same: bool = True) -> int:
    """Active creatures standing in the zone: of the team, or (same=False) of any other team.
    Incapacitated, fled and surrendered creatures don't count (Assumptions register)."""
    return sum(
        1
        for c in state.combatants
        if c.active and c.pos is not None and c.pos in zone and (c.team == team) == same
    )


def controls(state: BattleState, spec: ObjectiveSpec) -> bool:
    """Whether the objective's team controls its zone, by the scenario's control reading."""
    assert spec.zone is not None
    mine = in_zone(state, spec.zone, spec.team)
    theirs = in_zone(state, spec.zone, spec.team, same=False)
    if spec.control == "present":
        return mine > 0
    if spec.control == "uncontested":
        return mine > 0 and theirs == 0
    return mine > theirs  # majority


def still_possible(state: BattleState, spec: ObjectiveSpec, progress: int) -> bool:
    """Reach and escape: enough creatures who count are still active (or already counted)."""
    if spec.kind == "hold":
        return True
    counted = state.objectives[spec.id].reached
    able = sum(1 for c in members(state, spec) if c.active and c.id not in counted)
    return progress + able >= spec.count
