"""
Simulator for Playtest Packet v0.9 core combat rules.

Modelled rules (v0.9 text):
- HP = 6 + STR. Max stamina = 6 + current HP + round(L/5). Recovery at END of own turn = 4 + round(L/10).
- Melee attack: k steps, step i costs base + (actions already taken) -> total k*base + T(k-1).
  Each step adds one weapon damage roll (die + flat).
- Ranged: shot costs flat base; each aim step is an action costing 1 + actions so far; adds 1d6 + FIN.
- Defense: each block subtracts the defense value V. Perfect blocks cost 1,2,3,... within one attack.
  Grazing blocks cost 1 flat and leak 1 each. Armor soaks (residual + leaks). Each crit die ignores 1 armor.
  If >= 1 crit die, double what remains after armor.
- Crit: a die is critical on its max, widened by +1 per odd FIN value (max +3).
- Initiative 2d12 + odd AGI + odd CUN.
- Max stamina recomputed when HP changes; current clamped to max.

ASSUMPTIONS where the packet is TODO/silent are listed in the report (aim dice can crit; stamina is
observable; NPCs block optimally; no abilities, no strain use; no retreat - fight to incapacitation).
"""
import random
import math
import itertools
from dataclasses import dataclass, field
from statistics import mean, median
from collections import Counter

def T(n):
    return n * (n + 1) // 2

# --- tunable variants (defaults = v0.9 rules) ---
STEP_SLOPE = 1          # surcharge added per prior action
BLOCK_SLOPE = 1.0       # perfect block i costs 1 + floor((i-1)*BLOCK_SLOPE) ; 1.0 -> 1,2,3,... ; 0.5 -> 1,1,2,2,3,...
CRIT_MODE = 'double'    # 'double' (v0.9), 'linear1' (+1 per crit die after armor), 'linear2' (+2 per crit die), 'none'
def crit_effect(pre, crits):
    if crits <= 0: return pre
    if CRIT_MODE == 'double': return pre * 2
    if CRIT_MODE == 'linear1': return pre + crits
    if CRIT_MODE == 'linear2': return pre + 2 * crits
    return pre
def block_cost(p):
    """cumulative cost of p perfect blocks within one attack"""
    return sum(1 + math.floor((i - 1) * BLOCK_SLOPE + 1e-9) for i in range(1, p + 1))

def round_half_up(x):
    return math.floor(x + 0.5)

def odd_count(v):
    # number of odd values in 1..v  (1,3,5 -> up to 3)
    return 0 if v <= 0 else (v + 1) // 2

def even_count(v, armor_class=None):
    if v < 0:
        return 0
    if armor_class in (None, 'none', 'light'):
        return v // 2
    if armor_class == 'medium':
        return v // 3
    if armor_class == 'heavy':
        return v // 4
    raise ValueError

ARMOR_VALUE = {'none': 0, 'light': 1, 'medium': 2, 'heavy': 3}

@dataclass
class Weapon:
    name: str
    base: int
    die: int          # die size per step (0 for none)
    ndice: int = 1
    flat: int = 0     # flat bonus per step (computed from attributes)
    ranged: bool = False
    melee_ok: bool = True

