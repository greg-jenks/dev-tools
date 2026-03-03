from __future__ import annotations

import json

import typer
from rich.console import Console

from sonar_cli.client import SonarCloudClient
from sonar_cli.commands import OutputFormat
from sonar_cli.config import get_settings
from sonar_cli.formatting import format_quality_gate


def quality_gate(
    project: str,
    branch: str | None = typer.Option(None, "--branch"),
    pr: str | None = typer.Option(None, "--pr"),
    output: OutputFormat = typer.Option(OutputFormat.table, "--output"),
) -> None:
    settings = get_settings()
    with SonarCloudClient(settings) as client:
        result = client.project_quality_gate_status(project, branch=branch, pr=pr)
    if output == OutputFormat.json:
        typer.echo(json.dumps(result, indent=2))
    else:
        Console().print(format_quality_gate(result))
    status = (result.get("projectStatus") or {}).get("status", "")
    if status != "OK":
        raise typer.Exit(code=1)
