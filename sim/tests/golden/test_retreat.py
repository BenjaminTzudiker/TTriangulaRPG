"""Review Addendum 2: retreat cannot buy tempo on open ground."""

from fractions import Fraction

from stamina_engine.analysis.retreat import escape, retreat, table
from stamina_engine.grid.battlefield import parse_map
from stamina_engine.grid.geometry import distance
from stamina_engine.grid.pathing import Passage, reachable
from stamina_engine.rules.components.grid import V09Grid
from stamina_engine.rules.ruleset import preset

V09 = preset("v0.9")


def test_addendum_2_retreat_costs() -> None:
    """AGI 1: 4 purchases (1+2+3+4 = 10, +1 to avoid the OA); AGI 3: 3 (6, +1); AGI 5: 2
    (3, +1). The chaser (free movement 6, 2 squares a purchase) then pays 1."""
    expected = {1: (4, 10, 1, 1), 3: (3, 6, 1, 1), 5: (2, 3, 1, 1)}
    for agility, (purchases, movement, avoid, chaser) in expected.items():
        r = escape(V09, agility)
        assert (r.purchases, r.movement_cost, r.avoid_cost, r.chaser_cost) == (
            purchases,
            movement,
            avoid,
            chaser,
        ), agility
        assert r.distance == 8  # out of the chaser's free reach (6 + 1), and no farther
    # "Exchange rate 4:1 to 11:1 against the fleer."
    assert [escape(V09, a).ratio for a in (1, 3, 5)] == [11, 7, 4]


def test_using_every_square_bought() -> None:
    """The chaser's 1 assumes the fleer stops at distance 8-9. An AGI-3 fleer's 3 purchases
    give 9 squares: used in full it ends at 10 and the chaser pays 2 (3.5:1)."""
    full = retreat(V09, 3, 3, stop=False)
    assert (full.distance, full.fleer_cost, full.chaser_cost) == (10, 7, 2)
    assert full.ratio == Fraction(7, 2)
    assert retreat(V09, 1, 4, stop=False).chaser_cost == 1  # 8 squares: distance 9
    assert retreat(V09, 5, 2, stop=False).chaser_cost == 1
    more = retreat(V09, 5, 3, stop=False)
    assert (more.fleer_cost, more.chaser_cost) == (7, 3)
    rows = table(V09, 3, max_purchases=4)
    assert [(s.chaser_cost, f.chaser_cost) for s, f in rows] == [(0, 0), (0, 0), (1, 2), (1, 3)]


def test_the_grid_agrees() -> None:
    """On an open map the fleer needs 7 squares to reach a square 8 from the chaser, and
    the chaser's 6 free squares can't get adjacent to it."""
    field = parse_map("\n".join(["." * 20] * 20))
    grid = V09Grid()
    chaser, fleer = (5, 10), (6, 10)
    reach = reachable(field, grid, fleer, Passage(frozenset({chaser}), frozenset({chaser})), 9)
    far = [c for c, n in reach.steps.items() if distance(c, chaser, grid) >= 8]
    assert min(reach.steps[c] for c in far) == 7
    spot = (13, 10)
    chase = reachable(field, grid, chaser, Passage(), 6)
    assert not any(distance(c, spot, grid) <= 1 for c in chase.steps)
    chase = reachable(field, grid, chaser, Passage(), 8)
    assert any(distance(c, spot, grid) <= 1 for c in chase.steps)