@dataclass
class Fighter:
    name: str
    STR: int
    AGI: int
    FIN: int
    CUN: int = 0
    level: int = 1
    armor: str = 'medium'
    shield: bool = True
    weapon: Weapon = None
    # derived
    hp_max: int = 0
    hp: int = 0
    stamina: int = 0
    strain_abilities: bool = False
    # bookkeeping
    on_turn_actions: int = 0
    offturn_costs: int = 0
    wounds_taken: list = field(default_factory=list)

    def __post_init__(self):
        self.hp_max = 6 + self.STR
        self.hp = self.hp_max
        self.stamina = self.max_stamina()

    def level_stam_bonus(self):
        return round_half_up(self.level / 5)

    def recovery(self):
        return 4 + round_half_up(self.level / 10)

    def max_stamina(self):
        return 6 + max(self.hp, 0) + self.level_stam_bonus()

    def armor_value(self):
        return ARMOR_VALUE[self.armor]

    def eff_agi(self):
        return self.AGI  # STR requirements assumed met in all samples

    def melee_defense(self, wielding_melee=True):
        v = 0
        if self.eff_agi() >= 0:
            v += 1
        if wielding_melee:
            v += 1  # proficient melee weapon
            v += even_count(self.FIN)
        if self.shield:
            v += 2
        v += even_count(self.eff_agi(), self.armor)
        return v

    def ranged_defense(self):
        v = 1 if self.eff_agi() >= 0 else 0
        if self.shield:
            v += 2
        return v

    def crit_bonus(self):
        return min(3, odd_count(self.FIN))

    def take_damage(self, dmg):
        if dmg <= 0:
            return
        self.hp -= dmg
        self.wounds_taken.append(dmg)
        mx = self.max_stamina()
        if self.stamina > mx:
            self.stamina = mx

    def end_turn_recover(self):
        self.stamina = min(self.max_stamina(), self.stamina + self.recovery())

    def initiative(self):
        return random.randint(1, 12) + random.randint(1, 12) + odd_count(self.AGI) + odd_count(self.CUN)

# ---------- blocking ----------

def best_block(D, crits, V, A, S, hp, w=3.0, death_pen=1000.0):
    """Return (p, g, cost, injury) minimizing injury*w + cost over affordable (p,g).
    death_pen: extra penalty if injury >= hp (incapacitation)."""
    best = None
    eff_armor = max(0, A - crits)
    p = 0
    while block_cost(p) <= S:
        gmax = S - block_cost(p)
        # no point blocking more than needed
        n_needed = math.ceil(D / V) if V > 0 else 10**6
        for g in range(0, gmax + 1):
            n = p + g
            res = max(0, D - n * V)
            pre = max(0, res + g - eff_armor)
            inj = crit_effect(pre, crits)
            cost = block_cost(p) + g
            score = inj * w + cost + (death_pen if inj >= hp else 0.0)
            if best is None or score < best[0] - 1e-9 or (abs(score - best[0]) < 1e-9 and cost < best[3]):
                best = (score, p, g, cost, inj)
            if n >= n_needed and (pre == 0 or g > 0 and res == 0 and False):
                # once residual is zero, extra grazes only add leaks: stop increasing g
                if res == 0:
                    break
        p += 1
    _, p, g, cost, inj = best
    return p, g, cost, inj

# ---------- attacking ----------

def attack_cost(base, k, prior_actions=0):
    # steps cost base + STEP_SLOPE*(prior_actions + i), for i in 0..k-1
    return sum(base + STEP_SLOPE * (prior_actions + i) for i in range(k))

def max_steps(base, S, prior_actions=0):
    k = 0
    while attack_cost(base, k + 1, prior_actions) <= S:
        k += 1
    return k

def roll_damage(weapon, k, crit_bonus):
    total = 0
    crits = 0
    for _ in range(k):
        for _d in range(weapon.ndice):
            r = random.randint(1, weapon.die)
            total += r
            if r >= weapon.die - crit_bonus:
                crits += 1
        total += weapon.flat
    return total, crits

def expected_block_outcome(att, dfn, k, samples=60, w=3.0):
    """Expected (defender injury, defender stamina spent, P(kill)) for a k-step attack, sampling rolls."""
    inj_tot = 0; cost_tot = 0; kills = 0
    V = dfn.melee_defense()
    A = dfn.armor_value()
    for _ in range(samples):
        D, c = roll_damage(att.weapon, k, att.crit_bonus())
        p, g, cost, inj = best_block(D, c, V, A, dfn.stamina, dfn.hp, w)
        inj_tot += inj; cost_tot += cost
        if inj >= dfn.hp:
            kills += 1
    return inj_tot / samples, cost_tot / samples, kills / samples

# attacker policies: functions (att, dfn) -> k
def pol_alpha(att, dfn):
    return max_steps(att.weapon.base, att.stamina)

def pol_fixed(kfix):
    def f(att, dfn):
        return min(kfix, max_steps(att.weapon.base, att.stamina))
    return f

