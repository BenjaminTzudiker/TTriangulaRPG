"""The 0.10.0 ranged measures (requirements R9) from constructed fights, and the ranged10
suite: every row builds, and a small run renders."""

import sys
from pathlib import Path

from stamina_engine.experiments import ranged10_suite
from stamina_engine.experiments.metrics import fight_row
from stamina_engine.experiments.positioning import build_scenario, run_rows
from stamina_engine.experiments.runner import battle_for

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "golden"))


def test_a_reaction_that_closes_in_is_measured() -> None:
    import test_rules_0_10_0 as r

    t = r.Listed(dives=[r.Move(((2, 2), (1, 2)))])
    result = r.fight(
        [
            ("A", "red", r.profile(r.archer()), (0, 2), r.Listed(turns=[r.Shoot("T")])),
            ("T", "blue", r.sample(), (3, 2), t),
        ],
        attacks={"A": [8, 1]},  # 8 crits on the longbow's d8 at Finesse 2 (7-8)
    )
    row = fight_row(result, 0, 0)
    assert row["reactions:close"] == 1 and row["reaction_cost"] == 1
    assert sum(row[f"reactions:{k}"] for k in ("cover", "back", "shift")) == 0
    assert (row["shot_crits"], row["shots_band1"], row["shots_band2"]) == (1, 1, 0)
    assert row["pb_provoked"] == 0 and row["melee_round"] is None
    assert row["t1_shot_spend"] == 4 and row["t1_shot_reserve"] == 14 - 4
    # Unblocked, 8 + 1 + 1 = 10, less armor 2 - 1 (the crit), at most the limit 9, + 1: 10 HP.
    assert row["team:T"] == "blue" and row["fell:T"] == 1 and row["down_by_r2:blue"]
    hurt = sum(e.injury for e in result.log if type(e).__name__ == "AttackResolved")
    assert row["shot_hp:red"] == hurt


def test_a_point_blank_shot_is_measured() -> None:
    import test_rules_0_10_0 as r

    t = r.Listed(oas=[r.OATake("main", 1)])
    result = r.fight(
        [
            ("A", "red", r.profile(r.archer()), (2, 2), r.Listed(turns=[r.Shoot("T")])),
            ("T", "blue", r.sample(), (3, 2), t),
        ],
        attacks={"A": [1, 1], "T": [8]},
    )
    row = fight_row(result, 0, 0)
    assert (row["pb_provoked"], row["pb_taken"]) == (1, 1)
    assert row["melee_round"] == 1
    assert sum(row[f"reactions:{k}"] for k in ranged10_suite.REACTIONS) == 0


def test_every_row_builds() -> None:
    for row in ranged10_suite.ROWS:
        s = build_scenario(row)
        battle_for(s, 0)  # derives every build against its table


def test_a_small_run_renders() -> None:
    rows = [ranged10_suite.ROWS[0], ranged10_suite.ROWS[-1]]
    report = ranged10_suite.render(run_rows(rows, trials=2), "stamp", 2)
    assert "## S1. Open ground, archer v sword and board" in report
    assert "## S6. Two archers v an armored beast" in report
    assert "## Reading the columns" in report
