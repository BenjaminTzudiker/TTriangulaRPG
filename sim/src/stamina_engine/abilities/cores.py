"""The class cores (Packet: Core Abilities). Each is simple, powerful and defining.

- Fighter: gain 3 strain to recover your normal stamina recovery now, at any time (here:
  on your turn, between turns, and before declaring blocks).
- Barbarian: gain 1 strain to recover the biggest stamina expenditure you spent on an attack
  step, at any time on your turn (here: the biggest step paid this turn not yet refunded).
- Monk: gain 1 strain: your perfect block costs don't escalate for the current attack.
- Rogue: gain 3 strain to take your turn now, skipping it later in the round; or skip your
  turn and take it after a later turn (engine/timeline.py runs the turn order).
"""

from typing import TYPE_CHECKING

from stamina_engine.abilities.framework import Ability, Facts, register

if TYPE_CHECKING:
    from stamina_engine.engine.battle import Battle
    from stamina_engine.model.state import CombatantState

cites = ("Packet: Core Abilities", "Packet: Strain", "Review F13", "Review F14")


def _below_max(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> bool:
    return c.stamina < b.ops.max_stamina(c)


def _recover(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> None:
    b.ops.recover(c, c.profile.recovery)


FIGHTER = register(
    Ability(
        "fighter_core",
        frozenset({"turn", "off_turn", "before_blocks"}),
        strain=3,
        stamina=0,
        usable=_below_max,
        apply=_recover,
        cites=("Packet: Core Abilities",),
    )
)


def _has_step(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> bool:
    return bool(c.step_costs) and c.stamina < b.ops.max_stamina(c)


def _refund(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> None:
    b.ops.recover(c, b.ops.refund_step(c))


BARBARIAN = register(
    Ability(
        "barbarian_core",
        frozenset({"turn"}),
        strain=1,
        stamina=0,
        usable=_has_step,
        apply=_refund,
        cites=("Packet: Core Abilities",),
    )
)


def _blocking(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> bool:
    return int(facts.get("damage", 0)) > 0


def _nothing(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> None:
    """The effect lives in the blocks step: the procedure prices perfect blocks flat."""


MONK = register(
    Ability(
        "monk_core",
        frozenset({"before_blocks"}),
        strain=1,
        stamina=0,
        usable=_blocking,
        apply=_nothing,
        cites=("Packet: Core Abilities",),
    )
)


def _rogue_can(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> bool:
    return c.id not in b.state.acted


ROGUE = register(
    Ability(
        "rogue_core",
        frozenset({"between_turns", "turn_start"}),
        strain=3,
        stamina=0,
        usable=_rogue_can,
        apply=_nothing,
        cites=("Packet: Core Abilities",),
    )
)
