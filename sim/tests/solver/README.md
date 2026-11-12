# The ranged solver (test-only oracle)

`bows5.py` is the project's exact one-round ranged solver, copied unchanged from the design
study's bundle (`bows/bows5.py`, addendum 6; sha256 `0c0cbdadab42`). It extends `bows4.py`
(sha256 `12161ee521c9`, which the simulator requirements of 2026-11-11 name) with
`max_shots` and `cap_floor`, which the shortbow's Precise needs; for every `bows4` setting
it computes the same thing.

It's a parity oracle, not rules, and it isn't in the engine. `tests/parity/test_bows_solver.py`
compares it with the engine's shot distribution, injury, costs and the one-round harness
(`stamina_engine.analysis.one_round`). Never edit it: if the study's solver changes, copy
the new file beside it under its own name.

Its module-level switches (`INCAP`, `AP`) are set by `solve`; tests that call `injury`
directly set and restore them.
