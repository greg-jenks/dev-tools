from rich.console import Console

from sonar_cli.formatting import (
    _html_to_markdown,
    format_issues_table,
    format_quality_gate,
    format_rules_table,
    rating_to_letter,
)


def _render_text(renderable) -> str:
    console = Console(record=True, width=200)
    console.print(renderable)
    return console.export_text()


def test_html_to_markdown_conversion_preserves_structure():
    html = "<h2>Header</h2><p>Text</p><pre><code>print('x')</code></pre><ul><li>item</li></ul>"
    md = _html_to_markdown(html)
    assert "## Header" in md
    assert "print('x')" in md
    assert "* item" in md


def test_clean_code_taxonomy_display():
    table = format_issues_table(
        [
            {
                "key": "i1",
                "rule": "r1",
                "component": "src/a.py",
                "line": 1,
                "message": "m",
                "impacts": [{"softwareQuality": "SECURITY", "severity": "HIGH"}],
            }
        ]
    )
    text = _render_text(table)
    assert "SECURITY:HIGH" in text


def test_legacy_taxonomy_fallback():
    table = format_rules_table([{"key": "r1", "name": "Rule", "severity": "MAJOR", "type": "CODE_SMELL"}])
    text = _render_text(table)
    assert "CODE_SMELL:MAJOR" in text


def test_quality_gate_passed_failed_formatting():
    passed = _render_text(format_quality_gate({"projectStatus": {"status": "OK", "conditions": []}}))
    failed = _render_text(format_quality_gate({"projectStatus": {"status": "ERROR", "conditions": []}}))
    assert "PASSED" in passed
    assert "ERROR" in failed


def test_rating_translation():
    assert rating_to_letter("1.0") == "A"
    assert rating_to_letter("2.0") == "B"
