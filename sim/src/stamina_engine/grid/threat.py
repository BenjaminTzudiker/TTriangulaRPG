"""Who threatens a square, and who may pass whom (Packet: Triggers; Defined Terms).

A threatened square is a square within an enemy's melee reach. Readings (Assumptions
register):
- Every ready melee weapon in the current loadout threatens its reach, main hand and off hand.
  A bow, a sheathed weapon or no weapon threatens nothing.
- Threat is geometric: it doesn't depend on whether the enemy can afford an OA.
- Incapacitated and dead creatures threaten nothing.
- Passing through squares follows `grid.occupancy` for the living and `grid.bodies` for the
  incapacitated and dead; nobody ends a move in an occupied square.

Bodies are plain records, so the engine (from battle state) and agents (from observations)
build them the same way.
"""

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.grid.geometry import reach_cells
from stamina_engine.model.derive import LoadoutProfile, WeaponProfile
from stamina_engine.rules.components.grid import GridRule

cites = ("Packet: Triggers", "Packet: Weapon Table", "Packet: Defined Terms", "Ledger MV-3")


@dataclass(frozen=True)
class Body:
    id: str
    team: str
    pos: Cell
    reaches: tuple[int, ...]  # one per ready melee weapon; empty if it threatens nothing
    active: bool


def melee_weapons(gear: LoadoutProfile) -> tuple[WeaponProfile, ...]:
    """The ready melee weapons: the main weapon and an off-hand weapon, if not ranged."""
    return tuple(w for w in (gear.weapon, gear.off_hand_weapon) if w is not None and not w.ranged)


def body(cid: str, team: str, pos: Cell, gear: LoadoutProfile, active: bool) -> Body:
    return Body(cid, team, pos, tuple(w.reach for w in melee_weapons(gear)), active)


def threatened_by(field: Battlefield, rule: GridRule, b: Body) -> frozenset[Cell]:
    if not b.active:
        return frozenset()
    out: frozenset[Cell] = frozenset()
    for reach in sorted(set(b.reaches)):
        out |= reach_cells(field, b.pos, reach, rule)
    return out


def threatening(
    field: Battlefield, rule: GridRule, bodies: Iterable[Body], team: str, cell: Cell
) -> tuple[str, ...]:
    """Enemies of `team` that threaten `cell`, in the order given."""
    return tuple(b.id for b in bodies if b.team != team and cell in threatened_by(field, rule, b))


def can_pass(rule: GridRule, mover_team: str, other: Body) -> bool:
    """May a creature of mover_team move through other's square?"""
    if not other.active:
        return rule.body_mode() == "passable"
    mode = rule.occupancy_mode()
    if other.team == mover_team:
        return mode in ("allies_only", "anyone")
    return mode == "anyone"


def blocked_squares(
    rule: GridRule, mover: str, mover_team: str, bodies: Sequence[Body]
) -> tuple[frozenset[Cell], frozenset[Cell]]:
    """(squares the mover can't enter at all, squares it can pass but not stop in)."""
    no_entry, no_stop = set(), set()
    for b in bodies:
        if b.id == mover:
            continue
        no_stop.add(b.pos)
        if not can_pass(rule, mover_team, b):
            no_entry.add(b.pos)
    return frozenset(no_entry), frozenset(no_stop)
