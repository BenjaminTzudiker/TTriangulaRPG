#!/usr/bin/env python3
"""Hand-played fights on the engine (branch exp/holds).

A fight is a scenario (a Python dict in FIGHT.py) plus an orders file (FIGHT.orders, one order
per line). Each run replays the fight from the start with the orders so far and stops at the
first decision that has no order, printing what happened since the last run and the decision.

Routine decisions are automatic: blocks use the engine's exact block solver (w = 3 stamina
per HP unless a creature is listed under manual_blocks), ability windows pass. Everything
else needs an order.

Orders (one line each; "|" separates the parts of one creature's orders):
  X| m 5,4            move to a square by the route with the fewest threatened squares left,
                      or m 5,4 6,4 7,5 for an exact path. Add pay=all, pay=none or pay=A,B to
                      settle every opportunity-attack payment during that move.
  X| a Y 2            attack Y with 2 steps (a Y, then the steps as the next part, also works).
                      blk=1,0 forces Y's blocks for that attack (perfect, grazing).
  X| s Y 1            shoot Y with 1 aim step.
  X| d blade          draw a loadout.
  X| e                end the turn with no holds;  X| e Y:4 Z:2  ends it and sets holds.
  X| pay A B / pay all / pay none     answer a payment decision.
  X| oa 2             make an opportunity attack of 2 steps (0 declines).
  X| b 1 0            blocks, for a creature under manual_blocks.
  X| stay             don't react to a shot;  X| m 3,3  dives there.
  W|                  the dash phase: nobody dashes. (If the next order is a creature's turn
                      order, the dash phase before it is skipped the same way.)
  W| Y m 12,4 pay=all | X m 9,4      dashes, in this order. Reactions inside a dash phase can
                      be written in the line (W| Y m 12,4 | Y pay none | X oa 1) or as
                      ordinary orders after it (Y| pay none, then X| oa 1).
  cfg| oa X=max Y=0   standing opportunity-attack choices (max, or a number of steps)
  cfg| dive X=stay    X never reacts to shots
"""

import dataclasses
import importlib.util
import json
import pathlib
import sys
from collections import defaultdict
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))  # sim/src

from stamina_engine.agents.blocking import solver_blocks  # noqa: E402
from stamina_engine.agents.decisions import (  # noqa: E402
    Attack,
    Avoid,
    Draw,
    EndTurn,
    Flee,
    Holds,
    Move,
    OATake,
    Pass,
    Shoot,
    Surrender,
)
from stamina_engine.core.dice import ScriptedDice  # noqa: E402
from stamina_engine.core.errors import ConfigError, RulesError, Unaffordable  # noqa: E402
from stamina_engine.core.rng import Streams  # noqa: E402
from stamina_engine.engine.arena import bodies  # noqa: E402
from stamina_engine.engine.battle import Battle, Entrant  # noqa: E402
from stamina_engine.grid.battlefield import parse_map  # noqa: E402
from stamina_engine.grid.pathing import Passage, cheapest_routes  # noqa: E402
from stamina_engine.grid.threat import threatening  # noqa: E402
from stamina_engine.model.build import load_build  # noqa: E402
from stamina_engine.model.derive import derive, equipment_for  # noqa: E402
from stamina_engine.model.equipment import load_table  # noqa: E402
from stamina_engine.rules.block_solver import best_block  # noqa: E402
from stamina_engine.rules.exchange import Blocks  # noqa: E402
from stamina_engine.rules.ruleset import preset  # noqa: E402


class Need(Exception):
    """A decision with no order."""

    def __init__(self, who, kind, text):
        super().__init__(text)
        self.who, self.kind, self.text = who, kind, text


class Bad(Exception):
    """An order that doesn't fit the decision in front of it."""


def cell(text):
    x, y = text.split(",")
    return (int(x), int(y))


class Dice:
    """Named streams from a seed, with the initiative faces scripted if given."""

    def __init__(self, seed, initiative=None):
        self.streams = Streams(seed)
        self.init = ScriptedDice(initiative) if initiative else None

    def dice(self, name):
        if name == "initiative" and self.init is not None:
            return self.init
        return self.streams.dice(name)


