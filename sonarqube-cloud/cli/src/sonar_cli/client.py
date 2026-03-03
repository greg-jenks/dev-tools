from __future__ import annotations

import json
import sys
import time
from typing import Any

import httpx

from .config import Settings


class SonarCloudError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"SonarCloud API error ({status_code}): {message}")
        self.status_code = status_code
        self.message = message


class SonarCloudClient:
    def __init__(
        self,
        settings: Settings,
        *,
        http_client: httpx.Client | None = None,
        sleeper: Any = None,
    ) -> None:
        self.settings = settings
        self._sleeper = sleeper or time.sleep
        self._client = http_client or httpx.Client(
            base_url=settings.base_url,
            headers={"Authorization": f"Bearer {settings.token}"},
            timeout=30.0,
        )

    def close(self) -> None:
        self._client.close()

    def _extract_error_message(self, response: httpx.Response) -> str:
        try:
            data = response.json()
            if isinstance(data, dict):
                errors = data.get("errors")
                if isinstance(errors, list) and errors and isinstance(errors[0], dict):
                    msg = errors[0].get("msg")
                    if msg:
                        return str(msg)
                for key in ("message", "error", "msg"):
                    if data.get(key):
                        return str(data[key])
        except (ValueError, json.JSONDecodeError):
            pass
        return response.text or "Unknown error"

    def _request(self, method: str, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        retries = [1, 2, 4]
        request_params = params or {}
        for attempt in range(len(retries) + 1):
            response = self._client.request(method, path, params=request_params)
            if response.status_code not in (429, 503):
                break
            if attempt >= len(retries):
                break
            delay = retries[attempt]
            print(f"Retrying {path} after HTTP {response.status_code} in {delay}s...", file=sys.stderr)
            self._sleeper(delay)
        if response.status_code >= 400:
            raise SonarCloudError(response.status_code, self._extract_error_message(response))
        return response.json()

    def _paginate(self, path: str, params: dict[str, Any], list_key: str) -> list[dict[str, Any]]:
        page = 1
        page_size = 100
        collected: list[dict[str, Any]] = []
        while True:
            current = dict(params)
            current["p"] = page
            current["ps"] = page_size
            data = self._request("GET", path, current)
            items = data.get(list_key, [])
            if isinstance(items, list):
                collected.extend(items)
            paging = data.get("paging", {}) or {}
            total = int(paging.get("total", len(collected)))
            if page * page_size >= total:
                break
            page += 1
        return collected

    def search_components(self) -> list[dict[str, Any]]:
        return self._paginate(
            "/components/search",
            {"organization": self.settings.org, "qualifiers": "TRK"},
            "components",
        )

    def search_quality_profiles(self, project: str) -> list[dict[str, Any]]:
        return self._paginate(
            "/qualityprofiles/search",
            {"organization": self.settings.org, "project": project},
            "profiles",
        )

    def search_rules(self, quality_profile: str, language: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"organization": self.settings.org, "activation": "true", "qprofile": quality_profile}
        if language:
            params["languages"] = language
        return self._paginate("/rules/search", params, "rules")

    def show_rule(self, rule_key: str) -> dict[str, Any]:
        return self._request("GET", "/rules/show", {"organization": self.settings.org, "key": rule_key})

    def search_issues(
        self,
        project: str,
        branch: str | None = None,
        pr: str | None = None,
        since_leak_period: bool = False,
        impact: str | None = None,
        quality: str | None = None,
        severity: str | None = None,
        issue_type: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"organization": self.settings.org, "components": project}
        if branch:
            params["branch"] = branch
        if pr:
            params["pullRequest"] = pr
        if since_leak_period:
            params["sinceLeakPeriod"] = "true"
        if impact:
            params["impactSeverities"] = impact
        if quality:
            params["impactSoftwareQualities"] = quality
        if severity:
            params["severities"] = severity
        if issue_type:
            params["types"] = issue_type
        return self._paginate("/issues/search", params, "issues")

    def project_quality_gate_status(self, project: str, branch: str | None = None, pr: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"organization": self.settings.org, "projectKey": project}
        if branch:
            params["branch"] = branch
        if pr:
            params["pullRequest"] = pr
        return self._request("GET", "/qualitygates/project_status", params)

    def component_measures(self, project: str, metrics: str, branch: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"organization": self.settings.org, "component": project, "metricKeys": metrics}
        if branch:
            params["branch"] = branch
        return self._request("GET", "/measures/component", params)

    def ce_activity(self, project: str, branch: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"organization": self.settings.org, "component": project}
        if branch:
            params["branch"] = branch
        return self._request("GET", "/ce/activity", params)
