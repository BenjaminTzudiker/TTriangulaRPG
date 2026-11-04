"""Run the review's simulator (tests/oracle/sim.py) beside the engine, in lockstep.

Lockstep: the oracle's global `random` is swapped for random.Random(seed), and the engine
draws every die from SharedStream(seed). Both make the same calls in the same order, so each
fight should come out identical. The oracle files are only read, never edited, and its
variant knobs are always restored.

The oracle's 1v3 driver lives in experiments.py, which runs the whole review on import, so
`oracle_one_v_three` below is a line-for-line copy of its loop (experiments.py, section 6).
"""

import importlib.util
import random
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from stamina_engine.agents.scripted import make_agent
from stamina_engine.core.errors import ConfigError
from stamina_engine.core.rng import SharedStream
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.engine.events import (
    AttackDeclared,
    AttackResolved,
    AttackRolled,
    BlocksDeclared,
    Spent,
)
from stamina_engine.model.build import Build, load_build
from stamina_engine.model.derive import derive
from stamina_engine.provenance import PACKAGE_DIR
from stamina_engine.rules.ruleset import RuleSet

ORACLE_PATH = PACKAGE_DIR.parents[1] / "tests" / "oracle" / "sim.py"

_oracle: Any = None


def load_oracle(path: Path = ORACLE_PATH) -> Any:
    """Import the oracle by path. It exists only in a repo checkout."""
    global _oracle
    if _oracle is None:
        if not path.exists():
            raise ConfigError(f"the review's simulator isn't at {path}; run from a checkout")
        spec = importlib.util.spec_from_file_location("oracle_sim", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _oracle = module
    return _oracle


@dataclass(frozen=True)
class Knobs:
    """The oracle's module-level variant switches."""

    step_slope: int = 1
    block_slope: float = 1.0
    crit_mode: str = "double"

    def overrides(self) -> dict[str, dict[str, object]]:
        """The same variant as RuleSet overrides on top of review-sim."""
        crits: dict[str, dict[str, object]] = {
            "double": {"kind": "double_once"},
            "linear1": {"kind": "per_die_bonus", "bonus": 1},
            "linear2": {"kind": "per_die_bonus", "bonus": 2},
            "none": {"kind": "none"},
        }
        crit = crits[self.crit_mode]
        num, den = {1.0: (1, 1), 0.5: (1, 2)}[self.block_slope]
        return {
            "surcharge": {"slope": self.step_slope},
            "blocks": {"slope_num": num, "slope_den": den},
            "crit": crit,
        }


@contextmanager
def oracle_session(knobs: Knobs, seed: int) -> Iterator[Any]:
    """The oracle with its knobs set and its random swapped for a seeded stream."""
    sim = load_oracle()
    saved = (sim.STEP_SLOPE, sim.BLOCK_SLOPE, sim.CRIT_MODE, sim.random, sim.resolve_melee_attack)
    sim.STEP_SLOPE, sim.BLOCK_SLOPE, sim.CRIT_MODE = (
        knobs.step_slope,
        knobs.block_slope,
        knobs.crit_mode,
    )
    sim.random = random.Random(seed)
    try:
        yield sim
    finally:
        sim.STEP_SLOPE, sim.BLOCK_SLOPE, sim.CRIT_MODE, sim.random, sim.resolve_melee_attack = saved


# One attack, as both sides record it: (attacker, steps, total, crit dice, perfect, grazing,
# block stamina, injury).
AttackRecord = tuple[str, int, int, int, int, int, int, int]


@dataclass(frozen=True)
class FightRecord:
    winner: str | None  # a combatant id for duels, a team for 1v3; None for a draw
    rounds: int
    first: str
    attacks: tuple[AttackRecord, ...]
    final: tuple[tuple[str, int, int], ...]  # (id, hp, stamina)


def _record_attacks(sim: Any) -> list[AttackRecord]:
    """Wrap the oracle's resolve_melee_attack to record each attack it resolves."""
    original = sim.resolve_melee_attack
    out: list[AttackRecord] = []

    def recording(att: Any, dfn: Any, k: int, w: float = 3.0, log: Any = None) -> Any:
        d, c, p, g, bcost, inj = original(att, dfn, k, w, log)
        out.append((att.name, k, d, c, p, g, bcost, inj))
        return d, c, p, g, bcost, inj

    sim.resolve_melee_attack = recording
    return out


def oracle_policy(sim: Any, spec: str) -> Callable[..., int]:
    name, _, arg = spec.partition(":")
    if name == "alpha":
        return sim.pol_alpha  # type: ignore[no-any-return]
    if name == "fixed":
        return sim.pol_fixed(int(arg))  # type: ignore[no-any-return]
    if name == "reserve":
        return sim.pol_reserve(int(arg))  # type: ignore[no-any-return]
    if name == "chipkill":
        return sim.pol_chipkill  # type: ignore[no-any-return]
    if name == "lookahead":
        return sim.pol_greedy  # type: ignore[no-any-return]
    raise ConfigError(f"no oracle policy {spec!r}")


def oracle_duel(
    make_a: Callable[[Any], Any],
    make_b: Callable[[Any], Any],
    pol_a: str,
    pol_b: str,
    knobs: Knobs,
    seed: int,
    max_rounds: int = 30,
) -> FightRecord:
    with oracle_session(knobs, seed) as sim:
        a, b = make_a(sim), make_b(sim)
        a.name, b.name = "A", "B"
        attacks = _record_attacks(sim)
        winner, rounds, first = sim.duel(
            a, b, oracle_policy(sim, pol_a), oracle_policy(sim, pol_b), max_rounds=max_rounds
        )
        return FightRecord(
            winner.name if winner is not None else None,
            rounds,
            first.name,
            tuple(attacks),
            (("A", a.hp, a.stamina), ("B", b.hp, b.stamina)),
        )


def oracle_one_v_three(
    def_variant: str,
    att_policy: str,
    def_attacks: bool,
    knobs: Knobs,
    seed: int,
    att_variant: str = "sample",
    w: float = 3.0,
) -> FightRecord:
    """experiments.py one_v_three(), one trial, line for line."""
    with oracle_session(knobs, seed) as sim:
        attacks = _record_attacks(sim)
        pol = oracle_policy(sim, att_policy)
        d = sim.make_fighter(1, def_variant, "D")
        atts = [sim.make_fighter(1, att_variant, f"A{i}") for i in range(3)]
        order = sorted([d] + atts, key=lambda f: f.initiative(), reverse=True)
        r = 0
        finished = False
        while r < 20 and not finished:
            r += 1
            for actor in order:
                if actor.hp <= 0:
                    continue
                actor.on_turn_actions = 0
                if actor is d:
                    if def_attacks:
                        alive = [x for x in atts if x.hp > 0]
                        if alive:
                            tgt = min(alive, key=lambda x: (x.stamina, x.hp))
                            k = sim.pol_fixed(2)(d, tgt)
                            if k:
                                sim.resolve_melee_attack(d, tgt, k, w)
                else:
                    k = pol(actor, d)
                    if k:
                        sim.resolve_melee_attack(actor, d, k, w)
                    if d.hp <= 0:
                        finished = True
                        break
                actor.end_turn_recover()
        winner = "attackers" if finished else None
        return FightRecord(
            winner,
            r,
            order[0].name,
            tuple(attacks),
            tuple((f.name, f.hp, f.stamina) for f in [d, *atts]),
        )


def oracle_mk(sim: Any, level: int, md_target: int) -> Any:
    """grid.py mk(), line for line: a shield + medium fighter with the given Melee Defense."""
    if level == 1:
        if md_target == 4:
            f = sim.Fighter("X", STR=2, AGI=1, FIN=1, level=1)
        elif md_target == 5:
            f = sim.Fighter("X", STR=2, AGI=3, FIN=1, level=1)
        else:
            raise ValueError
    else:
        if md_target == 5:
            f = sim.Fighter("X", STR=3, AGI=2, FIN=2, CUN=1, level=30)
        elif md_target == 6:
            f = sim.Fighter("X", STR=3, AGI=3, FIN=2, CUN=1, level=30)
        elif md_target == 7:
            f = sim.Fighter("X", STR=3, AGI=6, FIN=2, level=30)
        else:
            raise ValueError
    f.weapon = sim.Weapon("ls", base=2, die=8, flat=f.STR + f.FIN)
    assert f.melee_defense() == md_target, (f.melee_defense(), md_target)
    return f


# Engine build -> how the oracle makes the same fighter.
ORACLE_FIGHTERS: dict[str, tuple[str, int, str | int]] = {
    "l1_sample": ("make", 1, "sample"),
    "l1_twohand": ("make", 1, "twohand"),
    "l1_greatsword": ("make", 1, "greatsword"),
    "l1_heavy": ("make", 1, "heavy"),
    "l1_duelist": ("make", 1, "duelist"),
    "l30_sample": ("make", 30, "sample"),
    "l30_strbrute": ("make", 30, "strbrute"),
    "l30_duelist": ("make", 30, "duelist"),
    "l30_heavy": ("make", 30, "heavy"),
    "l99_sample": ("make", 99, "sample"),
    "parity/l1_md5": ("mk", 1, 5),
    "parity/l30_md5": ("mk", 30, 5),
    "parity/l30_md7": ("mk", 30, 7),
}


def oracle_maker(build: str) -> Callable[[Any], Any]:
    how, level, arg = ORACLE_FIGHTERS[build]
    if how == "make":
        return lambda sim: sim.make_fighter(level, arg)
    return lambda sim: oracle_mk(sim, level, int(arg))


# --- the engine side -----------------------------------------------------------------


def engine_record(
    result: BattleResult, winner_of: Callable[[str | None], str | None]
) -> FightRecord:
    attacks: list[AttackRecord] = []
    current: dict[str, Any] = {}
    for e in result.log:
        if isinstance(e, AttackDeclared):
            current = {"attacker": e.attacker, "steps": e.steps, "block_cost": 0}
        elif isinstance(e, AttackRolled):
            current.update(total=e.total, crits=e.crit_dice)
        elif isinstance(e, BlocksDeclared):
            current.update(perfect=e.perfect, grazing=e.grazing)
        elif isinstance(e, Spent) and e.category == "block":
            current["block_cost"] = e.amount
        elif isinstance(e, AttackResolved):
            attacks.append(
                (
                    current["attacker"],
                    current["steps"],
                    current["total"],
                    current["crits"],
                    current.get("perfect", 0),
                    current.get("grazing", 0),
                    current["block_cost"],
                    e.injury,
                )
            )
    final = tuple((c.id, c.hp, c.stamina) for c in result.state.combatants)
    return FightRecord(
        winner_of(result.winner), result.rounds, result.order[0], tuple(attacks), final
    )


def engine_battle(
    rules: RuleSet,
    entrants: list[tuple[str, str, Build, str]],
    seed: int,
    round_cap: int,
    check: bool = False,
) -> BattleResult:
    """A lockstep battle: (id, team, build, agent spec) per combatant, sampled estimators."""
    dice = SharedStream(seed)
    built = [
        Entrant(
            cid,
            team,
            derive(build, rules),
            make_agent(
                {
                    "commit": spec,
                    "estimator": "sampled",
                    "target": "lowest_stamina" if cid == "D" else "first",
                },
                rules,
                dice.dice(f"agent:{cid}"),
            ),
        )
        for cid, team, build, spec in entrants
    ]
    return Battle(
        rules, built, dice, seed=seed, dice_mode="lockstep", round_cap=round_cap, check=check
    ).run()


def engine_duel(
    rules: RuleSet, a: Build, b: Build, pol_a: str, pol_b: str, seed: int, max_rounds: int = 30
) -> FightRecord:
    result = engine_battle(rules, [("A", "A", a, pol_a), ("B", "B", b, pol_b)], seed, max_rounds)
    return engine_record(result, lambda team: team)


def engine_one_v_three(
    rules: RuleSet,
    defender: Build,
    att_policy: str,
    def_attacks: bool,
    seed: int,
    attacker: Build | None = None,
) -> FightRecord:
    att = attacker or load_build("l1_sample")
    entrants = [("D", "defender", defender, "fixed:2" if def_attacks else "never")]
    entrants += [(f"A{i}", "attackers", att, att_policy) for i in range(3)]
    result = engine_battle(rules, entrants, seed, 20)
    return engine_record(result, lambda team: "attackers" if team == "attackers" else None)
