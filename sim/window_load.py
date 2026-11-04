# ruff: noqa: E501
"""Off-turn window load: how often windows are opened, how many creatures are asked, how often
anyone moves, per scenario and rule variant. From the decision logs of run_scenario.

Run from sim/ with PYTHONPATH=src: python3 window_load.py [trials]"""

import importlib.util
import sys
from collections import Counter

from stamina_engine.experiments.runner import run_scenario

sys.argv = sys.argv[:1] + ["none"] + sys.argv[1:]
spec = importlib.util.spec_from_file_location("em", "experiments_movement.py")
em = importlib.util.module_from_spec(spec)
spec.loader.exec_module(em)

TRIALS = int(sys.argv[2]) if len(sys.argv) > 2 else 150


def load(text: str, overrides: dict, label: str) -> None:
    s = em.toml_scenario(text).with_rules(em.rules_for(overrides))
    res = run_scenario(s, trials=TRIALS)
    asked = acted = 0
    windows: dict[tuple, bool] = {}
    rounds = sum(int(f["rounds"]) for f in res.fights)
    kinds = Counter()
    for d in res.decisions:
        kinds[d["kind"]] += 1
        if d["kind"] == "off_turn_move":
            asked += 1
            key = (d["trial"], d["context"])
            moved = bool(d["acted"])
            acted += moved
            windows[key] = windows.get(key, False) or moved
    n_windows = len(windows)
    moved_windows = sum(1 for v in windows.values() if v)
    print(f"  {label:48s} windows/round {n_windows / rounds:4.1f} | asked/round {asked / rounds:5.1f} | "
          f"moved {acted / max(1, asked):5.1%} of asks | windows with any move {moved_windows / max(1, n_windows):5.1%} | "
          f"all requests/round {sum(kinds.values()) / rounds:5.1f}")


if __name__ == "__main__":
    print(f"Off-turn window load, {TRIALS} fights per row")
    scenarios = {
        "duel 8 apart (tactical)": em.duel_apart(em.TACT, em.TACT),
        "1v3 open (tactical D, fixed:2)": em.one_v_three("open_12x12", em.TACT, '"fixed:2"'),
        "1v3 corridor (tactical D, fixed:2)": em.one_v_three("corridor", em.TACT, '"fixed:2"', spawn_d="D"),
        "archer open (tactical both)": em.archer_scenario(em.TACT),
        "retreat line 2v2": em.retreat_line(em.TACT_FLEE, '{ kind = "tactical", commit = "alpha", target = "first" }'),
        "3v3 open (tactical chipkill)": em.n_v_m(3, 3, em.TACT, em.TACT),
    }
    for name, text in scenarios.items():
        print(f"## {name}")
        for label, ov in (("v0.9", {}), ("scope: not after allies", {"off_turn": {"scope": "not_after_allies"}}),
                          ("no on-turn extra", {"movement": {"extra_mode": "none"}}),
                          ("desc + restart", {"off_turn": {"order": "descending_initiative", "restart_after_move": True}})):
            load(text, ov, label)
