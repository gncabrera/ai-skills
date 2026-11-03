---
name: phased-plan
version: 1.1.0
description: >-
  Hand-testable phased plans: every phase is one observable change a person can
  check by hand, gated by PASS / FAIL / SKIP before the next one, with advisory
  model and reasoning recommendations for software phases. Offers to save the
  plan for another chat. Use when the user asks for a phased plan, a hand-testable
  rollout, step-by-step phases they verify themselves, or names this skill.
  Also use when a saved phased plan exists and the user replies PASS, FAIL, or
  SKIP. Not for issue/wave decomposition or machine-checked plans — that is the
  `plan` skill.
disable-model-invocation: true
---

# Phased hand-testable plan

Write the plan in the user's language. Do not implement it in the same turn.

Do not add unit tests unless they ask. Implementation stops after each phase until they answer `PASS`, `FAIL`, or `SKIP`.

## Before the phases

If a choice would change the files, the phase split, or the manual test, ask one or two questions first. Wait. Then write the plan.

If a skill already covers that area, read it before naming types, folders, or files. That skill wins on names.

## Model recommendations for software plans

For a new software-development plan, ask once which models to use for **MAX / MEDIUM / LOW** before writing phases. Offer the vendor profiles below and mixed/custom choices; show the proposed mappings together so the user can accept or edit them in one answer. Combine this with other necessary discovery questions when practical. Wait for the answer.

Accept a profile name such as `Claude`, or a compact answer such as `MAX=Opus 4.8/high; MED=Sonnet 4.6/medium; LOW=Haiku`. This is natural-language input, not executable configuration. Normalize MED to MEDIUM and MIN to LOW. A clear selection accepts the proposed entries without another confirmation loop. Clarify only genuinely unresolved entries; never repeat the full questionnaire. If an explicit mapping already exists in this conversation, ask whether to reuse it. A supplied saved plan's mapping is already confirmed: do not ask again just to resume it.

Record a concrete model and supported reasoning setting for each tier when possible. A family name alone is not a version: suggest a concrete available model when known, or mark its version/effort as unconfirmed. If the user delegates the choice, choose without another confirmation loop and disclose uncertainty. If they decline model selection, keep the recommended tier and use `Model: user choice, reasoning: not specified (MEDIUM; suggested)` with the applicable tier. Do not block planning.

### Vendor profiles

These are family-based suggestions, not a current catalog, API identifiers, or mandatory defaults. Resolve concrete entries with the user when making the plan.

| Profile | MAX | MEDIUM | LOW |
|---|---|---|---|
| Claude | Opus, high effort if supported | Sonnet, medium effort if supported | Haiku, supported low effort or fixed reasoning |
| DeepSeek | Pro, supported thinking/effort | Flash, supported balanced effort | Same Flash at supported lower effort/non-thinking, for mechanical work only |
| OpenAI / Codex | Available strong coding/reasoning model, high effort if supported | Available coding model, medium effort if supported | Available mini coding model or same model at supported lower effort |
| Google Gemini | Available Pro, high thinking if supported | Available Flash, supported balanced thinking | Available Flash-Lite, supported minimal/low thinking |
| Mixed / custom | User choice | User choice | User choice |

For example, a user might choose Opus 4.8/high and Claude Sonnet 4.6/medium, or `deepseek-v4-pro` and `deepseek-flash`. These are illustrative preferences, not requirements or claims of current availability. Do not invent a smaller DeepSeek model to fill LOW. The same model can occupy multiple tiers with different supported efforts or bounded task fit.

Respect older versions the user selects; do not substitute the newest model. Do not research catalogs for every plan. Consult provider/client documentation only when needed to resolve availability or reasoning support, or when the user asks for current suggestions. If verification is unavailable, disclose that uncertainty and continue. Use `reasoning: fixed` for confirmed fixed behavior and `reasoning: not confirmed` for unknown support; never invent effort flags or assume cross-vendor equivalence.

### Choose the tier

Tier describes the phase's capability needs; reasoning describes the chosen model's supported effort. They are not the same thing.

- **MAX:** ambiguous architecture, security/authentication boundaries, data-loss risk, concurrency, cross-cutting changes, or difficult debugging. A tiny diff can still be MAX.
- **MEDIUM:** normal feature implementation, bounded refactoring, and integration with known contracts. Default for ordinary coding phases.
- **LOW:** deterministic, localized work with explicit instructions and an obvious check: mechanical renames, prescribed documentation edits, trivial wiring. Unclear behavior is not LOW just because the patch is short.

