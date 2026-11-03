# Using the engine from a design chat

For claude.ai chats in the "Tactical fantasy TTRPG" project. Claude Code keeps this file current.

**Status:** nothing to run yet. Milestone M0 (Foundations) is not built.

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

To be added as milestones land (`se table`, `se run`, `se sweep`, `se suite`).
