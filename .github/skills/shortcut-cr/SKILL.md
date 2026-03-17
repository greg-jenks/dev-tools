---
name: shortcut-cr
description: Generate and post Change Request (CR) comments on Shortcut stories for NRC Health's production change process. Use when preparing stories for production deployment, generating CR comments, updating CR-related custom fields (Deploy to prod?, Deployed environment, CR created from template), checking CR readiness, or guiding engineers through the Shortcut workflow state transitions (Dev, Stage, Ready for Prod, Production, Accepted). Requires the Shortcut MCP server (@shortcut/mcp@latest).
---

# Shortcut CR Skill

Generate CR comments, update custom fields, and guide engineers through NRC Health's production change process in Shortcut.

**Requires:** Shortcut MCP server (`@shortcut/mcp@latest`) configured with a read-write API token.

## ⚠️ Custom Field Update Safety Protocol (NON-NEGOTIABLE)

The stories-update custom_fields parameter uses REPLACE semantics — it overwrites ALL custom fields on the story, not just the ones you include. Sending a partial array silently deletes every field you didn't include.

### Mandatory Fetch-Preserve-Verify Workflow

Every custom field update MUST follow this exact sequence:

1. FETCH: Call stories-get-by-id(storyPublicId=X, full=true) and capture ALL existing custom_fields
2. PRESERVE: Start with the complete existing custom_fields array
3. MODIFY: Add or replace only the field(s) you intend to change
4. UPDATE: Call stories-update with the full merged array
5. VERIFY: Call stories-get-by-id(storyPublicId=X, full=true) again and confirm:
   - The intended field was set correctly
   - All pre-existing fields are still present and unchanged

If step 5 reveals any field was dropped, STOP and report the issue immediately.

### Restricted Fields — Require Explicit User Instruction

These fields affect project tracking workflows and must NEVER be changed unless the user explicitly requests it in the current message:

| Field | Why it's restricted |
|-------|-------------------|
| Deployed environment | Represents deployment state; advancing it incorrectly breaks CR workflow tracking |
| Deploy to prod? | Gates the CR process; setting incorrectly skips required steps |

Before changing a restricted field, confirm: 'The user explicitly asked me to set [field] to [value] in this conversation.' If not, do NOT change it.

## Capabilities

1. **Generate CR comment** -- draft and post a structured CR comment on a Shortcut story
2. **Update custom fields** -- set engineer-owned fields (`Deploy to prod?`, `Deployed environment`, `CR created from template`)
3. **Check CR readiness** -- validate whether a story meets requirements for "Ready for Prod"
4. **Guide workflow** -- tell the engineer what's needed for the next state transition

## Workflow: Generate CR Comment

This is the primary use case. Follow these steps:

### Step 1: Gather Context

Determine what information is available and what to ask for:

**Always needed:**
- Shortcut story ID (e.g., `sc-67376`)

**Derive from context when possible, otherwise ask:**
- What changed (from conversation, git diff, PR description, or story description)
- Which repos/services are affected
- Risk level (Low / Medium / High)
- Change time (date + time + timezone, or leave as placeholder)

Use `stories-get-by-id` to fetch the story. Read the title, description, labels, and current workflow state to inform the CR content.

### Step 2: Draft the CR Comment

Load [references/examples.md](references/examples.md) for style guidance before drafting.

Use this exact template:

```
CHANGE REQUEST: <Short action-oriented title>

<1-3 sentences: what changed and why (business goal, not technical details)>

Change plan:
<Numbered or bulleted deployment steps. List each service/repo. Note deploy order if it matters.>

Verification plan:
<Specific steps to verify the deployment succeeded. Be concrete enough that a reviewer could follow them.>

Rollback plan:
<How to undo. Usually: deploy previous version of each service. Note if DB migrations complicate rollback.>

The links to OD/GHA deployment:
<Deployment links, one per service. Use "[To be added at deployment time]" if not yet available.>

---
Change Time: <MM/DD/YY - Time TZ, or "[To be scheduled]">
Risk: <Low / Medium / High>
```

**Title:** Action-oriented verb phrase: "Add X", "Fix Y", "Update Z". Not generic ("Sprint 5 work").

**Risk guidance:**
- **Low**: Additive feature, no DB migrations, no breaking changes, limited scope
- **Medium**: Schema changes, multiple services, shared component changes
- **High**: Data migrations, breaking API changes, security changes, high-traffic paths

### Step 3: Present for Review

Show the full drafted CR comment to the engineer. Ask:
1. Does this look accurate?
2. Want to adjust anything (risk level, steps, description)?
3. Ready to post it to the story?

Do NOT post automatically. Always get confirmation first.

### Step 4: Post and Update Fields

After the engineer approves:

1. Post the CR comment using stories-create-comment with the story ID and the CR text
2. Fetch the story using stories-get-by-id(full=true) to get current custom_fields
3. Set CR created from template = Yes by adding it to the EXISTING custom_fields array (do NOT send it alone)
4. Call stories-update with the complete merged custom_fields array
5. Verify by re-fetching the story and confirming all fields are intact
6. Confirm what was done and what's next

