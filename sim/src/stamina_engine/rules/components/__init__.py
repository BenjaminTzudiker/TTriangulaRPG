"""One module per component kind. Importing this package registers every variant."""

from stamina_engine.rules.components import (
    blocks,
    crit,
    defenses,
    dying,
    grid,
    information,
    movement,
    off_turn,
    opportunity,
    ranged,
    resources,
    surcharge,
    turn_order,
    wounds,
)

__all__ = [
    "blocks",
    "crit",
    "defenses",
    "dying",
    "grid",
    "information",
    "movement",
    "off_turn",
    "opportunity",
    "ranged",
    "resources",
    "surcharge",
    "turn_order",
    "wounds",
]
