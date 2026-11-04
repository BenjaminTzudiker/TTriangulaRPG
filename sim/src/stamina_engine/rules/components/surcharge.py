"""On-turn surcharge (Packet: Actions and the On-Turn Surcharge)."""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class SurchargeRule(Component):
    cites = ("Packet: Actions and the On-Turn Surcharge", "Ledger CB-2", "Review F8")

    def surcharge(self, prior_actions: int) -> int:
        raise NotImplementedError

    def light_discount(self) -> int:
        """Surcharge points a light weapon's steps don't pay (Review F8 option 2)."""
        return 0


@register("surcharge", "linear")
@dataclass(frozen=True)
class LinearSurcharge(SurchargeRule):
    """Each action costs +slope for every action already taken this turn (v0.9: slope 1)."""

    slope: int = 1
    # Review F8 option 2: light weapons' steps pay this much less surcharge (floored at 0),
    # so they cost base, base, base + 1... (0 as written).
    light_exempt: int = 0

    def surcharge(self, prior_actions: int) -> int:
        return self.slope * prior_actions

    def light_discount(self) -> int:
        return self.light_exempt