ORDER_FACES = [(12, 12), (12, 8), (12, 4), (8, 4), (4, 4), (2, 2), (1, 1)]


class Director:
    def __init__(self, orders, cfg):
        self.items = []  # (scope, who, text, order index)
        for i, line in enumerate(orders):
            owner, _, rest = line.partition("|")
            owner = owner.strip()
            subs = [s.strip() for s in rest.split("|") if s.strip()]
            if owner == "W":
                for s in subs:
                    who, _, text = s.partition(" ")
                    self.items.append(("W", who, text.strip(), i))
                self.items.append(("W", None, "end", i))
            elif owner == "cfg":
                self.items += [("cfg", None, s, i) for s in subs]
            else:
                self.items += [("T", owner, s, i) for s in subs]
        self.pos = 0
        self.b = None
        self.avoid_rule = {}
        self.stash = {}
        self.oa_policy = dict(cfg.get("oa", {}))
        self.dive_policy = dict(cfg.get("dive", {}))
        self.w = dict(cfg.get("w", {}))
        self.manual_blocks = set(cfg.get("manual_blocks", ()))
        self.marks = {}  # order index -> log length when its first part was used
        self.pending_hold = None  # who gave hold tokens with its end-of-turn order
        self.counts = defaultdict(int)  # decisions answered by an order, by kind
        self.auto = defaultdict(int)  # decisions answered automatically, by kind

    # --- the queue -------------------------------------------------------------------

    def _cfg(self):
        while self.pos < len(self.items) and self.items[self.pos][0] == "cfg":
            _, _, text, idx = self.items[self.pos]
            self.marks.setdefault(idx, len(self.b.log))
            kind, _, rest = text.partition(" ")
            for pair in rest.split():
                who, _, val = pair.partition("=")
                {"oa": self.oa_policy, "dive": self.dive_policy, "w": self.w}[kind][who] = val
            self.pos += 1

    def _head(self, request):
        """The next order, after dropping a finished dash phase's end marker."""
        self._cfg()
        if self.pending_hold is not None:
            who, self.pending_hold = self.pending_hold, None
            self.stash.pop((who, "holds"), None)
            raise Bad(
                f"{who}'s hold wasn't set: no enemy was within its reach when its turn "
                f"ended, or this rule set has no holds. End the turn with plain 'e'."
            )
        if not self.in_window(request):
            while self.pos < len(self.items) and self.items[self.pos][0] == "W":
                _, who, text, idx = self.items[self.pos]
                if who is not None:
                    raise Bad(
                        f"order {idx + 1}: the dash-phase order '{who} {text}' was never used "
                        f"({who} wasn't asked: it couldn't do that, or the phase had ended)"
                    )
                self.marks.setdefault(idx, len(self.b.log))
                self.pos += 1
                self._cfg()
        return self.items[self.pos] if self.pos < len(self.items) else None

    def _use(self):
        item = self.items[self.pos]
        self.marks.setdefault(item[3], len(self.b.log))
        self.pos += 1
        return item

    @staticmethod
    def in_window(request):
        return any(f.startswith("off-turn") for f in request.context)

    def _mine(self, request, kind, starts=None):
        """The head order's text if it is for request.who (and starts as given), else None."""
        head = self._head(request)
        if head is None:
            return None
        scope, who, text, idx = head
        if scope == "W" and not self.in_window(request):
            return None
        if scope == "W" and who is None and self.pos + 1 < len(self.items):
            # A reaction inside a dash phase, written after the W| line.
            s2, w2, t2, i2 = self.items[self.pos + 1]
            if s2 == "T" and w2 == request.who and (starts is None or t2.split()[0] in starts):
                del self.items[self.pos + 1]
                self.marks.setdefault(i2, len(self.b.log))
                self.counts[kind] += 1
                return t2
            return None
        if scope == "T" and self.in_window(request):
            return None
        if who != request.who:
            return None
        if starts is not None and text.split()[0] not in starts:
            return None
        self._use()
        self.counts[kind] += 1
        return text

    def _need(self, request, kind, text):
        head = self._head(request)
        if head is not None:
            scope, who, t, idx = head
            if not (scope == "W" and who is None):
                raise Bad(
                    f"order {idx + 1} ('{who}| {t}') doesn't fit: the decision now is "
                    f"{request.who}'s {kind}.\n{text}"
                )
        raise Need(request.who, kind, text)

    # --- helpers ---------------------------------------------------------------------

    def _path(self, who, moves, words):
        """A Move from the words after m: one square (a route is chosen) or an exact path."""
        cells, pay = [], None
        for wd in words:
            if wd.startswith("pay="):
                pay = wd[4:]
            else:
                cells.append(cell(wd))
        self.avoid_rule[who] = pay
        if moves is None:
            raise Bad(f"{who} can't move now")
        if len(cells) > 1:
            return Move(tuple(cells))
        goal = cells[0]
        if goal not in moves.destinations:
            raise Bad(f"{who} can't reach {goal} now (most squares: {moves.max_squares})")
        b = self.b
        c = b.state.get(who)
        passage = Passage(moves.no_entry, moves.no_stop)
        bods = bodies(b.state)

        def leave_cost(sq):
            n = Fraction(0)
            for e in threatening(b.field, b.rules.grid, bods, c.team, sq):
                n += 1 + Fraction(b.state.get(e).holds.get(who, 0), 100)
            return n

        def length_cost(n):
            if n > moves.max_squares:
                return None
            return Fraction(moves.price_by_length[n]) + Fraction(n, 1000)

        routes = cheapest_routes(
            b.field, b.rules.grid, moves.start, passage, leave_cost, length_cost, moves.max_squares
        )
        return Move(routes[goal].path)

    # --- the Agent protocol ----------------------------------------------------------

    def turn_command(self, request):
        text = self._mine(request, "turn")
        if text is None:
            self._need(request, "turn", describe_turn(self.b, request))
        words = text.split()
        op, args = words[0], words[1:]
        who = request.who
        if op == "m":
            return self._path(who, request.moves, args)
        if op == "a":
            for a in args[1:]:
                if a.startswith("blk="):
                    p, g = a[4:].split(",")
                    self.stash[(args[0], "blocks")] = Blocks(int(p), int(g))
                else:
                    self.stash[(who, "steps")] = int(a)
            return Attack(args[0])
        if op == "s":
            if len(args) > 1:
                self.stash[(who, "aims")] = int(args[1])
            return Shoot(args[0])
        if op == "d":
            return Draw(args[0])
        if op == "e":
            tokens = {a.split(":")[0]: int(a.split(":")[1]) for a in args}
            self.stash[(who, "holds")] = tokens
            self.pending_hold = who if tokens else None
            self.avoid_rule[who] = None
            return EndTurn()
        if op == "flee":
            return Flee()
        if op == "surrender":
            return Surrender()
        raise Bad(f"{who}: '{text}' isn't a turn order")

    def commitment(self, request):
        if (request.who, "steps") in self.stash:
            return self.stash.pop((request.who, "steps"))
        text = self._mine(request, "steps")
        if text is None:
            self._need(request, "steps", describe_commit(self.b, request))
        return int(text)

    def aim(self, request):
        if (request.who, "aims") in self.stash:
            return self.stash.pop((request.who, "aims"))
        text = self._mine(request, "aims")
        if text is None:
            self._need(
                request,
                "aims",
                f"{request.who} shoots {request.target}: band {request.band}, cover "
                f"{request.cover}, needs {request.required} aims, penalty {request.penalty}; "
                f"prices by aims {[q.total for q in request.quotes]}",
            )
        return int(text)

    def holds(self, request):
        self.pending_hold = None
        self.counts["hold_asked"] += 1
        tokens = self.stash.pop((request.who, "holds"), {})
        if tokens:
            self.counts["hold_set"] += 1
        return Holds(tokens)

    def blocks(self, request):
        key = (request.who, "blocks")
        if key in self.stash:
            return self.stash.pop(key)
        if request.who in self.manual_blocks:
            text = self._mine(request, "blocks", ("b",))
            if text is None:
                self._need(
                    request,
                    "blocks",
                    f"{request.who} blocks {request.attacker}'s attack: damage "
                    f"{request.damage}, crit dice {request.crit_dice}, defense "
                    f"{request.defense}, armor {request.armor}, stamina {request.stamina}",
                )
            _, p, g = text.split()
            return Blocks(int(p), int(g))
        self.auto["blocks"] += 1
        w = Fraction(self.w.get(request.who, 3))
        return solver_blocks(request, self.b.rules, w)

    def off_turn_move(self, request):
        head = self._head(request)
        if head is None:
            raise Need(request.who, "dash phase", describe_window(self.b, request))
        scope, who, text, idx = head
        if scope != "W":
            return Pass()  # the next order is a turn's: the player skipped this dash phase
        if who != request.who:
            return Pass()
        words = text.split()
        if words[0] == "m":
            self._use()
            self.counts["dash"] += 1
            return self._path(request.who, request.moves, words[1:])
        if words[0] == "d":
            self._use()
            return Draw(words[1])
        return Pass()

    def avoid(self, request):
        who = request.who
        rule = self.avoid_rule.get(who)
        if rule is None:
            text = self._mine(request, "pay", ("pay",))
            if text is None:
                self._need(request, "pay", describe_avoid(self.b, request))
            rule = ",".join(text.split()[1:])
        else:
            self.auto["pay"] += 1
        if rule == "none":
            return Avoid(())
        if rule == "all":
            return Avoid(tuple(request.enemies))
        chosen = set(rule.split(","))
        return Avoid(tuple(e for e in request.enemies if e in chosen))

    def take_oa(self, request):
        text = self._mine(request, "oa", ("oa",))
        most = max(len(o.quotes) for o in request.options)
        if text is None:
            rule = self.oa_policy.get(request.who)
            if rule is None:
                self._need(request, "oa", describe_oa(self.b, request))
            self.auto["oa"] += 1
            steps = most if rule == "max" else min(int(rule), most)
        else:
            steps = int(text.split()[1])
        return OATake("main", steps)

    def dive(self, request):
        text = self._mine(request, "react", ("stay", "m"))
        if text is None:
            if self.dive_policy.get(request.who) == "stay":
                self.auto["react"] += 1
                return Pass()
            self._need(request, "react", describe_dive(self.b, request))
        words = text.split()
        if words[0] == "stay":
            return Pass()
        return self._path(request.who, request.moves, words[1:])

    def ability(self, request):
        return Pass()


