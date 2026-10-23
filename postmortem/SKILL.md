---
name: postmortem
description: >-
  Write an incident postmortem as a learning artifact: gather context, rebuild
  the timeline with the timezone verified, score severity, check for recurrence,
  draft from a fixed template, preview it, publish it, and add at least one
  concrete prevention per incident. Use after an outage, data loss, degraded
  service or any incident that needed manual intervention, or when asked to
  document what happened.
license: MIT
---

# Postmortem

A postmortem is written for the person who hits this failure in eight months —
often you, with no memory of it. It is not a status report, not a blame
document, and not an obituary.

**It answers four things:** what broke, why, how it was fixed, and what now
prevents it from happening again. If any of the four is missing, it is not
finished — a postmortem with no prevention is just a story about a bad day.

**When to use:** an incident is resolved and the cause is known; the user says
"write a postmortem", "document the incident", "what happened with X"; a
troubleshooting session ended with a real fix; an incident repeated.

**Don't use for:** an incident that is still open (troubleshoot it first, then
come back); a restart that fixed it in under a minute with no lasting effect; a
planned change with no surprises (that's a changelog entry).

## Step 1 — Gather the six facts

Ask only for what you don't already know from the session:

1. **What broke** — the specific service, host, component or pipeline.
2. **When it started** — and how it was noticed (alert, user report, luck).
3. **What the impact was** — downtime, data loss, degraded behaviour, who was
   affected.
4. **The root cause** — the underlying reason, not the first symptom.
5. **What fixed it** — the actual steps and commands.
6. **What prevents recurrence** — a check, an alert, a guard, a design change.

## Step 2 — Rebuild the timeline from the session

Before asking the user for a timeline, mine the conversation for timestamped
events: commands that ran, errors and when they appeared, the user's reports, and
the moment the fix was confirmed. Reconstruct as much as possible, then present it
for confirmation:

> "Here's what I pieced together — correct? Anything missing?"

A timeline you extracted is more accurate than a timeline someone remembers, and
confirming it takes one message.

## Step 3 — Verify the timezone before writing any times

**Always run this first.** Session timestamps are usually UTC internally; the
system may not be. Getting this wrong makes the postmortem useless for
cross-referencing logs and schedules later.

```bash
date +'%Z %z'      # local timezone and offset
date -u +'%Z %z'   # UTC reference
```

Then:

1. **Label the timeline column with what `date` actually printed** — `Time
   (UTC-3)`, not a guess.
2. **Convert session timestamps** using that offset.
3. **Cross-check any scheduled job involved** — a cron expression runs in the
   scheduler's timezone, which may differ from both the host and the user. If a
   job at `03:00` actually ran at midnight local, say so.

No assuming UTC. The column header must match the times in the column.

## Step 4 — Score the severity

| Level | Criteria |
|---|---|
| 🔴 **Critical** | Data loss, corruption, or the service could not be recovered without out-of-band access (console, physical, provider API); or total outage over an hour |
| 🟡 **Major** | Manual intervention over ~15 minutes, degraded service, partial data loss, a workaround that changes behaviour |
| 🟢 **Minor** | Recovered by a restart in under five minutes, brief degradation, self-healed but worth recording |

Derive from the evidence, and say why: "SSH plus manual repair, ~25 minutes → 🟡
Major." Then confirm with the user — severity drives how much attention the
prevention gets.

**Escalate one level on a recurrence.** A documented prevention that failed is
worse than no prevention, and the severity should say so.

## Step 5 — Check for recurrence

Scan existing postmortems before drafting:

```bash
ls <docs-dir>/postmortem/ 2>/dev/null
grep -ril '<keyword>' <docs-dir>/postmortem/ 2>/dev/null
```

Look for overlapping root causes (disk, memory, DNS, mounts, certificates,
credentials, scheduler). If one matches:

- Name it in the new root-cause section, with a link to the earlier file.
- In prevention, explain **why the earlier prevention didn't hold** — wrong
  place, wrong scope, silently disabled.
- Raise the severity one level.

If nothing matches, say it's novel; that's information too.

## Step 6 — Draft

Use the template in `references/postmortem-template.md`. Rules:

- **Timeline:** events only, no narration, times from Step 3.
- **Root cause:** one paragraph, specific. "The backup script staged 5 GB to the
  same filesystem it was backing up" — not "the disk filled up".
- **What went wrong:** the chain, as separate failure points. Each item is a
  place where the incident could have been caught.
- **Fix:** commands, paths and values. Someone reading this later should be able
  to reconstruct exactly what was done.
- **Prevention:** concrete. "Added a free-space pre-flight to the backup script"
  — not "monitor disk space better".
- **Lessons:** the part that generalises beyond this incident.

## Step 7 — Preview before writing

Show the full postmortem in chat:

> "📝 Preview — this is how it reads: … Ok to save, edit, or cancel?"

Only write the file after confirmation. Correcting severity, a wrong timezone or
a symptom-as-root-cause afterwards means an amend commit and a wrong artifact
in the meantime.

## Step 8 — Publish

```bash
# filename: YYYY-MM-DD-<slug>.md, date of the INCIDENT, slug from the ROOT CAUSE
ls <docs-dir>/postmortem/                      # avoid collisions first
# then write the file, and:
git add <docs-dir>/postmortem/<file>
git commit -m "docs(postmortem): <slug> — <one-line summary>"
```

- Slug from the cause: `disk-full` ✓, `service-down` ✗.
- Two incidents on one date: append `-2`.
- No repo? Write the file wherever the runbooks live and tell the user the path.

## Step 9 — Update the index

A postmortem nobody can find is a postmortem nobody reads. Keep
`<docs-dir>/postmortem/index.md` as a chronological table:

```
| Date | Severity | System | File | Summary |
|------|----------|--------|------|---------|
| 2026-05-04 | 🟡 | backup | [disk-full](2026-05-04-disk-full.md) | Staging dir filled the root filesystem |
```

Create it with a `Last verified:` line if it doesn't exist, then append the row
and commit it separately.

## Step 10 — Prevent it, concretely

Every postmortem produces at least one of these, matched to the root cause:

- **A check that alerts** — scheduled probe, health endpoint, threshold on disk or
  memory, alert only on failure so it stays quiet.
- **A tighter existing monitor** — the monitor that should have caught this had
  the wrong check type or too long an interval. Fix the monitor.
- **A pre-flight guard** — the script that broke should refuse to start when its
  precondition is false.
- **A design change** — remove the shared failure domain, add a retry, make the
  operation idempotent.

Offer the one that fits; skip the ones that don't. A watchdog suggested for a
one-off typo is noise and teaches the user to ignore suggestions.

## Pitfalls

1. **Writing before the incident is closed.** An open incident has no root cause
   yet; that's troubleshooting, not a postmortem.
2. **Symptom as root cause.** "The service was down" is a symptom. "The mount
   went stale after a reboot because the unit had no network dependency" is a
   cause. Keep asking why until you reach a decision someone made.
3. **Too vague to act on.** "Be more careful with disk space" helps nobody.
   "Pre-flight `df` guard added to the backup script, alert at 85%" does.
4. **No prevention.** Without it the document is an obituary.
5. **Wrong filename date.** The incident date, not the writeup date.
6. **Skipping the preview.** Every rework after publishing costs an amend and
   leaves a wrong artifact in history.
7. **Assuming UTC.** Label the column from `date`, not from convention.
8. **Not checking for recurrence.** A repeat incident changes both the severity
   and the prevention: you now have to explain why the last fix failed.
9. **Forgetting the index.** The file exists; nobody knows it does.
10. **Blaming a person.** Postmortems describe mechanisms. "The operator ran the
    wrong command" is a missing guard, a confusing interface, or a runbook gap.
11. **Suggesting prevention that doesn't fit.** A watchdog for a typo, a monitor
    for a hypervisor-level failure — mismatched suggestions erode trust in the
    next suggestion.

## Verification

- [ ] File exists at `<docs-dir>/postmortem/YYYY-MM-DD-<slug>.md`, dated by the incident
- [ ] Slug describes the cause, not the symptom
- [ ] All template sections filled — no empty headings
- [ ] Severity assigned, justified, user-confirmed; escalated if recurring
- [ ] Timezone derived from `date` and reflected in the column header
- [ ] Timeline has at least three events, extracted from the session
- [ ] Root cause is specific and causal, not a symptom
- [ ] Recurrence check ran against existing postmortems
- [ ] At least one concrete prevention measure
- [ ] Preview shown and approved before writing
- [ ] Index updated and committed
- [ ] Committed (or saved and the path reported)
