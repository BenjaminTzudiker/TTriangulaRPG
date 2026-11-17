#!/usr/bin/env python3
"""r4 scratch: X's round-1 opener on A under the wound rule, one ply deep.

X attacks A with K steps (A blocks as the solver), then sets a hold h on A after seeing A's
state. A answers with its best of: pay 1 + h; counter X with 2 or 1 steps (X blocks to keep its
hold when it can; if the hold breaks, A leaves paying 1 or eating X's 1-step OA); leave unpaid
and eat X's biggest OA (budget 2 + h, tokens first); or stay (pinned).
Outcome guesses (not computed): pinned A dies P_PIN; an A that got away dies p_late(...).
Prints P(A down) for each K with X's best h per A state.

python3 opener.py K [P_PIN]
"""
import sys

import calc as C

P_PIN = float(sys.argv[2]) if len(sys.argv) > 2 else 0.9


def p_late(hp, ready_end):
    """Guess: chance an A that broke contact in round 1 is still caught later."""
    return 0.05 + (0.10 if hp <= 3 else 0) + (0.03 if ready_end < 6 else 0)


def oa_steps(h, rx):
    """Most steps X's OA can make: cost 2,3,4.. total <= 2 + h, and total - h <= rx."""
    k, tot = 0, 0
    while True:
        nxt = tot + 2 + k
        if nxt > 2 + h or nxt - h > rx:
            return k
        k, tot = k + 1, nxt


def leave_after_break(hp, r, rx_after):
    """A leaves X after the hold broke: X can OA 1 step (2 from ready) if rx_after >= 2."""
    if rx_after < 2:
        return p_late(hp, r + 4)
    if r >= 1:
        return p_late(hp, r - 1 + 4)  # pay 1
    out = 0.0
    for (h2, s2), p in C.after(1, hp, r).items():
        out += float(p) * (1.0 if h2 <= 0 else p_late(h2, s2 + 4))
    return out


def a_best(hp, r, h, rx):
    opts = {}
    opts["stay"] = P_PIN
    if r >= 1 + h:
        opts["pay"] = p_late(hp, r - 1 - h + 4)
    for k, cost in ((2, 5), (1, 2)):
        if r < cost:
            continue
        v = 0.0
        for (xh, xs, kept), p in C.keep_after(k, 10, rx, h).items():
            p = float(p)
            if xh <= 0:
                v += p * p_late(hp, r - cost + 4)
            elif kept:
                v += p * P_PIN
            else:
                v += p * leave_after_break(hp, r - cost, xs)
        opts[f"counter{k}"] = v
    k = oa_steps(h, rx)
    if k:
        v = 0.0
        for (h2, s2), p in C.after(k, hp, r).items():
            v += float(p) * (1.0 if h2 <= 0 else p_late(h2, s2 + 4))
        opts[f"oa{k}"] = v
    best = min(opts, key=opts.get)
    return opts[best], best, opts


def main():
    K = int(sys.argv[1])
    cost = sum(2 + i for i in range(K))
    xr = 16 - cost
    total = 0.0
    rows = []
    for (hp, r), p in sorted(C.after(K, 10, 16).items(), key=lambda kv: (-kv[0][0], -kv[0][1])):
        p = float(p)
        if hp <= 0:
            total += p
            continue
        best = None
        for h in range(0, xr + 1):
            rx = min(16 - h, xr - h + 4)
            v, choice, _ = a_best(hp, r, h, rx)
            if best is None or v > best[0] + 1e-9:
                best = (v, h, choice)
        total += p * best[0]
        rows.append((hp, r, p, best))
    print(f"X {K} steps (X keeps {xr}); P_PIN {P_PIN}: P(A down) ~ {total:.3f}")
    for hp, r, p, (v, h, choice) in rows:
        if p > 0.01:
            print(f"  A hp {hp:>2} ready {r:>2} ({p:5.1%}): X holds {h} -> A {choice:<8} "
                  f"A down {v:.2f}")


if __name__ == "__main__":
    main()
