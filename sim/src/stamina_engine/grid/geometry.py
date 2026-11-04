"""Distance, steps and reach on the grid (Packet: Weapon Table reach, On-Turn Movement).

Readings (Assumptions register):
- Distance is Chebyshev: a diagonal is one square (`grid.metric`, ruled for now).
- A diagonal step past wall or pillar corners follows `grid.corners`; creatures never block
  a diagonal.
- A weapon threatens the squares within its reach to which it has a clear line
  (`grid.reach_needs_line`): the centre-to-centre segment doesn't pass through the inside of
  a wall or pillar square, and doesn't squeeze between two of them where they meet at a
  corner. Low walls, crates and creatures don't block reach.

Line tests use exact integer arithmetic on doubled coordinates, where square (x, y) spans
[2x, 2x + 2] x [2y, 2y + 2] and its centre is (2x + 1, 2y + 1).
"""

from fractions import Fraction
from functools import lru_cache

from stamina_engine.core.errors import ConfigError
from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.rules.components.grid import GridRule

cites = ("Packet: Weapon Table", "Packet: On-Turn Movement", "Ledger MV-1")

# Orthogonal steps first, then diagonals, clockwise from north: a fixed order keeps every
# search deterministic.
STEPS: tuple[Cell, ...] = ((0, -1), (1, 0), (0, 1), (-1, 0), (1, -1), (1, 1), (-1, 1), (-1, -1))


def _check_metric(rule: GridRule) -> None:
    metric = rule.metric_name()
    if metric != "chebyshev":
        raise ConfigError(f"grid.metric = {metric!r} isn't built yet; only chebyshev is")


def distance(a: Cell, b: Cell, rule: GridRule) -> int:
    _check_metric(rule)
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def step_allowed(field: Battlefield, a: Cell, b: Cell, corners: str) -> bool:
    """One square from a to b over terrain alone (occupancy is checked elsewhere)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    if max(abs(dx), abs(dy)) != 1 or not field.walkable(b):
        return False
    if dx == 0 or dy == 0 or corners == "free":
        return True
    side_a = field.tall((a[0] + dx, a[1]))
    side_b = field.tall((a[0], a[1] + dy))
    if corners == "no_cut":
        return not (side_a or side_b)
    return not (side_a and side_b)  # no_squeeze


@lru_cache(maxsize=64)
def _neighbour_table(field: Battlefield, corners: str) -> dict[Cell, tuple[Cell, ...]]:
    table: dict[Cell, tuple[Cell, ...]] = {}
    for cell in field.cells():
        table[cell] = tuple(
            (cell[0] + dx, cell[1] + dy)
            for dx, dy in STEPS
            if step_allowed(field, cell, (cell[0] + dx, cell[1] + dy), corners)
        )
    return table


def neighbours(field: Battlefield, cell: Cell, rule: GridRule) -> tuple[Cell, ...]:
    """Squares one legal step from cell, in STEPS order."""
    _check_metric(rule)
    return _neighbour_table(field, rule.corner_mode()).get(cell, ())


def _crosses_inside(p: Cell, q: Cell, box: tuple[int, int, int, int]) -> bool:
    """Does segment p-q pass through the open box (x0, x1) x (y0, y1)? (doubled coords)"""
    x0, x1, y0, y1 = box
    lo, hi = Fraction(0), Fraction(1)
    for start, delta, low, high in ((p[0], q[0] - p[0], x0, x1), (p[1], q[1] - p[1], y0, y1)):
        if delta == 0:
            if not low < start < high:
                return False
            continue
        t1, t2 = Fraction(low - start, delta), Fraction(high - start, delta)
        if t1 > t2:
            t1, t2 = t2, t1
        lo, hi = max(lo, t1), min(hi, t2)
    return lo < hi


@lru_cache(maxsize=65536)
def _clear(field: Battlefield, a: Cell, b: Cell) -> bool:
    if a == b:
        return True
    p = (2 * a[0] + 1, 2 * a[1] + 1)
    q = (2 * b[0] + 1, 2 * b[1] + 1)
    for x in range(min(a[0], b[0]), max(a[0], b[0]) + 1):
        for y in range(min(a[1], b[1]), max(a[1], b[1]) + 1):
            if (x, y) in (a, b) or not field.tall((x, y)):
                continue
            if _crosses_inside(p, q, (2 * x, 2 * x + 2, 2 * y, 2 * y + 2)):
                return False
    # Squeezing: the segment passes exactly through a corner point with tall squares on both
    # sides of it (the two squares it touches only at that point).
    dx, dy = q[0] - p[0], q[1] - p[1]
    if dx and dy:
        sx, sy = (1 if dx > 0 else -1), (1 if dy > 0 else -1)
        for cx in range(min(p[0], q[0]) + 1, max(p[0], q[0])):
            for cy in range(min(p[1], q[1]) + 1, max(p[1], q[1])):
                if cx % 2 or cy % 2 or (cx - p[0]) * dy != (cy - p[1]) * dx:
                    continue
                i, j = cx // 2, cy // 2
                # Square (i, j) has the corner point as its top-left; the touched squares sit
                # in the quadrants (sx, -sy) and (-sx, sy) around the point.
                side1 = (i if sx > 0 else i - 1, j - 1 if sy > 0 else j)
                side2 = (i - 1 if sx > 0 else i, j if sy > 0 else j - 1)
                if field.tall(side1) and field.tall(side2):
                    return False
    return True


def clear_line(field: Battlefield, a: Cell, b: Cell) -> bool:
    """A clear line for reach from square a to square b (terrain only)."""
    return _clear(field, a, b) if a <= b else _clear(field, b, a)


@lru_cache(maxsize=4096)
def _reach_cells(field: Battlefield, cell: Cell, reach: int, needs_line: bool) -> frozenset[Cell]:
    out = set()
    for x in range(cell[0] - reach, cell[0] + reach + 1):
        for y in range(cell[1] - reach, cell[1] + reach + 1):
            target = (x, y)
            if target == cell or not field.in_bounds(target) or not field.walkable(target):
                continue
            if needs_line and not clear_line(field, cell, target):
                continue
            out.add(target)
    return frozenset(out)


def reach_cells(field: Battlefield, cell: Cell, reach: int, rule: GridRule) -> frozenset[Cell]:
    """Squares a weapon of this reach threatens from cell. Squares no creature can stand on
    (walls, crates) are left out: nothing there to threaten."""
    _check_metric(rule)
    if reach <= 0:
        return frozenset()
    return _reach_cells(field, cell, reach, rule.reach_line())
