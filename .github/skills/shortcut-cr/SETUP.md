# Shortcut CR Skill — Setup Guide

Setup guide for installing the **shortcut-cr** skill and configuring the Shortcut MCP server across OpenCode, Claude Code, and VS Code Copilot.

**Time to set up:** ~10 minutes

---

## Prerequisites

- **Node.js 18+** (required to run the Shortcut MCP server via `npx`)
- **Shortcut API token** with read-write access (see below)

### Getting a Shortcut API Token

1. Go to [Shortcut Settings > API Tokens](https://app.shortcut.com/nrc-health/settings/account/api-tokens)
2. Click **Generate Token**
3. Name it something like `AI Tools` or `MCP Server`
4. Copy the token — you won't see it again

### Setting the Environment Variable

The Shortcut MCP server reads your token from the `SHORTCUT_API_TOKEN` environment variable.

**Windows (PowerShell — persistent, survives restarts):**
```powershell
[System.Environment]::SetEnvironmentVariable('SHORTCUT_API_TOKEN', 'your-token-here', 'User')
```
Then restart your terminal/IDE so it picks up the new variable.

**Mac / Linux (add to your shell profile):**
```bash
# Add to ~/.bashrc, ~/.zshrc, or equivalent:
export SHORTCUT_API_TOKEN="your-token-here"
```
Then `source ~/.zshrc` (or restart your terminal).

---

## 1. Skill Installation

The skill is a folder containing `SKILL.md` and a `references/` directory. It lives in this repo at `.github/skills/shortcut-cr/`.

### Do Both: Project-Level + Personal Install

**Project-level** gives you the skill automatically when working in this repo. **Personal install** gives you the skill everywhere — any NRC repo, any project. The CR process applies across all our services, so you want it available everywhere.

**We recommend doing both.** Project-level is already done (it's in this repo). Personal install takes 30 seconds.

### Project-Level (Already Done)

The skill is checked into this repo at:

```
dev-tools/.github/skills/shortcut-cr/
  SKILL.md
  references/
    cr-process.md
    examples.md
```

**Works automatically in:** Claude Code and VS Code Copilot when you have this repo open. No action needed.

**OpenCode:** Does not auto-discover project-level skills. Use the personal install below.

### Personal Install (Recommended — Works Everywhere)

Copy the skill to your home directory so it's available in every repo you open. The CR process applies to all NRC production deployments — survey-management-api, survey-fielding-api, survey-management-web, survey-fielding-web, and anything else that ships to prod.

**Claude Code:**

```powershell
# Windows
New-Item -ItemType Directory -Force -Path "$HOME\.claude\skills\shortcut-cr\references"
Copy-Item ".github\skills\shortcut-cr\SKILL.md" "$HOME\.claude\skills\shortcut-cr\"
Copy-Item ".github\skills\shortcut-cr\references\*" "$HOME\.claude\skills\shortcut-cr\references\"
```

```bash
# Mac / Linux
mkdir -p ~/.claude/skills/shortcut-cr/references
cp .github/skills/shortcut-cr/SKILL.md ~/.claude/skills/shortcut-cr/
cp .github/skills/shortcut-cr/references/* ~/.claude/skills/shortcut-cr/references/
```

Skill directory: `~/.claude/skills/shortcut-cr/`

**VS Code Copilot:**

VS Code Copilot discovers skills from `~/.claude/skills/` automatically, so if you did the Claude Code step above, you're already covered.

If you prefer a separate location:

```powershell
# Windows
New-Item -ItemType Directory -Force -Path "$HOME\.copilot\skills\shortcut-cr\references"
Copy-Item ".github\skills\shortcut-cr\SKILL.md" "$HOME\.copilot\skills\shortcut-cr\"
Copy-Item ".github\skills\shortcut-cr\references\*" "$HOME\.copilot\skills\shortcut-cr\references\"
```

Skill directory: `~/.copilot/skills/shortcut-cr/`

**OpenCode:**

OpenCode doesn't have a skills discovery directory yet. Add a reference in your AGENTS.md (typically at `~/.config/opencode/AGENTS.md`):

```markdown
## Skills

- When asked about Change Requests or CRs, read the skill at `~/.claude/skills/shortcut-cr/SKILL.md` first.
```

This way OpenCode picks it up from the same personal install you did for Claude Code.

---

## 2. MCP Server Configuration

Each tool needs the Shortcut MCP server configured so the skill can read and write stories. You need this regardless of which tool you use.

### OpenCode

Edit `~/.config/opencode/opencode.json` and add to the `"mcp"` section:

```json
{
  "mcp": {
    "shortcut": {
      "type": "local",
      "command": ["npx", "-y", "@shortcut/mcp@latest"],
      "enabled": true,
      "environment": {
        "SHORTCUT_API_TOKEN": "{env:SHORTCUT_API_TOKEN}"
      }
    }
  }
}
```

> **Note:** `{env:SHORTCUT_API_TOKEN}` tells OpenCode to read from your environment variable. Do NOT paste the raw token here.

### Claude Code

Edit `~/.claude/settings.json` (personal) or `.claude/settings.json` (project-level):

```json
{
  "mcpServers": {
    "shortcut": {
      "command": "npx",
      "args": ["-y", "@shortcut/mcp@latest"],
      "env": {
        "SHORTCUT_API_TOKEN": "${SHORTCUT_API_TOKEN}"
      }
    }
  }
}
```

> **Note:** Claude Code uses `${VAR}` syntax (not `{env:VAR}`).

### VS Code Copilot

Create or edit `.vscode/mcp.json` in your project root:

```json
{
  "servers": {
    "shortcut": {
      "command": "npx",
      "args": ["-y", "@shortcut/mcp@latest"],
      "env": {
        "SHORTCUT_API_TOKEN": "${SHORTCUT_API_TOKEN}"
      }
    }
  }
}
```

Or add it in VS Code settings (JSON) so it applies to all projects:

```json
{
  "mcp": {
    "servers": {
      "shortcut": {
        "command": "npx",
        "args": ["-y", "@shortcut/mcp@latest"],
        "env": {
          "SHORTCUT_API_TOKEN": "${SHORTCUT_API_TOKEN}"
        }
      }
    }
  }
}
```

---

## 3. Verification

After setup, verify everything works in your AI tool of choice.

### Quick Test

Say to your AI assistant:

> "Use the shortcut-cr skill to check the CR readiness of sc-67646"

**Expected behavior:**
1. The assistant loads the skill (you may see it reference SKILL.md)
2. It calls `stories-get-by-id` to fetch the story
3. It checks the custom fields and comments
4. It reports a checklist of CR readiness items

### If It Doesn't Work

| Symptom | Fix |
|---------|-----|
| "No MCP tool named stories-get-by-id" | MCP server not configured — check Section 2 |
| "Authentication failed" or 401 error | `SHORTCUT_API_TOKEN` not set or invalid — check env var |
| "Skill not found" or no skill behavior | Skill files not in the right directory — check Section 1 |
| npx hangs or fails | Node.js not installed or `npx` not on PATH |

### Verify MCP Server Independently

You can test the MCP server outside of any AI tool:

```powershell
# Should start without errors (Ctrl+C to stop)
npx -y @shortcut/mcp@latest
```

If this hangs waiting for input, that's correct — it's waiting for MCP protocol messages.

### Verify Environment Variable

```powershell
# Windows PowerShell
$env:SHORTCUT_API_TOKEN
# Should print your token (not empty)
```

```bash
# Mac / Linux
echo $SHORTCUT_API_TOKEN
# Should print your token (not empty)
```

---

## Quick Reference

| Component | OpenCode | Claude Code | VS Code Copilot |
|-----------|----------|-------------|-----------------|
| **Skill (project)** | AGENTS.md reference | `.github/skills/shortcut-cr/` | `.github/skills/shortcut-cr/` |
| **Skill (personal)** | AGENTS.md reference | `~/.claude/skills/shortcut-cr/` | `~/.copilot/skills/shortcut-cr/` |
| **MCP config file** | `~/.config/opencode/opencode.json` | `~/.claude/settings.json` | `.vscode/mcp.json` |
| **Env var syntax** | `{env:SHORTCUT_API_TOKEN}` | `${SHORTCUT_API_TOKEN}` | `${SHORTCUT_API_TOKEN}` |
| **Token env var** | `SHORTCUT_API_TOKEN` | `SHORTCUT_API_TOKEN` | `SHORTCUT_API_TOKEN` |
