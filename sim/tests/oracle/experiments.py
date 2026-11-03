import random, sys, math
from statistics import mean, median, pstdev
from collections import Counter
from sim import *

random.seed(20261101)
OUT = []
def P(*a):
    s = ' '.join(str(x) for x in a)
    print(s); OUT.append(s)

# ------------------------------------------------------------------
P("=== 1. STATIC: cost to fully stop a k-step longsword(1d8+3, base 2) attack at its MEAN roll ===")
P("Attack cost for k steps: ", {k: attack_cost(2, k) for k in range(1, 6)})
for V in (2, 3, 4, 5, 6):
    for A in (0, 2, 3):
        row = []
        for k in range(1, 6):
            D = round(7.5 * k)
            p, g, cost, inj = best_block(D, 0, V, A, 200, 100, w=1000)  # force zero injury if possible
            row.append(f"k{k}:{cost}st" + (f"/{inj}hp" if inj else ""))
        P(f"MD {V} armor {A}: " + "  ".join(row))
P("Perfect-block cost ~ (D/V)^2/2: doubling MD quarters the cost. Attack cost grows ~k^2/2 but blocks ~2k^2.")

# ------------------------------------------------------------------
P("\n=== 2. STATIC: same attack, same defender spend, outcome by crit count (variance from dice) ===")
# 2-step attack (mean 15) vs sample fighter (MD4 armor2), defender spends exactly 5 (p2 g2) vs optimal
for crits in (0, 1, 2):
    p, g, cost, inj = best_block(15, crits, 4, 2, 14, 8, w=3)
    # fixed spend p2g2
    n = 4; res = max(0, 15 - 16); pre = max(0, res + 2 - max(0, 2 - crits)); inj_fixed = pre * 2 if crits else pre
    P(f"2-step 15 dmg, {crits} crit dice: optimal p{p}/g{g} cost {cost} -> {inj} HP | fixed p2g2 (5 st) -> {inj_fixed} HP")
P("P(>=1 crit) with FIN1 on d8 (25%/die): 2 dice 44%, 3 dice 58%, 4 dice 68%. FIN3: 37.5%/die -> 4 dice 85%.")

# ------------------------------------------------------------------
P("\n=== 3. STATIC: alpha strike (4 steps = 14 st, 4d8+12, mean 30) vs sample fighter at full ===")
res = Counter(); injs = []
for _ in range(20000):
    w = Weapon('ls', 2, 8, flat=3)
    D, c = roll_damage(w, 4, 1)
    p, g, cost, inj = best_block(D, c, 4, 2, 14, 8, w=3)
    injs.append(inj); res[(inj >= 8)] += 1
P(f"Defender at full (14 st, 8 HP): mean injury {mean(injs):.2f}, P(dead) {res[True]/20000:.1%}, injury dist {sorted(Counter(injs).items())}")
injs13 = []
for _ in range(20000):
    w = Weapon('ls', 2, 8, flat=3)
    D, c = roll_damage(w, 4, 1)
    p, g, cost, inj = best_block(D, c, 4, 2, 13, 8, w=3)
    injs13.append(inj)
P(f"Defender at 13 st: mean injury {mean(injs13):.2f}, P(dead) {sum(1 for i in injs13 if i>=8)/20000:.1%}")
injs9 = []
for _ in range(20000):
    w = Weapon('ls', 2, 8, flat=3)
    D, c = roll_damage(w, 4, 1)
    p, g, cost, inj = best_block(D, c, 4, 2, 9, 8, w=3)
    injs9.append(inj)
P(f"Defender at 9 st (after one 2-step attack): mean injury {mean(injs9):.2f}, P(dead) {sum(1 for i in injs9 if i>=8)/20000:.1%}")

# ------------------------------------------------------------------
def run_duels(fa, fb, pa, pb, n=2000, w=3.0, label=''):
    wins = Counter(); rounds = []; first_wins = 0; first_n = 0
    wounds_a = []; wounds_b = []; final_hp = []
    for _ in range(n):
        a = fa(); b = fb()
        winner, r, first = duel(a, b, pa, pb, w=w)
        rounds.append(r)
        if winner is None:
            wins['draw'] += 1
        else:
            wins[winner.name] += 1
            if winner is first: first_wins += 1
            first_n += 1
        wounds_a += a.wounds_taken; wounds_b += b.wounds_taken
        final_hp.append((a.hp, b.hp))
    P(f"{label}: wins {dict(wins)} | rounds mean {mean(rounds):.1f} median {median(rounds)} | "
      f"P(first mover wins | decisive) {first_wins/max(1,first_n):.0%} | "
      f"wound sizes A {sorted(Counter(wounds_a).items())[:8]} B {sorted(Counter(wounds_b).items())[:8]}")
    return wins, rounds

