"""Initiative (Packet: Starting Combat and Turn Structure, Cunning)."""

from dataclasses import dataclass

from stamina_engine.core.dice import Dice
from stamina_engine.core.mathx import odd_count
from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class TurnOrderRule(Component):
    cites = ("Packet: Starting Combat and Turn Structure", "Packet: Cunning", "Ledger CB-9")
    allowed = {
        "tiebreak": frozenset({"reroll", "list_order", "higher_agility"}),
        # + 1 per odd Agility + 1 per odd Cunning (v0.9), or + Cunning, every point (0.9.1).
        "bonus": frozenset({"odd_agility_cunning", "cunning"}),
    }

    def initiative_bonus(self, agility: int, cunning: int) -> int:
        raise NotImplementedError

    def initiative_dice(self) -> Dice:
        raise NotImplementedError

    def tiebreak_mode(self) -> str:
        raise NotImplementedError


@register("turn_order", "v0_9")
@dataclass(frozen=True)
class V09Initiative(TurnOrderRule):
    """2d12 + 1 per odd Agility + 1 per odd Cunning (v0.9), or 2d12 + Cunning (0.9.1). Ties:
    the packet has no tiebreaker."""

    dice_count: int = 2
    dice_size: int = 12
    tiebreak: str = "reroll"
    bonus: str = "odd_agility_cunning"

    def initiative_bonus(self, agility: int, cunning: int) -> int:
        if self.bonus == "cunning":
            return cunning
        return odd_count(agility) + odd_count(cunning)

    def initiative_dice(self) -> Dice:
        return Dice(self.dice_count, self.dice_size)

    def tiebreak_mode(self) -> str:
        return self.tiebreak
