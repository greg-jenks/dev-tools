from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    token: str
    org: str = "nationalresearchcorporation"
    base_url: str = "https://sonarcloud.io/api"


def get_settings() -> Settings:
    token = os.environ.get("SONAR_TOKEN", "").strip()
    if not token:
        raise RuntimeError("SONAR_TOKEN not set. Export SONAR_TOKEN with your SonarCloud PAT.")
    org = os.environ.get("SONAR_ORG", "nationalresearchcorporation").strip() or "nationalresearchcorporation"
    base_url = os.environ.get("SONAR_BASE_URL", "https://sonarcloud.io/api").strip() or "https://sonarcloud.io/api"
    return Settings(token=token, org=org, base_url=base_url.rstrip("/"))
