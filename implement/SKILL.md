---
name: implement
description: >-
  Execute a plan produced by the `plan` skill: read a `plans/*.md` file and
  implement it wave by wave, honoring its Execution Contract, file ownership,
  and per-issue machine-readable checks. Language- and stack-agnostic — it
  follows the surrounding code and, if present, `AGENTS.md` conventions as
  advisory guidance. Use when the user says `/implement` or `$implement`, or
  asks to execute/build/carry out a plan, implement `plans/*.md`, or turn an
  issue-ready plan into working code.
disable-model-invocation: true
---

# implement — Execute an Issue-Ready Plan

Sister skill to `plan`. Consume a plan file and turn it into working code,
wave by wave, verifying each issue against its own checks. The plan file is the
contract; this skill is the executor.

**Do only what the plan specifies.** Do not expand scope, redesign, or touch
files the plan does not list. If the plan is ambiguous or wrong, stop and report.

## Inputs

Invoked as `/implement [plan-path]`.

| Flag | Purpose |
|------|---------|
| `--auto` | Skip the between-wave approval gate; run all waves end to end |
| `--wave N` | Execute only wave N, then stop |
| `--resume` | Continue from the run ledger + git state instead of starting over |
| `--dry-run` | Print the per-wave/issue action list and checks without editing files |

**Plan selection:** use the given `plan-path`; if none is provided, use the most
recently modified file in `plans/`. Confirm the chosen plan before starting.

## Workflow

1. **Locate & parse the plan.** Read the plan file. Extract the Execution
   Contract, Files to Modify, Boundaries, Issues (with `files`, `dependencies`,
   `confidence`, `checks`), Execution Order (waves), and Verification.
2. **Validate the plan (plan-lint).** Before touching code, statically check the
   plan and **stop with a clear message if any fails**:
   - every issue has non-empty `files` and at least one mechanical `checks` entry;
   - no two issues in the same wave share a file (matches the file-conflict matrix);
   - dependencies reference real issues and form no cycle;
   - the Execution Contract's environment commands are present.
   This catches a defective plan (e.g. from a weaker planner) before it breaks
   the repo.
