# Testing the 0.10.0 ranged rules: engine plan

*Status: in progress (2026-11-11). It answers the project doc `claude/Sim_Requirements_Ranged_Package_2026-11-11.md` ("the requirements"). Paths are relative to `sim/src/stamina_engine/` unless they start with `sim/` or `rules/`. P1 and P5 are built; P2 to P4 follow, in that order.*

## Where things stand

The engine now plays packet 0.10.0 as the preset `v0.10.0` with the equipment table `v0_10` (engine pull request of 2026-11-11), and it's the baseline. Since the requirements were written, the designer ruled several of the questions they leave open, and `rules/` is the source of truth. So this plan only covers what 0.10.0 doesn't already settle.

| Requirement | After 0.10.0 | Left to build |
|---|---|---|
| R1 range bands | Linear bands, −2 per band, Finesse widens (odd values, so at most +3), Strength shortfall, no maximum range: all in `v0.10.0` | An optional maximum range switch. **Sizes (R1.3) are shelved** in *Not in This Version*, so S6's and S7's size parts wait |
| R2 bows, Piercing | The packet's four bows, Piercing (Hammer = 1, melee too) and Precise, in `v0_10` | The requirements' other shortbows (1d6, shot cost 2) as equipment overlays, for comparison only |
| R2.2 `crit_in_cap` | Ruled: the critical bonus comes after the limit | An "inside" variant, only if the designer wants it measured |
| R3 aim, shared counter | Shots and aim steps are actions on one counter; one free aim die; no Finesse on aim | A per-shot aim reset variant (R3.2), low priority |
| R4 crits on shots | Ruled: aim dice are never critical (configuration A) | C′ and C as variants (`crit.aim_dice_widen`, `crit.per_shot_cap`), only if the designer wants them compared |
| R5 reaction switches | Range, Melee vs Ranged Defense and cover are all judged after the reaction; point-blank OAs need the enemy in reach at declaration and at resolution | `defense_timing`, `reaction_purchase_cap`, `swap_requires_single_purchase`, so the "reaction changes cover only" package can be run against 0.10.0 |
| R6 agents | The tactical defender weighs every square by this shot's blocks; the tactical archer's aim counts the penalty at the target's square, the limit and Piercing | Most of R6: positional value of the reaction, the archer weighing the target's reaction, pursuers buying movement |
| R7 parity | Golden tests reproduce every 0.10.0 worked example; the exact shot distribution equals the roller's; parity with the study's solver (P5, done) | — |
| R8 step-by-step play | Not started | All of it |
| R9 scenarios, measures | Not started | All of it |

## Phases

The order follows the requirements' priority list, with the work 0.10.0 already did removed. Each phase ends at a gate: `pytest`, `mypy --strict` and `ruff` clean, and the `v0.10.0` digest and suites unchanged unless the phase says otherwise.

### P1. The remaining switches (small)

- **Reactions** (`rules/components/ranged.py`, `engine/procedures/ranged.py`):
  - `ranged.defense_timing = declaration | after_reaction`: whether Melee vs Ranged Defense is judged where the target was when the shot was declared. `ranged.range_measured` already covers range.
  - `ranged.reaction_purchase_cap`: 0 for no cap, or N purchases. Today a reaction may buy as many off-turn purchases as it can afford.
  - `ranged.swap_single_purchase`: the defense swap counts only if one purchase reached or left reach.
  - `ranged.max_bands`: 0 for no maximum.
- **Named packages** as presets built on `v0.10.0`, never changing it: `v0.10.0-cover-only` (declaration timings), plus the C′ and C crit variants if wanted.
- **Equipment overlays:** `v0_10_shortbow_d6` and `v0_10_shortbow_cost2`.
- **Gate:** a register row for each switch, marked pending designer; the defaults pinned; a golden test per switch with a constructed shot.

### P2. Step-by-step play for chats (R8)

This is the most useful piece. It lets design chats probe positions before the agents are good, and it doesn't depend on P3.

- **Mechanism:** the engine calls agents synchronously, so a step is a replay.
  - `se play --step --answers answers.jsonl` rebuilds the trial from its seed.
  - A `ReplayAgent` answers each controlled decision from the file in order.
  - At the first decision with no answer, the agent raises `AwaitDecision(request)`, which unwinds the battle. Nothing persists between runs except the answers file, so determinism (R8.5) is by construction. Fights take milliseconds, so replaying from the start is cheap.
- **Wire format:** a new `agents/wire.py`, with one JSON encoder per request type.
  - Each request carries the context path, kind, observation, options with prices, and an answer schema.
  - It reuses the request fields the engine already fills: cover, damage and defense for each destination, the aim limit, the range penalty.
  - Answers are parsed by the same validation `HumanAgent` uses, so an invalid answer gets a reason and isn't appended.
  - The map comes from `Battlefield.render` with combatant marks, as `se trace` draws it.
- **Exit codes:** 0 fight over; 10 awaiting a decision; 2 invalid answer.
- **Session log:** the existing `--log` format, with `seconds` null, so `se load --session` works unchanged.
- **Gate:** a test plays a full archer fight through the files alone; the same answers always produce the same next request (hash-compared); a bad answer is reported and isn't consumed; `USAGE_FOR_CHATS.md` gets a section.