Choose for the hardest part of the whole phase, including cleanup and verification, not line count, phase number, or brand. Do not split or merge observable phases just to fit model tiers.

Before recommending MAX, internally check what concrete uncertainty or consequence makes MEDIUM insufficient. If there is no meaningful reason, reconsider MEDIUM. Expose only the short `Why this model` justification, not private deliberation or a scoring system. This calibration never overrides an explicit user request for MAX.

### Precedence and advisory scope

Resolve model choices in this order: explicit user choice for a particular phase, confirmed plan-local profile, then illustrative presets. A phase override affects only that phase, not the whole tier. Respect even a weaker user-selected model; give a concise caveat if necessary without enforcing a substitution. Disclose unsupported settings instead of claiming they work.

Recommendations never switch the live model, configure providers, require subscriptions, or block implementation because the current model differs. No pricing, benchmarks, automatic model changes, or separate reviewer model belong in this workflow. Non-software plans keep the original flow without a mandatory model interview or model fields.

## Phase card

Every phase uses this card. One observable change. The pass must not need a later phase. Software phases include `Model` and `Why this model`; omit those two fields for non-software plans.

```markdown
### Phase N — Title
- Status: pending
- Model: Claude Sonnet 4.6, medium reasoning (MEDIUM; suggested)
- Why this model: bounded implementation with an established contract
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

Illustrative Claude profile: MAX = Opus 4.8/high, MEDIUM = Claude Sonnet 4.6/medium, LOW = the user's confirmed Haiku model with fixed reasoning. Concrete Haiku version is omitted in this illustration only; a real plan records it or marks it unconfirmed. Model/effort availability must not be inferred from these examples. Assume the schema, fixed row, and mail-delivery/idempotency contracts are already prescribed.

### Phase 0 — Empty table
- Status: pending
- Model: Haiku (illustrative family), reasoning: fixed (LOW; suggested)
- Why this model: the schema and empty-table migration are fully prescribed
- Change: add the `invoices` table only
- Test: run the migration. Open the database client. Look for `invoices`.
- Pass: the table exists and has zero rows
- Must not: no writer, job, or email code in this phase

### Phase 1 — One hard-coded row
- Status: pending
- Model: Haiku (illustrative family), reasoning: fixed (LOW; suggested)
- Why this model: one prescribed debug action with fixed values
- Change: a temporary debug action inserts one fixed invoice
- Test: run that action once. Read the table.
- Pass: exactly one row, with the fixed id
- Must not: a second run does not insert a second row
- Remove in: Phase 2

### Phase 2 — Real mapper
- Status: pending
- Model: Claude Sonnet 4.6, medium reasoning (MEDIUM; suggested)
- Why this model: integrate known order and invoice contracts, including probe cleanup
- Change: the real mapper writes the row. Delete the debug action from Phase 1.
- Test: submit order `ORD-100` through the normal save path. Read the new row.
- Pass: columns match that order. The debug action is gone.
- Must not: no email is sent

### Phase 3 — Send pending mail
- Status: pending
- Model: Claude Sonnet 4.6, medium reasoning (MEDIUM; suggested)
- Why this model: implement a bounded send path under established delivery/idempotency contracts
- Change: send mail for rows with `status = pending`, then set `sent`
- Test: trigger one send. Check the inbox and the row.
- Pass: one message arrives and the row is `sent`
- Must not: running it again does not send a second message

If the mailer instead requires designing delivery/idempotency semantics or resolving ambiguous external side effects, recommend MAX with that reason. Do not add a phase merely to display MAX.

## After the plan is in the chat

Ask once, with these three answers. Do not write a file before they answer.

> Save this plan to a file so another chat can continue it?
>
> - **a)** `tmp/<short-name>-plan.md`
> - **b)** I will paste a path
> - **c)** Do not save

`c` stops file-saving there. The chat plan is the deliverable; any later progress capsule stays in chat too.

`a` or `b`: write markdown. The file must stand alone. No secrets, connection strings, or credentials.

Start the file with:

```markdown
Current phase: N

