"""Playing a fight one decision at a time (`se play --step`), for a chat that runs one
command and reads its output before the next.

Nothing is kept between commands except the answers file. Each command rebuilds the trial
from its seed and replays every answer so far. At the first decision with no answer, it
stops and reports that decision. The engine is deterministic, so the same scenario, trial
and answers always reach the same state and the same next request (simulator requirements
R8.5), and a fight takes milliseconds to replay.

Answers are the lines a person types at `se play` (its help, per decision kind, is in the
request), and they're read and checked the same way. One answer is written per line, as
JSON: {"answer": "s T"}, optionally with "who" (checked against the decision). An answer
the engine can't use is reported with the reason and isn't consumed: with --answer it isn't
appended to the file, and a bad line already in the file is reported by its number.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from string import ascii_uppercase
from typing import Any, TypeVar

from stamina_engine.agents.broker import Broker
from stamina_engine.agents.decisions import Agent
from stamina_engine.agents.human import HELP, HumanAgent
from stamina_engine.agents.wire import request as wire_request
from stamina_engine.core.errors import ConfigError, RulesError
from stamina_engine.engine.battle import Battle, BattleResult
from stamina_engine.engine.events import Event
from stamina_engine.experiments.runner import battle_for, trial_seed
from stamina_engine.experiments.scenario import Scenario
from stamina_engine.model.state import Status
from stamina_engine.rules.pricing import Pricing

cites = ("Packet: Starting Combat and Turn Structure", "Review F11")

T = TypeVar("T")

AWAITING, OVER, INVALID = 10, 0, 11  # se play --step's exit codes

ANSWER_HELP = {
    "turn": "a [ID] attack, s [ID] shoot, m X,Y move there (the cheapest path), or m X,Y X,Y "
    "... for an exact path, d NAME draw, u NAME use an ability, f flee, surrender, e end "
    "the turn",
    "steps": "a number of attack steps (0 withdraws)",
    "aim": "a number of aim steps",
    "blocks": "a listed option's number, or two numbers, perfect then grazing",
    "off_turn": "m X,Y (or an exact path m X,Y X,Y ...), d NAME, u NAME, or p to pass",
    "avoid": "ids to pay off, all, or none",
    "take_oa": "a number of steps (0 declines), optionally after the weapon (off_hand 1)",
    "react": "m X,Y (or an exact path m X,Y X,Y ...), or p to stay",
    "ability": "u NAME, or p",
}


@dataclass(frozen=True)
class Answer:
    text: str
    who: str | None = None
    line: int | None = None  # its line in the answers file; None for --answer


class _Await(Exception):
    pass


class _Rejected(Exception):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


@dataclass
class _Feed:
    """The answers, in order, for every controlled combatant: HumanAgent's io."""

    answers: list[Answer]
    used: int = 0
    seen: int = 0  # events already reported, up to the last answered decision
    who: str = ""  # who the current decision is for
    text: str = ""  # the current decision, as se play shows it

    def show(self, text: str) -> None:
        if text.startswith("  That isn't one of the options"):
            raise _Rejected(text.strip())
        if not text.startswith("  ") or "\n" in text:
            self.text = text  # the request itself (event lines are indented one-liners)

    def ask(self, prompt: str) -> str:
        if self.used >= len(self.answers):
            raise _Await
        a = self.answers[self.used]
        self.used += 1
        if a.who is not None and a.who != self.who:
            raise _Rejected(f"this decision is {self.who}'s, not {a.who}'s")
        if a.text.strip() in ("?", "help"):
            raise _Rejected("help isn't an answer; the request lists the options")
        return a.text


class _Fixed:
    """Answers one request with a given answer, so a throwaway Broker can check it."""

    def __init__(self, name: str, answer: object) -> None:
        setattr(self, name, lambda request: answer)


@dataclass
class _Stepper:
    """Stands in for a controlled combatant: HumanAgent reads the answer, then the broker's
    own checks run on it before the battle sees it, so a bad answer is reported, not
    raised from inside the fight."""

    who: str
    human: HumanAgent
    feed: _Feed
    pricing: Pricing
    log: list[Event] = field(default_factory=list)
    current: object | None = None

    def _do(self, name: str, request: object) -> Any:
        self.current = request
        self.feed.who = self.who
        answer = getattr(self.human, name)(request)
        try:
            fixed: Any = _Fixed(name, answer)
            getattr(Broker({self.who: fixed}, self.pricing), name)(request)
        except RulesError as exc:
            raise _Rejected(str(exc)) from None
        self.feed.seen = len(self.log)
        return answer

    def __getattr__(self, name: str) -> Callable[[object], Any]:
        if name in _AGENT_METHODS:
            return lambda request: self._do(name, request)
        raise AttributeError(name)