P("\n=== 4. 1v1 DUEL, level 1 sample fighter vs identical (strategy matrix). w=3 (1 HP ~ 3 stamina) ===")
L1 = lambda name: (lambda: make_fighter(1, 'sample', name))
pols = {'alpha': pol_alpha, 'k3': pol_fixed(3), 'k2': pol_fixed(2), 'k1': pol_fixed(1),
        'reserve5': pol_reserve(5), 'chipkill': pol_chipkill}
names = list(pols)
P("Row = A's policy, col = B's policy; entry = A win% / draw% (30-round cap) / mean rounds")
header = "         " + "".join(f"{n:>22}" for n in names)
P(header)
for na in names:
    row = f"{na:>8} "
    for nb in names:
        wins = Counter(); rs = []
        N = 600
        for _ in range(N):
            a = make_fighter(1, 'sample', 'A'); b = make_fighter(1, 'sample', 'B')
            winner, r, first = duel(a, b, pols[na], pols[nb])
            wins['A' if winner is a else ('B' if winner is b else 'draw')] += 1; rs.append(r)
        row += f"{wins['A']/N:5.0%}/{wins['draw']/N:4.0%}/{mean(rs):4.1f}      "
    P(row)

P("\n--- detail: alpha vs alpha, k2 vs k2, chipkill vs chipkill ---")
run_duels(L1('A'), L1('B'), pol_alpha, pol_alpha, label='alpha vs alpha')
run_duels(L1('A'), L1('B'), pol_fixed(2), pol_fixed(2), label='k2 vs k2')
run_duels(L1('A'), L1('B'), pol_chipkill, pol_chipkill, label='chipkill vs chipkill')
run_duels(L1('A'), L1('B'), pol_greedy, pol_greedy, n=300, label='greedy(1-ply) vs greedy')

P("\n--- sample log: alpha vs alpha ---")
random.seed(7)
a = make_fighter(1, 'sample', 'A'); b = make_fighter(1, 'sample', 'B'); log = []
duel(a, b, pol_alpha, pol_alpha, log=log)
for l in log[:8]: P("  " + l)
P("\n--- sample log: chipkill vs chipkill ---")
random.seed(11)
a = make_fighter(1, 'sample', 'A'); b = make_fighter(1, 'sample', 'B'); log = []
duel(a, b, pol_chipkill, pol_chipkill, log=log)
for l in log[:14]: P("  " + l)

# ------------------------------------------------------------------
P("\n=== 5. 1v1 at level 30 and 99 ===")
for lv, var in ((30, 'sample'), (30, 'strbrute'), (99, 'sample')):
    f = make_fighter(lv, var, 'X'); P(describe(f))
L30 = lambda name: (lambda: make_fighter(30, 'sample', name))
run_duels(L30('A'), L30('B'), pol_alpha, pol_alpha, label='L30 alpha vs alpha')
run_duels(L30('A'), L30('B'), pol_fixed(2), pol_fixed(2), label='L30 k2 vs k2')
run_duels(L30('A'), L30('B'), pol_chipkill, pol_chipkill, label='L30 chipkill vs chipkill')
run_duels(L30('A'), L30('B'), pol_alpha, pol_fixed(2), label='L30 alpha vs k2')
run_duels(L30('A'), L30('B'), pol_alpha, pol_chipkill, label='L30 alpha vs chipkill')
B30 = lambda name: (lambda: make_fighter(30, 'strbrute', name))
run_duels(B30('A'), L30('B'), pol_alpha, pol_alpha, label='L30 STR-brute(MD4) alpha vs sample(MD6) alpha')
run_duels(B30('A'), L30('B'), pol_chipkill, pol_chipkill, label='L30 STR-brute chipkill vs sample chipkill')
L99 = lambda name: (lambda: make_fighter(99, 'sample', name))
run_duels(L99('A'), L99('B'), pol_alpha, pol_alpha, label='L99 alpha vs alpha')
run_duels(L99('A'), L99('B'), pol_chipkill, pol_chipkill, label='L99 chipkill vs chipkill')
# static alpha at L30
injs = []
for _ in range(20000):
    f = make_fighter(30, 'sample'); kmax = max_steps(2, f.max_stamina())
    D, c = roll_damage(f.weapon, kmax, f.crit_bonus())
    p, g, cost, inj = best_block(D, c, f.melee_defense(), f.armor_value(), f.max_stamina(), f.hp_max, w=3)
    injs.append(inj)
