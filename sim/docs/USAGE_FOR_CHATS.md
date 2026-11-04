# Using the engine from a design chat

For claude.ai chats in the "Tactical fantasy TTRPG" project. Claude Code keeps this file current.

**Status:** milestones M0 (tag `m0`) and M1 (branch `m1-turn-engine`) are built: exact single-exchange calculators, plus whole fights with no grid (everyone adjacent), the review's five scripted policies, seeded runs, sweeps and paired comparisons. Movement, opportunity attacks and ranged fights arrive in M2 and M3.

## Reading the code

`rules/`, `design/` and `sim/` sync into the project automatically, so a chat can read them without cloning. Synced copies can lag behind GitHub; clone when the exact current code matters.

## Running it

```bash
git clone --depth 1 https://github.com/BenjaminTzudiker/TTriangulaRPG.git
cd TTriangulaRPG/sim
pip install -e . --break-system-packages
```

In a claude.ai chat, attach the repo first if the clone is refused. To reproduce a quoted result, check out the tag or commit its stamp names (`git fetch --depth 1 origin tag m1 && git checkout m1`).

## Commands

Run from `sim/`. With uv (`uv sync` once, then prefix commands with `uv run`), or after `pip install -e .`:

```bash
se table 1                                             # review Table 1, exact, packet rounding (half up)
se table 1 --ruleset review-sim --rounding half-even   # reproduces the review's printed Table 1
se table 8 --rounding half-even                        # review Table 8
se run src/stamina_engine/data/scenarios/l1_duel.toml --trials 2000 --workers 4
se compare src/stamina_engine/data/scenarios/one_v_three.toml --a v0.9 --b review-candidate
se sweep src/stamina_engine/data/scenarios/surcharge_sweep.toml --out results/surcharge
se suite parity --workers 8 --out reports/m1_parity.md # every published review fight, in lockstep
```

`--rounding half-even` reproduces the review, whose simulator used Python's `round()`. The packet's rounding is half up, which changes three Table 1 cells and Table 8's 2.125 (see the Assumptions register).

### Fights

A **scenario** names the combatants, their builds and agents, the RuleSet, the round cap, trials and seed. The format is documented at the top of `src/stamina_engine/experiments/scenario.py`; the examples are in `src/stamina_engine/data/scenarios/`. Agents are `alpha`, `fixed:2`, `reserve:5`, `chipkill`, `lookahead` or `never`, or a table such as `{ commit = "chipkill", target = "lowest_stamina", w = "3" }`; they block with the exact solver.

- `se run` prints win rates with 95% Wilson intervals, rounds, first-mover rate, winner-untouched rate, the loser's final HP, deaths and decisions per round, then the provenance stamp.
- `se compare` runs the same scenario under two RuleSets **on the same seeds** and reports each difference with a paired 95% interval. It is the cheapest honest way to test a rule change.
- `se sweep` runs scenarios × RuleSets × agent pairings (format at the top of `src/stamina_engine/experiments/sweep.py`); RuleSets in a sweep share seeds too.
- `--out DIR` writes Parquet tables (`runs`, `fights`, `attacks`, `decisions`); every row carries the run id and RuleSet digest, and `runs` holds the full stamp, the RuleSet TOML and the scenario TOML. Read them with Polars or pandas.
- Any fight re-runs alone: its seed is in the `fights` table, and `run_trial(scenario, trial)` replays it.

From Python:

```python
from stamina_engine.experiments.scenario import load_scenario
from stamina_engine.experiments.runner import run_scenario
from stamina_engine.experiments.metrics import summarize
from stamina_engine.experiments.sweep import compare
from stamina_engine.analysis.strike import mirror_strike   # the opening full strike, exactly

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

- **RuleSet** is the rules configuration: which variants, which parameters.
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

Grid commands (maps, movement, opportunity attacks) arrive with M2.
