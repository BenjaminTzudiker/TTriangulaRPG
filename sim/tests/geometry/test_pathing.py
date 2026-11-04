"""Pathing: reachable sets, exposure-priced paths and squares out of reach (ENGINE_PLAN
Verification 4: path costs with avoidance payments)."""

from hypothesis import given, settings
from hypothesis import strategies as st

from stamina_engine.grid.battlefield import Battlefield, Cell, parse_map
from stamina_engine.grid.geometry import distance, neighbours
from stamina_engine.grid.pathing import Passage, cheapest_path, out_of_reach, reachable
from stamina_engine.grid.threat import Body, threatening
from stamina_engine.rules.components.grid import V09Grid
from stamina_engine.rules.pricing import FRESH, Pricing
from stamina_engine.rules.ruleset import preset

GRID = V09Grid()
P = Pricing(preset("v0.9"))


def test_reachable_goes_around_walls() -> None:
    field = parse_map("....\n.##.\n....")
    reach = reachable(field, GRID, (0, 1), Passage(), 6)
    # Around the wall: diagonals past a single wall corner are allowed (no_squeeze).
    assert reach.path((3, 1)) == ((1, 0), (2, 0), (3, 1))
    assert reachable(field, GRID, (0, 1), Passage(), 2).steps.get((3, 1)) is None


def test_allies_passable_enemies_not_occupied_not_a_destination() -> None:
    field = parse_map("...\n...\n...")
    ally = Body("b", "red", (1, 0), (1,), True)
    enemy = Body("e", "blue", (1, 1), (1,), True)
    passage = Passage.for_mover(GRID, "a", "red", [ally, enemy])
    reach = reachable(field, GRID, (0, 1), passage, 3)
    assert (1, 1) not in reach.steps  # can't enter the enemy's square
    assert (1, 0) in reach.steps and (1, 0) not in reach.destinations()  # pass, don't stop
    assert reach.steps[(2, 1)] == 2
    assert (0, 1) not in reach.destinations()


SPEAR_FIELD = parse_map("\n".join(["......."] * 6))
SPEARMAN = Body("s", "blue", (3, 4), (2,), True)


def leave_price(cell: Cell) -> int:
    """Avoidance: 1 per enemy threatening the square left."""
    return len(threatening(SPEAR_FIELD, GRID, [SPEARMAN], "red", cell))


def test_detour_around_a_reach_when_avoidance_is_priced() -> None:
    passage = Passage.for_mover(GRID, "a", "red", [SPEARMAN])

    def moving(n: int) -> int:
        return P.move(
            n, on_turn=True, trackers=FRESH, free_left=6, movement=6, extra_squares=2
        ).total

    route = cheapest_path(SPEAR_FIELD, GRID, (0, 2), [(6, 2)], passage, leave_price, moving, 12)
    assert route is not None
    assert route.exposure == 0 and len(route.path) == 6  # through row 1, out of reach
    assert all(c[1] <= 1 for c in route.path[:-1])
    # When avoidance is free, the straight line is just as good and no longer.
    free = cheapest_path(SPEAR_FIELD, GRID, (0, 2), [(6, 2)], passage, lambda c: 0, moving, 12)
    assert free is not None and free.total == 0 and len(free.path) == 6


def test_detour_that_costs_a_purchase() -> None:
    """With 2 free squares and 1 square a purchase, the 4-square way round costs 2. It wins
    when the gap costs 3 to leave, ties at 2 (so the shorter path wins), loses at 1."""
    field = parse_map("...\n.#.\n...\n.#.\n...")
    start, goal, gap = (0, 2), (2, 2), (1, 2)

    def moving(n: int) -> int:
        return P.move(
            n, on_turn=True, trackers=FRESH, free_left=2, movement=2, extra_squares=1
        ).total

    for price, length in ((3, 4), (2, 2), (1, 2)):
        route = cheapest_path(
            field,
            GRID,
            start,
            [goal],
            Passage(),
            lambda c, p=price: p if c == gap else 0,
            moving,
            8,
        )
        assert route is not None and len(route.path) == length, price
        assert route.total == min(price, 2)


def test_unaffordable_lengths_stop_the_search() -> None:
    field = parse_map("......")
    route = cheapest_path(
        field, GRID, (0, 0), [(5, 0)], Passage(), lambda c: 0, lambda n: 0 if n <= 3 else None, 9
    )
    assert route is None


def test_out_of_reach() -> None:
    cells = SPEAR_FIELD.cells()
    safe = out_of_reach(SPEAR_FIELD, GRID, [SPEARMAN], "red", cells)
    assert (3, 1) in safe and (3, 2) not in safe and (0, 0) in safe
    assert out_of_reach(SPEAR_FIELD, GRID, [SPEARMAN], "blue", cells) == cells


maps = st.lists(st.text(alphabet="..#", min_size=6, max_size=6), min_size=6, max_size=6).map(
    lambda rows: parse_map("\n".join(rows))
)


def brute_force(field: Battlefield, start: Cell) -> dict[Cell, int]:
    dist = {start: 0}
    changed = True
    while changed:
        changed = False
        for cell, n in list(dist.items()):
            for nb in neighbours(field, cell, GRID):
                if dist.get(nb, 10**6) > n + 1:
                    dist[nb] = n + 1
                    changed = True
    return dist


@settings(max_examples=150, deadline=None)
@given(maps, st.tuples(st.integers(0, 5), st.integers(0, 5)))
def test_reachable_matches_brute_force(field: Battlefield, start: Cell) -> None:
    if not field.walkable(start):
        return
    reach = reachable(field, GRID, start, Passage(), 36)
    assert reach.steps == brute_force(field, start)
    for cell, n in reach.steps.items():
        path = reach.path(cell)
        assert len(path) == n
        prev = start
        for c in path:
            assert distance(prev, c, GRID) == 1 and c in neighbours(field, prev, GRID)
            prev = c
