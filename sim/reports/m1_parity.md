# M1 parity report

Every configuration behind the review's published fight tables, run in lockstep: the
review's simulator (`sim/tests/oracle/sim.py`) and the engine under `review-sim` play
each fight on the same seed. **The gate is that every pair of fights is identical.** The
figures below are the engine's (identical to the oracle's), at the review's trial counts
× 1, beside the review's printed figures. ✓: consistent; ✗: outside the
engine's interval allowing for the review's own sampling and rounding, to investigate;
·: the review gives a range or text (or names no policy), so read by eye.

**Fights: 143200. Mismatches with the oracle: 0.**

```text
RuleSet review-sim 717025450169
Code git m0-13-g4d804e9 (4d804e9e6ad9, clean); source 524dfe53f88a; stamina-engine 0.0.1
```

## Table 2: level-1 strategy matrix

A win % / draw % / mean rounds, engine (review). 600 fights per cell.

| A \ B | alpha | k3 | k2 | k1 | reserve5 | chip-kill |
|---|---|---|---|---|---|---|
| alpha | 53/1/6.4 (49/1/6.3) ✓✓✓ | 45/2/6.9 (47/1/6.9) ✓✓✓ | 51/1/7.1 (54/2/7.5) ✓✓✓ | 76/24/14.0 (77/23/13.6) ✓✓✓ | 76/3/9.2 (77/3/8.6) ✓✓✓ | 50/1/6.4 (52/2/6.6) ✓✓✓ |
| k3 | 54/2/7.2 (53/2/6.8) ✓✓✓ | 49/1/6.8 (50/2/7.4) ✓✓✓ | 61/2/7.4 (54/3/8.3) ✗✓✗ | 82/18/12.0 (74/26/13.4) ✗✗✗ | 82/2/8.5 (79/2/8.5) ✓✓✓ | 51/2/7.3 (55/2/6.8) ✓✓✓ |
| k2 | 46/1/7.4 (45/2/7.1) ✓✓✓ | 43/2/7.5 (42/1/7.9) ✓✓✓ | 51/3/8.4 (51/2/9.2) ✓✓✓ | 77/23/13.5 (74/26/14.7) ✓✓✓ | 74/4/10.4 (73/4/10.6) ✓✓✓ | 47/2/7.5 (50/2/7.4) ✓✓✓ |
| k1 | 0/25/12.9 (0/20/12.6) ✓✓✓ | 0/20/12.2 (0/21/12.1) ✓✓✓ | 0/25/13.9 (0/24/13.7) ✓✓✓ | 0/100/30.0 (0/100/30) ✓✓✓ | 0/47/21.4 (0/51/21.9) ✓✓✓ | 0/26/13.9 (0/25/13.2) ✓✓✓ |
| reserve5 | 25/3/8.8 (22/2/8.3) ✓✓✓ | 22/2/9.1 (18/4/9.2) ✓✓✓ | 24/3/10.2 (22/4/10.6) ✓✓✓ | 53/47/21.4 (54/46/21) ✓✓✓ | 48/4/11.9 (50/4/11.3) ✓✓✓ | 23/4/9.9 (22/3/9.1) ✓✓✓ |
| chip-kill | 52/2/6.7 (50/1/6.8) ✓✓✓ | 45/2/7.2 (48/2/7.3) ✓✓✓ | 51/2/7.8 (50/2/7.5) ✓✓✓ | 76/24/13.7 (78/22/13.2) ✓✓✓ | 77/2/8.6 (76/4/9.2) ✓✓✓ | 53/0/5.7 (55/2/6.4) ✓✗✓ |

## Table 3

