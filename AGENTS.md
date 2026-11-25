# TTriangulaRPG

A tactical fantasy TTRPG built on a regenerating stamina system, plus a Python rules engine (`sim/`) that measures how rule variants play on a 5 ft grid. The engine is a measuring instrument for the designer, not a playable product.

This file is the working guide for anyone changing the repo: coding agents of any kind (most read `AGENTS.md` on their own), design chats and people.

## Where things are

- `rules/` is the rules text, one Obsidian note per rule. It is authoritative for what the engine implements.
  - `rules/Playtest Packet.md` is the index and reading order; `rules/README.md` describes the layout and formatting.
  - `rules/CHANGELOG.md` records every rules change. Its Unreleased section is what has changed since the last packet version.
- `design/` holds the supporting documents:
  - `Fix_Order_and_Dependencies.md`: what each of the v0.9 review's findings (F1–F14) depends on and ripples to, the original fix order (Phases 0–8), and an index of the findings with where each stands now (section 10).
  - `Design_Notes_for_Design_Bible.md` and `Rules_Reconciliation_Ledger_v0.8-to-v0.9.md`: why the rules are the way they are. Ledger IDs (MV-3, CB-2…) are cited in code.
  - `Instructions_for_Design_Chats.md`: how any assistant helping with design (not code) should work. Read it before answering a design question.
- `sim/docs/ENGINE_PLAN.md` is the engine's architecture and milestone plan. Follow it; propose changes to it rather than drifting from it.
- `sim/docs/USAGE_FOR_CHATS.md` tells design chats how to install and run the engine, when a run is worth doing, and what the engine doesn't capture. Keep its "What the engine doesn't capture" section current when a milestone closes a gap (e.g. the campaign layer, packet 0.10.0, the search auditor).
- `archive/` holds frozen records that don't sync to the claude.ai project. `archive/design/Review_Playtest_Packet_v0.9.md` is the v0.9 review, the findings the engine exists to test; `sim/tests/properties/test_traceability.py` reads it, so keep its finding and addendum headings unchanged.
- `sim/tests/oracle/` holds the simulator from the original review. Never edit it. It is the parity oracle.
- `sim/reports/` is where experiment write-ups for the designer go.
- `sim/examples/` holds the worked plugin example design chats copy when they try a new mechanism (see `USAGE_FOR_CHATS.md`).

`rules/`, `design/` and `sim/` sync into the claude.ai project "Tactical fantasy TTRPG", so design chats there see what is pushed here. Other tools work from a clone of the repo.

Paths that start with `claude/` (`claude/Hold_Rule_Study_2026-11-17.md`), cited throughout `design/`, `sim/docs/` and the changelog, are working docs in that claude.ai project, not files in this repo. If you can't open one, say so; never guess what it says.

## Ground rules

1. **Never change what a rule means.** Rules change only when the designer decides. If the packet is silent, ambiguous or TODO, add the question to the Assumptions register in `sim/docs/ENGINE_PLAN.md`, implement the reading as a named switch, and say so in your summary. Never pick a silent default.
2. **Every stamina cost comes from `Pricing`.** Agents and the engine both call it.
3. **All state changes go through `StateOps`.** No other code writes battle state.
4. **Variants are RuleSet components selected in config.** No `if ruleset.name == ...` or similar branching in procedures.
5. **The engine never decides for a creature.** Every choice is a typed decision request answered by an agent.
6. **Cite the rule.** Each rule component and procedure declares `cites = ("Packet: <section>", "Ledger <ID>")`. `<section>` is a rules note's name or a heading inside one.
7. **Deterministic.** Same seed and config, same event log. Never use the global `random` module in engine code; use the seeded streams from `core/`.

## Working on the rules

- Before reasoning about a rule or changing one, compile the packet (`python3 tools/check_rules.py --compile packet.md` from the repo root) and read all of it. Rules interact, and one note is never the whole picture.
- A rules change updates every restatement of the rule in the same commit, as "Changing a rule" in `rules/README.md` describes.

## Conventions

- Python 3.12, `src/` layout under `sim/`, frozen dataclasses for rules and profiles.
- `mypy --strict` clean, `ruff` clean, `pytest` green before any milestone is called done.
- Integer arithmetic for all game math. The packet's "round" means round half up.
- Engine code imports only the standard library (pyarrow only inside `--out`), so chats that can't reach PyPI run it with `PYTHONPATH=src python3 -m stamina_engine`. Tests that need an optional package skip without it.
- The baseline preset is `BASELINE` in `rules/ruleset.py` (`v0.12.0`, packet 0.12.0, ruled 2026-11-24). Its equipment is the `v0_12` table (0.10.0's bows and shield, plus 0.11.1's two-handed spear reach): a scenario or table that names no equipment gets its RuleSet's own (`model.derive.equipment_for`). Scenarios, suites and defaults use it; tests that reproduce the review name `v0.9`, and the parity suite uses `review-sim`.
- A released component default never changes: the RuleSet digest leaves defaults out, so changing one would change rules under an unchanged digest. Set a new value in the preset instead; `tests/golden/component_defaults.json` pins them.

