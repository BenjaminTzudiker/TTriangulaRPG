"""se: the engine's command line. M0 has `se table`."""

from typing import Annotated

import typer

from stamina_engine.analysis.tables import (
    Rounding,
    render_table1,
    render_table8,
    table1,
    table8,
)
from stamina_engine.rules.ruleset import preset

app = typer.Typer(no_args_is_help=True, add_completion=False)


@app.callback()
def main() -> None:
    """Rules engine for the stamina TTRPG (see sim/docs/ENGINE_PLAN.md)."""


@app.command()
def table(
    number: Annotated[int, typer.Argument(help="Review table number: 1 or 8.")],
    ruleset: Annotated[str, typer.Option(help="Preset name.")] = "v0.9",
    rounding: Annotated[
        Rounding, typer.Option(help="half-even reproduces the review's printed tables.")
    ] = Rounding.HALF_UP,
) -> None:
    """Print one of the review's exact static tables."""
    rules = preset(ruleset)
    if number == 1:
        typer.echo(render_table1(table1(rules, rounding), rules, rounding))
    elif number == 8:
        typer.echo(render_table8(table8(rules), rules, rounding))
    else:
        raise typer.BadParameter("M0 has tables 1 and 8", param_hint="NUMBER")
