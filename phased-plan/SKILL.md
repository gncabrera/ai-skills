---
name: phased-plan
description: >-
  Hand-testable phased plans: every phase is one observable change a person can
  check by hand, gated by PASS / FAIL / SKIP before the next one, and the plan is
  then offered for saving to a file so a later chat can continue it. Use when the
  user asks for a phased plan, a hand-testable rollout, step-by-step phases they
  verify themselves, or names this skill. Also use when a saved phased plan exists
  and the user replies PASS, FAIL, or SKIP. Not for issue/wave decomposition or
  machine-checked plans — that is the `plan` skill.
disable-model-invocation: true
---

# Phased hand-testable plan

Write the plan in the user's language. Do not implement it in the same turn.

Do not add unit tests unless they ask. Implementation stops after each phase until they answer `PASS`, `FAIL`, or `SKIP`.

## Before the phases

If a choice would change the files, the phase split, or the manual test, ask one or two questions first. Wait. Then write the plan.

If a skill already covers that area, read it before naming types, folders, or files. That skill wins on names.

## Phase card

Every phase uses this card. One observable change. The pass must not need a later phase.

```markdown
### Phase N — Title
- Status: pending
- Change: one behavior difference
- Test: exact steps (command, URL, click path, breakpoint type, sample payload, query)
- Pass: what is true when it works
- Must not: what must stay unchanged or must not happen
- Remove in: Phase M
```

`Remove in` only when this phase leaves a temporary probe: a debug log, a hard-coded value, a throwaway endpoint, a feature flag. Name the later phase that deletes it. A probe with no removal phase is not allowed.

Bad tests: "make sure it works", "add tests later", "verify the whole feature".

Order phases so an early test is real. A stored document comes before the code that reads it. A call that reaches an empty handler comes before the work that handler will do.

## Examples

### Bad — one blob

Phase 1. Implement billing export: schema, writer, scheduler, email, and retries.

Nothing can be checked until the end.

### Good — cards

### Phase 0 — Empty table
- Status: pending
- Change: add the `invoices` table only
- Test: run the migration. Open the database client. Look for `invoices`.
- Pass: the table exists and has zero rows
- Must not: no writer, job, or email code in this phase

### Phase 1 — One hard-coded row
- Status: pending
- Change: a temporary debug action inserts one fixed invoice
- Test: run that action once. Read the table.
- Pass: exactly one row, with the fixed id
- Must not: a second run does not insert a second row
- Remove in: Phase 2

### Phase 2 — Real mapper
- Status: pending
- Change: the real mapper writes the row. Delete the debug action from Phase 1.
- Test: submit order `ORD-100` through the normal save path. Read the new row.
- Pass: columns match that order. The debug action is gone.
- Must not: no email is sent

### Phase 3 — Send pending mail
- Status: pending
- Change: send mail for rows with `status = pending`, then set `sent`
- Test: trigger one send. Check the inbox and the row.
- Pass: one message arrives and the row is `sent`
- Must not: running it again does not send a second message

## After the plan is in the chat

Ask once, with these three answers. Do not write a file before they answer.

> Save this plan to a file so another chat can continue it?
>
> - **a)** `tmp/<short-name>-plan.md`
> - **b)** I will paste a path
> - **c)** Do not save

`c` stops there. The chat plan is the deliverable.

`a` or `b`: write markdown. The file must stand alone. No secrets, connection strings, or credentials.

Start the file with:

```markdown
Current phase: N

Reply PASS, FAIL, or SKIP after the manual test.
Next chat: implement only the current phase. No unit tests. Stop for the test.
```

Then: decisions already made, what is done (with paths), every phase card, and what is out of scope.

## Continue a saved plan

Read the file. Implement only the phase in `Current phase`. Leave later phases alone. Stop for the manual test.

When they answer:

- `PASS` — set that phase to `done`. Set `Current phase` to the next `pending` phase. Do not start it.
- `FAIL` — stay on that phase and fix it. Status stays `pending`.
- `SKIP` — set that phase to `skipped`. Move `Current phase` to the next `pending` phase. Do not implement the skipped work.

If they already said yes to a file, update that file in the same turn as the status change.

## Pitfalls

1. **A phase carrying two changes.** If the Test needs the word "and", it is two phases — and the pass no longer tells you which half broke.
   *Recovery:* split the card. One phase, one behavior difference, one thing to look at afterwards.
2. **A probe with no removal phase.** Debug logs, hard-coded values, throwaway endpoints and feature flags survive into the final state.
   *Recovery:* every probe card names the later phase that deletes it (`Remove in: Phase M`). If no later phase can delete it, delete it in the same phase or do not add it. When that phase runs, check the probe is actually gone.
3. **Continuing without an answer.** Implementing phase N+1 in the same turn as N, or moving on the moment after a `PASS`, removes the only point where a wrong direction can be caught cheaply.
   *Recovery:* stop after each phase and wait. On `PASS` mark `done` and set `Current phase` to the next `pending` — do not start it. On `FAIL` stay on that phase. On `SKIP` mark `skipped`. Write the file update in the same turn as the answer, or the next chat re-reads a stale `Current phase` and redoes finished work.
