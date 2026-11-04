# Movement exploration: notes

Companion to `movement_exploration.md`. Written by the design chat on 2026-11-04 against `main` = 7bd1bb8 plus the `exp/movement` changes (patch attached to the report). Everything here is from `experiments_movement.py`, `window_race.py`, `window_load.py` and `se trace`, run from source with `PYTHONPATH=src`; raw rows with 95% Wilson intervals and the provenance stamp are in `movement_exploration_results/*.jsonl`, console logs beside them. Engine agents only; no human play.

Treat the fight numbers as measurements of the rules *as these agents play them*. Each point in the report names the agent behavior it depends on; the list of agent limitations is at the end of this file.

## 1. What was run

| Runner | Question | Scenarios | Rows | Trials |
|---|---|---|---|---|
| `window_race.py` | What the window order does when two creatures contest one window | one neutral turn, a fleer F and a pinner P with fixed budgets (deterministic) | 54 | — |
| B1 | Window order in fights | duel 8 apart (both retreat+pin), duel (pin vs flee), archer vs pinning fighter, 1v3 open and corridor (fleeing D vs pinning attackers), retreat line 2v2 | 5 orders × 6 | 400 |
| B1n | The same with no on-turn extra movement | archer (pinning and plain fighter), retreat line, duel both fleeing | 4 orders × 4 | 400 |
| B2 / B2rest | On-turn extra movement variants | archer open and scattered cover, duel 8 and 10 apart, retreat line, 1v3 open and corridor | 6 variants × 7 | 400 |
| B2x | The cost dial (flat, escalating slope 1 and 2, free 5, free 4, one-square escalating, none) | archer open, duel 8, retreat line, 2v2 | 7 × 4 | 400 |
| B3 | Terrain (a, b), counts (c), Agility (d) | 1v3 on open / corner / pillars / door / corridor; 1v1…3v4 open; AGI 5 defender in corridor and door | 56 | 300 |
| B3e | A defender that holds its square | 1v3 open / corner / door / corridor mouth / corridor one square in; 2v3 holders | 14 | 300 |
| B3f | Does the diagonal-corner rule make the door a chokepoint? | 1v3 door, holder and tactical defender, `grid.corners` = `no_squeeze` / `no_cut` | 4 | 300 |
| `window_load.py` | Prompts per round | duel, 1v3 open and corridor, archer, retreat line, 3v3 × (v0.9, not-after-allies, no extra, declaration scheme) | 24 | 150 |

Every variant of one scenario shares its trial seeds (the trial seed derives from the scenario seed, the scenario name and the trial number, never from the RuleSet), so differences between variants are paired, and a variant whose rule never binds reproduces the baseline fights exactly: "capped at Movement" equals v0.9 in every statistic, and at 7 squares to contact every priced variant but "free 4" plays the same fights.

## 2. Scenarios, builds and agents

- **Builds.** `l1_sample` (STR 2, AGI 1, FIN 1, medium armor and shield: HP 8, stamina 14, free movement 6, 2 squares per purchase) for every melee creature; `l1_archer` for the archer. `builds/l1_agi5.toml` (STR 2, AGI 5, FIN 1, medium + shield; free 8, 4 per purchase, Melee Defense 5) for B3d.
- **Maps.** `open_12x12`; `archer_open` (A at column 2, F at column 14 of a 17-wide room: 12 apart, 11 squares to contact); `archer_cover`; `corridor` (open 7×7 room on the left, a one-wide corridor from (8,4) to (14,4) with a dead end; D spawns at the mouth (8,4), attackers 1–3 six squares west); `retreat_line` (fleer F in front, ally A six squares back at (4,4), chasers C and B); and three inline maps in `experiments_movement.py`: `CORNER_MAP` (D in the top-left corner, attackers along the west wall), `PILLARS_MAP` (a grid of `o` pillars), `DOOR_MAP` (a wall at column 7 with a one-square gap at (7,6); D at (8,6) directly behind it; attackers at (1,5)–(1,7)).
- **Agents** (TOML specs in the script):
  - `TACT` = `{ kind = "tactical", commit = "chipkill" }`: the M2 tactical agent.
  - `TACT_FLEE` adds `retreat_engaged = 1, low_stamina = "1/2"`: retreats off-turn when engaged by one or more and below half stamina.
  - `TACT_PIN` adds `off_turn = "retreat_pin"`: when its target is out of reach after a turn ends, buys the cheapest route to a square that threatens it, spending up to `pin_budget` (default half its stamina).
  - `TACT_PIN_FLEE`: both.
  - `HOLD_NORETREAT` = `{ kind = "tactical", commit = "chipkill", hold = true, retreat_engaged = 9 }`: never moves on its turn; attacks whatever is in reach; never retreats off-turn.
  - `fixed:2`: the scripted two-step attacker (approaches with free movement, never moves off-turn).
  - Retreat-line chasers: `{ kind = "tactical", commit = "alpha", target = "first" }` (B2/B2x) or the same with `off_turn = "pin"` (B1/B1n).