# --- what a decision looks like ------------------------------------------------------


def step_table(b, attacker, target, weapon, quotes, stamina=None):
    """For each number of steps: cost, chance the target goes down, mean injury, mean stamina
    the target spends blocking (the target blocks as the solver would, w = 3)."""
    rules = b.rules
    per = defaultdict(Fraction)
    sizes = [d.size for d in weapon.damage.dice for _ in range(d.count)]

    def faces(i, tot, crits, p):
        if i == len(sizes):
            total = max(weapon.damage.step_floor, tot + weapon.damage.flat)
            per[(total, crits)] += p
            return
        for f in range(1, sizes[i] + 1):
            crit = int(rules.crit.is_crit(f, sizes[i], weapon.crit_widen))
            faces(i + 1, tot + f, crits + crit, p / sizes[i])

    faces(0, 0, 0, Fraction(1))
    st = target.stamina if stamina is None else stamina
    armor = max(0, target.gear.armor - weapon.piercing)
    dist = {(0, 0): Fraction(1)}
    lines = []
    for k, q in enumerate(quotes, 1):
        nxt = defaultdict(Fraction)
        for (t, c), p in dist.items():
            for (t2, c2), p2 in per.items():
                nxt[(t + t2, c + c2)] += p * p2
        dist = nxt
        down = inj = cost = Fraction(0)
        for (t, c), p in dist.items():
            ch = best_block(t, c, target.gear.melee_defense, armor, st, target.hp, rules)
            down += p * (ch.injury >= target.hp)
            inj += p * ch.injury
            cost += p * ch.cost
        lines.append(
            f"    {k} step(s): costs {q.total:>2} {list(q.parts)}  down {float(down):5.1%}  "
            f"injury {float(inj):4.2f}  target spends {float(cost):4.2f}"
        )
    return "\n".join(lines)


