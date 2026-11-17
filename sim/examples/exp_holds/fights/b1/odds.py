#!/usr/bin/env python3
"""My own what-if helper (read-only use of table.py and the engine): the odds of an attack
with a given weapon against a defender with a GIVEN ready stamina and hp.

usage: python3 odds.py WEAPON DEF ARMOR STAMINA HP [ESC] [MAXSTEPS]
  WEAPON: ls (longsword 1d8+3 base 2), gs (greatsword 1d12+5 base 3), sp (spear 1d8+2 base 2, crit top face)
  e.g.  python3 odds.py gs 3 2 7 10      greatsword vs a sample fighter with 7 ready, 10 hp
Also: python3 odds.py WEAPON DEF ARMOR STAMINA HP oa BUDGET   (opportunity attack within a budget)
"""
import sys
from collections import defaultdict
from fractions import Fraction

import table  # noqa: E402  (adds the engine to sys.path)
from stamina_engine.rules.block_solver import best_block  # noqa: E402
from stamina_engine.rules.ruleset import preset  # noqa: E402

RULES = preset("exp-holds")
WEAPONS = {  # die, flat, base, crit faces
    "ls": (8, 3, 2, (7, 8)),
    "gs": (12, 5, 3, (11, 12)),
    "sp": (8, 2, 2, (8,)),
}


def table_for(wname, defense, armor, stamina, hp, costs):
    die, flat, base, crits = WEAPONS[wname]
    per = defaultdict(Fraction)
    for f in range(1, die + 1):
        per[(f + flat, int(f in crits))] += Fraction(1, die)
    dist = {(0, 0): Fraction(1)}
    out = []
    for k, cost in enumerate(costs, 1):
        nxt = defaultdict(Fraction)
        for (t, c), p in dist.items():
            for (t2, c2), p2 in per.items():
                nxt[(t + t2, c + c2)] += p * p2
        dist = nxt
        down = inj = spend = Fraction(0)
        for (t, c), p in dist.items():
            ch = best_block(t, c, defense, armor, stamina, hp, RULES)
            down += p * (ch.injury >= hp)
            inj += p * ch.injury
            spend += p * ch.cost
        out.append(f"  {k} step(s): costs {sum(costs[:k]):>2}  down {float(down):6.1%}  injury {float(inj):5.2f}  "
                   f"target spends {float(spend):5.2f}")
    return "\n".join(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    w, defense, armor, stamina, hp = a[0], int(a[1]), int(a[2]), int(a[3]), int(a[4])
    base = WEAPONS[w][2]
    if len(a) > 5 and a[5] == "oa":
        budget = int(a[6])
        costs, tot = [], 0
        while tot + base + len(costs) <= budget:
            costs.append(base + len(costs))
            tot += costs[-1]
        print(f"{w} opportunity attack, budget {budget}, vs def {defense} armor {armor} ready {stamina} hp {hp}:")
        print(table_for(w, defense, armor, stamina, hp, costs) if costs else "  none possible")
    else:
        esc = int(a[5]) if len(a) > 5 else 0
        n = int(a[6]) if len(a) > 6 else 4
        costs = [base + esc + i for i in range(n)]
        print(f"{w} at escalation {esc} vs def {defense} armor {armor} ready {stamina} hp {hp}:")
        print(table_for(w, defense, armor, stamina, hp, costs))
