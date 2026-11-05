# Movement, second pass: notes

Companion to `movement_ranged_exploration.md`. Written by the design chat on 2026-11-04 against `exp/movement` at b1d826c plus the agent and switch changes listed in the report's §7. Everything here is from `experiments_ranged_movement.py`, the scratch driver that finished its last cells after the detached runs were stopped (`finish_console.txt`), `se trace`, and the exact ranged tables in `analysis/ranged.py`; raw rows with Wilson intervals and stamps are in `movement_ranged_results/*.jsonl`. Agents only; no human play.

## 1. What was run

| Runner | Question | Rows | Trials |
|---|---|---|---|
| D1, D1x | First-mover edge by starting distance (1–15 apart) and movement rule: v0.9, capped, one square flat, one square escalating, extra movement as an action, none | 40 | 300 |
| K1a–d | Agility 5 kiter vs two Agility 0 brutes on the long field: by rule; by the kiter's run budget and shot reserve (v0.9); by the brutes' patience (`chase_spend`); run budget under capped and none | 20 | 300 |
| K1e | A gap-holding kiter (`kite_gap` = the brutes' one-turn reach + 1 under each rule), with and without a shot reserve; the same in the room | 12 | 300 |
| K2 | The same kiter vs light-armor brutes; vs Agility 2 brutes; the Agility 1 archer as kiter; one brute; vs two shielded sample fighters (K2e) | 17 | 300 |
| K3 | The room (three squares of floor behind the kiter), by rule | 4 | 300 |
| D1x-k | Kiting under "extra movement is an action" | 2 | 300 |
| R1 | A shooter against a target that never moves and only blocks (brute, light brute; 6 and 12 squares) | 4 | 300 |
| S1 | An archer with a fighter one or two squares in front of it, against two fighters eight squares off, under v0.9 and none; the screen tactical or holding | 8 | 300 |

Every variant of one scenario shares its trial seeds (the seed is built from the scenario name and the trial number, not the rules), so a variant whose rule never binds reproduces the baseline fights exactly: the capped rows equal v0.9 through 13 apart, and every rule gives the same fights at 3–7 apart.

## 2. Scenarios, builds and agents

- **Builds** (under `movement_ranged_results/builds/`, all `budget = "ignore"`):
  - `l1_kiter`: STR 1, AGI 5, FIN 3, fighter core, light armor; longbow (`bow`) and a quick-drawn shortsword (`blade`). Free movement 8, 4 squares per purchase, 13 stamina, HP 7, Ranged Defense 1, Melee Defense 3 with the bow in hand.
  - `l1_brute`: STR 4, AGI 0, FIN 1, heavy armor (3), greataxe two-handed (2d6 + 12 a step, base 3). Free movement 5, **1 square per purchase** (no odd Agility), 16 stamina, HP 10, Ranged Defense 1.
  - `l1_brute_light`: the same in light armor (1). `l1_brute_agi2`: the same with AGI 2 (free 6, 2 squares per purchase).
  - Library builds: `l1_sample` (the duels and the screen), `l1_archer` (AGI 1, FIN 2; the ordinary archer as kiter and the screened archer).
- **Maps** (under `movement_ranged_results/maps/`): `kite_field` 38×10 interior, brutes at column 2 (rows 5 and 7), kiter at column 18, so 16 apart with 20 squares of room east; `kite_room` 21×10, the same start with the east wall three squares behind the kiter; `open_32x10` for the duels (A at column 2, B at 2 + distance, row 6) and the screen.
- **Agents** (TOML in the script):
  - Kiter: `{ kind = "tactical", commit = "chipkill", kite = "distance", kite_spend = s, kite_gap = g, shot_reserve = r, retreat_engaged = 2 }`. `kite = "distance"`: after its shot (or instead of a shot it cannot afford with the reserve) it moves to the square farthest from the nearest melee enemy, buying movement and paying avoidance up to `kite_spend`; with `kite_gap` it takes the cheapest square at least that far away instead. A kiter caught with its blade out runs first and never trades blows by choice. It does not buy a shot that would be a certain miss (medium and long range need one and two aims it cannot afford).
  - Brutes: `{ kind = "tactical", commit = "chipkill", target = "nearest", chase_spend = c }`. `chase_spend = -1` (default, v1 behavior): buy movement to any attack square if at least one attack step stays affordable. `chase_spend = n`: only when the purchases and avoidance cost at most n.
  - Duels and the screen's enemies: `{ kind = "tactical", commit = "chipkill" }`. The holding screen: `hold = true, retreat_engaged = 9`.
- **Rule variants**: `movement.extra_cap = free_movement` (capped), `extra_squares = one` (one square flat), `extra_squares = one` + `extra_mode = escalating`, `extra_is_action = true` (new; see below), `extra_mode = none`.

## 3. The approach sweep, read with the agents in mind

The tactical pursuer buys movement to an attack square whenever one attack step is still affordable afterwards, and its commitment policy sizes the strike from the stamina left. Under v0.9 and the cap that is a reasonable approximation of play. Under one-square pricing and "extra movement is an action" it is not: at 11 apart under one-square escalating it pays 10 of 14 to arrive and poke once (first mover 7.4%); under "action" at 15 apart it pays 1 + 2 + 3 + 4 and then strikes into a surcharge of 4 (8.8%). A player would stop short of reach instead. So the low rows under steep rules are what a dasher gets, and the regime a non-dasher would reach is the one measured directly under "none", where no dash is possible: whoever ends its free move inside the other's free reach loses the first strike (27–30% for the first mover at 9–13 apart), and the parity flips with a 12-square period (73% at 15 apart, contact in round 2). Agents that stopped outside reach would stand off instead; nothing in the engine models that patience.

The cap row at 15 apart (37.8%, purchases 0.5 a fight) is the same phenomenon at its edge: the first mover cannot buy the last squares and ends inside reach.

Costs to contact for an Agility 1 fighter (free 6, 2 squares per purchase), from `Pricing.move_prices`:

| Squares to contact | v0.9 / capped | one square flat | one square escalating | extra as action (purchases only; the strike then costs +1 a step per purchase) |
|---|---|---|---|---|
| 8 | 1 | 2 | 3 | 1 |
| 10 | 2 | 4 | 10 | 3 |
| 12 | 3 | 6 | 21 | 6 |
| 14 | 4 / — | 8 | 36 | 10 |

Threat radius (squares a reach-1 creature can attack next turn) by stamina spent on movement, from the same call:

| Rule | AGI 0 (free 5) at 0 / 1 / 3 / 5 / 8 stamina | AGI 1 (free 6) | AGI 5 (free 8) |
|---|---|---|---|
| v0.9 | 6 / 7 / 9 / 11 / 14 | 7 / 9 / 13 / 17 / 23 | 9 / 13 / 21 / 29 / 31 |
| capped | 6 / 7 / 9 / 11 / 11 | 7 / 9 / 13 / 13 / 13 | 9 / 13 / 17 / 17 / 17 |
| one square flat | 6 / 7 / 9 / 11 / 14 | 7 / 8 / 10 / 12 / 15 | 9 / 10 / 12 / 14 / 17 |
| one square escalating | 6 / 7 / 8 / 8 / 9 | 7 / 8 / 9 / 9 / 10 | 9 / 10 / 11 / 11 / 12 |
| extra as action | 6 / 7 / 8 / 8 / 9 | 7 / 9 / 11 / 11 / 13 | 9 / 13 / 17 / 17 / 21 |
| none | 6 | 7 | 9 |

Under v0.9 an Agility 1 fighter with its pool intact threatens the whole of a 12×12 map; under the cap its radius is 13 and an Agility 0 brute's 11.

## 4. Traces behind the kiting reading

Scratch scenario files with the variant in the `ruleset` table; their seeds differ from the experiment rows (different scenario names).

**v0.9, kiter runs 2 a turn, no reserve.** Brute b1 wins initiative, pays 10 stamina for 10 purchased squares (5 free + 10 = 15, to adjacency from 16), and attacks one step for 3; the kiter blocks for 9 (1, 2, 3 + three grazes) and has 4 left, draws its blade in the window. On its turn (v1 agent) it attacked with the blade for 3 and was killed by the second brute; the kite-mode agent runs instead (1 avoidance + 1 purchase, 12 squares), the brute walks 5 free squares, the kiter redraws the bow and shoots at short range for 6, leaving 1, and is caught the next round. In every v0.9 trace the first contact is a 10–11 stamina sprint ending in a 3-stamina poke that costs the kiter 8–10 to block.

**Capped, kiter holds gap 12 (reserve 6).** The brutes never buy movement (10 squares is short of 16); they walk 5 a turn. The kiter shoots every turn (5 at short range when a brute closes within 8, 6 with one aim at medium), moves 1–5 free squares to keep the gap at 12, and downs a brute in round 4 of trial 0 (14 injury). In round 6 it reaches column 38 (the east wall), cannot keep the gap, and dies to a three-step greataxe strike (54 damage after 13 single-graze blocks). Trial 2 is the same shape: four shots, cornered in round 6, 20 damage. Twenty squares of room is five or six rounds of kiting.

**v0.9, kiter holds gap 20.** From adjacency the kiter runs 16 squares (8 free + 2 purchases) to column 34–37 and is caught against the wall in round 3–4; the gap it needs is the size of the room.

**None, kiter holds gap 7.** The brutes (reach 6) never arrive; the kiter circles. 85–89% of fights reach the 20-round cap (field and room alike).

## 5. The standing exchange and the screen

**R1.** The kiter against a brute that holds its square and only blocks, 6 and 12 squares apart, heavy and light armor: 100% down in one shot in all four cells (300 trials each). The tactical archer's aim policy takes three aims whenever nothing can reach it next turn (11 stamina; 33–44 expected injury against RD 1; the target spends 13–14 blocking). The cell was meant to measure the shot-versus-block exchange rate over a fight; it measures instead that a longbow with a free turn ends one. The per-shot exchange rates are the exact table in the report's §4.1.

**S1.** `l1_archer` at (4,6) with a sample fighter at (5,6) or (6,6), two sample fighters at (13,5) and (13,7), open 32×10. Under v0.9 the enemies' first turn is a walk around the screen (14–15 squares of on-turn movement a fight, 1.3–1.9 stamina bought) ending adjacent to the archer; the archer gets 0.4–0.7 shots. Under "none" they need two turns to get round a body (30–32 squares moved a fight), the archer shoots 2–3 times, and the party wins 83% with the tactical screen one square ahead. The holding screen is worse under both rules (4–6% vs 14–24% under v0.9; 23–57% vs 52–83% under none): a fighter that never steps forward threatens only the squares beside it, and the enemies pass on the far side. Opportunity attacks barely figure: the screen spends 0.0–0.5 stamina a fight on them and the enemies 0.0–0.7 on avoidance; at 1 a square, avoidance is paid when needed and the OA cap of 1 makes the attack itself not worth much.

## 6. Agent limitations

- **The pursuer dashes whenever one step remains affordable.** Right under v0.9 (the poke still forces an 8-stamina block), wrong under steep pricing, where it produces the 7–30% rows. No agent waits at mutual threat range.
- **The kiter's gap-holding mode under-performs the simple runner** (15–17% vs 42% under the cap): with a reserve it fires low-aim medium-range shots that heavy armor absorbs (6 injury over 3.9 shots), and at the brutes' exact reach + 1 any shortfall in reachable squares gets it caught. Read the simple runner's rows as the competent baseline.
- **The brutes never spread out** to cut off a runner, and `target = "nearest"` keeps them on the same side of it.
- **Cover from the other brute** (creatures grant half cover) shows up as `cover=1` on many of the kiter's shots and lowers their injury; a human kiter would step sideways first.
- **The standing exchange (R1)** uses the holding agent for the target, which blocks optimally but never closes; it measures the exchange rate, not a fight.

## 7. The new switch

`movement.extra_is_action` (default `false`): an extra on-turn purchase is priced as an action — its base plus the on-turn surcharge — and advances the surcharge, so after one purchase a base-2 strike's steps cost 3, 4, 5 and after two they cost 4, 5, 6. The packet rules extra movement is not an action (2026-11-01), so this is an experiment variant, in the Assumptions register as pending. `Track.EXTRA_MOVE_ACTION` advances both the purchase count (so the cap and escalating variants still work with it) and the action count. The tactical agent's commitment check uses stale trackers under this rule (it thinks the strike after a dash costs what it would without the dash), which is part of why the dasher rows are so low; the engine clamps the commitment to what is affordable.

## 8. Reproducing

```bash
cd sim
PYTHONPATH=src python3 -u experiments_ranged_movement.py K1 300    # also K1e, K2, K3, D1, D1x, R1, S1
PYTHONPATH=src python3 -m pytest -q                                 # fast suite
```

Each results row carries `digest`, `stamp`, `trials`, per-team stamina by category (`spent:<team>:<category>`), squares moved on and off turn, and, for cells run with `events`, injury dealt per team and melee hits landed on each team from the first 100 trials' event logs.