Reply PASS, FAIL, or SKIP after the manual test.
Next chat: implement only the current phase. No unit tests unless requested. Stop for the test.
```

Then: decisions already made, what is done (with paths), every phase card, and what is out of scope. For software plans include the model profile before the cards:

```markdown
## Model profile
Recommendations only; use another model if preferred. No automatic switching.
- MAX: <confirmed model>, <supported reasoning setting>
- MEDIUM: <confirmed model>, <supported reasoning setting>
- LOW: <confirmed model>, <supported reasoning setting>
```

Populate actual entries or explicitly label user choice / unconfirmed settings. Preserve explicit phase overrides in their cards; another chat must not need private memory to resolve them.

## Continue a saved plan

Read the file. Implement only the phase in `Current phase`. Leave later phases alone. Stop for the manual test. Existing model recommendations are advisory, not gates. Legacy plans without model metadata remain executable: do not require retrofitting or a model interview just to continue.

When they answer:

- `PASS` — set that phase to `done`. Set `Current phase` to the next `pending` phase. Do not start it.
- `FAIL` — stay on that phase and fix it. Status stays `pending`. Reassess uncertainty; suggest a higher tier if useful and explain why. Update only that pending phase's recommendation when appropriate, respecting explicit overrides. Never change the live model automatically.
- `SKIP` — set that phase to `skipped`. Move `Current phase` to the next `pending` phase. Do not implement the skipped work.

If they already said yes to a file, update that file in the same turn as the status change.

### Profile changes

When the user changes the profile mid-project, update its block and applicable pending-phase recommendations only. Preserve explicit phase overrides unless the user explicitly replaces them too. Freeze `done` and `skipped` cards as historical records. Add one short note to the existing decisions/progress area explaining the profile change and pending-only scope. A profile edit does not authorize implementing, advancing, reopening, or rerunning a phase.

### Context capsule

After implementing a phase, leave a few lines in the existing `what is done` / progress area: key decisions, actual changed paths, manual-test result or `awaiting user test`, and unresolved blockers. Omit empty categories. No extra document or duplicated phase card. If saving was declined, put the capsule in chat; never create a file just for it.

Example shape, translated to the user's language: `Phase N handoff — Decisions: ...; Files: ...; Verification: awaiting user test; Blockers: none.` Replace placeholders with observed facts. Implementation checks never substitute for the user's PASS. A recommended model is not evidence of which model actually ran.

Refresh the capsule when the user gives a verdict. PASS/SKIP update the current-phase pointer under the existing rules, but never implement the next phase automatically; the capsule itself cannot authorize advancement. Keep it readable alongside the phase pointer and cards so another model can continue without private chat memory.

## Verification

Before presenting a new software plan, check that the profile was selected/delegated or explicitly declined, every phase has a model/tier and short reason, overrides win, and uncertain reasoning support is labeled. Check phase tests remain independently observable and any temporary probe has a removal phase. For non-software plans, omit mandatory model metadata.

Before handing off progress, check the capsule reports only observed facts, the user's verdict matches the status and current-phase pointer, and no finished/skipped recommendation was rewritten by a profile change. If saving was declined, confirm no plan or capsule file was created.

## Pitfalls

1. **A phase carrying two changes.** If the Test needs the word "and", it may be two independent changes — and the pass no longer tells you which half broke.
   *Recovery:* split independent behaviors. One phase, one behavior difference; necessary cleanup and its check can remain in that phase.
2. **A probe with no removal phase.** Debug logs, hard-coded values, throwaway endpoints and feature flags survive into the final state.
   *Recovery:* every probe card names the later phase that deletes it (`Remove in: Phase M`). If no later phase can delete it, delete it in the same phase or do not add it. When that phase runs, check the probe is actually gone.
3. **Continuing without an answer.** Implementing phase N+1 in the same turn as N, or moving on the moment after a `PASS`, removes the only point where a wrong direction can be caught cheaply.
   *Recovery:* stop after each phase and wait. On `PASS` mark `done` and set `Current phase` to the next `pending` — do not start it. On `FAIL` stay on that phase. On `SKIP` mark `skipped`. Write the file update in the same turn as the answer, or the next chat re-reads a stale `Current phase` and redoes finished work.
4. **Unsupported reasoning settings.** Model tiers and provider effort parameters get conflated.
   *Recovery:* verify support when needed; label fixed or unconfirmed behavior. Never invent settings or equivalent effort across vendors.
5. **Stale model catalogs.** Examples get mistaken for mandatory current defaults.
   *Recovery:* respect the user's chosen version; resolve availability only when needed and disclose uncertainty rather than forcing an upgrade.
6. **Advisory metadata becomes a gate.** The current model differs from the card, so work is refused or models are switched.
   *Recovery:* honor the user's model choice and continue under the original manual phase gates. Do not perform automatic routing.
7. **A risky small diff gets LOW.** Patch length hides authentication, data-loss or concurrency risk.
   *Recovery:* classify by the hardest risk/uncertainty of the entire phase and calibrate MAX with a concrete reason, not by code size.
