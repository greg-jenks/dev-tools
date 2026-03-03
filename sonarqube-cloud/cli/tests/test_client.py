import httpx
import pytest

from sonar_cli.client import SonarCloudClient, SonarCloudError
from sonar_cli.config import Settings


def test_retry_on_429_then_success():
    calls = {"count": 0}
    sleeps: list[int] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(429, json={"errors": [{"msg": "rate limited"}]})
        return httpx.Response(200, json={"components": [], "paging": {"total": 0}})

    transport = httpx.MockTransport(handler)
    client = SonarCloudClient(
        Settings(token="t", org="o", base_url="https://sonarcloud.io/api"),
        http_client=httpx.Client(transport=transport, base_url="https://sonarcloud.io/api"),
        sleeper=lambda sec: sleeps.append(sec),
    )
    try:
        client.search_components()
    finally:
        client.close()
    assert calls["count"] == 2
    assert sleeps == [1]


def test_retry_on_503_then_success():
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            return httpx.Response(503, json={"errors": [{"msg": "temporary"}]})
        return httpx.Response(200, json={"components": [], "paging": {"total": 0}})

    transport = httpx.MockTransport(handler)
    client = SonarCloudClient(
        Settings(token="t", org="o", base_url="https://sonarcloud.io/api"),
        http_client=httpx.Client(transport=transport, base_url="https://sonarcloud.io/api"),
        sleeper=lambda sec: None,
    )
    try:
        client.search_components()
    finally:
        client.close()
    assert calls["count"] == 2


def test_max_retries_exceeded_raises():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, json={"errors": [{"msg": "down"}]})

    transport = httpx.MockTransport(handler)
    client = SonarCloudClient(
        Settings(token="t", org="o", base_url="https://sonarcloud.io/api"),
        http_client=httpx.Client(transport=transport, base_url="https://sonarcloud.io/api"),
        sleeper=lambda sec: None,
    )
    with pytest.raises(SonarCloudError, match="down"):
        client.search_components()
    client.close()


def test_pagination_collects_all_pages():
    def handler(request: httpx.Request) -> httpx.Response:
        page = int(request.url.params.get("p", "1"))
        if page == 1:
            return httpx.Response(200, json={"issues": [{"key": "1"}], "paging": {"total": 101}})
        return httpx.Response(200, json={"issues": [{"key": "2"}], "paging": {"total": 101}})

    transport = httpx.MockTransport(handler)
    client = SonarCloudClient(
        Settings(token="t", org="o", base_url="https://sonarcloud.io/api"),
        http_client=httpx.Client(transport=transport, base_url="https://sonarcloud.io/api"),
        sleeper=lambda sec: None,
    )
    try:
        issues = client.search_issues("proj")
    finally:
        client.close()
    assert [i["key"] for i in issues] == ["1", "2"]


def test_auth_header_set_correctly_without_custom_http_client(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer secret"
        return httpx.Response(200, json={"components": [], "paging": {"total": 0}})

    transport = httpx.MockTransport(handler)
    real_client = httpx.Client

    def client_factory(*args, **kwargs):
        kwargs["transport"] = transport
        return real_client(*args, **kwargs)
    monkeypatch.setattr(httpx, "Client", client_factory)
    client = SonarCloudClient(
        Settings(token="secret", org="o", base_url="https://sonarcloud.io/api"),
        sleeper=lambda sec: None,
    )
    client.search_components()
    client.close()


def test_error_mapping_raises_sonar_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"errors": [{"msg": "invalid project"}]})

    transport = httpx.MockTransport(handler)
    client = SonarCloudClient(
        Settings(token="t", org="o", base_url="https://sonarcloud.io/api"),
        http_client=httpx.Client(transport=transport, base_url="https://sonarcloud.io/api"),
        sleeper=lambda sec: None,
    )
    with pytest.raises(SonarCloudError, match="invalid project"):
        client.search_components()
    client.close()


def test_search_issues_supports_files_and_statuses_filters():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["files"] = request.url.params.get("files")
        captured["statuses"] = request.url.params.get("statuses")
        return httpx.Response(200, json={"issues": [], "paging": {"total": 0}})

    transport = httpx.MockTransport(handler)
    client = SonarCloudClient(
        Settings(token="t", org="o", base_url="https://sonarcloud.io/api"),
        http_client=httpx.Client(transport=transport, base_url="https://sonarcloud.io/api"),
        sleeper=lambda sec: None,
    )
    try:
        client.search_issues("proj", files="src/a.py,src/b.py", statuses="OPEN,CONFIRMED")
    finally:
        client.close()
    assert captured["files"] == "src/a.py,src/b.py"
    assert captured["statuses"] == "OPEN,CONFIRMED"