### P3. Agents (R6)

Movement results depend on the agents more than on anything else, so every heuristic gets a register row and a constructed-position test.

- **Reaction value** (`agents/tactical.py`, `dive`). Today it's this shot's blocks less the move's cost. Add where the target ends up:
  - Ending adjacent to the shooter: the shooter's best next turn, found by a one-reply look-ahead like the archer's `_reply_cost`. Its options are to leave and provoke, pay to avoid, or shoot point blank against Melee Defense and provoke.
  - The stamina left for the target's own next turn, valued in the same units.
  - Optionally a parameter weight instead of the look-ahead, for sensitivity runs.
- **Archer aim** (`aim`). Take the expected value over the target's best reaction instead of assuming it stays.
  - The archer can see the target's reachable squares, and the engine's request fields say what each one does to the shot.
  - Cache the exact responses by (shot distribution, defense, penalty, limit), so the cost is aim counts × distinct outcomes, not squares.
  - Keep its step-out-of-reach move.
- **Pursuers** (tactical and scripted). Buy on-turn squares when that makes contact a turn earlier. Weigh the arrival stamina against the step thresholds: take them from `Pricing.max_steps` for the weapon, not hard-coded 5 / 9 / 14.
- **Gate:** each heuristic tested in a position where the right answer is known; both agent families run every scenario in P4 (R6.4).

### P4. Scenarios and measures (R9)

- **Scenarios S1–S5** as library scenarios on `v0.10.0` with `v0_10`: archer vs melee at 4 / 8 / 12 squares (sword-and-board and two-hander), with and without low walls; focus fire; normal-range lethality; bows against plate. S6 (Large beast) runs without the size rule until sizes come back.
- **New events** so the measures come straight from the log:
  - A `Reacted` event with a kind (stay, cover, close, back away) and its cost, classified by the engine from cover and reach before and after.
  - Crit dice per shot are already in `AttackRolled`; bands are in `RangePenalized`.
- **New row measures** (`experiments/metrics.py`):
  - any PC down by round 2;
  - down rate by target build;
  - archer stamina spent against HP dealt;
  - reactions by kind and cost;
  - rounds to contact;
  - the archer's turn-1 spend and reserve;
  - shots per band;
  - crit dice per shot;
  - point-blank OAs provoked and taken.
- **A suite** (`se suite ranged10`): scenarios × bows × reaction packages × crit variants × agent families, with `--workers`. The first report goes in `sim/reports/` with digests, switches, trial counts and confidence intervals.

### P5. Parity with the solver (R7)

R7.1 to R7.3 compare against `bows4.py` (sha256 12161ee521c9, in `claude/ranged_study/bundle_bows.txt`), which isn't in the repo.
- With its source checked in as a test-only oracle beside `sim/tests/oracle/`, the comparisons are exact-distribution tests like the existing ones. Use a test-only equipment table with the solver's bows, since the packet's shortbow differs from the solver's.
- R7.5's one-round harness is a small addition on `analysis/ranged.py`.

## The designer's answers (2026-11-11)

1. **Which open decisions get switches: left to the engine.** The test was whether the grid can say something the study's one-round solver couldn't, and what a switch costs.
   - **Built:**
     - the reaction switches (`ranged.defense_timing`, `ranged.reaction_purchases`, `ranged.swap_single_purchase`), since only fights on a map can test them;
     - crit rules C′ and C (`crit.aim_dice_widen`, `crit.per_shot_cap`) and `ranged.crit_in_limit`, since each is a few lines, the requirements ask for the scenarios under A, C′ and C, and the solver checks every one of them exactly.
   - **Named packages:** `v0.10.0-cover-only`, `v0.10.0-crit-c-prime` and `v0.10.0-crit-c`.
   - **Not built:**
     - the other shortbows (1d6, shot cost 2): the designer chose 1d4 and cost 3 after the solver runs;
     - the per-shot aim reset: the packet says the count carries across shots;
     - a maximum range: the packet says there is none;
     - a crit-widening cap: the Critical Range Table says a d4 at Finesse 5 always crits;
     - the band attribute: split attribute bonuses are shelved.
   - A chat can still try any of these as an equipment overlay or a plugin.
2. **Sizes: run without the size rule.** S6 uses a Large beast's numbers (armor 4, HP about 20) on an ordinary-size body.
3. **The solver:** used as a test-only oracle, `sim/tests/solver/bows5.py`, copied unchanged with its sha256 in the folder's README. The study bundle itself isn't in the repo.

## Done

- **P1:** the switches and packages above, with register rows, pinned defaults and golden tests (`tests/golden/test_ranged_switches.py`).
- **P5:** `tests/parity/test_bows_solver.py`. The engine matches the solver exactly on:
  - every shot distribution (R7.1: the packet's bows, aims 0–6, distance 0–40, rules A, B, C′ and C);
  - injury over R7.2's whole grid, with the critical bonus inside and outside the limit;
  - costs (R7.3).
- **R7.5:** `analysis.one_round.solve_round` plays one round of shooting with the engine's own pricing, distributions and blocks.
  - It matches the solver on every figure. The one exception is the aim count where aiming changes nothing.
  - It reproduces 38% / 6.2 HP (longbow against the caster) and 4% / 4.2 HP (warbow against plate).
