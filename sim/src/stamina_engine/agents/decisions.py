"""Decision requests, their answers, and what a creature can observe when it decides.

Agents see the battle only through these: an Observation filtered by the information rule,
the legal options with their Pricing quotes, and the timing context.
"""

from dataclasses import dataclass
from typing import Protocol

from stamina_engine.model.derive import CombatProfile, LoadoutProfile
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Quote, Trackers

cites = ("Packet: Commitment", "Packet: Attack Procedure", "Packet: Blocking", "Review F11")


@dataclass(frozen=True)
class CombatantView:
    id: str
    team: str
    profile: CombatProfile
    gear: LoadoutProfile
    hp: int
    max_stamina: int
    stamina: int  # the true value, or the observer's estimate when stamina is hidden
    stamina_exact: bool  # False when stamina is an estimate
    status: str
    trackers: Trackers | None  # only for the observer itself


@dataclass(frozen=True)
class Observation:
    me: CombatantView
    others: tuple[CombatantView, ...]
    round: int

    def view(self, cid: str) -> CombatantView:
        if cid == self.me.id:
            return self.me
        for v in self.others:
            if v.id == cid:
                return v
        raise KeyError(cid)

    def enemies(self) -> tuple[CombatantView, ...]:
        return tuple(v for v in self.others if v.team != self.me.team)


# --- requests ------------------------------------------------------------------------


@dataclass(frozen=True)
class TurnCommand:
    """Each loop of a creature's own turn: attack a target in reach, or end the turn."""

    who: str
    observation: Observation
    context: tuple[str, ...]
    targets: tuple[str, ...]  # active enemies it can attack, with at least one step affordable

    @property
    def option_count(self) -> int:
        return len(self.targets) + 1


@dataclass(frozen=True)
class Attack:
    target: str


@dataclass(frozen=True)
class EndTurn:
    pass


TurnAnswer = Attack | EndTurn


@dataclass(frozen=True)
class Commitment:
    """After declaring an attack: how many steps. quotes[k - 1] is the price of k steps;
    0 withdraws the declaration at no cost."""

    who: str
    observation: Observation
    context: tuple[str, ...]
    target: str
    quotes: tuple[Quote, ...]

    @property
    def max_steps(self) -> int:
        return len(self.quotes)

    @property
    def option_count(self) -> int:
        return len(self.quotes) + 1


@dataclass(frozen=True)
class BlocksRequest:
    """After the roll: the defender sees the total and the critical dice, then blocks."""

    who: str
    observation: Observation
    context: tuple[str, ...]
    attacker: str
    damage: int
    crit_dice: int
    defense: int
    armor: int
    stamina: int
    prior_perfect: int
    affordable: int  # option counts (F11)
    nondominated: int

    @property
    def option_count(self) -> int:
        return self.affordable


class Agent(Protocol):
    def turn_command(self, request: TurnCommand) -> TurnAnswer: ...

    def commitment(self, request: Commitment) -> int: ...

    def blocks(self, request: BlocksRequest) -> Blocks: ...


@dataclass(frozen=True)
class DecisionRecord:
    """One logged decision: the F11 measurement."""

    round: int
    who: str
    kind: str  # turn_command, commitment, blocks
    option_count: int
    nondominated: int | None
    answer: str
    acted: bool  # differed from passing (attacked, committed steps, blocked)
    context: tuple[str, ...]
