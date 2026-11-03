"""What creatures can see of each other. Stamina visibility is unstated (Review F6)."""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class InformationRule(Component):
    cites = ("Packet: Commitment", "Review F6")
    allowed = {"stamina": frozenset({"public", "hidden"})}


@register("information", "v0_9")
@dataclass(frozen=True)
class V09Information(InformationRule):
    stamina: str = "public"
