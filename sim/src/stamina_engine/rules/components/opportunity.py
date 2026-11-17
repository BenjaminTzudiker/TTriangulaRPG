"""Opportunity attacks: cap and avoidance (Packet: Opportunity Attacks)."""

from dataclasses import dataclass

from stamina_engine.core.errors import ConfigError
from stamina_engine.core.mathx import odd_count
from stamina_engine.rules.registry import Component, register


@dataclass(frozen=True)
class OpportunityRule(Component):
    cites = (
        "Packet: Avoiding Opportunity Attacks",
        "Packet: Making Opportunity Attacks",
        "Ledger MV-3",
        "Ledger MV-5",
        "Review F9",
        "Review F14",
        "Packet: Triggers",
    )
    allowed = {
        "timing": frozenset({"on_leave"}),
        # The cap: 1 + odd FIN (v0.9), the OA weapon's base cost + odd FIN (F9 option 1), or
        # none (0.9.1: the off-turn escalation is the only limit).
        "cap_rule": frozenset({"flat", "weapon_base", "none"}),
        # Price to deny one enemy for one square: flat (1), or that enemy's cap (F9 option 2).
        "avoid_price": frozenset({"flat", "attacker_cap"}),
        # Whether avoidance escalates and counts as an off-turn cost (F9 option 3): never,
        # always, or only when paid off-turn.
        "avoid_track": frozenset({"none", "off_turn", "off_turn_only"}),
        # The hold rule (experiments): when a holder's tokens come back (the start of its
        # next turn, or the end of it, right before it recovers), and whether holds are set
        # before or after the holder recovers.
        "hold_return": frozenset({"turn_start", "turn_end"}),
        "hold_set": frozenset({"after_recovery", "before_recovery"}),
        # When a wound lowers a holder's maximum below ready stamina plus tokens, which comes
        # off first: ready stamina (then ended holds, then live ones), or tokens (ended holds,
        # then live ones, then ready stamina; the designer's placeholder of 2026-11-17).
        "hold_wound_clamp": frozenset({"ready_first", "tokens_first"}),
        # Which enemies a point-blank shot's OAs come from: those threatening the shooter
        # once the shot resolves (v0.9's reading), or (0.10.0) only those threatening it both
        # when the shot is declared and when the attacks happen.
        "point_blank_eligible": frozenset({"at_resolution", "declared_and_resolution"}),
        # How an OA's steps are priced: on the off-turn track (to 0.10.1), or "fresh"
        # (0.11.0 on): base + 1 per earlier step of this OA, on no track.
        "pricing": frozenset({"track", "fresh"}),
    }

    def cap(self, finesse: int, weapon_base: int = 0) -> int | None:
        """The most one opportunity attack may cost, or None for no cap."""
        raise NotImplementedError

    def avoid_cost(self, enemies: int) -> int:
        raise NotImplementedError

    def avoid_part(self, enemy_cap: int | None) -> int:
        """The base price of denying one enemy whose cap is enemy_cap, before any escalation."""
        raise NotImplementedError

    def avoid_on_track(self, on_turn: bool) -> bool:
        raise NotImplementedError

    def allows_debt(self) -> bool:
        raise NotImplementedError

    def attacks_allowed(self) -> bool:
        """False reproduces the review's duels and 1v3 runs, which had no OAs."""
        raise NotImplementedError

    def per_square(self) -> bool:
        raise NotImplementedError

    def point_blank_avoid(self) -> bool:
        """Can the shooter pay to avoid the OAs a point-blank shot provokes? (Not for now.)"""
        raise NotImplementedError

    def point_blank_needs_declared(self) -> bool:
        """Must an enemy have threatened the shooter when the shot was declared to get its
        point-blank OA?"""
        raise NotImplementedError

    def fresh_pricing(self) -> bool:
        return False

    def step_limit(self) -> int:
        """Most steps in one OA; 0 for no limit."""
        return 0

    def holds_on(self) -> bool:
        """The hold rule (designer, 2026-11-17)."""
        return False

    def holds_return_at_turn_end(self) -> bool:
        return False

    def holds_set_before_recovery(self) -> bool:
        return False

    def holds_break_on_injury(self) -> bool:
        return False

    def wound_clamps_tokens_first(self) -> bool:
        """A wound that lowers maximum stamina takes tokens before ready stamina."""
        return False

    def hold_limit(self, stamina: int) -> int:
        """Most tokens a creature with this much ready stamina may set."""
        return stamina


