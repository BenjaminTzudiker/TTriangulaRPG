"""Map parsing and the library maps (ENGINE_PLAN: Battlefield)."""

import pytest
from typer.testing import CliRunner

from stamina_engine.cli import app
from stamina_engine.core.errors import ConfigError
from stamina_engine.grid.battlefield import library_maps, load_map, parse_map

SMALL = """
; a comment line
#####
#A.1#
#=o1#
#####
"""


def test_parse_terrain_and_spawns() -> None:
    field = parse_map(SMALL, "small")
    assert (field.width, field.height) == (5, 4)
    assert field.terrain((0, 0)).name == "wall"
    assert field.terrain((1, 2)).name == "low"
    assert field.terrain((2, 2)).name == "pillar"
    assert field.terrain((2, 1)).name == "floor"
    # A spawn marker is a floor square; a repeated marker keeps reading order.
    assert field.walkable((1, 1))
    assert field.spawn("A") == ((1, 1),)
    assert field.spawn("1") == ((3, 1), (3, 2))
    # Outside the map counts as wall.
    assert field.terrain((-1, 0)).name == "wall" and not field.walkable((9, 9))
    assert not field.tall((1, 2)) and field.tall((2, 2))
    with pytest.raises(ConfigError, match="no spawn"):
        field.spawn("Z")


def test_legend_override() -> None:
    field = parse_map("~.\n..", "l", {"~": "low"})
    assert field.terrain((0, 0)).name == "low"
    with pytest.raises(ConfigError, match="terrain is one of"):
        parse_map("..", "l", {"~": "lava"})


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("", "empty"),
        ("...\n..", "wide"),
        ("..~", "unknown character"),
        ("." * 41, "limit"),
        ("\n".join(["."] * 41), "limit"),
    ],
)
def test_parse_errors(text: str, message: str) -> None:
    with pytest.raises(ConfigError, match=message):
        parse_map(text)


def test_render_marks_creatures() -> None:
    field = parse_map(SMALL, "small")
    shown = field.render({(2, 1): "x"})
    assert "  1 #Ax1#" in shown


def test_library_maps_load() -> None:
    assert "open_12x12" in library_maps()
    for name in library_maps():
        field = load_map(name)
        assert field.spawns, name
    with pytest.raises(ConfigError, match="no library map"):
        load_map("nowhere")


def test_se_map_show() -> None:
    runner = CliRunner()
    out = runner.invoke(app, ["map", "show", "open_12x12"])
    assert out.exit_code == 0, out.output
    assert "open_12x12: 14 x 14" in out.output
    assert "spawn A: (4, 6)" in out.output
    assert runner.invoke(app, ["map", "list"]).output.split() == library_maps()
    assert runner.invoke(app, ["map", "show", "nowhere"]).exit_code != 0