| Configuration | Metric | Engine (95% CI) | Review | |
|---|---|---|---|---|
| L1 alpha v alpha | rounds median | 3 | 4 | · |
| L1 alpha v alpha | rounds mean | 6.237 [5.939, 6.536] | 6.5 | ✓ |
| L1 alpha v alpha | first mover % | 71.1% [69.0, 73.0] | 69 | ✓ |
| L1 alpha v alpha | loser HP | -3.417 [-3.557, -3.276] | -3 | ✓ |
| L1 k2 v k2 | rounds median | 5 | 6 | · |
| L1 k2 v k2 | rounds mean | 8.589 [8.278, 8.901] | 8.7 | ✓ |
| L1 k2 v k2 | first mover % | 64.0% [61.8, 66.1] | 65 | ✓ |
| L1 k2 v k2 | loser HP | -3.887 [-4.058, -3.716] | -4 | ✓ |
| L1 k2 v k2 | winner untouched % | 84.9% [83.3, 86.4] | 85 | ✓ |
| L1 chip-kill v chip-kill | rounds median | 4 | 4 | · |
| L1 chip-kill v chip-kill | rounds mean | 6.359 [6.060, 6.659] | 6.3 | ✓ |
| L1 chip-kill v chip-kill | first mover % | 71.2% [69.2, 73.2] | 69–72 | ✓ |
| L1 chip-kill v chip-kill | loser HP | -3.473 [-3.616, -3.330] | -3 | ✓ |
| L1 chip-kill v chip-kill | winner untouched % | 64.3% [62.1, 66.4] | 63 | ✓ |
| L30 alpha v alpha | draws % | 7.1% [6.1, 8.4] | 6 | ✓ |
| L30 alpha v alpha | rounds median | 9 | 9 | · |
| L30 alpha v alpha | rounds mean | 11.492 [11.098, 11.886] | 11.5 | ✓ |
| L30 alpha v alpha | first mover % | 65.6% [63.4, 67.7] | 64 | ✓ |
| L30 alpha v alpha | loser HP | -2.430 [-2.521, -2.340] | -3 | ✓ |
| L30 alpha v alpha | winner untouched % | 53.6% [51.3, 55.8] | 59 | ✗ |
| L30 k2 v k2 | draws % | 77.4% [75.5, 79.2] | 75–77 | ✓ |
| L30 k2 v k2 | rounds median | 30 | 30 | · |
| L30 k2 v k2 | rounds mean | 28.177 [27.982, 28.373] | 28 | ✓ |
| L30 k2 v k2 | first mover % | 56.0% [51.4, 60.5] | 55 | ✓ |
| L30 STR-brute (MD 4) v sample (MD 6) | B wins % | 66.5% [64.4, 68.5] | 67 | ✓ |
| L30 STR-brute (MD 4) v sample (MD 6) | rounds median | 2 | 2 | · |
| L30 STR-brute (MD 4) v sample (MD 6) | rounds mean | 3.452 [3.301, 3.603] | 3.4 | ✓ |
| L30 STR-brute (MD 4) v sample (MD 6) | first mover % | 78.3% [76.4, 80.0] | 77 | ✓ |
| L99 alpha v alpha | rounds median | 1 | 1 | · |
| L99 alpha v alpha | rounds mean | 1.489 [1.440, 1.538] | 1.6 | ✓ |
| L99 alpha v alpha | first mover % | 85.7% [84.1, 87.2] | 83 | ✗ |

## Table 4

