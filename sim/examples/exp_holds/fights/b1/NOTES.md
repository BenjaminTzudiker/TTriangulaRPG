# br_holds (exp-holds) — play notes

Setup: Red A sample (5,4), B greatsword (5,2), C spear (5,6). Blue X sample (15,4), Y greatsword (15,6),
Z spear (15,2). Order A X B Y C Z. Round cap 8.

Hold arithmetic I worked out before playing (budget = cap + tokens; steps cost base, base+1, ...):
- longsword (base 2, cap 2): 0 tokens -> 1 step; 3 tokens -> 2 steps; 7 -> 3 steps; 12 -> 4.
- greatsword (base 3, cap 2): 0 -> none; 1 -> 1 step; 5 -> 2 steps; 10 -> 3 steps.
- spear Fin 0 (base 2, cap 1): 0 -> none; 1 -> 1 step; 4 -> 2 steps; 8 -> 3 steps; 13 -> 4.
- the mover's price to leave is 1 + tokens, so tokens between those breakpoints only raise the price.

Pre-fight read (odds tables): everything is very lethal. A fresh greatsworder (Def 2) goes down 78% to a fresh
4-step longsword and 87% to a 3-step greatsword. A drained creature dies to the next attacker. So: do not step
into the free strike range (7 for swords, 8 for the spear) of two enemies who act back to back; keep the
greatsworder out of an enemy sample fighter's range until that fighter is busy/drained.

Second player's read (took over at Z's round-1 turn, kept the first player's orders):
- A greatsword with one dash still makes a 3-step attack (15) on a fresh Def-2 target: 87% down. So B and Y must
  stay 10+ from the enemy greatsword at the end of every turn. A greatsword 1-step probe (3 stamina) makes a
  fresh Def-3 target spend ~6.5 to block it; a longsword 2-step (5) makes it spend ~9. Probes are cheap drains.
- Each creature is followed in initiative by one enemy (A->X, X->B, B->Y, Y->C, C->Z, Z->A). A prober is
  answered by that enemy at once. A two-attack combo on one target always has one enemy turn in between; the
  best combo targets are creatures that do NOT act in between (they can only escape by dashing). Holds are what
  make that dash escape expensive, and they cost the holder blocking stamina against the in-between enemy.

## Round 1 (first player's orders, kept)
- Dash phase before A: nobody (10 apart, nothing to gain).
- A: moved 5,4 -> 7,4. X: stayed. B: 5,2 -> 5,3. Y: 15,6 -> 17,5 (back). C: 5,6 -> 7,5.
- Z (me from here): stayed at 15,2. Could reach A or C (spear free range 8) but would end alone in front of
  A, B, C, who all act before Z again. No enemy in reach, no hold.

## Round 2
- A: stayed at 7,4. Alternatives: dash-strike X/Z (ends drained beside all three blue) or creep (puts A in X's
  free range with B/C too far back to punish). Stay.
- X: stayed at 15,4. Same reasoning mirrored.
- B: 5,3 -> 5,4 (central, 10 from X and Z, 12 from Y: out of every one-dash 3-step).
- Y: stayed at 17,5 (10+ from all red).
- C: stayed at 7,5. Could probe X (free range 8) but A/B too far to follow up; Z would answer at once.
- Z: stayed at 15,2.

## Round 3
- A: 7,4 -> 8,4. Creep: inside X's free strike range but out of Y's one-dash 3-step only if Y stays put; B and C
  can reach every square X would probe from. Alternative (stay) = endless standoff/draw at the cap.
- X: moved 9,4, 2-step probe on A. Two crit dice: A blocked 7 times (10 stamina) and still took 6 -> A 4 HP, 6 ready.
  HOLD DECISION (X, 11 ready -> 15 after recovery). Options: none (X keeps 15; A can run: pay 1 + two dashes 3 =
  4 of its 6, ends crippled but alive); 3 tokens (A's run costs 4 + 3 = 7 > 6, so A is pinned for Y/Z; X drops
  to 12 and B's 3-step on X goes 31% -> 45% down); a second 1-step chip (4 stamina gone for good, drains A to ~3).
  Chose A:3. Reason: X was going to eat B's attack anyway; pinning the crippled A is what lets blue convert.
- Dash phase before B: A (held, 3 tokens) stays. Options: pay 4 + dash (A left on 1-2 ready, any chaser kills it);
  leave unpaid = X's OA budget 5 = 2 steps, 48% down for A; stay on 6 ready. (Later, at 0 ready, X could still
  have made a 1-step OA on A paid wholly by the 3 tokens.) Stayed.
- B: hit-and-run on X: in to 8,3, 2-step (rolled 1,1 = 12, X blocked for 5), then a 1-step (13, X blocked for 7 ->
  X at 0 ready, 10 HP), out to 5,3. Chose 2 steps not 3: 3 steps = 45% kill but B left on ~8 in Z's one-dash
  reach (54% for Z); 2 steps + chip left B on 8 after recovery. X had 0 ready and no tokens on B, so B left its
  reach without paying: X's OA was impossible. (X's 3 tokens sat on A, useless for X's own defence.)
