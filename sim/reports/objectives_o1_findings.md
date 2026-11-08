# Objectives O1: first results

*2026-11-08. Code: branch `objectives/o1` at commit b922ef7 (the suite) and later commits that change only docs and docstrings. RuleSet `v0.9`, digest `3bf6fc070dbf` unless a row says otherwise. Full tables: [objectives_o1_suite.md](objectives_o1_suite.md) (`se suite objectives --trials 500 --workers 8`). 500 trials per row; 95% intervals (Wilson for rates, normal for means and paired differences). Rows of one scenario share seeds.*

**Flagged for the designer.** Two results look like rules behaving differently from what the packet intends; neither is fixed here.

## Setup

| Scenario | Objective (pursuers: party / defender) | Readings stated in the file |
|---|---|---|
| `extraction_3v3` | Escape: 2 of 3 off the map through the right-hand exits by round 10 | count 2, deadline 10 |
| `breakthrough_3v3` | Reach: 2 of 3 into the back row, through a wall with two gaps that 3 NPCs start behind, by round 8 | count 2, deadline 8 |
| `hold_hill_3v3` | Hold the 3×3 hill uncontested for 2 rounds running, by round 10 | `uncontested`, `consecutive`, 2 rounds |
| `hold_hill_final_3v3` | Hold the hill uncontested at the end of round 6 | `uncontested`, `final`, deadline 6 |
| `hold_the_door_1v3` | The lone defender still in the corridor at the end of round 4 | `present`, `final`, deadline 4 |

**Sides and agents.** The party (sample fighter, duelist, archer; tactical chip-kill) faces NPCs (two sample fighters and an archer; `disciplined_2step` profile). The "scripted" family replaces everyone with `fixed:2` scripted agents.

**Modes.** Pursuers play `kill` (ignore the objective; the control) or `first`; deniers always play the objective. The O1 readings not in the packet are the Assumptions-register rows marked (O1) in `sim/docs/ENGINE_PLAN.md`: zone control and hold scoring are stated per scenario; only active creatures count in a zone.

## Results (tactical family; objective done)

| Scenario | Pursuers kill | Pursuers first | First − kill (paired) | Fights ending side-out, first | Mean rounds, first |
|---|---|---|---|---|---|
| Extraction | 0.0% [0.0, 0.8] | 35.4% [31.3, 39.7] | +0.354 [0.312, 0.396] | 0.0% | 1.15 [1.12, 1.18] |
| Breakthrough | 0.6% [0.2, 1.7] | 78.2% [74.4, 81.6] | +0.776 [0.739, 0.813] | 0.0% | 1.06 [1.04, 1.09] |
| Hill, 2 rounds running | 0.0% [0.0, 0.8] | 12.6% [10.0, 15.8] | +0.126 [0.097, 0.155] | 85.4% | 3.19 [3.04, 3.33] |
| Hill, at round 6 | 0.0% [0.0, 0.8] | 3.8% [2.4, 5.9] | +0.038 [0.021, 0.055] | 91.4% | 3.26 [3.15, 3.38] |
| Hold the door | 23.2% [19.7, 27.1] | 39.2% [35.0, 43.5] | +0.160 [0.128, 0.192] | 60.8% | 3.05 [2.95, 3.15] |

In the scripted family, pursuing the objective changes almost nothing. The gains are +0.004 to +0.074, and hold the door is 0% either way. Scripted pursuers move with free movement only and never buy squares, so this gap between families comes from the agents, not the rules.

## Finding 1: movement objectives are decided by round-1 sprints

Escape and reach end in round 1 in most fights (mean 1.06–1.15 rounds), before the deniers can act. In one traced extraction (trial 0), the fighter bought 10 extra squares for 5 stamina and crossed 16 squares to an exit on its first turn. This is Review F10 ("extra on-turn movement is too cheap to be plausible and makes range irrelevant") showing up as an objective result.

F10's two options, same seeds, tactical family:

| Scenario, pursuers first | v0.9 (`3bf6fc070dbf`) | F10 opt 1, extra purchase = 1 square (`ef5c0f656642`) | F10 opt 2, bought squares ≤ Movement (`f7fd70927981`) |
|---|---|---|---|
| Extraction, done | 35.4% [31.3, 39.7] | 1.6% [0.8, 3.1] | 1.8% [0.9, 3.4] |
| Breakthrough, done | 78.2% [74.4, 81.6] | 77.0% [73.1, 80.5] | 78.8% [75.0, 82.2] |
| Hill (2 running), done | 12.6% [10.0, 15.8] | 13.8% [11.1, 17.1] | 12.6% [10.0, 15.8] |

**Extraction is purely an F10 effect.** Under either F10 option an escape against flankers almost never succeeds. That fits the review's Addendum 2: "retreat only pays to break contact entirely".

**Breakthrough is not an F10 effect.** The zone is within one turn's reach even without purchases. What lets the attackers through is avoidance at the gaps, which is Review F9's "avoidance dominates the cap". Per fight they provoked 3.26 [3.07, 3.46] opportunity attacks and paid off 2.93 [2.74, 3.12] of them, for about 2.5 stamina; 0.08 opportunity attacks were actually taken. F9's options barely help:

| Breakthrough, pursuers first | Done | OAs taken per fight |
|---|---|---|
| v0.9 | 78.2% [74.4, 81.6] | 0.07 [0.05, 0.10] |
| F9 opt 2, avoidance priced at the attacker's cap (`116766774e3f`) | 73.8% [69.8, 77.5] | 0.25 [0.20, 0.30] |
| F9 opt 3, avoidance on the off-turn track (`9f7c2e210ea8`) | 67.4% [63.2, 71.4] | 0.11 [0.08, 0.14] |

**Agent caveat.** The deniers don't body-block the gaps; they attack the pursuer closest to the zone. A denier that stands in a gap could change this result, so it needs a blocking denier before it counts as a rules result.

## Finding 2: holds collapse into the fight

85–97% of hill fights end with one side out, under every agent and mode. In the kill-mode control, the party loses the hill fight 96% of the time, so this 3v3 is lopsided against the party on this map. That is partly scenario balance, not only rules. Playing the objective still helps (+0.13 and +0.04), but the hold rarely decides the encounter. A deadline-only hold (`final`) does worse than a streak hold: the party has to survive to round 6 with someone in the zone.

**Hold the door: one defender held a corridor against three for 4 rounds in 39% of fights (tactical).** That is up from 23% when it ignored the objective, and 0% for the scripted defender. Deaths per fight fell from 0.21 to 0.11. Holding still, rather than advancing to attack, is worth +16 points of survival here, which bears on F6: focus fire is answerable when the defender doesn't step out of the chokepoint.

## What this does not show

- Agent quality, which drives these numbers as much as the rules do:
  - the scripted family never buys movement;
  - tactical deniers never body-block;
  - nobody plays the objective with look-ahead.
- Morale, secondary objectives and graded outcomes (O2, O3).

## Questions for the designer

1. Are round-1 escapes and breakthroughs intended? Extraction suggests F10 needs one of its options; breakthrough suggests F9's options are not enough at a gap.
2. Zone control, hold scoring and who counts in a zone are the Assumptions rows marked *pending designer*.
