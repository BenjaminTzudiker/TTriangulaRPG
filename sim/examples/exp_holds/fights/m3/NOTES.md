# NOTES: sc_next (rule set exp-holds-next-turn), played by hand, both sides

Format: one line per turn (what, why). HOLD lines give the options and reasons for every hold
set, every hold considered and not set, and every decision a hold forced.

Rule under test, as I read BRIEF.md: at the end of your turn (1) your old tokens come back and
your holds end, (2) you may set tokens from what you have READY NOW (before recovery), (3) you
recover 4, with ready + tokens capped at max. Tokens stay out through your whole next turn.
So max tokens = what you have left after your turn; and a hold of T costs T of blocking until
your next turn AND T of your next turn's attack.

Hold arithmetic for a longsword (base 2, OA cap 2): OA budget = 2 + T. Steps cost 2, 3, 4, 5.
T=0-2 -> 1 step; T=3-6 -> 2 steps (5); T=7-11 -> 3 steps (9); T=12 -> 4 steps (14).
Pay-off for the first square = 1 + T. The OA is paid tokens first, then the holder's READY.

## Opening (rounds 1-2): checked against the earlier fight
Rounds 1-2 reused the earlier orders after checking each one; no creature ended a turn within
an enemy's reach, so no hold was possible and nothing in them depends on hold timing. Same dice,
same results (X shot for 4, 0 hp; Z dived the 1-aim shot for 2).
- R1 X/Y/Z stop 8 from A/B (out of a free strike: 6 moves + reach 1 = 7); A, B stay; C walks up,
  shoots X (no aim) using recovery it would waste anyway, walks back behind A/B, draws the blade.
- R2 X, Y, Z step to 7; A and B step back so any strike needs a dash (+1 per step); C shoots Z
  with 1 aim, Z dives (2 instead of ~5). Red has 2-4 columns of room left behind it.

## Round 3
- Dash phase before X: C dashes 2 to (3,5) (1 stamina, escalation 1 for its own turn). Without it
  X can reach (6,5) with one dash and no payment and hit C with 3 steps (17% down, ~5 hp, ~10
  stamina off). Alternatives: (a) nobody (X's dive on C is a sacrifice of X for most of C);
  (b) A dashes back too (then Red is cornered next round). Hold timing doesn't change this.
- X: dash-strike on A from (7,3), 3 steps (1 + 12 = 13). Plans: (a) this; (b) 2 steps (8) and keep 8
  for a big hold (under this rule a hold can only use what is left before recovery); (c) wait at 7
  squares again. 3 steps does ~4.3 hp vs ~0.9 for 2; A acts next while drained. Chose (a). Same dice
  as before: 19, 1 crit; A blocked 9, took 4 -> A hp 6, ready 7. X 3 ready.
- HOLD X on A (first decision the new rule changes). X has 3 ready, so T <= 3 (old rule: up to 7,
  set after recovery). X ends with 7-T ready, and the T tokens are also gone from X's round-4 turn.
  A (6 hp, 7 ready) can always leave: pay 1+T <= 4. A's best answer to any hold is to hit X with 2
  steps first (X at 7/5/4 ready takes 2.4/3.8/5.2 hp, 0/6/16% down), which also strips X's ready so
  the OA can only be paid from tokens. T=2 is the smallest hold whose 1-step OA is paid by tokens
  alone (12.5% to down A at 2 ready); T=3 adds a 2nd OA step only if X still has 2 ready, which A's
  counter prevents. Every token also leaves X weaker vs B's fresh strike later (3 steps on X: 30% at
  7 ready, 59% at 5, 73% at 4) and is missing from X's round-4 attack. Chose T=0: no hold can pin
  A, and every token comes out of X's survival. (Old-rule player chose 3; it backfired.)
