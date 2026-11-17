#!/usr/bin/env python3
"""Planning calculator (my own helper; reads the engine, changes nothing).

  python3 calc.py melee WEAPON STEPS DEF ARMOR STAMINA HP
      odds of a WEAPON attack of 1..STEPS steps against a defender with that Melee Defense,
      armor, ready stamina and HP (defender blocks as the engine's solver, w = 3).
      WEAPON: longsword (1d8+3, crit 7-8) or shortsword (1d6+2, crit 5-6)
  python3 calc.py shot AIMS PENALTY DEF ARMOR STAMINA HP
      a longbow shot (1d8+1, crit 7-8, + (1+AIMS)d6, - PENALTY) against total defense DEF
      (ranged defense + cover + 1 if it dashed).

It uses no dice from any fight: these are exact odds over all rolls.
"""
import sys
from collections import defaultdict
from fractions import Fraction
from itertools import product

sys.path.insert(0, "/home/claude/work/holds/sim/src")
from stamina_engine.rules.block_solver import best_block  # noqa: E402
from stamina_engine.rules.ruleset import preset  # noqa: E402

RULES = preset("exp-holds")
WEAPONS = {"longsword": (8, 3, 2), "shortsword": (6, 2, 1)}  # die, flat, base


def melee(weapon, steps, defense, armor, stamina, hp):
    die, flat, base = WEAPONS[weapon]
    per = defaultdict(Fraction)
    for f in range(1, die + 1):
        per[(f + flat, int(f >= die - 1))] += Fraction(1, die)
    dist = {(0, 0): Fraction(1)}
    for k in range(1, steps + 1):
        nxt = defaultdict(Fraction)
        for (t, c), p in dist.items():
            for (t2, c2), p2 in per.items():
                nxt[(t + t2, c + c2)] += p * p2
        dist = nxt
        down = inj = cost = anyinj = Fraction(0)
        for (t, c), p in dist.items():
            ch = best_block(t, c, defense, armor, stamina, hp, RULES)
            down += p * (ch.injury >= hp)
            inj += p * ch.injury
            cost += p * ch.cost
            anyinj += p * (ch.injury > 0)
        price = sum(base + i for i in range(k))
        print(f"  {k} step(s) (fresh cost {price:>2}): down {float(down):6.1%}  wounded {float(anyinj):6.1%}  "
              f"injury {float(inj):5.2f}  defender spends {float(cost):5.2f}")


def shot(aims, penalty, defense, armor, stamina, hp):
    down = inj = cost = anyinj = Fraction(0)
    n = 1 + aims
    for d8 in range(1, 9):
        for aim in product(range(1, 7), repeat=n):
            p = Fraction(1, 8) * Fraction(1, 6) ** n
            total = max(0, d8 + 1 + sum(aim) - penalty)
            crit = int(d8 >= 7)
            ch = best_block(total, crit, defense, armor, stamina, hp, RULES, ranged=True, limit=d8 + 1)
            down += p * (ch.injury >= hp)
            inj += p * ch.injury
            cost += p * ch.cost
            anyinj += p * (ch.injury > 0)
    price = 4 + sum(1 + 1 + i for i in range(aims))
    print(f"  shot, {aims} aim(s) (fresh cost {price}), penalty {penalty}, defense {defense}: down {float(down):6.1%}  "
          f"wounded {float(anyinj):6.1%}  injury {float(inj):5.2f}  defender spends {float(cost):5.2f}")


if __name__ == "__main__":
    kind = sys.argv[1]
    args = sys.argv[2:]
    if kind == "melee":
        melee(args[0], *map(int, args[1:]))
    else:
        shot(*map(int, args))
