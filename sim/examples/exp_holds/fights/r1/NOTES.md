# NOTES — r1 (rearguard pair: rg_holds first, then rg_placeholder)

Conventions: one line per turn (what + why). HOLD lines give options and reasons.
Squares x,y. "alpha" = a 4-step attack at escalation 0 (2+3+4+5 = 14 stamina).

## Pre-fight reading of the position (both rule sets; nobody can hold before X's first turn ends)
- X is 1 square from A, 2 from B and C. Y is 3 from B, Z is 3 from C. Everyone has 6 free squares,
  so no number of Red dashes in the opening dash phase takes B, C or A out of a full attack
  (B would need 4 dashes = all 10 of its stamina to force even two enemy dashes).
- Odds I worked out (engine block solver): 4 steps on B (4 HP, 10 ready) downs it 95%; on C
  (6 HP, 12 ready) 75%; on fresh A 23% (mean injury 7.3, A spends ~13). 3 steps: 64% / 30% / 1%.
- Pre-dashing lowers the runner's blocking stamina faster than it raises the chaser's cost
  (B after 3 dashes: 4 ready, chaser needs 1 dash + 3 steps = 13, down 98%).
- So Red keeps its stamina and waits to see what Blue does; B and C can still dash in the
  phase just before Y's / Z's turn.

## rg_holds (exp-holds) — turn log
Kept the earlier player's two orders (W|, X| a A 4). Checked X's alternatives: X->B (pay 1 to leave A's
reach, 4 steps, B down 95%) leaves A fresh at 16 to down X (5 ready) or drain Y before Y's turn; X->A
drains A (spent 12 blocking, 5 HP, 4 ready) so Red's only fresh fighter can't punish anyone in round 1,
and Y/Z still get free alphas on B and C. I agree with X->A.
- R1 X: 4 steps on A: 28 total, A blocked 3P+6G, took 5 (5 HP, 4 ready, max 11). X at 2, recovers to 6.
- R1 X HOLD on A, options (X has 6 after recovery; A has 4 until its turn ends):
  0: A pays 1 and leaves, can go hold Y. 3: A can pay 4 (all its ready) to go. 4: A can't pay 5; OA
  budget 6 = 2 steps (5 = 4 tokens + 1 ready), but A can poke X first (1 step, 2 st) to drain X's 2
  ready, then leave facing only a 1-step OA: A down ~40% overall (calc). 5: OA budget 7, 2 steps paid
  entirely from tokens, so a poke can't shrink it: leaving costs A 53% down (84% after poking);
  X keeps 1 ready, enough to survive any single step (calc: 0% down, mean 3.1 injury). 6: X at 0
  ready, a 1-step poke downs X 25%. Chose A:5.
