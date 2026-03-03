import pytest


@pytest.fixture
def sample_rule():
    return {
        "key": "typescript:S6759",
        "name": "Rule name",
        "lang": "ts",
        "langName": "TypeScript",
        "cleanCodeAttribute": "FOCUSED",
        "impacts": [{"softwareQuality": "MAINTAINABILITY", "severity": "HIGH"}],
        "htmlDesc": "<h2>Title</h2><p>Body</p><pre><code>const a = 1;</code></pre><ul><li>item</li></ul>",
    }


@pytest.fixture
def sample_issue():
    return {
        "key": "issue-1",
        "rule": "typescript:S6759",
        "component": "src/file.ts",
        "line": 10,
        "message": "Fix this",
        "impacts": [{"softwareQuality": "SECURITY", "severity": "MEDIUM"}],
    }


@pytest.fixture
def sample_quality_gate_ok():
    return {
        "projectStatus": {
            "status": "OK",
            "conditions": [{"metricKey": "coverage", "actualValue": "85", "comparator": "LT", "errorThreshold": "80"}],
        }
    }


@pytest.fixture
def sample_measures():
    return {
        "component": {
            "measures": [
                {"metric": "coverage", "value": "85.4"},
                {"metric": "security_rating", "value": "1.0"},
            ]
        }
    }


@pytest.fixture
def sample_ce_activity():
    return {
        "tasks": [
            {"status": "SUCCESS", "submittedAt": "2026-03-03T00:00:00+0000", "executionTimeMs": 1234, "branch": "main"}
        ]
    }
