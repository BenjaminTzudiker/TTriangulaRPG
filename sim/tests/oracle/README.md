# Oracle: the original review simulator

These four files are the simulator used for the v0.9 review, copied unmodified. Do not edit them.

- `sim.py`: rules, block choice, policies and `make_fighter` builds. Variant knobs are module globals: `STEP_SLOPE`, `BLOCK_SLOPE`, `CRIT_MODE`.
- `experiments.py`: the review's main tables (static costs, duels, 1v3, ranged, archer, armored vs unarmored, weapon efficiency, w sensitivity).
- `variants.py`: the shape-change variants (A, B, A+B, C, D) in review Table 9.
- `grid.py`: the configuration grid in the review's Addendum.

The scripts write `results.txt` and `variants.log` into the current directory when run, so run them from a scratch folder, not from here.
