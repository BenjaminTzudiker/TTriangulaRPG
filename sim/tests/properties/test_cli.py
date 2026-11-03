"""se table prints the review layouts."""

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
