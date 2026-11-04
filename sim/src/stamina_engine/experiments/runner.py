"""Run scenarios: one seeded battle per trial, across processes if asked.

Each trial's seed derives from the master seed, the cell key and the trial number, so any
single fight can be re-run alone. The cell key leaves out the RuleSet, so different RuleSets
in a sweep or a comparison fight on the same dice (common random numbers).
"""

import hashlib
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field

from stamina_engine.agents.scripted import make_agent
from stamina_engine.core.rng import DiceProvider, SharedStream, Streams, derive_seed
from stamina_engine.engine.battle import Battle, BattleResult, Entrant
from stamina_engine.experiments.metrics import Row, attack_rows, decision_rows, fight_row
from stamina_engine.experiments.scenario import Scenario
from stamina_engine.model.derive import CombatProfile, derive
from stamina_engine.provenance import Provenance, collect
from stamina_engine.rules.plugins import load_plugin

cites = ("Packet: Starting Combat and Turn Structure",)


def trial_seed(master_seed: int, cell: str, trial: int) -> int:
    return derive_seed(master_seed, f"{cell}:{trial}")


def battle_for(scenario: Scenario, seed: int, check: bool = False) -> Battle:
    dice: DiceProvider = SharedStream(seed) if scenario.dice == "lockstep" else Streams(seed)
    profiles: dict[str, CombatProfile] = {}
    entrants = []
    for c in scenario.combatants:
        if c.build.name not in profiles:
            profiles[c.build.name] = derive(c.build, scenario.rules)
        agent = make_agent(
            dict(c.agent) if not isinstance(c.agent, str) else c.agent,
            scenario.rules,
            dice.dice(f"agent:{c.id}"),
        )
        entrants.append(Entrant(c.id, c.team, profiles[c.build.name], agent, c.loadout))
    return Battle(
        scenario.rules,
        entrants,
        dice,
        seed=seed,
        dice_mode=scenario.dice,
        round_cap=scenario.round_cap,
        check=check,
    )


def run_trial(scenario: Scenario, trial: int, cell: str = "", check: bool = False) -> BattleResult:
    return battle_for(
        scenario, trial_seed(scenario.seed, cell or scenario.name, trial), check
    ).run()


@dataclass
class RunResult:
    scenario: Scenario
    cell: str
    provenance: Provenance
    fights: list[Row] = field(default_factory=list)
    attacks: list[Row] = field(default_factory=list)
    decisions: list[Row] = field(default_factory=list)

    @property
    def run_id(self) -> str:
        """Deterministic: the same scenario, rules, code and plugins give the same id."""
        key = "|".join(
            [
                self.scenario.source,
                self.scenario.rules.digest(),
                self.provenance.source_sha256,
                self.cell,
                str(self.scenario.trials),
            ]
            + [p.sha256 for p in self.scenario.plugins]
        )
        return hashlib.sha256(key.encode()).hexdigest()[:16]


def _chunk(
    args: tuple[Scenario, str, Sequence[int], bool],
) -> tuple[list[Row], list[Row], list[Row]]:
    scenario, cell, trials, check = args
    fights, attacks, decisions = [], [], []
    for t in trials:
        seed = trial_seed(scenario.seed, cell, t)
        result = battle_for(scenario, seed, check).run()
        fights.append(fight_row(result, t, seed))
        attacks += attack_rows(result, t)
        decisions += decision_rows(result, t)
    return fights, attacks, decisions


def _init_worker(plugin_paths: Sequence[str]) -> None:
    for p in plugin_paths:
        load_plugin(p)


def run_scenario(
    scenario: Scenario,
    trials: int | None = None,
    workers: int = 1,
    cell: str = "",
    check: bool = False,
) -> RunResult:
    n = scenario.trials if trials is None else trials
    cell = cell or scenario.name
    chunks = [range(i, min(n, i + 250)) for i in range(0, n, 250)]
    jobs = [(scenario, cell, list(c), check) for c in chunks]
    if workers > 1 and len(jobs) > 1:
        with ProcessPoolExecutor(
            max_workers=workers, initializer=_init_worker, initargs=(scenario.plugin_paths,)
        ) as pool:
            parts = list(pool.map(_chunk, jobs))
    else:
        parts = [_chunk(j) for j in jobs]
    out = RunResult(scenario, cell, collect(scenario.rules, scenario.plugins))
    for fights, attacks, decisions in parts:
        out.fights += fights
        out.attacks += attacks
        out.decisions += decisions
    return out
