---
name: plan
description: >-
  Decompose a goal or research artifact into an issue-ready implementation plan
  with dependency waves, file ownership, acceptance criteria, and mechanical
  validation checks, written to a markdown plan under `plans/`. Use when the
  user says `/plan` or `$plan`, or asks to plan work, break down a feature,
  decompose a goal into issues/tasks/tickets, produce an execution/handoff
  plan, or turn research into a buildable spec. Planning only — keep WHAT
  separate from HOW and do not implement.
disable-model-invocation: true
---

# plan — Issue-Ready Decomposition

Turn a goal or research note into a durable markdown plan: a file inventory,
discrete issues with acceptance criteria, dependency waves, and validation
commands. The plan should let a fresh session execute without any chat-only
context.

**Execute this workflow — don't just describe it.** Keep planning separate from
implementation: produce the plan, do not write feature code.

## Inputs

Invoked as `/plan <goal>` or `/plan <path-to-research.md>`.

| Flag | Purpose |
|------|---------|
| `--auto` | Skip the approval gate and produce the plan directly |
| `--fast` | Force a minimal 1–2 issue plan |
| `--deep` | Force symbol-level detail (file:line reuse points, signatures) |

## Workflow

1. **Gather inputs.** Read the goal and any referenced research, prior plans,
   or notes. If context is thin, explore the codebase (or dispatch an `explore`
   subagent) for a file inventory, symbol names, reuse points with `file:line`,
   test locations, and import relationships.
2. **Baseline audit.** Before making any quantitative claim, mechanically count
   the current state: files, LOC, tests, endpoints, schemas. Record the exact
   commands (`rg`, `Glob`, line counts) and their results.
3. **Choose detail level.** Minimal for 1–2 simple issues, Standard for 3–6,
   Deep for 7+ issues, broad refactors, or `--deep`.
4. **Decompose into issues.** Each issue gets a title, file ownership,
   dependencies, acceptance criteria, and at least one **mechanical** check in
   the machine-readable `checks` YAML block (`files_exist`, `content_check`,
   `command`, `tests`, or `lint`) so a different model can run them without
   interpreting prose. If an acceptance criterion can't be checked mechanically,
   mark it underspecified. Tag each issue `confidence: high|low` — set `low`
   when assumptions are unverified, so the executor knows where to be cautious.
5. **Compute waves.** Group independent issues into parallel waves. Serialize
   or merge any issues that write the same file — two parallel issues must never
   touch the same file. List every touched file in ownership, including tests,
   docs, schemas, and fixtures.
6. **Write the plan.** Save to `plans/YYYY-MM-DD-<goal-slug>.md` using the
   template below. Always fill in the **Execution Contract** — it is what makes
   the plan safe to hand to a different model/session.
7. **Track tasks.** Mirror the issues into the `TodoWrite` tool so execution
   sessions have live task state.
8. **Approval gate.** Unless `--auto`, present the plan and ask whether to
   proceed, revise, or gather more context.

## Plan Template

