# Testing the 0.10.0 ranged rules: engine plan

*Status: built (2026-11-11). It answers the project doc `claude/Sim_Requirements_Ranged_Package_2026-11-11.md` ("the requirements"). Paths are relative to `sim/src/stamina_engine/` unless they start with `sim/` or `rules/`. The first results are in `sim/reports/ranged10_first_run.md`.*

## What 0.10.0 already settled

The engine plays packet 0.10.0 as the preset `v0.10.0` with the equipment table `v0_10`, and it's the baseline. The designer ruled several questions the requirements leave open, and `rules/` is the source of truth. So this plan covers only what 0.10.0 doesn't settle.

| Requirement | Settled by 0.10.0 | Built here |
|---|---|---|
| R1 range bands | Linear bands, −2 per band, Finesse widening, Strength shortfall, no maximum range | — (sizes are shelved) |
| R2 bows, Piercing | The four bows, Piercing (Hammer = 1, melee too), Precise | — |
| R2.2 `crit_in_cap` | The bonus comes after the limit | `ranged.crit_in_limit` |
| R3 aim, shared counter | One counter, one free aim die, no Finesse on aim | — |
| R4 crits on shots | Aim dice never crit (rule A) | C′ and C: `crit.aim_dice_widen`, `crit.per_shot_cap` |
| R5 reactions | Range, defense and cover judged after the reaction; point-blank OAs need reach at declaration and resolution | `ranged.defense_timing`, `ranged.reaction_purchases`, `ranged.swap_single_purchase`; the `v0.10.0-cover-only` package |
| R6 agents | — | `buy`, `close`, `reaction`, `approach_weight`, `aim` agent fields |
| R7 parity | Golden tests of every worked example | Exact parity with the study's solver |
| R8 step-by-step play | — | `se play --step` |
| R9 scenarios, measures | — | S1–S6, the ranged measures, `se suite ranged10` |

## The designer's answers (2026-11-11)

1. **Which open decisions get switches: left to the engine.** The test was whether the grid can say something the study's one-round solver couldn't, and what a switch costs.
   - **Built:**
     - the reaction switches, since only fights on a map can test them;
     - crit rules C′ and C and `ranged.crit_in_limit`, since each is a few lines, the requirements ask for the scenarios under A, C′ and C, and the solver checks every one exactly.
   - **Not built:**
     - the other shortbows (1d6, shot cost 2): the designer chose 1d4 and cost 3 after the solver runs;
     - the per-shot aim reset: the packet says the count carries across shots;
     - a maximum range: the packet says there is none;
     - a crit-widening cap: the Critical Range Table says a d4 at Finesse 5 always crits;
     - the band attribute: split attribute bonuses are shelved.
   - A chat can still try any of these as an equipment overlay or a plugin.
2. **Sizes: run without the size rule.** S6's beast is a stand-in: armor 4 but HP 14, since the engine has no stat blocks.
3. **The solver:** used as a test-only oracle, `sim/tests/solver/bows5.py`, copied unchanged with its sha256 in the folder's README. The study bundle itself isn't in the repo.

## What was built

### P1. Switches and packages

- **The switches** (each has an Assumptions register row, marked pending designer):
  - `ranged.defense_timing`;
  - `ranged.reaction_purchases`;
  - `ranged.swap_single_purchase` (purchases counted from the move's length);
  - `ranged.crit_in_limit`;
  - `crit.aim_dice_widen` and `crit.per_shot_cap` (shots only).
- **Presets:** `v0.10.0-cover-only`, `v0.10.0-crit-c-prime` and `v0.10.0-crit-c`. None is a packet version.
- **Tests:** `tests/golden/test_ranged_switches.py`, a constructed shot per switch.

### P2. Step-by-step play (`se play --step`)

- **How a command runs.** Each command replays the trial from its seed with the answers file and prints the next decision as JSON: context, observation, options with prices, answer help, `se play`'s prompt, the map, and the events since the last decision.
- **Answers.** They're `se play`'s typed lines, checked by the same agent and by the broker's checks before the battle sees them.
  - `--answer` appends one only if the engine accepts it.
  - Exit codes: 10 awaiting, 0 over, 11 invalid (2 was taken by usage errors).
- **Session log.** `--log` at the end writes the session log, untimed. Several `--as` share one file.
- **Code and tests:** `experiments/step.py`, `agents/wire.py`, `tests/properties/test_step.py`.

### P3. Agents (R6)

All of these are opt-in agent spec fields, so every earlier result reproduces. The suite turns them on. Each is tested in a constructed position (`tests/golden/test_ranged_agents.py`).

- **`buy`** (scripted and tactical): buying on-turn squares to attack this turn.
  - `keep_steps` buys only if the commitment policy still makes as many steps: the policy's step costs are the thresholds, so nothing is hard-coded at 5 / 9 / 14.
  - `any` buys if one step is left (the tactical default).
  - `never` is the scripted default.
- **`close = off_turn`** (tactical): in the window right before its turn, buy off-turn squares so its free movement reaches the target.
- **`reaction = position`** (tactical): a reaction also values where it ends.
  - Contact with the shooter is worth the shooter's cheapest answer next turn: paying 1 to leave, or taking the opportunity attack. That's the one-reply look-ahead.
  - `approach_weight` adds a value per square closer. Its default of 0 is a sensitivity knob; the suite uses 1, an on-turn square's price.
  - The stamina left for the target's own next turn isn't valued yet.
- **`aim = reaction`** (tactical archer): the expected value over the target's best reaction to each roll.
  - Every square one off-turn move reaches is grouped by what it makes the shot face (defense, penalty, price), and dominated groups are dropped.
  - The target's off-turn track is taken as fresh, since the archer can't see it.

### P4. Scenarios, measures, suite (R9)

- **Scenarios:** `s1_archer_v_melee` to `s6_archers_v_beast`, on the maps `range_open`, `range_walls` and `range_party`.
  - The bow archers are over the level-1 budget at their bows' attributes, as in the study.
  - S7 (the Small target) waits for sizes.
- **Events:** `Reacted` (close, cover, back or shift; squares; cost) and `PointBlankProvoked`. They're measures only: without them every earlier log is unchanged.
- **Measures:** every fight row carries `metrics.ranged_measures`, the requirements' list.
- **Suite:** `se suite ranged10`, 88 rows. It varies distance, bow, melee build, reaction package, crit rule and agent family, and ends with a sensitivity group for `approach_weight`.

### P5. Parity with the solver (R7)

`tests/parity/test_bows_solver.py` checks the engine against `tests/solver/bows5.py`, a superset of the `bows4.py` the requirements name. The engine matches it exactly on:
- every shot distribution (aims 0–6, distance 0–40, rules A, B, C′ and C);
- injury over R7.2's whole grid, with the bonus inside and outside the limit;
- costs.

`analysis.one_round.solve_round` matches its one-round game on every figure, except the aim count where aiming changes nothing. It also reproduces 38% / 6.2 HP and 4% / 4.2 HP (R7.5).

## Still open

- **The target's stamina for its own turn** isn't in the reaction's value, so the tactical target may spend stamina it then lacks on its turn.
- **Monster stat blocks** (S6's HP 20) and **sizes** (S6, S7).
- **The scripted family's archers** never react or weigh reactions: they're the floor, not a second strategy.
