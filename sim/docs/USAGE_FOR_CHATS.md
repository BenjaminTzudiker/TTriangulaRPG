# Using the engine from a design chat

For claude.ai chats in the "Tactical fantasy TTRPG" project. Claude Code keeps this file current.

**Status:** milestone M0 (Foundations) is built on branch `m0-foundations`: dice, RuleSets, builds and derived numbers, Pricing, single-attack resolution, the block solver and the exact static tables. There is no battle loop yet (M1).

## Reading the code

`rules/`, `design/` and `sim/` sync into the project automatically, so a chat can read them without cloning. Synced copies can lag behind GitHub; clone when the exact current code matters.

## Running it

```bash
git clone --depth 1 https://github.com/BenjaminTzudiker/TTriangulaRPG.git
cd TTriangulaRPG/sim
pip install -e . --break-system-packages
```

In a claude.ai chat, attach the repo first if the clone is refused. To reproduce a quoted result, check out the tag it names (`git fetch --depth 1 origin tag m1 && git checkout m1`).

## Changing it

A chat can push only if the Claude GitHub App has access to this repo. Without that, a chat makes the change in its own clone and hands it over as a patch or files for Claude Code or the designer to commit.

## Rules for chats

- Read `CLAUDE.md` at the repo root before changing anything. Its ground rules apply to chats too.
- Never change what a rule means. If the packet is unclear, flag it and add it to the Assumptions register in `sim/docs/ENGINE_PLAN.md`.
- Quote every number with its RuleSet digest, assumption switches, trial count and confidence interval, and the tag or commit it came from.
- Small, safe changes (scenarios, maps, builds, reports) can go to `main`. Engine procedure and rule component changes go on a branch with a pull request.

## Commands

Run from `sim/`. With uv (`uv sync` once, then prefix commands with `uv run`), or after `pip install -e .`:

```bash
se table 1                                        # review Table 1, exact, v0.9 rounding (half up)
se table 1 --ruleset review-sim --rounding half-even   # reproduces the review's printed Table 1
se table 8 --rounding half-even                   # review Table 8
```

Every table prints the RuleSet name and digest and the rounding it used; quote those with any number. `--rounding half-even` reproduces the review, whose simulator used Python's `round()`. The packet's rounding is half up, which changes three Table 1 cells and Table 8's 2.125 (see the Assumptions register).

From Python, the pieces a chat is most likely to want:

```python
from stamina_engine.rules.ruleset import preset          # "v0.9", "review-candidate", "review-sim"
from stamina_engine.model.build import load_build        # library builds in src/stamina_engine/data/builds
from stamina_engine.model.derive import derive           # Build x RuleSet -> CombatProfile
from stamina_engine.rules.pricing import Pricing, Trackers
from stamina_engine.rules.block_solver import best_block, cheapest_zero_injury
from stamina_engine.analysis import dist                 # exact (total, crit dice) distributions

rules = preset("v0.9")
fighter = derive(load_build("l1_sample"), rules)
Pricing(rules).melee_attack(base=2, steps=3).total      # 9
```

Variants: `preset("v0.9").override({"surcharge": {"slope": 2}}, name="mine")`, or a TOML file with `[ruleset] base = "v0.9"` and one table per changed component.

`se run`, `se sweep` and `se suite` arrive with later milestones.
