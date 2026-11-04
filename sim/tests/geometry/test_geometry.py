"""Distance, steps around corners and reach lines (ENGINE_PLAN Verification 4), on
hand-drawn maps. Readings C1 and C2 in the Assumptions register."""

from dataclasses import replace

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from stamina_engine.core.errors import ConfigError
from stamina_engine.grid.battlefield import Battlefield, Cell, parse_map
from stamina_engine.grid.geometry import (
    clear_line,
    distance,
    neighbours,
    reach_cells,
    step_allowed,
)
from stamina_engine.rules.components.grid import V09Grid

RULE = V09Grid()


def test_chebyshev_distance() -> None:
    assert distance((0, 0), (3, 1), RULE) == 3
    assert distance((2, 2), (1, 1), RULE) == 1
    with pytest.raises(ConfigError, match="isn't built yet"):
        distance((0, 0), (1, 1), replace(RULE, metric="alternating"))


@pytest.mark.parametrize(
    ("rows", "corners", "allowed"),
    [
        # Walls on both sides of the diagonal: only "free" lets you squeeze through.
        (".#\n#.", "no_squeeze", False),
        (".#\n#.", "free", True),
        (".#\n#.", "no_cut", False),
        # A wall on one side: blocked only by "no_cut".
        (".#\n..", "no_squeeze", True),
        (".#\n..", "no_cut", False),
        # Pillars are tall like walls; low walls and crates aren't (C1).
        (".o\no.", "no_squeeze", False),
        (".=\n=.", "no_squeeze", True),
        (".=\n=.", "no_cut", True),
    ],
)
def test_diagonal_steps_past_corners(rows: str, corners: str, allowed: bool) -> None:
    field = parse_map(rows)
    assert step_allowed(field, (0, 0), (1, 1), corners) is allowed


def test_steps_never_enter_blocked_squares() -> None:
    field = parse_map(".#=\n...")
    assert not step_allowed(field, (0, 0), (1, 0), "free")  # wall
    assert not step_allowed(field, (1, 1), (2, 0), "free")  # crate
    assert not step_allowed(field, (0, 0), (2, 0), "free")  # not one square
    assert neighbours(field, (0, 0), RULE) == ((0, 1), (1, 1))


def test_spear_threatens_two_squares_on_open_ground() -> None:
    field = parse_map("\n".join(["....."] * 5))
    assert len(reach_cells(field, (2, 2), 2, RULE)) == 24
    assert reach_cells(field, (2, 2), 1, RULE) == {
        (x, y) for x in (1, 2, 3) for y in (1, 2, 3) if (x, y) != (2, 2)
    }
    assert reach_cells(field, (2, 2), 0, RULE) == frozenset()


def test_walls_and_pillars_cut_reach_low_walls_dont() -> None:
    assert (2, 0) not in reach_cells(parse_map(".#."), (0, 0), 2, RULE)
    assert (2, 0) not in reach_cells(parse_map(".o."), (0, 0), 2, RULE)
    assert (2, 0) in reach_cells(parse_map(".=."), (0, 0), 2, RULE)
    # Nothing can stand on a wall or crate, so neither is a threatened square.
    assert (1, 0) not in reach_cells(parse_map(".=."), (0, 0), 2, RULE)
    # Without the clear-line reading, distance alone decides.
    assert (2, 0) in reach_cells(parse_map(".#."), (0, 0), 2, replace(RULE, reach_needs_line=False))


def test_reach_past_a_corner() -> None:
    # S#.
    # ...
    field = parse_map(".#.\n...")
    threatened = reach_cells(field, (0, 0), 2, RULE)
    assert (1, 1) in threatened  # diagonal with one wall beside it
    assert (2, 1) not in threatened  # the line crosses the wall square
    assert (2, 0) not in threatened
    assert (0, 1) in threatened


def test_reach_cannot_squeeze_between_corners() -> None:
    # Reach 1 across a corner with walls on both sides, as for movement (C1, C2).
    assert (1, 1) not in reach_cells(parse_map(".#\n#."), (0, 0), 1, RULE)
    assert (1, 1) in reach_cells(parse_map(".#\n.."), (0, 0), 1, RULE)
    # A long diagonal through a corner point with tall squares on both sides.
    field = parse_map("...\n.#.\n#..")
    # From (0, 0) to (2, 2) the line passes the centre of the wall at (1, 1).
    assert not clear_line(field, (0, 0), (2, 2))
    squeeze = parse_map("...\n..#\n.#.")
    # From (1, 1) to (2, 2): corner point between walls at (2, 1) and (1, 2).
    assert not clear_line(squeeze, (1, 1), (2, 2))
    assert not clear_line(squeeze, (2, 2), (1, 1))


# --- properties on random small maps --------------------------------------------------

maps = st.lists(st.text(alphabet=".#=o", min_size=5, max_size=5), min_size=5, max_size=5).map(
    lambda rows: parse_map("\n".join(rows))
)
cells = st.tuples(st.integers(0, 4), st.integers(0, 4))


@settings(max_examples=200, deadline=None)
@given(maps, cells, cells)
def test_line_and_step_symmetry(field: Battlefield, a: Cell, b: Cell) -> None:
    assert clear_line(field, a, b) == clear_line(field, b, a)
    if field.walkable(a) and field.walkable(b):
        for corners in ("no_squeeze", "free", "no_cut"):
            assert step_allowed(field, a, b, corners) == step_allowed(field, b, a, corners)


@settings(max_examples=200, deadline=None)
@given(maps, cells)
def test_reach_grows_with_reach(field: Battlefield, cell: Cell) -> None:
    one, two = reach_cells(field, cell, 1, RULE), reach_cells(field, cell, 2, RULE)
    assert one <= two
    assert all(distance(cell, t, RULE) <= 2 and field.walkable(t) for t in two)
    assert all(distance(cell, n, RULE) == 1 for n in neighbours(field, cell, RULE))


@given(cells, cells, cells)
def test_triangle_inequality(a: Cell, b: Cell, c: Cell) -> None:
    assert distance(a, c, RULE) <= distance(a, b, RULE) + distance(b, c, RULE)
    assert distance(a, b, RULE) == distance(b, a, RULE)
