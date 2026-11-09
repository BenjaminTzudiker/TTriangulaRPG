"""A person at the keyboard (`se play`): each request is printed with its options and
answered with a line of text, and timed (the broker logs the seconds with the decision).

The broker still checks every answer. This agent re-asks on a line it can't read or that
isn't among the options, so a typo never ends the fight. The CLI does some arithmetic a
table wouldn't: it prices each option, and for blocks it lists the pairs no other pair
beats, with their cost and injury. Seconds measured here are a lower bound on table time.

Answers (? at any prompt prints this):
- your turn: a [ID] attack, s [ID] shoot, m X,Y move there (the cheapest path), or
  m X,Y X,Y ... for an exact path, d NAME draw, u NAME use an ability, f flee,
  surrender, e end the turn;
- steps or aims: a number;
- blocks: a listed option's number, or two numbers, perfect then grazing;
- off-turn: m X,Y, d NAME, u NAME, or p to pass;
- avoiding OAs: ids to pay off, all, or none;
- taking an OA: a number of steps (0 declines), optionally after the weapon (off_hand 1);
- an ability window: u NAME, or p.
"""

import time
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from string import ascii_uppercase
from typing import Protocol, TypeVar

from stamina_engine.agents.decisions import (
    AbilityOption,
    AbilityRequest,
    AimRequest,
    Attack,
    Avoid,
    AvoidOA,
    BlocksRequest,
    Commitment,
    DiveRequest,
    Draw,
    DrawOption,
    EndTurn,
    Flee,
    Move,
    MoveAnswer,
    MoveOptions,
    OATake,
    ObjectiveView,
    Observation,
    OffTurnMove,
    Pass,
    Shoot,
    Surrender,
    TakeOA,
    TurnAnswer,
    TurnCommand,
    UseAbility,
)
from stamina_engine.core.errors import RulesError, Unaffordable
from stamina_engine.engine.events import Event
from stamina_engine.grid.battlefield import Cell
from stamina_engine.rules.exchange import Blocks, resolve
from stamina_engine.rules.pricing import Pricing
from stamina_engine.rules.ruleset import RuleSet

cites = ("Review F11", "Packet: Starting Combat and Turn Structure")

T = TypeVar("T")

HELP = __doc__.split("Answers (? at any prompt prints this):\n", 1)[1] if __doc__ else ""


class HumanIO(Protocol):
    def show(self, text: str) -> None: ...

    def ask(self, prompt: str) -> str: ...


class TerminalIO:
    def show(self, text: str) -> None:
        print(text)

    def ask(self, prompt: str) -> str:
        return input(prompt)


@dataclass
class ScriptedIO:
    """Lines typed in advance, for tests; what was shown is kept."""

    lines: list[str]
    shown: list[str] = field(default_factory=list)

    def show(self, text: str) -> None:
        self.shown.append(text)

    def ask(self, prompt: str) -> str:
        if not self.lines:
            raise EOFError("no more scripted input")
        return self.lines.pop(0)


class _Invalid(Exception):
    pass


def _cell(text: str) -> Cell:
    x, y = text.split(",")
    return (int(x), int(y))


def _pick(name: str | None, options: Sequence[str]) -> str:
    """The named option, or the only one if no name is given."""
    if name is None:
        if len(options) == 1:
            return options[0]
        raise _Invalid
    if name not in options:
        raise _Invalid
    return name


