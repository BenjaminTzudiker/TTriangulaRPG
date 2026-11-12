# 0.10.0 ranged rules: first results

*2026-11-11. Code: commit b1164f3 on branch `engine/ranged-agents`, clean. Full tables: [ranged10_suite.md](ranged10_suite.md) (`se suite ranged10 --trials 500 --workers 8`).*

*RuleSets:*

| Preset | Digest | What changes |
|---|---|---|
| `v0.10.0` | `a89fed59543d` | The baseline |
| `v0.10.0-cover-only` | `820505340da8` | `ranged.range_measured` and `ranged.defense_timing` set to `"declaration"` |
| `v0.10.0-crit-c-prime` | `b7690db2f629` | Crit rule C′ |
| `v0.10.0-crit-c` | `6a1c7e8b7971` | Crit rule C |

*Equipment `v0_10`; S6 uses `s6_beast`. 500 trials per row, seed 20261111. 95% intervals: Wilson for rates, normal for means. Rows of one scenario share seeds.*

**Two results are flagged for the designer** (sections 1 and 2): normal-range lethality, and the choice between the two reaction packages. Nothing in the rules was changed to get them.

## Read this first

- **Agents.** The tactical family turns on every new agent behavior:
  - the reaction values contact and approach, with `approach_weight = 1`;
  - the archer aims against the target's best reaction;
  - pursuers close off-turn and buy squares only to keep their steps.

  The scripted family is the floor: archers shoot with 1 aim and stand, and pursuers buy squares only to keep their steps.
- **The tactical archer overcommits.** It often puts the whole first turn into one aimed shot: a warbow plus 3 aims is 15 of its 16 stamina. It's then left fighting with its blade on 1 stamina (trial 0 of S1, warbow against the two-hander at 12 squares, shows it).
  - That's why scripted archers beat tactical ones with heavy bows. Against the two-hander at 12 squares, with the warbow, they win 62% against 16%.
  - Treat the tactical archers' win rates as a lower bound. This is an agent flaw, not a rules result. Fixing its aim is the next engine task.
- **Builds.** Only the longbow archer (`l1_archer`) is a legal level-1 character.
  - The other bows' archers are over the Expertise budget at the attributes their bows want, as in the design study.
  - Strength also gives them HP and stamina: the warbow archer has 10 HP and 16 stamina, the superheavy 12 and 18, against the longbow archer's 8 and 14. So the bow comparisons mix bow and body.
- **Setups are first drafts.** S3 is 3 against 2 as the requirements describe it, and S6's beast has 14 HP, not 20. Treat absolute win rates as properties of these setups. The comparisons inside a group (paired, same dice) are the useful part.

## 1. Two archers at normal range down a defender fast (flagged)

S4 puts two archers 8 to 10 squares from a caster and a knight in heavy armor with a shield, near scattered cover. The longbow archers are the only legal builds here. The table shows how often either defender is down (incapacitated or dead) by the end of round 2, under crit rule A (0.10.0):

| Bow | Tactical | Scripted |
|---|---|---|
| Shortbow | 64.2% [59.9, 68.3] | 68.6% [64.4, 72.5] |
| **Longbow** | **67.8% [63.6, 71.7]** | **73.4% [69.4, 77.1]** |
| Warbow | 85.2% [81.8, 88.0] | 90.0% [87.1, 92.3] |
| Superheavy | 94.6% [92.3, 96.3] | 96.0% [93.9, 97.4] |

The caster is the one who falls: it's down at the end in 74% of longbow fights, against 28–40% for the knight.

The packet's Open Questions name this as the main risk ("two archers shooting one target back to back"), untested at normal ranges. With these agents and this map, the answer is that it happens at 8–10 squares too, not only point blank. The reactions don't prevent it: the tactical targets react to about half the shots (cover 13%, close 7%, shift 27%), at 1.4 stamina a reaction.

