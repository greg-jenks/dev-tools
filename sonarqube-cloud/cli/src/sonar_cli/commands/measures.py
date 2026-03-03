from __future__ import annotations

import json

import typer
from rich.console import Console

from sonar_cli.client import SonarCloudClient
from sonar_cli.commands import OutputFormat
from sonar_cli.config import get_settings
from sonar_cli.formatting import format_measures


DEFAULT_METRICS = ",".join(
    [
        "coverage",
        "reliability_rating",
        "security_rating",
        "sqale_rating",
        "duplicated_lines_density",
        "ncloc",
        "bugs",
        "vulnerabilities",
        "code_smells",
    ]
)


def measures(
    project: str,
    branch: str | None = typer.Option(None, "--branch"),
    metrics: str = typer.Option(DEFAULT_METRICS, "--metrics"),
    output: OutputFormat = typer.Option(OutputFormat.table, "--output"),
) -> None:
    settings = get_settings()
    with SonarCloudClient(settings) as client:
        result = client.component_measures(project, metrics=metrics, branch=branch)
    if output == OutputFormat.json:
        typer.echo(json.dumps(result, indent=2))
        return
    Console().print(format_measures(result))