- Y: one dash to 9,5, 2-step on A (20): A blocked with its last 6, took 5 -> A DOWN. Chose 2 steps (81%, keeps Y
  on 10) over 3 steps (99%, Y on 4 next to C). No enemy in reach, no hold.
- C: 4-step on Y from 7,5 (reach 2, no move needed): 25 with a crit, Y blocked 10 times, took 14 -> Y DOWN.
  Chose Y (78.6% kill, fresh greatsword) over X (98% kill, but X is harmless for a turn). Then retreated
  7,5 -> 4,5 (out of Z's one-dash range). No hold: holding X would leave C on 4-6 ready in front of Z (66-88%
  down) and X just walks east next turn anyway.
- Dash phase before Z: B dashed 5,3 -> 3,3 (1 stamina, esc 1). Z's best attack on B fell from 45.9% to 7.8%.
- Z: two dashes to 5,2, 2-step on B: rolled 8, B blocked for 5 -> B 2 ready.
  HOLD DECISION (Z, 4 -> 8 after recovery). B can't attack next turn (1 step costs 4, it has 2) and can't get out
  of Z's 8-square reach in this arena, so B gains little by moving. Breakpoint is 4 tokens (2-step OA, 39% down);
  1-3 tokens = 1 step (~2 HP) and a price B can barely pay. Each token is blocking stamina lost vs C's 2-step
  (0% at 8 ready, 4.7% at 4). Chose B:1 as a cheap tax on any move.

## Round 4
- Dash phase before X: nobody (B held and on 2; X on 0).
- X (3 ready: its tokens on A came back unused, A being down): 9,4 -> 4,3 (route went round C's reach-2 zone via
  Z's square), 1-step chip on B. Crit: B took 7 -> 3 HP, 0 ready. Chose the chip because it raised Z's later
  2-step on B from 10.9% to 46.9%; C's answer on X (5 ready) only 1.6%. No hold: B on 0 ready would die to X's
  own free 1-step OA (cap 2) if it moved, so a hold adds nothing and costs X blocking stamina vs C.
- B: stayed, no attack possible (0 ready, esc 1). Any move = X's free OA + Z's hold. No hold on X (B needs every
  point to block).
- C: 4,5 -> 4,4, 2-step on Z (Z blocked for 5 -> 2 ready). Purpose: Z's 2-step on B is 84% at 5 ready, but with
  only 2 (+1 token back) Z can only 1-step (12.5%). No hold: X and Z can hit B without moving.
- Dash phase before Z: B stays (running costs all 4 of its stamina and still ends in Z's reach on 0).
- Z (3 ready with its token back): 1-step chip on B (B blocked with 1 graze -> 3 ready). Chip makes X's next
  2-step ~100% (vs 95%). Z's B:1 hold had ended unused at Z's turn start. No new hold: B won't move, C won't
  move, and tokens would leave Z weak vs C's 2-step.
  Checked the engine: at the round cap the result is a draw (winner None).

## Round 5
- X: 2-step on B (12): B blocked with its last 3, took 6 -> B DOWN. No hold (C can reach X anywhere; holding C only
  weakens X: C's 2-step on X is 4.7% at 4 ready, 22% at 2).
- C (alone; X 4 ready, Z 5): 2-step on Z (blocked for 5 -> Z 0 ready) so Z can't attack this round; X has only 4
  next round. Alternatives: hit X (then Z hits C on 4 ready), or rest. Stayed adjacent to X (leaving would be X's
  free 1-step OA: C had 0 ready to pay). No hold.
- Z (0 ready): moved 5,2 -> 9,2 to recover; leaving C's reach was free (C has no OA without tokens; Z couldn't
  have paid anyway). Moving away also makes any C attack on Z cost C a trigger from X.

## Round 6
- X (4): 1-step chip on C (C blocked for 3 -> 1 ready). HOLD: C:3, and it was free: C (1 ready) cannot attack
  before X's next turn and X doesn't move, so X's lower ready stamina risks nothing. 3 tokens = breakpoint for a
  2-step OA (~60% down on C at 1 ready). More tokens add nothing (C can't pay 4 anyway).
- C (1): stayed, no attack possible; moving = X's 2-step OA. Recovered to 5. No hold.
- Z (4): 9,2 -> 6,3, 1-step chip on C (blocked for 3 -> 2 ready). No hold: C has nowhere to run.

## Round 7
- Dash phase: C stays (leaving = X's held 2-step OA).
- X (6 with tokens back; hold on C ran out unused): 2-step on C: 45.3% listed; C blocked 2, took 10 -> C DOWN.
- FIGHT OVER: blue wins, round 7. X 10 HP (1 ready), Z 10 HP (6 ready). Red A, B, C and blue Y down.

## Totals (from the log)
- 38 turns, 14 attacks, 3 holds set (7 tokens), 11 end-of-turn hold opportunities, 0 holds triggered or paid,
  0 opportunity attacks, 0 stamina paid to leave a square, 4 dashes.
- Post-fight check of the one hold that mattered (X on A, r3): unheld, A could have run for 4 (to ~4,4 on 2
  ready); Y's only chase (3 dashes + 1 step at esc 3) downs A there 58.3% and leaves Y deep in red's half. Held,
  A stayed and Y's 2-step from one dash was 80.6% (it hit). X's held 2-step OA on C in r6 would have been 59.4%.