3. **Resume or start fresh.** Look for the run ledger at
   `plans/<plan-slug>.run.md` (see [Run Ledger](#run-ledger)). With `--resume`,
   read it plus `git log` and continue at the first wave not marked done. Without
   `--resume`, if a ledger already shows progress, ask before overwriting it.
4. **Load conventions (advisory).** If `AGENTS.md` (or a similar conventions
   file) exists, read it and follow it as guidance. Also match the conventions
   of the surrounding code. Stay stack-agnostic: infer language, build, and test
   tooling from the repo and the plan's Execution Contract — never assume a
   specific framework. **Convention snapshot:** before the first edit of a given
   file type, sample 1–2 existing files of that type and mirror their style.
5. **Pre-flight.** Run the Execution Contract's environment commands
   (build/test/lint) to confirm a clean baseline. If the baseline is already
   broken, stop and report before changing anything.
6. **Execute wave by wave.** For each wave, in order, implement its issues.
   Because a wave's issues own disjoint files, **independent issues may be run in
   parallel** (e.g. dispatch one subagent per issue); serialize any that declare
   a dependency. For each issue:
   - Edit **only** the files listed in that issue's `files`.
   - Follow the issue's Description and Acceptance; keep changes minimal.
   - For `confidence: low` issues, re-verify the assumption against the real
     code first; if reality differs from the plan, **stop and report**.
7. **Verify each issue.** After an issue, run its `checks` block (see
   [Check Types](#check-types)). All must PASS before the next issue.
   - **On failure:** attempt an auto-fix and re-run the checks, up to **2
     retries**. If it still fails, **stop and report** with the failing check,
     the error, and what you tried. Record it in the ledger. Do not proceed.
8. **Review & checkpoint per wave.** When all issues in a wave pass:
   - **Self-review the wave diff** before committing — scan for bugs, scope
     leaks (files outside issue ownership), and AGENTS.md deviations. Fix or
     stop-and-report before committing.
   - Commit with traceability trailers:
     ```
     git commit -m "wave <n>: <summary>" -m "Issues: S1, S2" -m "Checks: PASS"
     ```
   - Update the run ledger (wave marked done, commit sha, checks status) and
     mirror the same state into the `TodoWrite` list.
9. **Approval gate.** Unless `--auto`, after each wave present a short status
   (issues done, checks passed, commit sha) and ask whether to proceed to the
   next wave, revise, or stop.
10. **Final verification.** After the last wave, run the plan's Verification
    section end to end, record the result in the ledger, and report.

## Check Types

Run each entry in an issue's `checks` YAML block and require PASS:

| `type` | How to run | PASS when |
|--------|-----------|-----------|
| `files_exist` | Check each path in `paths` exists | all exist |
| `content_check` | Search `file` for `pattern` | pattern found |
| `tests` | Run `command` | exit code 0 |
| `lint` | Run `command` | exit code 0 |
| `command` | Run `command` | exit code 0 |

If an issue has no mechanical check, treat it as underspecified: verify the
Acceptance criteria manually and flag it in the wave status.

## Run Ledger

Persist execution state to `plans/<plan-slug>.run.md` so a run is auditable and
**resumable by a different session or model** — the `TodoWrite` list is
session-local and does not survive a crash or model switch. Update it after each
issue and each wave. Suggested shape:

```markdown
# Run: <plan-slug>
Plan: plans/2026-07-03-add-rate-limiting.md
Started: <timestamp> · Executor: <model/session>

| Wave | Issue | Status | Checks | Commit |
|------|-------|--------|--------|--------|
| 1 | S1 | done | PASS | a1b2c3d |
| 2 | S2 | in_progress | — | — |
| 3 | S3 | pending | — | — |

## Notes
- S2: check `tests` failed once (missing import); fixed on retry 1.
```

On `--resume`, treat any wave whose issues are all `done` (and whose commit
exists in `git log`) as complete, and continue from the first incomplete wave.

## Guardrails

- Implement strictly to the plan; never widen scope or refactor unrelated code.
- Touch only files a given issue owns. If work seems to need another file, stop
  and report — the plan's file ownership may be wrong.
- Respect the plan's **Boundaries** (Always / Ask first / Never).
- `AGENTS.md` is advisory guidance, not a gate — follow it and the surrounding
  code, but the plan's instructions win on conflicts (and report the conflict).
- Never skip a failing check to "keep going." A red check stops the wave.
- Keep each wave's commit self-contained so it stays a clean rollback point.
- Never commit a wave that fails its self-review; fix or stop-and-report first.
- Keep the run ledger current — it is the durable, resumable source of truth.

## Handoff Note

This skill is the executor half of the `plan` → `implement` loop. Because the
plan file carries its own Execution Contract, `implement` can run in a fresh
session or a different model than the one that wrote the plan — it relies only
on the `plans/*.md` file, not on chat history.

## Troubleshooting

| Problem | Response |
|---------|----------|
| No plan path given | Use the newest file in `plans/` and confirm it before starting |
| Plan fails plan-lint (missing checks, shared files, dep cycle) | Stop and report the specific failure before editing code |
| Interrupted mid-run | Re-invoke with `--resume`; the ledger + `git log` restore progress |
| Baseline build/test already broken | Stop and report; do not start implementing |
| Check keeps failing after 2 retries | Stop; report failing check, error, and attempted fixes |
| Issue needs a file it doesn't own | Stop; the plan's file ownership is likely wrong |
| Two issues in one wave touch the same file | Stop; flag the plan's file-conflict matrix as invalid |
| Plan contradicts AGENTS.md | Follow the plan, report the conflict in the wave status |
