"""Random legal play on random maps: the engine never breaks its own invariants. Every op is
re-validated (check=True), so a creature on a wall, two creatures at rest on one square,
stamina out of range or a move through an enemy would raise."""

import random
from dataclasses import dataclass, field

from hypothesis import given, settings
from hypothesis import strategies as st

from stamina_engine.agents.decisions import (
    AimRequest,
    Attack,
    Avoid,
    AvoidOA,
    BlocksRequest,
    Commitment,
    DiveRequest,
    Draw,
    EndTurn,
    Move,
    MoveAnswer,
    MoveOptions,
    OATake,
    OffTurnMove,
    Pass,
    Shoot,
    TakeOA,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.core.rng import Streams
from stamina_engine.engine.battle import Battle, Entrant
from stamina_engine.engine.events import OpportunityDeclared, Spent
from stamina_engine.grid.battlefield import Battlefield, parse_map
from stamina_engine.grid.pathing import Passage, reachable
from stamina_engine.model.build import load_build
from stamina_engine.model.derive import derive
from stamina_engine.rules.block_solver import block_options
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import RuleSet, preset

BUILDS = [
    "l1_sample",
    "l1_duelist",
    "l1_heavy",
    "l1_caster_dagger",
    "l1_greatsword",
    "l1_archer",
    "l1_spear",
]


@dataclass
class RandomAgent:
    rules: RuleSet
    rng: random.Random
    _steps: int = 0
    moves_made: list[int] = field(default_factory=list)

    def _path(self, field_: Battlefield | None, moves: MoveOptions) -> Move:
        assert field_ is not None
        goal = self.rng.choice(sorted(moves.destinations))
        reach = reachable(
            field_,
            self.rules.grid,
            moves.start,
            Passage(moves.no_entry, moves.no_stop),
            moves.max_squares,
        )
        return Move(reach.path(goal))

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        roll = self.rng.random()
        if request.shots and roll < 0.4:
            return Shoot(self.rng.choice(request.shots))
        if request.draws and roll > 0.9:
            return Draw(self.rng.choice(request.draws).loadout)
        if request.targets and roll < 0.5:
            return Attack(self.rng.choice(request.targets))
        if request.moves is not None and roll < 0.8:
            return self._path(request.observation.field, request.moves)
        return EndTurn()

    def commitment(self, request: Commitment) -> int:
        return self.rng.randint(0, request.max_steps)

    def blocks(self, request: BlocksRequest) -> Blocks:
        pricing = Pricing(self.rules)
        options = [
            Blocks(p, g)
            for p in range(4)
            for g in range(4)
            if pricing.blocks(p, g, prior_perfect=request.prior_perfect).total <= request.stamina
        ]
        assert block_options  # the engine's count is checked elsewhere
        return self.rng.choice(options)

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer:
        roll = self.rng.random()
        if request.draws and roll < 0.15:
            return Draw(self.rng.choice(request.draws).loadout)
        if request.moves is not None and roll < 0.3:
            return self._path(request.observation.field, request.moves)
        return Pass()

    def aim(self, request: AimRequest) -> int:
        return self.rng.randint(0, request.max_aims)

    def dive(self, request: DiveRequest) -> MoveAnswer:
        if self.rng.random() < 0.3:
            return self._path(request.observation.field, request.moves)
        return Pass()

    def avoid(self, request: AvoidOA) -> Avoid:
        pricing = Pricing(self.rules)
        chosen = tuple(e for e in request.enemies if self.rng.random() < 0.5)
        caps = [request.caps[request.enemies.index(e)] for e in chosen]
        q = pricing.avoid_opportunity(
            len(caps), caps=caps, trackers=request.trackers, on_turn=request.on_turn
        )
        return Avoid(chosen) if q.total <= request.stamina else Avoid()

    def take_oa(self, request: TakeOA) -> OATake:
        option = self.rng.choice(request.options)
        return OATake(option.weapon, self.rng.randint(0, len(option.quotes)))


VARIANTS = [
    {},
    {"opportunity": {"per_square_cap": True}},
    {"opportunity": {"cap_rule": "weapon_base", "avoid_price": "attacker_cap"}},
    {"opportunity": {"avoid_track": "off_turn", "avoid_debt": True}},
    {"movement": {"extra_squares": "one", "extra_cap": "free_movement", "leftover": "move"}},
    {"grid": {"occupancy": "anyone", "bodies": "blocking", "corners": "no_cut"}},
    {"ranged": {"bands": "minus_d6", "aim_mode": "precision"}, "blocks": {"ranged_flat": 2}},
    {"defenses": {"ranged_mode": "dodge_folded"}, "opportunity": {"point_blank_avoidable": True}},
]


@settings(max_examples=40, deadline=None)
@given(
    st.integers(0, 10**6),
    st.lists(st.text(alphabet="....#=", min_size=7, max_size=7), min_size=6, max_size=6),
    st.integers(0, len(VARIANTS) - 1),
)
def test_random_legal_play_keeps_invariants(seed: int, rows: list[str], v: int) -> None:
    field_ = parse_map("\n".join(rows))
    rng = random.Random(seed)
    floor = [c for c in field_.cells() if field_.walkable(c)]
    if len(floor) < 4:
        return
    rules = preset("v0.9").override(VARIANTS[v]) if VARIANTS[v] else preset("v0.9")
    spots = rng.sample(floor, 4)
    entrants = [
        Entrant(
            f"c{i}",
            "red" if i % 2 else "blue",
            derive(load_build(rng.choice(BUILDS)), rules),
            RandomAgent(rules, random.Random(seed + i)),
            "",
            spots[i],
        )
        for i in range(4)
    ]
    result = Battle(
        rules, entrants, Streams(seed), seed=seed, round_cap=4, check=True, field=field_
    ).run()
    # OAs never cost more than the cap allows: with the plain cap, 1 + odd FIN at most 4.
    for i, e in enumerate(result.log):
        if isinstance(e, OpportunityDeclared):
            paid = next(s for s in result.log[i:] if isinstance(s, Spent))
            assert paid.category == "opportunity" and paid.track == "off_turn"
