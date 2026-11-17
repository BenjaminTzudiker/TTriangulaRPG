#!/usr/bin/env python3
"""Planning odds for hypothetical states (my own helper; does not change the fight).

usage: python3 calc.py ATTACKER TARGET COSTS [st=N] [hp=N] [def=N] [arm=N]
  COSTS: comma list of step costs, e.g. 3,4,5 (only the number of steps matters for dice;
         the costs are printed back for reference).
  st/hp/def/arm override the target's ready stamina, HP, melee defense, armor.
Weapons, defenses and HP come from the fight's current state (replayed quietly).
"""
import sys
from collections import defaultdict
from fractions import Fraction

sys.path.insert(0, "/home/claude/work/hold/play/m3")
import table  # noqa: E402
from stamina_engine.rules.block_solver import best_block  # noqa: E402

scen, orders = table.load("/home/claude/work/hold/play/m3/sc_next")
b, d, result, stop = table.play(scen, orders, 0, quiet=True)

att, tgt, costs = sys.argv[1], sys.argv[2], [int(c) for c in sys.argv[3].split(",")]
opts = dict(a.split("=") for a in sys.argv[4:])
a, t = b.state.get(att), b.state.get(tgt)
w = a.gear.weapon
rules = b.rules
st = int(opts.get("st", t.stamina))
hp = int(opts.get("hp", t.hp))
dfn = int(opts.get("def", t.gear.melee_defense))
armor = int(opts.get("arm", max(0, t.gear.armor - w.piercing)))
per = defaultdict(Fraction)
sizes = [dd.size for dd in w.damage.dice for _ in range(dd.count)]


def faces(i, tot, crits, p):
    if i == len(sizes):
        per[(max(w.damage.step_floor, tot + w.damage.flat), crits)] += p
        return
    for f in range(1, sizes[i] + 1):
        crit = int(rules.crit.is_crit(f, sizes[i], w.crit_widen))
        faces(i + 1, tot + f, crits + crit, p / sizes[i])


faces(0, 0, 0, Fraction(1))
dist = {(0, 0): Fraction(1)}
print(f"{att} ({w.name if hasattr(w, 'name') else 'weapon'}) on {tgt}: st={st} hp={hp} def={dfn} armor={armor}")
for k in range(1, len(costs) + 1):
    nxt = defaultdict(Fraction)
    for (tt, c), p in dist.items():
        for (t2, c2), p2 in per.items():
            nxt[(tt + t2, c + c2)] += p * p2
    dist = nxt
    down = inj = cost = Fraction(0)
    for (tt, c), p in dist.items():
        ch = best_block(tt, c, dfn, armor, st, hp, rules)
        down += p * (ch.injury >= hp)
        inj += p * ch.injury
        cost += p * ch.cost
    print(f"  {k} step(s) cost {sum(costs[:k]):>2}: down {float(down):5.1%}  injury {float(inj):4.2f}  "
          f"target spends {float(cost):4.2f}")