_AGENT_METHODS = frozenset(
    {
        "turn_command",
        "commitment",
        "blocks",
        "off_turn_move",
        "avoid",
        "take_oa",
        "aim",
        "dive",
        "ability",
    }
)


@dataclass(frozen=True)
class StepResult:
    code: int  # OVER, AWAITING or INVALID
    report: dict[str, Any]
    used: int  # answers consumed
    result: BattleResult | None = None
    seed: int = 0


def read_answers(path: Path) -> list[Answer]:
    if not path.exists():
        return []
    out = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ConfigError(f"{path}:{n}: not JSON") from exc
        if isinstance(d, str):
            out.append(Answer(d, None, n))
        elif isinstance(d, dict) and isinstance(d.get("answer"), str):
            who = d.get("who")
            out.append(Answer(d["answer"], str(who) if who is not None else None, n))
        else:
            raise ConfigError(f'{path}:{n}: expected {{"answer": "..."}} or a JSON string')
    return out


def _marks(b: Battle) -> dict[tuple[int, int], str]:
    out: dict[tuple[int, int], str] = {}
    for i, c in enumerate(b.state.combatants):
        if c.pos is None:
            continue
        letter = ascii_uppercase[i % 26]
        mark = letter if c.active else ("+" if c.status is Status.DEAD else letter.lower())
        if c.pos not in out or c.active:
            out[c.pos] = mark
    return out


def step(scenario: Scenario, who: tuple[str, ...], trial: int, answers: list[Answer]) -> StepResult:
    """Replay the trial with these answers for the combatants in `who`."""
    ids = [c.id for c in scenario.combatants]
    for w in who:
        if w not in ids:
            raise ConfigError(f"no combatant {w!r}; ids: {ids}")
    feed = _Feed(list(answers))
    pricing = Pricing(scenario.rules)
    steppers = {w: _Stepper(w, HumanAgent(scenario.rules, feed), feed, pricing) for w in who}
    seed = trial_seed(scenario.seed, scenario.name, trial)
    agents: dict[str, Agent] = dict(steppers)
    battle = battle_for(scenario, seed, check=True, agents=agents)
    for s in steppers.values():
        s.log = battle.log
        s.human.events = battle.log
    legend = {
        ascii_uppercase[i % 26]: f"{c.id} ({c.team})" for i, c in enumerate(battle.state.combatants)
    }
    base: dict[str, Any] = {
        "scenario": scenario.name,
        "trial": trial,
        "seed": str(seed),
        "playing": list(who),
        "ruleset": scenario.rules.name,
        "ruleset_digest": scenario.rules.short_digest(),
    }

    def board() -> dict[str, Any]:
        if battle.field is None:
            return {}
        return {"map": battle.field.render(_marks(battle), spawns=False), "legend": legend}

    def since(n: int) -> list[Any]:
        return [json.loads(e.to_json()) for e in battle.log[n:]]

    try:
        result = battle.run()
    except _Await:
        current = steppers[feed.who]
        req = wire_request(current.current)
        report = {
            **base,
            "status": "awaiting",
            "answers_used": feed.used,
            "decision": {
                **req,
                "answer_help": ANSWER_HELP.get(req["kind"], HELP),
                "text": feed.text,
            },
            "events_since_last_decision": since(feed.seen),
            **board(),
        }
        return StepResult(AWAITING, report, feed.used, seed=seed)
    except _Rejected as exc:
        bad = feed.answers[feed.used - 1] if feed.used else None
        report = {
            **base,
            "status": "invalid",
            "reason": exc.reason,
            "answer": bad.text if bad else None,
            "answers_file_line": bad.line if bad else None,
            "answers_used": feed.used - 1,
        }
        return StepResult(INVALID, report, max(0, feed.used - 1), seed=seed)
    report = {
        **base,
        "status": "over",
        "answers_used": feed.used,
        "winner": result.winner,
        "reason": result.reason,
        "rounds": result.rounds,
        "log_sha256": result.log_sha256(),
        "events_since_last_decision": since(feed.seen),
        **board(),
    }
    return StepResult(OVER, report, feed.used, result, seed)


def answer_line(text: str, report: dict[str, Any]) -> str:
    """The answers-file line for an answer to the decision in report."""
    d = report.get("decision", {})
    return json.dumps({"who": d.get("who"), "kind": d.get("kind"), "answer": text})
