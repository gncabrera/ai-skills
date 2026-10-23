---
name: skill-audit
description: >-
  Grade any SKILL.md A-F on five dimensions: frontmatter and description,
  unambiguous steps, real pitfalls with recoveries, verification, and structure.
  Use when auditing one skill or a whole library, before publishing a new skill,
  after a reorganization, or when a skill exists but never seems to get loaded.
license: MIT
---

# Skill Audit — Five-Dimension Grading (A–F)

An audit answers one question: **will this skill actually fire, and once fired,
will it execute correctly?** A skill can read beautifully and still be dead —
wrong folder name, description that never matches a request, steps too vague to
follow, no way to tell whether it worked.

**Don't use for:** code review, runtime debugging, config validation, or grading
non-skill documents (a plan, a README, an API spec). Auditing a *library's*
overlap problems is in scope — the batch section covers it.

## How a skill gets discovered

Three phases, and a skill can die in any of them:

1. **Discovery.** The client scans its skills directory and puts `name` +
   `description` into the prompt/index. The model decides from that line alone
   whether to load the skill. Nothing inside the body matters if this step fails.
2. **Loading.** The full `SKILL.md` enters context. Structure, commands and
   clarity matter now.
3. **Execution.** The model follows the skill. Vague steps, missing commands and
   absent verification cause silent failures — especially on smaller models.

### The truncation caveat (read this before grading dimension 1)

Some clients truncate the description inside their index before the model ever
sees it. **Hermes Agent cuts at ~57 characters**; the full description only
becomes visible after the skill is already loaded, when the load decision is
already made. That is a property of one client, not of the format — the Agent
Skills spec allows **1024 characters**.

So grade against the spec, and treat front-loading as the portable defence:
trigger words belong in the first ~50 characters so the skill still fires
wherever it gets cut. Do not fail a cross-tool skill for exceeding 57
characters. Do flag one whose trigger appears only at character 300.

## The five dimensions

### Dimension 1 — Frontmatter & description (25 points)

The description is the discovery mechanism. Everything else is secondary.

**Check:**
- Frontmatter block exists, opens with `---`, has `name` and `description`.
- `name` is ≤64 chars, `[a-z0-9-]`, no leading/trailing/consecutive hyphen, and
  **matches the containing folder name**.
- `description` is ≤1024 chars, states **what** it does and **when** to use it.
- The trigger words (the words a user would actually type) appear in the first
  ~50 characters.
- The description starts with the trigger class, not with filler or a tagline.
- The description does not overlap another skill's trigger.

**Penalties:** missing frontmatter −5 · missing description −3 · `name` ≠ folder
−5 · description over 1024 −5 · trigger past ~50 chars −3 · description generic
(no trigger class) −2 · overlaps another skill's scope −1.

### Dimension 2 — Unambiguous steps (25 points)

Every step must be followable without invention. What "unambiguous" means depends
on the kind of skill:

- **Operational skill** → a copy-pasteable command: `pytest tests/test_x.py::test_y -v`,
  `docker compose restart api`, `curl -sI http://host/health`.
- **Planning / writing / review skill** → a numbered manual check with an
  observable result: "the plan lists every touched file", "the section names the
  rejected options and why".

Do not penalise prose a human follows. Do penalise a step that could mean two
different actions.

**Check:** no step says "run the tests", "check the config", "use the appropriate
tool". Paths are either absolute or clearly relative to a stated base. Expected
output is given where the result is ambiguous.

**Penalties:** a step with no concrete action −3 each · placeholder with no
explanation −1 each · mix of precise and vague steps −2.

### Dimension 3 — Pitfalls (20 points)

Pitfalls are what separates a skill written by someone who did the work from one
written by someone who imagined it. Each item must be a failure that actually
happens, with the recovery.

**Check:** 2–3+ specific failure modes; each has a concrete recovery; at least one
is a trap the skill's own steps can walk into.

| Good pitfall | Bad pitfall |
|---|---|
| "The YAML date is parsed as a date object unless quoted — quote `last_verified: \"2026-01-01\"`, unquoted it breaks strict parsers." | "Watch out for YAML formatting." |
| "A restart fixes the symptom and tempts you to stop; the failure returns — continue to the checklist." | "Be careful when restarting." |
| "`ln -s` on an existing symlink nests a link inside a link; use `ln -sfn`." | "Make sure symlinks work." |

**Penalties:** no pitfalls section −5 · vague pitfall −2 each · no recovery action
−1 each.

### Dimension 4 — Verification (15 points)

How does the agent know it worked, rather than assuming it did?

**Check:** at least one explicit verification after the major actions;
verification is observable (exit code, file exists, endpoint returns 200, count
matches); the failure state is checked too, not only the happy path.

| Good | Missing |
|---|---|
| "`git status` shows the file staged; `git diff --cached` shows only the intended change." | "Commit the changes." |
| "`test -f out/report.md && wc -l out/report.md` — zero lines means the extract failed silently." | "The report is generated." |