| Configuration | Metric | Engine (95% CI) | Review | |
|---|---|---|---|---|
| sample, 2-step attackers | defender down % | 100.0% [99.6, 100.0] | 100 | ✓ |
| sample, 2-step attackers | rounds to down mean | 1.524 [1.493, 1.555] | 1.5 | ✓ |
| sample, 2-step attackers | rounds to down median | 2 | 1 | · |
| sample, 2-step attackers | attackers downed per fight | 0.002 [-0.001, 0.005] | 0–0.01 | ✓ |
| sample, 1-step attackers | defender down % | 99.9% [99.4, 100.0] | 100 | ✓ |
| sample, 1-step attackers | rounds to down mean | 4.075 [3.981, 4.169] | 4 | ✓ |
| sample, 1-step attackers | rounds to down median | 4 | 4 | · |
| sample, 1-step attackers | attackers downed per fight | 0.012 [0.005, 0.019] | 0–0.01 | ✓ |
| sample, chip-kill attackers | defender down % | 100.0% [99.6, 100.0] | 100 | ✓ |
| sample, chip-kill attackers | rounds to down mean | 1.000 [1.000, 1.000] | 1 | ✓ |
| sample, chip-kill attackers | rounds to down median | 1 | 1 | · |
| sample, chip-kill attackers | attackers downed per fight | 0.013 [0.006, 0.020] | 0–0.01 | ✓ |
| sample never attacks, 2-step attackers | defender down % | 100.0% [99.6, 100.0] | 100 | ✓ |
| sample never attacks, 2-step attackers | rounds to down mean | 1.618 [1.585, 1.651] | 1.6 | ✓ |
| sample never attacks, 2-step attackers | rounds to down median | 2 | 2 | · |
| sample never attacks, 2-step attackers | attackers downed per fight | 0.000 [0.000, 0.000] | 0–0.01 | ✓ |
| heavy armor + shield, 2-step attackers | defender down % | 100.0% [99.6, 100.0] | 100 | ✓ |
| heavy armor + shield, 2-step attackers | rounds to down mean | 1.735 [1.706, 1.764] | 1.7 | ✓ |
| heavy armor + shield, 2-step attackers | rounds to down median | 2 | 2 | · |
| heavy armor + shield, 2-step attackers | attackers downed per fight | 0.001 [-0.001, 0.003] | 0–0.01 | ✓ |

## Table 7

| Configuration | Metric | Engine (95% CI) | Review | |
|---|---|---|---|---|
| L1 heavy+shield v duelist (alpha) | A wins % | 79.6% [77.8, 81.3] | 79 | ✓ |
| L1 heavy+shield v duelist (chipkill) | A wins % | 88.0% [86.6, 89.4] | 88 | ✓ |
| L1 heavy+shield v duelist (fixed:2) | A wins % | 88.6% [87.2, 90.0] | 87 | ✓ |
| L1 sample v duelist (alpha) | A wins % | 78.0% [76.2, 79.8] | 80 | ✓ |
| L1 sample v duelist (chipkill) | A wins % | 87.2% [85.7, 88.6] | 86 | ✓ |
| L1 sample v duelist (fixed:2) | A wins % | 85.1% [83.5, 86.6] | 85 | ✓ |
| L1 sample v same-stats two-hander (alpha) | A wins % | 74.0% [72.0, 75.9] | 73 | ✓ |
| L1 sample v same-stats two-hander (chipkill) | A wins % | 76.4% [74.5, 78.2] | 74 | ✓ |
| L1 sample v same-stats two-hander (fixed:2) | A wins % | 84.8% [83.2, 86.3] | 86 | ✓ |
| L1 sample v greatsword (alpha) | A wins % | 76.0% [74.1, 77.9] | 77 | ✓ |
| L1 sample v greatsword (chipkill) | A wins % | 76.1% [74.2, 77.9] | 78 | ✓ |
| L1 sample v greatsword (fixed:2) | A wins % | 83.6% [81.9, 85.2] | 84 | ✓ |
| L30 heavy+shield v duelist (alpha) | A wins % | 66.5% [64.4, 68.5] | 63 | ✗ |
| L30 heavy+shield v duelist (chipkill) | A wins % | 65.0% [62.8, 67.0] | 64 | ✓ |
| L30 heavy+shield v duelist (fixed:2) | A wins % | 77.1% [75.2, 78.9] | 78 | ✓ |
| L30 sample v duelist (alpha) | A wins % | 70.1% [68.1, 72.1] | 70 | ✓ |
| L30 sample v duelist (chipkill) | A wins % | 68.0% [65.9, 70.0] | 70 | ✓ |
| L30 sample v duelist (fixed:2) | A wins % | 82.8% [81.1, 84.4] | 82 | ✓ |

## Table 9

Duel rows of each variant. The review prints one figure per variant without naming the policy; read by eye.

