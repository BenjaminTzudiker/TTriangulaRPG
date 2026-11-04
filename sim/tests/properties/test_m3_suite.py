"""M3: ranged metrics and the ranged suite."""

import sys
from pathlib import Path

from stamina_engine.analysis.ranged import render_table5
from stamina_engine.experiments.metrics import attack_rows, fight_row
from stamina_engine.experiments.positioning import run_rows
from stamina_engine.experiments.ranged_suite import ROWS, render
from stamina_engine.rules.ruleset import preset

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "golden"))


def test_ranged_metrics_from_the_dive_battle() -> None:
    import test_ranged_battles as r

    walled = r.parse_map("\n".join([".....#..", ".....#..", ".....#..", "........", "........"]))
    t = r.Listed(dives=[r.Move(((6, 3), (6, 2)))])
    result = r.fight(
        [
            ("A", "red", r.archer(), (0, 1), r.Listed(turns=[r.Shoot("T")], aims=[1])),
            ("T", "blue", r.sample(), (6, 4), t),
        ],
        attacks={"A": [1, 1]},
        field=walled,
    )
    row = fight_row(result, 0, 0)
    assert (row["shots"], row["aims"], row["dives"], row["shots_missed"]) == (1, 1, 1, 0)
    assert row["spent:red:shot"] == 6
    (attack,) = attack_rows(result, 0)
    assert (attack["kind"], attack["steps"], attack["cost"]) == ("shot", 1, 6)


def test_ranged_suite_small() -> None:
    rows = [ROWS[0], ROWS[-1]]
    report = render(run_rows(rows, trials=3), "stamp", 3, render_table5(preset("v0.9")))
    assert "## Archer v fighter, open ground" in report
    assert "## Review Table 5's static part, exactly" in report and "✗" not in report
    assert "Duelist (AGI 2" in report
