#!/usr/bin/env python3
"""Odds helper for hand play (my own; uses the same engine calls as table.py's step_table).

python3 calc.py STEPS HP READY [ESC] [CHAIN...]
  Longsword (1d8+3) attack of STEPS steps on a sample fighter (MD 3, armor 2) with HP and READY.
  Prints down chance, mean injury, mean stamina the target spends, and the distribution of
  (hp, ready) after the attack.
python3 calc.py seq HP READY S1 S2 ...
  Several separate attacks in a row on the same target (no recovery in between), e.g. an
  attack then an OA. Prints the cumulative down chance after each.
"""
import os
import sys
from collections import defaultdict
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.normpath(os.path.join(HERE, "..", ".."))]  # table.py
import table as T  # noqa: E402

scen, _ = T.load(os.path.join(HERE, "rg_next"))
b, _d = T.build(scen, [])
rules = b.rules
X = b.state.get("X")
W = X.gear.weapon
MD = X.gear.melee_defense
ARMOR = max(0, X.gear.armor - W.piercing)

per = defaultdict(Fraction)
sizes = [d.size for d in W.damage.dice for _ in range(d.count)]


def faces(i, tot, crits, p):
    if i == len(sizes):
        total = max(W.damage.step_floor, tot + W.damage.flat)
        per[(total, crits)] += p
        return
    for f in range(1, sizes[i] + 1):
        crit = int(rules.crit.is_crit(f, sizes[i], W.crit_widen))
        faces(i + 1, tot + f, crits + crit, p / sizes[i])


faces(0, 0, 0, Fraction(1))
_cache = {}


def total_dist(k):
    if k in _cache:
        return _cache[k]
    dist = {(0, 0): Fraction(1)}
    for _ in range(k):
        nxt = defaultdict(Fraction)
        for (t, c), p in dist.items():
            for (t2, c2), p2 in per.items():
                nxt[(t + t2, c + c2)] += p * p2
        dist = nxt
    _cache[k] = dist
    return dist


def after(k, hp, st):
    """distribution over (hp_after, st_after) after a k-step attack; hp<=0 means down."""
    out = defaultdict(Fraction)
    if k == 0:
        out[(hp, st)] = Fraction(1)
        return out
    for (t, c), p in total_dist(k).items():
        ch = best_block(t, c, st, hp)
        h2 = hp - ch.injury
        out[(h2, max(0, min(st - ch.cost, 6 + h2)))] += p  # engine clamps ready to 6 + hp
    return out


def best_block(t, c, st, hp):
    return T.best_block(t, c, MD, ARMOR, st, hp, rules)


def summary(dist):
    down = sum(p for (h, s), p in dist.items() if h <= 0)
    return float(down)


def main(argv):
    if argv[0] == "seq":
        hp, st = int(argv[1]), int(argv[2])
        dist = {(hp, st): Fraction(1)}
        for k in map(int, argv[3:]):
            nxt = defaultdict(Fraction)
            for (h, s), p in dist.items():
                if h <= 0:
                    nxt[(h, s)] += p
                    continue
                for key, p2 in after(k, h, s).items():
                    nxt[key] += p * p2
            dist = nxt
            alive = [(h, s, p) for (h, s), p in dist.items() if h > 0]
            pa = sum(p for *_, p in alive)
            mh = sum(h * p for h, s, p in alive) / pa if pa else 0
            ms = sum(s * p for h, s, p in alive) / pa if pa else 0
            print(f"after {k}-step: down {summary(dist):6.1%}; if up: mean hp {float(mh):.2f}, "
                  f"mean ready {float(ms):.2f}")
        return
    k, hp, st = int(argv[0]), int(argv[1]), int(argv[2])
    dist = after(k, hp, st)
    inj = sum((hp - h) * p for (h, s), p in dist.items())
    spend = sum((st - s) * p for (h, s), p in dist.items())
    print(f"{k} step(s) on hp {hp} ready {st}: down {summary(dist):6.1%}  mean injury "
          f"{float(inj):.2f}  mean spend {float(spend):.2f}")
    if "-v" in argv:
        rows = sorted(dist.items(), key=lambda kv: (-kv[0][0], -kv[0][1]))
        for (h, s), p in rows:
            if p > 0.005:
                print(f"   hp {h:>3} ready {s:>3}: {float(p):5.1%}")


if __name__ == "__main__":
    main(sys.argv[1:])