- **Rule variants** are `RuleSet.override` tables, named in each results row (`label`, `digest`): `off_turn.order`, `off_turn.restart_after_move`, `off_turn.purchase_cap`, `off_turn.scope`, `movement.extra_mode`, `movement.extra_slope`, `movement.extra_squares`, `movement.extra_cap`, `movement.free_base`, `grid.corners`. "Windows OFF" is the existing `off_turn.windows = false` switch.

## 3. Traces behind the arrival-budget reading (§3 of the report)

`se trace` on scenario files written to a scratch folder with the variant in the `ruleset` table. Those files carry their own scenario names, so their seeds differ from each other and from the experiment rows: these are illustrative fights, not paired ones.

**Archer, v0.9, fighter wins initiative (trials 0 and 8).** F buys three purchases (1, 1, 1), moves 11 squares, attacks with three steps (parts 2, 3, 4 = 9; the move counts as a prior action), and has 2 stamina left. Trial 0: 46 damage with crits, archer dead on turn 1. Trial 8: 13 damage, archer incapacitated.

**Archer, escalating slope 2, archer wins initiative (trials 0 and 8).** A fires a three-aim volley at medium range (parts 5, 1, 2, 3 = 11; 2 stamina left). F blocks for 13 (1, 2, 3, 4 + three grazes) and has 1 left; trial 0: 8 damage leaks, F incapacitated at once. Trial 8: F walks six free squares to distance 6, A shoots again at short range for 6, F blocks with 5 single grazes and dies.

**Archer, free 4 + escalating.** Fighter first (trials 1, 2): F pays 1 + 2 + 3 + 4 = 10 to move 11 squares, arrives with 4, attacks with one step (2); A blocks for 3, steps away with one avoidance and shoots at short range. F still won both (8 and 6 rounds) but without the opening blow. Archer first (trials 0, 3, 5, 8): the three-aim volley costs F 9–12 in blocks; with 2–5 stamina F walks 4 free squares to distance 8; A shoots again at short range; F closes on turn 2 for 3 (1 + 2) and attacks once for 2. Trial 8: the second volley leaks 10 into a fighter with 0 stamina, dead on round 2.

**Duel 10 apart, one-square escalating, first mover (trials 0 and 1).** The first mover pays 1 + 2 + 3 = 6 for the last three squares, arrives with 8, strikes two steps (5), has 3 left. The defender blocks for 3 (trial 0) or 7 (trial 1) and answers with a three-step (9) or two-step strike into the near-empty pool.

**Duel 10 apart, v0.9 (trials 0 and 1).** The first mover pays 1 + 1 = 2, arrives with 12, strikes two steps (5) and has 7 left to block the reply. Trial 1 shows the defender's side of it: it blocks the arrival strike for 11 (1, 2, 3, 4 + graze), pokes once, and dies on round 2 to a three-step strike — the first mover's untouched win.

Pricing check (from `Pricing.move_prices` for AGI 1, free 6, 2 squares per purchase; AGI 5 free 8, 4 per purchase): the §3.1 table of the report was produced by this call, not by hand.

