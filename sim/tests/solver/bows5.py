"""bows5: bows4 + max_shots (per shooter per round) and cap_floor (wound cap = max(dice + cap_mod, cap_floor)). bows4: bows3 + per-bow pierce and a per-shot crit cap. Designer's placeholder bow proposal (2026-11-10), exact solver. Not rules.

Per shot: total = bow die + mod + aim dice (1d6 each) - range penalty (floored at 0; 0 cancels crits).
Blocks at defense D (perfect 1,2,3..., graze 1 leaking 1), armor soaks, then the wound is capped:
HP lost <= bow die face + mod (aim never adds to the wound). A crit (bow die shows its max face;
aim dice never crit -- our assumption, the proposal doesn't say) ignores 1 armor and adds +1 if
anything gets through. Draw cost per bow; aim steps 1 + surcharge; `draw_action` decides whether a
draw is itself an action on the surcharge (the proposal doesn't say).

Several shooters may act in a row (each with its own surcharge) before the target's turn. The target
may dive after a shot is rolled (off-turn price 1, 2, 3... across ALL shooters this round, per the
off-turn escalation rule): +2 D for that shot and it stays in cover (+2) for the rest of the round
('static' shooters) or shooters re-angle so each shot needs a new dive ('flank').
Zero-sum on U = 100*[down] + 3*HP + target stamina spent (shooters maximise). One round.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from functools import lru_cache

DOWN, W = 100, 3


@dataclass(frozen=True)
class Bow:
    name: str; die: int; mod: int; draw: int; band: int
    cap_mod: int | None = None   # wound cap = die + cap_mod (default: mod)
    crit_mode: str = "bow_max"   # bow_max (bow die max face only) | bow_w (bow die only, Finesse-widened) | all (bow + aim dice, widen applies to both) | aim_only (aim dice only, widened)
    widen: int = 0               # crit-range widening from Finesse
    free_aims: int = 0           # aim dice included in every shot (no aim cost, no escalation)
    per_band: int = 1            # penalty per band beyond the first
    aim_reset: bool = False      # aim escalation resets each shot (draws still escalate)
    aim_base: int = 1
    nd: int = 1                  # number of bow damage dice (each max face is a crit die)
    crit_ap: bool = True         # crits ignore 1 armor each (False: shortbow ability, crits only add +1)
    pierce: int = 0              # flat armor ignored (Hammer-style property)
    aim_widen: int | None = None # widening on aim dice (None: same as widen)
    crit_in_cap: bool = False    # True: the crit bonus counts toward the wound cap
    max_shots: int = 99
    cap_floor: int = 0
    crit_cap: int = 99           # max crit dice counted per shot (1 = one arrow, one vital spot)
    stamina: int = 14
    draw_action: bool = True
    max_aims: int = 6


@dataclass(frozen=True)
class Tgt:
    D: int; armor: int = 0; hp: int = 8; st: int = 14; sbase: int = 6
    can_dive: bool = False; dive_bonus: int = 2; flank: bool = False


def shot_dist(b: Bow, aims: int, pen: int):
    joint = {(0, 0, 0): 1.0}
    bw = b.widen if b.crit_mode in ("all", "bow_w") else 0
    for _ in range(b.nd):
        nxt = defaultdict(float)
        for (t, c, cap), p in joint.items():
            for f in range(1, b.die + 1):
                bc = int(b.crit_mode in ("bow_max", "all", "bow_w") and f >= b.die - bw)
                nxt[(t + f, c + bc, cap + f)] += p / b.die
        joint = nxt
    joint = {(t + b.mod, c, max(b.cap_floor, cap + (b.mod if b.cap_mod is None else b.cap_mod))): p for (t, c, cap), p in joint.items()}
    aw = b.widen if b.aim_widen is None else b.aim_widen
    for _ in range(aims + b.free_aims):
        nxt = defaultdict(float)
        for (t, c, cap), p in joint.items():
            for f in range(1, 7):
                ac = int(b.crit_mode in ("all", "aim_only") and f >= 6 - aw)
                nxt[(t + f, c + ac, cap)] += p / 6
        joint = nxt
    out = defaultdict(float)
    for (t, c, cap), p in joint.items():
        c = min(c, b.crit_cap)
        t2 = max(0, t - pen)
        out[(t2, c if t2 > 0 else 0, cap)] += p
    return tuple((p, t, c, cap) for (t, c, cap), p in out.items())


INCAP = [False]

def injury(total, crits, d, armor, p, g, cap, ap=True):
    through = max(0, total - (p + g) * d)
    after = min(cap, max(0, through + g - max(0, armor - (crits if ap else 0))))
    if INCAP[0]:
        return min(cap, after + crits) if after > 0 else 0
    return after + crits if after > 0 else 0


AP = [True]

def solve(bows: tuple, t: Tgt, distance: int = 0):
    AP[0] = bows[0].crit_ap
    INCAP[0] = bows[0].crit_in_cap
    front_cache_key = AP[0]
    pens = [max(0, distance // b.band - (1 if distance >= b.band else 0)) if distance else 0 for b in bows]
    # bands: squares 0..band-1 are band 1 (no penalty); each further band -1
    pens = [b.per_band * max(0, (distance - 1) // b.band) if distance > 0 else 0 for b in bows]

    @lru_cache(maxsize=None)
    def front(total, crits, sd, D, cap, arm, ap):
        opts, p = [], 0
        while p * (p + 1) // 2 <= sd:
            pc, g = p * (p + 1) // 2, 0
            while pc + g <= sd:
                inj = injury(total, crits, D, arm, p, g, cap, ap)
                opts.append((pc + g, inj))
                if inj == 0 and (p + g) * D >= total:
                    break
                g += 1
            p += 1
        f = []
        for c, i in sorted(set(opts)):
            if not f or i < f[-1][1]:
                f.append((c, i))
        return tuple(f)

    dists = {}

    def dist(si, aims):
        k = (si, aims)
        if k not in dists:
            dists[k] = shot_dist(bows[si], aims, pens[si])
        return dists[k]

    ZERO = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)  # U, Pdown, HP, St, shots, aims

    @lru_cache(maxsize=None)
    def V(si, sa, k, sd, h, dives, incover, n=0):
        if si >= len(bows):
            return ZERO
        best = V(si + 1, bows[si + 1].stamina if si + 1 < len(bows) else 0, 0, sd, h, dives, incover)
        b = bows[si]
        for aims in (range(b.max_aims + 1) if n < b.max_shots else ()):
            kk, cost = k, b.draw + (k if b.draw_action else 0)
            if b.draw_action:
                kk += 1
            for j in range(aims):
                if b.aim_reset:
                    cost += b.aim_base + j
                else:
                    cost += b.aim_base + kk; kk += 1
            if cost > sa:
                break
            acc = [0.0] * 6
            for p, total, crits, cap in dist(si, aims):
                bv = None
                base_D = t.D + (t.dive_bonus if incover else 0)
                choices = [(base_D, 0, dives, incover)]
                if t.can_dive and not incover and 1 + dives <= sd:
                    choices.append((t.D + t.dive_bonus, 1 + dives, dives + 1, not t.flank))
                for D, dc, dv2, ic2 in choices:
                    for c0, inj in front(total, crits, sd - dc, D, cap, max(0, t.armor - b.pierce), b.crit_ap):
                        c = c0 + dc
                        h2 = h - inj
                        if h2 <= 0:
                            val = (DOWN + W * h + c, 1.0, float(h), float(c), 1.0, float(aims))
                        else:
                            cont = V(si, sa - cost, kk, min(sd - c, t.sbase + h2), h2, dv2, ic2, n + 1)
                            val = (W * inj + c + cont[0], cont[1], inj + cont[2], c + cont[3], 1 + cont[4], aims + cont[5])
                        if bv is None or val[0] < bv[0]:
                            bv = val
                for i in range(6):
                    acc[i] += p * bv[i]
            cand = tuple(acc)
            if cand[0] > best[0]:
                best = cand
        return best

    r = V(0, bows[0].stamina, 0, t.st, t.hp, 0, False)
    return dict(U=r[0], P_down=r[1], HP=r[2], St=r[3], shots=r[4], aims=r[5])


# L1 placeholder archers (designer's numbers; attribute picks ours)
def shortbow(fin=3, band_bonus=2, **kw): return Bow("shortbow", 4, fin, 2, 2 + band_bonus, **kw)
def longbow(st_=1, band_bonus=1, **kw): return Bow("longbow", 8, st_, 4, 3 + band_bonus, **kw)
def warbow(st_=3, band_bonus=1, **kw): return Bow("warbow", 10, st_, 6, 4 + band_bonus, **kw)
