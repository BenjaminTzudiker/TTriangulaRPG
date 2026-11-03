"""Wound rules beyond plain HP loss. v0.9 has none (Packet: Not in This Version)."""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class WoundRule(Component):
    cites = ("Packet: Not in This Version", "Ledger CB-5", "Ledger CR-6")


@register("wounds", "none")
@dataclass(frozen=True)
class NoWounds(WoundRule):
    """Everything past blocks and armor is HP damage; no cap, no max-stamina loss."""
