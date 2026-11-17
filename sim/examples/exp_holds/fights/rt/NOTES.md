# Red-team notes (exact odds from `table.py --odds` unless marked as a roll)

## Earlier player's files, checked
- t01a/b/c: A all-in (4 steps), recovers to 6. X (5 ready) attacking A: hold 6 (A 0 ready) gives 84% A down on 2 steps (25% on 1); hold 3 gives 28%; no hold gives 4.7%.
- t02: A spent 3 steps (9 of 16), not all-in, then held 4 of its 11. X's 2-step-OA death was a 53% roll.
- t03/t03y/t03z: fresh duel, A holds 8/6/0. X's best attack (2 steps) does 2.38/1.70/1.23 expected injury, 0% down. The hold is nearly free.
- t04: X stepped IN (7,2 -> 6,2), not back. The kill was a lucky roll (two 8s).
- t05 family: under exp-holds the walk past the greatsword or Fin-0 spear draws no OA. Placeholder: greatsword 1 step per square (3 OAs). Per-square: a 1-step OA from the 2nd square on.

## r02 / r02h: drained-target lock, 1v1
- A 3 steps, then hold. Options: 4 (keep 7), or 8 (keep 3). X has 4 ready, 5 HP, so a 1-step attack is its best and does 0% against A at 3+ ready. I chose 8.
- X options with hold 8: pay 9 (can't, has 4); leave unpaid (96.1% down); attack A (0%, 0.88 inj); stay (A's next 3-step: 64.1% down, then the same lock). With hold 4: leave = 53.1% down.

## r04 family: reach-2 pin
- r04 (seed 7): Z pokes 1 step, holds 13 (keeps 3). The 13 was chosen as X's ready, so the pay-off is 14 and unpayable; 4 OA steps fit 14. X can't reach Z and every move leaves a square in reach. X stepped in: 4-step OA (7.6% down) rolled two 8s, X down.
- r04s8 / r04s9 / r04s12: same, holds 14/14/13 (= X's ready). X steps in and loses 5/5/8 HP, keeping 3/4/0 ready. Z untouched with 2 ready; X's 1-step reply does 0%.
- r04n (seed 8, exp-0.11.0): X pays 1, keeps 13 against a 16-ready Z.
- r04w: X waits instead. Z gets all 14 tokens back, pokes 2 steps and re-holds 14. X is at 14 ready again with a pay-off of 15. Repeats indefinitely.
- r04y: ally Y reaches Z (Y need not pay: Z has no OA without a hold) and attacks; 3 steps = 93.2% down; Z went down.
- r04f: X first from 6 squares away. Walks in free (pay prompt is moot), attacks, holds Z with 7 (keeps 8) so that Z stepping back costs 8. r04g: Z first closes to 2, pokes, holds 14: pin.

## r06: two holders, 2v1
- A 2 steps (crit), holds 9 (keeps 6). B 2 steps drains X to 0. B's best is a second attack (100% down), not a hold. Holds irrelevant.

## r07 / r07b / r07c: lock with a fresh ally of the target in reach
- A 3 steps on X (7 HP), holds 4 (= X's ready; keeps 7). Y's 4-step on A: 81.0% down; without the hold (r07c), 39.7%. r07b (Y before X): Y downed A, hold ended. In r07 (X before Y), X's answer is to wait for Y.

## r08: held archer (blade drawn)
- X 1 step; C's solver block spent 10 of 14. X holds 10 (keeps 6). C's options: leave = 89.1% down; 2-step blade attack = 0%, 1.5 inj; point-blank shot = all 4 ready, then the same OA with 0 ready.

## r09 / r09n: held target shot at
- A holds X with 6. C shoots (12, 1 crit). Dodging would cost 1 dash + 7 pay-off = all 8 ready, so X stays: 4 HP. Placeholder: dodge for 2, 2 HP.

## r10 / r10a / r10n: rearguard
- B holds pursuer X with 8 (keeps 8); wounded A runs 6 west. X's choices: pay 9 and chase (best attack on A 15.6%), or hit B (4 steps, 70.6%). Placeholder: pay 1, chase, 95.0% on A.

## r11: split tokens
- A 3 steps drains X to 3. Y is fresh (12). Locking Y would need 12+, so A holds only X with 3 (keeps 8). X leaving = 67.2% down; Y's 3-step on A = 20.3%.