- R1 A (5 HP, 4 ready, pinned by X's 5): options: (a) leave and eat a token-paid 2-step OA, 53% down
  (calc) to gain 6 squares; (b) stay, poke X (1 step, 2 st; 2 steps cost 5 > 4); (c) stay and hold X.
  Y and Z are out of A's reach from (17,4), so A can't hold them without moving (which springs X's hold).
  Chose (b): X will attack A next round anyway; a poke costs 2 of A's blocking but strips X. Rolled 4,
  X grazed for 1 (0 injury) -> X at 0 ready until its turn, with all 5 tokens tied up on A.
- R1 A end: HOLD on X? X will want to stay and hit A in round 2, not leave, and A's ready (6) is what
  it blocks X's round-2 attack with; tokens would come straight off that. No hold.
- R1 dash phase before Y: B could dash, but every 2 squares it buys costs more of its own blocking than
  it adds to Y's price (3 dashes: Y needs 1 dash, then 3 steps vs B at 4 ready, worse for B). Nobody.
- R1 Y: options: B (4 HP, 10 ready) 4 steps 95% / 3 steps 64% (calc); A (pinned anyway, can wait); must
  drain B now or B (10 ready) either runs ~14 squares or kills X (0 ready). Went (18,2)->(17,3), the
  one square next to B and A reachable without leaving a threatened square; 4 steps: 28 with a crit,
  B blocked 2P+7G for all 10, took 8: B down (-4).
- R1 Y HOLD on A (Y at 6 after recovery): X's hold already pins A until X's round-2 turn; Y's lasts
  until Y's round-2 turn, so it covers A's round-2 turn after X's hold has gone back. Risk to Y: A's
  2-step attack on Y in its round-2 turn if X doesn't drain A first (Y at 2 ready: 45% down, 4: 16%,
  calc); C (if it lives) would have to spring Z's hold to reach Y. Options: 0 (A pays 1 to leave),
  3 (pay 4; 2-step OA needs 2 of Y's ready), 4 (pay 5; 2-step OA = 4 tokens + 1 ready), 5-6 (Y at
  0-1 ready). Plan is for X to hit A first in round 2, so chose A:4, keeping 2.
- R1 (B down, its turn skipped) dash phase before Z: C's options (calc): stand at 12 ready vs Z's
  4 steps 74.6% down; 2 dashes: Z needs none, 4 steps vs 9 ready 86%; 3 dashes (6 st) to x=10: Z must
  dash once, then 3 steps (12 of 15) vs 6 ready 73%; 4 dashes: Z 2 dashes, 2 steps vs 2 ready 77%.
  3 dashes ties standing on odds and gains 6 squares west; it also lets Z trade C for a sure kill on
  pinned A. Chose 3 dashes to (10,6).
- R1 Z: options: chase C (8 squares = 6 free + 1 dash, then 3 steps at esc 1 = 12 of 15, 73%) or take
  pinned A (1 square, 4 steps, ~97%) and let C (6 ready, at x=10) walk off next round. Chase: 22 with a
  crit, C blocked 1P+5G for all 6, took 9: C down (-3). Z has nothing in reach: no hold.
  Tool note: one W| line served both dash phases after Y and after B's dying-roll turn.
- R2 X (tokens back: 5 ready; X's round-1 hold ran out unused, A never tried to move): options: 2 steps
  (28% down, strips A), 1 step and a bigger hold, or no attack and hold 9 (but then A, with 6 ready,
  hits X at 0 ready: 84% down). Chose 2 steps: 16, A blocked 2P+3G for all 6, took 2 -> A 3 HP, 0 ready.
- R2 X HOLD on A (4 after recovery): A at 0 ready can't attack X on its turn, and leaving already means
  Y's token-paid OA (dead), so the hold only matters in the dash phases after Y's turn, when Y's hold
  will have gone back and A will have 4 ready: hold 4 makes leaving cost 5 > 4. Any OA X could make is
  1 step anyway (2 steps would need 1 ready beyond the tokens). No risk to X. Chose A:4.
- R2 A (3 HP, 0 ready, held by X:4 and Y:4): can't attack (a step costs 2), can't pay; leaving means
  Y's 2-step OA from tokens + X's 1 step = dead. Stayed; recovered to 4; no hold (Y and Z will attack
  it and don't need to move away from it, so tokens would only come off its blocking).
- R2 Y (tokens back: 6): 2 steps on A (67% per the tool): 16, A blocked 1P+3G for all 4, took 5: A down.
  FIGHT OVER round 2: Blue wins, no Blue creature injured. Holds set 3 (X:5, Y:4, X:4), none ever
  sprung: nobody paid one off and no token was spent on an attack; 2 ran out, 1 was live at the end.

### rg_holds afterthoughts (after the fight)
- Missed Red line, R1 A's turn: A eats X's 2-step token OA (53% down, calc) to step to (18,3) next to
  Y and hold Y with its 4 after recovery. Then Y must kill A first (cheap) and has only 2 steps at esc 2
  left for B (B 16% down instead of 95%), or pay 5 / take a 1-step OA and hit B with 3 steps (64%).
  Rough guess: B's chance to live through round 1 goes from ~5% to ~20-40% (which Y
  option Blue picks decides it). Not replayed: dice streams
  are per attacker and fixed by the seed, and I had already seen X's next two dice (6, 4: 16 total,
  which beats A's 4 ready for 5+ injury, so with this seed the line fails at the OA).
- Same seed (31) in rg_placeholder: per-creature dice streams repeat there, so I know the first rolls
  of X, Y, Z and A going in. Decisions there are made from the odds tables only.

## rg_placeholder (exp-0.11.0: no holds; OA = 1 step at base 2; pay-off always 1) — turn log
- Opening dash phase: same reading as in rg_holds (no Red dash outruns a 6-square move + reach). Nobody.
- R1 X: without holds X can't pin A, so X->A only drains A and has a 23% chance to down it; A can then
  pay 1 and run. Rough expected Blue downs (my estimate from the calc tables): X->A ~2.1 (A 23%, B 95%,
  C ~90%); X->B ~2.0 if A answers by running off (it reaches x=3 with 4 dashes and can't be caught),
  ~2.5 if A instead spends itself draining Z to save C. Close; X->A also takes away Red's option of
  using A's stamina to drain Y or Z. Chose X->A 4 steps (I know this seed's roll will not down A; the
  choice is from the odds).
- R1 X (2 ready after the alpha): no holds, so the only way to tax A's escape is position. Moved
  (18,4)->(17,5), paying A off (1; A's 1-step OA would cost X ~1.75 + 1.75 HP): still next to A (A pays 1
  to leave), and next to C, so a C that survives Z's alpha springs two OAs when it runs. X ends at 5.
- R1 A (5 HP, 4 ready), options: (a) pay X 1 and run: 6 free + 1 dash = 8 squares, keep 2 (+4 = 6), one
  more dash before X's round-2 turn puts it 10 from X, out of X's reach for any attack (2 dashes +
  a step costs 3 + 4 > 5); (b) pay 1, step next to Z and poke it (2 st) so Z may lack the 14 for 4
  steps on C: by my count Z keeps 14+ about half the time, so C's round-1 death drops ~75% -> ~50%,
  but A then sits next to X and Z at 5 ready and likely dies; (c) same poke on Y for B (95% -> 64%).
  My estimate: (a) A escapes ~95%, C ~3%; (b) A ~35%, C ~15%. Even weighting the wounded 2x, (a).
  Chose (a), the exact path (16,3) first so only one square left is in X's reach.
- R1 Y: B (4 HP, 10 ready) 4 steps 95%, same as in rg_holds. Without holds there's no reason to stay
  next to A's old square, so Y went (18,3)-(17,4)-(16,4)-(15,3), west of B, with no square left in a
  Red reach; 28 with a crit, B blocked 2P+7G for all 10, took 8: B down. With its last 2 free squares Y
  stepped to (15,5), west of C and next to it: a surviving C now has to leave three reaches (X, Y, Z).
- R1 dash phase before Z: C (12 ready) is next to X and Y. Running costs 1 per pay-off (2) on top
  of the dashes: pay 2 + 3 dashes leaves 4 ready and Z still gets 3 steps after one dash: 93% down
  (calc), worse than standing (74.6%). Stand. A (9,4) waits to dash until just before X's round-2
  turn (same price now or later; later sees what X does).
- R1 Z: moved (18,6)-(17,6) (no reach left), 4 steps on C (74.6%): 26 with a crit, C blocked 3P+6G for
  all 12, took 6: C down (0). Z spent its last 4 squares going west to (13,5), in case A stalls.
- R1 dash phase after Z (it and the one after C's dying roll take one W| line, so A can't wait for the
  second): A at (9,4) is 8 from X; X (5 ready) could reach it next turn with 1 dash + 1 step (1 + 3).
  One dash (1) to (7,4) makes it 10: X would need 2 dashes + a step = 3 + 4 > 5, and any dash war in
  the phase costs X more than A (X 1, 2.. vs A 1, 2..; X needs a step on top). Y, Z act after A's
  round-2 turn, so they can't stop it. Blue: no dash is worth it.
- R2 X (5 ready, A 10 away): reaching A takes 9 squares = 2 dashes (3), then a step at esc 2 costs 4:
  no attack possible. Best left: make A pay tolls. Moved 10 squares to (7,5) next to A (cost 3), ended
  at 6; in the dash phase dashed (1) to (6,4), into A's path, without paying A off (A's OA would leave
  A 3 short of its own escape: 2 tolls + 1 dash = 4). A declined the OA.
- R2 A (5 ready, esc 1): 7 squares to x=0 around X = 6 free + 1 dash (2) + 2 tolls (1 each) = 4 of 5.
  Took (6,3)-(5,2)-...-(0,2), paid both, fled with 1 left. FIGHT OVER round 2: B and C down, A fled
  (5 HP); no Blue creature injured. Pay-offs: 4 paid (X once, A three times), 1 OA declined.