def describe_turn(b, r):
    c = b.state.get(r.who)
    lines = [f"{r.who}'s turn: free movement left {c.free_move_left}; stamina {c.stamina}; "
             f"escalation {c.trackers.actions_this_turn}."]
    if r.moves is not None:
        prices = r.moves.price_by_length
        lines.append(f"  can move up to {r.moves.max_squares} squares; price by squares "
                     f"{list(prices)}")
    if r.targets:
        lines.append(f"  can attack: {', '.join(r.targets)}")
        w = c.gear.weapon
        for t in r.targets:
            quotes = []
            while True:
                q = b.pricing.melee_attack(w.base, len(quotes) + 1, c.trackers, light=w.light)
                if q.total > c.stamina or len(quotes) >= 5:
                    break
                quotes.append(q)
            lines.append(f"   vs {t}:")
            lines.append(step_table(b, c, b.state.get(t), w, quotes))
    if r.shots:
        lines.append(f"  can shoot: {', '.join(r.shots)}")
    if r.can_flee:
        lines.append("  is on an exit square: 'flee' leaves the fight")
    if b.rules.opportunity.holds_on() and b.field is not None and c.pos is not None:
        opp = b.rules.opportunity
        near = [o.id for o in b.state.enemies_of(c) if o.active and o.pos is not None
                and (opp.holds_any_enemy() or c.id in b.arena.threatening(b.state, o, o.pos))]
        if near:
            if opp.holds_set_before_recovery():
                when = "set before you recover; tokens you have out come back first"
            else:
                when = f"after recovering {c.profile.recovery}"
            if opp.hold_limit(100) < 100:
                when += f"; at most {opp.hold_limit(100)}% of your ready stamina"
            where = "any enemy" if opp.holds_any_enemy() else "in reach"
            lines.append(f"  can hold at end of turn ({where}; {when}): "
                         + ", ".join(f"{o} (ready {b.state.get(o).stamina})" for o in near))
    if r.draws:
        draws = ", ".join(f"{d.loadout} ({d.quote.total})" for d in r.draws)
        lines.append(f"  can draw: {draws}")
    return "\n".join(lines)