| Configuration | Fights | Rounds median / mean | First mover % | Draws % | Review |
|---|---|---|---|---|---|
| Baseline v0.9: L1_ alpha v alpha | 1500 | 4 / 6.7 | 71 | 2 | L1 duel 69% first mover / 1% draws; L30 draws 6% (alpha), 75% (k2) |
| Baseline v0.9: L1_ fixed:2 v fixed:2 | 1500 | 6 / 8.5 | 65 | 2 | L1 duel 69% first mover / 1% draws; L30 draws 6% (alpha), 75% (k2) |
| Baseline v0.9: L1_ alpha v fixed:2 | 1500 | 5 / 7.1 | 65 | 2 | L1 duel 69% first mover / 1% draws; L30 draws 6% (alpha), 75% (k2) |
| Baseline v0.9: L1_ alpha v reserve:5 | 1500 | 7 / 9.3 | 68 | 4 | L1 duel 69% first mover / 1% draws; L30 draws 6% (alpha), 75% (k2) |
| Baseline v0.9: L1_ chipkill v chipkill | 800 | 3 / 6.2 | 73 | 2 | L1 duel 69% first mover / 1% draws; L30 draws 6% (alpha), 75% (k2) |
| Baseline v0.9: L30 alpha v alpha | 1500 | 9 / 11.6 | 68 | 7 | L1 duel 69% first mover / 1% draws; L30 draws 6% (alpha), 75% (k2) |
| Baseline v0.9: L30 fixed:2 v fixed:2 | 1500 | 30 / 28.0 | 54 | 78 | L1 duel 69% first mover / 1% draws; L30 draws 6% (alpha), 75% (k2) |
| Baseline v0.9: L30 chipkill v chipkill | 800 | 10 / 12.5 | 69 | 10 | L1 duel 69% first mover / 1% draws; L30 draws 6% (alpha), 75% (k2) |
| A: surcharge +2: L1_ alpha v alpha | 1500 | 12 / 14.1 | 61 | 17 | L1 61% / 17%, 13 rounds; L30 draws 68–86% |
| A: surcharge +2: L1_ fixed:2 v fixed:2 | 1500 | 13 / 14.7 | 61 | 17 | L1 61% / 17%, 13 rounds; L30 draws 68–86% |
| A: surcharge +2: L1_ alpha v fixed:2 | 1500 | 13.5 / 15.0 | 61 | 16 | L1 61% / 17%, 13 rounds; L30 draws 68–86% |
| A: surcharge +2: L1_ alpha v reserve:5 | 1500 | 14 / 16.1 | 63 | 22 | L1 61% / 17%, 13 rounds; L30 draws 68–86% |
| A: surcharge +2: L1_ chipkill v chipkill | 800 | 14 / 15.1 | 57 | 16 | L1 61% / 17%, 13 rounds; L30 draws 68–86% |
| A: surcharge +2: L30 alpha v alpha | 1500 | 30 / 26.1 | 59 | 70 | L1 61% / 17%, 13 rounds; L30 draws 68–86% |
| A: surcharge +2: L30 fixed:2 v fixed:2 | 1500 | 30 / 28.8 | 58 | 86 | L1 61% / 17%, 13 rounds; L30 draws 68–86% |
| A: surcharge +2: L30 chipkill v chipkill | 800 | 30 / 27.3 | 57 | 80 | L1 61% / 17%, 13 rounds; L30 draws 68–86% |
| B: blocks every 2nd: L1_ alpha v alpha | 1500 | 13 / 14.7 | 68 | 24 | L1 67% / 24%, 13 rounds; L30 draws 94–100% |
| B: blocks every 2nd: L1_ fixed:2 v fixed:2 | 1500 | 18 / 17.7 | 62 | 30 | L1 67% / 24%, 13 rounds; L30 draws 94–100% |
| B: blocks every 2nd: L1_ alpha v fixed:2 | 1500 | 15 / 16.3 | 63 | 28 | L1 67% / 24%, 13 rounds; L30 draws 94–100% |
| B: blocks every 2nd: L1_ alpha v reserve:5 | 1500 | 30 / 20.8 | 70 | 49 | L1 67% / 24%, 13 rounds; L30 draws 94–100% |
| B: blocks every 2nd: L1_ chipkill v chipkill | 800 | 16 / 17.1 | 62 | 27 | L1 67% / 24%, 13 rounds; L30 draws 94–100% |
| B: blocks every 2nd: L30 alpha v alpha | 1500 | 30 / 29.1 | 65 | 93 | L1 67% / 24%, 13 rounds; L30 draws 94–100% |
| B: blocks every 2nd: L30 fixed:2 v fixed:2 | 1500 | 30 / 30.0 | 0 | 100 | L1 67% / 24%, 13 rounds; L30 draws 94–100% |
| B: blocks every 2nd: L30 chipkill v chipkill | 800 | 30 / 28.9 | 46 | 93 | L1 67% / 24%, 13 rounds; L30 draws 94–100% |
| A + B: L1_ alpha v alpha | 1500 | 30 / 24.5 | 52 | 65 | L1 45% / 63%; L30 draws 100% |
| A + B: L1_ fixed:2 v fixed:2 | 1500 | 30 / 24.1 | 61 | 63 | L1 45% / 63%; L30 draws 100% |
| A + B: L1_ alpha v fixed:2 | 1500 | 30 / 24.1 | 57 | 64 | L1 45% / 63%; L30 draws 100% |
| A + B: L1_ alpha v reserve:5 | 1500 | 30 / 27.7 | 62 | 84 | L1 45% / 63%; L30 draws 100% |
| A + B: L1_ chipkill v chipkill | 800 | 30 / 24.3 | 65 | 64 | L1 45% / 63%; L30 draws 100% |
| A + B: L30 alpha v alpha | 1500 | 30 / 30.0 | 0 | 100 | L1 45% / 63%; L30 draws 100% |
| A + B: L30 fixed:2 v fixed:2 | 1500 | 30 / 30.0 | nan | 100 | L1 45% / 63%; L30 draws 100% |
| A + B: L30 chipkill v chipkill | 800 | 30 / 30.0 | nan | 100 | L1 45% / 63%; L30 draws 100% |
| D: no crit doubling: L1_ alpha v alpha | 1500 | 13 / 14.3 | 52 | 8 | L1 55% / 9%, 13 rounds |
| D: no crit doubling: L1_ fixed:2 v fixed:2 | 1500 | 13 / 14.8 | 66 | 11 | L1 55% / 9%, 13 rounds |
| D: no crit doubling: L1_ alpha v fixed:2 | 1500 | 13 / 14.3 | 59 | 9 | L1 55% / 9%, 13 rounds |
| D: no crit doubling: L1_ alpha v reserve:5 | 1500 | 13 / 15.0 | 59 | 11 | L1 55% / 9%, 13 rounds |
| D: no crit doubling: L1_ chipkill v chipkill | 800 | 14 / 14.8 | 64 | 11 | L1 55% / 9%, 13 rounds |
| D: no crit doubling: L30 alpha v alpha | 1500 | 20 / 19.9 | 45 | 25 | L1 55% / 9%, 13 rounds |
| D: no crit doubling: L30 fixed:2 v fixed:2 | 1500 | 30 / 29.8 | 44 | 96 | L1 55% / 9%, 13 rounds |
| D: no crit doubling: L30 chipkill v chipkill | 800 | 29 / 23.8 | 48 | 47 | L1 55% / 9%, 13 rounds |