## Commands

Run from `sim/`:

```bash
uv sync                       # install (or nothing: PYTHONPATH=src python3 -m stamina_engine ...)
uv run pytest                 # fast tests (under a minute)
uv run pytest -m slow         # full-count oracle parity and long differentials
uv run pytest tests/golden    # packet worked examples only
uv run mypy src
uv run ruff check src tests examples
uv run se suite parity --workers 8   # M1 parity report (lockstep with the oracle)
uv run se suite positioning --workers 8   # M2 grid scenarios across agent families
uv run se suite ranged --workers 8        # M3 archers on three maps, Table 5, F3 options
uv run se suite phase --workers 8         # M4 the full phase suite in the review's layouts
uv run se suite cores --workers 8         # M5 class cores and candidate abilities, off and on
uv run se suite objectives --workers 8    # O1 objective scenarios, pursuers kill v first
uv run se trace <scenario.toml> --trial N # one fight, with the board at each turn
uv run se play <scenario.toml> --as ID --log session.jsonl  # play one side yourself, timed
uv run se load <scenario.toml>            # decision load per round (or --session logs)
```

Run from the repo root:

```bash
python3 tools/check_rules.py                      # rules notes: links resolve, titles match, index reaches every note
python3 tools/check_rules.py --compile packet.md  # the whole packet as one Markdown file (gitignored)
python3 tools/check_rules.py --nav                # regenerate prev/next/up and Full Packet from the index
```

## Git workflow

- Start every session with `git pull`. Design chats and other agents may push to this repo too.
- Ask the designer before your first push in a session, unless they've already said to push. Once you may push, commit in small steps and push when tests pass, so chats always see current code.
- Small, safe changes (scenarios, maps, builds, reports, bug fixes that keep tests green) can go straight to `main`. Changes to engine procedures or rule components go on a branch with a pull request.
- Experiments from design chats live on `exp/<topic>` branches or as plugin files beside a report, never in the baseline. Promote one to a real component (with tests and citations) only when the designer asks; delete rejected variants unless a published result needs them for parity.
- Rules and design doc changes come from the designer: write a decision into `rules/` or `design/` only once the designer has made it, and commit it only with their go-ahead. Update `rules/` in the same commit as the engine changes that implement a rules change.
- A packet version in progress lives on a `rules/v<version>` branch (for example `rules/v0.11.5`) until it's merged, so `main` can be behind the current rules.
- **Every commit that changes `rules/` adds a line to `rules/CHANGELOG.md` under Unreleased, in the same commit**, in the format at the top of that file. This includes the designer's own edits you commit for them.
  - If a change alters what a rule means, it goes under Rules, never Clarified.
  - If you don't know why a change was made, write *Why: not recorded.* and ask the designer; never invent a reason.
  - The `rules` workflow fails any push that changes `rules/` without touching the changelog. `[no changelog]` in a commit message skips it, for typo-only fixes.
- After adding, removing or reordering notes in the index, run `python3 tools/check_rules.py --nav` to regenerate the reading-order links.
- Rename or move a rules note only with every link and engine `cites` string that names it updated. `python3 tools/check_rules.py` and `uv run pytest tests/properties/test_traceability.py` catch misses.
- Keep `sim/docs/USAGE_FOR_CHATS.md` current whenever commands or install steps change.
- Tag each finished milestone (`m0`, `m1`…) so results can name the code that produced them.

## Working on milestones

Work one milestone at a time (M0–M5 in `sim/docs/ENGINE_PLAN.md`). Plan first, then build. A milestone is done only when its "Done when" gate passes. M0–M5 are merged and tagged (`m0`–`m5`). M5's gate still needs one human session, played by the designer (`se play`, then `se load --session`). The optional M6 (search auditor, replay viewer) is built only if agent quality or playtest review calls for it.

When a result looks like a design finding (a rule behaving differently than the packet intends), write it up in `sim/reports/` with the RuleSet digest, the assumption switches used, trial counts and confidence intervals, and stop to flag it. Don't fix the rules to make the numbers look better.

## The oracle

`sim/tests/oracle/sim.py` uses module-level globals (`STEP_SLOPE`, `BLOCK_SLOPE`, `CRIT_MODE`) as variant knobs. Tests that touch it must set them explicitly and restore them afterwards. Known quirks to reproduce under the `review-sim` preset, not in the default rules:

- Initiative ties go to the first-listed combatant (stable sort).
- Linear crit modes add their bonus even when nothing gets past armor.
- Duels and the 1v3 runs have no off-turn movement or opportunity attacks.
- The heavy-armor builds apply Strength penalties by hand in `make_fighter`.