def describe_commit(b, r):
    c = b.state.get(r.who)
    return (f"{r.who} attacks {r.target}: how many steps?\n"
            + step_table(b, c, b.state.get(r.target), c.gear.weapon, r.quotes))


def describe_window(b, r):
    order = list(b.state.order)
    done = b.state.acted
    left = [c for c in order if c not in done and b.state.get(c).active]
    nxt = left[0] if left else next((c for c in order if b.state.get(c).active), "?")
    return (f"Dash phase ({r.context[-1]}); next to act: {nxt}. Anyone may dash now (1 + its "
            f"escalation each, 2 squares). Write W| if nobody does, or W| X m x,y | Y m x,y ...")


def describe_avoid(b, r):
    parts = []
    for i, e in enumerate(r.enemies):
        extra = r.extras[i] if r.extras else 0
        cap = r.caps[i]
        en = b.state.get(e)
        budget = "no cap" if cap is None else f"budget {cap + extra}"
        parts.append(f"{e}: pay {1 + extra} (its attack: {budget}, ready {en.stamina})")
    return (f"{r.who} leaves {r.leaving} (stamina {r.stamina}). " + "; ".join(parts)
            + f".  Answer: {r.who}| pay ... (ids, all or none)")


def describe_oa(b, r):
    a = b.state.get(r.who)
    t = b.state.get(r.target)
    out = [f"{r.who} may make an opportunity attack on {r.target} (cap {r.cap}, tokens "
           f"{r.tokens}, ready {a.stamina}):"]
    for o in r.options:
        w = a.gear.weapon if o.weapon == "main" else a.gear.off_hand_weapon
        out.append(step_table(b, a, t, w, o.quotes))
    out.append(f"  Answer: {r.who}| oa N")
    return "\n".join(out)


