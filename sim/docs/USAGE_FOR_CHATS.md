# Using the engine from a design chat

For claude.ai chats in the "Tactical fantasy TTRPG" project. Claude Code keeps this file current.

**Status:** milestones M0–M5 are done (tags `m0`–`m5`): the turn engine, maps and movement, opportunity attacks, ranged attacks, cover and diving, drawing weapons, equipment variant tables, NPC profiles, fleeing and surrendering, the full phase suite, class cores and candidate abilities with strain, playing a side yourself, and the load report. M5's gate still needs one session played by a person.

## Reading the code

`rules/`, `design/` and `sim/` sync into the project automatically, so a chat can read them without cloning. Synced copies can lag behind GitHub; clone when the exact current code matters.

## Running it

```bash
git clone --depth 1 https://github.com/BenjaminTzudiker/TTriangulaRPG.git
cd TTriangulaRPG/sim
pip install -e . --break-system-packages   # add [parquet], as in '.[parquet]', for --out
```

**No PyPI? Install nothing.** The engine and its CLI use only the standard library (Python 3.12 or newer), so a chat that can't reach PyPI runs them straight from the checkout:

```bash
cd TTriangulaRPG/sim
export PYTHONPATH=src
python3 -m stamina_engine table 1   # every se command works this way
python3 -m pytest                   # needs pytest; the property tests skip without hypothesis
```

Only `--out` (Parquet tables) needs a package, pyarrow; without it, `--out` says so and everything else runs. From Python, `invoke(["table", "1"]).output` (from `stamina_engine.cli`) runs any command and returns its output.

In a claude.ai chat, attach the repo first if the clone is refused. To reproduce a quoted result, check out the tag or commit its stamp names (`git fetch --depth 1 origin tag m1 && git checkout m1`).

## Commands

Run from `sim/`. With uv (`uv sync` once, then prefix commands with `uv run`), after `pip install -e .`, or with nothing installed as `python3 -m stamina_engine` in place of `se` (with `PYTHONPATH=src`):

```bash
se table 1                                             # review Table 1, exact, packet rounding (half up)
se table 1 --ruleset review-sim --rounding half-even   # reproduces the review's printed Table 1
se table 8 --rounding half-even                        # review Table 8
se run src/stamina_engine/data/scenarios/l1_duel.toml --trials 2000 --workers 4
se compare src/stamina_engine/data/scenarios/one_v_three.toml --a v0.9 --b review-candidate
se sweep src/stamina_engine/data/scenarios/surcharge_sweep.toml --out results/surcharge
se suite parity --workers 8 --out reports/m1_parity.md # every published review fight, in lockstep
se map list                                            # library maps
se map show corridor                                   # a map with coordinates and spawns
se run src/stamina_engine/data/scenarios/one_v_three_corridor.toml --trials 500 --workers 4
se trace src/stamina_engine/data/scenarios/one_v_three_corridor.toml --trial 0
se suite positioning --workers 8 --out reports/m2_positioning.md
se table 5                                             # review Table 5, exactly, beside the review's figures
se table 5 --ruleset my_f3_idea.toml                   # the same single shots under your variant
se suite ranged --workers 8 --out reports/m3_ranged.md # archers on three maps, F3 options
se suite phase --workers 8 --out reports/phase_suite.md # all eight phase-suite items, review layouts
se table 8 --equipment f8_die_upgrades                 # an exact table with a variant equipment table
se suite cores --workers 8 --out reports/cores_suite.md # each core and candidate ability, off and on
se suite objectives --workers 8 --out reports/objectives_o1_suite.md # O1: objective scenarios, kill v first
se play src/stamina_engine/data/scenarios/l1_duel_open.toml --as A --log session.jsonl
se load src/stamina_engine/data/scenarios/one_v_three_open.toml --trials 200
se load --session session.jsonl                        # a person's decisions, with seconds
```

### Equipment variants and NPC profiles (M4)

A scenario's `equipment = "f4_shield_1"` swaps the weapon, armor and shield table for a variant in `src/stamina_engine/data/equipment/` (each overlays the packet's table entry by entry; copy one to try your own). The shipped variants are Review F8's (die upgrades, Strength capped at die size) and F4's (a +1/+2 shield, a shield with a Strength requirement); F8's light-weapon discount and F4's two-hander bonus are RuleSet switches (`surcharge.light_exempt`, `defenses.two_hander_bonus`, `defenses.agility_split`).

