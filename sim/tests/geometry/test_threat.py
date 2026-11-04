"""Threat maps and passing rules (ENGINE_PLAN Verification 4; readings C4 and C5)."""

from dataclasses import replace

from stamina_engine.grid.battlefield import parse_map
from stamina_engine.grid.threat import (
    Body,
    blocked_squares,
    body,
    can_pass,
    threatened_by,
    threatening,
)
from stamina_engine.model.build import Build, Loadout, load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.components.grid import V09Grid
from stamina_engine.rules.ruleset import preset

RULES = preset("v0.9")
GRID = V09Grid()
OPEN = parse_map("\n".join(["......."] * 7))


def gear(build: Build, loadout: str = "") -> object:
    profile = derive(build, RULES)
    return profile.loadout(loadout or profile.main.name)


def with_loadout(lo: Loadout, name: str = "test") -> Build:
    base = load_build("l1_sample")
    return replace(base, name=name, loadouts=(("main", lo),))


def test_sample_fighter_threatens_adjacent_squares() -> None:
    b = body("a", "red", (3, 3), derive(load_build("l1_sample"), RULES).main, True)
    assert threatened_by(OPEN, GRID, b) == {
        (x, y) for x in (2, 3, 4) for y in (2, 3, 4) if (x, y) != (3, 3)
    }


def test_spear_threatens_two_squares_and_walls_cut_it() -> None:
    spear = derive(
        with_loadout(Loadout(armor="medium", weapon="spear", grip="one", off_hand="shield")), RULES
    ).main
    assert spear.weapon is not None and spear.weapon.reach == 2
    b = body("s", "red", (3, 3), spear, True)
    assert len(threatened_by(OPEN, GRID, b)) == 24
    walled = parse_map(".......\n.......\n.......\n...#...\n.......\n.......\n.......")
    b = body("s", "red", (3, 1), spear, True)
    assert (3, 2) in threatened_by(walled, GRID, b)
    assert (3, 3) not in threatened_by(walled, GRID, b)  # the wall itself
    assert (3, 4) not in threatened_by(walled, GRID, b)  # behind it, out of reach anyway
    behind = body("s", "red", (3, 2), spear, True)
    assert (3, 4) not in threatened_by(walled, GRID, behind)  # the wall blocks the line


def test_off_hand_weapon_adds_its_reach() -> None:
    lo = Loadout(armor="medium", weapon="spear", grip="one", off_hand="dagger")
    g = derive(with_loadout(lo), RULES).main
    assert g.off_hand_weapon is not None
    b = body("s", "red", (3, 3), g, True)
    assert b.reaches == (2, 1)
    assert len(threatened_by(OPEN, GRID, b)) == 24


def test_what_threatens_nothing() -> None:
    caster = derive(load_build("l1_caster_unarmed"), RULES).main
    assert body("c", "red", (3, 3), caster, True).reaches == ()
    archer = derive(load_build("l1_archer"), RULES)
    assert body("a", "red", (3, 3), archer.loadout("bow"), True).reaches == ()
    assert body("a", "red", (3, 3), archer.loadout("blade"), True).reaches == (1,)
    sample = derive(load_build("l1_sample"), RULES).main
    assert threatened_by(OPEN, GRID, body("x", "red", (3, 3), sample, False)) == frozenset()


def test_threatening_lists_enemies_in_order() -> None:
    sample = derive(load_build("l1_sample"), RULES).main
    bodies = [
        body("c", "blue", (4, 3), sample, True),
        body("a", "blue", (2, 3), sample, True),
        body("ally", "red", (3, 4), sample, True),
        body("far", "blue", (6, 6), sample, True),
    ]
    assert threatening(OPEN, GRID, bodies, "red", (3, 3)) == ("c", "a")


def test_passing_rules() -> None:
    ally = Body("b", "red", (1, 1), (1,), True)
    enemy = Body("e", "blue", (2, 2), (1,), True)
    down = Body("d", "blue", (3, 3), (1,), False)
    assert can_pass(GRID, "red", ally) and not can_pass(GRID, "red", enemy)
    assert can_pass(GRID, "red", down)  # bodies are passable by default
    assert not can_pass(replace(GRID, bodies="blocking"), "red", down)
    assert can_pass(replace(GRID, occupancy="anyone"), "red", enemy)
    assert not can_pass(replace(GRID, occupancy="no_one"), "red", ally)
    no_entry, no_stop = blocked_squares(GRID, "a", "red", [ally, enemy, down])
    assert no_entry == {(2, 2)}
    assert no_stop == {(1, 1), (2, 2), (3, 3)}
