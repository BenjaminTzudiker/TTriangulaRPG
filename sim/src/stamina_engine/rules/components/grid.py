"""Grid geometry readings (Packet: Weapon Table reach, Movement, Opportunity Attacks).

The packet only says the grid uses 5 ft squares; every reading here is in the Assumptions
register.
"""

from dataclasses import dataclass

from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class GridRule(Component):
    cites = (
        "Packet: Weapon Table",
        "Packet: On-Turn Movement",
        "Packet: Triggers",
        "Packet: Cover",
        "Ledger MV-1",
        "Ledger MV-3",
        "Ledger RG-4",
    )
    allowed = {
        # alternating (5-10-5 diagonals) is recognized but not built yet (deferred).
        "metric": frozenset({"chebyshev", "alternating"}),
        "occupancy": frozenset({"allies_only", "anyone", "no_one"}),
        "creature_cover": frozenset({"half", "none"}),
        # A diagonal step past wall or pillar corners: blocked only when both orthogonal
        # neighbours are walls or pillars (no_squeeze), never (free), or when either is (no_cut).
        "corners": frozenset({"no_squeeze", "free", "no_cut"}),
        # Squares of incapacitated or dead creatures: anyone may pass through, or no one may.
        # Nobody may end a move in one either way.
        "bodies": frozenset({"passable", "blocking"}),
    }

    def metric_name(self) -> str:
        raise NotImplementedError

    def corner_mode(self) -> str:
        raise NotImplementedError

    def reach_line(self) -> bool:
        raise NotImplementedError

    def occupancy_mode(self) -> str:
        raise NotImplementedError

    def body_mode(self) -> str:
        raise NotImplementedError


@register("grid", "v0_9")
@dataclass(frozen=True)
class V09Grid(GridRule):
    metric: str = "chebyshev"
    occupancy: str = "allies_only"
    creature_cover: str = "half"
    reach_needs_line: bool = True
    corners: str = "no_squeeze"
    bodies: str = "passable"

    def metric_name(self) -> str:
        return self.metric

    def corner_mode(self) -> str:
        return self.corners

    def reach_line(self) -> bool:
        return self.reach_needs_line

    def occupancy_mode(self) -> str:
        return self.occupancy

    def body_mode(self) -> str:
        return self.bodies
