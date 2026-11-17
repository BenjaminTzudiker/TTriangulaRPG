#!/usr/bin/env python3
"""My own odds calculator for planning (reads the engine, changes nothing).
usage: python3 calc.py HP STAMINA [steps_max]   -> longsword (1d8+3, crit on 7-8) vs def 3 armor 2
"""
import pathlib
import sys
from collections import defaultdict
from fractions import Fraction

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "src"))  # sim/src
from stamina_engine.rules.block_solver import best_block
from stamina_engine.rules.ruleset import preset

rules = preset("exp-holds")

def per_step():
    per = defaultdict(Fraction)
    for f in range(1, 9):
        crit = 1 if f >= 7 else 0
        per[(f + 3, crit)] += Fraction(1, 8)
    return per

def table(hp, st, kmax=5, defense=3, armor=2):
    per = per_step()
    dist = {(0, 0): Fraction(1)}
    out = []
    for k in range(1, kmax + 1):
        nxt = defaultdict(Fraction)
        for (t, c), p in dist.items():
            for (t2, c2), p2 in per.items():
                nxt[(t + t2, c + c2)] += p * p2
        dist = nxt
        down = inj = cost = Fraction(0)
        hist = defaultdict(Fraction)
        for (t, c), p in dist.items():
            ch = best_block(t, c, defense, armor, st, hp, rules)
            down += p * (ch.injury >= hp)
            inj += p * ch.injury
            cost += p * ch.cost
            hist[min(ch.injury, hp)] += p
        out.append((k, float(down), float(inj), float(cost), {i: round(float(p), 3) for i, p in sorted(hist.items())}))
    return out

if __name__ == "__main__":
    hp, st = int(sys.argv[1]), int(sys.argv[2])
    kmax = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    print(f"defender hp {hp}, ready stamina {st} (longsword attacker)")
    for k, down, inj, cost, hist in table(hp, st, kmax):
        print(f"  {k} step(s): down {down:6.1%}  mean injury {inj:5.2f}  defender spends {cost:5.2f}   injury dist {hist}")
