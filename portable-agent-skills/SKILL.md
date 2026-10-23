---
name: portable-agent-skills
description: >-
  Package skills so several agent tools can use the same file: the Agent Skills
  format, one source-of-truth repo symlinked into each client's discovery
  directory, publishing without leaking private context, and a shape-based
  pre-commit checker. Use when building or maintaining a cross-tool skill
  library, deciding where a skill file should live so two tools both see it,
  writing a README for a public skills collection, or publishing, renaming or
  retiring a skill.
license: MIT
---

# Portable Agent Skills

A skill that only works in one product is a skill you will rewrite three times.
The open **Agent Skills** format is a folder with `SKILL.md` inside — YAML
frontmatter plus a markdown body — read natively by Cursor, Claude Code, Codex,
Hermes Agent and others that follow the spec.

This skill covers the class: keep ONE source-of-truth repo of agent-agnostic
skills, symlink it into each client's discovery directory, and paste bodies into
clients with no file loader. It goes end to end — add, check, publish, retire.

**Don't use for:** skills that only ever run inside one client (write them with
`skill-creator` and keep them local). Upstream in-repo package skills shipped
inside a vendor's source tree are a different job — follow that project's own
authoring guide.

## The Format

Minimum viable skill is one directory with one file:

```
skill-name/            # directory name IS the skill name
└── SKILL.md           # YAML frontmatter + markdown body
```

Optional siblings defined by the spec: `scripts/`, `references/`, `assets/`.

Only two frontmatter fields are required:

- `name` — ≤64 chars, lowercase letters/digits/hyphens, no leading/trailing or
  consecutive hyphen, and **must match the containing directory name**.
- `description` — ≤1024 chars. Must state what the skill does AND when to use it.
  This is the only text a client loads before deciding whether to pull the skill
  in, so a vague description means the skill never fires.

Optional in the spec: `license`, `compatibility` (≤500), `metadata`
(string→string map), `allowed-tools` (experimental). Clients layer their own on
top:

- `disable-model-invocation: true` — Claude Code. The user must invoke
  explicitly; the model cannot auto-fire it. Present on user-triggered modes
  such as `/ask` or `/plan`.
- `paths: ["**/*.tsx"]` — Cursor. Scopes the skill to matching files.

Unknown fields are ignored by clients that don't understand them, so carrying
extras does not break portability.

### Truncation: the one client quirk worth designing for

Some clients truncate the description in their index before the model ever sees
it — Hermes Agent cuts at ~57 characters. That is a property of one client, not
of the format: the spec budget is 1024. Write the full description, and
**front-load the trigger words in the first ~50 characters** so the skill still
fires wherever it gets cut. Do not shrink a portable skill to 57 characters to
satisfy one client's index.

Field-by-field table and client discovery paths:
`references/agent-skills-spec.md`.

## Adding a Skill

```bash
cd <repo>
mkdir -p <skill-name>          # lowercase, digits, hyphens; ≤64 chars; must match `name:`
$EDITOR <skill-name>/SKILL.md
```

1. **Frontmatter** — `name` + `description`, nothing more required. Constraints
   in The Format above.
2. **Body** — generic, per Writing for Portability below. Explicit trigger
   keywords, exact copy-pasteable commands, a pitfalls section with the recovery
   for each, a verification section. Keep it under ~5000 tokens.
3. **Add the row to the README `## Skills` table.** There is no generator. Skip
   this and the skill is invisible.
