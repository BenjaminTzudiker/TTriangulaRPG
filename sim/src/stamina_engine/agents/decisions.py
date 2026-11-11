"""Decision requests, their answers, and what a creature can observe when it decides.

Agents see the battle only through these: an Observation filtered by the information rule,
the legal options with their Pricing quotes, and the timing context.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.model.derive import CombatProfile, LoadoutProfile
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Quote, Trackers

cites = (
    "Packet: Commitment",
    "Packet: Attack Procedure",
    "Packet: Blocking",
    "Packet: On-Turn Movement",
    "Packet: Off-Turn Movement",
    "Packet: Avoiding Opportunity Attacks",
    "Packet: Making Opportunity Attacks",
    "Packet: Ranged Attacks",
    "Packet: Cover",
    "Packet: Drawing Weapons",
    "Review F11",
)


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
    pos: Cell | None = None  # positions are public; None in the all-adjacent arena
    free_move_left: int | None = None  # only for the observer itself
    banked: int | None = None  # only for the observer itself


@dataclass(frozen=True)
class ObjectiveView:
    """A scenario objective and its progress: public information (Assumptions register)."""

    id: str
    kind: str  # reach, escape, hold
    team: str  # the side pursuing it
    who: tuple[str, ...]  # the creatures who count
    deadline: int
    cells: tuple[Cell, ...]  # its zone's squares (reach, hold); () for escape
    count: int  # reach, escape: how many must make it
    control: str  # hold: present, uncontested, majority
    score: str  # hold: consecutive, cumulative, final
    rounds: int  # hold: rounds of control needed
    progress: int
    streak: int
    reached: frozenset[str]
    status: str  # open, done, failed


@dataclass(frozen=True)
class Observation:
    me: CombatantView
    others: tuple[CombatantView, ...]
    round: int
    field: Battlefield | None = None  # the map; None in the all-adjacent arena
    order: tuple[str, ...] = ()  # initiative order
    objectives: tuple[ObjectiveView, ...] = ()  # the scenario's objectives, if any

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
class MoveOptions:
    """Where a creature can move right now. A path is any sequence of legal steps that ends
    on one of the destinations, at most max_squares long; it costs price_by_length[len]."""

    start: Cell
    on_turn: bool
    max_squares: int
    price_by_length: tuple[int, ...]  # [n] = stamina for n squares, n = 0..max_squares
    destinations: Mapping[Cell, int]  # squares it could end on -> fewest squares to get there
    no_entry: frozenset[Cell]  # squares it can't enter (enemies, as the rules have it)
    no_stop: frozenset[Cell]  # squares it can pass but not end on (occupied)

    @property
    def option_count(self) -> int:
        return len(self.destinations)


@dataclass(frozen=True)
class DrawOption:
    loadout: str
    quote: Quote


@dataclass(frozen=True)
class AbilityOption:
    """An ability usable now: its stamina quote (cost plus strain overage) and strain."""

    name: str
    quote: Quote
    strain: int


@dataclass(frozen=True)
class UseAbility:
    name: str


@dataclass(frozen=True)
class TurnCommand:
    """Each loop of a creature's own turn: move, attack a target in reach, shoot, draw, or
    end the turn."""

    who: str
    observation: Observation
    context: tuple[str, ...]
    targets: tuple[str, ...]  # active enemies it can attack, with at least one step affordable
    moves: MoveOptions | None = None  # None when it can't move (or there's no map)
    shots: tuple[str, ...] = ()  # enemies its ranged weapon can target, shot affordable
    draws: tuple[DrawOption, ...] = ()  # loadouts it can switch to now
    can_flee: bool = False  # standing on an exit square (M4)
    can_surrender: bool = False  # on a map, any active creature may (M4)
    abilities: tuple[AbilityOption, ...] = ()  # usable on its turn now (M5)

    @property
    def option_count(self) -> int:
        moves = self.moves.option_count if self.moves else 0
        extra = int(self.can_flee) + int(self.can_surrender) + len(self.abilities)
        return len(self.targets) + 1 + moves + len(self.shots) + len(self.draws) + extra


@dataclass(frozen=True)
class Attack:
    target: str


@dataclass(frozen=True)
class EndTurn:
    pass


@dataclass(frozen=True)
class Move:
    path: tuple[Cell, ...]  # the squares entered, in order


@dataclass(frozen=True)
class Pass:
    pass


@dataclass(frozen=True)
class Shoot:
    target: str


@dataclass(frozen=True)
class Draw:
    loadout: str


@dataclass(frozen=True)
class Flee:
    pass


@dataclass(frozen=True)
class Surrender:
    pass


TurnAnswer = Attack | Move | Shoot | Draw | Flee | Surrender | UseAbility | EndTurn
MoveAnswer = Move | Draw | UseAbility | Pass


@dataclass(frozen=True)
class OffTurnMove:
    """In an off-turn window: move (with off-turn purchases), draw another loadout, or pass."""

    who: str
    observation: Observation
    context: tuple[str, ...]
    moves: MoveOptions | None
    draws: tuple[DrawOption, ...] = ()
    abilities: tuple[AbilityOption, ...] = ()  # usable between turns (M5)

    @property
    def option_count(self) -> int:
        moves = self.moves.option_count if self.moves else 0
        return moves + len(self.draws) + len(self.abilities) + 1


@dataclass(frozen=True)
class AbilityRequest:
    """A timing window where abilities can fire (before blocks, between turns, ...): use
    one, or pass. `facts` describes the moment (the incoming roll before blocks, say)."""

    who: str
    observation: Observation
    context: tuple[str, ...]
    window: str
    options: tuple[AbilityOption, ...]
    facts: Mapping[str, int | str] = field(default_factory=dict)

    @property
    def option_count(self) -> int:
        return len(self.options) + 1


@dataclass(frozen=True)
class AimRequest:
    """After declaring a shot: how many aim steps. quotes[k] is the price of the shot with k
    aims (from 0); fewer than `required` aims miss at this range. penalty is what linear
    range bands take off the total at the target's square now (its reaction may change
    it)."""

    who: str
    observation: Observation
    context: tuple[str, ...]
    target: str
    band: str
    cover: int  # the target's cover now (0 none, 1 half, 2 three-quarters)
    required: int
    quotes: tuple[Quote, ...]
    penalty: int = 0

    @property
    def max_aims(self) -> int:
        return len(self.quotes) - 1

    @property
    def option_count(self) -> int:
        return len(self.quotes)


@dataclass(frozen=True)
class DiveRequest:
    """A shot at you has been rolled: react with off-turn movement (dive for cover, close
    in, back away), or don't. cover_after says the cover the shot would then face from each
    destination. Where the rules make moving pay for more than cover (0.10.0: range measured
    after the reaction, Ranged Defense for moving), the engine also says what you'd block
    from each destination: the total (damage_after) and your defense with cover
    (defense_after), and the same if you stay (damage, defense). armor is what the shot
    faces after Piercing, and limit its aim limit. Melee's Tactical Withdrawal uses this
    request too, with only the moves."""

    who: str
    observation: Observation
    context: tuple[str, ...]
    shooter: str
    damage: int  # the total to block if it stays
    crit_dice: int
    cover: int  # if it stays
    moves: MoveOptions
    cover_after: Mapping[Cell, int]
    defense: int | None = None  # if it stays (with cover); None if not given
    damage_after: Mapping[Cell, int] = field(default_factory=dict)
    defense_after: Mapping[Cell, int] = field(default_factory=dict)
    armor: int | None = None
    limit: int | None = None

    @property
    def option_count(self) -> int:
        return self.moves.option_count + 1


@dataclass(frozen=True)
class AvoidOA:
    """Leaving a threatened square: which threatening enemies to pay off for this square.
    The mover decides before any of them says whether it would attack."""

    who: str
    observation: Observation
    context: tuple[str, ...]
    leaving: Cell
    enemies: tuple[str, ...]  # threatening enemies, in the order they would be asked
    caps: tuple[int | None, ...]  # each enemy's OA cap here (None: no cap); prices variants
    on_turn: bool
    trackers: Trackers
    stamina: int
    affordable: int  # how many subsets of enemies it can pay for (F11)

    @property
    def option_count(self) -> int:
        return self.affordable


@dataclass(frozen=True)
class Avoid:
    enemies: tuple[str, ...] = ()  # the enemies paid off, in the request's order


@dataclass(frozen=True)
class OAOption:
    weapon: str  # "main" or "off_hand"
    name: str
    quotes: tuple[Quote, ...]  # quotes[k - 1] is the price of k steps, all within the cap


@dataclass(frozen=True)
class TakeOA:
    """An enemy left a square you threaten: attack it with steps within your cap, or not."""

    who: str
    observation: Observation
    context: tuple[str, ...]
    target: str
    leaving: Cell
    cap: int | None  # None: no cap (0.9.1), only stamina and the off-turn escalation
    options: tuple[OAOption, ...]  # one per ready melee weapon that reaches the square

    @property
    def option_count(self) -> int:
        return 1 + sum(len(o.quotes) for o in self.options)


@dataclass(frozen=True)
class OATake:
    weapon: str = "main"
    steps: int = 0  # 0 declines


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
    ranged: bool = False  # against a ranged attack (prices perfect blocks: blocks.ranged_flat)
    cover: int = 0  # the cover bonus included in defense
    flat_perfect: bool = False  # perfect blocks don't escalate for this attack (Monk core)
    limit: int | None = None  # a shot's aim limit: the most HP it can take before crits

    @property
    def option_count(self) -> int:
        return self.affordable


class Agent(Protocol):
    def turn_command(self, request: TurnCommand) -> TurnAnswer: ...

    def commitment(self, request: Commitment) -> int: ...

    def blocks(self, request: BlocksRequest) -> Blocks: ...

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer: ...

    def avoid(self, request: AvoidOA) -> Avoid: ...

    def take_oa(self, request: TakeOA) -> OATake: ...

    def aim(self, request: AimRequest) -> int: ...

    def dive(self, request: DiveRequest) -> MoveAnswer: ...

    def ability(self, request: AbilityRequest) -> "UseAbility | Pass": ...


@runtime_checkable
class Timed(Protocol):
    """An agent that times its answers (a person): the broker logs the seconds."""

    def take_seconds(self) -> float | None: ...


@dataclass(frozen=True)
class DecisionRecord:
    """One logged decision: the F11 measurement."""

    round: int
    who: str
    kind: str  # turn_command, commitment, blocks, off_turn_move, avoid, take_oa, aim, dive, ability
    option_count: int
    nondominated: int | None
    answer: str
    acted: bool  # differed from passing (attacked, committed steps, blocked)
    context: tuple[str, ...]
    seconds: float | None = None  # how long a human took to answer (human agents only)
