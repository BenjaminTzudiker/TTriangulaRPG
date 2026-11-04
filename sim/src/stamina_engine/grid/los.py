"""Line of sight and cover, by the 5e grid method the packet points to (Packet: Cover).

The shooter picks the corner of its square that gives the best result and traces lines to
the four corners of the target's square. Readings (Assumptions register):
- A line is blocked by a square it passes through the inside of, by running along the edge
  between two blocking squares, or by squeezing through a corner point between two blocking
  squares. A line that only touches a corner or runs along the outside edge of a blocking
  square isn't blocked.
- Terrain: walls and pillars (tall) and low walls or crates all block lines. Lines blocked:
  none, no cover; 1-2, half; 3-4, three-quarters. Total cover (no shot) needs all four
  lines blocked by tall terrain: a low wall alone never gives total cover.
- Creatures between (not the shooter or the target) give half cover at most
  (`grid.creature_cover`), if any line from the chosen corner passes through one.

Points are square corners in integer coordinates: square (x, y) spans [x, x + 1] x
[y, y + 1].
"""

from collections.abc import Callable, Iterable
from enum import IntEnum
from functools import lru_cache
from math import gcd

from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.grid.geometry import crosses_inside
from stamina_engine.rules.components.grid import GridRule

cites = ("Packet: Cover", "Packet: Ranged Attacks", "Ledger RG-4")

Point = tuple[int, int]


class Cover(IntEnum):
    NONE = 0
    HALF = 1
    THREE_QUARTERS = 2
    TOTAL = 3


def corners(cell: Cell) -> tuple[Point, ...]:
    x, y = cell
    return ((x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1))


def line_blocked(p: Point, q: Point, blocks: Callable[[Cell], bool], skip: frozenset[Cell]) -> bool:
    """Is the segment p-q blocked by any square for which blocks() is true (skip aside)?"""
    if p == q:
        return False

    def solid(c: Cell) -> bool:
        return c not in skip and blocks(c)

    (px, py), (qx, qy) = p, q
    if px == qx or py == qy:  # along a grid line: blocked only between two solid squares
        if px == qx:
            for y in range(min(py, qy), max(py, qy)):
                if solid((px - 1, y)) and solid((px, y)):
                    return True
        else:
            for x in range(min(px, qx), max(px, qx)):
                if solid((x, py - 1)) and solid((x, py)):
                    return True
        return False
    for x in range(min(px, qx), max(px, qx)):
        for y in range(min(py, qy), max(py, qy)):
            if solid((x, y)) and crosses_inside(p, q, (x, x + 1, y, y + 1)):
                return True
    dx, dy = qx - px, qy - py
    g = gcd(abs(dx), abs(dy))
    sx, sy = (1 if dx > 0 else -1), (1 if dy > 0 else -1)
    for k in range(1, g):
        i, j = px + k * dx // g, py + k * dy // g
        # The two squares the line only touches at this corner point.
        side1 = (i if sx > 0 else i - 1, j - 1 if sy > 0 else j)
        side2 = (i - 1 if sx > 0 else i, j if sy > 0 else j - 1)
        if solid(side1) and solid(side2):
            return True
    return False


@lru_cache(maxsize=65536)
def terrain_cover(field: Battlefield, shooter: Cell, target: Cell) -> tuple[Cover, ...]:
    """Cover from terrain alone, for each corner of the shooter's square."""
    skip = frozenset({shooter, target})

    def sight(c: Cell) -> bool:
        return field.terrain(c).blocks_move  # walls, pillars, low walls and crates

    out = []
    for c in corners(shooter):
        any_blocked = tall_blocked = 0
        for t in corners(target):
            if line_blocked(c, t, sight, skip):
                any_blocked += 1
                if line_blocked(c, t, field.tall, skip):
                    tall_blocked += 1
        if tall_blocked == 4:
            out.append(Cover.TOTAL)
        elif any_blocked >= 3:
            out.append(Cover.THREE_QUARTERS)
        elif any_blocked >= 1:
            out.append(Cover.HALF)
        else:
            out.append(Cover.NONE)
    return tuple(out)


def cover(
    field: Battlefield,
    rule: GridRule,
    shooter: Cell,
    target: Cell,
    creatures: Iterable[Cell] = (),
) -> Cover:
    """The cover target has from shooter: the best of the shooter's corners. Creatures are the
    squares of every other creature (shooter and target are left out here)."""
    others = frozenset(creatures) - {shooter, target}
    best = Cover.TOTAL
    counts = bool(others) and rule.creature_cover_mode() == "half"

    def creature(s: Cell) -> bool:
        return s in others

    for c, level in zip(corners(shooter), terrain_cover(field, shooter, target), strict=True):
        behind = counts and level < Cover.HALF
        if behind and any(line_blocked(c, t, creature, frozenset()) for t in corners(target)):
            level = Cover.HALF
        best = min(best, level)
    return best


def can_see(field: Battlefield, rule: GridRule, shooter: Cell, target: Cell) -> bool:
    """A target in total cover can't be targeted."""
    return cover(field, rule, shooter, target) < Cover.TOTAL
