# br_next (exp-holds-next-turn) - play notes

Setup: Red A sample (5,4), B greatsword (5,2), C spear (5,6). Blue X sample (15,4), Y greatsword (15,6),
Z spear (15,2). Order A X B Y C Z. Round cap 8. Seed 86 (same dice as the earlier br_holds fight).

Engine check (read timeline.py/stateops.py, not edited): end of turn = escalation resets, tokens out come
back to ready, holds set from ready, then recover 4 capped at max - tokens. So a hold of H never loses
stamina; it locks H out of ready (blocking AND my next turn's attack) until the end of my next turn.
Holding at full stamina also wastes recovery (cap counts tokens).

Hold arithmetic (budget = cap + tokens; OA steps cost base, base+1, ...; tokens spent first):
- longsword (base 2, cap 2): 0 tokens -> 1 step; 3 -> 2 steps; 7 -> 3 steps; 12 -> 4.
- greatsword (base 3, cap 2): 0 -> none; 1 -> 1 step; 5 -> 2 steps; 10 -> 3 steps.
- spear Fin 0 (base 2, cap 1): 0 -> none; 1 -> 1 step; 4 -> 2 steps; 8 -> 3 steps.
- price to leave = 1 + tokens. Tokens between breakpoints only raise the price.
- New cost: each token is also 1 less to attack with on my next turn. Attack steps cost
  longsword 2,3,4,5 (cum 2,5,9,14); greatsword 3,4,5 (cum 3,7,12); spear 2,3,4,5 (cum 2,5,9,14).

Fresh-vs-fresh odds (tool, esc 0): longsword 4-step on greatsword 77.6% down, on sample 23%;
greatsword 3-step on greatsword 87.3%, on sample/spear 30%; spear 4-step on greatsword 47.5%.

## Round 1-2 (standoff)
Reused the earlier orders after checking each: nobody ends a turn in an enemy's reach in rounds 1-2,
so no hold can be set, and the standoff logic (free strike ranges 7 sword / 8 spear, +2 per dash;
greatsworders must stay out of enemy fighters' one-dash range) does not involve holds. The new rule
only makes holds dearer, which if anything makes approaching slightly safer - not enough to change
who should approach first (see round 3).
- R1 A 5,4->7,4 (sturdiest creature forward; only Z's free reach or a dash can hit it, low odds).
- R1 X stays (dash-strike on A 1.4% down, leaves X drained beside A, B, C). B 5,2->5,3 (stay 10 from Y).
- R1 Y 15,6->17,5 (out of A's one-dash 3-step, 30% on a greatsworder). C 5,6->7,5 (support A).
- R1 Z stays (a probe leaves Z alone before A, B, C all act).
- R2 A stays (creep would be in X's free range with B too far back). X stays (mirror).
- R2 B 5,3->5,4 (central, 10 from X and Z, 12 from Y). Y, C, Z stay (any probe is answered at once).

## Round 3
- A 7,4->8,4 (kept the earlier creep: invites X where B and C answer; staying = draw at the cap; the new
  rule makes X's pin dearer, so the creep is if anything safer). Last copied order.
- X (first decision the new rule could change): options stay / 2-step probe / 3-4-step. 2-step from 9,4
  chosen on reasoning (A spends ~9; X keeps 15 vs B). Same dice as before: two crits, A 4 HP, 6 ready
  (max 10). X 11 ready, esc 2.
  HOLD DECISION (X, 11 ready; whatever it holds is also off its round-4 attack):
  B's 3-step on X (whatif): 15 ready 31.3% down, 14 36.9%, 13 42.8%, 12 45.4%, 11 (if X chips) 55.7%.
  A's run to 4,4 (2 dashes, 1+2): H0 pay 1 -> 2 ready (Y's 3-dash chase 58%); H1 pay 2 -> 1 ready (75%);
  H2 pay 3 or block X's token-paid 1-step OA (~2.9) -> 0 ready (certain death if chased); H3 pay 4,
  can only reach 6,4 on 1. Staying on 6: Y's one-dash 2-step 80.6%, 3-step 99.9%.
  X's OA on A: 0-2 tokens = 1 step (A spends 2.9, 0% down); 3 tokens = 2 steps (34% down).
  Chose A:2 = smallest hold that makes running worse than staying for A. A:3 only adds an OA that
  A will never trigger, for 1 more off X's blocking (B 42.8 -> 45.4) and off X's round-4 attack.
  Chip (4 more, X to 11) rejected: B's 3-step 55.7%. No hold rejected: A runs and blue's only kill is a
  deep chase. Cost of A:2 vs none: +11.5 points on B downing X, and X attacks with 2 less in round 4.
- Dash phase before B: nobody. HELD (A, 6 ready): stay. Every run ends on 0-2 ready inside a chaser's
  range; staying keeps 6 to block. A also waits: if B downs X the hold ends and A can leave free.
- B: 5,4 -> 8,3, 3-step on X (43% listed; single 3-step beats 2+1 for damage). Rolled 1,1,8 = 25:
  X blocked 11, took 4 -> X 6 HP, 2 ready (max 12), 2 tokens still on A. B (4, esc 3) cannot attack again;
  staying beside X = Y's free 3-step. Paid X 1 to leave (unpaid: X's 1-step OA costs B ~3.25 blocking +
  1.75 HP) and went back to 5,3 (12 from Y). No hold possible.
- Dash phase before Y: nobody. HELD (A): stay (same reasoning; X alive, hold on). X stays: it can't
  outrun C (reach 2, free range 8) and moving off A would release the hold.
- Y: one dash to 9,5, 2-step on A (80.6%) rather than 3-step (99.9%): the 3-step leaves Y on 4 and
  C's 3-step then downs Y 77%; on 10, C's better target is X (3-step 96%). If the 2-step failed, Y could
  pin a drained A with a 1-token hold (greatsword 1-step OA). Rolled 5,5 = 20: A blocked with its last
  6, took 5 -> A DOWN. THE HOLD MATTERED: A stayed because running was worse. No enemy in Y's reach
  after (C is 2 away), so no hold. X's 2 tokens on A stay locked until the end of X's round-4 turn.
- Dash phase before C: nobody (X/Y can't escape C's reach 2 + 6 moves; red dashes only add escalation).
- C: X (2 ready, 6 HP) 3-step 96% for 9 vs Y (10 ready) 4-step 79% for 14 (C left on 6 for Z).
  3-step on X: rolled 1,8,6 + crit -> X DOWN. X's hold on A ended (holder down), 2 tokens idle.
  HOLD DECISION (C, 7 ready, Y in reach 2): Y wants to move (any attack needs it to leave 9,5), so a
  hold would tax it 1+T. But C stays in Z's free range: Z's 4-step on C 13% down at 11 ready, 37.9%
  at 8 (T=3), 51.9% at 7 (T=4), and Z drains C for Y's kill either way. Declined; retreated
  7,5 -> 4,4 instead (Z's best on C there ~0%), which also put Y out of reach.
- Dash phase before Z: B 5,3 -> 3,3 (1, esc 1): at 5,3 Z's one-dash 3-step downs B (7 ready) 54.1%;
  at 3,3 Z needs two dashes and gets a 2-step: 10.9%. Cost: B's round-4 steps start at 4.
- Z: options attack B (2 dashes + 2-step, the most it can afford), attack C (~0%), wait (red recovers).
  Key: a drained B can't get beyond 8 squares of Y, and Y's dash + 2-step costs exactly its 10, so
  draining B sets up Y's kill (2-step on B at 4 ready: 90-100%). 5,2 (pay=none: B and C have no OA
  without holds). Rolled 1,3 = 8: B blocked all (5 stamina) -> B 10 HP, 1 ready. Z 4 ready.
  HOLD DECISION (Z, 4 ready; B and C in reach): B's best reply is to run west to x=1 for free (spear has
  no OA without tokens): B's death stays 85.4% (Y 2-step on 5 ready) but Y must dash + spend all 10,
  ending on 4 -> C's 3-step on Y 77.1% instead of 54.1%. B:1 makes that run cost B Z's token-paid
  1-step OA (B blocks with 1, ~2.9 HP) -> Y's kill ~98%. Cost: Z 7 instead of 8 vs C (C 3-step on Z
  4.9% -> 10.4%) and 1 off Z's round-4 attack. B:4 (2-step OA, 47% down) would leave Z on 4 (C's
  3-step 45.9%) and just make B stay. No hold on C (C has no reason to move). Chose B:1.

## Round 4
- Dash phase before B: nobody (B can't afford a dash at esc 1; others gain nothing).
- B (1 ready, esc 1, HELD by Z:1): can't attack. Options: stay (Y free 2-step 85.4%, Y left on 7, C's
  3-step on Y 54.1%) or run west to x=1 (8 from Y: Y must dash + spend all 10, left on 4, C's 3-step
  77.1%; but the hold makes B eat Z's 1-step OA first). Ran to 1,4 unpaid (couldn't pay 2).
  Z's OA (1 token + 1 ready): rolled 3, B grazed with its last 1, injury 0. B 10 HP, 0 ready (4 after
  recovery): Y's kill 89.6% instead of 85.4% (the hoped-for ~98% needed the OA to wound).
  THE HOLD MATTERED a little: it cost B its last stamina point, not HP.