- A (6 hp, 7 ready, not held): hit X with 2 steps (5), then walked to the corner (1,4). Plans: (a) pay 1
  and leave (X untouched at 7); (b) drain X first, then leave (X can't afford even a 1-step OA below 2
  ready); (c) stay and fight (Y and Z then strike A at ~6 ready: dead). Chose (b). Rolled 16, 1 crit:
  X blocked 6, took 4 -> X hp 6, ready 1. Left for free: X had 1 ready, no OA possible, no tokens.
  (Same dice as the earlier fight; there X held with 3, so X had 4 ready, took 7 and still got a
  token-paid OA.) A ends at (1,4), 12+ from Y/Z (they'd need 3 dashes). No enemy in reach: no hold.
- Dash phase before Y: B dashes 2 back to (3,6) (1 + escalation 1 on its own turn). Plans: (a) stay,
  Y's 1-dash 3-step strike costs B ~4.3 hp and ~10.6 stamina, then Z follows; (b) step back so every
  Red creature is 9+ from Y and Z (they need 2 dashes = 2 steps at most); B can still walk to X (1
  ready, 6 hp) on its own turn. Chose (b). (Not a hold decision; the earlier player let Y strike B.)
- Y: walked 2 to (12,6), behind the crate, 9 from B and C (one dash away next round). Plans: (a)
  2-dash strike on B or C = only 2 steps (12) and Y ends at 4 ready next to B and C; (b) stand
  next to X (X is lost anyway: C's 3 blade steps 98%, B's 2 steps 91%) = Y within a free strike of
  B and C; (c) stage for round 4. Chose (c). No enemy in reach: no hold.
- Dash phase before C: X (1 ready, 6 hp) dashes 2 east to (9,4), spending its last stamina. Plans:
  (a) stay at (7,3) with 1 ready: C walks 3, blades it (3 steps 98%) and walks back into the corner
  for free; (b) dash east: still inside C's and B's free reach, but a melee killer now ends its move
  within Z's or Y's free strike, so C must shoot from range (~half chance) or come out. Chose (b).
- C (11 ready, esc 1): drew the bow, walked 2 to (5,4) (4 from X: no range penalty), shot X (5): 11,
  wound capped at the bow roll 5 -> X hp 1. Then a 2nd shot (6) killed X (any wound downs a 1-hp,
  0-ready target). Plans: (a) one shot and keep 6 (-> 10) for Y's round-4 strike (3 steps on C: 30%
  at 10 ready, 89% at 4); (b) 2 shots and hide; (c) blade X = C ends next to fresh Z. Chose (a)
  then (b) once X was at 1 hp. C then walked to (1,5) (next to A, behind B: Y needs 2 dashes) and
  drew the blade. 0 -> 4 ready. X DOWN (round 3).
- (Session restarted here; fight state was intact.)
- Dash phase before Z: nobody.
- Z: walked 3 to (10,5), 7 from B, 9 from A and C. Plans: (a) 2-dash strike on B = 2 steps (12)
  and Z ends at 4 ready next to B; (b) A or C need 3 dashes = 1 step; (c) stand 7 from B so a
  round-4 strike needs no dash (3 steps for 9, leaving 7: enough for a real hold). B striking Z
  first would leave B in the open for Y's fresh strike. Chose (c). No enemy in reach: no hold.
- B (15 ready, esc 1): stepped back to (1,6): Red is a column A(1,4) C(1,5) B(1,6) against the west
  wall. Plans: (a) strike Z (3 steps at esc 1 = 12) = B ends in the open, Y's fresh strike next turn
  and Z's follow-up likely kill it; (b) stay at (3,6) = Z strikes B without a dash; (c) close up.
  Chose (c): every square next to C is also next to A or B; Y needs 2 dashes to reach anyone, Z 1.

## Round 4 (X is down)
- Dash phase before A: nobody.
- A (6 hp, 6 ready): stayed at (1,4), 6 -> 10. Plans: (a) stay; (b) step to (2,5) or out to x=3 to
  cover C's open squares (it can't: Y reaches any x=2 square with exactly 2 dashes, and A at x=3
  is in Z's free strike, 3 steps = 43% down); (c) 1-dash attack on Z = 1 weak step. Chose (a).
  Blue's threats this round: Y (2 dashes, 2 steps) on C at 4 ready = 36% down; Z (1 dash, 3 steps)
  on A at 10 ready = 43%, on C at 8 = 44%. No enemy in reach: no hold.
- Dash phase before Y: nobody (C can't get out of Y's 2-dash range anywhere on the wall).
- Y: 2 dashes to (2,4) (next to A and C) and hit C with 2 steps (3 + 9 = 12). Plans: (a) this
  (C at 4 ready: 36% down); (b) 2 steps on A at 10 ready = 6%; (c) stage and wait = B and A strike
  Y first. Chose (a). Rolled 14, 1 crit: C blocked 4 (all it had), took 6 -> C hp 2, ready 0.
- HOLD Y (4 ready; can hold A and/or C, T <= 4): none. C (0 ready, 2 hp) is pinned without a hold:
  it can't pay even 1, and an unheld 1-step OA kills it. After its own turn C has 4 and could pay
  1 + dash in the dash phase before Z, but that doesn't take it out of Z's 1-dash reach, so a hold
  of 3 (which would stop that) buys nothing. A won't leave (it wants to hit Y). Cost of tokens:
  B's 4-step attack on Y downs it 71% at 8 ready, 89% at 6; A hits Y next. Chose T=0.
- Dash phase before C: nobody. (A to (2,5) + B to (2,6) would close C's open squares to 1-dash
  routes, but Z then reaches (1,4) or (1,6) with 2 dashes and still kills C; costs A 2, B 1.)
- C (0 ready, 2 hp, held by nobody): stayed. Any step out of (1,5) gives Y a 1-step OA that kills it,
  and it has nothing to attack with. Ends 0 -> 4. No hold possible (0 ready before recovery).
- Dash phase before Z: nobody.
- Z: 1 dash to (2,6) (next to B and C) and hit C with 2 steps (1 + 7 = 8): 90.6% to kill. Plans: (a)
  this; (b) 3 steps (13) = certain, but Z left at 3 -> B's 4 steps down it ~95%; (c) 3 steps on A
  (10 ready, 6 hp) = 43%. Chose (a). Rolled 8 (1, 1): C blocked all 4, took 0 -> C 2 hp, 0 ready.
  A 3rd step now costs 5 (esc 3): certain kill but Z ends at 7 -> B's 4 steps on Z: 81%. Declined.
