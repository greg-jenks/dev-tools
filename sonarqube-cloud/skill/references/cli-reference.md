# Sonar CLI Reference

## Global

- `sonar --help`
- `sonar --version`

## Commands

### `sonar projects`

List org projects.

Flags:
- `--output [table|json]`

Example:
- `sonar projects --output json`

### `sonar rules list <project>`

List active rules from quality profiles.

Flags:
- `--language <lang>`
- `--output [table|json]`

Example:
- `sonar rules list survey-management-web --language ts --output json`

### `sonar rules show <rule-key>`

Show rule details and remediation.

Flags:
- `--output [table|json]`

Example:
- `sonar rules show typescript:S6759 --output json`

### `sonar issues <project>`

List issues.

Flags:
- `--branch <branch>`
- `--pr <number>`
- `--new`
- `--impact [HIGH|MEDIUM|LOW]`
- `--quality [RELIABILITY|SECURITY|MAINTAINABILITY]`
- `--severity [INFO|MINOR|MAJOR|CRITICAL|BLOCKER]`
- `--type [BUG|VULNERABILITY|CODE_SMELL]`
- `--output [table|json]`

Example:
- `sonar issues survey-management-web --branch feature/my-branch --new --output json`

### `sonar quality-gate <project>`

Check quality gate status.

Flags:
- `--branch <branch>`
- `--pr <number>`
- `--output [table|json]`

Exit codes:
- `0` passed
- `1` failed

Example:
- `sonar quality-gate survey-management-web --branch feature/my-branch --output json`

### `sonar measures <project>`

Show project metrics.

Flags:
- `--branch <branch>`
- `--metrics <csv>`
- `--output [table|json]`

Default metrics:
- coverage, reliability_rating, security_rating, sqale_rating, duplicated_lines_density, ncloc, bugs, vulnerabilities, code_smells

Example:
- `sonar measures survey-management-web --output json`

### `sonar analysis-status <project>`

Check latest analysis task state from Compute Engine.

Flags:
- `--branch <branch>`
- `--wait`
- `--timeout <seconds>` (default 300)
- `--output [table|json]`

Exit codes:
- `0` success
- `1` failed or no analysis
- `2` timeout

Example:
- `sonar analysis-status survey-management-web --branch feature/my-branch --wait --timeout 300 --output json`

## JSON response shapes (examples)

Projects:
```json
[{"key":"survey-management-web","name":"Survey Management Web"}]
```

Rules list:
```json
[{"key":"typescript:S6759","impacts":[{"softwareQuality":"MAINTAINABILITY","severity":"HIGH"}],"severity":"MAJOR","type":"CODE_SMELL"}]
```

Rule show:
```json
{"rule":{"key":"typescript:S6759","name":"...","htmlDesc":"<p>...</p>"}}
```

Issues:
```json
[{"key":"AX1","rule":"typescript:S6759","impacts":[{"softwareQuality":"SECURITY","severity":"MEDIUM"}],"severity":"CRITICAL","type":"VULNERABILITY"}]
```

Quality gate:
```json
{"projectStatus":{"status":"OK","conditions":[]}}
```

Measures:
```json
{"component":{"measures":[{"metric":"coverage","value":"85.2"}]}}
```

Analysis status:
```json
{"status":"SUCCESS","tasks":[{"status":"SUCCESS","submittedAt":"2026-03-03T00:00:00+0000"}]}
```

## Error handling

- Missing token: `SONAR_TOKEN not set`
- Invalid project/rule: SonarCloud API error with response message
- Rate limiting: automatic retries for HTTP 429/503 (1s, 2s, 4s)
- Analysis not ready: `NO_ANALYSIS`, `PENDING`, or `IN_PROGRESS`