def pol_reserve(r):
    def f(att, dfn):
        return max_steps(att.weapon.base, max(0, att.stamina - r))
    return f

def pol_chipkill(att, dfn, w=3.0):
    """k=2 by default; go all-in if the all-in attack is expected to wound >= half HP or kill with p>=0.5."""
    kmax = max_steps(att.weapon.base, att.stamina)
    if kmax == 0:
        return 0
    inj, cost, pk = expected_block_outcome(att, dfn, kmax, samples=40, w=w)
    if pk >= 0.5 or inj >= dfn.hp / 2:
        return kmax
    return min(2, kmax)

def pol_greedy(att, dfn, w=3.0):
    """1-ply: maximize E[def injury]*w + E[def stamina spent] - own cost, minus exposure:
    the opponent's best reply against my remaining stamina (+regen)."""
    kmax = max_steps(att.weapon.base, att.stamina)
    best = (-1e9, 0)
    for k in range(0, kmax + 1):
        if k == 0:
            inj = cost = pk = 0.0
            own = 0
        else:
            inj, cost, pk = expected_block_outcome(att, dfn, k, samples=40, w=w)
            own = attack_cost(att.weapon.base, k)
        my_left = min(att.max_stamina(), att.stamina - own + att.recovery())
        # opponent reply: their max steps with their stamina (+ they may also have regen later; approximate)
        opp_k = max_steps(dfn.weapon.base, dfn.stamina - cost) if dfn.weapon and not dfn.weapon.ranged else 0
        exp_inj_me = 0.0
        if opp_k > 0:
            # evaluate the opponent's alpha and k=2 and take the worse for me
            saved = att.stamina
            att.stamina = my_left
            worst = 0.0
            for kk in set([opp_k, min(2, opp_k)]):
                i2, c2, pk2 = expected_block_outcome(dfn, att, kk, samples=30, w=w)
                worst = max(worst, i2 * w + c2 + (pk2 * 10 * w))
            att.stamina = saved
            exp_inj_me = worst
        score = inj * w + cost + pk * 10 * w - own - exp_inj_me
        if score > best[0]:
            best = (score, k)
    return best[1]

# ---------- duel ----------

def resolve_melee_attack(att, dfn, k, w=3.0, log=None):
    base = att.weapon.base
    cost = attack_cost(base, k, att.on_turn_actions)
    att.stamina -= cost
    att.on_turn_actions += k
    D, c = roll_damage(att.weapon, k, att.crit_bonus())
    V = dfn.melee_defense()
    A = dfn.armor_value()
    p, g, bcost, inj = best_block(D, c, V, A, dfn.stamina, dfn.hp, w)
    dfn.stamina -= bcost
    dfn.take_damage(inj)
    if log is not None:
        log.append(f"{att.name} {k} steps ({cost} st) rolls {D} [{c} crit] -> {dfn.name} blocks p{p}/g{g} ({bcost} st), takes {inj} HP. "
                   f"{att.name} st {att.stamina}; {dfn.name} hp {dfn.hp} st {dfn.stamina}")
    return D, c, p, g, bcost, inj

def duel(a, b, pol_a, pol_b, w=3.0, max_rounds=30, log=None):
    order = sorted([a, b], key=lambda f: f.initiative(), reverse=True)
    first = order[0]
    rounds = 0
    while rounds < max_rounds:
        rounds += 1
        for actor in order:
            target = b if actor is a else a
            if actor.hp <= 0:
                continue
            actor.on_turn_actions = 0
            pol = pol_a if actor is a else pol_b
            k = pol(actor, target)
            if k > 0:
                resolve_melee_attack(actor, target, k, w, log)
                if target.hp <= 0:
                    return (actor, rounds, first)
            actor.end_turn_recover()
    return (None, rounds, first)