def describe_dive(b, r):
    per = max(1, b.state.get(r.who).gear.squares_per_purchase)

    def rank(d):
        after = r.damage_after.get(d, r.damage)
        return (-r.defense_after.get(d, 0), after, r.moves.destinations[d])

    lines = [f"{r.who} is shot by {r.shooter}: total {r.damage} to block, crit dice {r.crit_dice}, "
             f"its defense if it stays {r.defense} (cover {r.cover}), the wound is capped at "
             f"{r.limit}. It may dash first (prices by squares {list(r.moves.price_by_length)}); "
             f"moving at all gives +1 defense, and distance and cover are judged where it ends."]
    for n in (1, 2):
        dests = [d for d, k in r.moves.destinations.items() if (n - 1) * per < k <= n * per]
        for d in sorted(dests, key=rank)[: 4 if n == 1 else 2]:
            lines.append(f"    {n} dash(es) to {d}: total {r.damage_after.get(d)}, defense "
                         f"{r.defense_after.get(d)}, cover {r.cover_after.get(d)}")
    lines.append(f"  Answer: {r.who}| stay   or   {r.who}| m x,y")
    return "\n".join(lines)


# --- reporting -----------------------------------------------------------------------


def board(b):
    f = b.field
    marks = {}
    for c in b.state.combatants:
        if c.pos is None:
            continue
        ch = c.id[0] if c.active else c.id[0].lower()
        if c.pos not in marks or c.active:
            marks[c.pos] = ch
    out = ["    " + "".join(str(x % 10) for x in range(f.width))]
    for y, row in enumerate(f.rows):
        line = "".join(marks.get((x, y), ch if ch in "#o=~>" else ".") for x, ch in enumerate(row))
        out.append(f"{y:>3} {line}")
    return "\n".join(out)


def status(b):
    out = [f"Round {b.state.round}. Order: {' '.join(b.state.order)}. "
           f"Turn of: {b.state.turn_of or '-'}"]
    out.append("  id team  hp  ready/max  esc  tokens out             pos     weapon")
    for c in b.state.combatants:
        held = " ".join(f"{t}:{n}" for t, n in c.holds.items())
        if c.parked:
            held += f" (+{c.parked} idle)"
        w = c.gear.weapon.name if c.gear.weapon else "-"
        state = "" if c.active else f" [{c.status.value}]"
        out.append(
            f"  {c.id:<2} {c.team:<5} {c.hp:>2}  {c.stamina:>2}/{b.ops.max_stamina(c):<2}     "
            f"{c.trackers.actions_this_turn:>2}   {held:<22} {str(c.pos):<8}{w}{state}"
        )
    return "\n".join(out)


def fmt_events(log):
    out = []
    run = None  # a run of Moved events: [who, how-counts, from, to]

    def flush():
        nonlocal run
        if run:
            who, hows, frm, to = run
            how = ", ".join(f"{n} {h}" for h, n in hows.items())
            out.append(f"  {who} moves {tuple(frm)} -> {tuple(to)} ({how})")
            run = None

    for e in log:
        d = json.loads(e.to_json())
        k = d.pop("event")
        if k == "Moved":
            if run and run[0] == d["who"]:
                run[1][d["how"]] = run[1].get(d["how"], 0) + 1
                run[3] = d["to"]
            else:
                flush()
                run = [d["who"], {d["how"]: 1}, d["frm"], d["to"]]
            continue
        flush()
        if k in ("Placed", "MapLoaded", "BattleStarted", "TurnEnded", "OpportunityProvoked"):
            continue
        if k == "TurnStarted":
            out.append(f"--- round {d['round']}: {d['who']}'s turn ---")
        elif k == "RoundStarted":
            out.append(f"=== round {d['round']} ===")
        elif k == "InitiativeRolled":
            out.append(f"Initiative: {' '.join(d['order'])}")
        elif k == "Spent":
            out.append(f"  {d['who']} pays {d['amount']} {d['parts']} for {d['category']} "
                       f"-> ready {d['stamina_after']}")
        elif k == "Recovered":
            out.append(f"  {d['who']} recovers {d['amount']} -> ready {d['stamina_after']}"
                       + (f" ({d['wasted']} wasted)" if d["wasted"] else ""))
        elif k == "AttackDeclared":
            out.append(f"  {d['attacker']} attacks {d['target']}, {d['steps']} step(s)")
        elif k == "OpportunityDeclared":
            out.append(f"  {d['attacker']} makes an opportunity attack on {d['target']}, "
                       f"{d['steps']} step(s)")
        elif k == "OpportunityAvoided":
            out.append(f"  {d['mover']} pays off {d['enemies']} leaving {tuple(d['square'])}")
        elif k == "AttackRolled":
            out.append(f"    rolled {d['faces']} = {d['total']}, crit dice {d['crit_dice']}")
        elif k == "BlocksDeclared":
            out.append(
                f"    {d['defender']} blocks: {d['perfect']} perfect, {d['grazing']} grazing")
        elif k == "AttackResolved":
            out.append(f"    injury {d['injury']} (through blocks {d['through_blocks']}, leaked "
                       f"{d['leaked']}, armor {d['armor_applied']})")
        elif k == "Injured":
            out.append(f"    {d['who']}: hp {d['hp_after']}, ready {d['stamina_after']}, "
                       f"{d['status_after']}")
        elif k == "HoldSet":
            out.append(f"  {d['who']} sets a hold on {d['target']}: {d['tokens']} tokens "
                       f"-> ready {d['stamina_after']}")
        elif k == "HoldEnded":
            out.append(f"  {d['who']}'s hold on {d['target']} ends ({d['reason']}), "
                       f"{d['tokens_left']} tokens idle")
        elif k == "HoldSpent":
            out.append(f"    {d['who']} spends {d['tokens']} tokens of its hold on {d['target']}")
        elif k == "HoldsReturned":
            out.append(f"  {d['who']} gets {d['tokens']} tokens back -> ready {d['stamina_after']}")
        elif k == "ShotDeclared":
            out.append(f"  {d['shooter']} shoots {d['target']}: {d['aims']} aim(s), band "
                       f"{d['band']}, cover {d['cover']}")
        else:
            out.append(f"  {k}: " + " ".join(f"{a}={v}" for a, v in d.items()))
    flush()
    return "\n".join(out)


