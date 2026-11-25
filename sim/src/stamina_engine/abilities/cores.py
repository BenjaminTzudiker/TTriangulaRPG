"""The class cores (Packet: Core Abilities). Each is simple, powerful and defining.

- Fighter: gain 3 strain to recover your normal stamina recovery now, at any time (here:
  on your turn, between turns, and before declaring blocks).
- Barbarian: gain 1 strain to recover the biggest stamina expenditure you spent on an attack
  step, at any time on your turn (here: the biggest step paid this turn not yet refunded).
- Monk: gain 1 strain: your perfect block costs don't escalate for the current attack.
- Rogue: gain 3 strain to take your turn now, skipping it later in the round; or skip your
  turn and take it after a later turn (engine/timeline.py runs the turn order).
"""

from collections.abc import Callable
from typing import TYPE_CHECKING

from stamina_engine.abilities.framework import Ability, Facts, register

if TYPE_CHECKING:
    from stamina_engine.engine.battle import Battle
    from stamina_engine.model.state import CombatantState

cites = ("Packet: Core Abilities", "Packet: Not in This Version", "Review F13", "Review F14")


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
    """Between turns: jump in if it hasn't acted (or come back if waiting). At its turn's
    start: wait, unless it's the last turn left in the round."""
    if c.id in b.state.acted:
        return False
    if window == "turn_start":
        return bool(facts.get("later", 0))
    return True


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


# --- Packet 0.12.0 strain-free martial class cores (resources.cores_mode == "in_fight") ---


def _second_wind_usable(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> bool:
    """Fighter (Second Wind): when it isn't your turn, recover normal recovery now and skip
    your next end-of-turn recovery (can't reuse until skipped). Costs 0 stamina, counts as
    an action (+1 escalation until your next turn ends)."""
    return (
        b.state.turn_of != c.id
        and not c.skip_next_recovery
        and (c.stamina + c.set_aside) < b.ops.max_stamina(c)
    )


def _second_wind_apply(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> None:
    b.ops.recover(c, c.profile.recovery)
    b.ops.set_skip_recovery(c, True)


SECOND_WIND = register(
    Ability(
        "second_wind",
        frozenset({"off_turn", "before_blocks"}),
        strain=0,
        stamina=0,
        usable=_second_wind_usable,
        apply=_second_wind_apply,
        cites=("Packet: Core Abilities",),
        action=True,
    )
)


def _press_wound_usable(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> bool:
    """Barbarian (Press the Wound): once on your turn, when a melee attack you make deals
    at least 1 HP damage to an enemy, recover stamina equal to your weapon's base cost."""
    return (
        b.state.turn_of == c.id
        and not c.press_wound_used
        and int(facts.get("injury", 0)) >= 1
        and int(facts.get("weapon_base", 0)) > 0
        and (c.stamina + c.set_aside) < b.ops.max_stamina(c)
    )


def _press_wound_apply(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> None:
    b.ops.mark_press_wound(c)
    b.ops.recover(c, int(facts["weapon_base"]))


PRESS_THE_WOUND = register(
    Ability(
        "press_the_wound",
        frozenset({"on_melee_wound"}),
        strain=0,
        stamina=0,
        usable=_press_wound_usable,
        apply=_press_wound_apply,
        cites=("Packet: Core Abilities",),
    )
)


def _poised_guard_usable(
    n: int,
) -> Callable[["Battle", "CombatantState", str, Facts], bool]:
    def check(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> bool:
        """Monk (Poised Guard): unarmored with no shield, when an enemy you hold makes a
        melee attack on you (including an OA), spend up to 2 held stamina on it so each
        spent point pays for one non-escalating perfect block."""
        if bool(facts.get("ranged", 0)) or int(facts.get("damage", 0)) <= 0:
            return False
        if c.gear.armor > 0 or c.gear.shield is not None:
            return False
        attacker = str(facts.get("attacker", ""))
        return c.holds.get(attacker, 0) >= n

    return check


def _poised_guard_apply(
    n: int,
) -> Callable[["Battle", "CombatantState", str, Facts], None]:
    def apply(b: "Battle", c: "CombatantState", window: str, facts: Facts) -> None:
        b.ops.spend_hold(c, str(facts["attacker"]), n)

    return apply


POISED_GUARD_1 = register(
    Ability(
        "poised_guard_1",
        frozenset({"before_blocks"}),
        strain=0,
        stamina=0,
        usable=_poised_guard_usable(1),
        apply=_poised_guard_apply(1),
        cites=("Packet: Core Abilities",),
    )
)

POISED_GUARD_2 = register(
    Ability(
        "poised_guard_2",
        frozenset({"before_blocks"}),
        strain=0,
        stamina=0,
        usable=_poised_guard_usable(2),
        apply=_poised_guard_apply(2),
        cites=("Packet: Core Abilities",),
    )
)