def make_fighter(level=1, variant='sample', name='F'):
    if level == 1 and variant == 'sample':
        f = Fighter(name, STR=2, AGI=1, FIN=1, level=1, armor='medium', shield=True)
        f.weapon = Weapon('longsword 1H', base=2, die=8, flat=f.STR + f.FIN)
    elif level == 1 and variant == 'twohand':
        f = Fighter(name, STR=2, AGI=1, FIN=1, level=1, armor='medium', shield=False)
        f.weapon = Weapon('longsword 2H', base=2, die=10, flat=max(f.STR, f.AGI) + f.FIN)
    elif level == 1 and variant == 'greatsword':
        f = Fighter(name, STR=2, AGI=1, FIN=1, level=1, armor='medium', shield=False)
        f.weapon = Weapon('greatsword', base=3, die=12, flat=2 * f.STR + f.FIN)
    elif level == 1 and variant == 'heavy':
        # STR 2 in heavy armor: -1 AGI, -1 FIN -> AGI 0, FIN 0
        f = Fighter(name, STR=2, AGI=0, FIN=0, level=1, armor='heavy', shield=True)
        f.weapon = Weapon('longsword 1H', base=2, die=8, flat=f.STR + f.FIN)
    elif level == 1 and variant == 'duelist':
        # unarmored, no shield, AGI 2 FIN 1 STR 1 (5 EP)
        f = Fighter(name, STR=1, AGI=2, FIN=1, level=1, armor='none', shield=False)
        f.weapon = Weapon('longsword 2H', base=2, die=10, flat=max(f.STR, f.AGI) + f.FIN)
    elif level == 30 and variant == 'sample':
        # 16 EP: STR 3 (6) AGI 3 (6) FIN 2 (3) CUN 1 (1)
        f = Fighter(name, STR=3, AGI=3, FIN=2, CUN=1, level=30, armor='medium', shield=True)
        f.weapon = Weapon('longsword 1H', base=2, die=8, flat=f.STR + f.FIN)
    elif level == 30 and variant == 'strbrute':
        # STR 5 (15) FIN 1 (1): heavy armor, shield
        f = Fighter(name, STR=5, AGI=0, FIN=1, level=30, armor='heavy', shield=True)
        f.weapon = Weapon('longsword 1H', base=2, die=8, flat=f.STR + f.FIN)
    elif level == 30 and variant == 'duelist':
        # AGI 4 (10) FIN 3 (6): unarmored, two-handed longsword
        f = Fighter(name, STR=0, AGI=4, FIN=3, level=30, armor='none', shield=False)
        f.weapon = Weapon('longsword 2H', base=2, die=10, flat=max(f.STR, f.AGI) + f.FIN)
    elif level == 30 and variant == 'heavy':
        # STR 3 (6) AGI 3 (6) FIN 2 (3) +1: heavy armor (AGI every 4th -> 0)
        f = Fighter(name, STR=3, AGI=3, FIN=2, CUN=1, level=30, armor='heavy', shield=True)
        f.weapon = Weapon('longsword 1H', base=2, die=8, flat=f.STR + f.FIN)
    elif level == 99 and variant == 'sample':
        # ~44 EP: STR 6 (21) AGI 6 (21) FIN 1 (1)
        f = Fighter(name, STR=6, AGI=6, FIN=1, CUN=0, level=99, armor='medium', shield=True)
        f.weapon = Weapon('longsword 1H', base=2, die=8, flat=f.STR + f.FIN)
    else:
        raise ValueError(variant)
    return f

def describe(f):
    return (f"{f.name}: STR{f.STR} AGI{f.AGI} FIN{f.FIN} L{f.level} {f.armor}{'+shield' if f.shield else ''} | "
            f"HP {f.hp_max} | Stam {f.max_stamina()} (+{f.recovery()}/turn) | MD {f.melee_defense()} RD {f.ranged_defense()} "
            f"armor {f.armor_value()} | {f.weapon.name}: base {f.weapon.base}, {f.weapon.ndice}d{f.weapon.die}+{f.weapon.flat} "
            f"(avg {f.weapon.ndice*(f.weapon.die+1)/2 + f.weapon.flat:.1f}/step), crit on {f.weapon.die - f.crit_bonus()}+")

if __name__ == '__main__':
    random.seed(1)
    f = make_fighter(1, 'sample')
    print(describe(f))
