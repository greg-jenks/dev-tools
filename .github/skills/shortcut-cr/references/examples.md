# CR Comment Examples

Reference examples for generating CR comments. Load this file when generating a new CR comment to match the expected style and level of detail.

## Example 1: Multi-Service Deployment (Transparency)

This is a real CR from a multi-service deployment. Note the clear structure: what's changing, deploy order, verification, rollback mirrors deploy order.

```
CHANGE REQUEST: Add Amplitude to Transparency

Description
The goal is to:
- Automatically track user interactions (clicks, page views, form inputs, etc.)
- Activate the Session replays module

Change plan:
Deploy Cron Service
Deploy Portal Service
Deploy Queue Service
Deploy Survey Service
Deploy Widget Service

Verification plan:
Smoke testing
Review user interactions in Amplitude for the project Transparency - PRD

Rollback plan:
Deploy each service's previous, working release

Deploy Cron Service
Deploy Portal Service
Deploy Queue Service
Deploy Survey Service
Deploy Widget Service

The links to OD/GHA deployment:
https://build.nationalresearch.com:4443/app#/Spaces-1/projects/transparency-app-cron/deployments?groupBy=Channel
https://build.nationalresearch.com:4443/app#/Spaces-1/projects/transparency-app/deployments?groupBy=Channel
https://build.nationalresearch.com:4443/app#/Spaces-1/projects/transparency-app-queue/deployments?groupBy=Channel
https://build.nationalresearch.com:4443/app#/Spaces-1/projects/transparency-app-survey/deployments?groupBy=Channel
https://build.nationalresearch.com:4443/app#/Spaces-1/projects/transparency-app-widget/deployments?groupBy=Channel
```

### What makes this effective:
- **Clear title** summarizing the change in a few words
- **Description** explains the "why" (business goal), not just the "what"
- **Change plan** lists each service to deploy -- the reader knows exactly what's happening
- **Verification plan** is specific: smoke testing + checking a specific tool (Amplitude) for a specific project
- **Rollback plan** mirrors the change plan -- deploy previous version of each service
- **Deployment links** are provided for each service individually

## Example 2: Survey Platform Feature (Template)

A typical single-repo or dual-repo (API + web) CR for the survey management platform:

```
CHANGE REQUEST: Provider Quota Export Feature

Add ability to export quota data by panel provider with vendor alias filtering and Excel formatting.

Change plan:
1. Deploy survey-management-api via GHA to Production
2. Deploy survey-management-web via GHA to Production
3. API must deploy first (backend dependency)

Verification plan:
1. Navigate to Quotas > Provider Export
2. Export with vendor alias filter -- verify Excel output
3. Export without filter -- verify all providers included
4. Verify 404 response for surveys with no providers

Rollback plan:
1. Revert survey-management-api to previous version via GHA
2. Revert survey-management-web to previous version via GHA
3. No DB migrations -- feature is additive only

The links to OD/GHA deployment:
[To be added at deployment time]

---
Change Time: [To be scheduled]
Risk: Low
```

### What makes this effective:
- **Deploy order matters** and is called out (API before web)
- **Verification plan** has specific test steps a reviewer can follow
- **Rollback plan** notes there are no DB migrations (important for rollback confidence)
- **Risk: Low** because the feature is additive with no schema changes

## Writing Guidance

### Title
- Short, descriptive: "Add Amplitude to Transparency", "Fix Survey Export Timeout"
- Action-oriented: starts with a verb (Add, Fix, Update, Remove, Migrate)
- Avoid generic titles like "Release 2.5" or "Sprint work"

### Description
- 1-3 sentences explaining the business goal or problem being solved
- Focus on "why" not "how"

### Change Plan
- List each deployment step in order
- If order matters (e.g., API before web), say so explicitly
- For multi-service deploys, list each service

### Verification Plan
- Specific steps someone else could follow to verify the change works
- Include what to check, where to check it, and expected outcome
- "Smoke testing" alone is acceptable for low-risk changes but more detail is better

### Rollback Plan
- How to undo the change if something goes wrong
- Usually: deploy previous version of each service
- Note if there are DB migrations (makes rollback harder) or if the change is additive-only (easier)

### Deployment Links
- One link per service/repo being deployed
- GHA pattern: `https://github.com/nrchealth/<repo>/actions` (specific run URL added at deployment)
- Can be left as placeholder `[To be added at deployment time]` when creating the CR before deployment

### Change Time
- Date and time with timezone: "02/25/26 - 2:00 PM CST"
- Can be placeholder `[To be scheduled]` if not yet determined

### Risk Level
- **Low**: Additive feature, no DB migrations, no breaking changes, limited scope
- **Medium**: Schema changes, multiple services affected, changes to shared components
- **High**: Data migrations, breaking API changes, security-related changes, high-traffic paths
