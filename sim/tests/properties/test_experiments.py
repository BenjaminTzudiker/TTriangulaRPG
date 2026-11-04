"""Scenarios, the runner, sweeps, metrics, stats, Parquet output and the CLI."""

from pathlib import Path

import pyarrow.parquet as pq
import pytest
from typer.testing import CliRunner

from stamina_engine.cli import app
from stamina_engine.core.errors import ConfigError
from stamina_engine.experiments.metrics import summarize
from stamina_engine.experiments.results import write_results
from stamina_engine.experiments.runner import run_scenario, run_trial, trial_seed
from stamina_engine.experiments.scenario import load_scenario, scenario_from_toml, scenario_to_toml
from stamina_engine.experiments.stats import paired_difference, wilson
from stamina_engine.experiments.sweep import compare, load_sweep, run_sweep
from stamina_engine.provenance import PACKAGE_DIR
from stamina_engine.rules.ruleset import review_candidate, v0_9

SCENARIOS = PACKAGE_DIR / "data" / "scenarios"
DUEL = SCENARIOS / "l1_duel.toml"
SWARM = SCENARIOS / "one_v_three.toml"


def test_scenario_loading() -> None:
    s = load_scenario(SWARM)
    assert [c.id for c in s.combatants] == ["D", "A0", "A1", "A2"]
    assert {c.team for c in s.combatants} == {"defender", "attackers"}
    assert s.round_cap == 20 and s.rules == v0_9()
    swapped = s.with_agents({"A": "alpha"})
    assert [c.agent for c in swapped.combatants][1:] == ["alpha"] * 3


@pytest.mark.parametrize("path", [DUEL, SWARM])
def test_scenario_round_trip(path: Path) -> None:
    s = load_scenario(path)
    again = scenario_from_toml(scenario_to_toml(s))
    assert again == s


@pytest.mark.parametrize(
    "text",
    [
        '[scenario]\nname = "x"\narena = "corridor"\n[[combatant]]\nid="a"\nbuild="l1_sample"\n'
        '[[combatant]]\nid="b"\nbuild="l1_sample"',
        '[scenario]\nname = "x"\n[[combatant]]\nid="a"\nteam="t"\nbuild="l1_sample"\n'
        '[[combatant]]\nid="b"\nteam="t"\nbuild="l1_sample"',
        '[scenario]\nname = "x"\nspeed = 3\n[[combatant]]\nid="a"\nbuild="l1_sample"',
        '[scenario]\nname = "x"\ndice = "loaded"\n[[combatant]]\nid="a"\nbuild="l1_sample"\n'
        '[[combatant]]\nid="b"\nbuild="l1_sample"',
    ],
)
def test_bad_scenarios(text: str) -> None:
    with pytest.raises(ConfigError):
        scenario_from_toml(text)


def test_any_fight_reruns_alone() -> None:
    s = load_scenario(DUEL)
    run = run_scenario(s, trials=6)
    for row in run.fights:
        alone = run_trial(s, row["trial"])
        assert alone.log_sha256() == row["log_sha256"]
        assert str(trial_seed(s.seed, s.name, row["trial"])) == row["seed"]


def test_processes_match_single_process() -> None:
    s = load_scenario(DUEL)
    single = run_scenario(s, trials=520, workers=1)
    multi = run_scenario(s, trials=520, workers=3)
    assert single.fights == multi.fights
    assert single.attacks == multi.attacks
    assert single.run_id == multi.run_id


def test_wilson_known_values() -> None:
    iv = wilson(50, 100)
    assert (round(iv.low, 4), round(iv.high, 4)) == (0.4038, 0.5962)
    zero = wilson(0, 10)
    assert zero.low == 0.0 and round(zero.high, 4) == 0.2775
    assert paired_difference([1, 2, 3], [1, 2, 3]).estimate == 0


def test_summary_on_known_rows() -> None:
    rows = [
        {
            "winner": "a",
            "win:a": True,
            "win:b": False,
            "rounds": 2,
            "first_won": True,
            "winner_untouched": True,
            "loser_hp": -3,
            "dead": 0,
            "decisions": 10,
        },
        {
            "winner": "b",
            "win:a": False,
            "win:b": True,
            "rounds": 4,
            "first_won": False,
            "winner_untouched": False,
            "loser_hp": -1,
            "dead": 1,
            "decisions": 20,
        },
        {
            "winner": None,
            "win:a": False,
            "win:b": False,
            "rounds": 30,
            "first_won": None,
            "winner_untouched": None,
            "loser_hp": None,
            "dead": 0,
            "decisions": 60,
        },
    ]
    s = summarize(rows)
    assert (s.trials, s.wins["a"].estimate, s.draws.estimate) == (3, 1 / 3, 1 / 3)
    assert s.first_mover.estimate == 0.5 and s.first_mover.n == 2
    assert s.loser_hp.estimate == -2 and s.rounds_median == 4
    assert s.decisions_per_round == 90 / 36


def test_compare_is_paired() -> None:
    s = load_scenario(DUEL)
    _, _, same = compare(s, v0_9(), v0_9().with_(name="copy"), trials=60)
    assert all(d.diff.estimate == 0 and d.diff.low == d.diff.high == 0 for d in same)
    _, _, diff = compare(s, v0_9(), review_candidate(), trials=60)
    assert any(d.diff.estimate != 0 for d in diff)


def test_sweep_cells_share_seeds(tmp_path: Path) -> None:
    name, cells = load_sweep(SCENARIOS / "surcharge_sweep.toml")
    assert name == "surcharge" and len(cells) == 4
    duel = [c for c in cells if c.scenario.name == "l1-duel"]
    assert duel[0].seed_key == duel[1].seed_key  # RuleSets compared on the same dice
    assert duel[0].scenario.rules.surcharge != duel[1].scenario.rules.surcharge
    results = run_sweep(cells, trials=8)
    paths = write_results(results, tmp_path)
    fights = pq.read_table(tmp_path / "fights.parquet")
    assert fights.num_rows == 32
    assert set(fights.column("ruleset").to_pylist()) == {"v0.9", "surcharge+2"}
    runs = pq.read_table(tmp_path / "runs.parquet").to_pylist()
    assert all(r["source_sha256"] and r["ruleset_toml"] for r in runs)
    assert len(paths) == 4


def test_cli_commands(tmp_path: Path) -> None:
    runner = CliRunner()
    out = runner.invoke(app, ["run", str(DUEL), "--trials", "20", "--out", str(tmp_path)])
    assert out.exit_code == 0, out.output
    assert "A wins:" in out.output and "RuleSet v0.9" in out.output
    assert (tmp_path / "decisions.parquet").exists()
    cmp = runner.invoke(
        app, ["compare", str(DUEL), "--a", "v0.9", "--b", "review-candidate", "--trials", "20"]
    )
    assert cmp.exit_code == 0, cmp.output
    assert "B - A" in cmp.output and "RuleSet review-candidate" in cmp.output
    sw = runner.invoke(app, ["sweep", str(SCENARIOS / "surcharge_sweep.toml"), "--trials", "4"])
    assert sw.exit_code == 0, sw.output
    assert sw.output.count("Trials: 4") == 4
