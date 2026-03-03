from __future__ import annotations

import json

import typer
from rich.console import Console

from sonar_cli.client import SonarCloudClient
from sonar_cli.commands import OutputFormat
from sonar_cli.config import get_settings
from sonar_cli.formatting import format_rule_detail, format_rules_table

app = typer.Typer(help="Rule lookup commands")


@app.command("list")
def rules_list(
    project: str,
    language: str | None = typer.Option(None, "--language"),
    output: OutputFormat = typer.Option(OutputFormat.table, "--output"),
) -> None:
    settings = get_settings()
    with SonarCloudClient(settings) as client:
        profiles = client.search_quality_profiles(project)
        profile_keys = [p.get("key") for p in profiles if p.get("key")]
        rules: list[dict] = []
        seen: set[str] = set()
        for profile_key in profile_keys:
            for rule in client.search_rules(str(profile_key), language=language):
                rule_key = str(rule.get("key") or "")
                if rule_key and rule_key not in seen:
                    seen.add(rule_key)
                    rules.append(rule)
    if output == OutputFormat.json:
        typer.echo(json.dumps(rules, indent=2))
        return
    Console().print(format_rules_table(rules))


@app.command("show")
def rules_show(rule_key: str, output: OutputFormat = typer.Option(OutputFormat.table, "--output")) -> None:
    settings = get_settings()
    with SonarCloudClient(settings) as client:
        result = client.show_rule(rule_key)
    if output == OutputFormat.json:
        typer.echo(json.dumps(result, indent=2))
        return
    Console().print(format_rule_detail(result))
