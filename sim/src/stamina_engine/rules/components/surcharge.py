"""On-turn surcharge (Packet: Actions and the On-Turn Surcharge)."""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class SurchargeRule(Component):
    cites = ("Packet: Actions and the On-Turn Surcharge", "Ledger CB-2")

    def surcharge(self, prior_actions: int) -> int:
        raise NotImplementedError


@register("surcharge", "linear")
@dataclass(frozen=True)
class LinearSurcharge(SurchargeRule):
    """Each action costs +slope for every action already taken this turn (v0.9: slope 1)."""

    slope: int = 1

    def surcharge(self, prior_actions: int) -> int:
        return self.slope * prior_actions
