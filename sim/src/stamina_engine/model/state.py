"""Battle state. Only engine/stateops.py writes it; everything else reads it."""

import copy
from dataclasses import dataclass, field
from enum import Enum

from stamina_engine.grid.battlefield import Cell
from stamina_engine.model.derive import CombatProfile, LoadoutProfile
from stamina_engine.rules.components.dying import DyingState
from stamina_engine.rules.pricing import Trackers


class Status(Enum):
    ACTIVE = "active"
    INCAPACITATED = "incapacitated"  # 0 HP or below, alive
    DEAD = "dead"


@dataclass
class CombatantState:
    id: str
    team: str
    profile: CombatProfile
    loadout: str
    dying: DyingState  # holds HP and System Shock
    stamina: int
    strain: int = 0
    trackers: Trackers = field(default_factory=Trackers)
    damage_taken: list[int] = field(default_factory=list)
    # Perfect blocks already made, keyed by (attacker, round), for block-reset variants.
    perfect_blocks: dict[tuple[str, int], int] = field(default_factory=dict)
    pos: Cell | None = None  # None in the all-adjacent arena
    free_move_left: int = 0  # free squares left this turn
    banked: int = 0  # squares bought this turn and not yet used (on-turn purchases)

    @property
    def hp(self) -> int:
        return self.dying.hp

    @property
    def status(self) -> Status:
        if self.dying.dead:
            return Status.DEAD
        if self.dying.hp <= 0:
            return Status.INCAPACITATED
        return Status.ACTIVE

    @property
    def active(self) -> bool:
        return self.status is Status.ACTIVE

    @property
    def gear(self) -> LoadoutProfile:
        return self.profile.loadout(self.loadout)


@dataclass
class BattleState:
    combatants: tuple[CombatantState, ...]  # in listed order
    round: int = 0
    order: tuple[str, ...] = ()  # initiative order, highest first
    turn_of: str | None = None
    moving: str | None = None  # a creature mid-move may share an ally's square
    version: int = 0

    def get(self, cid: str) -> CombatantState:
        for c in self.combatants:
            if c.id == cid:
                return c
        raise KeyError(cid)

    def enemies_of(self, c: CombatantState) -> tuple[CombatantState, ...]:
        return tuple(o for o in self.combatants if o.team != c.team)

    def at(self, cell: Cell) -> tuple[CombatantState, ...]:
        return tuple(c for c in self.combatants if c.pos == cell)

    def teams(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(c.team for c in self.combatants))

    def clone(self) -> "BattleState":
        return copy.deepcopy(self)


def new_combatant(cid: str, team: str, profile: CombatProfile, loadout: str = "") -> CombatantState:
    """A combatant as a fight starts: full HP, stamina at maximum, no strain."""
    return CombatantState(
        id=cid,
        team=team,
        profile=profile,
        loadout=loadout or profile.main.name,
        dying=DyingState(hp=profile.hp_max),
        stamina=profile.start_stamina,
        strain=profile.start_strain,
    )