**Penalties:** no verification −5 · vague verification −2 each · only the success
state checked −1.

### Dimension 5 — Structure & conventions (15 points)

Structure is about scannability and matching the peers in the same repo.

**Check:** headings that name the task; a "when to use" section with
counter-triggers ("don't use for…"); body sections specific to the subject, not
generic filler; length in the range of its peers (8–20k chars is typical; bulk
belongs in `references/`).

**Penalties:** no when-to-use / counter-triggers −3 · body over 20k chars without
splitting into `references/` −2 · structure inconsistent with peer skills −1.

## Grading scale

- **A (90–100)** — production-ready. Fires reliably, executes without invention,
  documents its own traps.
- **B (80–89)** — minor gaps, still robust. Missing one element above.
- **C (70–79)** — functional but vague in 1–2 places; a smaller model will
  improvise where it shouldn't.
- **D (60–69)** — error-prone: incomplete steps, or a description that won't fire.
- **F (<60)** — broken discovery or broken execution.

## Output format

```
## Skill Audit: <skill-name>

**Grade: <score>/100 — Grade <letter>**

### Description check
- Length: <N> chars (spec limit 1024)
- Folder `<folder>` vs `name:` <match|MISMATCH>
- Trigger visible in the first ~50 chars? <yes/no — list the words>
- If trigger is late, suggested front-load: `<rewritten opening>`

### Dimension scores
- Frontmatter & description: <N>/25 — <one line>
- Unambiguous steps: <N>/25 — <one line>
- Pitfalls: <N>/20 — <one line>
- Verification: <N>/15 — <one line>
- Structure: <N>/15 — <one line>

### Issues, ranked
1. <issue> → <fix, with before/after>

### Quick wins
- <the fix that moves the grade most>
```

## Batch audit (10+ skills)

**Phase 1 — mechanical triage.** One pass, no judgment:

```bash
cd <skills-root>
python3 - <<'PY'
import pathlib, re
for skill in sorted(pathlib.Path('.').glob('*/SKILL.md')):
    text = skill.read_text(encoding='utf-8')
    fm = text.split('---', 2)[1] if text.startswith('---') else ''
    name = re.search(r'^name:\s*(\S+)', fm, re.M)
    desc = re.search(r'^description:\s*(.+?)(?=^\w[\w-]*:|\Z)', fm, re.S | re.M)
    d = ' '.join(desc.group(1).split()) if desc else ''
    print(f"{skill.parent.name:26} name={name.group(1) if name else 'MISSING':26} desc={len(d):4} chars")
PY
```

Flag `name` ≠ folder, missing name, and descriptions near or past 1024 **characters**
(the script counts characters, not bytes — `wc -c` would overcount emoji and
accents by 2–4× and make a compliant description look illegal).

**Phase 2 — deep audits.** If the client supports parallel subagents, split the
flagged skills across them with the full five-dimension methodology pasted into
each brief; otherwise do them in batches of five. Roughly 30 seconds per skill.

**Phase 3 — compile.** A table of grades, the distribution, the offenders with
suggested rewrites, one priority queue ordered by impact, and merge/overlap
recommendations for skills that claim the same trigger.

## Pitfalls

1. **Counting characters wrong.** `echo -n "$D" | wc -c` counts **bytes**;
   emoji and accents take 2–4. Use `wc -m`, or `python3 -c 'print(len(s))'`.
2. **Trimming to exactly the limit and cutting a word.** Aim for a few characters
   under, so the last word completes before any client's ellipsis.
3. **Grading a cached description.** Clients cache the skill index at startup.
   After editing a description, compare the file (`grep '^description:'`) with
   what the client shows you; a mismatch means the cache is stale and the new
   description is not being used yet.
4. **Subagents skipping the description check.** Delegated audits routinely
   report "A" while missing that the trigger sits at character 200, and sometimes
   report a wrong length. Always run the mechanical triage first and cross-check
   every report against it; when they disagree, trust the measurement.
5. **Subagents patching during an audit.** A subagent asked to audit may also
   "fix" things. Either instruct audit-only or expect to review its edits — never
   merge an unverified patch into a published skill.
6. **Confusing the description with the overview.** The frontmatter `description`
   is the discovery line; the body's opening section is the expanded what-and-why.
   Optimising one does nothing for the other.
7. **Scoring dimension 1 by another tool's limit.** Grading a portable skill
   against a single client's 57-character index truncation produces a false F on
   a compliant skill. Spec first, truncation as advice.
8. **Auditing without reading the skill's own claims.** An audit that never opens
   the references it points at cannot tell whether they exist or say the same
   thing.

## Verification

Before delivering an audit:

- [ ] Every length figure comes from a command, not from counting by eye
- [ ] `name` was compared against the folder name, not just read
- [ ] All five dimensions scored, and the total matches their sum (±1)
- [ ] Every issue has a concrete fix, with before/after where it is a rewrite
- [ ] No placeholders left in the output (`<N>`, `<one line>`)
- [ ] Cross-checked against the mechanical triage if this was a batch run
