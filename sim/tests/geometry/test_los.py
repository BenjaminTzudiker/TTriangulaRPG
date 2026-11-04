"""Line of sight and cover, 5e corner method (ENGINE_PLAN Verification 4: LOS and cover cases,
including corner-grazing lines). Readings in the Assumptions register."""

from dataclasses import replace

from hypothesis import given, settings
from hypothesis import strategies as st

from stamina_engine.grid.battlefield import Battlefield, Cell, parse_map
from stamina_engine.grid.los import Cover, can_see, cover, line_blocked, terrain_cover
from stamina_engine.rules.components.grid import V09Grid

GRID = V09Grid()


def field(*rows: str) -> Battlefield:
    return parse_map("\n".join(rows))


def test_open_ground_no_cover() -> None:
    f = field(".....", ".....", ".....")
    assert cover(f, GRID, (0, 1), (4, 1)) is Cover.NONE
    assert cover(f, GRID, (0, 0), (4, 2)) is Cover.NONE


def test_solid_wall_is_total_cover() -> None:
    f = field(".....", "..#..", "..#..", "..#..", ".....")
    assert cover(f, GRID, (0, 2), (4, 2)) is Cover.TOTAL
    assert not can_see(f, GRID, (0, 2), (4, 2))
    # From further round the end of the wall, the shot is open again.
    assert cover(f, GRID, (0, 0), (4, 0)) is Cover.NONE


def test_single_pillar_gives_half_cover() -> None:
    f = field(".....", ".....", "..o..", ".....", ".....")
    assert cover(f, GRID, (0, 2), (4, 2)) is Cover.HALF


def test_low_wall_never_gives_total_cover() -> None:
    f = field(".....", "..=..", "..=..", "..=..", ".....")
    assert cover(f, GRID, (0, 2), (4, 2)) is Cover.THREE_QUARTERS
    assert can_see(f, GRID, (0, 2), (4, 2))


def test_creatures_give_half_cover_at_most() -> None:
    f = field(".....", ".....", ".....")
    assert cover(f, GRID, (0, 1), (4, 1), [(2, 1)]) is Cover.HALF
    assert cover(f, GRID, (0, 1), (4, 1), [(2, 0), (2, 1), (2, 2)]) is Cover.HALF
    off = replace(GRID, creature_cover="none")
    assert cover(f, off, (0, 1), (4, 1), [(2, 1)]) is Cover.NONE
    # The shooter's and target's own squares never count.
    assert cover(f, GRID, (0, 1), (4, 1), [(0, 1), (4, 1)]) is Cover.NONE


def test_lines_along_edges_and_through_corners() -> None:
    solid = {(2, 1), (2, 2)}

    def blocks(c: Cell) -> bool:
        return c in solid

    # Along the outside edge of a wall: not blocked.
    assert not line_blocked((3, 0), (3, 3), blocks, frozenset())
    # Along the seam between two wall squares: blocked.
    assert line_blocked((0, 2), (4, 2), blocks, frozenset())
    # Through the inside of a wall square: blocked.
    assert line_blocked((0, 0), (4, 3), blocks, frozenset())
    # Through a corner point between two diagonal walls: blocked (squeezing).
    pillars = {(2, 1), (1, 2)}
    assert line_blocked((1, 1), (3, 3), lambda c: c in pillars, frozenset())
    # Touching one wall's corner only: not blocked.
    assert not line_blocked((1, 1), (3, 3), lambda c: c == (2, 1), frozenset())


def test_shooter_picks_its_best_corner() -> None:
    # A wall square right in front of the shooter: every corner has two lines through it.
    f = field("......", ".#....", "......")
    assert cover(f, GRID, (0, 1), (5, 1)) is Cover.HALF
    # Corners differ when the wall is off to one side: the best one is used.
    g = field("......", "......", ".#....", "......")
    levels = terrain_cover(g, (0, 1), (5, 3))
    assert len(set(levels)) > 1
    assert cover(g, GRID, (0, 1), (5, 3)) == min(levels)


maps = st.lists(st.text(alphabet="...#=o", min_size=6, max_size=6), min_size=6, max_size=6).map(
    lambda rows: parse_map("\n".join(rows))
)
cells = st.tuples(st.integers(0, 5), st.integers(0, 5))


@settings(max_examples=150, deadline=None)
@given(maps, cells, cells, st.lists(cells, max_size=3))
def test_creatures_only_add_cover_and_adjacent_squares_see(
    f: Battlefield, a: Cell, b: Cell, others: list[Cell]
) -> None:
    plain = cover(f, GRID, a, b)
    assert plain == min(terrain_cover(f, a, b))
    assert cover(f, GRID, a, b, others) >= plain
    if max(abs(a[0] - b[0]), abs(a[1] - b[1])) <= 1:
        assert plain < Cover.TOTAL  # shared corner points: always a clear line