P(f"L30 alpha ({kmax} steps, {attack_cost(2,kmax)} st) vs identical at full: mean injury {mean(injs):.2f} of {f.hp_max} HP, P(dead) {sum(1 for i in injs if i>=f.hp_max)/20000:.1%}")
injs = []
for _ in range(20000):
    f = make_fighter(99, 'sample'); kmax = max_steps(2, f.max_stamina())
    D, c = roll_damage(f.weapon, kmax, f.crit_bonus())
    p, g, cost, inj = best_block(D, c, f.melee_defense(), f.armor_value(), f.max_stamina(), f.hp_max, w=3)
    injs.append(inj)
P(f"L99 alpha ({kmax} steps, {attack_cost(2,kmax)} st) vs identical at full: mean injury {mean(injs):.2f} of {f.hp_max} HP, P(dead) {sum(1 for i in injs if i>=f.hp_max)/20000:.1%}")

# ------------------------------------------------------------------
P("\n=== 6. ONE DEFENDER vs THREE ATTACKERS (level 1; attackers = sample fighters; defender = sample fighter) ===")
def one_v_three(def_variant='sample', att_policy=pol_fixed(2), def_attacks=True, n=1000, w=3.0, att_variant='sample'):
    rounds = []; dead = 0; dmg_taken = []; att_dead = 0
    for _ in range(n):
        d = make_fighter(1, def_variant, 'D')
        atts = [make_fighter(1, att_variant, f'A{i}') for i in range(3)]
        order = sorted([d] + atts, key=lambda f: f.initiative(), reverse=True)
        r = 0; finished = False
        while r < 20 and not finished:
            r += 1
            for actor in order:
                if actor.hp <= 0: continue
                actor.on_turn_actions = 0
                if actor is d:
                    if def_attacks:
                        # attack the most-wounded / lowest-stamina living attacker with k=2
                        alive = [x for x in atts if x.hp > 0]
                        if alive:
                            tgt = min(alive, key=lambda x: (x.stamina, x.hp))
                            k = pol_fixed(2)(d, tgt)
                            if k: resolve_melee_attack(d, tgt, k, w)
                else:
                    k = att_policy(actor, d)
                    if k: resolve_melee_attack(actor, d, k, w)
                    if d.hp <= 0:
                        finished = True; dead += 1; break
                actor.end_turn_recover()
        rounds.append(r); dmg_taken.append(d.hp_max - d.hp)
        att_dead += sum(1 for x in atts if x.hp <= 0)
    P(f"  defender {def_variant}, attackers {att_variant} using {getattr(att_policy,'__name__','k2')}: P(defender down within 20 rounds) {dead/n:.0%}, "
      f"rounds-to-down mean {mean(rounds):.1f} median {median(rounds)}, attackers downed per fight {att_dead/n:.2f}")
one_v_three('sample', pol_fixed(2))
one_v_three('sample', pol_fixed(1))
one_v_three('heavy', pol_fixed(2))
one_v_three('sample', pol_chipkill)
one_v_three('sample', pol_fixed(2), def_attacks=False)

# ------------------------------------------------------------------
P("\n=== 7. RANGED: static block costs vs Ranged Defense (shortbow 1d6+FIN2, longbow 1d8+FIN2+STR1; aim 1d6+2) ===")
def ranged_attack(shot_die, shot_flat, aims, fin_bonus_crit, aim_can_crit=True, medium=False):
    D = 0; c = 0
    r = random.randint(1, shot_die); D += r + shot_flat
    if r >= shot_die - fin_bonus_crit: c += 1
    for i in range(aims):
        if medium and i == 0:
            D += 2  # FIN only
            continue
        r = random.randint(1, 6); D += r + 2
        if aim_can_crit and r >= 6 - fin_bonus_crit: c += 1
    return D, c