4. **Audit it before publishing.** Run the `skill-audit` methodology over the new
   skill, fix anything below B, re-run. Three of its dimensions assume a
   single-client library and would misfire on a cross-tool skill — override
   those and keep the rest:
   - **Description budget.** Grade against the spec (≤1024 chars, states what and
     when, trigger front-loaded), not against one client's index truncation.
   - **Required headings.** `## Overview` / `## When to Use` are not in the spec.
     Match this repo's peer skills, which use task-shaped headings
     (`## Phase card`, `## Inputs`).
   - **Hermes-specific pitfalls.** A portable skill's pitfalls stay on its own
     subject; do not import another tool's router trivia.

   What carries over unchanged: a pitfalls section with a recovery per pitfall, a
   verification step, and the scope-overlap check (confirm the new skill does not
   claim an existing one's trigger). "Exact commands" means "an unambiguous
   step" — a `pytest` line for an ops skill, a numbered manual check for a
   planning or writing skill. Do not penalize prose a human follows.

## Distribution: one repo, symlinked out

Never copy skill folders into each client's directory — copies go stale on the
next `git pull`. Symlink instead, so an edit in the repo is live everywhere:

```bash
mkdir -p ~/.cursor/skills
cd /path/to/skills-repo          # must be the repo root
for d in */; do
  [ -f "$d/SKILL.md" ] && ln -sfn "$PWD/${d%/}" ~/.cursor/skills/"${d%/}"
done
```

- `ln -sfn`, not `ln -s`: `-n` keeps the operation idempotent instead of nesting
  a link inside an existing link.
- The `[ -f "$d/SKILL.md" ]` guard skips README-only or docs folders.
- Verify with `ls -l ~/.cursor/skills/` and confirm each `<skill>/SKILL.md`
  resolves.
- Repeat per client (`~/.claude/skills/`, `~/.codex/skills/`) or loop over
  several targets.
- Test the loop in a throwaway directory before putting it in a public README.

Client quirks worth knowing before you document them:

- Cursor walks the skills root recursively, so category subfolders work — but the
  skill's name comes from the folder that directly contains `SKILL.md`, not the
  category above it.
- Only `~/.cursor/skills/` syncs to Cursor Cloud Agents; project-level skills
  stay in the repo.
- ChatGPT has no file loader. Paste the body (everything below the closing `---`)
  — frontmatter is directory metadata and paste text does not need it.

## Retiring or Renaming a Skill

Remove the surface, keep the evidence.

**Renaming**

1. `git mv <old>/ <new>/` — `git mv`, not `mv`, so the history follows the
   folder.
2. Update `name:` in the frontmatter. Folder and `name` must match or some
   clients stop seeing it.
3. Update the README row: the link target and the wording.
4. Grep for the old name everywhere else — other skills' descriptions, their
   "Don't use for" lines, Credits:

   ```bash
   cd <repo>
   grep -rn "<old-name>" --include="*.md" . | grep -v "^\./<new-name>/"
   ```

   The checker catches broken *links*. Nothing but this grep catches a stale
   *prose* mention.
5. Re-run the symlink loop. An existing symlink keeps pointing at the old path.
6. Bump `version` if the behavior changed (see Versioning).

**Retiring**

1. Drop the README row first — it is the only index.
2. Delete the folder and let git keep the history. Keep `<name>/RETIRED.md` (date,
   reason, replacement) only when the reasoning is worth more than the code was;
   the distribution loop and the checker both skip a folder with no `SKILL.md`.
3. Remove the client symlinks.
4. Run the grep from step 4 above and fix whatever still dangles.
5. Say in the commit body what was retired and what replaces it.

## Writing for Portability

- Avoid vendor-specific tool names and flags. A skill that hardcodes `WebSearch`
  or a Cursor-only field degrades the moment it lands in another client.
- Keep the body under ~5000 tokens. Frontmatter for EVERY skill is loaded at
  startup; the body only when the skill is actually used. Bloat in frontmatter
  taxes every single turn.
- Push bulk into `references/` and point at it. A skill whose body is 200 lines of
  tables is a skill nobody loads.
- Keep it generic: no hostnames, no absolute paths from your machine, no
  credentials, no client names. Verify before publishing — see Pre-commit checks.

## Public Repo Hygiene

- The README must let a stranger use the repo in 30 seconds: what it is, the
  skill table, directory anatomy, how to consume it per client, how to add one.
  Per-client install commands in the README are the whole value of the repo.
- Ship a LICENSE from day one (MIT unless there is a reason otherwise).
- Credit third-party skills explicitly. A bundled root LICENSE does NOT cover a
  skill pulled from someone else's repo — name the upstream and author in a
  Credits section and keep their own `license` field in frontmatter.
- Never let the repo description promise something the repo does not contain.
- Update the `## Skills` table in the same commit that adds the skill.

## Pre-commit checks

One script does all of it. `scripts/check_repo.py` takes the repo root, prints
`LEVEL scope TAG message` with a fix hint per finding, and exits 1 on any FAIL —
so the same command serves as a manual check, a pre-push hook or a CI step.

```bash
cd <repo>
python3 portable-agent-skills/scripts/check_repo.py .
```

- `NAME` **FAIL** — folder name != frontmatter `name`
- `DESC_LEN` **FAIL** — `description` over the spec's 1024 chars
- `CRLF` **FAIL** — Windows line endings in a `SKILL.md`
- `README_ROW` **FAIL** — skill missing from the README `## Skills` table
- `LINK` **FAIL** — a relative markdown link that does not resolve, in any `.md`
  (this is what catches a stale link after a folder rename)
- `BODY_SIZE` **WARN** — `SKILL.md` over 20k chars, split into `references/`
- `PRIVATE_PATH` / `PRIVATE_EMAIL` / `PRIVATE_IP` / `TOKEN` / `PRIVATE_KEY`
  **FAIL** — private context caught by **shape**, not by a list of names someone
  remembered

Fenced code blocks and inline spans are skipped for link checking — a markdown
link inside a fenced example is illustrative, not navigational — but they are
still scanned for privacy: a real path hides in a command example far more often
than in prose.

### The denylist stays outside the repo

Shape detection cannot know your employer's name. Literal terms live one per line
in a file found in this order: `--denylist PATH`, `$AI_SKILLS_DENYLIST`,
`~/.config/ai-skills/denylist.txt`.

**Never commit that file.** A denylist inside a public repo is the leak it exists
to prevent.

### Deliberate exceptions

`<REPO>/.skillchecks-ignore`, one `skill:TAG` per line (`*:TAG` for repo-wide),
optionally followed by `# reason`:

```
deep-research:DESC_LEN   # upstream skill kept verbatim from the original repo
```

An exception is a finding with a reason, not a deleted finding. Use it for a
decision you can defend, never to silence something you have not understood.

### Don't trust the checker on faith

`scripts/selftest_check_repo.py` builds throwaway repos with planted defects and
false-positive traps (fenced fake links, `/home/<user>/`, `user@example.com`) and
asserts that only the first set is reported. Run it after touching the checker:

```bash
python3 portable-agent-skills/scripts/selftest_check_repo.py
```

Its first real run caught a pre-existing spec violation in an upstream skill and
two false positives in the checker itself — which is why the fenced-block
handling exists.

## Publishing (commit & push)

Conventional format: `<type>(<scope>): <imperative>`, ≤72 chars, body only for a
non-obvious *why*.

```bash
cd <repo>
git status --short --ignored
git add -A
git diff --cached --stat
git commit -m 'feat(<skill-name>): add <what>' -m '<why>'
git push origin main
git log origin/main -1 --oneline   # must equal `git log -1 --oneline`
```

Types: `feat` new skill, `fix` content correction, `docs` README/LICENSE only,
`chore` cleanup.

### Versioning

Bump `version:` in the frontmatter when the skill's **behavior** changes — steps,
gates, commands, checks. A typo, a reworded sentence or a README-only fix does not
bump. The bump rides in the same commit as the change, so anyone reading the log
can tell which revision changed what the skill does. No `version` field yet? Add
one the first time you change the skill.

## Common Pitfalls

1. **Documenting client behaviour from memory instead of vendor docs.** Discovery
   paths change. Before writing "Cursor reads skills from X", fetch the vendor
   docs and confirm. If your extraction backend is not configured, fetch the page
   with `curl` and strip tags:

```bash
curl -sL -A "Mozilla/5.0" "$URL" | python3 -c "import sys,re,html;t=sys.stdin.read();t=re.sub(r'(?is)<(script|style|nav|footer|svg).*?</\1>',' ',t);t=re.sub(r'(?s)<[^>]+>',' ',t);print(re.sub(r'\n\s*\n+','\n',html.unescape(t))[:5000])"
```

   A README that documents a wrong path is worse than one that documents nothing.

2. **Repo description advertising features that do not exist.** A description
   claiming "auto-generated index" when there is no `INDEX.md` and no generator is
   a lie the first visitor hits in 30 seconds. Either build it or drop the claim. A
   hand-maintained table in the README is perfectly legitimate — just do not
   describe it as generated. When you find this mismatch, surface it to the user
   with both options instead of silently picking one.

3. **Copying instead of symlinking.** Copies drift on the next `git pull`; now
   there are two versions of the same skill and no way to tell which one a client
   loaded.

4. **Renaming the skill folder without updating `name`,** or vice versa. The spec
   requires they match; a mismatch makes the skill silently undiscoverable in some
   clients. Full sequence in Retiring or Renaming a Skill.

5. **Vague `description`.** It is the entire discovery mechanism. "Helps with
   research" never fires. "Deep multi-source research producing a cited report. Use
   when asked to research a topic, compare options, or analyze a landscape" does.

6. **Publishing before grepping for private context.** Paths, hostnames, employer
   names and project codenames leak easily from a skill that started life as a
   personal workflow.

7. **Attributing third-party skills to yourself.** Keep the upstream author and
   license in the skill's frontmatter, and add a Credits line in the README.

8. **Delivering more than was asked when the user names one artifact.** "Just give
   me the description" / "only the README" means exactly that artifact — no
   adjacent recommendations, no bonus variants, no unsolicited next steps in the
   same reply. The default elsewhere is to add value; for this pattern it reads as
   noise. Give the artifact and stop, or hold the extras for a single optional
   question.

9. **Putting a real name in the LICENSE.** Use a neutral holder
   (`The <repo> Authors`) on purpose. Same rule for `author:` fields and
   co-author trailers.

10. **Adding a skill without the README row.** No generator exists — the table is
    manual. The skill works, loads, and nobody ever finds it. Update the table in
    the same commit.

11. **CRLF line endings from a Windows-side editor.** A conforming YAML parser
    handles them fine (`\r\n` is a single line break), so the frontmatter is *not*
    actually broken — but the repo ends up with mixed line endings, diffs gain
    `^M` noise, and naive `sed`/`grep` checks misfire on the `name:` line.
    Normalize with `sed -i 's/\r$//' <skill>/SKILL.md`, or add a `.gitattributes`
    containing `*.md text eol=lf`.

12. **A checker that fails on its own fixtures.** If the repo ships scripts that
    contain planted private-shaped strings (an IP, a home path, an email) for
    testing, the checker will scan those `.py` files and fail the repo that ships
    them. Assemble the planted values at runtime (`"192." + "168.1.50"`) instead
    of silencing your own check with an ignore rule.

## Verification Checklist

Only what no other step already covers. `scripts/check_repo.py` runs the
private-context, name-vs-folder, README-link, CRLF and README-row checks; artifact
quality is graded by `skill-audit`. Restating those here just invites a stale
copy.

- [ ] Symlinks resolve: `<client>/skills/<skill>/SKILL.md` is readable
- [ ] Symlink loop tested in a sandbox dir before being published in the README
- [ ] Vendor discovery paths verified against current vendor docs, not memory
- [ ] README has: what-it-is, skill table, directory anatomy, per-client
      consumption, how to add one
- [ ] README `## Skills` table includes the new skill
- [ ] LICENSE present; third-party skills credited in README and frontmatter
- [ ] Repo description/README claim nothing the repo does not actually contain
- [ ] `python3 portable-agent-skills/scripts/check_repo.py .` exits 0
- [ ] `python3 portable-agent-skills/scripts/selftest_check_repo.py` exits 0

## References

- `references/agent-skills-spec.md` — frontmatter field table with exact
  constraints, client discovery paths, and Cursor scoping/sync behaviour. Load
  when writing or auditing a `SKILL.md` for cross-tool use.
- `scripts/check_repo.py` — the pre-commit checks, in one command. Run before
  every publish; the same script works as a CI step or a pre-push hook.
- `scripts/selftest_check_repo.py` — proves the checker still reports what it
  claims. Run it after any edit to `check_repo.py`.
