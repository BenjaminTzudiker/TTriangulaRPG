"""What creatures can see of each other. Stamina visibility is unstated (Review F6).

stamina: public, or hidden (observers see only what a table would: declared steps and blocks,
that recovery happened, wounds).
builds: known (observers know each creature's level and equipment, so its maximum stamina and
recovery) or unknown. With known builds every stamina change is public or computable, so a
careful observer can reconstruct hidden stamina exactly; "hidden" then changes bookkeeping,
not information. Unknown builds need priors and wait until Phase 0 asks for them.
"""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class InformationRule(Component):
    cites = ("Packet: Commitment", "Review F6")
    allowed = {
        "stamina": frozenset({"public", "hidden"}),
        "builds": frozenset({"known", "unknown"}),
    }

    def stamina_visibility(self) -> str:
        raise NotImplementedError

    def builds_visibility(self) -> str:
        raise NotImplementedError


@register("information", "v0_9")
@dataclass(frozen=True)
class V09Information(InformationRule):
    stamina: str = "public"
    builds: str = "known"

    def stamina_visibility(self) -> str:
        return self.stamina

    def builds_visibility(self) -> str:
        return self.builds
