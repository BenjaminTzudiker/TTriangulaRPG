"""Perfect and grazing blocks (Packet: Blocking)."""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register

RESETS = frozenset({"per_attack", "per_attacker_round", "per_round"})


@dataclass(frozen=True)
class BlockRule(Component):
    """reset says when the perfect-block escalation starts over (Assumptions register):

    - per_attack (v0.9): every attack starts at 1.
    - per_attacker_round: the count is kept per attacker and resets each round, so an
      attacker's later attacks in the same round continue it. One reading of review F6
      option 2 ("block count reset per attacker per round").
    - per_round: one count per defender per round, shared across attackers. The other
      reading.
    """

    cites = ("Packet: Blocking", "Ledger CB-3", "Ledger CB-4", "Review F3", "Review F6")
    allowed = {"reset": RESETS}

    graze_cost: int = 1
    graze_leak: int = 1
    reset: str = "per_attack"
    # Review F3 option 2: perfect blocks against a ranged attack cost this flat amount each
    # (no escalation). 0 is as written: the same escalation as melee.
    ranged_flat: int = 0

    def perfect_cost(self, nth: int) -> int:
        """Cost of the nth perfect block against one attack (nth starts at 1)."""
        raise NotImplementedError

    def ranged_perfect_cost(self, nth: int) -> int:
        return self.ranged_flat if self.ranged_flat > 0 else self.perfect_cost(nth)

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
