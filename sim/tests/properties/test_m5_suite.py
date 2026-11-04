"""M5: the cores suite's rows and report."""

from stamina_engine.experiments.cores_suite import ABILITIES, FAMILIES, MODES, render, rows
from stamina_engine.experiments.positioning import build_scenario, run_rows


def test_rows_pair_every_ability_off_and_on() -> None:
    plan = rows()
    assert len({(r.group, r.label) for r in plan}) == len(plan)
    assert len(plan) == len(ABILITIES) * len(MODES) * (1 + len(FAMILIES))
    for r in plan:
        s = build_scenario(r)  # every build and agent spec loads
        assert s.combatants


def test_cores_report_renders() -> None:
    small = [r for r in rows() if r.label.startswith(("Fighter core", "Riposte"))]
    results = run_rows(small, trials=2)
    by = {(r.group, r.label) for r, _ in results}
    full = [(r, run) for r, run in results] + [
        (r, results[0][1]) for r in rows() if (r.group, r.label) not in by
    ]  # fill the other rows with any run: this checks the layout, not the numbers
    report = render(full, "stamp", 2)
    assert "## What turning each ability on buys" in report
    assert "| Fighter core | " in report and "## One against three, tactical defender" in report