@register("opportunity", "v0_9")
@dataclass(frozen=True)
class V09Opportunity(OpportunityRule):
    """Cap 1 + 1 per odd Finesse (v0.9; none from 0.9.1); avoiding costs 1 per enemy per
    square, never escalating."""

    cap_base: int = 1
    cap_per_odd_finesse: int = 1
    avoid_cost_each: int = 1
    avoid_debt: bool = False
    per_square_cap: bool = False  # the packet's optional rule
    point_blank_avoidable: bool = False
    timing: str = "on_leave"
    enabled: bool = True
    cap_rule: str = "flat"
    avoid_price: str = "flat"
    avoid_track: str = "none"
    point_blank_eligible: str = "at_resolution"
    # Experiments (exp/holds): 0.11.0's placeholder is pricing = fresh, max_steps = 1, no cap;
    # the hold rule is pricing = fresh, cap_rule = flat, holds = true.
    pricing: str = "track"
    max_steps: int = 0
    holds: bool = False  # meant for pricing = fresh (tokens pay on no track)
    hold_return: str = "turn_start"
    hold_set: str = "after_recovery"
    hold_breaks_on_injury: bool = False  # a holder that loses HP drops its holds
    hold_max_percent: int = 100  # tokens set at most this % of ready stamina (rounded down)
    hold_wound_clamp: str = "ready_first"

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.cap_rule == "none" and self.per_square_cap:
            raise ConfigError("opportunity.per_square_cap needs a cap (cap_rule isn't none)")
        if self.cap_rule == "none" and self.avoid_price == "attacker_cap":
            raise ConfigError("opportunity.avoid_price = attacker_cap needs a cap")

    def cap(self, finesse: int, weapon_base: int = 0) -> int | None:
        if self.cap_rule == "none":
            return None
        base = weapon_base if self.cap_rule == "weapon_base" else self.cap_base
        return base + self.cap_per_odd_finesse * odd_count(finesse)

    def avoid_cost(self, enemies: int) -> int:
        return self.avoid_cost_each * enemies

    def avoid_part(self, enemy_cap: int | None) -> int:
        if self.avoid_price == "attacker_cap":
            assert enemy_cap is not None  # refused with no cap (__post_init__)
            return enemy_cap
        return self.avoid_cost_each

    def avoid_on_track(self, on_turn: bool) -> bool:
        return self.avoid_track == "off_turn" or (
            self.avoid_track == "off_turn_only" and not on_turn
        )

    def allows_debt(self) -> bool:
        return self.avoid_debt

    def attacks_allowed(self) -> bool:
        return self.enabled

    def per_square(self) -> bool:
        return self.per_square_cap

    def point_blank_avoid(self) -> bool:
        return self.point_blank_avoidable

    def point_blank_needs_declared(self) -> bool:
        return self.point_blank_eligible == "declared_and_resolution"

    def fresh_pricing(self) -> bool:
        return self.pricing == "fresh"

    def step_limit(self) -> int:
        return self.max_steps

    def holds_on(self) -> bool:
        return self.holds

    def holds_return_at_turn_end(self) -> bool:
        return self.hold_return == "turn_end"

    def holds_set_before_recovery(self) -> bool:
        return self.hold_set == "before_recovery"

    def holds_break_on_injury(self) -> bool:
        return self.hold_breaks_on_injury

    def wound_clamps_tokens_first(self) -> bool:
        return self.hold_wound_clamp == "tokens_first"

    def hold_limit(self, stamina: int) -> int:
        return stamina * self.hold_max_percent // 100
