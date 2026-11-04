"""Candidate abilities (Packet: Candidate Abilities; Exploratory, not yet in trees). Feint
waits until contests are defined. Readings (Assumptions register):

- Heavy Swing: chosen as you declare a melee attack, before its steps: each step costs 1
  more stamina, and the attack ignores 2 more armor.
- Riposte: after you make at least one perfect block against a melee attack, and it has
  resolved, you may make an opportunity attack on the attacker (priced and capped as any OA).
- Tactical Withdrawal: in a melee attack's reactions step, pay 2 stamina to move up to one
  off-turn purchase's worth of squares (not an off-turn cost; it provokes as any move
  does). If the attacker no longer reaches you, the attack is avoided.
"""

from typing import TYPE_CHECKING

from stamina_engine.abilities.framework import Ability, Facts, register

if TYPE_CHECKING:
    from stamina_engine.engine.battle import Battle
    from stamina_engine.model.state import CombatantState

cites = ("Packet: Candidate Abilities", "Packet: Making Opportunity Attacks")


def _melee(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> bool:
    w = c.gear.weapon
    return w is not None and not w.ranged


def _nothing(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> None:
    """The effect lives in the procedure that opened the window."""


HEAVY_SWING = register(
    Ability(
        "heavy_swing",
        frozenset({"declare_attack"}),
        strain=0,
        stamina=0,
        usable=_melee,
        apply=_nothing,
        cites=("Packet: Candidate Abilities",),
    )
)


def _on_map(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> bool:
    return b.field is not None and c.pos is not None


WITHDRAWAL = register(
    Ability(
        "tactical_withdrawal",
        frozenset({"reactions"}),
        strain=0,
        stamina=2,
        usable=_on_map,
        apply=_nothing,
        cites=("Packet: Candidate Abilities",),
    )
)

RIPOSTE_NAME = "riposte"  # offered as an opportunity attack, not through a window
