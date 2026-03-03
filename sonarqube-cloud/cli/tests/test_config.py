import pytest

from sonar_cli.config import get_settings


def test_missing_token_raises(monkeypatch):
    monkeypatch.delenv("SONAR_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="SONAR_TOKEN not set"):
        get_settings()


def test_default_org_and_base_url(monkeypatch):
    monkeypatch.setenv("SONAR_TOKEN", "abc")
    monkeypatch.delenv("SONAR_ORG", raising=False)
    monkeypatch.delenv("SONAR_BASE_URL", raising=False)
    settings = get_settings()
    assert settings.org == "nationalresearchcorporation"
    assert settings.base_url == "https://sonarcloud.io/api"


def test_custom_env_values(monkeypatch):
    monkeypatch.setenv("SONAR_TOKEN", "abc")
    monkeypatch.setenv("SONAR_ORG", "myorg")
    monkeypatch.setenv("SONAR_BASE_URL", "https://example.com/api")
    settings = get_settings()
    assert settings.token == "abc"
    assert settings.org == "myorg"
    assert settings.base_url == "https://example.com/api"
