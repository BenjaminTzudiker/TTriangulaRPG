# NOTES — r3: rg_next (rule set exp-holds-next-turn)

Conventions: one line per turn (what + why). HOLD lines give the options and the reason.
Squares x,y. "alpha" = 4-step attack at escalation 0 (2+3+4+5 = 14). Odds marked (calc) come
from my helper calc.py (same engine block solver as the tool's tables; checked against the
earlier notes' 23% / 95% / 74.6% / 64% / 30%), (tool) from the tool's own tables.

Fair play: same seed as the earlier fight, so I know a few dice from earlier_NOTES.md (X's first
4 dice total 28, its next two 6 and 4; A's first die 4; Y's first 4 total 28, next two 16; Z's
first 3 total 22). Every decision below is made from odds, not from those known dice.

## Rule under test, as I read it
- End of my turn: (1) my tokens come back, my holds end; (2) set holds from READY (before
  recovering); (3) recover 4, ready + tokens <= max.
- Tokens stay out through my whole next turn: a hold of h is h less to attack, block and dash
  with until the end of my next turn. Pay-off 1 + h; unpaid OA budget = cap 2 + h, tokens first.
- Consequence for the opening: after a 4-step alpha X has 2 ready, so its hold is at most 2
  (pay-off 3; OA budget 4 = still only 1 step, now free for X). The old X:5 trap is impossible.

## Pre-fight reading
- Nobody can reach x=0 and flee in round 1 (A needs 17 squares: 6 free + 5 dashes = 16 at most).
  So every Red creature must survive at least one Blue turn after its own round-1 turn.
- Opening dash phase: same as the earlier fight (no Red dash outruns 6 free squares + reach;
  pre-dashing only spends the runner's blocking stamina). Nobody dashes.

## Turn log
- R1 opening dash phase: nobody (as above).
- R1 X, attack size (FIRST DECISION THE NEW RULE CHANGES): options 4 steps on A (23% down, A left
  ~3 ready; X keeps 2, so hold <= 2: pay-off 3, OA still 1 step, 0% down vs A at 4 ready, calc)
  vs 3 steps (1.4% down, A left ~5; X keeps 7 for a hold bigger than A's ready) vs going to B
  (pay A 1, alpha B 95%, but fresh A then kills X at 5 ready or runs: A escapes ~100%).
  Rough guess A dies ~0.6 (4 steps, then chase) vs ~0.85 (3 steps + trap). The 4th step (5 st)
  now competes directly with 5 tokens of hold. Chose 3 steps. Result: A blocked 3P+3G (9),
  took 2 -> A 8 HP, 7 ready (max 14). X 7 ready.
- R1 X HOLD on A (X 7 ready, A 7 ready; nobody else in reach): h=7: pay-off 8 > 7, unpaid OA
  budget 9 = 3 steps (7 tokens + 2 of X's ready): A 45% down (calc); X ends at 4 ready, A's
  2-step counter downs X 15.6% (calc). h=6: A can pay exactly 7 and walk 6 west (or eat a
  2-step all-token OA, 6.2% down); X ends at 5 (counter 6.2%). h=5: A pays 6, keeps 1.
  h=0: A pays 1 and runs 10+ squares, gone. Chose A:7: the only hold A can't pay on its turn.
  Known gap: A can poke X first; if X's blocks leave it under 2 ready the OA shrinks to 2 steps
  from tokens (15.6% vs A at 5 ready). After A recovers (11) it could pay 8 in a dash phase,
  but then has 3 left for dashes (4 squares): useless.
- R1 dash phase before A: nobody (A can't pay 8; B/C dashing only spends their blocking).
- R1 A (8 HP, 7 ready; HELD by X:7: pay-off 8, unpaid OA 3 steps = 45% down, calc). Options:
  (a) break out now, eat the 3-step OA: 45% dead, survivors ~0 ready at (11,4) - then Blue's
  Z can still pick C (75%) and leave a crippled A to X's chase, so it may not even save C;
  (b) poke 1 step (2) hoping X's blocks drop it under 2 ready (then the OA is 2 steps from
  tokens, 15.6% vs A at 5): solver leaves X >= 2 half the time, and a plan-aware X keeps 2
  every time (1P+1G), so no real door; (c) counter the holder with 2 steps (5): X at 4 ready
  is down 15.6% (then the hold ends and A walks 6 west); otherwise X ~0 ready and hurt, so a
  second 2-step counter next round downs it 36-53% (calc); (d) stay passive to 11 and counter
  with 3 steps next round: X moves first and can poke A under 9, so this is weaker than (c).
  Chose (c). (Fair play: I know A's first die is a 4 from the earlier fight; choice is on odds.)
  Result: rolled 14 with a crit; X blocked 1P+3G with all 4, took 5 -> X 5 HP, 0 READY, tokens
  A:7 still out until the end of X's round-2 turn. With X at 0 ready its OA can only be the
  2 steps the tokens pay for (3rd step needs 2 ready). (Earlier notes' "A rolled 4" does not
  match: my "known dice" are not reliable, good.)
- R1 A after the counter (2 ready, 6 free squares): leave now = 2-step token OA on A at 2 ready,
  59.4% dead (calc): no. Stay, recover to 6. HOLD on X? No: X at 0 ready can't pay to leave
  anyway and A's unheld 1-step OA already downs X 62.5%; tokens would cut A's 6 to 4. A| e.
- R1 Y: options alpha B (95%) vs alpha A (A 8 HP 6 ready: 95% too) - but B would then run free
  (or kill X at 0 ready); B is the one that escapes. Path (19,2)-(18,2)-(17,3) leaves no Red
  reach; (17,3) touches B and A. 4 steps (3 steps only 64%; a bigger hold on A isn't worth
  31 points of B). B blocked everything (10), took 8: B down.
- R1 Y HOLD on A (Y 2 ready): y=0 -> Y 6 ready in R2, A pays 1 to walk off Y; y=1 -> Y 5 ready,
  still exactly 2 steps (2+3) in R2, pay-off 2; y=2 -> Y 4 ready = only 1 step in R2, pay-off 3.
  Purpose: if A's R2 counter downs X, A has ~1 ready and can't pay 2 to walk off Y; and the two
  pay-offs add, so X can re-hold smaller (safer) and still trap A. Chose A:1 (free in steps).
- R1 dash phase before Z (B down, its turn skipped): C (6 HP, 12 ready) options (calc): stand
  -> Z's alpha 74.6%; 3 dashes (6) to (10,6) -> Z needs 1 dash + 3 steps at esc 1, 73.0%;
  4 dashes -> 2 ready vs 2 steps at esc 2, 76.6%. Equal-ish on odds; dash 3 gains 6 squares
  and pulls Z away from A (standing invites Z to (17,5), next to A AND C, where it could add a
  hold on A). It also offers Blue a fork: Z can take the trapped A (95%) and let C escape.
  Chose 3 dashes to (10,6).
- R1 Z: fork: chase C (73%) or alpha trapped A (95%, then C walks off). Trapped A's later death
  (calc): if A counters X in R2 it sits at 5 ready and Y's + Z's 2-step attacks down it 96%;
  passive at 10 ready, 62% in R2 and 98% by R3. Well above the 0.22 break-even: chase C.
  Route (19,6)-(11,7) along row 7, no Red reach left; 6 free + 1 dash. 3 steps (2 steps + big
  hold on C would also kill C later but ties Z to C in R2). 22 with a crit: C down.
  Z: nothing in reach, no hold. End of round 1: B, C down; A 8 HP 6 ready, held by X:7 and Y:1.
- R1 dash phase after Z: nobody. (A leaving now = dash 1, pay Y 2, X's 2-step token OA at 3
  ready ~40% dead, and it is still only 2 squares away at 0 ready. Z: A is within its 6 free
  squares next turn; a dash now would cost it its 2nd step.)
- R2 X (0 ready, 5 HP; can't attack; leaving A's reach unpaid = A's OA, 62.5% dead): stays.
- R2 X HOLD (its 7 tokens come back first -> 7 ready; A has 6 ready; Y's A:1 still on, pay-off 2):
  h=7 -> X 4 ready; pay-off 8; OA 3 steps (7 tokens + 2 ready), so "pay Y 2, take X's OA"
  is 84% dead (3 steps vs A at 4, calc); A's 2-step counter downs X 53%, but then A is at 1
  ready and still held by Y. h=6 -> X 5 ready (counter 36%); OA only 2 steps from tokens, so
  A pays Y 2 and breaks out at 28% risk. h=0 -> A pays 1+2 and runs to (7,4). Blue's score
  doesn't count X's life, only Red downs: chose A:7 again (same tokens, re-set).
  (X's R1 hold ran out unused: A never tried to leave; X re-set the same 7 tokens.)
- R2 dash phase before A: nobody (A leaving = X's 3-step OA; Z already within reach of any
  square A can reach west, a dash now would cost Z its 2nd step).
- R2 A (8 HP, 6 ready; held X:7 -> pay 8 / OA 3 steps; Y:1 -> pay 2 / OA 1 step): options
  passive (10 ready): Y's + Z's 2-step attacks 62% dead this round, ~95% by X's R3 turn;
  pay Y + eat X's 3-step OA: 84% dead; counter X 2 steps: X (5 HP, 4 ready) down 53.1%, then
  A at 1 ready eats Y's 1-step OA (pay 2 > 1) and walks 6 west with Y and Z still to outrun
  (my guess ~9% A gets away overall). Chose the counter on the holder.
  Result: rolled 11 (low); X blocked 1P+3G with all 4, took 1 -> X 4 HP, 0 ready, A:7 still out.
- R2 A after the counter (1 ready): leave now = X's 2-step token OA + Y's 1-step OA (can't pay 2):
  98% dead (calc); stay = recover to 5, then Y's + Z's 2-step attacks 96% dead. Stay. No hold
  (X and Y both want to stay put; Z is out of reach). A| e.
- R2 dash phase before Y: nobody (A's 5 ready can't buy a way out: dash 1 + Y's 2 + X's 2-step
  token OA, and Y/Z still reach it).
- R2 Y (5 ready): 2 steps on A (15.6%; 1 step + bigger hold would barely dent A): 16, A blocked
  1P+4G with all 5, took 3 -> A 5 HP, 0 ready. Any 2-step attack on A is now a certain kill
  (min 8 - 2 armor = 6 >= 5). Y HOLD: its 1 token comes back -> 1 ready; hold pointless (A
  can't move at 0 ready and Z kills it next). Y| e, no hold.
- R2 Z: moved (11,7)-(16,5), 5 free, no reach left; 2 steps (certain kill vs 0 ready): A down.
  FIGHT OVER, round 2: Blue wins, all Red down. X 4 HP, Y 10, Z 10.

## After the fight
- Hold counts (tool): 3 holds set (X:7 R1, Y:1 R1, X:7 re-set R2), 15 tokens set; 2 ran out
  unused, 1 live at the end; none paid off, no opportunity attack, no token ever spent.
  6 end-of-turn hold prompts (X, A, Y twice each).
- Checked in the engine (scratch copy chk.*, deleted after): with tokens 7 and ready 4 X's OA
  offers 3 steps (45.1% vs A at 7 ready); at ready 0 only 2 steps. So A's counter that emptied
  X's ready also shrank X's OA from 3 steps to 2 (tested).
- Correction: the earlier notes' "A rolled 4" was the total (die 1 + 3); this fight's A first
  die was also 1, so the dice streams did repeat (Y's 28 on B, Z's 22 on C, Y's R2 16 are all
  the same as before). No decision here turned on known dice: X's 3-step opener and A's
  counters were new attacks, and C would have died standing too (the earlier no-holds fight
  shows Z's 4 dice on a standing C).
