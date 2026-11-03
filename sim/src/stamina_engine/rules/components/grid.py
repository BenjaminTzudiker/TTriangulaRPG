"""Grid geometry readings (Packet: Weapon Table reach, Cover). Data only until M2."""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class GridRule(Component):
    cites = ("Packet: Weapon Table", "Packet: Cover", "Ledger RG-4")
    allowed = {
        "metric": frozenset({"chebyshev", "alternating"}),
        "occupancy": frozenset({"allies_only", "anyone", "no_one"}),
        "creature_cover": frozenset({"half", "none"}),
    }


@register("grid", "v0_9")
@dataclass(frozen=True)
class V09Grid(GridRule):
    metric: str = "chebyshev"
    occupancy: str = "allies_only"
    creature_cover: str = "half"
    reach_needs_line: bool = True
