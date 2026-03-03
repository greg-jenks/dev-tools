from __future__ import annotations

import json
from enum import Enum

import typer
from rich.console import Console

from sonar_cli.client import SonarCloudClient
from sonar_cli.config import get_settings
from sonar_cli.formatting import format_projects_table


class OutputFormat(str, Enum):
    table = "table"
    json = "json"


def projects(output: OutputFormat = typer.Option(OutputFormat.table, "--output")) -> None:
    settings = get_settings()
    client = SonarCloudClient(settings)
    try:
        result = client.search_components()
    finally:
        client.close()
    if output == OutputFormat.json:
        typer.echo(json.dumps(result, indent=2))
        return
    Console().print(format_projects_table(result))