NPC profiles (`src/stamina_engine/data/profiles/`) configure the tactical agent the way a stat block would: `agent = { kind = "npc", profile = "disciplined_2step" }` commits 2 steps, 3 against a target below half stamina, and focuses fire. `cautious` flees through an exit square (`>` on a map) at half HP and surrenders at a quarter. Fleeing and surrendering aren't in the packet; they're engine end states pending the designer (Assumptions register).

### Objectives (O1)

A scenario on a map can give one side an objective other than downing every opponent, with `[[zone]]` and `[[objective]]` tables (format at the top of `src/stamina_engine/experiments/scenario.py`):
- `reach`: get `count` creatures into a zone;
- `escape`: get `count` creatures off the map through exits (`>`);
- `hold`: control a zone, by a `control` reading (`present`, `uncontested`, `majority`) and a `score` reading (`consecutive`, `cumulative`, `final`) that the scenario must state.

Every objective has a `deadline` round. The fight ends when the objective is done (its side wins, reason `objective:<id>`), fails (the other side wins, `objective_failed:<id>`), or one side is out first (`side_out`). `se run` then also prints the objective's success rate and how fights ended. A zone can be a map letter that no combatant uses (`marker = "H"`), a list of squares or a rectangle.

Agents ignore objectives unless their spec says `objective = "first"` (the default `"kill"` is today's behaviour and the control). `se suite objectives` runs the five objective scenarios (`extraction_3v3`, `breakthrough_3v3`, `hold_hill_3v3`, `hold_hill_final_3v3`, `hold_the_door_1v3`) under both agent families, pursuers in `kill` and in `first`, and reports the paired first − kill difference: if it is near zero, the objective adds nothing a straight fight doesn't already decide. The readings the packet doesn't give are in the Assumptions register; the plan is `sim/docs/OBJECTIVES_PLAN.md`.

#### Setting up an objective scenario that tells you something

The engine measures whatever fight you give it. An objective only produces an insight if the scenario makes the objective hard in the way your question is about. If you put an escape on open ground with the exits in reach, you've measured a footrace. Work through these before trusting a number:

1. **Start from the question, then choose the objective.** Name the rule or finding you're probing, and pick the objective and terrain that put pressure on it. For example:
   - opportunity attacks and reach (F9): a breakthrough through a gap a defender can stand in;
   - focus fire (F6): a lone defender holding a corridor;
   - retreat economics (Review Addendum 2): an escape that has to break contact, with pursuers able to reach the route;
   - stamina banking: a hold scored only at the deadline (`score = "final"`).
2. **Use the current movement rules.** The `v0.9` preset predates packet v0.9.1, so its extra on-turn purchase moves 1 + odd Agility squares. The packet now moves 1 square per purchase. For current movement, use `ruleset = { base = "v0.9", movement = { extra_squares = "one" } }`. Some other v0.9.1 changes (for example the removed opportunity-attack cap) aren't in the engine yet; `rules/CHANGELOG.md` says which with an *Engine:* note. Movement decides most objective fights, so this matters more here than anywhere else.
3. **Do the movement arithmetic.** Under current rules a creature covers its free Movement (5, +1 per odd Agility) plus 1 square per stamina it spends, all on its own turn. It can also move off-turn, at escalating prices. With `se map show <map>`, measure each pursuer's distance to the goal and each denier's distance to the intercept squares.
   - If a pursuer can reach the goal on its first turn before any denier can engage it, the fight is a race decided by initiative.
   - That is a fine thing to measure on purpose, but not by accident.
   - To get a contest, put the deniers between the pursuers and the goal, give the route a chokepoint, or start the goal further away.
4. **Give terrain a job.** Corridors, gaps in a wall, low walls and pillars make position matter. Open ground makes most objectives a matter of speed and numbers.
   - Spread the deniers so that every route passes through someone's reach.
   - Give the deniers a reason to choose between positions, such as two gaps and three defenders.
5. **Set the deadline from the movement arithmetic.** Make it long enough that the objective takes several turns, and short enough that turtling fails. A reach or escape deadline defaults to the round cap.
6. **Choose the hold readings deliberately.**
   - `present` lets a single body hold against any number of enemies.
   - `uncontested` lets one enemy deny the hold by standing in the zone.
   - `majority` rewards numbers.
   - `consecutive` punishes losing the zone even once; `final` lets a side fight elsewhere and arrive late.
   These change the answer, so say which you used.
7. **Balance the straight fight first.** Run the scenario with the pursuers in `kill` mode. If one side wins the straight fight almost every time, the objective has little room to matter. In the hill scenario, the party loses the straight fight 96% of the time, and 85–97% of its hold fights end with one side wiped out. Adjust the sides or the map until the straight fight is roughly even, or until its imbalance is the thing you're studying.
8. **Read how fights ended, not just who won.**
   - Mostly `side_out`: the objective isn't deciding the encounter.
   - Mostly round 1: a race.
   - Mostly `objective_failed` well before the deadline: the pursuers are being wiped out, not outplayed on the objective.
   Then `se trace` a few trials of each kind of ending before you believe the pattern.
9. **Run both agent families, and know their limits.**
   - Scripted pursuers move with free movement only and never buy squares.
   - Tactical pursuers buy up to half their stamina.
   - Deniers of either family attack the pursuer nearest its goal; they don't body-block gaps.
   A result that holds for only one family, or that a blocking denier would plausibly overturn, is about the agents, not the rules.
10. **Compare rules on the same seeds.**
    - `se compare` (or suite rows that share a scenario) gives paired differences.
    - `first − kill` tells you whether the objective matters at all.
    - Comparing RuleSet variants with the pursuers in `first` tells you how a rule changes the objective.

### Abilities, people and load (M5)

A build's cores bring their abilities (`cores = ["barbarian"]` gives it `barbarian_core`), and `abilities = ["heavy_swing"]` adds candidate abilities (`heavy_swing`, `riposte`, `tactical_withdrawal`; Feint waits for contests). The library has the sample fighter's stats with each core (`l1_sample` is the Fighter, `l1_barbarian`, `l1_monk`, `l1_rogue`) and with each candidate alone (`l1_heavy_swing`, `l1_withdrawal`, `l1_riposte`). How each one reads where the packet is silent is in the Assumptions register; `src/stamina_engine/abilities/cores.py` shows how one is written. Strain starts at 0 every fight, so a fight's results are the best case for a day of several.

Engine agents pass every ability window unless their spec says `abilities = "use"`, so results without abilities stay comparable; the heuristics they then follow are documented in `src/stamina_engine/agents/ability_policy.py`. `se suite cores` prices each ability by turning it off and on over the same seeds, in duels and one against three, and plays the four cores against each other.

`se play scenario.toml --as ID` lets you play one combatant at the keyboard; everyone else keeps the scenario's agent, and the dice are trial N's, so the fight is comparable with the engine's. Each prompt lists the options with their prices (`?` shows the answer formats). Every decision is timed, and `--log` writes the session as JSON lines. `se load` reports decision load (Review F11): requests per creature-round by kind, their option counts, how many are non-trivial, how often they did something, dice per attack, and, from session logs, seconds per decision.

`--rounding half-even` reproduces the review, whose simulator used Python's `round()`. The packet's rounding is half up, which changes three Table 1 cells and Table 8's 2.125 (see the Assumptions register).

### Fights

A **scenario** names the combatants, their builds and agents, the RuleSet, the round cap, trials and seed. The format is documented at the top of `src/stamina_engine/experiments/scenario.py`; the examples are in `src/stamina_engine/data/scenarios/`. Agents are `alpha`, `fixed:2`, `reserve:5`, `chipkill`, `lookahead` or `never`, or a table such as `{ commit = "chipkill", target = "lowest_stamina", w = "3" }`; they block with the exact solver. Add `abilities = "use"` to a table to have it use its abilities.

- `se run` prints win rates with 95% Wilson intervals, rounds, first-mover rate, winner-untouched rate, the loser's final HP, deaths and decisions per round, then the provenance stamp.
- `se compare` runs the same scenario under two RuleSets **on the same seeds** and reports each difference with a paired 95% interval. It is the cheapest honest way to test a rule change.
- `se sweep` runs scenarios × RuleSets × agent pairings (format at the top of `src/stamina_engine/experiments/sweep.py`); RuleSets in a sweep share seeds too.
- `--out DIR` writes Parquet tables (`runs`, `fights`, `attacks`, `decisions`); every row carries the run id and RuleSet digest, and `runs` holds the full stamp, the RuleSet TOML and the scenario TOML. Read them with Polars or pandas.
- Any fight re-runs alone: its seed is in the `fights` table, and `run_trial(scenario, trial)` replays it. `se trace scenario.toml --trial N` prints that fight's events with the board at each turn; read one before trusting a surprising number.

### Maps and positioning (M2)

A scenario with `map = "open_12x12"` (a library map in `src/stamina_engine/data/maps/`, or a `.txt` path) is fought on a grid; without one, everyone is adjacent, as in M1 and the review. Map legend: `.` floor, `#` wall, `=` low wall or crate, `o` pillar; other letters and digits are spawn markers. Each combatant gets `spawn = "A"` (a marker) or `spawn = [x, y]`; a counted group takes a list. `map_text = """..."""` puts the map inline.

On a grid, movement is square by square: free movement, then extra purchases (1 stamina, flat) on your turn; off-turn purchases (escalating) in the window after every turn. Leaving a threatened square provokes an opportunity attack from each enemy threatening it unless the mover pays to avoid it. Every reading the packet leaves open (corners, reach lines, what threatens, window order, the per-square cap and the F9/F10/F14 options) is a switch in the Assumptions register in `sim/docs/ENGINE_PLAN.md`.

Agents on a grid:
- **Scripted** (`alpha`, `chipkill`, ...): approach their target with free movement, attack if they can, never move off-turn. Add `avoid = "worth_it" | "always" | "never"` and `oa = "max" | "never"` to a table spec.
- **Tactical** (`"tactical"`, or `{ kind = "tactical", commit = "fixed:2", target = "lowest_stamina" }`): picks squares by how many enemies could engage it, keeps reach-weapon spacing, retreats off-turn when two or more could engage it (`retreat_engaged`) or when engaged with low stamina (`low_stamina = "1/3"`), and values avoidance exactly.

At range (M3), a creature with a bow shoots enemies within its long range that aren't in total cover. Cover is the 5e corner method; the target may dive for cover with off-turn movement after the roll; a shooter within an enemy's reach provokes from every enemy threatening it. Scripted shooters take `aims = 3` (a spec field) and stand; tactical archers choose aims by exact expected value (looking one enemy reply ahead), step out of reach, ready a quick-draw blade between turns and dive. Builds with several loadouts (`l1_archer`: `bow` and `blade`) switch with the packet's drawing costs.

Report positional results for both families: agent behavior can drive a result as much as the rules do. The variant switches Phases 4 and 5 ask about:

```toml
[ruleset]
base = "v0.9"
opportunity = { cap_rule = "weapon_base" }       # F9 option 1: cap = weapon base + odd FIN
# opportunity = { avoid_price = "attacker_cap" } # F9 option 2
# opportunity = { avoid_track = "off_turn" }     # F9 option 3 (or "off_turn_only")
# opportunity = { per_square_cap = true }        # the packet's optional rule
# opportunity = { avoid_debt = true }            # F14: avoidance paid from the next recovery
# movement = { extra_squares = "one" }           # F10 option 1
# movement = { extra_cap = "free_movement" }     # F10 option 2
# off_turn = { order = "descending_initiative" } # F14: who moves first after a turn
# defenses = { ranged_mode = "dodge_folded" }    # F3 option 1: RD gains even Agility
# blocks = { ranged_flat = 2 }                   # F3 option 2: flat ranged perfect blocks
# ranged = { aim_mode = "precision" }            # F3 option 3: aim widens crit range instead
# ranged = { bands = "minus_d6" }                # F11 (b): range bands as -1d6 / -2d6
# crit = { aim_dice_can_crit = false }           # the packet's TODO
```

From Python:

```python
from stamina_engine.experiments.scenario import load_scenario
from stamina_engine.experiments.runner import run_scenario
from stamina_engine.experiments.metrics import summarize
from stamina_engine.experiments.sweep import compare
from stamina_engine.analysis.strike import mirror_strike   # the opening full strike, exactly
from stamina_engine.analysis.retreat import escape, table  # Addendum 2 retreat costs, exactly

s = load_scenario("src/stamina_engine/data/scenarios/l1_duel.toml")
print("\n".join(summarize(run_scenario(s, trials=500).fights).lines()))
```

The core pieces for single exchanges:

```python
from stamina_engine.rules.ruleset import preset, load_ruleset   # presets: "v0.9", "review-candidate", "review-sim"
from stamina_engine.model.build import load_build        # library builds in src/stamina_engine/data/builds
from stamina_engine.model.derive import derive           # Build x RuleSet -> CombatProfile
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.block_solver import best_block, cheapest_zero_injury
from stamina_engine.analysis import dist                 # exact (total, crit dice) distributions
from stamina_engine.provenance import collect            # the stamp to quote with results

rules = preset("v0.9")
fighter = derive(load_build("l1_sample"), rules)
Pricing(rules).melee_attack(base=2, steps=3).total      # 9
print(collect(rules).text())
```

`review-sim` reproduces the review's simulator, quirks included; use `v0.9` (or your variant) for design questions. `uv run pytest` takes under a minute; `uv run pytest -m slow` adds the full-count oracle parity runs.

## Trying a rule change

Never edit the baseline: not the v0.9 components, not the presets, not `rules/`. The baseline is what you compare against, and only the designer changes it. Try ideas as **new, named variants** instead. That keeps the old and new rules side by side in one run, and keeps every result honest about which rules produced it. Pick the lightest of three tiers that fits:

1. **Numbers or an existing variant: no code.** Override parameters in a RuleSet file:

   ```toml
   # steep.toml
   [ruleset]
   base = "v0.9"
   name = "steep-surcharge"
   surcharge = { slope = 2 }
   blocks = { slope_num = 1, slope_den = 2 }   # perfect blocks 1, 1, 2, 2, 3...
   ```

   Run with `se table 8 --ruleset steep.toml`, or `load_ruleset("steep.toml")` in Python. `sim/docs/ENGINE_PLAN.md` lists every component and its parameters; the source is in `src/stamina_engine/rules/components/`.

2. **A new mechanism that fits a component: one plugin file.** Write a variant class in a file outside the package, registered under a new name starting with `exp_`. The working example is `examples/exp_quadratic_surcharge.py` with `examples/exp_quadratic_surcharge.toml`:

   ```python
   from dataclasses import dataclass

   from stamina_engine.rules.components.surcharge import SurchargeRule
   from stamina_engine.rules.registry import register


   @register("surcharge", "exp_quadratic")
   @dataclass(frozen=True)
   class QuadraticSurcharge(SurchargeRule):
       slope: int = 1

       def surcharge(self, prior_actions: int) -> int:
           return self.slope * prior_actions * prior_actions
   ```

   ```bash
   se table 8 --plugin examples/exp_quadratic_surcharge.py --ruleset examples/exp_quadratic_surcharge.toml
   ```

   In Python, call `load_plugin("my_idea.py")` (from `stamina_engine.rules.plugins`) before loading a RuleSet that names its variants. Subclass the kind's base class (`CritRule`, `BlockRule`, `DefenseRule`...): it supplies the methods to implement and the packet citations. Taking a name that already exists is refused, so a plugin can't quietly replace a rule.

3. **A change to a procedure or timing** (a new reaction window, a new kind of action): this needs engine code. Work in your clone, on a branch named `exp/<topic>`. Run the baseline from the same commit before your change, so both sides differ only by your diff. Say in the report that the idea needed a procedure change; Claude Code can then add a component for it, so the next idea like it fits tier 2.

If the designer wants to keep an idea, Claude Code moves it into the engine as a proper component with tests. Ideas the designer rejects are deleted, or kept for parity only if a published result depends on them.

## Reporting results

Every `se` command prints a provenance stamp after its result; in Python, `collect(rules, plugins).text()` gives the same lines. For example:

```text
RuleSet exp-quadratic-surcharge 509a51df050e
Code git m0 (f57367eb5d62, clean); source ee6c5479eb85; stamina-engine 0.0.1
Plugin exp_quadratic_surcharge.py 9460148edc70: surcharge/exp_quadratic
```

- **RuleSet** is the rules configuration: which variants, which parameters. Parameters left at their default don't enter the digest, so a digest stays the same as the engine gains new switches. Digests stamped at tags `m0`–`m5` hashed every parameter and differ from today's for the same rules: v0.9 was `89e49ba8c42d` at `m5` and is `3bf6fc070dbf` now.
- **source** hashes the engine's code and data tables. It identifies the implementation even outside git, in an unpacked copy or with uncommitted edits. "uncommitted changes" means that copy's code differs from the commit shown.
- **Plugin** lines hash each plugin file.

Quote the whole stamp with every number, plus trial counts and confidence intervals for anything simulated (`se run` and `se compare` print both). Attach plugin files and RuleSet files to the report, so anyone can rerun it. Write-ups go in `sim/reports/`. The report, not the branch, is what lasts.

## Sharing changes

A chat can push only if the Claude GitHub App has access to this repo.
- With access: push experiments to `exp/<topic>` branches, never to `main`. Small, safe changes (scenarios, maps, builds, reports) can go to `main`. Engine procedure and rule component changes go on a branch with a pull request.
- Without access: hand over the report, plus the plugin or RuleSet files or a patch, for Claude Code or the designer to commit.

## Rules for chats

- Read `CLAUDE.md` at the repo root before changing anything. Its ground rules apply to chats too.
- Never change what a rule means. Experiments are new named variants, never edits to the baseline. If the packet is unclear, flag it and add it to the Assumptions register in `sim/docs/ENGINE_PLAN.md`.
- Quote every number with its full provenance stamp.
