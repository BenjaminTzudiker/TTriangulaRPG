"""Initiative (Packet: Starting Combat and Turn Structure). Data only until M1."""

from dataclasses import dataclass

from stamina_engine.core.dice import Dice
from stamina_engine.core.mathx import odd_count
from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class TurnOrderRule(Component):
    cites = ("Packet: Starting Combat and Turn Structure", "Ledger CB-9")
    allowed = {"tiebreak": frozenset({"reroll", "list_order", "higher_agility"})}

    def initiative_bonus(self, agility: int, cunning: int) -> int:
        raise NotImplementedError

    def initiative_dice(self) -> Dice:
        raise NotImplementedError

    def tiebreak_mode(self) -> str:
        raise NotImplementedError


@register("turn_order", "v0_9")
@dataclass(frozen=True)
class V09Initiative(TurnOrderRule):
    """2d12 + 1 per odd Agility + 1 per odd Cunning. Ties: packet has no tiebreaker."""

    dice_count: int = 2
    dice_size: int = 12
    tiebreak: str = "reroll"

    def initiative_bonus(self, agility: int, cunning: int) -> int:
        return odd_count(agility) + odd_count(cunning)

    def initiative_dice(self) -> Dice:
        return Dice(self.dice_count, self.dice_size)

    def tiebreak_mode(self) -> str:
        return self.tiebreak
