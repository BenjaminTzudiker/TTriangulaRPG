# Objectives O1: first results

*2026-11-08. Code: branch `objectives/o1` at commit 30af4c1. All scenarios use RuleSet `v0.9` with v0.9.1 movement (`movement.extra_squares = "one"`), digest `ef5c0f656642`. Full tables: [objectives_o1_suite.md](objectives_o1_suite.md) (`se suite objectives --trials 500 --workers 8`). 500 trials per row; 95% intervals (Wilson for rates, normal for means and paired differences). Rows of one scenario share seeds. Nothing here is flagged as a rules finding.*

## Setup

The scenarios were rebuilt using "Setting up an objective scenario that tells you something" in `sim/docs/USAGE_FOR_CHATS.md`.

**The first versions** put each goal within one turn's movement on open ground, and they ran the `v0.9` preset, whose movement purchases predate packet v0.9.1. Their results were round-1 races, and they are in this file's git history.

**These versions** follow the checklist:
- **Current movement:** 6 free squares for these Agility 1 builds, plus 1 square per stamina.
- **Goals out of one-turn reach,** with routes that pass through a denier's reach.
- **Mirrored sides:** sample fighter, duelist and archer on each side. The party is tactical chip-kill; the NPCs use the `disciplined_2step` profile.

**The straight fights are close to even.** With the objective removed and everyone fighting, 500 trials:

| Map | Party wins | Draws | Mean rounds |
|---|---|---|---|
| extraction | 39.8% [35.6, 44.2] | 1.8% [0.9, 3.4] | 4.28 |
| breakthrough | 47.2% [42.9, 51.6] | 1.2% [0.6, 2.6] | 3.83 |
| hill | 43.6% [39.3, 48.0] | 1.6% [0.8, 3.1] | 4.77 |

**Scenarios:**

| Scenario | Objective (pursuers) | What the setup does |
|---|---|---|
| `extraction_3v3` | Escape, party: 2 of 3 off the east edge by round 6 | The party starts engaged with the NPC melee, 24 squares from the exits, and must pass one gap in a low wall |
| `breakthrough_3v3` | Reach, party: 2 of 3 into the back row by round 8 | The only ways through are two one-square gaps, each with an NPC standing in it. The zone is 13 rows away, beyond one turn |
| `hold_hill_3v3` | Hold, party: uncontested, 2 rounds running, by round 10 | The hill is ringed by low walls, open on four sides |
| `hold_hill_final_3v3` | Hold, party: uncontested at the end of round 6 | Same map and sides |
| `hold_the_door_1v3` | Hold, lone defender: `present` at the end of round 4 | A one-wide corridor. The straight fight is lopsided on purpose |

## Results (tactical family)

| Scenario | Done, pursuers kill | Done, pursuers first | First − kill (paired) | How fights ended, first | Mean rounds, first |
|---|---|---|---|---|---|
| Extraction | 0.0% [0.0, 0.8] | 14.4% [11.6, 17.7] | +0.144 [0.113, 0.175] | 86% failed (2 of 3 down) | 2.08 |
| Breakthrough | 0.0% [0.0, 0.8] | 6.4% [4.6, 8.9] | +0.064 [0.043, 0.085] | 93% failed (2 of 3 down) | 1.61 |
| Hill, 2 rounds running | 1.2% [0.6, 2.6] | 21.0% [17.7, 24.8] | +0.198 [0.161, 0.235] | 78% side out | 3.50 |
| Hill, at round 6 | 1.2% [0.6, 2.6] | 7.6% [5.6, 10.3] | +0.064 [0.040, 0.088] | 89% side out | 3.72 |
| Hold the door | 23.2% [19.7, 27.1] | 39.2% [35.0, 43.5] | +0.160 [0.128, 0.192] | 61% side out | 3.05 |

In the scripted family, pursuing the objective adds at most +0.058, and hold the door is 0% either way. Scripted pursuers move with free movement only and walk into the held gaps. That gap between the families comes from the agents.

## Observations

1. **Every objective now matters, but none is easy.** The objective is never done by accident: the kill-mode control does it at most 1.2% of the time, apart from hold the door. Playing for it adds 6 to 20 points.
2. **Breaking contact is costly: escape fails mostly because pursuers are downed while running.** 86% of extraction fights end with too few of the party left to get 2 out, a mean of 2.1 rounds in. That fits the intended rule that chasers win (Ledger MV-1, Review Addendum 2). This scenario asks whether a team can escape anyway, and the answer is about 1 time in 7 for these agents.
3. **Two held one-square gaps stop a breakthrough at 6%.** Pursuers who rush the gaps are downed (93% fail, in 1.6 rounds). The scenario is at the hard end. A deadline that leaves time to fight first, or a third gap, would move it toward the middle, if the question calls for that.
4. **Holds are still decided mostly by the fight** (78–89% side out), even with an even straight fight. A streak hold (21%) is easier than a deadline-only hold (8%). The difference: in a streak hold, a party that wins the zone early can finish before it is worn down.
5. **The 1v3 door: holding still is worth +16 points.** The defender survives 4 rounds 39% of the time when it stays in the corridor, against 23% when it advances to attack. Deaths per fight halve, from 0.21 to 0.11. The movement change makes no difference here; the numbers match the `v0.9` run exactly.

## Agent limits that bound these results

- Scripted agents never buy movement.
- Deniers attack the pursuer nearest its goal but don't hold a gap on purpose. In the breakthrough they start in the gaps, and they leave them when they attack.
- Pursuers buy up to half their stamina for movement and have no look-ahead.

A stronger denier or pursuer could move any of these numbers.

## Not shown here

These wait for O2 and O3:
- morale;
- secondary objectives;
- graded outcomes.

Zone control, hold scoring and who counts in a zone are still Assumptions rows marked *pending designer*.