@dataclass
class HumanAgent:
    rules: RuleSet
    io: HumanIO = field(default_factory=TerminalIO)
    clock: Callable[[], float] = time.monotonic
    events: list[Event] | None = None  # the battle's log, to print what happened between asks
    _seen: int = field(default=0, init=False)
    _seconds: float | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.pricing = Pricing(self.rules)

    def take_seconds(self) -> float | None:
        """How long the last answer took (the broker reads it once per decision)."""
        seconds, self._seconds = self._seconds, None
        return seconds

    # --- plumbing --------------------------------------------------------------------

    def _news(self) -> None:
        if self.events is None:
            return
        from stamina_engine.experiments.trace import event_line

        for e in self.events[self._seen :]:
            self.io.show("  " + event_line(e))
        self._seen = len(self.events)

    def _read(self, text: str, prompt: str, parse: Callable[[str], T]) -> T:
        self._news()
        self.io.show(text)
        start = self.clock()
        while True:
            line = self.io.ask(prompt).strip()
            if line in ("?", "help"):
                self.io.show(HELP)
                continue
            try:
                value = parse(line)
            except (_Invalid, ValueError, IndexError, KeyError, RulesError, Unaffordable):
                self.io.show("  That isn't one of the options (? for help).")
                continue
            self._seconds = self.clock() - start
            return value

    def _status(self, obs: Observation) -> str:
        me = obs.me
        strain = me.trackers.strain if me.trackers is not None else 0
        where = f" at {me.pos}" if me.pos is not None else ""
        lines = [
            f"Round {obs.round}. You are {me.id} ({me.team}){where}: HP {me.hp}/"
            f"{me.profile.hp_max}, stamina {me.stamina}/{me.max_stamina}, strain {strain}/"
            f"{me.profile.strain_max}."
        ]
        letters = {}
        for i, v in enumerate(obs.others):
            letters[v.id] = ascii_uppercase[i % 26]
            est = "" if v.stamina_exact else "~"
            at = f" at {v.pos}" if v.pos is not None else ""
            lines.append(
                f"  {letters[v.id]} {v.id} ({v.team}, {v.status}){at}: HP {v.hp}, stamina "
                f"{est}{v.stamina}/{v.max_stamina}"
            )
        for o in obs.objectives:
            lines.append(_objective_line(o))
        if obs.field is not None:
            marks = {c: "*" for o in obs.objectives for c in o.cells}  # zone squares
            marks.update({v.pos: letters[v.id] for v in obs.others if v.pos is not None})
            if me.pos is not None:
                marks[me.pos] = "@"
            lines.append(obs.field.render(marks, spawns=False))
        return "\n".join(lines)

    def _context(self, context: tuple[str, ...]) -> str:
        return "[" + " > ".join(context) + "]"

    def _route(self, obs: Observation, moves: MoveOptions, words: list[str]) -> Move:
        from stamina_engine.agents.broker import Broker

        cells = tuple(_cell(w) for w in words)
        if not cells:
            raise _Invalid
        if len(cells) == 1:
            from stamina_engine.agents.grid_view import Board

            if cells[0] not in moves.destinations:
                raise _Invalid
            route = Board(obs, self.rules).route(moves, [cells[0]], moves.max_squares)
            if route is None:
                raise _Invalid
            cells = route.path
        Broker({}, self.pricing).check_path(obs.me.id, obs.field, moves, cells)
        return Move(cells)

    @staticmethod
    def _moves_line(moves: MoveOptions | None) -> list[str]:
        if moves is None:
            return []
        prices = ", ".join(f"{n}: {p}" for n, p in enumerate(moves.price_by_length) if n)
        return [
            f"  m X,Y      move (up to {moves.max_squares} squares; stamina by squares: "
            f"{prices or 'free'})"
        ]

    @staticmethod
    def _draws_lines(draws: tuple[DrawOption, ...]) -> list[str]:
        return [f"  d {d.loadout:<9} draw ({d.quote.total} stamina)" for d in draws]

    @staticmethod
    def _ability_lines(options: tuple[AbilityOption, ...]) -> list[str]:
        return [
            f"  u {o.name:<9} use ({o.quote.total} stamina, +{o.strain} strain)" for o in options
        ]

    def _ability(self, words: list[str], options: tuple[AbilityOption, ...]) -> UseAbility:
        return UseAbility(_pick(words[1] if len(words) > 1 else None, [o.name for o in options]))

    # --- requests --------------------------------------------------------------------

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        obs = request.observation
        lines = [self._status(obs), f"Your turn {self._context(request.context)}. Options:"]
        lines += [f"  a {t:<9} attack" for t in request.targets]
        lines += [f"  s {t:<9} shoot" for t in request.shots]
        lines += self._moves_line(request.moves)
        lines += self._draws_lines(request.draws) + self._ability_lines(request.abilities)
        if request.can_flee:
            lines.append("  f          flee the fight")
        if request.can_surrender:
            lines.append("  surrender")
        lines.append("  e          end your turn")

        def parse(line: str) -> TurnAnswer:
            words = line.split()
            if not words:
                raise _Invalid
            cmd, arg = words[0], (words[1] if len(words) > 1 else None)
            if cmd == "a":
                return Attack(_pick(arg, request.targets))
            if cmd == "s":
                return Shoot(_pick(arg, request.shots))
            if cmd == "m" and request.moves is not None:
                return self._route(obs, request.moves, words[1:])
            if cmd == "d":
                return Draw(_pick(arg, [d.loadout for d in request.draws]))
            if cmd == "u":
                return self._ability(words, request.abilities)
            if cmd == "f" and request.can_flee:
                return Flee()
            if cmd == "surrender" and request.can_surrender:
                return Surrender()
            if cmd in ("e", "end"):
                return EndTurn()
            raise _Invalid

        return self._read("\n".join(lines), "turn> ", parse)

    def commitment(self, request: Commitment) -> int:
        prices = ", ".join(f"{k}: {q.total}" for k, q in enumerate(request.quotes, 1))
        text = (
            f"Attack on {request.target} {self._context(request.context)}: how many steps? "
            f"Stamina by steps: {prices}. 0 withdraws."
        )

        def parse(line: str) -> int:
            k = int(line)
            if not 0 <= k <= request.max_steps:
                raise _Invalid
            return k

        return self._read(text, "steps> ", parse)

    def _block_frontier(self, r: BlocksRequest) -> list[tuple[Blocks, int, int]]:
        """Every affordable (perfect, grazing) pair no other beats on cost and injury."""
        points: list[tuple[Blocks, int, int]] = []
        p = 0
        while True:
            try:
                self.pricing.blocks(p, 0, r.stamina, r.prior_perfect, r.ranged, r.flat_perfect)
            except Unaffordable:
                break
            g = 0
            while True:
                try:
                    cost = self.pricing.blocks(
                        p, g, r.stamina, r.prior_perfect, r.ranged, r.flat_perfect
                    ).total
                except Unaffordable:
                    break
                out = resolve(r.damage, r.crit_dice, r.defense, r.armor, Blocks(p, g), self.rules)
                points.append((Blocks(p, g), cost, out.injury))
                if out.injury == 0:
                    break
                g += 1
            p += 1
        return [
            (b, c, i)
            for b, c, i in points
            if not any(c2 <= c and i2 <= i and (c2, i2) != (c, i) for _, c2, i2 in points)
        ]

    def blocks(self, request: BlocksRequest) -> Blocks:
        frontier = self._block_frontier(request)
        hp = request.observation.me.hp
        kind = "shot" if request.ranged else "attack"
        lines = [
            self._status(request.observation),
            f"{request.attacker}'s {kind} {self._context(request.context)}: {request.damage} "
            f"damage, {request.crit_dice} critical dice; your defense {request.defense}, armor "
            f"{request.armor}, stamina {request.stamina}"
            + (" (perfect blocks don't escalate)" if request.flat_perfect else "")
            + ". Blocks worth considering:",
        ]
        for n, (b, cost, injury) in enumerate(frontier, 1):
            down = " (down)" if injury >= hp else ""
            lines.append(
                f"  {n}) {b.perfect} perfect, {b.grazing} grazing: {cost} stamina, "
                f"{injury} injury{down}"
            )

        def parse(line: str) -> Blocks:
            words = line.split()
            if len(words) == 1:
                return frontier[int(words[0]) - 1][0]
            if len(words) == 2:
                p, g = int(words[0]), int(words[1])
                if p < 0 or g < 0:
                    raise _Invalid
                r = request
                self.pricing.blocks(p, g, r.stamina, r.prior_perfect, r.ranged, r.flat_perfect)
                return Blocks(p, g)
            raise _Invalid

        return self._read("\n".join(lines), "blocks> ", parse)

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer:
        obs = request.observation
        lines = [self._status(obs), f"Off-turn window {self._context(request.context)}:"]
        lines += self._moves_line(request.moves)
        lines += self._draws_lines(request.draws) + self._ability_lines(request.abilities)
        lines.append("  p          pass")

        def parse(line: str) -> MoveAnswer:
            words = line.split() or ["p"]
            cmd = words[0]
            if cmd == "m" and request.moves is not None:
                return self._route(obs, request.moves, words[1:])
            if cmd == "d":
                return Draw(
                    _pick(words[1] if len(words) > 1 else None, [d.loadout for d in request.draws])
                )
            if cmd == "u":
                return self._ability(words, request.abilities)
            if cmd in ("p", "pass"):
                return Pass()
            raise _Invalid

        return self._read("\n".join(lines), "off-turn> ", parse)

    def avoid(self, request: AvoidOA) -> Avoid:
        one = self.pricing.avoid_opportunity(
            1, caps=request.caps[:1], trackers=request.trackers, on_turn=request.on_turn
        )
        text = (
            f"Leaving {request.leaving} {self._context(request.context)}: "
            f"{', '.join(request.enemies)} threaten it (OA caps {list(request.caps)}). Pay any "
            f"off? (the first costs {one.total}; you have {request.stamina})"
        )

        def parse(line: str) -> Avoid:
            words = line.replace(",", " ").split()
            if not words or words == ["none"]:
                return Avoid()
            chosen = set(request.enemies) if words == ["all"] else set(words)
            if not chosen <= set(request.enemies):
                raise _Invalid
            ordered = tuple(e for e in request.enemies if e in chosen)
            caps = [request.caps[request.enemies.index(e)] for e in ordered]
            quote = self.pricing.avoid_opportunity(
                len(caps), caps=caps, trackers=request.trackers, on_turn=request.on_turn
            )
            if quote.total > request.stamina and not self.rules.opportunity.allows_debt():
                raise _Invalid
            return Avoid(ordered)

        return self._read(text, "avoid> ", parse)

    def take_oa(self, request: TakeOA) -> OATake:
        lines = [
            f"{request.target} leaves {request.leaving} {self._context(request.context)}: "
            f"opportunity attack? ({'no cap' if request.cap is None else f'cap {request.cap}'})"
        ]
        for o in request.options:
            prices = ", ".join(f"{k}: {q.total}" for k, q in enumerate(o.quotes, 1))
            lines.append(f"  {o.weapon} ({o.name}): stamina by steps {prices}")
        lines.append("  0          decline")

        def parse(line: str) -> OATake:
            words = line.split() or ["0"]
            weapon = words[0] if len(words) == 2 else request.options[0].weapon
            k = int(words[-1])
            if k == 0:
                return OATake()
            (option,) = [o for o in request.options if o.weapon == weapon]
            if not 0 < k <= len(option.quotes):
                raise _Invalid
            return OATake(weapon, k)

        return self._read("\n".join(lines), "oa> ", parse)

    def aim(self, request: AimRequest) -> int:
        prices = ", ".join(f"{k}: {q.total}" for k, q in enumerate(request.quotes))
        text = (
            f"Shot at {request.target} ({request.band}, cover {request.cover}) "
            f"{self._context(request.context)}: how many aims? At least {request.required} "
            f"to hit. Stamina by aims: {prices}."
        )

        def parse(line: str) -> int:
            k = int(line)
            if not 0 <= k <= request.max_aims:
                raise _Invalid
            return k

        return self._read(text, "aims> ", parse)

    def dive(self, request: DiveRequest) -> MoveAnswer:
        obs = request.observation
        better = sorted(c for c, level in request.cover_after.items() if level > request.cover)
        lines = [
            self._status(obs),
            f"{request.shooter}'s roll {self._context(request.context)}: {request.damage} "
            f"damage, {request.crit_dice} critical dice. Move (dive for cover, or Tactical "
            "Withdrawal's step), or p to stay.",
        ]
        lines += self._moves_line(request.moves)
        if better:
            lines.append("  better cover at: " + " ".join(f"{x},{y}" for x, y in better[:12]))

        def parse(line: str) -> MoveAnswer:
            words = line.split() or ["p"]
            if words[0] == "m":
                return self._route(obs, request.moves, words[1:])
            if words[0] in ("p", "pass"):
                return Pass()
            raise _Invalid

        return self._read("\n".join(lines), "move> ", parse)

    def ability(self, request: AbilityRequest) -> UseAbility | Pass:
        facts = ", ".join(f"{k} {v}" for k, v in request.facts.items())
        lines = [
            f"Ability window: {request.window} {self._context(request.context)}"
            + (f" ({facts})" if facts else "")
        ]
        lines += self._ability_lines(request.options) + ["  p          pass"]

        def parse(line: str) -> UseAbility | Pass:
            words = line.split() or ["p"]
            if words[0] == "u":
                return self._ability(words, request.options)
            if words[0] in ("p", "pass"):
                return Pass()
            raise _Invalid

        return self._read("\n".join(lines), "ability> ", parse)


def _objective_line(o: ObjectiveView) -> str:
    """One line on the scenario objective; its zone is drawn as * on the board."""
    if o.kind == "hold":
        need = "control at the deadline" if o.score == "final" else f"{o.rounds} rounds"
        how = f"{o.control} control, {o.score}: {need}; scored {o.progress}, streak {o.streak}"
    else:
        where = "zone *" if o.kind == "reach" else "an exit"
        how = f"{o.count} of {', '.join(o.who)} to {where}; {o.progress} so far"
    return f"  Objective {o.id} ({o.kind}, team {o.team}, by round {o.deadline}, {o.status}): {how}"
