#!/usr/bin/env python3
"""Odds for hypothetical states, using table.py's own step_table (probabilities only, no dice).

usage: python3 whatif.py FIGHT ATTACKER TARGET [st=N] [hp=N] [esc=N] [oa=TOKENS]
  st  = target's ready stamina (default: now), hp = target's HP (default: now),
  esc = attacker's escalation (default: now), oa = show an opportunity attack with this many
  tokens instead of an on-turn attack.
"""
import copy
import dataclasses
import sys

import table

name, aid, tid = sys.argv[1:4]
kw = dict(a.split("=") for a in sys.argv[4:])
scen, orders = table.load(name)
b, d, result, stop = table.play(scen, orders, quiet=True)
a, t = b.state.get(aid), b.state.get(tid)
t2 = copy.copy(t)
if "hp" in kw:
    t2.dying = dataclasses.replace(t.dying, hp=int(kw["hp"]))
st = int(kw["st"]) if "st" in kw else t.stamina
w = a.gear.weapon
tr = a.trackers
if "esc" in kw:
    tr = dataclasses.replace(tr, actions_this_turn=int(kw["esc"]))
quotes = []
if "oa" in kw:
    cap = b.pricing.oa_cap(a.gear.attributes.FIN, w.base)
    tok = int(kw["oa"])
    while len(quotes) < 5:
        try:
            quotes.append(b.pricing.opportunity_attack(w.base, len(quotes) + 1, tr, cap,
                                                       stamina=99, tokens=tok))
        except table.Unaffordable:
            break
    print(f"{aid} OA on {tid} (cap {cap}, tokens {tok}); {tid} ready {st}, hp {t2.hp}")
else:
    while len(quotes) < 5:
        quotes.append(b.pricing.melee_attack(w.base, len(quotes) + 1, tr, light=w.light))
    print(f"{aid} attacks {tid} at esc {tr.actions_this_turn}; {tid} ready {st}, hp {t2.hp}")
print(table.step_table(b, a, t2, w, quotes, stamina=st) if quotes else "    none possible")
