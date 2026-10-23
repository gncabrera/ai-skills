# Postmortem Template

> Copy this into `<docs-dir>/postmortem/YYYY-MM-DD-<slug>.md` and fill every
> section. For guided creation, use the `postmortem` skill — it walks these
> sections in order and gates the write behind a preview.

````markdown
# Postmortem: <Title> — YYYY-MM-DD

> **Severity:** 🔴 Critical | 🟡 Major | 🟢 Minor
> **Duration:** <impact duration, e.g. "12 min total, 8 min user-visible">
> **Date:** YYYY-MM-DD (incident date, not writeup date)
> **Detected by:** <alert | user report | manual check>

## Summary

<2-3 sentences. What broke, for how long, who noticed, and what stopped it.
A reader who only reads this section should still understand the incident.>

## Impact

<What was unavailable or degraded, for whom, and what was lost if anything.
Distinguish "nobody noticed" from "every request failed".>

## Timeline

| Time (<timezone from `date +'%Z %z'`>) | Event |
|------------|-------|
| ~HH:MM     | <first failure or trigger> |
| ~HH:MM     | <detection> |
| ~HH:MM     | <attempt and its result> |
| ~HH:MM     | <fix applied> |
| ~HH:MM     | <confirmed recovered> |

## Root Cause

<The underlying cause, in one paragraph — not the symptom. Why was this
possible? Which configuration, assumption or decision made it inevitable?>

_Recurrence:_ <"Novel incident." | "Recurrence of [YYYY-MM-DD-slug.md](...); the
earlier prevention did not hold because …">

## What Went Wrong

<The chain of failures that turned the root cause into an incident. One bullet
per failure point — each one is a place where this could have been caught.>

- <failure point>
- <failure point>

## Fix

<The concrete steps taken, with commands and paths where relevant. Someone
rebuilding this environment should be able to reproduce them.>

```bash
# commands that actually ran
```

## Prevention

<At least one concrete change. Each entry says what was added and where.>

- [ ] <check / alert / guard / design change — file and command>
- [ ] <monitor adjusted: interval or check type, and why>

## Lessons

<What generalises beyond this incident: a design principle, a process gap, a
class of failure worth watching for.>

## Links

- <related postmortems, incident ticket, change request, logs or dashboards>
````

## Severity levels

- 🔴 **Critical** — data loss or corruption; unrecoverable without out-of-band
  access; total outage over an hour.
- 🟡 **Major** — manual intervention over ~15 minutes; degraded service; partial
  loss; a workaround that changes behaviour.
- 🟢 **Minor** — recovered by a restart in under five minutes; brief degradation;
  self-healed but worth recording.

**Escalate one level when the incident is a recurrence** — a documented
prevention that failed is a worse signal than no prevention at all.

## Slug convention

Derive from the root cause, not the symptom:

- `disk-full` ✓ (cause)
- `service-down` ✗ (symptom — down because of what?)

Lowercase, hyphens, 2–4 words.

## Naming convention

Filename: `YYYY-MM-DD-<slug>.md`

- Date: the date of the **incident**, not the writeup.
- Two incidents on one date: append a number — `2026-05-04-disk-full-2.md`.
- Check the directory before choosing a name; a collision overwrites the earlier
  file.
