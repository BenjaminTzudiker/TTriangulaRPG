"""Test candidate fixes to the block/step convexity mismatch. Not proposals yet; evidence for options."""
import random
from statistics import mean, median
from collections import Counter
import sim
from sim import *

random.seed(99)
OUT = []
def P(*a):
    s = ' '.join(str(x) for x in a); print(s); OUT.append(s)

def alpha_at_full(level, variant='sample', n=8000, w=3.0, def_md_bonus=0):
    injs = []
    f = make_fighter(level, variant); kmax = max_steps(f.weapon.base, f.max_stamina())
    for _ in range(n):
        D, c = roll_damage(f.weapon, kmax, f.crit_bonus())
        p, g, cost, inj = best_block(D, c, f.melee_defense() + def_md_bonus, f.armor_value(), f.max_stamina(), f.hp_max, w=w)
        injs.append(inj)
    return kmax, attack_cost(f.weapon.base, kmax), mean(injs), sum(1 for i in injs if i >= f.hp_max) / n

def kfull_table(level, variant='sample', def_md_bonus=0):
    f = make_fighter(level, variant)
    V = f.melee_defense() + def_md_bonus; A = f.armor_value(); avg = (f.weapon.die + 1) / 2 + f.weapon.flat
    row = []
    for k in range(1, 8):
        c = attack_cost(f.weapon.base, k)
        if c > f.max_stamina(): break
        D = round(avg * k)
        p, g, cost, inj = best_block(D, 0, V, A, 500, 999, w=1000)
        row.append(f"k{k}: att {c:2d} / def {cost:2d}" + (f"+{inj}hp" if inj else ""))
    return "  |  ".join(row)

def duel_stats(level, pa, pb, n=1500, variant='sample', w=3.0):
    wins = Counter(); rounds = []; fw = 0; dec = 0
    for _ in range(n):
        a = make_fighter(level, variant, 'A'); b = make_fighter(level, variant, 'B')
        winner, r, first = duel(a, b, pa, pb, w=w)
        rounds.append(r)
        if winner is None: wins['draw'] += 1
        else:
            wins[winner.name] += 1; dec += 1
            if winner is first: fw += 1
    return f"A {wins['A']/n:.0%} B {wins['B']/n:.0%} draw {wins['draw']/n:.0%} | rounds med {median(rounds)} mean {mean(rounds):.1f} | first-mover wins {fw/max(1,dec):.0%}"

def suite(label):
    P(f"\n##### {label} #####")
    for lv in (1, 30, 99):
        k, c, mi, pd = alpha_at_full(lv)
        P(f"L{lv}: alpha = {k} steps ({c} st) vs identical at full -> mean injury {mi:.1f}, P(dead) {pd:.0%}")
        P(f"     cost-to-fully-block table (mean roll, no crit): {kfull_table(lv)}")
    P("L1 alpha vs alpha:   " + duel_stats(1, pol_alpha, pol_alpha))
    P("L1 k2 vs k2:         " + duel_stats(1, pol_fixed(2), pol_fixed(2)))
    P("L1 alpha vs k2:      " + duel_stats(1, pol_alpha, pol_fixed(2)))
    P("L1 alpha vs reserve5:" + duel_stats(1, pol_alpha, pol_reserve(5)))
    P("L1 chipkill vs chipkill: " + duel_stats(1, pol_chipkill, pol_chipkill, n=800))
    P("L30 alpha vs alpha:  " + duel_stats(30, pol_alpha, pol_alpha))
    P("L30 k2 vs k2:        " + duel_stats(30, pol_fixed(2), pol_fixed(2)))
    P("L30 chipkill vs chipkill: " + duel_stats(30, pol_chipkill, pol_chipkill, n=800))

sim.STEP_SLOPE = 1; sim.BLOCK_SLOPE = 1.0
suite("BASELINE v0.9")

sim.STEP_SLOPE = 2; sim.BLOCK_SLOPE = 1.0
suite("VARIANT A: surcharge +2 per prior action (steps cost base, base+2, base+4...)")

sim.STEP_SLOPE = 1; sim.BLOCK_SLOPE = 0.5
suite("VARIANT B: perfect blocks escalate every second block (1,1,2,2,3,3...)")

sim.STEP_SLOPE = 2; sim.BLOCK_SLOPE = 0.5
suite("VARIANT A+B")

sim.STEP_SLOPE = 1; sim.BLOCK_SLOPE = 1.0
P("\n##### VARIANT C: +2 Melee Defense for everyone (baseline costs) #####")
for lv in (1, 30, 99):
    k, c, mi, pd = alpha_at_full(lv, def_md_bonus=2)
    P(f"L{lv}: alpha {k} steps ({c} st) -> mean injury {mi:.1f}, P(dead) {pd:.0%} | table: {kfull_table(lv, def_md_bonus=2)}")

P("\n##### VARIANT D: no crit doubling (crit dice still ignore 1 armor) — baseline costs #####")
_orig = sim.best_block
def bb_nodouble(D, crits, V, A, S, hp, w=3.0, death_pen=1000.0):
    best = None; eff_armor = max(0, A - crits); p = 0
    while block_cost(p) <= S:
        gmax = S - block_cost(p)
        for g in range(0, gmax + 1):
            n = p + g; res = max(0, D - n * V); pre = max(0, res + g - eff_armor); inj = pre
            cost = block_cost(p) + g; score = inj * w + cost + (death_pen if inj >= hp else 0.0)
            if best is None or score < best[0] - 1e-9 or (abs(score - best[0]) < 1e-9 and cost < best[3]):
                best = (score, p, g, cost, inj)
            if res == 0: break
        p += 1
    return best[1], best[2], best[3], best[4]
sim.best_block = bb_nodouble
import sim as S2
for lv in (1, 30, 99):
    injs = []
    f = make_fighter(lv); kmax = max_steps(2, f.max_stamina())
    for _ in range(6000):
        D, c = roll_damage(f.weapon, kmax, f.crit_bonus())
        p, g, cost, inj = bb_nodouble(D, c, f.melee_defense(), f.armor_value(), f.max_stamina(), f.hp_max, w=3)
        injs.append(inj)
    P(f"L{lv}: alpha {kmax} steps -> mean injury {mean(injs):.1f}, P(dead) {sum(1 for i in injs if i>=f.hp_max)/6000:.0%}")
# duel uses resolve_melee_attack which calls best_block from module namespace -> patched above via sim.best_block? resolve uses the name bound at def time in sim module globals
S2.best_block = bb_nodouble
P("L1 alpha vs alpha (no doubling): " + duel_stats(1, pol_alpha, pol_alpha))
P("L1 k2 vs k2 (no doubling):       " + duel_stats(1, pol_fixed(2), pol_fixed(2)))
sim.best_block = _orig; S2.best_block = _orig

with open('variants.log', 'w') as f:
    f.write("\n".join(OUT))