Example confirmation:
```
Posted CR comment to sc-67376
Set 'CR created from template' = Yes (preserved 3 existing custom fields)
Verified: all custom fields intact
Next: Get a peer or lead to reply "Approved" on the CR comment and set "CR Approved" = Yes
```

## Workflow: Check CR Readiness

When asked "is this story ready for prod?" or similar:

1. Fetch the story with `stories-get-by-id`
2. Check current workflow state
3. Evaluate against the readiness checklist:

| Requirement | How to Check |
|-------------|--------------|
| CR comment posted | Look for a comment starting with "CHANGE REQUEST:" |
| All template sections filled | CR comment has Change plan, Verification plan, Rollback plan, Deployment links |
| `CR created from template` = Yes | Check custom field value |
| `CR Approved` = Yes | Check custom field value |
| `Deployed environment` correct | Check custom field matches current state |

4. Report status with checkmarks:
```
For sc-67376 to move to "Completed (Ready for Prod)":
[x] CR comment posted (found comment from 02/24)
[x] "CR created from template" = Yes
[ ] No "Approved" reply from peer/lead
[ ] "CR Approved" not set to Yes

Remaining: Need peer/lead to approve the CR comment and set "CR Approved" = Yes.
```

## Workflow: Update Custom Fields

ALWAYS follow the Custom Field Update Safety Protocol above.

When asked to update fields, or as part of another workflow:

| Field | Valid Values | When to Set | Requires Explicit Ask? |
|-------|-------------|-------------|----------------------|
| Deploy to prod? | Yes, No | When scope is known | YES — never set proactively |
| Deployed environment | Develop, Stage, Ready for Prod, Production | As story progresses | YES — never advance proactively |
| CR created from template | Yes | After posting CR comment | No — implied by CR workflow |

Use stories-update with the appropriate custom field IDs, following the fetch-preserve-verify pattern.

Do NOT set CR Approved — that is the peer/lead reviewer's responsibility, not the engineer's.

## Workflow: Guide State Transitions

When asked "what do I need to do next?" or "how do I move this to prod?":

1. Fetch the story to determine current state
2. Load [references/cr-process.md](references/cr-process.md) for the full process
3. Tell the engineer exactly what's required for the NEXT transition
4. If multiple transitions away from production, give a summary of remaining steps

Focus on what the engineer needs to do NOW, not the entire process.

## Shortcut MCP Tools Reference

| Tool | Use For |
|------|---------|
| `stories-get-by-id` | Fetch story details, state, custom fields, comments |
| `stories-create-comment` | Post the CR comment |
| `stories-update` | Set custom fields |
| `stories-search` | Find related stories in a batch release |

## Custom Field IDs

Use these UUIDs with `stories-update` to set custom fields:

| Field | field_id | Value | value_id |
|-------|----------|-------|----------|
| **Deploy to prod?** | `67925032-1041-4ff8-a50a-9d1c23981a5c` | Yes | `67925032-ce04-41d4-8340-ba7c397ffeb1` |
| | | No | `67925032-df22-46eb-9f94-f7e4c7bd4c39` |
| **Deployed environment** | `671722a5-5d7e-4bb1-8b81-f35d40e3f647` | Develop | `671722a5-d21e-44d7-bcbc-f87e44e495e1` |
| | | Stage | `671722b8-ac82-4b7d-91c2-752d3602ec89` |
| | | Ready for Prod | `67c91849-06de-490d-8371-d30faa7aa1f7` |
| | | Production | `671722b8-3cc6-4185-89a3-55d6586d1b6a` |
| **CR created from template** | `68a61b44-f08c-4a76-9263-15b823973f56` | Yes | `68a61b44-59e7-427a-8fd6-4a5cb9491987` |
| **CR Approved** (read-only) | `68a7b256-d894-47f1-b705-db187fc86c9d` | Yes | `68a7b256-497d-459e-a3c6-cfdf5b9da84c` |

Example safe sequence to set `CR created from template` = Yes:
```
1) stories-get-by-id(storyPublicId=67376, full=true)
2) Start from existing custom_fields and add/replace:
   {field_id: "68a61b44-f08c-4a76-9263-15b823973f56", value_id: "68a61b44-59e7-427a-8fd6-4a5cb9491987"}
3) stories-update(storyPublicId=67376, custom_fields=<full merged array>)
4) stories-get-by-id(storyPublicId=67376, full=true) to verify no fields were dropped
```

## Important Rules

- **Never skip steps** in the workflow: Dev -> Stage -> Ready for Prod -> Production -> Accepted
- **Deployment links are OK as placeholders** -- they get added at actual deployment time, not when the CR is created
- **Same-version redeployments** with no config changes do NOT need a CR
- **Config/variable changes** DO need a full CR even without code changes
- **Multiple stories in a batch**: each story needs its own CR; cross-link in comments
