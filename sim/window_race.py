# ruff: noqa: E501
"""The off-turn window as a race: a fleer who wants distance and a pinner who wants adjacency,
deterministic policies, under each window-order rule. Measures who ends adjacent, what each
paid (movement, avoidance, OAs) and how many questions the window asked.

Run from sim/ with PYTHONPATH=src: python3 window_race.py"""

import sys
from dataclasses import dataclass

sys.path.insert(0, ".")

from stamina_engine.agents.decisions import (
    Avoid,
    AvoidOA,
    BlocksRequest,
    Commitment,
    EndTurn,
    Move,
    MoveAnswer,
    OATake,
    OffTurnMove,
    Pass,
    TakeOA,
    TurnAnswer,
    TurnCommand,
)
from stamina_engine.engine.events import Spent
from stamina_engine.grid.battlefield import parse_map
from stamina_engine.model.build import Attributes, Build, Loadout
from stamina_engine.model.derive import derive
from stamina_engine.rules.exchange import Blocks
from stamina_engine.rules.ruleset import preset
from tests.golden.test_off_turn_battles import run

RULES = preset("v0.9")
FIELD = parse_map("\n".join(["." * 40] * 5))


def built(name: str, agility: int, finesse: int = 1, weapon: str = "longsword") -> Build:
    return Build(
        name, 1, Attributes(STR=2, AGI=agility, FIN=finesse),
        (("m", Loadout(armor="medium", weapon=weapon, grip="one", off_hand="shield")),),
        ("fighter",), budget="ignore",
    )


@dataclass
class Fleer:
    """Wants to be out of the pinner's one-purchase reach. Moves one purchase (+x) when the
    enemy is within `trigger` squares; pays to avoid every OA it can."""

    enemy: str
    trigger: int
    budget: int
    squares: int
    asked: int = 0
    spent_budget: int = 0

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        return EndTurn()

    def commitment(self, request: Commitment) -> int:
        return 0

    def blocks(self, request: BlocksRequest) -> Blocks:
        return Blocks()

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer:
        self.asked += 1
        if request.moves is None:
            return Pass()
        me = request.moves.start
        e = request.observation.view(self.enemy).pos
        if e is None or abs(e[0] - me[0]) > self.trigger:
            return Pass()
        path = tuple((me[0] + i, me[1]) for i in range(1, self.squares + 1))
        if path[-1] not in request.moves.destinations:
            return Pass()
        price = request.moves.price_by_length[len(path)]
        if self.spent_budget + price > self.budget:
            return Pass()
        self.spent_budget += price
        return Move(path)

    def avoid(self, request: AvoidOA) -> Avoid:
        return Avoid(tuple(request.enemies))

    def take_oa(self, request: TakeOA) -> OATake:
        return OATake()

    def ability(self, request: object) -> Pass:
        return Pass()


