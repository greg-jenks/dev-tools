from __future__ import annotations

import typer

from . import __version__
from .commands.analysis import analysis_status
from .commands.issues import issues
from .commands.measures import measures
from .commands.projects import projects
from .commands.quality_gate import quality_gate
from .commands.rules import app as rules_app

app = typer.Typer(help="SonarCloud CLI for pre-PR quality checking")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", callback=version_callback, is_eager=True, help="Show version"),
) -> None:
    return None


app.command("projects")(projects)
app.command("issues")(issues)
app.command("quality-gate")(quality_gate)
app.command("measures")(measures)
app.command("analysis-status")(analysis_status)
app.add_typer(rules_app, name="rules")
