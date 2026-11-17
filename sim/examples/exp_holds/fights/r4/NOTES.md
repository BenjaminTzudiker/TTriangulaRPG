# NOTES - r4: rg_break (rule set exp-holds-next-turn-break)

Conventions: one line per turn (what + why); HOLD lines give the options and the reason.
Squares x,y. Odds tags: (calc) = my calc.py on the engine's block solver; (tool) = the tool's
own tables; (opener.py) = my small one-ply script on calc.py (assumptions stated there).

Fair play: dice come from one stream per attacker (engine: `attack:<id>`), so each creature's
nth die is the same as in the earlier fight whatever it attacks. From earlier_NOTES I know some
of them (X's 3-step opener left A at 8 HP / 7 ready; A's first 2-step counter rolled 14 with a
crit, its second 11; Y's first 4 dice 28; Z's first 3 dice 22 with a crit; Y's 5th-6th dice 16).
Every decision below is made on odds, not on those dice; where known dice could bias a choice I
say so.

## Rule under test, as I read it (checked in the engine source, read only)
- End of my turn: (1) my tokens come back, holds end; (2) set holds from READY (before
  recovering); (3) recover 4, ready + tokens <= max (6 + HP).
- Tokens stay out through my whole next turn. Pay-off 1 + h; unpaid OA budget = cap 2 + h,
  tokens spent first, rest from ready.
- NEW: the moment a holder loses any HP, all its holds end (engine: HoldEnded reason
  "injured"); tokens stay out (parked) until the end of its next turn.
- Engine detail: when a creature is wounded, ready + tokens are cut to the new maximum, ready
  first. So a wounded holder with many tokens out can lose ready stamina too.
- The tool's block solver (w = 3) does not value a hold: it may accept 1 HP to save stamina,
  which now ends the hold. Blocks are chosen after the defender sees the total, so where the
  solver's choice would be wrong for a holder I may re-run the same attack (same dice) with
  blk=P,G. I note every time I do this.

## Pre-fight reading
- Nobody reaches x=0 in round 1 (A needs 17 squares; 6 free + 5 dashes = 16 at most).
- Hold-break arithmetic (calc keep): a holder at 10 HP keeps its hold against a 2-step counter
  9.4% at 4 ready, 23% at 6, 47% at 8-10, 66% at 12, 84% at 16 (blocking for zero injury when
  it can). Against a 1-step counter: 75% at 4 ready, 87.5% at 6, 100% at 8.
- So once A has 5 ready for a 2-step counter, no hold X can afford pins it: A's price to leave
  is capped near 5 (the counter), whatever the tokens.

## Turn log
- R1 opening dash phase: nobody (A dashing only spends blocking stamina and raises its own
  escalation; X reaches it anyway with free squares. B/C can't outrun Y/Z; dashing early only
  spends their blocking stamina).
- R1 X, attack size (FIRST DECISION THE WOUND RULE CHANGES). Options: 4 steps (14; A down 23%,
  A left ~3 ready; X keeps 2 so hold <= 2) vs 3 steps (9; 1.4% down, A left ~5.4, 76% >= 5; X
  keeps 7) vs 2 steps (5; X keeps 11) (tool/calc). Under the wound rule a 2-step counter (5)
  breaks a hold on a holder at 4-6 ready 77-91% (calc keep), so A's price to leave is capped
  near 5 whatever the tokens. opener.py (one ply, guessed follow-ups): P(A down) 4 steps 0.39
  (0.388-0.391 for pin-death guesses 0.8-0.95), 3 steps 0.33-0.36, 2 steps 0.37-0.43 (but the
  2-step edge comes from A's solver blocks spending 15-16 to save 1-3 HP, which a fleeing A
  would refuse). Chose 4 steps: robust, and the drain itself now does the pinning.
  Fair play: I knew the 3-step result (A 8 HP / 7 ready = enough to counter), which leans
  toward 4; the choice rests on the odds above. Result: 28, no crits; A blocked 3P+6G (12),
  took 5 -> A 5 HP, 4 ready (max 11). X 2 ready.
- R1 X HOLD on A (X 2 ready; A 4 ready, can't afford a 2-step counter): A:2 -> pay-off 3, OA
  1 step paid by tokens (budget 4), X 4 ready in A's turn; A:1 -> pay 2; A:0 -> pay 1.
  A's best reply to each is to pay and run, so the hold is a pure stamina tax; A:2 takes the
  most (3). Cost to X: 2 ready during A's turn and its own round-2 turn (X is not going to
  catch a runner anyway). Also considered stepping X to (16,4), west of A, to force a
  2-trigger detour: every route there passes B's or C's reach, and B (95% dead anyway) can
  OA X for 2 stamina, costing X its hold stamina or ~5 HP. Stayed. Chose A:2.
- R1 dash phase before A: nobody (A can dash on its own turn at the same price).
- R1 A (5 HP, 4 ready; held X:2 = pay 3, or X's free 1-step token OA; A can't afford the 2-step
  counter, and a 1-step counter breaks the hold only 25% at X's 4 ready). Options: pay 3 + run;
  eat the OA (blocking costs ~2.5 on average, 25% to lose 2-3 HP); counter 1 step; stay (dies).
  Plan: stay out of 2-step range of Y/Z when they act (2 steps on A at 4 ready: 53% down; 1 step
  at 3 ready: 0%, calc). Paid 3, ran 6 free + 1 dash at esc 0 (1) to (9,4), 0 ready.
  HOLD DECISION: the hold changed what A did only by price: it paid 3 instead of 1.
- R1 dash phase before Y: A dashed (9,4)->(7,4) (1): with 3 ready, Y's or Z's best is 1 step
  (0% down, calc) instead of 2 steps at (9,4) (53%). B stands (dashing 1-4 only raises Y's
  odds from 95% toward 100%: Y reaches it on free squares, B just has less to block with).
- R1 Y: options alpha B (95%) vs 1-step chase on A (0%) vs C (lets B run off). Alpha B via
  (18,2)-(17,3): rolled 28 with a crit (same dice as the earlier fight), B blocked all 10,
  down.
- R1 Y with 4 free squares and 2 ready: moved (16,4)-(15,4)-(14,5)-(15,6), never leaving C's
  reach, to stand west of C against the (14,6) pillar (C's westward exit now costs 2
  triggers). HOLD on C: C:2 (pay-off 3) vs C:1 (pay 2, keeps Y's 2-step round-2 attack) vs
  none. A C that survives Z's alpha has 0-2 ready (calc), so 3 is never payable and 2
  sometimes is; C stands against Z either way (any dash pays Y's triggers and stays in Z's
  range). Chose C:2. Effect: it raised Z's value of attacking C (a surviving C is pinned,
  ~0.97 total) over the drain-A combo below.
- R1 dash phase before Z: A dashed (7,4)->(5,4) (2), 1 ready. Reason: at (7,4) Blue had a combo,
  Z's 1-step drains A under 2 ready 75% (my count of the solver's blocks at 3 ready), so A
  can't make its last dash, and X (4 ready, reach x=8 in its round-2 turn) re-holds A with its
  2 returning tokens + 1 (pay-off 4): about 0.68 A dead. At (5,4) X can't reach, A needs no more
  stamina, and Z's best on A is a 1-step at 25%. C stands.
- R1 Z: alpha C (74.6%; ~0.97 with Y's hold) vs 1-step on A (25%). From (17,6), east of C, so
  every square next to C is in Y's or Z's reach. C blocked all 12, took 6: down.
- R1 Z: nothing in reach, no hold. Blue can no longer reach A before A's round-2 turn.
- R2 dash phase before X: nobody (no Blue creature can get next to A before A's turn: X tops out
  at x=8, Y/Z can dash to ~x=11 and act after A anyway). X: nothing in reach, ended (its 2
  idle tokens came back: 4 + 2 + 4 = 10). A walked (5,4)->(0,4) and fled. FIGHT OVER round 2:
  A escaped at 5 HP; B, C down; Blue X, Y, Z all at 10 HP. Engine: "winner blue, side_out".

## After the fight
- Hold counts (tool): 2 holds set (X on A: 2 tokens; Y on C: 2), 4 tokens; 1 paid off (A paid
  3); 0 opportunity attacks, 0 tokens spent; the wound rule never fired. Y's C:2 was still out
  at the end (C went down while held). Hold prompts: 2 (X R1, Y R1).
- Branch check cf_r3line (scratch, same seed): the earlier fight's line (X 3 steps, A:7) under
  this rule set. A's 2-step counter rolled 14 with a crit; X blocked 1P+3G with all 4 (no block
  could reach 0 injury: armor 1 after the crit), took 5 -> "X's hold on A ends (injured), 7
  tokens idle"; X 5 HP, 0 ready, 7 tokens stuck until the end of its round-2 turn. A then walked
  off with pay=none: no prompt, no OA (X had no ready stamina). A at (11,4), 8 HP, 6 ready.
- Missed-line check cf_yhold (scratch): at Y's R1 turn, Y could have run to (8,4) (3 dashes) and
  held A with 10 without attacking: pay-off 11, OA 3 steps from tokens, 99.2% down (tool). I
  didn't consider it during play. Argued after: B (free, 10 ready) then reaches Y with 1 dash
  and 2 steps; Y at 4 ready keeps the hold only 9.4% (calc keep), and B ends far enough west to
  flee too. Then Blue's best is roughly one down (Z re-pins A or takes C), so Y->B (~1.9) was
  probably still right. The wound rule is what makes the lone run-and-hold fragile here.
- Same idea for Z at its R1 turn (A at (5,4), 1 ready): Z could run to (6,x) and hold A with 6
  (pay 7, OA 2 steps from tokens): about 0.9-0.95 A dead, but C (pays Y's 3 and runs) escapes;
  Z->C was ~0.97 with Y's hold. Near-equal; Y's C:2 hold tipped it.
