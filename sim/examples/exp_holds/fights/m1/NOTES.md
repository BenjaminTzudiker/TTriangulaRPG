# NOTES: sc_holds (rule set exp-holds), played by hand, both sides

Format: one line per turn (what, why). HOLD lines give the options and reasons for every hold
set, every hold considered and not set, and every decision a hold forced.

Planning numbers I use (exact odds from the engine's block solver, via my calc.py; no fight dice):
- Longsword on a fresh sample fighter: 3 steps (cost 9) = 4.3 HP and 10.6 stamina off; 2 steps (5) =
  0.9 HP, 9 stamina. On a fighter with <=4 ready, 3 steps down it 73%+.
- Shot, no aim (4): within 4 squares vs Ranged Def 2: 6.9 stamina (23% wound); vs 3 (dashed or half
  cover): 4.2. At 5-8 squares: 5.3 / 2.9. At 9-12: 3.3 / 1.8.
- So: the first strike costs the striker its blocking stamina and the answer usually kills it. Both
  sides want the other to come within 7 squares (6 free + reach) first.

## Round 1
- Opening dash phase: nobody. (Dashing before your own turn costs the same as on it; no one gains.)
- X: walks 5 to (15,4), 8 squares from A. Plans: (a) 6 squares to (14,4) = inside A's free-move strike
  range before Y and Z have come up, A could hit and hold me; (b) stop at 8 so A must dash (+1 per
  step) to strike. Chose (b). No stamina spent, recovery wasted.
- Dash phase before A: nobody.
- A: stays at (7,4). Plans: (a) dash-strike X for 13 stamina = A ends 7 squares from its friends with 7
  ready and Y, Z both reach it at full price; (b) hold the line and let the archer shoot. Chose (b).
- Dash phase before Y: nobody.
- Y: walks 5 to (15,6). Plans: (a) (15,5), the open middle lane = no cover from an archer who peeks out
  between A and B; (b) (15,6), where the crate at (11,6) gives half cover from row 5. Chose (b).
- (Second player takes over here; I agree with the orders so far and continue from them.)
- C: walked 4 to (7,5) and shot X, no aim (4; total 9 after -2 range, 1 crit die). A second shot (5) would
  leave C at 5 ready with Melee Def 1; not worth it while X is near max and wastes recovery anyway.
- X, shot: (a) stay and block, 4 stamina, 0 HP; (b) dash to (15,3) for cover, 1 + 2 blocks = 3, but
  escalation 1 on its own next turn (+1 on every step). Chose (a): X may attack in round 2.
- C: then 2 squares back to (5,5) (A and B screen it; nothing reaches it frontally without paying to leave
  their squares) and drew the blade for free (Melee Def 3 instead of 1 until its next turn). Ends 14/14.
- Z: walked to (15,5), making a line X-Z-Y at distance 8 from A and B (out of a free strike: 6 squares
  of movement + reach 1 = 7). Plans: (a) this; (b) bottom flank (14,9) = alone, 7 from B. Chose (a).
- B: stayed. A dash-strike on Y or Z (1 + 3+4+5 = 13) leaves B alone in front of three fresh Blues.

## Round 2
- X: (14,4), behind the pillar, exactly 7 from A and B. Plans: (a) bait at 2-3 squares (A strikes and
  steps back, Y and Z need dashes to punish); (b) 7 squares: A could only strike by walking 6 and
  stopping in Blue's line; next turn X strikes A fresh with no dash. Chose (b). Recovers to 16.
- A: back 1 to (6,4) (8 from X, so X needs a dash to strike first: +1 dash, +1 per step). Plans:
  (a) stay and take X's fresh strike next turn; (b) step back; (c) strike X now = A ends in Blue's
  line and dies. Chose (b). No enemy in reach: no hold.
- Y: (14,6), behind the crate, 7 from B. Same reasoning as X. Recovers nothing (full).
- C: drew the bow (free), walked 2 to (7,5), shot Z (open lane on row 5; X and Y had cover) with 1 aim
  (6). Plans: 0 aims (4) = drain ~5 only; 2 aims (9) = better if Z stays but Z will dash. Rolled 8.
- Z, shot: (a) stay, 5 to block; (b) dash to (16,6), total 6 vs defense 4: 1 + 1 = 2 and escalation 1
  on a turn where Z only walks. Chose (b).
- C: back to (5,5), drew the blade (free). Ends 12/14.
- Z: (13,5): 7 from A, 6 from B, so B must step back or be struck fresh next round. Plans: (a) (14,5)
  in the line; (b) (13,5) one step closer. Chose (b).
- B: back 2 to (5,6), 8 from Z: a strike on Z would end in front of X and Y; staying gives Z a fresh
  strike. Red's room to retreat is running out (x=1 wall).

## Round 3
- Dash phase before X: C dashed back 2 to (3,5) (1 stamina, escalation 1 on its own turn). Reason: from
  (14,4) X could reach (6,5), next to A, B and C, with one dash and no payment (route via (8,6),(7,6))
  and hit C with 3 steps (17% down). From (3,5) X would need 2 dashes + payments.
- X: dash-strike on A from (7,3), 3 steps (1 + 12 = 13). Plans: (a) this; (b) walk to 7 squares again
  (Red just steps back; round cap 8); (c) top flank to (8,2) = A hits and runs. Attacking A rather than
  B because A, the victim, acts next while drained, and fresh B acts last. Rolled 19, 1 crit: A blocked
  9, took 4 (hp 6, ready 7). X 3 ready, recovers to 7.
- HOLD X on A: 3 tokens. A's answers by token count (A 7 ready, X 7 after recovery):
  T=0: A pays 1 and walks away to a corner. T=3: pays 4 (ends 7). T=5-6: pays 6-7 (ends 4-5), but X is
  left with 1-2 ready, and A's 2-step counter (5) downs X 45-59%; if X drops, the hold ends and A walks
  off free. T=7: A can't pay; the OA would be 3 steps from tokens (A 62% down) so A counter-attacks X
  at 0 ready (84% down) and leaves. No T pins A: every T<=6 is just a toll. Chose 3: a 3-stamina toll on
  A for 3 less block for X against C's shot and B (X keeps 4).
- A (held by X, 3 tokens; A 6 hp, 7 ready; X 4 ready): options (a) pay 4 and walk to a corner (ends 7);
  (b) leave unpaid: X's OA 2 steps (5 = 3 tokens + 2 of X's ready), A 9% down; (c) hit X first with 2
  steps (5) to drain X's ready, so that the OA can only use tokens (1 step), then leave; (d) stay = Y and
  Z hit A at 6 ready (73% down). Chose (c): it spends A's stamina on X instead of on a toll. Rolled 16, 1
  crit: X blocked 4 (all it had), took 7 -> hp 3, ready 0. Then A left unpaid toward (1,4) (12 squares
  from Z: Z needs 3 dashes and gets 1 step).
