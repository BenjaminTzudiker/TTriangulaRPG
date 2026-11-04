"""M4: the phase suite's plan and layouts."""

import pytest

from stamina_engine.experiments.phase_suite import (
    LEVELS,
    NPC_DIAL,
    POLICIES,
    TABLE7_PAIRS,
    TABLE7_POLICIES,
    TABLE7_VARIANTS,
    plan,
    render,
    run,
)


def test_plan_covers_every_item() -> None:
    p = plan()
    rows = p.rows()
    assert len({(r.group, r.label) for r in rows}) == len(rows)  # every cell unique
    assert len(p.duels) == len(POLICIES) ** 2
    assert len(p.levels) == 2 * len(LEVELS)
    assert len(p.dial) == 2 * len(NPC_DIAL) * 2
    assert len(p.table7) == len(TABLE7_VARIANTS) * len(TABLE7_PAIRS) * len(TABLE7_POLICIES)
    assert p.ranged and p.reach and p.retreat and len(p.party) == len(NPC_DIAL)


@pytest.mark.slow
def test_phase_suite_renders_every_section() -> None:
    report = render(run(trials=1, workers=4), "stamp", 1)
    for heading in (
        "## 1. Exchange tables, exactly",
        "### The L1 policy matrix",
        "### By level",
        "## 3. One against three",
        "## 4. Archer",
        "## 5-6.",
        "## 7. Armored",
        "## 8. A 3v3",
        "Table 8 under F8 option 1",
    ):
        assert heading in report, heading
