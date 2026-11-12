"""The se command line: table layouts, plugins, help and errors, and running with nothing
installed."""

import os
import subprocess
import sys
from pathlib import Path

from stamina_engine.cli import invoke

SIM = Path(__file__).resolve().parents[2]


def test_se_table() -> None:
    one = invoke(["table", "1", "--ruleset", "review-sim", "--rounding", "half-even"])
    assert one.exit_code == 0, one.output
    assert "| MD 4, armor 2 | 2 | 5 | 12 | 23 | 38 |" in one.output
    eight = invoke(["table", "8"])
    assert eight.exit_code == 0
    assert "Greataxe 2d6 + 6 (base 3) | 4.33" in eight.output
    assert invoke(["table", "4"]).exit_code != 0
    assert "RuleSet v0.10.0 " in eight.output and "source " in eight.output  # the baseline


def test_se_table_with_plugin() -> None:
    examples = SIM / "examples"
    args = ["table", "8", "--plugin", str(examples / "exp_quadratic_surcharge.py")]
    args += ["--ruleset", str(examples / "exp_quadratic_surcharge.toml")]
    out = invoke(args)
    assert out.exit_code == 0, out.output
    assert "Longsword 1H 1d8 + 3 (base 2) | 3.75 | 3.00 | 2.05 |" in out.output
    assert "RuleSet exp-quadratic-surcharge " in out.output
    assert "Plugin exp_quadratic_surcharge.py " in out.output
    missing = invoke(["table", "1", "--ruleset", "nope.toml"])
    assert missing.exit_code == 2
    assert "se table: error: can't read RuleSet file nope.toml" in missing.output


def test_help_and_bad_arguments() -> None:
    top = invoke([])
    assert top.exit_code == 0 and "suite" in top.output and "trace" in top.output
    assert invoke(["run", "--help"]).exit_code == 0
    assert invoke(["suite", "nope"]).exit_code == 2
    assert invoke(["compare", "x.toml"]).exit_code == 2  # --a and --b are required
    both = invoke(["load"])
    assert both.exit_code == 2 and "give a scenario or --session logs" in both.output


def test_runs_with_no_installed_packages() -> None:
    """A chat that can't reach PyPI runs the engine from source: the package needs only the
    standard library (pyarrow just for --out). `-S` leaves site-packages off the path."""
    env = {**os.environ, "PYTHONPATH": str(SIM / "src")}
    scenario = SIM / "src/stamina_engine/data/scenarios/l1_duel.toml"
    for args in (["table", "8"], ["run", str(scenario), "--trials", "3"]):
        done = subprocess.run(
            [sys.executable, "-S", "-m", "stamina_engine", *args],
            capture_output=True,
            text=True,
            env=env,
            cwd=SIM,
            timeout=120,
        )
        assert done.returncode == 0, done.stderr
        assert "RuleSet v0.10.0 " in done.stdout
