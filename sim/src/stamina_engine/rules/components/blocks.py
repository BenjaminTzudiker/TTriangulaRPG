"""Perfect and grazing blocks (Packet: Blocking)."""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class BlockRule(Component):
    cites = ("Packet: Blocking", "Ledger CB-3", "Ledger CB-4")

    graze_cost: int = 1
    graze_leak: int = 1

    def perfect_cost(self, nth: int) -> int:
        """Cost of the nth perfect block against one attack (nth starts at 1)."""
        raise NotImplementedError

    def perfect_total(self, count: int) -> int:
        return sum(self.perfect_cost(i) for i in range(1, count + 1))


@register("blocks", "perfect_slope")
@dataclass(frozen=True)
class PerfectSlope(BlockRule):
    """The nth perfect block costs first + floor((n - 1) * num / den).

    v0.9 is 1, 2, 3... (slope 1/1). The review's half slope (1, 1, 2, 2...) is 1/2.
    """

    first: int = 1
    slope_num: int = 1
    slope_den: int = 1

    def perfect_cost(self, nth: int) -> int:
        return self.first + (nth - 1) * self.slope_num // self.slope_den
