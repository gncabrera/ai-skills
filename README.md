# ai-skills

Agent-agnostic skills for Cursor, ChatGPT and Hermes. Plain markdown, copy, paste, adapt.

## What this is

A collection of reusable instruction files written in the **Agent Skills** format: a folder
containing a `SKILL.md` with YAML frontmatter plus a markdown body.

Nothing here is tied to a specific product, model or vendor. Any agent that understands the
format loads them directly (Cursor, Claude Code, Codex, and anything else that follows the
spec). Anything that doesn't, gets the body pasted in and works just as well.

The point is portability: write the skill once, use it from every tool you already have open.

## Skills

| Skill | What it does |
|-------|--------------|
| [`ask`](ask/SKILL.md) | Clarifies requirements before any work starts. Numbered questions, three labeled options each, one marked default. Discovery only — no implementation until you answer. |
| [`caveman`](caveman/SKILL.md) | Ultra-compressed output mode. Cuts token usage ~75% while keeping every piece of technical substance. Intensity levels: `lite`, `full` (default), `ultra`. |
| [`plan`](plan/SKILL.md) | Decomposes a goal into an issue-ready plan: file inventory, discrete issues with acceptance criteria, dependency waves, and mechanical validation commands. Planning only. |
| [`implement`](implement/SKILL.md) | Executes a plan written by `plan`, wave by wave, honoring its Execution Contract and per-issue checks. Sister skill to `plan`. |
| [`phased-plan`](phased-plan/SKILL.md) | Writes a plan as small phases a person tests by hand, one at a time, gated by `PASS` / `FAIL` / `SKIP`, then offers to save it for a later chat to continue. |
| [`deep-research`](deep-research/SKILL.md) | Parallel multi-source research producing a cited Markdown report with confidence tracking. Eleven research types: market, domain, technical, competitive, product, academic, person/org, financial, legal, trend, community. |
| [`suggestion`](suggestion/SKILL.md) | Generates 7–12 ranked, context-specific improvement ideas with quick-win and effort tags. |

`plan` and `implement` are designed as a pair: `plan` produces the artifact, `implement`
consumes it. `phased-plan` is the human-in-the-loop alternative to that pair: instead of
machine-checked issues and dependency waves it writes one hand-testable phase at a time and
stops for a `PASS` / `FAIL` / `SKIP` answer before the next one. The rest stand alone.

## Structure

Every skill is a folder. The folder name is the skill name.

```
skill-name/
├── SKILL.md        # required — frontmatter + instructions
├── references/     # optional — extra docs, loaded on demand
├── assets/         # optional — templates and resources
├── scripts/        # optional — executable code
└── evals/          # optional — test cases
```

`SKILL.md` starts with YAML frontmatter. Only two fields are required:

| Field | Required | Constraint |
|-------|----------|------------|
| `name` | yes | Max 64 chars. Lowercase letters, numbers and hyphens. Must match the containing folder name. |
| `description` | yes | Max 1024 chars. Should say **what** it does and **when** to use it — this is the only text the agent sees before deciding to load the skill. |

Optional fields the spec defines: `license`, `compatibility` (max 500 chars, environment
requirements), `metadata` (a string-to-string map), `allowed-tools` (experimental).

Individual clients add their own fields on top. `disable-model-invocation: true` (used here)
is Claude Code's way of saying *the user must invoke this one, the model can't fire it
automatically*. Cursor's equivalent scoping field is `paths`. Unknown fields are ignored by
clients that don't understand them, so a skill can carry extras without breaking anywhere.

Write `description` carefully. A vague one means the skill never triggers; it's the whole
discovery mechanism.

## Use it

### Cursor

Cursor discovers skills from `.cursor/skills/`, `~/.cursor/skills/`, `.agents/skills/` and
`~/.agents/skills/` — plus the Claude and Codex equivalents for compatibility. It walks the
root recursively, so category subfolders work, but the skill's name comes from the folder
that directly contains `SKILL.md`.

Symlink each skill into your global skills directory so `git pull` keeps them current:

```bash
mkdir -p ~/.cursor/skills
cd ~/ai-skills
for d in */; do
  [ -f "$d/SKILL.md" ] && ln -sfn "$PWD/${d%/}" ~/.cursor/skills/"${d%/}"
done
```

Then invoke with `/skill-name` in chat, or attach as context with `@skill-name`.

Only `~/.cursor/skills/` is synced to Cloud Agents. Project-level skills live in the repo.

### Claude Code / Codex

Same folders, same format. Drop or symlink the skill folder into `~/.claude/skills/` or
`~/.codex/skills/`.

### ChatGPT

No file loading. Open the `SKILL.md`, copy the body (everything below the closing `---`) and
paste it into the conversation or a Project's instructions. The frontmatter is metadata for
agents that scan directories — paste text doesn't need it.

### Anything else

If the tool reads the Agent Skills format, point it at the folder. If it doesn't, paste the
body. Both work.

## Adding a skill

1. `mkdir <skill-name>` — lowercase, hyphens, no leading or trailing hyphen.
2. Create `<skill-name>/SKILL.md` with `name` and `description` frontmatter.
3. Write the body as if briefing a competent colleague: trigger conditions, numbered steps
   with exact commands, pitfalls, and a verification step. Instructions should stay under
   ~5000 tokens — the frontmatter is loaded for every skill at startup, the body only when
   the skill is actually used.
4. Keep it generic. No hostnames, no paths from your own machine, no credentials, no client
   names.

## Credits

`deep-research` is adapted from [samber/cc-skills](https://github.com/samber/cc-skills) by
Samuel Berthe and Maxme Courant (MIT). The rest are original or trimmed down from skills
used in daily work.

## License

MIT — see [LICENSE](LICENSE).
