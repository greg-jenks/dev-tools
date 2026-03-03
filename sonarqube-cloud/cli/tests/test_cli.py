import json

from typer.testing import CliRunner

from sonar_cli.commands.analysis import _wait_for_terminal_status
from sonar_cli.main import app

runner = CliRunner()


class DummyClient:
    def __init__(self, responses):
        self._responses = list(responses)
        self._index = 0

    def close(self):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()

    def search_components(self):
        return [{"key": "proj", "name": "Project"}]

    def project_quality_gate_status(self, project, branch=None, pr=None):
        return {"projectStatus": {"status": "ERROR", "conditions": []}}

    def search_quality_profiles(self, project):
        return [{"key": "p1"}, {"key": "p2"}]

    def search_rules(self, qprofile, language=None):
        return [{"key": "typescript:S1", "name": "Rule"}]

    def ce_activity(self, project, branch=None):
        if not self._responses:
            return {"tasks": []}
        current = self._responses[min(self._index, len(self._responses) - 1)]
        self._index += 1
        return current


def test_projects_json_cli(monkeypatch):
    from sonar_cli.commands import projects as projects_cmd

    monkeypatch.setattr(projects_cmd, "get_settings", lambda: object())
    monkeypatch.setattr(projects_cmd, "SonarCloudClient", lambda settings: DummyClient([]))
    result = runner.invoke(app, ["projects", "--output", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload[0]["key"] == "proj"


def test_quality_gate_failed_exit_code(monkeypatch):
    from sonar_cli.commands import quality_gate as gate_cmd

    monkeypatch.setattr(gate_cmd, "get_settings", lambda: object())
    monkeypatch.setattr(gate_cmd, "SonarCloudClient", lambda settings: DummyClient([]))
    result = runner.invoke(app, ["quality-gate", "proj", "--output", "json"])
    assert result.exit_code == 1


def test_rules_list_dedupes_rule_keys(monkeypatch):
    from sonar_cli.commands import rules as rules_cmd

    monkeypatch.setattr(rules_cmd, "get_settings", lambda: object())
    monkeypatch.setattr(rules_cmd, "SonarCloudClient", lambda settings: DummyClient([]))
    result = runner.invoke(app, ["rules", "list", "proj", "--output", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert len(payload) == 1
    assert payload[0]["key"] == "typescript:S1"


def test_wait_for_terminal_status_pending_to_success():
    client = DummyClient(
        [
            {"tasks": [{"status": "PENDING"}]},
            {"tasks": [{"status": "SUCCESS"}]},
        ]
    )
    calls = {"sleep": 0}

    def fake_sleep(_seconds):
        calls["sleep"] += 1

    now = {"v": 0}

    def fake_time():
        now["v"] += 1
        return now["v"]

    status, payload = _wait_for_terminal_status(client, "proj", "main", 30, sleeper=fake_sleep, time_fn=fake_time)
    assert status == "SUCCESS"
    assert payload["status"] == "SUCCESS"
    assert calls["sleep"] == 1


def test_wait_for_terminal_status_timeout():
    client = DummyClient([{"tasks": [{"status": "IN_PROGRESS"}]}])
    now = {"v": 0}

    def fake_time():
        now["v"] += 20
        return now["v"]

    status, payload = _wait_for_terminal_status(client, "proj", "main", 10, sleeper=lambda _s: None, time_fn=fake_time)
    assert status == "TIMEOUT"
    assert payload["status"] == "TIMEOUT"