The crit rules barely move it. For longbows, round-2 down is 67.8% under A, 69.6% under C′ and 71.0% under C. Under C, warbow and superheavy archers win less often (warbow 55.2% under A, 40.6% under C) with the same round-2 rate. That looks like the overcommitting aim interacting with extra crits, so I wouldn't read it as a crit result.

## 2. The two reaction packages play out the same (flagged)

Pairing `v0.10.0`, where reactions are judged where the target ends, with `v0.10.0-cover-only`, judged at declaration, on the same dice:

| Scenario | 0.10.0 | Cover only |
|---|---|---|
| Open ground, sword and board, archers win | 2.8% [1.7, 4.6] | 3.0% [1.8, 4.9] |
| Open ground, two-hander | 11.6% [9.1, 14.7] | 12.0% [9.4, 15.1] |
| Low walls, sword and board | 1.2% [0.6, 2.6] | 1.4% [0.7, 2.9] |
| Low walls, two-hander | 4.4% [2.9, 6.6] | 5.4% [3.7, 7.7] |
| S3 focus fire | 93.0% [90.4, 94.9] | 95.0% [92.7, 96.6] |

(All tactical. The scripted rows are identical by construction, since scripted targets never react.)

What changes is what reactions do, not the outcome:
- Backing away disappears under cover only (25–29% of shots on open ground under 0.10.0, 0% under cover only), since it no longer moves the band. Sidesteps take its place.
- Closing in holds steady at 33–43% of shots in both: its value is the position, not Melee Defense.
- Fights are a fraction of a round shorter under cover only.

Neither package creates a dead zone around archers in these setups. In every 1v1 row the first melee attack comes by round 2 on average, even from 12 squares, so the choice between them can rest on which reads better at the table.

## 3. Archers 1v1 against melee, and the bow niches

- **One archer rarely beats one melee fighter on open ground.** Across S1's 36 rows, the archer wins 0–29%. The one exception is the scripted warbow against the unshielded two-hander at 12 squares, at 62%. The first melee attack comes by round 2 on average.
- **Shields close the window.** Against the shielded knight in heavy armor (S5), every bow wins 3% or less.
- **Without the shield, the superheavy stands out** at 22.0% [18.6, 25.8], against 7–10% for the others.
- **Against S6's armored beast (armor 4),** the bows rank by weight: shortbow 55.6%, longbow 58.0%, warbow 79.2%, superheavy 96.4%.
- **These rankings match the study's niches** (heavy bows against armor), but the heavier archers also have more HP and stamina (see Read this first).

## 4. What reactions cost and do

- **A reaction costs about 1 stamina:** one off-turn purchase, 1.0–2.4 a reaction. It's more where low walls invite a longer dive.
- **Against a warbow at 8 or 12 squares, tactical targets almost always react,** and it's nearly always a 1-square shift for the +1 Ranged Defense (95–100% of shots on open ground). The +1 is worth more than the stamina against a big total. At 4 squares they close in or back away instead.
- **Point-blank shots are rare** with tactical archers (none in these rows). Scripted archers that stand provoke up to 1.2 opportunity attacks a fight (two archers in S4), and 20–50% of those are made.

## 5. Agent sensitivity

The weight on a square closer (S1, longbow, 8 squares, sword and board) changes behavior a lot but outcomes little:

| `approach_weight` | Archer wins | Shots answered by backing away |
|---|---|---|
| 0 | 1.8% | 71% |
| 1/2 | 2.6% | 34% |
| 1 | 2.8% | 25% |
| 2 | 5.2% | 2% |

At 2, the fighter pays 2.4 stamina a reaction to close in and arrives with less.

## Next

- **Fix the tactical archer's aim** so it keeps a reserve. The heuristic treats stamina the target spends as worth as much as its own, so it goes all in. Then rerun S1, S4 and S5.
- **Value the reacting target's own next turn** in its reaction (the plan's "still open" item).
- **Retune S3** to an even fight before reading anything from it.
- **Give S6 a stat block** once monsters exist.
