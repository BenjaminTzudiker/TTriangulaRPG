"""se table prints the review layouts."""

from pathlib import Path

from typer.testing import CliRunner

from stamina_engine.cli import app


def test_se_table() -> None:
    runner = CliRunner()
    one = runner.invoke(app, ["table", "1", "--ruleset", "review-sim", "--rounding", "half-even"])
    assert one.exit_code == 0, one.output
    assert "| MD 4, armor 2 | 2 | 5 | 12 | 23 | 38 |" in one.output
    eight = runner.invoke(app, ["table", "8"])
    assert eight.exit_code == 0
    assert "Greataxe 2d6 + 6 (base 3) | 4.33" in eight.output
    assert runner.invoke(app, ["table", "5"]).exit_code != 0
    assert "RuleSet v0.9 " in eight.output and "source " in eight.output


def test_se_table_with_plugin() -> None:
    examples = Path(__file__).resolve().parents[2] / "examples"
    args = ["table", "8", "--plugin", str(examples / "exp_quadratic_surcharge.py")]
    args += ["--ruleset", str(examples / "exp_quadratic_surcharge.toml")]
    out = CliRunner().invoke(app, args)
    assert out.exit_code == 0, out.output
    assert "Longsword 1H 1d8 + 3 (base 2) | 3.75 | 3.00 | 2.05 |" in out.output
    assert "RuleSet exp-quadratic-surcharge " in out.output
    assert "Plugin exp_quadratic_surcharge.py " in out.output
    missing = CliRunner().invoke(app, ["table", "1", "--ruleset", "nope.toml"])
    assert missing.exit_code != 0
