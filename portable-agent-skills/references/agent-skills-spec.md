# Agent Skills format + client discovery paths

Condensed from the Agent Skills specification (agentskills.io/specification) and the Cursor
skills docs (cursor.com/help/customization/skills). Verified 2026-10. Re-verify paths against
vendor docs before publishing them — clients move.

## Directory structure

A skill is a directory containing at minimum a `SKILL.md`:

```
skill-name/
├── SKILL.md        # Required: metadata + instructions
├── scripts/        # Optional: executable code
├── references/     # Optional: documentation
├── assets/         # Optional: templates, resources
└── ...             # Any additional files or directories
```

## Frontmatter fields

| Field | Required | Constraint |
|-------|----------|------------|
| `name` | yes | Max 64 chars. Lowercase alphanumerics and hyphens only. Must not start or end with a hyphen. No consecutive hyphens. **Must match the parent directory name.** |
| `description` | yes | Max 1024 chars, non-empty. Describes what the skill does and when to use it. |
| `license` | no | License name, or reference to a bundled license file. Keep short. |
| `compatibility` | no | Max 500 chars. Environment requirements (intended product, system packages, network access). Most skills do not need it. |
| `metadata` | no | Arbitrary string→string map for properties the spec does not define. Use reasonably unique key names to avoid collisions. |
| `allowed-tools` | no | Space-separated string of pre-approved tools. Experimental, support varies between implementations. |

Minimal example:

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

Body content: markdown after the frontmatter, no format restrictions.

### Context budget

- Metadata (name + description) is loaded **at startup for all skills** — roughly 100 tokens each.
  This is why frontmatter must stay lean.
- Full instructions: **under 5000 tokens recommended**, and only loaded when the skill is used.

### Client-specific extra fields

Unknown frontmatter fields are ignored by clients that don't define them, so extras are safe to
carry. Known ones:

- `disable-model-invocation: true` — Claude Code. The user must invoke the skill; the model cannot
  auto-trigger it. Used on user-triggered modes (`/ask`, `/plan`, `/suggestion`, `/implement`).
- `paths: ["**/*.tsx"]` — Cursor. Scopes the skill to files matching the glob. Accepts a list or a
  comma-separated string. Leave unset for a skill available regardless of open files.

## Cursor

Discovery — skills are loaded automatically from all of:

- `.cursor/skills/` (project)
- `~/.cursor/skills/` (global, local machine)
- `.agents/skills/` (project)
- `~/.agents/skills/` (global, local machine)
- Nested project subdirectories, e.g. `apps/web/.cursor/skills/` in a monorepo. Skills under a
  nested project directory are automatically scoped to files inside that directory.
- Compatibility paths: `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, `~/.codex/skills/`

Walking behaviour:

- Cursor walks the skills root **recursively**, so category folders work for grouping, e.g.
  `.cursor/skills/shipping/deploy-staging/SKILL.md`.
- The skill's **name comes from the folder that directly contains `SKILL.md`**, not the category
  above it.

Invocation: type `/` followed by the skill name in chat to run it (e.g. `/write-tests`), or type
`@` and select it to attach as context.

Cloud Agents:

- Personal skills in `~/.cursor/skills/` stay local until synced. Sync is opt-in via
  Settings → Agents → Sync Skills for Cloud Agents (Context and Tools).
- **Only `~/.cursor/skills/` syncs.** `~/.agents/skills/` and unsynced local skills do not reach
  Cloud Agents, Agents Window remote SSH, or self-hosted workers. On self-hosted workers, use
  project skills in the repo or bake skills into the worker image.

Rules vs skills (why skills are the right vehicle for multi-step procedures):

| | Rules | Skills |
|---|---|---|
| Purpose | Short coding guidelines and constraints | Multi-step workflows and procedures |
| Length | A few lines to a few hundred | Often longer, detailed step-by-step |
| Applied | Included in every (or matching) conversation | Invoked on demand with `/name` or `@name` |

## ChatGPT

No file loader. Open the `SKILL.md`, copy the body (everything below the closing `---`) and paste
it into the conversation or a Project's instructions. Frontmatter is directory-scan metadata and
is not needed in pasted text.

## Hermes Agent

Same folder-plus-`SKILL.md` shape, under the client's skills directory
(`~/.hermes/skills/<category>/<name>/SKILL.md`), and every skill name becomes a
`/name` slash command. Two client-specific behaviours matter when porting:

- **The index truncates descriptions at ~57 characters.** The full description is
  available only after the skill loads; the load/no-load decision is made from the
  truncated view. Front-load the trigger words.
- Skill files are runtime config for that client, not repo content. Keep a
  portable copy in your shared repo and, if you want both, symlink rather than
  copying so the two cannot drift.

Client-specific authoring rules (validator constraints, size caps, peer
structure) are a separate concern from portability — check that client's own
authoring docs.

## Verifying a client's current paths

Docs pages are the source of truth; fetch them rather than trusting recall:

```bash
curl -sL -A "Mozilla/5.0" "https://cursor.com/help/customization/skills" \
  | python3 -c "import sys,re,html;t=sys.stdin.read();t=re.sub(r'(?is)<(script|style|nav|footer|svg).*?</\1>',' ',t);t=re.sub(r'(?s)<[^>]+>',' ',t);print(re.sub(r'\n\s*\n+','\n',html.unescape(t))[:5000])"
```
