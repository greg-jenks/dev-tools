from __future__ import annotations

import json
from enum import Enum

import typer
from rich.console import Console

from sonar_cli.client import SonarCloudClient
from sonar_cli.config import get_settings
from sonar_cli.formatting import format_issues_table


class OutputFormat(str, Enum):
    table = "table"
    json = "json"


def issues(
    project: str,
    branch: str | None = typer.Option(None, "--branch"),
    pr: str | None = typer.Option(None, "--pr"),
    new: bool = typer.Option(False, "--new"),
    impact: str | None = typer.Option(None, "--impact"),
    quality: str | None = typer.Option(None, "--quality"),
    severity: str | None = typer.Option(None, "--severity"),
    issue_type: str | None = typer.Option(None, "--type"),
    output: OutputFormat = typer.Option(OutputFormat.table, "--output"),
) -> None:
    settings = get_settings()
    client = SonarCloudClient(settings)
    try:
        result = client.search_issues(
            project=project,
            branch=branch,
            pr=pr,
            since_leak_period=new,
            impact=impact,
            quality=quality,
            severity=severity,
            issue_type=issue_type,
        )
    finally:
        client.close()
    if output == OutputFormat.json:
        typer.echo(json.dumps(result, indent=2))
        return
    Console().print(format_issues_table(result))