```markdown
# Plan: <Goal>

## Execution Contract
> For the executor (may be a different model/session with no chat context).
- Read this plan top to bottom; assume **no** chat-only context exists.
- Execute **wave by wave**, and within a wave, issue by issue.
- After each issue, run its `checks` block; do not start the next issue until all pass.
- Only touch files listed in that issue's `files`.
- Treat `confidence: low` issues as risky: re-verify assumptions before coding; stop and report if reality differs.
- If a check fails or a decision is ambiguous, **stop and report** — do not guess.
- **Checkpoint:** commit at the end of each wave (`git commit -m "wave <n>: <summary>"`) so every wave is a rollback point.
- **Environment:** build `<cmd>` · test `<cmd>` · lint/typecheck `<cmd>` · runtime `<version>`

## Context
<1–2 paragraphs: the problem, current state, and why this change is needed.>

## Files to Modify
| File | Change |
|------|--------|
| `path/to/file.ts` | Description of change |
| `path/to/new_file.ts` | **NEW** — description |

## Boundaries
**Always:** <non-negotiables — security, backward compat, tests>
**Ask first:** <decisions needing human input>
**Never:** <explicit out-of-scope items>

## Baseline Audit
| Metric | Command | Result |
|--------|---------|--------|
| <what was measured> | `<rg/glob/count command>` | <result> |

## Issues
### Issue 1: <Title>
- **Files:** `path/to/file.ts`
- **Dependencies:** none
- **Confidence:** high  <!-- high | low — mark low when assumptions are unverified -->
- **Acceptance:** <how to verify — behavior + edge cases>
- **Description:** <what to do>
- **Checks:** (machine-readable; the executor runs each and requires PASS)
  ```yaml
  - type: content_check
    file: path/to/file.ts
    pattern: "export function authenticate"
  - type: tests
    command: npm test -- auth
  ```

### Issue 2: <Title>
- **Files:** `path/to/other.ts`
- **Dependencies:** Issue 1
- **Confidence:** low
- **Acceptance:** <how to verify>
- **Description:** <what to do>
- **Checks:**
  ```yaml
  - type: files_exist
    paths: ["docs/api-v2.md"]
  - type: lint
    command: npm run lint
  ```

## Execution Order
**Wave 1** (parallel): Issue 1, Issue 3
**Wave 2** (after Wave 1): Issue 2

## File-Conflict Matrix
| File | Issues that touch it | Resolution |
|------|----------------------|------------|
| `path/to/shared.ts` | Issue 1, Issue 2 | serialize in Wave 1 → 2 |

## Verification
1. Unit tests: `<command>`
2. Full suite: `<command>`
3. Lint/typecheck: `<command>`

## Next Steps
- Review and approve
- Implement Wave 1
```

## Handoff / Execution

The plan file (`plans/*.md`) is the **only** durable handoff — it must be
executable by a fresh session or a **different model** without any chat context.
The `TodoWrite` mirror is session-local and does **not** transfer across
models/sessions, so never rely on it as the handoff.

When the executor is a different (or less capable) model:

- **Generate with `--deep`.** Give symbol-level detail (`file:line` reuse
  points, function signatures, inline snippets) so the executor makes no
  architectural decisions.
- **Lean on mechanical Checks.** Each issue must be self-verifiable without
  human judgment (`tests`, `content_check`, `files_exist`, `lint`).
- **Fill the Execution Contract** with concrete build/test/lint/runtime
  commands — the executor's boot instructions live there.

Cross-model routing (e.g. one model plans, another executes) happens outside
this skill: point the executing session/tool at the plan file. The plan is
model-agnostic by design. The sister skill `/implement` is the executor — it
reads a `plans/*.md` file and runs it wave by wave.

## Guardrails

- Keep WHAT and HOW distinct; do not implement while planning.
- Prefer concrete file paths, symbol names, and runnable validation commands
  over narrative prose.
- Schema/interface changes go in an earlier wave than their consumers.
- No parallel issues sharing a file — serialize or merge them first.

## Examples

**`/plan "add rate limiting to the API"`**
Produce a plan with a file inventory, issues with acceptance criteria and
checks, wave order, and a file-conflict matrix.

**`/plan --auto "plans/research-auth.md"`**
Use the research as input, write the plan, mirror issues into `TodoWrite`, and
skip the approval gate.

For a full worked example (filled template, machine-readable checks, confidence
tags, waves), see [references/example-plan.md](references/example-plan.md).

## Troubleshooting

| Problem | Response |
|---------|----------|
| Context is thin | Explore enough to produce file and symbol evidence before decomposing |
| Same file in parallel issues | Serialize or merge those issues |
| Acceptance can't be checked mechanically | Mark it underspecified before handing off |
| Baseline audit missing | Mark the plan incomplete until the counts are recorded |
