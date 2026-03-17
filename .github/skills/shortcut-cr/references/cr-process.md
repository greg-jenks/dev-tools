# Production Change Process

Reference for the full NRC Health production change process. Load this file when guiding engineers through workflow transitions or validating CR readiness.

## Custom Shortcut Fields

| Field | Values | Who Sets It | When |
|-------|--------|-------------|------|
| **Deploy to prod?** | Yes / No | Engineer | At story creation or when scope is known |
| **Deployed environment** | Develop / Stage / Ready for Prod / Production | Engineer | Updated as story progresses through environments |
| **CR created from template** | Yes | Engineer (via this skill) | After posting CR comment |
| **CR Approved** | Yes | Peer or lead reviewer | After reviewing and approving the CR comment |

## Workflow States

```
Backlog -> Ready -> In Process -> Completed (Dev) -> Completed (Stage) -> Completed (Ready for Prod) -> Completed (Production) -> Accepted
```

### Transition Requirements

**Backlog -> Ready**
- Story defined and accepted (meets Definition of Ready)
- `Deploy to prod?` field set

**Ready -> In Process**
- Development started

**In Process -> Completed (Dev)**
- Code completed, tests passed
- DoD met: peer review, quality/security gates, test coverage

**Completed (Dev) -> Completed (Stage)**
- Deployed to Stage environment
- Stage verification complete
- `Deployed environment` = Stage

**Completed (Stage) -> Completed (Ready for Prod)**
- CR comment posted using template (ALL sections required)
- `CR created from template` = Yes
- Peer/lead replied "Approved" to CR comment
- `CR Approved` = Yes (set by peer/lead)
- Release communicated with PSG if needed
- `Deployed environment` = Ready for Prod

**Completed (Ready for Prod) -> Completed (Production)**
- Post notification to #info-change Slack channel (work started, story links)
- Deployment finished, final checks passed, verification completed
- Post completion notification to #info-change Slack channel
- `Deployed environment` = Production

**Completed (Production) -> Accepted**
- Stakeholders confirm production is stable and correct
- May wait for client feedback depending on PM preference
- Final state

## Important Rules

- **Order and timelines matter** -- compliance, DORA metrics, PSG awareness
- **No skipping steps** -- every state transition has requirements
- Stories with `Deploy to prod? = No` should never appear as Completed/Accepted with Production environment
- Multiple stories in a release batch: each follows process individually; cross-link in comments, use custom labels to group
- **Same-version redeployments** (no config/variable changes) are NOT changes -- no CR needed
- **Configuration/variable updates** ARE changes -- full CR process required

## CR Readiness Checklist

Before a story can move to "Completed (Ready for Prod)":

1. CR comment posted on the story (using the template format)
2. All template sections filled in (deployment links can be placeholder)
3. `CR created from template` = Yes
4. Peer or lead has replied "Approved" on the CR comment
5. `CR Approved` = Yes
6. `Deployed environment` = Ready for Prod
