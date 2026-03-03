---
name: sonarcloud-quality
description: >
  Pre-PR quality gate checking, SonarCloud rule lookup, code smell detection,
  static analysis, sonar, sonarqube, sonarcloud, quality gate, code quality
---

# SonarCloud Quality Skill

Use this skill to check SonarCloud quality requirements before opening PRs.
Known project keys: `survey-management-api`, `survey-management-web`, `survey-fielding-api`.

## Workflow 1: Pre-flight

1. Read `sonar-project.properties` and use `sonar.projectKey`.
2. Use org from `SONAR_ORG` env var (never from properties file).
3. Run `sonar rules list <project-key> --output json`.
4. Focus on rules for modified file languages.
5. Implement code to match those patterns before commit.

## Workflow 2: Pre-PR check

1. Detect project key from `sonar-project.properties`.
2. Detect branch: `git branch --show-current`.
3. Run `sonar analysis-status <project-key> --branch <branch> --output json`.
4. If status is `PENDING` or `IN_PROGRESS`, wait and re-run (or use `--wait`).
5. If status is `NO_ANALYSIS`, ask user to push and wait for CI.
6. If status is `SUCCESS`, run `sonar quality-gate <project-key> --branch <branch> --output json`.
7. If gate fails, run `sonar issues <project-key> --branch <branch> --new --output json`.
8. Group issues by rule and run `sonar rules show <rule-key> --output json` for each.
9. Fix code, commit, and push.
10. Loop back to step 3 after each push and repeat until analysis is `SUCCESS` and quality gate is passing.

## Workflow 3: Fix mode

1. Run `sonar issues <project-key> --branch <branch> --output json` (or `--pr <number>`).
2. Group by `rule`.
3. For each rule, run `sonar rules show <rule-key> --output json`.
4. Prioritize fixes by impact: HIGH, then MEDIUM, then LOW.
5. Re-run issues and quality gate checks.

## Rules of use

- Prefer Clean Code filters: `--impact` and `--quality`.
- Use legacy filters (`--severity`, `--type`) only for compatibility.
- Always use `--output json` when running as an agent.
