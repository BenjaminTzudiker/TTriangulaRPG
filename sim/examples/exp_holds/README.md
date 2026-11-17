# exp/holds: the hold rule (designer's rulings of 2026-11-17)

Experiment branch, not baseline. Presets added in `rules/ruleset.py` (none is the baseline):

- `exp-0.11.0`: packet 0.11.0's movement on 0.10.1 (one escalation, dash as an action, a dash
  phase before every turn with the highest in initiative first, and the placeholder opportunity
  attack: one step at base).
- `exp-holds`: exp-0.11.0 plus the hold rule as ruled.
- `exp-holds-per-square`: exp-holds with the cap added per unpaid square left in reach.

Readings the engine makes that the rulings don't settle: holds are set after recovering;
leftover tokens stay out until the holder's next turn; a hold ends when its holder goes down;
a wound clamps ready stamina first, then idle tokens, then live holds.

## Hand play

`table.py` replays a fight from an orders file and stops at each decision with exact odds
(blocks are automatic, by the block solver). `BRIEF.md` is the rules digest and order syntax
given to the players; `REDTEAM.md` is the red team's brief. Run from a fight folder:

    cd fights/r1 && python3 ../../table.py rg_holds        # or copy go.sh and table.py in

Fights played (orders and players' notes in `fights/`):

- `r1/rg_holds`, `r1/rg_placeholder`: rearguard, 6 sample fighters, same seed, both rule sets.
- `b1/br_holds`: all-melee 3v3 brawl (sample, greatsword, Finesse-0 spear per side).
- `m1/sc_holds`: two fighters screening an archer against three fighters (stopped in round 5).
- `rt/`: the red team's small constructed cases (each .py starts with what it tests).
- `v2/`: a runner passing a guard in a corridor, three rule sets x three guard weapons.

## Exact solvers (C, no dependencies: `gcc -O3 -o pin2 pin2.c -lm`)

- `pin2.c`: one round, N equal sample fighters attacking one on an open line (keys at the top;
  `HREC`, `HMAX`, `PAYALL` added for the variants). `pin.c` is the version the first results
  came from.
- `pursuit.c`: one pursuer and one fleer on a line, several rounds; the fleer may also attack.
