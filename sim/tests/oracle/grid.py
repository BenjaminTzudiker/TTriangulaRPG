"""Small grid over (block slope, crit effect, defense value) at L1 and L30 to see whether a configuration
exists that meets the design targets. Uses sim's module-level knobs so duels and static checks agree."""
import random
from statistics import mean, median
from collections import Counter
import sim
from sim import Fighter, Weapon, make_fighter, max_steps, attack_cost, roll_damage, duel, pol_alpha, pol_chipkill, pol_fixed

random.seed(777)

def mk(level, md_target):
    """Build a shield+medium fighter whose Melee Defense equals md_target by adjusting AGI/FIN (FIN kept at 1 for crit 7+)."""
    if level == 1:
        # MD = 1+1+2 + even AGI(medium: every 3rd) + even FIN
        if md_target == 4: f = Fighter('X', STR=2, AGI=1, FIN=1, level=1)
        elif md_target == 5: f = Fighter('X', STR=2, AGI=3, FIN=1, level=1)   # AGI3 in medium -> +1 (10 EP; illustrative)
        else: raise ValueError
    else:
        if md_target == 5: f = Fighter('X', STR=3, AGI=2, FIN=2, CUN=1, level=30)   # +1 from FIN2
        elif md_target == 6: f = Fighter('X', STR=3, AGI=3, FIN=2, CUN=1, level=30) # +1 AGI3(med) +1 FIN2
        elif md_target == 7: f = Fighter('X', STR=3, AGI=6, FIN=2, level=30)        # AGI6 med -> +2, FIN2 -> +1
        else: raise ValueError
    f.weapon = Weapon('ls', base=2, die=8, flat=f.STR + f.FIN)
    assert f.melee_defense() == md_target, (f.melee_defense(), md_target)
    return f

def strike(make, n=4000, w=3.0):
    injs = []
    for _ in range(n):
        f = make(); k = max_steps(2, f.max_stamina())
        D, c = roll_damage(f.weapon, k, f.crit_bonus())
        p, g, cost, inj = sim.best_block(D, c, f.melee_defense(), f.armor_value(), f.max_stamina(), f.hp_max, w)
        injs.append(inj)
    return mean(injs), sum(1 for i in injs if i >= f.hp_max) / n

def duels(make, pa, pb, n=500):
    wins = Counter(); rounds = []; fw = 0; dec = 0; loser_hp = []; winner_lost = []
    for _ in range(n):
        a = make(); a.name = 'A'; b = make(); b.name = 'B'
        winner, r, first = duel(a, b, pa, pb)
        rounds.append(r)
        if winner is None: wins['draw'] += 1
        else:
            dec += 1; fw += (winner is first)
            loser = b if winner is a else a
            loser_hp.append(loser.hp); winner_lost.append(winner.hp_max - winner.hp)
    return (wins['draw'] / n, median(rounds), fw / max(1, dec), mean(winner_lost) if winner_lost else 0)

def ratio_table(make):
    f = make(); V = f.melee_defense(); A = f.armor_value(); avg = (f.weapon.die + 1) / 2 + f.weapon.flat
    out = []
    for k in range(1, 8):
        c = attack_cost(2, k)
        if c > f.max_stamina(): break
        p, g, cost, inj = sim.best_block(round(avg * k), 0, V, A, 500, 999, w=1000)
        out.append(f"{c}/{cost}")
    return " ".join(out)

print(f"{'cfg':44s} | {'att/def by k (mean roll, no crit)':34s} | full strike: HP, down | chipkill duel: draws, med rounds, first-mover, winner HP lost | alpha duel: draws, rounds, first")
for level, mds in ((1, (4, 5)), (30, (5, 6, 7))):
    for md in mds:
        for slope in (1.0, 0.5):
            for crit in ('double', 'linear2', 'linear1', 'none'):
                sim.BLOCK_SLOPE = slope; sim.CRIT_MODE = crit
                make = lambda level=level, md=md: mk(level, md)
                f = make(); r = ((f.weapon.die + 1) / 2 + f.weapon.flat) / f.melee_defense()
                mi, pd = strike(make)
                d1 = duels(make, pol_chipkill, pol_chipkill, 400)
                d2 = duels(make, pol_alpha, pol_alpha, 400)
                cfg = f"L{level} MD{md} r={r:.2f} slope={slope} crit={crit}"
                print(f"{cfg:44s} | {ratio_table(make):34s} | {mi:4.1f} HP {pd:4.0%} | {d1[0]:4.0%} {d1[1]:5.1f} {d1[2]:4.0%} {d1[3]:4.1f} | {d2[0]:4.0%} {d2[1]:5.1f} {d2[2]:4.0%}", flush=True)
sim.BLOCK_SLOPE = 1.0; sim.CRIT_MODE = 'double'
