"""The parity suite runs end to end: every case in lockstep, and the report renders."""

from stamina_engine.experiments.oracle_bridge import Knobs
from stamina_engine.experiments.parity import cases, check, render, rules_for, run_cases
from stamina_engine.experiments.stats import wilson
from stamina_engine.provenance import collect


def test_every_table_is_covered() -> None:
    tables = {c.table for c in cases()}
    assert tables == {"Table 2", "Table 3", "Table 4", "Table 7", "Table 9", "Addendum"}
    assert sum(1 for c in cases() if c.table == "Table 2") == 36


def test_suite_runs_in_lockstep() -> None:
    sample = cases()[::9]  # a spread over every table
    results = run_cases(sample, scale=0.001)
    assert all(not r.mismatches for r in results)
    report = render(results, collect(rules_for(Knobs())).text(), 0.001)
    assert "Mismatches with the oracle: 0" in report
    assert "## Flagged for investigation" in report


def test_check_marks() -> None:
    iv = wilson(500, 1000)  # 50%, half-width about 3.1 points
    assert check(iv, 52, pct=True) == "✓"
    assert check(iv, 60, pct=True) == "✗"
    assert check(iv, (54, 58), pct=True) == "✓"  # within sqrt(2) x half-width + 0.5
    assert check(iv, "text", pct=True) == "·"
