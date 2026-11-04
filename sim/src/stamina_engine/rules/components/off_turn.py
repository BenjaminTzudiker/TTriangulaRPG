"""Off-turn escalation (Packet: Off-Turn Escalation)."""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class OffTurnRule(Component):
    cites = (
        "Packet: Off-Turn Escalation",
        "Packet: Off-Turn Movement",
        "Ledger MV-2",
        "Ledger MV-4",
    )
    allowed = {
        "order": frozenset({"ascending_initiative", "descending_initiative"}),
        # Who is asked in the window after a turn: everyone (as written), or everyone except
        # the allies of the creature whose turn just ended (you still move after your own
        # turn and after an enemy's). A decision-load experiment, not a packet reading.
        "scope": frozenset({"all", "not_after_allies"}),
    }

    def cost(self, base: int, earlier_costs: int) -> int:
        raise NotImplementedError

    def purchase_base(self) -> int:
        raise NotImplementedError

    def max_purchases(self) -> int:
        """Most purchases in one off-turn move; 0 for no cap."""
        raise NotImplementedError

    def windows_open(self) -> bool:
        """False reproduces the review's duels, which had no off-turn movement."""
        raise NotImplementedError

    def order_mode(self) -> str:
        raise NotImplementedError

    def repeats(self) -> bool:
        raise NotImplementedError

    def restarts(self) -> bool:
        """After any move, start the pass over from the first creature in order (so the
        first in order may answer every move). With descending order this is the
        designer's declaration scheme: whoever wants to move, highest initiative first,
        and everyone may respond once a move is done."""
        raise NotImplementedError

    def scope_mode(self) -> str:
        raise NotImplementedError


@register("off_turn", "escalation")
@dataclass(frozen=True)
class Escalation(OffTurnRule):
    """Each off-turn cost is its base + slope per earlier off-turn cost since your turn began.

    enabled = false reproduces the review's duels, which had no off-turn movement.
    """

    slope: int = 1
    movement_base: int = 1
    order: str = "ascending_initiative"
    repeat_until_all_pass: bool = True
    enabled: bool = True
    purchase_cap: int = 0  # most purchases in one off-turn move; 0 means no cap (as written)
    restart_after_move: bool = False
    scope: str = "all"

    def cost(self, base: int, earlier_costs: int) -> int:
        return base + self.slope * earlier_costs

    def purchase_base(self) -> int:
        return self.movement_base

    def max_purchases(self) -> int:
        return self.purchase_cap

    def windows_open(self) -> bool:
        return self.enabled

    def order_mode(self) -> str:
        return self.order

    def repeats(self) -> bool:
        return self.repeat_until_all_pass

    def restarts(self) -> bool:
        return self.restart_after_move

    def scope_mode(self) -> str:
        return self.scope
