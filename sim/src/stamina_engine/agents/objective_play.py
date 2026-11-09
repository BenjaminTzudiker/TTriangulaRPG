"""Playing a scenario objective (O1), shared by the scripted and tactical agents.

An agent's `objective` spec field is `kill` (the default: ignore objectives, exactly as
before; the control) or `first`. In `first` mode its role follows from its team:
- **pursuer** (its team holds the objective):
  - reach or escape, while it still counts: head for the zone or an exit, and flee from
    an exit as soon as it can; attack only what is in reach on the way;
  - hold: get into the zone, then stay there; attack what is in reach;
  - otherwise (it doesn't count, or has already reached the zone): fight as in kill mode;
- **denier** (the other team): attack the pursuer closest to its goal first, and in a hold
  with contested control, step into the zone when that is free.
"""

from dataclasses import dataclass

from stamina_engine.agents.decisions import MoveOptions, ObjectiveView, Observation
from stamina_engine.core.errors import ConfigError
from stamina_engine.grid.battlefield import Cell
from stamina_engine.grid.geometry import distance
from stamina_engine.rules.ruleset import RuleSet

cites = ("Packet: Running the Game",)

MODES = frozenset({"kill", "first"})


def check_mode(mode: str) -> str:
    if mode not in MODES:
        raise ConfigError(f"objective must be one of {sorted(MODES)}, not {mode!r}")
    return mode


@dataclass(frozen=True)
class Goal:
    view: ObjectiveView
    pursue: bool  # its team holds the objective
    counts: bool  # it is one of the creatures who still count (reach, escape) or can hold
    cells: tuple[Cell, ...]  # where it is going (zone squares, or exits)


def goal(obs: Observation) -> Goal | None:
    """The open objective as this creature sees it, or None."""
    if obs.field is None:
        return None
    for v in obs.objectives:
        if v.status != "open":
            continue
        pursue = v.team == obs.me.team
        cells = v.cells if v.kind != "escape" else obs.field.exits()
        if v.kind == "hold":
            counts = pursue and obs.me.id in v.who
        else:
            counts = pursue and obs.me.id in v.who and obs.me.id not in v.reached
        return Goal(v, pursue, counts, cells)
    return None


def goal_distance(rules: RuleSet, cell: Cell | None, cells: tuple[Cell, ...]) -> int:
    if cell is None or not cells:
        return 1 << 20
    return min(distance(cell, c, rules.grid) for c in cells)


def in_goal(obs: Observation, g: Goal) -> bool:
    return obs.me.pos is not None and obs.me.pos in g.cells


def denier_order(obs: Observation, rules: RuleSet, g: Goal, ids: tuple[str, ...]) -> list[str]:
    """Enemy pursuers who count first, closest to their goal first; then the rest."""

    def key(cid: str) -> tuple[int, int, str]:
        v = obs.view(cid)
        counting = v.id in g.view.who and (g.view.kind == "hold" or v.id not in g.view.reached)
        return (0 if counting else 1, goal_distance(rules, v.pos, g.cells), cid)

    return sorted(ids, key=key)


def open_goal_cells(obs: Observation, g: Goal, moves: MoveOptions) -> list[Cell]:
    """Goal squares it could end a move on."""
    return [c for c in g.cells if c in moves.destinations or c == obs.me.pos]


def closer_free(
    obs: Observation, rules: RuleSet, moves: MoveOptions, cells: tuple[Cell, ...]
) -> Cell | None:
    """With free movement only: a goal square if one is in reach, else the square that gets
    closest to one. None if it can't get any closer."""
    me = obs.me
    free = (me.free_move_left or 0) + (me.banked or 0)
    if me.pos is None or free <= 0:
        return None
    options = sorted(c for c, n in moves.destinations.items() if n <= free)
    if not options:
        return None
    now = goal_distance(rules, me.pos, cells)
    pick = min(options, key=lambda c: (goal_distance(rules, c, cells), moves.destinations[c], c))
    return pick if goal_distance(rules, pick, cells) < now else None
