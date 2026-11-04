"""Battle = state + RuleSet + dice + broker + log. run() plays the fight to its end."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from stamina_engine.agents.broker import Broker
from stamina_engine.agents.decisions import Agent, DecisionRecord, Observation
from stamina_engine.core.errors import ConfigError
from stamina_engine.core.rng import DiceProvider
from stamina_engine.engine.arena import AllAdjacent, Arena, GridArena
from stamina_engine.engine.context import TimingContext
from stamina_engine.engine.events import Event, log_sha256
from stamina_engine.engine.ledger import PublicLedger
from stamina_engine.engine.observe import observe
from stamina_engine.engine.stateops import StateOps
from stamina_engine.grid.battlefield import Battlefield, Cell
from stamina_engine.model.derive import CombatProfile
from stamina_engine.model.state import BattleState, new_combatant
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import RuleSet


@dataclass(frozen=True)
class Entrant:
    """One combatant entering a battle."""

    id: str
    team: str
    profile: CombatProfile
    agent: Agent
    loadout: str = ""
    pos: Cell | None = None  # its starting square, on a map


@dataclass(frozen=True)
class BattleResult:
    winner: str | None  # winning team; None for a draw
    reason: str  # side_out or round_cap
    rounds: int
    order: tuple[str, ...]  # initiative order; order[0] moved first
    state: BattleState
    log: tuple[Event, ...]
    decisions: tuple[DecisionRecord, ...]

    def log_sha256(self) -> str:
        return log_sha256(self.log)


class Battle:
    def __init__(
        self,
        rules: RuleSet,
        entrants: Sequence[Entrant],
        dice: DiceProvider,
        *,
        seed: int,
        dice_mode: str = "named",
        round_cap: int = 30,
        check: bool = False,
        field: Battlefield | None = None,
    ) -> None:
        if len({e.id for e in entrants}) != len(entrants):
            raise ValueError("combatant ids must be unique")
        if field is not None and any(e.pos is None for e in entrants):
            raise ConfigError("on a map, every combatant needs a starting square")
        if field is None and any(e.pos is not None for e in entrants):
            raise ConfigError("starting squares need a map")
        self.rules = rules
        self.entrants = tuple(entrants)
        self.state = BattleState(
            tuple(new_combatant(e.id, e.team, e.profile, e.loadout) for e in entrants)
        )
        self.log: list[Event] = []
        self.ops = StateOps(self.state, rules, self.log, check, field)
        self.field = field
        self.arena: Arena = GridArena(field, rules) if field is not None else AllAdjacent()
        self.pricing = Pricing(rules)
        agents: Mapping[str, Agent] = {e.id: e.agent for e in entrants}
        self.broker = Broker(agents, self.pricing)
        self.context = TimingContext()
        self.dice = dice
        self.seed = seed
        self.dice_mode = dice_mode
        self.round_cap = round_cap
        self.outcome: tuple[str | None, str] | None = None  # (winner, reason) once over
        self.ledger: PublicLedger | None = None
        info = rules.information
        if info.stamina_visibility() == "hidden":
            if info.builds_visibility() != "known":
                raise ConfigError("hidden stamina with unknown builds needs priors (Phase 0)")
            self.ledger = PublicLedger(self.state, rules)
            self.ops.listeners.append(self.ledger.observe)

    def observe(self, who: str) -> Observation:
        return observe(self.state, self.rules, who, self.ledger, self.field)

    def run(self) -> BattleResult:
        from stamina_engine.engine.timeline import run_battle

        return run_battle(self)

    def check_end(self) -> bool:
        """A fight ends as soon as at most one side has an active member."""
        standing = {c.team for c in self.state.combatants if c.active}
        if len(standing) <= 1 and self.outcome is None:
            self.outcome = (next(iter(standing)) if standing else None, "side_out")
        return self.outcome is not None
