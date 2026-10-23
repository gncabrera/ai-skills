---
name: skill-creator
description: >-
  Author a new skill end to end with quality gates: context questions, placement,
  draft, a measurable validation pass, a real load test, an A-F audit before
  publishing, and the symlink-not-copy distribution rule. Use when asked to
  create, write or save a skill, capture a repeated workflow as a skill, or turn
  a procedure the user just walked through into a reusable instruction file.
license: MIT
---

# Skill Creator

Writing a skill is not writing a markdown file. It is making sure the file
**fires** when it should (description), **loads** at all (frontmatter, folder
name), and **executes** without invention (steps, pitfalls, verification). This
skill is the pipeline that enforces those three things, in that order.

Each step gates the next. Do not skip the gates because the skill "seems
obvious".

**Don't use for:** editing an existing skill (just patch it), batch-auditing a
library (that's `skill-audit`), or packaging skills for several clients at once
(that's `portable-agent-skills`).

## Step 0 — Context questions (max 5, and only if needed)

If the request already names the domain and the trigger ("create a skill for
reading AniList's API"), skip to Step 1. If it's vague ("make me a skill"),
ask up to five questions, in one block, before writing anything:

```
**1. What kind of skill is this?**
- **a)** Operational — API calls, CLI, deployment, debugging *(default)*
- **b)** Workflow — a procedure with phases and decisions
- **c)** Writing/analysis — a document shape and its quality bar

**2. Who consumes it?**
- **a)** Just me *(default)*
- **b)** My team / shared repo
- **c)** Public
```

Rules: exactly three options per question, mark the default, ask at most five,
never pad. Skip any question you can answer from the request, from existing
skills, or from the repo's conventions. The question pool to draw from:

| Question | Ask when |
|---|---|
| Operational, workflow, or writing? | Domain unclear |
| Does it need credentials/network? | Ops territory |
| Personal, team, or public? | Affects placement and tone |
| One specific task or a class of tasks? | Affects description and scope |
| Auto-load on trigger, or explicit invocation only? | Affects description investment |
| Is there an existing skill it overlaps? | Always worth one grep first |

## Step 1 — Discovery

Establish, in one sentence each:

- **Name** — lowercase, hyphens, ≤64 chars. Prefer `<domain>-<activity>`
  (`radarr-ops`, `postmortem`, `weekly-review-planning`).
- **What it does** — becomes the opening of the body.
- **Trigger** — the words a user will actually type when they need it. These go
  in the description, front-loaded.
- **The failure it prevents** — the reason the skill exists. If you can't name
  it, the skill is documentation, not a skill.

## Step 2 — Placement

Decide where the file lives before writing it:

- **Personal client config** — e.g. `~/.cursor/skills/<name>/`, `~/.claude/skills/`,
  `~/.hermes/skills/<category>/<name>/`. Only that machine sees it.
- **Shared repo** — one folder per skill at the repo root, symlinked into each
  client (see `portable-agent-skills`). Right answer when two tools must see it.
- **In-project** — `.cursor/skills/`, `.agents/skills/` in the repository, so the
  skill travels with the code and is scoped to it.

**The folder name IS the skill name.** Whatever the placement, the directory
containing `SKILL.md` must be named exactly like the frontmatter `name`.

## Step 3 — Skeleton

Use the peer structure of the repo you're adding to. For a standalone or
ops-style skill:

```
# <Title>

## What this is / why it exists      (2-3 sentences, no filler)
## When to use                         (bullets) + "Don't use for:" (counter-triggers)
## <Topic sections>                    (steps with exact commands and expected output)
## Pitfalls                            (numbered, each with its recovery)
## Verification                        (checklist with observable results)
```

Headings should name the work ("## Step 2 — placement", "## Rollback"), not
generic labels ("## Details", "## Notes").

## Step 4 — Draft

Write the whole file in one pass, then fix it. While drafting:

- Every step gets a concrete action: a command, a tool call, or a numbered manual
  check with an observable result. "Configure it appropriately" is not a step.
- Every path is absolute, or clearly relative to a stated base.
- Every command that produces ambiguous output states the expected output.
- Leave **no placeholders**. `<service>`, `<port>`, `<TOKEN>` are acceptable only
  where the reader must substitute a value, and the skill must say so.
- Aim for 6–15k characters. Past ~20k, move bulk into `references/` and point at
  it from the body.

## Step 5 — Validate (measurable, run it)

```bash
SKILL=<path/to/skill>            # e.g. portable-agent-skills/SKILL.md
DIR=$(dirname "$SKILL")

# name matches folder, legal charset, length
NAME=$(awk -F': *' '/^name:/{print $2; exit}' "$SKILL")
[ "$NAME" = "$(basename "$DIR")" ] && echo "name ok" || echo "NAME MISMATCH"
printf '%s' "$NAME" | grep -qE '^[a-z0-9]+(-[a-z0-9]+)*$' && echo "charset ok"
printf '%s' "$NAME" | wc -m        # must be <= 64

# description present and within the spec budget (chars, not bytes)
python3 - "$SKILL" <<'PY'
import sys, re
t = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r'^description:\s*(.+?)(?=^[a-z-]+:|\Z)', t, re.S | re.M)
d = " ".join(m.group(1).split()).strip(' "') if m else ""
print(f"description: {len(d)} chars (limit 1024)")
print("opening:", d[:60])
PY

# no CRLF, no unfilled angle-bracket placeholders left unintentionally
grep -c $'\r' "$SKILL" || true
grep -n '<[A-Za-z][^>]*>' "$SKILL" || true
```

Gates:

- **`name` ≠ folder → STOP.** Some clients never see the skill.
- **description > 1024 chars → STOP.** Over the spec; trim it.
- **trigger words not in the first ~50 chars → WARN.** Hermes Agent truncates its
  index at ~57 characters, and other clients may truncate too; front-load them.
  (Same caveat as `skill-audit` — one copy, not two.)
- **CRLF present → fix.** `sed -i 's/\r$//' "$SKILL"`.
- **unquoted YAML date → quote it.** `last_verified: 2026-10-23` may be parsed as
  a date object and break strict parsers: `last_verified: "2026-10-23"`.
- **unexplained `<placeholder>` → fill or document it.**

## Step 6 — Load test

Actually load the skill the way a consumer would. A skill that can't be loaded is
a dead skill, and frontmatter breakage is silent until this step:

- Hermes Agent: `skill_view(name='<name>')` — it must return content, not an error.
- File-loading clients (Cursor, Claude Code, Codex): open the folder, confirm
  `SKILL.md` parses and appears in the skills list.
- No loader (fresh chat, ChatGPT): paste the body below the closing `---`; if the
  text alone isn't enough to do the job, the body is missing context.

Fix and repeat until it loads cleanly.

## Step 7 — Audit

Run the `skill-audit` methodology on the new skill: five dimensions, A–F.

- Below **B** → fix before publishing. A published C is a skill that will
  misfire in someone else's hands.
- At or above **B** → continue.

Do not confuse "the audit passed" with "the skill is useful". The audit checks
craft; usefulness comes from having actually done the task once.

## Step 8 — Publish

- **Shared repo:** add the README `## Skills` row in the same commit as the
  skill, then symlink the folder into each client (never copy — copies drift).
- **Personal config:** nothing to publish; the file is live after the restart in
  Step 9.
- **Version:** start at `1.0.0` and bump when behavior changes, not for typos.
- **Commit message:** `feat(<skill-name>): add <what>`, with the *why* in the body
  only if it isn't obvious.

## Step 9 — Tell the user about the restart

Most clients cache their skill index at startup. A skill created now usually
does not appear in the current session:

> "This skill won't show up until you restart the client or start a new session."

Say it explicitly; otherwise the next request looks like the skill is broken.

## Step 10 — Optional improvement pass

After publishing, offer one more round: load the `suggestion` skill (if available)
for 7–12 ideas about the new skill, tagged quick-win vs strategic.

Exclude anything the audit already flagged — those are **defects**, not
opportunities. The improvement pass is about missing operations, better
verification, edge cases, and integration with sibling skills.

## Pitfalls

1. **Description blindness.** The single most common reason a skill never fires.
   Measure the length with a command, confirm the trigger words are in the
   opening, and confirm they're words a user would type — not internal jargon.
2. **Hardcoding a path from memory.** Never copy a template path out of another
   skill or out of your own recall. Locate the real file (`find`, `ls`) and use
   what exists. A skill pointing at a path that moved six weeks ago fails in the
   only moment it matters.
3. **Description vs overview confusion.** The frontmatter description is the
   discovery line (~1 sentence, trigger-loaded). The body's first section is the
   expanded what-and-why. Writing the overview into the description wastes the
   budget; writing the description into the overview tells the reader nothing.
4. **Placeholders shipped.** A `<Pitfall name>` or `<service>` left in a published
   skill reads as an unfinished template. Grep for `<` before publishing.
5. **Over-questioning.** Five questions when the user already said exactly what
   they want is noise. The question pool is a tool, not a checklist.
6. **`cp -r src dst` nesting when `dst` exists.** It produces `dst/name/name/`.
   Use `rsync -a src/ dst/` (trailing slashes) or `cp -r src/. dst/`.
7. **Unquoted YAML dates in metadata.** Parsed as date objects, which strict
   parsers reject; quote them.
8. **Silently corrupted generated code.** After writing a file with an automated
   tool, read the lines containing environment lookups, URLs and tokens back. A
   redaction filter or a printer can mangle a line that still passes lint.
9. **Skipping the load test.** Everything else can pass while the frontmatter is
   unparseable. Loading is the only proof the skill exists.
10. **Publishing a library of one-use skills.** If it won't recur, it's a note,
    not a skill. Skills that never fire still cost prompt budget in every session.

## Verification

- [ ] Folder name equals frontmatter `name`, ≤64 chars, legal charset
- [ ] Description ≤1024 chars, states what + when, trigger in the first ~50 chars
- [ ] Every step has a concrete action; no orphan placeholders
- [ ] Pitfalls are real failures, each with a recovery
- [ ] Verification section says how to confirm success
- [ ] `skill_view` / client load returns content without error
- [ ] Audit score is B or better
- [ ] README row added in the same commit (shared repo) or skill symlinked
- [ ] User told that a restart is needed to see it