@dataclass
class Pinner:
    """Wants to be adjacent to the fleer: moves to the adjacent square (+x side) with as many
    purchases as that takes, within budget; `segments` caps purchases per move. Takes OAs."""

    target: str
    budget: int
    squares: int
    segments: int = 0  # 0: whole move at once
    asked: int = 0
    spent_budget: int = 0

    def turn_command(self, request: TurnCommand) -> TurnAnswer:
        return EndTurn()

    def commitment(self, request: Commitment) -> int:
        return 0

    def blocks(self, request: BlocksRequest) -> Blocks:
        return Blocks()

    def off_turn_move(self, request: OffTurnMove) -> MoveAnswer:
        self.asked += 1
        if request.moves is None:
            return Pass()
        me = request.moves.start
        t = request.observation.view(self.target).pos
        if t is None or abs(t[0] - me[0]) <= 1:
            return Pass()
        need = t[0] - 1 - me[0]  # squares to the square left of the target
        purchases = -(-need // self.squares)
        if self.segments:
            purchases = min(purchases, self.segments)
        n = min(need, purchases * self.squares)
        path = tuple((me[0] + i, me[1]) for i in range(1, n + 1))
        if len(path) >= len(request.moves.price_by_length) or path[-1] not in request.moves.destinations:
            return Pass()
        price = request.moves.price_by_length[len(path)]
        if self.spent_budget + price > self.budget:
            return Pass()
        self.spent_budget += price
        return Move(path)

    def avoid(self, request: AvoidOA) -> Avoid:
        return Avoid()

    def take_oa(self, request: TakeOA) -> OATake:
        return OATake("m", 1)

    def ability(self, request: object) -> Pass:
        return Pass()


def race(order: str, restart: bool, fleer_higher: bool, agi_f: int, agi_p: int,
         budget_f: int, budget_p: int, segments: int = 0, start_gap: int = 2, trigger: int = 2,
         verbose: bool = False):
    """One window: a neutral creature T (on F's team, highest initiative) takes an empty turn;
    the window after it is the race. Events after the second TurnStarted are ignored."""
    rules = RULES.override({"off_turn": {"order": order, "restart_after_move": restart,
                                         "purchase_cap": segments}})
    fp = derive(built("F", agi_f), rules)
    pp = derive(built("P", agi_p), rules)
    tp = derive(built("T", 0), rules)
    sq_f = fp.main.squares_per_purchase
    sq_p = pp.main.squares_per_purchase
    f = Fleer("P", trigger, budget_f, sq_f)
    p = Pinner("F", budget_p, sq_p, segments)
    t = Fleer("P", -1, 0, 1)  # never moves
    ini_f, ini_p = ((10, 10), (2, 2)) if fleer_higher else ((2, 2), (10, 10))
    result = run(
        [("T", "red", tp, (30, 4), t, (12, 12)),
         ("F", "red", fp, (2 + start_gap, 2), f, ini_f),
         ("P", "blue", pp, (2, 2), p, ini_p)],
        rules=rules, field_=FIELD, rounds=1,
    )
    from stamina_engine.engine.events import Moved, TurnStarted
    pos = {"F": (2 + start_gap, 2), "P": (2, 2)}
    spent = {"F": {}, "P": {}}
    turns = 0
    seq = []
    for e in result.log:
        if isinstance(e, TurnStarted):
            turns += 1
            if turns == 2:
                break
        if isinstance(e, Moved) and e.who in pos:
            pos[e.who] = e.to
            seq.append(e.who)
        if isinstance(e, Spent) and e.who in spent:
            spent[e.who][e.category] = spent[e.who].get(e.category, 0) + e.amount
    gap = abs(pos["F"][0] - pos["P"][0])
    asks = sum(1 for d in result.decisions if d.kind == "off_turn_move" and d.context and "after T" in " ".join(d.context))
    if verbose:
        print("   moves:", "".join(seq))
    return gap, spent["F"], spent["P"], None, None, asks


if __name__ == "__main__":
    print("Window race: fleer F (wants gap > 1) vs pinner P (wants adjacency), start gap 2, one round, "
          "F's and P's empty turns each followed by a window. Budgets are off-turn stamina each will spend.")
    print("cells: final gap | F paid {move, avoid} | P paid {move, OA} | asks\n")
    orders = (("ascending_initiative", False, "asc"), ("descending_initiative", False, "desc"),
              ("descending_initiative", True, "desc+restart"))
    for agi_f, agi_p, bf, bp, seg, note in (
        (1, 1, 6, 6, 0, "equal AGI 1, equal budgets 6 (three purchases each)"),
        (1, 1, 6, 10, 0, "equal AGI 1, pinner richer (10 vs 6)"),
        (1, 1, 10, 6, 0, "equal AGI 1, fleer richer (10 vs 6)"),
        (3, 1, 6, 6, 0, "fleer AGI 3 (3 sq/purchase) vs pinner AGI 1 (2), equal budgets"),
        (1, 3, 6, 6, 0, "fleer AGI 1 vs pinner AGI 3, equal budgets"),
        (3, 1, 6, 6, 1, "fleer AGI 3 vs pinner AGI 1, one purchase per move (segment reactions)"),
        (1, 3, 6, 6, 1, "fleer AGI 1 vs pinner AGI 3, one purchase per move"),
        (1, 1, 6, 6, 1, "equal AGI 1, one purchase per move"),
    ):
        print(f"### {note}")
        for order, restart, label in orders:
            for fleer_higher in (True, False):
                gap, sf, sp, hp_p, hp_f, asks = race(order, restart, fleer_higher, agi_f, agi_p, bf, bp, seg)
                who = "F higher init" if fleer_higher else "P higher init"
                fm, fa = sf.get("off_turn_move", 0), sf.get("avoid", 0)
                pm, po = sp.get("off_turn_move", 0), sp.get("opportunity", 0)
                print(f"  {label:13s} {who:14s}: gap {gap} {'(adjacent)' if gap <= 1 else '          '} | F move {fm:2d} avoid {fa:2d} | P move {pm:2d} OA {po:2d} | asks {asks}")
        print()