## 4. Why the door is not a corridor (§4.2)

`grid.corners` (assumptions register, pending designer) decides whether a diagonal step past a wall corner is legal. The engine default `no_squeeze` blocks a diagonal only when *both* orthogonal neighbours are tall terrain. In `DOOR_MAP` an attacker standing in the gap (7,6) wants (8,5), beside the defender at (8,6). The two orthogonal neighbours of that step are (8,6), the defender's square (a creature never blocks a diagonal), and (7,5), a wall: one wall, so the step is legal, and the second and third attackers flank the defender within a round. Under `no_cut` (blocked if either neighbour is tall) the only square adjacent to the defender that an attacker can reach is the gap itself, and the door plays like the corridor one square in:

| Door, 1v3, 300 trials | Attackers win | Draws | Median rounds | Deaths / fight |
|---|---|---|---|---|
| holder, `no_squeeze` (default) | 100% | 0% | 2 | 0.457 |
| holder, `no_cut` | 64.7% [59.1, 69.9] | 35.3% | 9 | 0.190 |
| tactical D, `no_squeeze` | 100% | 0% | 2 | 0.393 |
| tactical D, `no_cut` | 93.0% [89.5, 95.4] | 7.0% | 5 | 0.277 |

RuleSet digests: `3bf6fc070dbf` (v0.9) and `33ed3f912b30` (`grid.corners = no_cut`). The corridor-one-square-in holder row is 63.7% / 36.3% / 8 / 0.180 for comparison.

Cutting the corner also matters for the corridor mouth: under `no_squeeze` the mouth square (8,4) is adjacent to three open squares, (7,3), (7,4) and (7,5), so three attackers engage; one square in, only (8,4) is adjacent.

## 5. Agent limitations that bound these results

- **The tactical defender leaves terrain to attack.** Its turn heuristic approaches the target with the fewest engagers; from a corridor or doorway that means stepping out. The `hold` option (never move on your turn) was added to measure what the terrain is worth to a disciplined defender. No agent decides *when* to hold and when to step out.
- **The pin heuristic is a losing trade on open ground.** Closing off-turn costs the pinner as much as the fleer and is undone on the fleer's turn; the fighter that pins wins 31% of archer fights against 47% without (B1n-a vs B1n-b). Treat pin rows as "what pinning does", not "what a good player would do".
- **Fleeing agents loop.** With no on-turn extra movement, two agents set to flee when engaged retreat six squares after the enemy's turn and walk six back on their own (18–24 off-turn squares a fight in B1n-d). The first-mover figures of that row measure the loop.
- **No agent waits-then-reacts in a window, kites pre-emptively, or rotates attackers out of a chokepoint.** The declaration scheme's advantage for the higher-initiative creature (pre-empt or react) is therefore unmeasured in fights; `window_race.py` measures it with hand-written reactors.
- **The archer never backs off before the fighter's approach**, only after being engaged. A kiting archer would be uncatchable on an unbounded field under the "none" variant and hard to catch under free 4.
- **`fixed:2` attackers never move off-turn** and never rotate; they queue behind the one engaging the holder.

## 6. Reproducing

```bash
cd sim
PYTHONPATH=src python3 -u experiments_movement.py B1 400        # also B1n, B2, B2rest, B2x, B3, B3e, B3f
PYTHONPATH=src python3 window_race.py  > reports/movement_exploration_results/window_race.txt
PYTHONPATH=src python3 window_load.py  > reports/movement_exploration_results/load_console.txt
PYTHONPATH=src python3 -m pytest -q    # fast suite; test_no_hypothesis.py fails only in a source-only checkout
```

Each results row carries `digest` (RuleSet, 12 hex digits), `stamp` (code git, source hash) and `trials`. Wall time on the chat's container, from the `seconds` field of the rows: B1 12 min, B1n 5, B2 (with B2rest) 11, B2x 12, B3 20, B3e 2, B3f 1.
