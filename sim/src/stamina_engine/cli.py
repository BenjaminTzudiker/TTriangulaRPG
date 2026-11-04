"""se: the engine's command line. M0 has `se table`.

Every command prints its provenance (RuleSet, code and plugins) after its result.
"""

from pathlib import Path
from typing import Annotated

import typer

from stamina_engine.analysis.tables import (
    Rounding,
    render_table1,
    render_table8,
    table1,
    table8,
)
from stamina_engine.core.errors import ConfigError
from stamina_engine.provenance import collect
from stamina_engine.rules.plugins import PluginInfo, load_plugin
from stamina_engine.rules.ruleset import RuleSet, load_ruleset

app = typer.Typer(no_args_is_help=True, add_completion=False)

RulesetOption = Annotated[
    str, typer.Option(help="A preset name (v0.9, review-candidate, review-sim) or a .toml file.")
]
PluginOption = Annotated[
    list[Path] | None,
    typer.Option("--plugin", help="A Python file of extra rule variants. Repeatable."),
]


@app.callback()
def main() -> None:
    """Rules engine for the stamina TTRPG (see sim/docs/ENGINE_PLAN.md)."""


def _setup(ruleset: str, plugins: list[Path] | None) -> tuple[RuleSet, list[PluginInfo]]:
    """Plugins load first, so a RuleSet file can name their variants."""
    try:
        infos = [load_plugin(p) for p in plugins or []]
        return load_ruleset(ruleset), infos
    except ConfigError as exc:
        raise typer.BadParameter(str(exc)) from exc


@app.command()
def table(
    number: Annotated[int, typer.Argument(help="Review table number: 1 or 8.")],
    ruleset: RulesetOption = "v0.9",
    rounding: Annotated[
        Rounding, typer.Option(help="half-even reproduces the review's printed tables.")
    ] = Rounding.HALF_UP,
    plugin: PluginOption = None,
) -> None:
    """Print one of the review's exact static tables."""
    rules, infos = _setup(ruleset, plugin)
    if number == 1:
        typer.echo(render_table1(table1(rules, rounding), rounding))
    elif number == 8:
        typer.echo(render_table8(table8(rules), rounding))
    else:
        raise typer.BadParameter("M0 has tables 1 and 8", param_hint="NUMBER")
    typer.echo("")
    typer.echo(collect(rules, infos).text())
