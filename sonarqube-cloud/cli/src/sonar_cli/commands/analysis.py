from __future__ import annotations

import json
import time

import typer
from rich.console import Console

from sonar_cli.client import SonarCloudClient
from sonar_cli.commands import OutputFormat
from sonar_cli.config import get_settings
from sonar_cli.formatting import format_analysis_status

def _status_from_activity(activity: dict) -> str:
    tasks = activity.get("tasks", []) or []
    if not tasks:
        return "NO_ANALYSIS"
    return str(tasks[0].get("status", "NO_ANALYSIS"))


def _wait_for_terminal_status(
    client: SonarCloudClient,
    project: str,
    branch: str | None,
    timeout: int,
    sleeper=time.sleep,
    time_fn=time.time,
) -> tuple[str, dict]:
    started = time_fn()
    while True:
        result = client.ce_activity(project, branch=branch)
        status = _status_from_activity(result)
        if status in ("SUCCESS", "FAILED", "NO_ANALYSIS", "CANCELED"):
            return status, {"status": status, **result}
        if time_fn() - started >= timeout:
            return "TIMEOUT", {"status": "TIMEOUT", **result}
        sleeper(10)


def analysis_status(
    project: str,
    branch: str | None = typer.Option(None, "--branch"),
    wait: bool = typer.Option(False, "--wait"),
    timeout: int = typer.Option(300, "--timeout"),
    output: OutputFormat = typer.Option(OutputFormat.table, "--output"),
) -> None:
    settings = get_settings()
    client = SonarCloudClient(settings)
    try:
        if not wait:
            result = client.ce_activity(project, branch=branch)
            status = _status_from_activity(result)
            payload = {"status": status, **result}
        else:
            status, payload = _wait_for_terminal_status(client, project, branch, timeout)
            if status == "TIMEOUT":
                if output == OutputFormat.json:
                    typer.echo(json.dumps(payload, indent=2))
                else:
                    Console().print("Status: TIMEOUT")
                raise typer.Exit(code=2)
    finally:
        client.close()
    if output == OutputFormat.json:
        typer.echo(json.dumps(payload, indent=2))
    else:
        Console().print(format_analysis_status(payload))
    if status in ("FAILED", "NO_ANALYSIS", "CANCELED"):
        raise typer.Exit(code=1)
