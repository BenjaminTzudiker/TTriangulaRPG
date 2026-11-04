"""A person's fight (`se play`) and its session log: one JSON object a line.

The first line describes the session (scenario, trial, seed, who played, the RuleSet digest
and the code stamp); then every decision in order, with the seconds each of the person's
took; then every attack (as `se run` tabulates them); then every event; then the result.
`se load --session` reads these back.
"""

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from stamina_engine.agents.human import HumanAgent, HumanIO, TerminalIO
from stamina_engine.core.errors import ConfigError
from stamina_engine.engine.battle import BattleResult
from stamina_engine.experiments.metrics import Row, attack_rows, decision_rows
from stamina_engine.experiments.runner import battle_for, trial_seed
from stamina_engine.experiments.scenario import Scenario
from stamina_engine.provenance import collect

cites = ("Packet: Starting Combat and Turn Structure", "Review F11")


@dataclass(frozen=True)
class Session:
    header: dict[str, Any]
    decisions: list[Row]
    attacks: list[Row]
    events: list[dict[str, Any]]
    result: dict[str, Any]


def play(
    scenario: Scenario,
    who: str,
    trial: int = 0,
    io: HumanIO | None = None,
    clock: Callable[[], float] = time.monotonic,
) -> tuple[BattleResult, int]:
    """One trial with a person playing `who`; everyone else keeps the scenario's agent and
    the dice are the trial's own, so the fight is comparable with the engine's."""
    if who not in {c.id for c in scenario.combatants}:
        raise ConfigError(f"no combatant {who!r}; ids: {[c.id for c in scenario.combatants]}")
    human = HumanAgent(scenario.rules, io or TerminalIO(), clock)
    seed = trial_seed(scenario.seed, scenario.name, trial)
    battle = battle_for(scenario, seed, check=True, agents={who: human})
    human.events = battle.log
    result = battle.run()
    human.events = None
    return result, seed


def write_session(
    path: Path, scenario: Scenario, who: str, trial: int, seed: int, result: BattleResult
) -> None:
    stamp = collect(scenario.rules, scenario.plugins)
    header = {
        "type": "session",
        "scenario": scenario.name,
        "trial": trial,
        "seed": str(seed),
        "played_by_human": who,
        "ruleset": scenario.rules.name,
        "ruleset_digest": scenario.rules.digest(),
        "stamp": stamp.text(),
    }
    lines = [json.dumps(header)]
    lines += [json.dumps({"type": "decision", **d}) for d in decision_rows(result, trial)]
    lines += [json.dumps({"type": "attack", **a}) for a in attack_rows(result, trial)]
    lines += [json.dumps({"type": "event", **json.loads(e.to_json())}) for e in result.log]
    lines.append(
        json.dumps(
            {
                "type": "result",
                "winner": result.winner,
                "reason": result.reason,
                "rounds": result.rounds,
                "log_sha256": result.log_sha256(),
            }
        )
    )
    path.write_text("\n".join(lines) + "\n")


def read_session(path: Path) -> Session:
    header: dict[str, Any] = {}
    decisions: list[Row] = []
    attacks: list[Row] = []
    events: list[dict[str, Any]] = []
    result: dict[str, Any] = {}
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"{path}:{n}: not JSON") from exc
        kind = d.pop("type", None)
        if kind == "session":
            header = d
        elif kind == "decision":
            decisions.append(d)
        elif kind == "attack":
            attacks.append(d)
        elif kind == "event":
            events.append(d)
        elif kind == "result":
            result = d
        else:
            raise ConfigError(f"{path}:{n}: unknown line type {kind!r}")
    if not header:
        raise ConfigError(f"{path}: no session header")
    return Session(header, decisions, attacks, events, result)
