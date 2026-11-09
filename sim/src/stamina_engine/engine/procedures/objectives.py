"""Scenario objectives (O1): reach, escape and hold (Packet: Running the Game: combat
usually ends when one side "achieves its objective"; the packet defines no objective, so
every reading here is a scenario field or an Assumptions-register row).

Checks run with every fight-end check (after any injury, flee or surrender, after every
completed move when a scenario has an objective) and at the end of each round:
- reach: an active creature who counts and stands in the zone counts, once. Passing
  through a zone mid-path doesn't count: only where a move ends is checked;
- escape: a creature who counts and has fled counts;
- either succeeds once `count` have counted, and fails once too few who count are still
  active to make it up, or at the end of the deadline round;
- hold: scored at the end of each round by the scenario's control and score readings; it
  fails if not done by the end of the deadline round.
"""

from stamina_engine.engine.battle import Battle
from stamina_engine.model.objectives import (
    OPEN,
    ObjectiveSpec,
    controls,
    members,
    still_possible,
)
from stamina_engine.model.state import Status

cites = ("Packet: Running the Game",)


def settle(b: Battle) -> None:
    """Count new arrivals and escapes; resolve what can no longer go another way."""
    for spec in b.objectives:
        o = b.state.objectives[spec.id]
        if o.status != OPEN or spec.kind == "hold":
            continue
        for c in members(b.state, spec):
            if c.id in o.reached:
                continue
            if spec.kind == "reach":
                arrived = c.active and spec.zone is not None and c.pos in spec.zone
            else:
                arrived = c.status is Status.FLED
            if arrived:
                b.ops.objective_reached(spec.id, c.id)
                if o.progress >= spec.needed:
                    break
        if o.progress >= spec.needed:
            b.ops.resolve_objective(spec.id, True, spec.team)
        elif not still_possible(b.state, spec, o.progress):
            b.ops.resolve_objective(spec.id, False, spec.team)


def end_of_round(b: Battle) -> None:
    """Score holds; fail whatever is still open at the end of its deadline round."""
    settle(b)
    for spec in b.objectives:
        o = b.state.objectives[spec.id]
        if o.status != OPEN:
            continue
        if spec.kind == "hold":
            _score_hold(b, spec)
            if o.status != OPEN:
                continue
        if b.state.round >= spec.deadline:
            b.ops.resolve_objective(spec.id, False, spec.team)


def _score_hold(b: Battle, spec: ObjectiveSpec) -> None:
    o = b.state.objectives[spec.id]
    if spec.score == "final" and b.state.round < spec.deadline:
        return
    b.ops.objective_scored(spec.id, controls(b.state, spec))
    done = {
        "consecutive": o.streak >= spec.rounds,
        "cumulative": o.progress >= spec.rounds,
        "final": o.streak >= 1,
    }[spec.score]
    if done:
        b.ops.resolve_objective(spec.id, True, spec.team)
