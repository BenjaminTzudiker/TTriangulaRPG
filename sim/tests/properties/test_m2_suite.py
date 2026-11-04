"""M2 scenarios, positioning metrics, se trace and the positioning suite."""

import sys
from pathlib import Path

import pytest

from stamina_engine.cli import invoke
from stamina_engine.experiments.metrics import attack_rows, fight_row, summarize
from stamina_engine.experiments.positioning import ROWS, build_scenario, render, run_rows
from stamina_engine.experiments.runner import run_trial
from stamina_engine.experiments.scenario import load_scenario
from stamina_engine.experiments.trace import trace

SCENARIOS = Path(__file__).resolve().parents[2] / "src" / "stamina_engine" / "data" / "scenarios"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "golden"))


@pytest.mark.parametrize("path", sorted(SCENARIOS.glob("*.toml")), ids=lambda p: p.stem)
def test_every_library_scenario_runs(path: Path) -> None:
    if path.stem == "surcharge_sweep":
        pytest.skip("a sweep, not a scenario")
    s = load_scenario(path)
    result = run_trial(s, 0, check=True)
    assert result.reason in ("side_out", "round_cap")


def test_positioning_metrics_from_the_avoidance_example() -> None:
    import test_movement_battles as m  # the golden battle: avoid 2, then 1, then 1

    mover = m.Listed(
        turns=[m.Move(((3, 2), (4, 2), (5, 2)))],
        avoids=[m.Avoid(("B", "A")), m.Avoid(("C",)), m.Avoid(("C",))],
    )
    result = m.fight(
        [
            m.Who("M", "red", m.sample(), (2, 2), mover, (12, 12)),
            m.Who("A", "blue", m.sample(), (1, 1), m.Listed(), (2, 2)),
            m.Who("B", "blue", m.sample(), (1, 3), m.Listed(), (1, 2)),
            m.Who("C", "blue", m.sample(), (4, 3), m.Listed(), (1, 1)),
        ]
    )
    row = fight_row(result, 0, 0)
    assert (row["oa_provoked"], row["oa_avoided"], row["oa_taken"]) == (4, 4, 0)
    assert row["moved:red:on"] == 3 and row["moved:red:off"] == 0
    assert row["spent:red:avoid"] == 4
    assert row["contact_round"] is None
    s = summarize([row])
    assert s.contact_round is None and s.oa_taken is not None


def test_oa_rows_are_marked() -> None:
    import test_movement_battles as m

    path = m.Move(((5, 2), (5, 3), (5, 4)))
    result = m.fight(
        [
            m.Who("M", "red", m.sample(), (5, 1), m.Listed(turns=[path]), (12, 12)),
            m.Who("S", "blue", m.spearman(1), (5, 0), m.Listed(oas=[m.OATake("main", 1)]), (1, 1)),
        ],
        attacks={"S": [4]},
    )
    (row,) = attack_rows(result, 0)
    assert (row["kind"], row["attacker"], row["cost"]) == ("opportunity", "S", 2)


def test_se_trace() -> None:
    out = invoke(["trace", str(SCENARIOS / "one_v_three_corridor.toml")])
    assert out.exit_code == 0, out.output
    assert "Creatures: A = D (defender)" in out.output
    assert "TurnStarted" in out.output and "  4 #." in out.output
    s = load_scenario(SCENARIOS / "one_v_three_corridor.toml")
    assert trace(s, 3) == trace(s, 3)


def test_positioning_suite_small() -> None:
    rows = [r for r in ROWS if "door" in r.group][:2]
    results = run_rows(rows, trials=4)
    report = render(results, "stamp", 4)
    assert "## Reach at a door (F9)" in report
    assert report.count("| v0.9, FIN") == 2
    fin0 = build_scenario(rows[1])
    assert fin0.combatants[0].build.name == "l1_spear_fin0"


def test_grid_fight_with_everyone_adjacent_matches_the_all_adjacent_arena() -> None:
    """Starting engaged with scripted agents, nobody moves and no OA is provoked, so on the
    same seeds the grid plays exactly the all-adjacent fights (map events aside)."""
    from dataclasses import replace

    s = load_scenario(SCENARIOS / "one_v_three_engaged.toml").with_agents(
        {"D": {"commit": "fixed:2", "target": "lowest_stamina"}}
    )
    flat = replace(
        s,
        battlefield=None,
        arena="all_adjacent",
        combatants=tuple(replace(c, pos=None) for c in s.combatants),
    )
    skip = {"MapLoaded", "Placed", "BattleStarted"}
    for t in range(30):
        on_grid = run_trial(s, t, cell="same").log
        adjacent = run_trial(flat, t, cell="same").log
        assert [e.to_json() for e in on_grid if type(e).__name__ not in skip] == [
            e.to_json() for e in adjacent if type(e).__name__ not in skip
        ], t