for label, die, flat, base in (('shortbow', 6, 2, 3), ('longbow', 8, 3, 5)):
    for aims in (0, 1, 2, 3):
        cost = base + sum(1 + i for i in range(aims))
        for RD, A, who in ((1, 0, 'unarmored no shield (wizard, 6hp)'), (1, 1, 'light armor no shield (archer/2H, 7hp)'), (3, 2, 'shield+medium (sample fighter)'), (8, 2, 'shield+medium + 3/4 cover (dive)')):
            injs = []; costs = []
            hp = 6 if 'wizard' in who else (7 if 'archer' in who else 8)
            S = 12 if 'wizard' in who else (13 if 'archer' in who else 14)
            for _ in range(4000):
                D, c = ranged_attack(die, flat, aims, 1)
                p, g, bc, inj = best_block(D, c, RD, A, S, hp, w=3)
                injs.append(inj); costs.append(bc)
            P(f"  {label} +{aims} aim ({cost} st) vs {who:42s}: target spends {mean(costs):4.1f} st, takes {mean(injs):4.1f} HP, P(down) {sum(1 for i in injs if i>=hp)/4000:4.0%}")
P("  (shots are flat-cost: 4 unaimed shortbow shots = 12 st; each is a separate attack so blocks reset)")

# ------------------------------------------------------------------
P("\n=== 8. ARCHER vs APPROACHING MELEE (scripted) ===")
P("Archer: STR1 AGI1 FIN2, light armor, longbow; HP 7, stam 13, MD 3 with quick-drawn shortsword (1 w/ bow in hand), RD 1.")
P("Fighter: sample (shield, medium, HP 8, stam 14, RD 3, MD 4). Start 12 squares apart (medium range). Open field unless noted.")
def archer_scenario(cover=False, aims_first=3, n=3000, archer_kites=True):
    out = Counter(); fhp = []; ahp = []; rounds_l = []
    for _ in range(n):
        F = make_fighter(1, 'sample', 'F')
        Ar = Fighter('Ar', STR=1, AGI=1, FIN=2, level=1, armor='light', shield=False)
        Ar.weapon = Weapon('shortsword', 1, 6, flat=2)  # for melee defense/attacks; MD computed with wielding_melee
        dist = 12; rounds = 0; done = None
        # initiative
        a_first = Ar.initiative() >= F.initiative()
        turn_order = [Ar, F] if a_first else [F, Ar]
        while rounds < 15 and done is None:
            rounds += 1
            for actor in turn_order:
                if actor is Ar:
                    # kite: free move 6 to open distance if adjacent/close
                    if archer_kites and dist <= 2:
                        dist += 6
                    # shoot if can afford, with as many aims as affordable up to aims_first
                    medium = dist > 8
                    if Ar.stamina >= 5 + (1 if medium else 0):
                        aims = 0; spent = 5; acts = 0
                        while aims < aims_first and Ar.stamina - spent >= 1 + acts:
                            spent += 1 + acts; acts += 1; aims += 1
                        if medium and aims == 0:
                            pass  # auto-miss: don't shoot
                        else:
                            Ar.stamina -= spent
                            D, c = ranged_attack(8, 3, aims, 1, medium=medium)
                            RD = F.ranged_defense() + (5 if cover else 0)
                            if dist <= 1:
                                RD = F.melee_defense() + (5 if cover else 0)
                            p, g, bc, inj = best_block(D, c, RD, F.armor_value(), F.stamina, F.hp, 3)
                            F.stamina -= bc; F.take_damage(inj)
                            if F.hp <= 0: done = 'archer'; break
                    Ar.end_turn_recover()
                    # off-turn: nothing
                else:
                    # fighter: close. free 6 squares, then buy 2 squares per stamina up to need, keeping 2 for an attack
                    move = 6
                    if dist - move > 1:
                        need = dist - move - 1
                        buys = min((need + 1) // 2, max(0, F.stamina - 2))
                        F.stamina -= buys; move += 2 * buys
                    dist = max(1, dist - move)
                    if dist <= 1 and F.stamina >= 2:
                        k = max_steps(2, F.stamina)
                        k = min(k, 3)
                        cost = attack_cost(2, k); F.stamina -= cost
                        D, c = roll_damage(F.weapon, k, F.crit_bonus())
                        # archer defends with quick-drawn shortsword: MD = 1 + 1 + even FIN(2->1) = 3, armor 1
                        p, g, bc, inj = best_block(D, c, 3, 1, Ar.stamina, Ar.hp, 3)
                        Ar.stamina -= bc; Ar.take_damage(inj)
                        if Ar.hp <= 0: done = 'fighter'; break
                    F.end_turn_recover()
                    # archer off-turn retreat: 1 purchase = 2 squares for 1 st (+1 to avoid OA)
                    if archer_kites and dist <= 1 and Ar.stamina >= 2:
                        Ar.stamina -= 2; dist += 2
        out[done or 'draw'] += 1; fhp.append(F.hp); ahp.append(Ar.hp); rounds_l.append(rounds)
    P(f"  cover={cover} aims={aims_first} kite={archer_kites}: {dict(out)} | rounds mean {mean(rounds_l):.1f} | fighter HP left mean {mean(fhp):.1f} (of 8) | archer HP left {mean(ahp):.1f} (of 7)")
archer_scenario(cover=False, aims_first=3)
archer_scenario(cover=False, aims_first=2)
archer_scenario(cover=False, aims_first=0)
archer_scenario(cover=True, aims_first=3)
archer_scenario(cover=False, aims_first=3, archer_kites=False)
P("  (Assumptions: aim dice can crit; archer always fires max aims; fighter keeps 2 st for one step; no OAs beyond 1-st avoidance; archer switches to shortsword for defense.)")

# ------------------------------------------------------------------
P("\n=== 9. ARMORED vs UNARMORED ===")
for lv, va, vb in ((1, 'heavy', 'duelist'), (1, 'sample', 'duelist'), (1, 'sample', 'twohand'), (1, 'sample', 'greatsword'), (30, 'heavy', 'duelist'), (30, 'sample', 'duelist')):
    fa = make_fighter(lv, va, 'Arm'); fb = make_fighter(lv, vb, 'Duel')
    P(describe(fa)); P(describe(fb))
    run_duels(lambda: make_fighter(lv, va, 'Arm'), lambda: make_fighter(lv, vb, 'Duel'), pol_chipkill, pol_chipkill, label=f'  L{lv} {va} vs {vb} (chipkill both)')
    run_duels(lambda: make_fighter(lv, va, 'Arm'), lambda: make_fighter(lv, vb, 'Duel'), pol_alpha, pol_alpha, label=f'  L{lv} {va} vs {vb} (alpha both)')
    run_duels(lambda: make_fighter(lv, va, 'Arm'), lambda: make_fighter(lv, vb, 'Duel'), pol_fixed(2), pol_fixed(2), label=f'  L{lv} {va} vs {vb} (k2 both)')

# ------------------------------------------------------------------
P("\n=== 10. WEAPON EFFICIENCY (damage per stamina by commitment; STR2 FIN1 AGI1) ===")
weps = {'dagger(1d4+1)': (1, 2.5 + 1), 'shortsword(1d6+1)': (1, 3.5 + 1), 'longsword1H(1d8+3)': (2, 4.5 + 3),
        'longsword2H(1d10+3)': (2, 5.5 + 3), 'spear(1d8+3)': (2, 7.5), 'greatsword(1d12+5)': (3, 6.5 + 5), 'greataxe(2d6+6)': (3, 7 + 6)}
P(f"{'weapon':22s}" + "".join(f"{'k'+str(k):>14}" for k in range(1, 6)))
for nme, (base, avg) in weps.items():
    row = f"{nme:22s}"
    for k in range(1, 6):
        c = attack_cost(base, k); row += f"{avg*k:6.1f}/{c:2d}={avg*k/c:4.2f}"
    P(row)
P("STR3 (level ~30): greatsword 1d12+7=13.5, greataxe 2d6+9=16; longsword1H 1d8+4=8.5")

# ------------------------------------------------------------------
P("\n=== 11. SENSITIVITY: HP valuation w for the block policy (alpha vs alpha, k2 vs k2 at L1) ===")
for w in (1.5, 3, 6):
    run_duels(L1('A'), L1('B'), pol_fixed(2), pol_fixed(2), n=800, w=w, label=f'  w={w} k2 vs k2')
    run_duels(L1('A'), L1('B'), pol_chipkill, pol_chipkill, n=800, w=w, label=f'  w={w} chipkill vs chipkill')

with open('results.txt', 'w') as f:
    f.write("\n".join(OUT))
