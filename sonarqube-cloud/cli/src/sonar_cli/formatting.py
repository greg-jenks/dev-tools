from __future__ import annotations

from markdownify import markdownify
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


def _impact_quality(item: dict) -> str:
    impacts = item.get("impacts") or []
    if isinstance(impacts, list) and impacts and isinstance(impacts[0], dict):
        quality = impacts[0].get("softwareQuality")
        severity = impacts[0].get("severity")
        if quality and severity:
            return f"{quality}:{severity}"
    legacy_severity = item.get("severity")
    legacy_type = item.get("type")
    if legacy_severity and legacy_type:
        return f"{legacy_type}:{legacy_severity}"
    return str(legacy_severity or legacy_type or "")


def _clean_code_attr(item: dict) -> str:
    return str(item.get("cleanCodeAttribute") or item.get("cleanCodeAttributeCategory") or "")


def _html_to_markdown(html: str) -> str:
    return markdownify(html or "", heading_style="ATX")


def _status_text(status: str) -> Text:
    style = "green" if status in ("OK", "PASSED", "SUCCESS") else "red"
    return Text(status, style=style)


def format_projects_table(data: list[dict]) -> Table:
    table = Table(title="Projects", box=box.SIMPLE_HEAVY)
    table.add_column("Key")
    table.add_column("Name")
    table.add_column("Last Analysis")
    for item in data:
        table.add_row(str(item.get("key", "")), str(item.get("name", "")), str(item.get("analysisDate", "")))
    return table


def format_rules_table(data: list[dict]) -> Table:
    table = Table(title="Rules", box=box.SIMPLE_HEAVY)
    table.add_column("Key")
    table.add_column("Name")
    table.add_column("Impact")
    table.add_column("Clean Code Attribute")
    table.add_column("Language")
    for item in data:
        table.add_row(
            str(item.get("key", "")),
            str(item.get("name", "")),
            _impact_quality(item),
            _clean_code_attr(item),
            str(item.get("langName") or item.get("lang") or ""),
        )
    return table


def format_rule_detail(data: dict) -> Panel:
    rule = data.get("rule", data)
    description_html = str(rule.get("htmlDesc") or rule.get("description") or "")
    md = _html_to_markdown(description_html)
    lines = [
        f"Key: {rule.get('key', '')}",
        f"Name: {rule.get('name', '')}",
        f"Impact: {_impact_quality(rule)}",
        f"Clean Code Attribute: {_clean_code_attr(rule)}",
        f"Remediation: {rule.get('debtRemFnType') or rule.get('remFnType') or ''}",
        "",
        md,
    ]
    return Panel(Markdown("\n".join(lines)), title="Rule Detail")


def format_issues_table(data: list[dict]) -> Table:
    table = Table(title="Issues", box=box.SIMPLE_HEAVY)
    table.add_column("Key")
    table.add_column("Rule")
    table.add_column("Impact")
    table.add_column("Quality")
    table.add_column("File")
    table.add_column("Line")
    table.add_column("Message")
    for item in data:
        impact = _impact_quality(item)
        quality = ""
        impacts = item.get("impacts") or []
        if isinstance(impacts, list) and impacts and isinstance(impacts[0], dict):
            quality = str(impacts[0].get("softwareQuality", ""))
        table.add_row(
            str(item.get("key", "")),
            str(item.get("rule", "")),
            impact,
            quality,
            str(item.get("component", "")),
            str(item.get("line", "")),
            str(item.get("message", "")),
        )
    return table


def format_quality_gate(data: dict) -> Table:
    status = (data.get("projectStatus") or {}).get("status", "")
    table = Table(title="Quality Gate", box=box.SIMPLE_HEAVY)
    table.add_column("Status")
    table.add_column("Metric")
    table.add_column("Actual")
    table.add_column("Operator")
    table.add_column("Error Threshold")
    conditions = (data.get("projectStatus") or {}).get("conditions", [])
    if not conditions:
        table.add_row(_status_text("PASSED" if status == "OK" else status), "", "", "", "")
    for condition in conditions:
        table.add_row(
            _status_text("PASSED" if status == "OK" else status),
            str(condition.get("metricKey", "")),
            str(condition.get("actualValue", "")),
            str(condition.get("comparator", "")),
            str(condition.get("errorThreshold", "")),
        )
    return table


def rating_to_letter(value: str) -> str:
    mapping = {"1.0": "A", "2.0": "B", "3.0": "C", "4.0": "D", "5.0": "E"}
    return mapping.get(str(value), str(value))


def format_measures(data: dict) -> Table:
    component = data.get("component", {})
    measures = component.get("measures", [])
    table = Table(title="Measures", box=box.SIMPLE_HEAVY)
    table.add_column("Metric")
    table.add_column("Value")
    for measure in measures:
        key = str(measure.get("metric", ""))
        value = str(measure.get("value", ""))
        if key.endswith("_rating"):
            value = rating_to_letter(value)
        table.add_row(key, value)
    return table


def format_analysis_status(data: dict) -> Table:
    tasks = data.get("tasks", []) or []
    status = "NO_ANALYSIS"
    submitted = ""
    duration = ""
    branch = ""
    if tasks:
        latest = tasks[0]
        status = str(latest.get("status", "NO_ANALYSIS"))
        submitted = str(latest.get("submittedAt", ""))
        duration = str(latest.get("executionTimeMs", ""))
        branch = str(latest.get("branch") or latest.get("branchType") or "")
    table = Table(title="Analysis Status", box=box.SIMPLE_HEAVY)
    table.add_column("Status")
    table.add_column("Submitted")
    table.add_column("Duration(ms)")
    table.add_column("Branch")
    table.add_row(_status_text(status), submitted, duration, branch)
    return table