- HOLD Z on B: 2 tokens (Z 8 ready -> 6 -> 10 after recovery, 2 tokens out through Z's round-5
  turn). Purpose: protect Y, not pin B. B (16) is next to Z only; to reach Y (8 ready) it must leave
  (1,6), which is in Z's reach. B's best by T: T=0: pay 1, 4 steps on Y = 70.6% down; T=1: pay 2,
  still 4 steps (14) = 70.6%; T=2: pay 3 -> 13 = only 3 steps on Y (20%), or unpaid = token-paid
  1-step OA first, same; so B hits Z at 10 instead: 4 steps 45.5%; T=3: Z at 9 = 58.1%. T=2 is the
  smallest hold that makes switching targets cost B its 4th step. Not holding C: at 0 ready it is
  pinned anyway (can't pay 1; an unheld 1-step OA kills it).
- Dash phase before B: nobody.
- B (16, held by Z with 2): hit Z with 4 steps (14), no move. Plans: (a) this (45% down, and Z is
  drained either way); (b) pay 3 to reach Y = 3 steps on Y (20%); (c) 3 steps on Z and a big hold.
  Z's hold did what it was set for: B never considered leaving (1,6). Rolled 30, 1 crit: Z blocked
  10 (1 perfect, 9 grazing), took 9 -> Z hp 1, ready 0 (2 tokens still out on B).
- HOLD B on Z: none (B has 2 left). Z at 0 ready, 1 hp is pinned without one: it can't pay 1, and
  B's unheld 1-step OA from B's own ready kills it. B stays put: leaving (1,6) now would give Z a
  token-paid 1-step OA (Z has 0 ready but 2 tokens) and B can't pay the 3. B ends 2 -> 6.

## Round 5 (Z is down; Y alone)
- Dash phase before A: nobody.
- A (10 ready): paid Y 1 to step to (2,5) and killed Z (0 ready, 1 hp) with 1 step (2). Then hit Y
  with 2 steps (7) to drain it below the 2 it needs to kill C (0 ready, 2 hp, pinned by Y).
  Plans: (a) 3 steps on Y now (20% down) and let B kill Z later (Z would recover to ~6 first);
  (b) kill Z, keep 7 (Y then kills C anyway); (c) kill Z and drain Y. Chose (c). Z DOWN (round 5).
  Z's hold on B ended with it ("holder down"), 2 tokens idle.
- Y's blocks overridden (blk=2,2): rolled 13; the solver blocked 7 for 0 hp, leaving Y 1 ready =
  can't kill C. 2 perfect + 2 grazing (5) costs 1 hp and keeps 3. Y hp 9, ready 3.
- A: 0 ready, stays (moving gives Y a 1-step OA on 0-ready A, ~50% down). No hold (0 ready). -> 4.
- Dash phase before Y: nobody (C at 0 ready can't dash; nobody can stop Y's step on C).
- Y (3 ready): killed C (0 ready, 2 hp) with 1 step (2). C DOWN (round 5). Then stayed at (2,4).
  Plans for the rest: (a) stay, end at 5; (b) pay A 1 and walk 6 east = 0 -> 4, and B (7 away at
  most) still reaches Y with free movement; (c) attack A = nothing left. Chose (a).
- HOLD Y on A considered (T <= 1): none. A won't need to leave to win; 1 token = 1 less block vs B
  and 1 less attack next turn.
- Dash phase before B: nobody (Y can't get out of B's free reach even with dashes).
- B (6 ready): walked round to (3,5) without leaving a threatened square and hit Y with 2 steps
  (5): rolled 16, 1 crit, Y blocked 5 (all), took 5 -> Y hp 4, ready 0.
- HOLD B on Y: none (1 ready). Y at 0 ready is pinned without one (can't pay; A's and B's unheld
  1-step OAs each likely kill it). B ends 1 -> 5.

## Round 6
- Dash phase before A: nobody. A (4 ready) hit Y (0 ready, 4 hp) with 1 step (75%): rolled 10,
  1 crit -> Y DOWN. FIGHT OVER: Red wins in round 6 (A 6 hp, B 10 hp up; C, X, Y, Z down).

## Side check (scratch copy, deleted afterwards; not part of the fight)
- Replayed to Z's round-5 turn with Z alive and B:2 out: the tool showed Z at "stamina 0" and
  offered no attack; at the end of the turn it returned the 2 tokens, let Z re-set them, then
  recovered 4. So the engine does keep tokens unusable on the holder's own turn.

## Tally
- End-of-turn moments with an enemy in reach: 8 (X r3, Y r4, C r4, Z r4, B r4, A r5, Y r5, B r5).
  2 had 0 ready (no choice). 6 real choices: 1 hold set (Z on B, 2 tokens), 5 declined.
- Pay-offs: 1 (A paid Y 1, no hold). Free exits because the enemy couldn't afford an OA: 1 (A off X).
- Creatures pinned at 0 ready with no hold on them: C (r4), Z (r4-5), Y (r5).