def hold_stats(log):
    """Counts for judging the hold rule's weight in a fight, from the event log."""
    st = defaultdict(int)
    live = {}  # (holder, target) -> tokens set
    for e in log:
        d = json.loads(e.to_json())
        k = d["event"]
        if k == "TurnStarted":
            st["turns"] += 1
        elif k == "HoldSet":
            st["holds set"] += 1
            st["tokens set"] += d["tokens"]
            live[(d["who"], d["target"])] = d["tokens"]
        elif k == "HoldEnded":
            live.pop((d["who"], d["target"]), None)
            if d["reason"] == "paid":
                st["holds paid off"] += 1
                st["stamina paid for holds"] += 1 + d["tokens_left"]
            elif d["reason"] == "triggered":
                st["holds triggered"] += 1
            else:
                st["holds dropped (holder down)"] += 1
        elif k == "HoldSpent":
            st["tokens spent on attacks"] += d["tokens"]
            key = (d["who"], d["target"])
            if key in live:
                live[key] -= d["tokens"]
                if live[key] <= 0:
                    live.pop(key)
                    st["holds triggered"] += 1
        elif k == "HoldsReturned":
            unused = [key for key in live if key[0] == d["who"]]
            st["holds that ran out unused"] += len(unused)
            for key in unused:
                live.pop(key)
        elif k == "OpportunityDeclared":
            st["opportunity attacks"] += 1
            st["opportunity attack steps"] += d["steps"]
        elif k == "OpportunityAvoided":
            st["payments to leave"] += 1
        elif k == "Spent" and d["category"] == "avoid":
            st["stamina paid to leave"] += d["amount"]
        elif k == "Spent" and d["category"] in ("off_turn_move", "extra_move"):
            st["dashes"] += len(d["parts"])
    return dict(st)


def build(scen, orders):
    rules = preset(scen["rules"])
    table = load_table(scen.get("equipment") or equipment_for(rules))
    field = parse_map(scen["map"])
    director = Director(orders, scen.get("cfg", {}))
    ents = []
    for cid, team, bname, loadout, pos in scen["roster"]:
        profile = derive(load_build(bname), rules, table)
        ents.append(Entrant(cid, team, profile, director, loadout, pos))
    faces = None
    if scen.get("order"):
        rank = {cid: i for i, cid in enumerate(scen["order"])}
        faces = [f for cid, *_ in scen["roster"] for f in ORDER_FACES[rank[cid]]]
    b = Battle(rules, ents, Dice(scen.get("seed", 1), faces), seed=scen.get("seed", 1),
               round_cap=scen.get("round_cap", 12), check=True, field=field)
    director.b = b
    for cid, hp in scen.get("hp", {}).items():  # a fight that starts with wounds
        c = b.state.get(cid)
        c.dying = dataclasses.replace(c.dying, hp=hp)
        c.stamina = min(c.stamina, b.ops.max_stamina(c))
    return b, director


