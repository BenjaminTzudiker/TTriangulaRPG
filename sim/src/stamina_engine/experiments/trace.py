"""One fight, readable: its events in order, with the board drawn at the start of every turn.
For checking by eye that agents and procedures do what they should (`se trace`).

On the board each creature is a letter (its legend is printed first): capital while it can
fight, lower case once it is down, and `+` once it is dead.
"""

import json
from string import ascii_uppercase

from stamina_engine.engine.battle import BattleResult
from stamina_engine.engine.events import Event
from stamina_engine.experiments.runner import battle_for, trial_seed
from stamina_engine.experiments.scenario import Scenario
from stamina_engine.grid.battlefield import Cell

cites = ("Packet: Starting Combat and Turn Structure",)


def _line(e: Event) -> str:
    d = json.loads(e.to_json())
    kind = d.pop("event")
    fields = " ".join(f"{k}={v}" for k, v in d.items())
    return f"{kind}: {fields}"


class _Board:
    """Positions and status replayed from the log, for drawing."""

    def __init__(self, result: BattleResult) -> None:
        self.letters = {
            c.id: ascii_uppercase[i % 26] for i, c in enumerate(result.state.combatants)
        }
        self.pos: dict[str, Cell] = {}
        self.status: dict[str, str] = {c.id: "active" for c in result.state.combatants}

    def apply(self, e: Event) -> None:
        d = json.loads(e.to_json())
        kind = d["event"]
        if kind == "Placed":
            self.pos[d["who"]] = (d["pos"][0], d["pos"][1])
        elif kind == "Moved":
            self.pos[d["who"]] = (d["to"][0], d["to"][1])
        elif kind in ("Injured", "DyingRolled"):
            self.status[d["who"]] = d["status_after"]

    def marks(self) -> dict[Cell, str]:
        out: dict[Cell, str] = {}
        for cid, cell in self.pos.items():
            letter = self.letters[cid]
            status = self.status[cid]
            mark = letter if status == "active" else ("+" if status == "dead" else letter.lower())
            if cell not in out or status == "active":
                out[cell] = mark
        return out


def trace(scenario: Scenario, trial: int = 0, cell: str = "") -> str:
    seed = trial_seed(scenario.seed, cell or scenario.name, trial)
    result = battle_for(scenario, seed, check=True).run()
    board = _Board(result)
    field = scenario.battlefield
    lines = [
        f"{scenario.name}, trial {trial} (seed {seed}): {result.reason}, "
        f"winner {result.winner}, {result.rounds} rounds",
        "Creatures: "
        + ", ".join(f"{board.letters[c.id]} = {c.id} ({c.team})" for c in result.state.combatants),
        "",
    ]
    for e in result.log:
        board.apply(e)
        if type(e).__name__ == "TurnStarted" and field is not None:
            lines.append(field.render(board.marks(), spawns=False))
        lines.append(_line(e))
    return "\n".join(lines)
