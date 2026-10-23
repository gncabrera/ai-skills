---
name: retrospective
description: >-
  Run a retro after a task: what went wrong, what went well, what to improve, a
  scored summary, a recurrence check against past work, and an offer to turn the
  lesson into a skill. Use when the user says "retro", "retrospective", "what did
  we learn", "post-mortem" about a finished piece of work (not an outage), or
  after closing a large task, migration or multi-step change.
license: MIT
---

# Retrospective

After a significant task, run a structured retro. **The agent answers, not the
user** — analysis of what actually happened in the session is the agent's job;
the user only reacts. Three questions, evidence, a score, and one or two lessons
worth keeping.

Not a postmortem: a postmortem exists because something broke and someone needs
to know why. A retro exists because work happened and the next run should be
smoother.

**When to use:** a multi-step task just finished; a migration or deploy landed; a
debugging session ended; a piece of work was abandoned or reworked; a tracker
ticket was closed; the user says "let's do a retro".

**Don't use for:** an active task (finish first); a single command or a one-line
fix; an incident that needs a written postmortem (use `postmortem`); grading a
person.

## Workflow

### 1. Gather context

Reconstruct what actually happened, not what was supposed to happen:

- The session itself: what was requested, what was attempted, what failed, what
  was retried, what was reverted.
- Conversation history — if the task spans sessions, search it. Don't guess at
  what happened last week.
- Evidence of friction: error messages, failed tool calls, repeated attempts at
  the same step, corrections the user made.

Aim for specifics you can cite. A retro without a single concrete reference is a
mood, not an analysis.

### 2. Ask one extra question, matched to the task type

| Task type | Extra question |
|---|---|
| Deploy / infra change | Was rollback possible? Was it tested? |
| Code / script | Did the tests catch it, or was it found afterwards? |
| Docs / writing | Did anything go stale that we didn't touch? |
| Debug / fix | Was the root cause reached, or was it a patch? |
| Config / environment | Was the change recorded anywhere? |
| Mixed / unclear | Skip — use only the three standard questions |

Fold the answer into "what could improve" when it exposes a gap.

### 3. Answer the three questions

Both directions matter. "What went well" is not decoration — it is the only
section that tells you what to keep doing.

Answer with specifics:

- What failed, and **why** it failed (the mechanism, not the feeling).
- What worked first try, and which decision or tool made it work.
- What to change next time — a process change, a missing check, a clearer
  instruction. Not "be more careful".

### 4. Check for recurrence

Search past sessions, past retros, notes or the issue tracker for the same
failure. If it appears twice or more, flag it:

```
- [failure] 🔁 recurring (seen 2026-03-14 and 2026-04-02)
```

A recurring failure is not a lesson to remember — it is a fix to schedule. Say so
and propose the root-cause fix instead of a third reminder.

### 5. Score

Give 1–10 for how the session went (productivity and friction, not the agent's
self-image) plus a two-word summary: "smooth", "productive but slow", "stuck on
permissions", "constant rework". A score with no justification is noise — one
line why.

### 6. Extract reusable lessons

If something non-trivial was solved, offer to keep it:

> "Want me to save this approach as a skill for next time?"

Worth it when: it took three or more steps to figure out, it involved a
non-obvious command or setting, and it will recur. Not worth it for a one-line
config change. If yes, use `skill-creator`; if no, move on.

### 7. Optional improvement pass

Offer one round of ideas about the finished work — what to add, simplify or
automate next. If a `suggestion` skill is available, load it; otherwise propose
5–7 ideas yourself, tagged quick-win vs strategic.

### 8. Record what was learned about the user

If the retro revealed a standing preference — they hated being asked twice, they
want verification before commits, they prefer small increments — record it in
whatever durable memory the client provides (memory tool, a project notes file,
the repo's conventions doc). One or two entries, only if new. Do not ask
permission for this; do not write noise, and never write something that will be
stale in a week.

### 9. Optional: file it where the work is tracked

If the task came from an issue tracker, offer to post the retro as a comment on
the ticket. Only when there is clear evidence of a ticket — a false positive
here is annoying.

## Output template

```
📋 Retrospective — <task>

❌ What went wrong
- <specific failure: what happened, why, cost>
- <another, if applicable>
- If nothing major: "Nothing critical. <minor friction>"

✅ What went well
- <what worked first try>
- <good decision>
- <tool or skill that saved time>

🔧 What could improve
- <process change or gap, with the concrete action>
- [extra: <task-type question answer>, if it exposed something]

📊 Score: <1-10>/10 — <two-word summary>
```

A filled example of one section, to show the level of detail expected:

```
❌ What went wrong
- The migration script had the old export path hardcoded. Spent 15 minutes
  debugging storage permissions that were never the problem; the real cause was
  a path that had moved. Cost: ~15 min and one wrong hypothesis the user had to
  correct.

🔧 What could improve
- Read paths from one variable, not from five literals. Next move of that path
  should be a one-line change, not a hunt.
```

## Pitfalls

1. **Skipping "what went well".** Without it the retro becomes a scolding, and the
   patterns worth repeating never get named.
2. **Generic answers.** "Everything went fine" tells nobody anything. If the
   session was genuinely smooth, say which decision made it smooth.
3. **Inventing drama.** A quiet, well-executed task should be reported as one.
   Fabricated friction destroys trust in the whole retro.
4. **Over-offering skill creation.** Not every minor fix deserves a skill.
   Reserve it for non-trivial, recurring patterns.
5. **Guessing at multi-session context.** If the user references earlier work,
   search the history. Reconstruction from memory is how a retro becomes fiction.
6. **Re-litigating old history.** Stay on this session unless a pattern repeats —
   then name the pattern, not the whole back catalogue.
7. **Scoring to please.** A 9/10 on a session with three wrong turns is worthless.
   The score is only useful if it can be low.
8. **Turning a defect into an "improvement".** If the audit found it, it's a bug
   to fix, not an idea to consider.

## Verification

- [ ] Context gathered from the session (and from history if multi-session)
- [ ] Task type identified; extra question answered when relevant
- [ ] Recurrence checked; flagged with dates if found
- [ ] All three questions answered with concrete, citable specifics
- [ ] Score given with a one-line justification
- [ ] Skill creation offered if a reusable lesson exists, and the answer handled
- [ ] Improvement pass offered
- [ ] Any new standing preference recorded, or explicitly nothing to record
