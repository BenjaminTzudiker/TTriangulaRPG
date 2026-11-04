"""Typed, append-only battle events. The log is the record of a fight: telemetry, replay
and determinism checks all read it."""

import hashlib
import json
from collections.abc import Iterable
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Event:
    def to_json(self) -> str:
        payload = {"event": type(self).__name__, **asdict(self)}
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class BattleStarted(Event):
    seed: int
    ruleset: str
    ruleset_digest: str
    combatants: tuple[str, ...]
    dice: str  # "named" or "lockstep"


@dataclass(frozen=True)
class InitiativeRolled(Event):
    rolls: tuple[tuple[str, int], ...]  # (combatant, total) in rolling order, rerolls appended
    order: tuple[str, ...]


@dataclass(frozen=True)
class RoundStarted(Event):
    round: int


@dataclass(frozen=True)
class TurnStarted(Event):
    who: str
    round: int


@dataclass(frozen=True)
class TurnEnded(Event):
    who: str


@dataclass(frozen=True)
class Spent(Event):
    who: str
    amount: int
    category: str  # attack, block, ...
    track: str  # none, on_turn, off_turn
    parts: tuple[int, ...]
    stamina_after: int


@dataclass(frozen=True)
class Indebted(Event):
    """Part of a Spent paid without stamina (only avoidance, with opportunity.avoid_debt)."""

    who: str
    owed: int
    debt_after: int


@dataclass(frozen=True)
class DebtPaid(Event):
    """Recovery that went to paying off debt before any stamina came back."""

    who: str
    amount: int
    debt_after: int


@dataclass(frozen=True)
class Recovered(Event):
    who: str
    amount: int
    wasted: int  # recovery lost at the cap
    stamina_after: int


@dataclass(frozen=True)
class Injured(Event):
    who: str
    damage: int
    hp_after: int
    shock_after: int
    stamina_after: int  # after the max-stamina clamp
    status_after: str


@dataclass(frozen=True)
class DyingRolled(Event):
    who: str
    total: int
    shock_after: int
    status_after: str


@dataclass(frozen=True)
class AttackDeclared(Event):
    attacker: str
    target: str
    steps: int


@dataclass(frozen=True)
class AttackRolled(Event):
    attacker: str
    faces: tuple[int, ...]
    total: int
    crit_dice: int


@dataclass(frozen=True)
class BlocksDeclared(Event):
    defender: str
    perfect: int
    grazing: int
    prior_perfect: int  # perfect blocks already counted against this attacker (reset variants)


@dataclass(frozen=True)
class AttackResolved(Event):
    attacker: str
    target: str
    damage: int
    crit_dice: int
    through_blocks: int
    leaked: int
    armor_applied: int
    injury: int


@dataclass(frozen=True)
class MapLoaded(Event):
    """Grid battles only, right after BattleStarted (so all-adjacent logs are unchanged)."""

    name: str
    width: int
    height: int
    rows_sha256: str


@dataclass(frozen=True)
class Placed(Event):
    who: str
    pos: tuple[int, int]


@dataclass(frozen=True)
class Moved(Event):
    who: str
    frm: tuple[int, int]
    to: tuple[int, int]
    how: str  # free, extra (bought on turn) or off_turn


@dataclass(frozen=True)
class OpportunityProvoked(Event):
    """The mover is leaving a square these enemies threaten (in the order they'd be asked)."""

    mover: str
    square: tuple[int, int]
    enemies: tuple[str, ...]


@dataclass(frozen=True)
class OpportunityAvoided(Event):
    mover: str
    square: tuple[int, int]
    enemies: tuple[str, ...]  # paid off for this square


@dataclass(frozen=True)
class OpportunityDeclared(Event):
    """An OA's steps, declared and paid like an attack's (AttackDeclared is on-turn only)."""

    attacker: str
    target: str
    weapon: str  # main or off_hand
    steps: int


@dataclass(frozen=True)
class BattleEnded(Event):
    reason: str  # side_out, round_cap
    winner: str | None  # winning team, or None for a draw
    round: int


def log_lines(events: Iterable[Event]) -> list[str]:
    return [e.to_json() for e in events]


def log_sha256(events: Iterable[Event]) -> str:
    return hashlib.sha256("\n".join(log_lines(events)).encode()).hexdigest()
