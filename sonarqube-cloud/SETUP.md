# SonarCloud CLI + Skill Setup

## Prerequisites

- Python 3.10+
- pip

## Create SonarCloud token

1. Open `https://sonarcloud.io/account/security`.
2. Create a personal access token.
3. Note: inactive tokens expire after 60 days.

## Set environment variables

### Windows PowerShell

```powershell
$env:SONAR_TOKEN = "your_token_here"
$env:SONAR_ORG = "nationalresearchcorporation"
```

### Mac/Linux bash

```bash
export SONAR_TOKEN="your_token_here"
export SONAR_ORG="nationalresearchcorporation"
```

`SONAR_ORG` is optional; default is `nationalresearchcorporation`.

## Install CLI

From `dev-tools` repo root:

```bash
pip install -e sonarqube-cloud/cli
```

For development dependencies:

```bash
pip install -e "sonarqube-cloud/cli[dev]"
```

## Install skill

### OpenCode

1. Copy `sonarqube-cloud/skill` to `~/.config/opencode/skills/sonarcloud-quality/`.
2. Add the skill reference to your project `AGENTS.md` (required, no auto-discovery).

### Claude Code

Copy `sonarqube-cloud/skill` to `~/.claude/skills/`.

### VS Code Copilot

Copy `sonarqube-cloud/skill` to `.github/skills/` in-repo or `~/.copilot/skills/` globally.

## Verify

```bash
sonar --help
sonar projects --output json
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `SONAR_TOKEN not set` | Token not exported | Export `SONAR_TOKEN` and rerun |
| 401/403 from API | Token invalid/expired | Regenerate token and update env var |
| Empty project list | Wrong org | Set `SONAR_ORG` correctly |
| Retries then failure | Rate limit/service issue | Retry later; reduce request frequency |
| `NO_ANALYSIS` | CI analysis not complete | Push branch and wait for analysis |
