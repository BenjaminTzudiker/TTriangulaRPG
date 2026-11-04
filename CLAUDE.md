# TTriangulaRPG

A tactical fantasy TTRPG built on a regenerating stamina system, plus a Python rules engine (`sim/`) that measures how rule variants play on a 5 ft grid. The engine is a measuring instrument for the designer, not a playable product.

## Where things are

- `rules/Playtest_Packet_v0.9.md` is the rules text. It is authoritative for what the engine implements.
- `design/` holds the supporting documents:
  - `Review_Playtest_Packet_v0.9.md`: the findings (F1–F14) the engine exists to test.
  - `Fix_Order_and_Dependencies.md`: the order those findings get fixed (Phases 0–8).
  - `Design_Notes_for_Design_Bible.md` and `Rules_Reconciliation_Ledger_v0.8-to-v0.9.md`: why the rules are the way they are. Ledger IDs (MV-3, CB-2…) are cited in code.
- `sim/docs/ENGINE_PLAN.md` is the engine's architecture and milestone plan. Follow it; propose changes to it rather than drifting from it.
- `sim/docs/USAGE_FOR_CHATS.md` tells design chats how to install and run the engine.
- `sim/tests/oracle/` holds the simulator from the original review. Never edit it. It is the parity oracle.
- `sim/reports/` is where experiment write-ups for the designer go.
- `sim/examples/` holds the worked plugin example design chats copy when they try a new mechanism (see `USAGE_FOR_CHATS.md`).

`rules/`, `design/` and `sim/` sync into the claude.ai project "Tactical fantasy TTRPG", so design chats see what is pushed here.

## Ground rules

1. **Never change what a rule means.** Rules change only when the designer decides. If the packet is silent, ambiguous or TODO, add the question to the Assumptions register in `sim/docs/ENGINE_PLAN.md`, implement the reading as a named switch, and say so in your summary. Never pick a silent default.
2. **Every stamina cost comes from `Pricing`.** Agents and the engine both call it.
3. **All state changes go through `StateOps`.** No other code writes battle state.
4. **Variants are RuleSet components selected in config.** No `if ruleset.name == ...` or similar branching in procedures.
5. **The engine never decides for a creature.** Every choice is a typed decision request answered by an agent.
6. **Cite the rule.** Each rule component and procedure declares `cites = ("Packet: <section>", "Ledger <ID>")`.
7. **Deterministic.** Same seed and config, same event log. Never use the global `random` module in engine code; use the seeded streams from `core/`.

## Conventions

- Python 3.12, `src/` layout under `sim/`, frozen dataclasses for rules and profiles.
- `mypy --strict` clean, `ruff` clean, `pytest` green before any milestone is called done.
- Integer arithmetic for all game math. The packet's "round" means round half up.

## Commands

Run from `sim/`:

```bash
uv sync                       # install
uv run pytest                 # fast tests (under a minute)
uv run pytest -m slow         # full-count oracle parity and long differentials
uv run pytest tests/golden    # packet worked examples only
uv run mypy src
uv run ruff check src tests examples
uv run se suite parity --workers 8   # M1 parity report (lockstep with the oracle)
uv run se suite positioning --workers 8   # M2 grid scenarios across agent families
uv run se suite ranged --workers 8        # M3 archers on three maps, Table 5, F3 options
uv run se trace <scenario.toml> --trial N # one fight, with the board at each turn
```

## Git workflow

- Start every session with `git pull`. Design chats in the claude.ai project may push to this repo too.
- Commit in small steps and push when tests pass, so chats always see current code.
- Small, safe changes (scenarios, maps, builds, reports, bug fixes that keep tests green) can go straight to `main`. Changes to engine procedures or rule components go on a branch with a pull request.
- Experiments from design chats live on `exp/<topic>` branches or as plugin files beside a report, never in the baseline. Promote one to a real component (with tests and citations) only when the designer asks; delete rejected variants unless a published result needs them for parity.
- Rules or design doc changes come from the designer. Update `rules/` in the same commit as the engine changes that implement a rules change.
- Keep `sim/docs/USAGE_FOR_CHATS.md` current whenever commands or install steps change.
- Tag each finished milestone (`m0`, `m1`…) so results can name the code that produced them.

## Working on milestones

Work one milestone at a time (M0–M5 in `sim/docs/ENGINE_PLAN.md`). Plan first, then build. A milestone is done only when its "Done when" gate passes. Current milestone: **M2 Grid and positioning**. M0 and M1 are done (tags `m0`, `m1`).

When a result looks like a design finding (a rule behaving differently than the packet intends), write it up in `sim/reports/` with the RuleSet digest, the assumption switches used, trial counts and confidence intervals, and stop to flag it. Don't fix the rules to make the numbers look better.

## The oracle

`sim/tests/oracle/sim.py` uses module-level globals (`STEP_SLOPE`, `BLOCK_SLOPE`, `CRIT_MODE`) as variant knobs. Tests that touch it must set them explicitly and restore them afterwards. Known quirks to reproduce under the `review-sim` preset, not in the default rules:

- Initiative ties go to the first-listed combatant (stable sort).
- Linear crit modes add their bonus even when nothing gets past armor.
- Duels and the 1v3 runs have no off-turn movement or opportunity attacks.
- The heavy-armor builds apply Strength penalties by hand in `make_fighter`.
