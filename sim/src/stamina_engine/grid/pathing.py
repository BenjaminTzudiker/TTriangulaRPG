"""Pathing queries (ENGINE_PLAN: Battlefield). All are advisory: agents plan with them, and the
engine still executes every move square by square, re-checking threat at each step.

- reachable: the fewest squares to every square a mover could stop on.
- cheapest_path: the path to a goal that minimizes an agent-supplied cost: a price for each
  square left (avoidance, or expected OA cost) plus the movement stamina for the path's length.
- out_of_reach: squares no enemy threatens.

Searches visit neighbours in geometry.STEPS order, so ties always break the same way.
"""

from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from fractions import Fraction

from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.grid.geometry import neighbours
from stamina_engine.grid.threat import Body, blocked_squares, threatened_by
from stamina_engine.rules.components.grid import GridRule

cites = ("Packet: On-Turn Movement", "Packet: Off-Turn Movement", "Ledger MV-1", "Ledger MV-2")

Number = int | Fraction


@dataclass(frozen=True)
class Passage:
    """Where a mover may go: squares it can't enter, and squares it can pass but not stop in."""

    no_entry: frozenset[Cell] = frozenset()
    no_stop: frozenset[Cell] = frozenset()

    @staticmethod
    def for_mover(rule: GridRule, mover: str, team: str, bodies: Sequence[Body]) -> "Passage":
        no_entry, no_stop = blocked_squares(rule, mover, team, bodies)
        return Passage(no_entry, no_stop)


@dataclass(frozen=True)
class Reach:
    """Fewest squares to each square, with one shortest path to each."""

    start: Cell
    steps: dict[Cell, int]
    parent: dict[Cell, Cell]
    passage: Passage

    def destinations(self) -> dict[Cell, int]:
        """Squares the mover could end on (not its own, not occupied)."""
        return {
            c: n for c, n in self.steps.items() if c != self.start and c not in self.passage.no_stop
        }

    def path(self, goal: Cell) -> tuple[Cell, ...]:
        """The squares entered, in order, ending at goal."""
        if goal not in self.steps:
            raise KeyError(goal)
        out = []
        cell = goal
        while cell != self.start:
            out.append(cell)
            cell = self.parent[cell]
        return tuple(reversed(out))


def reachable(
    field: Battlefield, rule: GridRule, start: Cell, passage: Passage, limit: int
) -> Reach:
    steps: dict[Cell, int] = {start: 0}
    parent: dict[Cell, Cell] = {}
    frontier = [start]
    for n in range(1, limit + 1):
        nxt = []
        for cell in frontier:
            for nb in neighbours(field, cell, rule):
                if nb in steps or nb in passage.no_entry:
                    continue
                steps[nb] = n
                parent[nb] = cell
                nxt.append(nb)
        frontier = nxt
        if not frontier:
            break
    return Reach(start, steps, parent, passage)


@dataclass(frozen=True)
class Route:
    path: tuple[Cell, ...]  # squares entered, in order
    exposure: Number  # the summed price of the squares left
    movement: Number  # length_cost(len(path))

    @property
    def total(self) -> Number:
        return self.exposure + self.movement


def cheapest_path(
    field: Battlefield,
    rule: GridRule,
    start: Cell,
    goals: Iterable[Cell],
    passage: Passage,
    leave_cost: Callable[[Cell], Number],
    length_cost: Callable[[int], Number | None],
    limit: int,
) -> Route | None:
    """Exact: for each path length up to limit, the least-exposure path to every square,
    then the best goal and length overall. length_cost(n) is the movement stamina for n
    squares, or None if n squares can't be afforded. Ties go to the shorter path, then to
    the goal listed first."""
    goal_list = [g for g in goals if g not in passage.no_stop and g != start]
    goal_set = set(goal_list)
    layer: dict[Cell, tuple[Number, tuple[Cell, ...]]] = {start: (0, ())}
    best: tuple[Number, int, int, Route] | None = None
    for n in range(1, limit + 1):
        moving = length_cost(n)
        if moving is None:
            break
        nxt: dict[Cell, tuple[Number, tuple[Cell, ...]]] = {}
        for cell, (cost, path) in layer.items():
            left = cost + leave_cost(cell)
            for nb in neighbours(field, cell, rule):
                if nb in passage.no_entry:
                    continue
                if nb not in nxt or left < nxt[nb][0]:
                    nxt[nb] = (left, path + (nb,))
        layer = nxt
        for g in goal_set & set(layer):
            exposure, path = layer[g]
            route = Route(path, exposure, moving)
            key = (route.total, n, goal_list.index(g), route)
            if best is None or key[:3] < best[:3]:
                best = key
        if not layer:
            break
    return best[3] if best is not None else None


def out_of_reach(
    field: Battlefield, rule: GridRule, bodies: Sequence[Body], team: str, cells: Iterable[Cell]
) -> tuple[Cell, ...]:
    """The given squares that no active enemy of `team` threatens, in the order given."""
    threatened: set[Cell] = set()
    for b in bodies:
        if b.team != team:
            threatened |= threatened_by(field, rule, b)
    return tuple(c for c in cells if c not in threatened)