- Y: options dash + 2-step on B (all 10, 89.6%), dash + 1-step (16.7%), wait (B recovers, C free hit
  on Z). 2,4 + 2-step: rolled 10,7 = 27 -> B DOWN. Y 0 ready, no enemy in reach -> no hold.
- C (11): 3-step on Y (4 ready) 77.1% vs Z (6) 18.6%; red's only winning line. Rolled 2,6,2 = 16:
  Y blocked 4, took 9 -> Y 1 HP, 0 ready (max 7). C 2 ready, esc 3, can't attack again.
  HOLD DECISION (C, 2 ready; Y and Z in reach): Z drains C next regardless (Z's 2-step on C at 6:
  C spends 5.0; at 4: 3.8 and 4.7% down). Y:1 is useless once C is drained (the OA needs 1 of C's
  own ready). Y:2 (token-paid OA, kills a 0-ready Y 100%) pins Y but leaves C on 4 vs Z; keeping 2
  for a round-5 1-step on Y (37.5%) would then mean ~25% death. Without a hold, staying near Y
  fails to Z pinning C + Y stepping out of C's reach; Y's round-6 1-step on a drained C ~50%.
  Chose no hold; ran 4,4 -> 10,5 (8 from Y: Y can't reach C on round 6 with 4 ready).
- Dash phase before Z: nobody (C can't leave Z's free range 8 with one dash).
- Z (6): blue's plan is Z drains C every turn so C never has stamina on its own turn, and Y (the
  damage) strikes a drained C: Y 1-step on C 0 ready 58%, 2 ready 17%; 2-step on 2 ready 93%.
  2-step from 11,4 (free move only; a dash makes the 2-step unaffordable): rolled 7,3 = 14, C blocked
  with all 6, took 1 -> C 9 HP, 0 ready. Z 1 ready.
  HOLD DECISION (Z, 1 ready, C in reach): the new-rule cost is concrete: C:1 leaves Z on 4 at its
  round-5 turn, so its drain drops from a 2-step (C to ~0.2) to a 1-step (C to ~1.9). Gain: a 0-ready
  C leaving pays 2 (can't) or eats a token-paid 1-step OA (12.5% down, 4.75 HP) -> C stays pinned
  in the middle within Y's reach. Unheld, C runs east free and is cornered by round 7 anyway
  (Y's 2-step ~93%). Close call; chose C:1 because it keeps C pinned for rounds 6-7, and from
  round 6 Z's stamina supports a 2-step drain alongside a 1-token hold.

## Round 5 (live order Y C Z; the tool now lists dead creatures last)
- Y (0 ready): can't attack; C has 0 ready so it can't punish Y either -> moved 2,4 -> 8,5 (2 from C).
- C (0 ready, HELD by Z:1): can't attack, can't hold (holds come from ready before recovery). Leaving
  = pay 2 (has 0) or Z's token-paid 1-step OA (12.5% down, 4.75 HP) and then cornered anyway ->
  stayed. THE HOLD MATTERED: a drained creature stayed put inside the striker's reach.
- Dash phase before Z: nobody (C paying 2 + a dash escapes neither Z nor Y).
- Z (4 ready, 1 token locked): 1-step drain (2 stamina; its 2-step needs 5). C blocked with all 4, took 2
  (crit) -> C 7 HP, 0 ready. HOLD: token back -> 3; C:1 again. Chose 1 not 2-3: a 0-ready C leaving
  already takes a token+1-ready 1-step that likely kills it; Z keeps 6 for round 6 (2-step). C:2 would
  only matter if C could pay 2.

## Round 6
- Y (4): 1-step on C (0 ready, 7 HP) 75% vs waiting for a 2-step at r7 (C would recover first).
  9,5, rolled 3 = 8, C took 6 -> C 1 HP, 0 ready. Y 1 ready. No hold: Z's C:1 already makes any C move
  fatal; tokens would only shrink Y's round-7 attack. Stayed adjacent (C has 0 ready on its turn).
- C (1 HP, 0 ready, HELD by Z:1 and adjacent to Y): can't attack; leaving = Z's token-paid OA, certain
  death. Stayed, recovered to 4.
- Z (6, 1 token locked): 2-step on C (76.6%): rolled 5,1 = 10, C blocked all with its last 4. Token back
  -> 2. No hold: C has 0 ready, can't dash before Y, and Y's 1-step on it is 100%.

## Round 7
- Y (5): 1-step on C, 100% -> C DOWN. FIGHT OVER: blue wins, round 7. Y 1 HP (2 ready), Z 10 HP (6).
  Red A, B, C and blue X down.

## Totals (log)
- 33 turns, 12 attacks + 1 OA, 5 dashes. 8 real hold decisions: 6 the engine asked (X r3, Z r3, Z r4,
  Z r5, Y r6, Z r6) + 2 where C stepped out of reach instead (r3, r4). C at 0 ready on r5/r6 had
  enemies in reach but nothing to set. 4 holds set, 5 tokens (A:2, B:1, C:1, C:1), all 1-2 tokens.
  1 triggered (Z on B: OA, 1 token + 1 ready, 0 HP), 1 dropped (holder X down; its target A was
  already down), 2 ran out unused (Z's C:1 twice; both kept C in place). 1 payment to leave (B paid X 1,
  unheld). Earlier fight: 3 holds (7 tokens), 0 triggered, 0 paid, 0 OAs.
- Engine notes: a hold on a downed target keeps its tokens locked (X showed A:2 after A went down) until
  the holder's next turn ends; digest is silent on that. Order line reshuffles dead creatures to the
  end from round 5 (display only). Holds are set before the +4, so a holder can only hold what it has
  left after attacking (Z: 4, 1, 3 max).
- Tool trouble: the session was cut off after Y's round-3 turn; resumed from br_next.orders cleanly.
  whatif.py (mine) = table.py's own odds function for hypothetical ready/HP/escalation.

## Comparison with the earlier fight (exp-holds)
- Same through X's round-3 probe (same dice: A 4 HP, 6 ready). X held A:2 instead of A:3 (new rule:
  the 3rd token only bought a 2-step OA A would never trigger, and now also came off X's round-4
  attack). Same effect: A stayed and died to Y's 2-step.
- Divergence (my choice, not the rule): B used one 3-step on X instead of 2+1. Same dice (1,1,8) but X
  took 4 HP and kept 2 ready (earlier 0 HP, 0 ready). So B paid 1 to leave; C then killed X (96%) rather
  than Y. From there the attacks differ, so the dice differ.
- Endgame: Z drained and pinned with 1-token holds (3 holds) where the earlier Z chipped and retreated.
  Blue won in round 7 both times (earlier X 10 HP + Z 10 HP; now Y 1 HP + Z 10 HP).