## Addendum

Duel columns: rounds (median), first-mover win %, draws %, for chip-kill and alpha (the review doesn't say which it printed).

| Configuration | Fights | Rounds median / mean | First mover % | Draws % | Review |
|---|---|---|---|---|---|
| v0.9 as written: l1_sample chipkill | 400 | 3 / 6.5 | 68 | 1 | printed: 3–4, 69%, 0% |
| v0.9 as written: l1_sample alpha | 400 | 4 / 6.8 | 73 | 1 | printed: 3–4, 69%, 0% |
| v0.9 as written: l30_sample chipkill | 400 | 10 / 13.0 | 67 | 13 | printed: 9–11, 67%, 10% |
| v0.9 as written: l30_sample alpha | 400 | 9 / 10.9 | 65 | 5 | printed: 9–11, 67%, 10% |
| Crit +1 per crit die: l1_sample chipkill | 400 | 7 / 7.6 | 56 | 0 | printed: 7, 59%, 0% |
| Crit +1 per crit die: l1_sample alpha | 400 | 6 / 7.2 | 58 | 0 | printed: 7, 59%, 0% |
| Crit +1 per crit die: l30_sample chipkill | 400 | 7 / 7.9 | 55 | 0 | printed: 7, 54%, 0% |
| Crit +1 per crit die: l30_sample alpha | 400 | 6 / 7.3 | 50 | 0 | printed: 7, 54%, 0% |
| Crit none: l1_sample chipkill | 400 | 12 / 14.2 | 62 | 10 | printed: 13, 59%, 12% |
| Crit none: l1_sample alpha | 400 | 13 / 14.3 | 51 | 5 | printed: 13, 59%, 12% |
| Crit none: l30_sample chipkill | 400 | 30 / 24.2 | 55 | 48 | printed: 30, 51%, 49% |
| Crit none: l30_sample alpha | 400 | 20 / 20.3 | 48 | 24 | printed: 30, 51%, 49% |
| Surcharge +2, crit x2: l1_sample chipkill | 400 | 12.5 / 14.7 | 61 | 18 | printed: 12, 64%, 18% |
| Surcharge +2, crit x2: l1_sample alpha | 400 | 11 / 13.4 | 58 | 13 | printed: 12, 64%, 18% |
| Surcharge +2, crit x2: l30_sample chipkill | 400 | 30 / 27.7 | 59 | 80 | printed: 30, 57%, 83% |
| Surcharge +2, crit x2: l30_sample alpha | 400 | 30 / 25.0 | 63 | 64 | printed: 30, 57%, 83% |
| Surcharge +2, crit +2 per crit die: l1_sample chipkill | 400 | 7 / 7.6 | 61 | 0 | printed: 7, 55–64%, 0% |
| Surcharge +2, crit +2 per crit die: l1_sample alpha | 400 | 6 / 7.4 | 57 | 0 | printed: 7, 55–64%, 0% |
| Surcharge +2, crit +2 per crit die: l30_sample chipkill | 400 | 6 / 6.9 | 56 | 0 | printed: 5–7, 54–57%, 0% (MD 6) / 4, 46% (MD 5) |
| Surcharge +2, crit +2 per crit die: l30_sample alpha | 400 | 6 / 6.3 | 52 | 0 | printed: 5–7, 54–57%, 0% (MD 6) / 4, 46% (MD 5) |
| Surcharge +2, crit +2 per crit die: parity/l30_md5 chipkill | 400 | 5 / 5.3 | 45 | 0 | printed: 5–7, 54–57%, 0% (MD 6) / 4, 46% (MD 5) |
| Surcharge +2, crit +2 per crit die: parity/l30_md5 alpha | 400 | 4 / 4.9 | 51 | 0 | printed: 5–7, 54–57%, 0% (MD 6) / 4, 46% (MD 5) |
| Surcharge +2, crit +1 per crit die: l1_sample chipkill | 400 | 12 / 12.7 | 61 | 2 | printed: 11, 54–61%, 3% |
| Surcharge +2, crit +1 per crit die: l1_sample alpha | 400 | 11 / 12.9 | 54 | 2 | printed: 11, 54–61%, 3% |
| Surcharge +2, crit +1 per crit die: l30_sample chipkill | 400 | 14 / 14.5 | 53 | 1 | printed: 11–15, 56%, 0% |
| Surcharge +2, crit +1 per crit die: l30_sample alpha | 400 | 11 / 11.6 | 53 | 0 | printed: 11–15, 56%, 0% |
| Block slope 1/2, crit x2: l1_sample chipkill | 400 | 16 / 16.9 | 62 | 28 | printed: 15–17, 64–70%, 27% |
| Block slope 1/2, crit x2: l1_sample alpha | 400 | 14 / 15.1 | 72 | 25 | printed: 15–17, 64–70%, 27% |
| Block slope 1/2, crit x2: l30_sample chipkill | 400 | 30 / 28.9 | 62 | 94 | printed: 30, 65%, 96% |
| Block slope 1/2, crit x2: l30_sample alpha | 400 | 30 / 29.1 | 52 | 94 | printed: 30, 65%, 96% |
| Block slope 1/2, crit +2 per crit die: l1_sample chipkill | 400 | 7 / 7.8 | 65 | 0 | printed: 6–7, 63–68%, 0% |
| Block slope 1/2, crit +2 per crit die: l1_sample alpha | 400 | 6 / 6.9 | 72 | 0 | printed: 6–7, 63–68%, 0% |
| Block slope 1/2, crit +2 per crit die: l30_sample chipkill | 400 | 7 / 7.1 | 55 | 0 | printed: 5–7, 60%, 0% |
| Block slope 1/2, crit +2 per crit die: l30_sample alpha | 400 | 6 / 6.4 | 64 | 0 | printed: 5–7, 60%, 0% |

Strike columns, computed exactly (the review sampled 4,000):

| Configuration | Build | Engine (exact) | Review |
|---|---|---|---|
| v0.9 as written | l1_sample | 6.13 HP, 34.9% | 6.1 HP, 35% ✓ |
| v0.9 as written | l30_sample | 5.28 HP, 8.5% | 5.2 HP, 8% ✓ |
| Crit +1 per crit die | l1_sample | 4.79 HP, 17.2% | 4.7 HP, 16% ✓ |
| Crit +1 per crit die | l30_sample | 5.56 HP, 1.6% | 5.6 HP, 2% ✓ |
| Crit none | l1_sample | 3.82 HP, 0.9% | 3.8 HP, 1% ✓ |
| Crit none | l30_sample | 4.46 HP, 0.0% | 4.5 HP, 0% ✓ |
| Surcharge +2, crit x2 | l1_sample | 2.28 HP, 6.2% | 2.3 HP, 6% ✓ |
| Surcharge +2, crit x2 | l30_sample | 2.20 HP, 0.0% | 2.2 HP, 0% ✓ |
| Surcharge +2, crit +2 per crit die | l1_sample | 3.22 HP, 6.2% | 3.2 HP, 6% ✓ |
| Surcharge +2, crit +2 per crit die | l30_sample | 4.60 HP, 5.0% | 4.6 HP, 5% ✓ |
| Surcharge +2, crit +1 per crit die | l1_sample | 2.54 HP, 0.2% | 2.6 HP, 0% ✓ |
| Surcharge +2, crit +1 per crit die | l30_sample | 3.68 HP, 0.0% | 3.7 HP, 0% ✓ |
| Block slope 1/2, crit x2 | l1_sample | 2.85 HP, 17.7% | 2.8 HP, 17% ✓ |
| Block slope 1/2, crit x2 | l30_sample | 0.91 HP, 0.0% | 0.9 HP, 0% ✓ |
| Block slope 1/2, crit +2 per crit die | l1_sample | 3.43 HP, 17.2% | 3.4 HP, 18% ✓ |
| Block slope 1/2, crit +2 per crit die | l30_sample | 4.03 HP, 4.7% | 4 HP, 4% ✓ |

## Flagged for investigation

- Table 2 k3 v k2: 61/2/7.4 (54/3/8.3) ✗✓✗
- Table 2 k3 v k1: 82/18/12.0 (74/26/13.4) ✗✗✗
- Table 2 chip-kill v chip-kill: 53/0/5.7 (55/2/6.4) ✓✗✓
- Table 3 L30 alpha v alpha, winner untouched %: engine 53.6% [51.3, 55.8], review 59
- Table 3 L99 alpha v alpha, first mover %: engine 85.7% [84.1, 87.2], review 83
- Table 7 L30 heavy+shield v duelist (alpha), A wins %: engine 66.5% [64.4, 68.5], review 63