- HOLD-forced, X: OA on A leaving: 1 step (2, paid from tokens; X has 0 ready so 2 steps were not
  affordable). Took it: free. Rolled 7, A blocked 2, 0 hp. Hold ends, 1 token idle. A ends 0 -> 4.
  Lesson: the holder kept 4 ready, the target spent its turn draining exactly that, and the hold's
  OA shrank to what the tokens alone could pay. The holder got hurt (7 hp) because it held.
- A: ends at (1,4), 0 -> 4 ready, 12+ squares from Y and Z. No enemy in reach: no hold.
- Y: dash-strike on B from (6,6), 3 steps (13). Plans: (a) B (fresh, 16): Z can follow up on B with
  a fresh strike (7 squares); (b) C with 2 dashes, only 2 steps, and Y ends next to fresh B; (c) A in
  the corner: 3 dashes for 1 step. Chose (a). Rolled 20, 1 crit: B blocked 10, took 4 (hp 6, ready 6).
- HOLD considered, Y on B (Y 7 after recovery): none set. B could only want to leave after Z hits it,
  and by then it will have ~0 ready: two unpaid 1-step OAs (Y, Z) at 0 ready would kill it anyway, so a
  hold adds nothing; tokens would only cut Y's block against C's shot and B's swing.
- C: shot Z from (5,4) (not adjacent to X or Y, open lane) with 1 aim (8), to drain Z below the 9 it
  needs for a 3-step strike on B (6 hp, 6 ready: 73% down). Plans: (a) kill X (3 hp, 0 ready) with a
  plain shot; (b) this. X can be finished later; B can't be saved later. Rolled 14, no crit (cap 5).
- Z, shot: (a) stay: solver takes the full 5 hp and spends nothing (blocking 14 at defense 2 costs more
  than the capped wound); (b) dash for 4 stamina, 0 hp, but then only 2 steps on B (16% down). Chose (a):
  hp for the 3-step strike. Z: hp 5, 11/11.
- C: 4 squares back to (1,5) (12 from Z), drew the blade. 3 -> 7 ready.
- I missed something on Y's hold: B can flee in the dash phase BEFORE Z's turn, when it still has 6
  ready. With no hold it pays 1 to leave Y; a 3-token hold would have made it 4.
- Dash phase before Z: B dashed 2 to (3,6), paying Y 1 (no hold) + 1 dash: 6 -> 4 ready, escalation 1.
  From (3,6) Z needs 2 dashes and gets only 1 step. B's plans: (a) stay = Z's fresh 3 steps, 73% down;
  (b) this; (c) 2 dashes (4 squares) for 4 total = 2 ready left, unnecessary.
