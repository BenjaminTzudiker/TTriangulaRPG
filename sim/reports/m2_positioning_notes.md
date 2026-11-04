# M2 positioning: notes on the suite

Companion to `m2_positioning.md`, which `se suite positioning --workers 8 --trials 500` generates. Every figure below is from that report: 500 trials a row, 95% intervals. Rows in one group share trial seeds, so differences within a group are paired.

Treat these as first measurements, not conclusions. Two agent families played them:
- **Scripted** agents approach with free movement only and never move off-turn.
- **Tactical v1** agents use simple, documented heuristics (`agents/tactical.py`).

Where the two families disagree, the agents are driving the result. Each point below names the agent behavior it depends on.

## What the M2 gate checked

- **The packet's movement and OA examples play out as battles** (`tests/golden/test_movement_battles.py`, `test_off_turn_battles.py`):
  - Avoiding Opportunity Attacks: 2, then 1, then 1.
  - Off-Turn Escalation: 1, 2, a 3-stamina dagger OA, 4; 10 in all.
  - The triggers: entering reach doesn't provoke; stepping sideways, leaving reach and stepping closer to a spear do.
  - Review F9's FIN-0 spearman, who can never make an OA.
- **Review Addendum 2's retreat costs are exact:** the AGI 1/3/5 fleer pays 10+1, 6+1 and 3+1, and the chaser then pays 1. This holds from `analysis/retreat.py` and as a played battle.
- **Geometry tests:** reach lines past corners and between walls, steps around corners, threat maps with walls and reach, path costs with avoidance, and reachable sets against brute force.
- **M1 is untouched:**
  - Lockstep parity with the review's simulator is still identical (the `slow` suite).
  - The pinned all-adjacent logs are byte-identical to `m1` apart from the RuleSet digest in `BattleStarted`.
  - A grid fight where everyone starts adjacent and nobody moves plays exactly the all-adjacent fights on the same seeds (`test_m2_suite.py`).
- **Random legal play on random maps, under every variant, never breaks an invariant**, and neither agent family is ever refused by the broker.

## For the designer

### 1. Phase 3's question, first answer: on open ground, movement doesn't save the 1v3 defender

On open ground the defender is down in every fight, in about 1.5 rounds. That holds starting engaged and starting 6 squares apart, under both v0.9 and review-candidate.

- **Starting engaged,** the tactical defender plays exactly as the scripted one: the same fights on the same seeds. On open ground no square it can reach lowers how many attackers can engage it. Attackers have 6 free squares; the defender's off-turn purchases give 2 squares each, escalating. This is Addendum 2's "retreat cannot buy tempo on open ground", now measured in a team fight.
- **Starting apart,** it backs off about 2 squares off-turn and lasts about 0.3 rounds longer (1.83 against 1.51 rounds), with no change in outcome.

Terrain is what changes it. With a one-square corridor behind it, the tactical defender steps in, so only one attacker at a time can reach it:

| Defender in the corridor scenario | Deaths per fight | Rounds | Draws (round cap 20) |
|---|---|---|---|
| v0.9, scripted | 0.45 | 1.5 | 0% |
| v0.9, tactical | 0.26 | 3.6 | 1.8% |
| review-candidate, tactical | 0.22 | 4.9 | 9.0% |

It still never wins, against attackers who simply queue.

Both depend on the agents:
- The tactical defender won't retreat if the move costs more than half its stamina. After a big block it may not afford to (trial 0's trace shows this).
- Attackers never rotate out to let a fresh one in.

So Phase 3's "does 1v3 still end in 1–2 rounds once the defender can move?" gets this first answer: on open ground, yes; with terrain at its back, it ends in 3–5 rounds. F6's options (block reset per attacker, a free retreat) are still the open-ground levers. The free retreat isn't built (ruled 2026-11-03).

### 2. F9: the weapon-based cap doubles a FIN-0 spearman's wins at a door, but he still mostly loses

A spear holds a door against a sword (both sample fighters otherwise).

| Spear | Spear wins |
|---|---|
| FIN 1, as written | 55% |
| FIN 0, as written | 7% |
| FIN 0, with F9 option 1 (`cap_rule = weapon_base`) | 15% |

The FIN-0 build differs from FIN 1 in more than the cap: FIN 1 also gives +1 damage per step and +1 crit range. So the honest F9 comparison is the paired pair on the same FIN-0 build: 7.4% [5.4, 10.0] against 15.4% [12.5, 18.8]. Opportunity attacks per fight rise from 0.64 to 0.86. The 0.64 are the sword's OAs on the spear, when it steps back to keep its distance.

"Control space with reach" works at FIN 1. At FIN 0, F9's first option helps but doesn't make the spearman competitive here.

### 3. Retreating to an ally helps only against chasers who won't buy movement

Two against two: the fleer starts adjacent to a chaser, with its ally 6 squares back.

| Fleer | Chasers | Fleer's side wins |
|---|---|---|
| Stands and fights (scripted) | Scripted (free movement only) | 39.4% |
| Falls back (tactical) | Scripted | 57.0% |
| Stands and fights | Tactical (buy extra movement) | 28.8% |
| Falls back | Tactical | 25.8% |
| Falls back, F10 option 1 (extra purchases move 1 square) | Tactical | 28.6% |
| Falls back, F10 option 2 (purchased squares capped at Movement) | Tactical | 25.8% |

Against chasers who only use free movement, falling back to the ally is worth 18 points. Against chasers who buy movement it gains nothing: 25.8% against 28.8% for standing, within noise. That is Addendum 2's "retreat cannot buy tempo" again, now with an ally to reach.

F10 option 1 barely moves it (+3 points, within noise). Option 2 changes nothing here, because no chaser in this scenario ever buys more than its Movement in a turn. F10 needs a scenario where chasers must buy a lot of movement, such as archer chases (M3), before its options can be judged.

### 4. A duel's first-mover edge depends on whether agents will buy movement

Two sample fighters start 8 squares apart on open ground. The first in initiative can't reach (6 free + reach 1 = 7).

- **Scripted agents** move only with free movement, so the first mover closes to distance 2 and the second mover strikes first. The first mover wins only 32.4% [28.4, 36.6] of decisive fights.
- **Tactical agents** buy the one extra square (1 stamina) and strike first: 57.3% [52.8, 61.6], back near M1's all-adjacent edge.

This mostly measures agents, not rules. It does show how much the opening can hinge on one flat-priced purchase. That's relevant to F10 (extra movement too cheap) and to Phase 3's first-mover check: on a grid, the first-mover edge depends on the starting distance.

## A reading that changed in M2, for your ruling

**When movement purchases are paid (C8).** The plan proposed paying each purchase when it is first needed, square by square. A random-play test then found a move stranded partway. Avoidance and blocks against OAs paid during the move, or an OA's injury lowering maximum stamina, left the mover unable to buy a square it had committed to, sometimes while it stood in an ally's square, and no rule says what happens then.

The engine now pays a path's purchases when the move is declared, like attack steps; a mover downed partway loses squares it paid for. It's recorded as pending in the Assumptions register. If you prefer pay-as-you-go, it needs a rule for a mover who can't pay for its next square.

## Smaller notes

- The 1v3 "first mover wins" column (about 75%) is trivial: three of the four creatures are attackers, and the attackers always win.
- "OAs per fight" and "off-turn squares" count both sides.
- The 1v3 all-adjacent rows reproduce M1's v0.9 result: the defender dies in about half of fights under System Shock. The engaged-start grid rows differ (0.43) only by sampling: on shared seeds the fights are identical.
