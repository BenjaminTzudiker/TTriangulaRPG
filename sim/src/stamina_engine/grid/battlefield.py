"""Maps: a square grid of 5 ft cells loaded from ASCII (ENGINE_PLAN: Battlefield).

```text
; corridor.txt  (lines starting with ';' are comments)
#########
#A..#...#
#...=..1#
#########
```

Default legend: `.` floor, `#` wall, `=` low wall or crate, `o` pillar, `>` exit (floor a
creature can leave the map from, M4). Any other letter or
digit is a spawn marker on a floor square; a marker may repeat, and its squares are taken in
reading order. Outside the map counts as wall. Maps are at most 40 x 40.

Terrain, for M2 (Assumptions register): walls and pillars block movement, sight and reach;
low walls and crates block movement only (their cover arrives with ranged attacks in M3).
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from functools import cached_property
from importlib.resources import files
from pathlib import Path

from stamina_engine.core.errors import ConfigError

cites = ("Packet: Weapon Table", "Packet: Movement", "Packet: Cover")

Cell = tuple[int, int]  # (x, y): column, then row; (0, 0) is the top-left square

MAX_SIDE = 40


@dataclass(frozen=True)
class Terrain:
    name: str
    blocks_move: bool
    tall: bool  # blocks sight and reach (walls, pillars)


TERRAIN: dict[str, Terrain] = {
    "floor": Terrain("floor", False, False),
    "wall": Terrain("wall", True, True),
    "low": Terrain("low", True, False),
    "pillar": Terrain("pillar", True, True),
    "exit": Terrain("exit", False, False),  # floor a creature can leave the map from
}

DEFAULT_LEGEND: dict[str, str] = {
    ".": "floor",
    "#": "wall",
    "=": "low",
    "o": "pillar",
    ">": "exit",
}

OUTSIDE = TERRAIN["wall"]


@dataclass(frozen=True)
class Battlefield:
    name: str
    rows: tuple[str, ...]
    legend: tuple[tuple[str, str], ...]  # (character, terrain name), sorted
    spawn_list: tuple[tuple[str, tuple[Cell, ...]], ...] = field(compare=False)

    @property
    def width(self) -> int:
        return len(self.rows[0])

    @property
    def height(self) -> int:
        return len(self.rows)

    @cached_property
    def _terrain(self) -> dict[Cell, Terrain]:
        table = dict(self.legend)
        out: dict[Cell, Terrain] = {}
        for y, row in enumerate(self.rows):
            for x, ch in enumerate(row):
                out[(x, y)] = TERRAIN[table.get(ch, "floor")]
        return out

    @cached_property
    def spawns(self) -> Mapping[str, tuple[Cell, ...]]:
        return dict(self.spawn_list)

    def in_bounds(self, cell: Cell) -> bool:
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def terrain(self, cell: Cell) -> Terrain:
        return self._terrain.get(cell, OUTSIDE)

    def walkable(self, cell: Cell) -> bool:
        return not self.terrain(cell).blocks_move

    def tall(self, cell: Cell) -> bool:
        return self.terrain(cell).tall

    def is_exit(self, cell: Cell) -> bool:
        return self.terrain(cell).name == "exit"

    def exits(self) -> tuple[Cell, ...]:
        return tuple(c for c in self.cells() if self.is_exit(c))

    def cells(self) -> tuple[Cell, ...]:
        """Every square, in reading order."""
        return tuple((x, y) for y in range(self.height) for x in range(self.width))

    def spawn(self, marker: str) -> tuple[Cell, ...]:
        try:
            return self.spawns[marker]
        except KeyError:
            raise ConfigError(
                f"map {self.name} has no spawn {marker!r}; it has {sorted(self.spawns)}"
            ) from None

    def render(self, marks: Mapping[Cell, str] | None = None, spawns: bool = True) -> str:
        """The map with column and row numbers; marks overwrite squares (e.g. creatures).
        Without spawns, spawn markers are drawn as the floor they are."""
        marks = marks or {}
        if not spawns:
            marks = {**{c: "." for _, cells in self.spawn_list for c in cells}, **marks}
        tens = "".join(str(x // 10) if x >= 10 else " " for x in range(self.width))
        ones = "".join(str(x % 10) for x in range(self.width))
        lines = [f"    {tens}", f"    {ones}"] if self.width > 10 else [f"    {ones}"]
        for y, row in enumerate(self.rows):
            shown = "".join(marks.get((x, y), ch) for x, ch in enumerate(row))
            lines.append(f"{y:>3} {shown}")
        return "\n".join(lines)


def parse_map(text: str, name: str = "map", legend: Mapping[str, str] | None = None) -> Battlefield:
    table = dict(DEFAULT_LEGEND)
    for ch, terrain in (legend or {}).items():
        if len(ch) != 1:
            raise ConfigError(f"legend keys are single characters, not {ch!r}")
        if terrain not in TERRAIN:
            raise ConfigError(f"legend {ch!r} = {terrain!r}; terrain is one of {sorted(TERRAIN)}")
        table[ch] = terrain
    rows = [line.rstrip("\n") for line in text.splitlines()]
    rows = [r for r in rows if not r.startswith(";")]
    while rows and not rows[0].strip():
        rows.pop(0)
    while rows and not rows[-1].strip():
        rows.pop()
    if not rows:
        raise ConfigError(f"map {name} is empty")
    width = len(rows[0])
    if any(len(r) != width for r in rows):
        raise ConfigError(f"map {name}: every row must be {width} characters wide")
    if width > MAX_SIDE or len(rows) > MAX_SIDE:
        raise ConfigError(
            f"map {name} is {width} x {len(rows)}; the limit is {MAX_SIDE} x {MAX_SIDE}"
        )
    spawns: dict[str, list[Cell]] = {}
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch in table:
                continue
            if not ch.isalnum():
                raise ConfigError(f"map {name}: unknown character {ch!r} at ({x}, {y})")
            spawns.setdefault(ch, []).append((x, y))
    return Battlefield(
        name,
        tuple(rows),
        tuple(sorted(table.items())),
        tuple((m, tuple(cells)) for m, cells in sorted(spawns.items())),
    )


def library_maps() -> list[str]:
    folder = files("stamina_engine.data").joinpath("maps")
    return sorted(p.name.removesuffix(".txt") for p in folder.iterdir() if p.name.endswith(".txt"))


def load_map(
    name: str, base_dir: Path | None = None, legend: Mapping[str, str] | None = None
) -> Battlefield:
    """A library map by name (data/maps/<name>.txt), or a .txt path (relative to base_dir)."""
    if name.endswith(".txt"):
        path = Path(name)
        if not path.is_absolute() and base_dir is not None:
            path = base_dir / path
        try:
            text = path.read_text()
        except OSError as exc:
            raise ConfigError(f"can't read map {name}: {exc}") from exc
        return parse_map(text, path.stem, legend)
    resource = files("stamina_engine.data").joinpath("maps", f"{name}.txt")
    if not resource.is_file():
        raise ConfigError(f"no library map {name!r}; known: {library_maps()}")
    return parse_map(resource.read_text(), name, legend)