- Z: walked to (8,6) (5 from B, 2 from X's square), stays at 11 ready. Plans: (a) 2 dashes to (4,5) next
  to B, no attack, hold B with 4 (B can't pay 5; the OA would be 2 steps from tokens, B 45% down): pins B
  so it can't kill X, but leaves Z (5 hp) beside A, B, C, and a Red hold on Z would stop Z diving from
  C's shot; (b) 1 step on B with 2 dashes (weak); (c) stand where Z can strike B fresh next round
  wherever it goes. Chose (c): X (3 hp) is probably lost either way; Z keeps 11 for a full strike.
- B: walked to (6,4) and hit X (3 hp, 0 ready) with 1 step (3): rolled 9, X down. Then back 3 to (3,5)
  next to the A/C corner. 1 -> 5 ready. Plans: (a) this (87% kill for 3 stamina); (b) retreat to the
  corner and recover to 8, leaving X alive. No enemy in reach: no hold.

## Round 4 (X is down)
- A: walked to (5,5) (next to Y, not next to Z) and hit Y with 1 step (2) to drain it below the 5 it
  needs for 2 steps. Plans: (a) drain Y; (b) drain Z (= A ends next to both); (c) stay in the corner
  and recover. Chose (a). Rolled 5: Y blocked 1 (6 ready). A 2 -> 6.
- HOLD considered, A on Y: none. T=1 or 2 stops Y paying to reach B or C with 2 steps left, but then
  A (6-T ready) is Y's best target instead: T=2 -> Y's 2 steps on A down 45%; T=4 -> 77%. Without a
  hold Y's best is ~30% on B or 16% on A. Holding only paints a target on the holder here.
- Y: hit A with 2 steps (5): rolled 13, A blocked 5, took 1 (hp 5, ready 1). Then Y walked off to
  (11,7) without paying: A, at 1 ready, could not afford even a 1-step OA (2), so leaving A was free.
  Plans for the rest of Y's move: (a) stay next to A with a 1-3 token hold as insurance if Z fails (A
  at 0-1 ready is stuck anyway); (b) back off out of B's reach to protect Y's 5 ready. Chose (b).
  No hold: nobody in reach at the end.
- C (archer, blade): walked 6 to (7,6), next to Z, and hit Z with 3 blade steps (6) instead of shooting.
  Plans: (a) shot with 1 aim: Z drains ~6 if it stays or dives (dive = escalation), keeps ~5 = still
  2 steps on A (95% down); (b) melee 3 steps: Z (5 hp) blocks ~8.7 to save hp, left ~2 = only 1 step
  on A (25%). Chose (b). Rolled 14: Z blocked all of it with 11 = 0 ready, 0 hp lost.
- HOLD C on Z: 1 token (C 5 after recovery). Z at 0 ready can't pay anything. T=0: Z walks away under
  a 1-step OA (1d6+2 vs 0 ready, 5 hp: 33% down) and escapes B. T=1: budget 3 = 2 blade steps (1 token +
  2 of C's ready), ~90% down, so Z must stay and take B's 2 steps (~55% down). T=2-3 adds nothing (3
  steps cost 6); T=4 only lowers C's block vs Y. Chose 1: the smallest hold that pins. (1 token buys
  a second OA step: the hold's leverage is largest when the target is at 0 ready.)
- Z (held by C, 1 token; Z 0 ready, 5 hp): options (a) walk away unpaid = C's 2-step OA at 0 ready
  (~90% down); (b) pay 2 = can't; (c) stay and recover to 4; (d) attack = no stamina. Chose (c).
- HOLD considered, Z on C (Z 4 after recovery): none. B is about to hit Z with 2 steps: Z at 4 ready
  ~50% down, at 2 ready ~77%. Every token would come straight out of Z's survival.
- B: walked 4 to (7,5) and hit Z with 2 steps (5): rolled 10, Z blocked 4, 0 hp. Z at 0 ready again.
  Plans: (a) this; (b) stay in the corner and recover to 9. Chose (a): Z is pinned (C's hold) and at 4.
- HOLD considered, B on Z (B 4 after recovery): none. Z at 0 ready already can't pay and would take a
  1-step OA (65% down) even without a hold; T=1-2 buys nothing more (2 steps cost 5); T=3 buys the
  2nd step but leaves B at 1 ready for Y's 2 steps (~85% down).

## Round 5
- Dash phase: nobody (Z at 0 can't dash; Red gains nothing by dashing before its own turns).
- A (1 ready, 5 hp): back to (1,4), 10 from Y (Y would need 2 dashes and can't afford a step after).
  Plans: (a) this; (b) walk next to Z and hold it in case C fails (A at 5-T ready next to Y's
  approach: Y's 2 steps on A ~50%+); (c) stand where Y attacking B must also stand next to A. Chose (a).
- Y (5 ready): walked to (8,7) and hit C (the archer, 4 ready, blade) with 2 steps (5). Plans: (a) B
  (4 ready, 6 hp): 45% down, but then C kills pinned Z (2 blade steps on 0 ready, ~92%); (b) C: 36%
  down, and even if it lives it is drained to ~1, so it can't kill Z. Chose (b). Rolled 17, 1 crit: C
  blocked 4, took 9: C DOWN. Its hold on Z ends (holder down), 1 token idle.
- Y: then 1 square to (7,7): it is the only square next to Z that A (at (1,4)) can reach without a
  dash; with Y on it A needs a dash and gets 1 step on Z instead of 2. 0 -> 4 ready. No enemy in reach.
