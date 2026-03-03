from __future__ import annotations

import json

import typer
from rich.console import Console

from sonar_cli.client import SonarCloudClient
from sonar_cli.commands import OutputFormat
from sonar_cli.config import get_settings
from sonar_cli.formatting import format_issues_table


def issues(
    project: str,
    branch: str | None = typer.Option(None, "--branch"),
    pr: str | None = typer.Option(None, "--pr"),
    files: str | None = typer.Option(None, "--files"),
    status: str | None = typer.Option(None, "--status"),
    new: bool = typer.Option(False, "--new"),
    impact: str | None = typer.Option(None, "--impact"),
    quality: str | None = typer.Option(None, "--quality"),
    severity: str | None = typer.Option(None, "--severity"),
    issue_type: str | None = typer.Option(None, "--type"),
    output: OutputFormat = typer.Option(OutputFormat.table, "--output"),
) -> None:
    settings = get_settings()
    with SonarCloudClient(settings) as client:
        result = client.search_issues(
            project=project,
            branch=branch,
            pr=pr,
            files=files,
            statuses=status,
            since_leak_period=new,
            impact=impact,
            quality=quality,
            severity=severity,
            issue_type=issue_type,
        )
    if output == OutputFormat.json:
        typer.echo(json.dumps(result, indent=2))
        return
    Console().print(format_issues_table(result))