def play(scen, orders, start=0, quiet=False):
    b, d = build(scen, orders)
    result = stop = None
    try:
        result = b.run()
    except Need as n:
        stop = ("need", n)
    except (Bad, RulesError, Unaffordable, ConfigError, KeyError, ValueError, IndexError) as bad:
        stop = ("bad", f"{type(bad).__name__}: {bad}")
    if not quiet:
        if start > len(b.log):
            start = 0
        print(fmt_events(b.log[start:]))
        print()
        print(board(b))
        print(status(b))
        if stop:
            kind, exc = stop
            print()
            print(("DECISION: " if kind == "need" else "ORDER PROBLEM: ") + str(exc))
        else:
            print(f"\nFIGHT OVER: winner {result.winner}, {result.reason}, {result.rounds} rounds")
        print(f"[orders used: {max((i for i in d.marks), default=-1) + 1} of {len(orders)}; "
              f"decisions by order {dict(d.counts)}; automatic {dict(d.auto)}]")
        print(f"[hold counts so far: {hold_stats(b.log)}]")
    return b, d, result, stop


def load(name):
    base = pathlib.Path(name)
    spec = importlib.util.spec_from_file_location("fight", base.with_suffix(".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    path = base.with_suffix(".orders")
    orders = []
    if path.exists():
        orders = [ln.strip() for ln in path.read_text().splitlines()
                  if ln.strip() and not ln.strip().startswith("#")]
    return mod.SCEN, orders


if __name__ == "__main__":
    name = sys.argv[1]
    scen, orders = load(name)
    seen_path = pathlib.Path(name).with_suffix(".seen")
    start = 0
    if "--all" not in sys.argv and seen_path.exists():
        saved = json.loads(seen_path.read_text())
        if orders[: len(saved["orders"])] == saved["orders"]:
            start = saved["seen"]
    b, d, result, stop = play(scen, orders, start)
    used = max((i for i in d.marks), default=-1) + 1
    pathlib.Path(name).with_suffix(".log").write_text(
        fmt_events(b.log) + "\n\n" + board(b) + "\n" + status(b) + "\n"
        + (f"FIGHT OVER: winner {result.winner}, {result.reason}, {result.rounds} rounds\n"
           if result else "")
        + f"hold counts: {hold_stats(b.log)}\n"
        + f"decisions by order {dict(d.counts)}; automatic {dict(d.auto)}\n"
    )
    if "--odds" in sys.argv:
        i = sys.argv.index("--odds")
        a, t = b.state.get(sys.argv[i + 1]), b.state.get(sys.argv[i + 2])
        w = a.gear.weapon
        esc = a.trackers.actions_this_turn
        print(f"\n{a.id} attacking {t.id} on its turn at its escalation now ({esc}):")
        quotes = []
        while len(quotes) < 5:
            q = b.pricing.melee_attack(w.base, len(quotes) + 1, a.trackers, light=w.light)
            if q.total > a.stamina:
                break
            quotes.append(q)
        print(step_table(b, a, t, w, quotes))
        tokens = a.holds.get(t.id, 0)
        cap = b.pricing.oa_cap(a.gear.attributes.FIN, w.base)
        print(f"{a.id}'s opportunity attack on {t.id} now "
              f"(cap {cap}, tokens {tokens}, ready {a.stamina}):")
        quotes = []
        while len(quotes) < 5:
            try:
                quotes.append(b.pricing.opportunity_attack(
                    w.base, len(quotes) + 1, a.trackers, cap, stamina=a.stamina, tokens=tokens))
            except Unaffordable:
                break
        print(step_table(b, a, t, w, quotes) if quotes else "    none possible")
    if not (stop and stop[0] == "bad"):
        seen_path.write_text(json.dumps({"orders": orders[:used], "seen": len(b.log)}))
