---
name: unit-test-impl
description: >-
  Execute a unit-test case document produced by the `unit-test-plan` skill: write
  one test per case with the case ID in the test name, run each test as you go,
  update every case's status, and report findings instead of editing production
  code. Language-agnostic — it detects the project's runner and follows its
  conventions. Use when the user says `/unit-test-impl` or asks to implement,
  write, or generate the tests from a test plan or case document.
disable-model-invocation: true
---

# unit-test-impl — Case Document to Tests

Sister skill to `unit-test-plan`. This skill consumes the case document and
produces tests. The document is the specification; this skill is the executor.

**Do exactly what the document says.** One test per case, the case ID in the test
name, no production-code edits, no invented cases. If the document is wrong or
ambiguous, report it — do not quietly improve on it.

## Gate

Refuse to start in these four situations, with these messages:

1. **No document, or the path does not exist**
   → `unit-test-impl: requires a case document. Run unit-test-plan first.`
2. **Document `status: draft`**
   → `unit-test-impl: <path> is still a draft. Review it, set status: ready, and re-run.`
   Offer to run the self-check from `unit-test-plan` if the issue is only hygiene.
3. **The document contradicts itself** — a case `done` or `finding` with no test
   in the tree, a `blocked`/`skipped` without `notes:`, duplicate IDs, a count in
   `## Progress` that does not match the fichas
   → report every inconsistency and stop. Fixing the tests around a broken ledger
   makes the ledger permanent fiction.
4. **Document `status: implemented`**
   → `unit-test-impl: nothing pending.` Report the counts and exit.

A document with some `done` cases and some `pending` cases is **not** a refusal —
that is a resume, and it is the normal case.

## Inputs

Invoked as `/unit-test-impl <doc>`.

| Flag | Purpose |
|------|---------|
| `--only ID[,ID]` | Execute only these cases (still must be `pending`) |
| `--priority P0\|P1\|P2` | Execute only cases at this priority |
| `--test-root DIR` | Where the tests live. Default: detected from the project |
| `--dry-run` | Print the selected cases, the runner, and the planned test names. Write nothing |

If no document is given, look for `docs/tests/*.md`; if there is exactly one, use
it; if there are several, list them and ask.

## Workflow

1. **Parse the document.** Extract frontmatter, every case (ID, title, all
   fields), the substitution map, and the `## Out of scope` section. Print the
   status breakdown before doing anything else:
   `14 cases — 9 done, 1 finding, 1 blocked, 3 pending`.
2. **Select work: `status: pending` only.** `done` and `finding` cases are already
   built; `blocked` and `skipped` are decisions, not work. Respect `--only` and
   `--priority` if given. This is what makes a second run idempotent: it touches
   nothing that already exists.
3. **Detect the runner.** Read `framework:` from the frontmatter first — a previous
   session already decided. Otherwise detect it:
   [references/framework-detection.md](references/framework-detection.md). Existing
   config wins over existing test files, which win over the language default. Never
   mix runners. Never install a dependency without asking.
4. **Match the project's conventions.** Sample one or two existing test files and
   mirror them: directory layout, file naming, import style, fixture style,
   assertion library, and the language the tests are written in. A test that reads
   like the rest of the suite is worth more than a prettier test that does not.
5. **Build the fakes once.** Follow the document's substitution map. If the project
   already has a test support module, extend it; otherwise create one small support
   file for the document's fakes. Never inline the same fake in five files.
6. **Write one test per case, in priority order (P0 → P2).** The test must be able
   to fail for exactly one reason: that case's `then`. Use `given` for setup,
   `when` for the single action, `then` for the assertion. The case ID appears in
   the test name or an adjacent comment (see [Test naming](#test-naming)).
7. **Run that test immediately**, alone. Then update the case status in the
   document:
   - **PASS** → `status: done`.
   - **FAIL with a real assertion mismatch on existing code** → `status: finding`,
     keep the test exactly as written, and record `case`, `file:line`, `expected`,
     `observed`. Do not weaken the assertion, do not mark it `xfail`, do not edit
     production code.
   - **FAIL because the case is under-specified** — the `then` does not pin a
     value, or `given` omits state the test needs → `status: blocked` with a
     `notes:` line naming the missing decision. Skip that unit's remaining cases
     and continue with the others.
   - **Never** self-approve a `skipped`. Only the user can exclude a case.
8. **Run the full suite.** A test that passes alone and fails in the suite is
   leaking state or depending on order — fix the test's isolation, not the suite.
9. **Run the checks in [Verification](#verification).** They are the proof that the
   ledger and the tree agree.
10. **Rewrite `## Progress`** from the fichas (counts, suite command, exact result,
    next action). Set document `status: implemented` only with zero `pending`,
    zero `finding`, zero `blocked`; otherwise leave it `ready`.
11. **Report** in the shape below, then stop. Do not continue into another
    document unless asked.

## Status transitions

| Outcome | Case status | Test kept? |
|---------|-------------|------------|
| Test written and green | `done` | yes |
| Test written, fails on existing code (real assertion) | `finding` | **yes** — the failure is the deliverable |
| Case cannot be implemented as written | `blocked` + `notes:` | no |
| Excluded by explicit user approval | `skipped` + `notes:` | no |
| Left untouched this run | `pending` | no |

`finding` is not a soft failure. It is the skill's whole value in a retrofit: the
test documents what the unit *should* do, the report says what it *does*, and the
decision about which one changes belongs to the user.

## Test naming

One rule: **the exact canonical ID — `UT-<SLUG>-<NNN>`, uppercase with hyphens —
appears in the test name when the dialect allows a hyphenated string, and
otherwise in a comment on the line directly above the test declaration.** This is
what makes coverage a `grep` instead of a promise. Never lowercase it, never split
it across lines, never abbreviate it.

| Dialect | Test name | Where the ID lives |
|---------|-----------|--------------------|
| pytest / unittest | `def test_div_by_zero_raises():` | `# UT-CRYO-STORE-001` on the line above |
| Go | `func TestDivByZeroRaises(t *testing.T) {` | `// UT-CRYO-STORE-001` above |
| Jest / Vitest | `it("UT-CRYO-STORE-001 div by zero raises", () => {` | in the name string |
| JUnit | `void divByZeroRaises() {` | `// UT-CRYO-STORE-001` above |
| xUnit / NUnit | `public void DivByZeroRaises() {` | `// UT-CRYO-STORE-001` above |
| RSpec | `it "UT-CRYO-STORE-001 div by zero raises" do` | in the name string |
| bash harness | `ut_div_by_zero_raises() {` | `# UT-CRYO-STORE-001` above |

Python, Go, Java, C# and bash cannot hold a hyphen in an identifier — the comment
**is** the contract there, not decoration. Keep the function name behavioral so it
still reads well; the comment carries the traceability.

```python
# UT-CRYO-STORE-001
def test_div_by_zero_raises():
    ...
```

Keep the title short and behavioral. `test_works` tells a future reader nothing;
`test_div_by_zero_raises` tells them why it exists.

## Verification

Run these before writing the report. Each catches a specific way the ledger and
the tests drift apart.

```bash
doc=docs/tests/<slug>.md
root=tests

# 1. Case IDs declared in the document
grep -oE '^### (UT-[A-Z0-9-]+-[0-9]{3})' "$doc" | awk '{print $2}' | sort > /tmp/ut-cases
# 2. Case IDs present in the test tree
grep -rhoE 'UT-[A-Z0-9-]+-[0-9]{3}' "$root" | sort -u > /tmp/ut-found

# 3. Cases with no test (expected: only blocked/skipped)
comm -23 /tmp/ut-cases /tmp/ut-found

# 4. Tests whose case no longer exists (stale after a re-plan)
comm -13 /tmp/ut-cases /tmp/ut-found

# 5. Cases that claim an outcome, with the claim
grep -nE '^- status: (done|finding|blocked|skipped)' "$doc"

# 6. A case that claims an outcome with no test behind it — the loudest failure
awk '/^### UT-/{id=$2} /^- status: (done|finding)/{print id, $3}' "$doc" |
while read -r id st; do
  grep -rqF -- "$id" "$root" || echo "LIE: $id claims $st"
done

# 7. The whole suite
<runner command from framework:>
```

Rules for reading the output:

- Every ID in (3) must be a `blocked` or `skipped` case with a `notes:` reason.
  A `pending` there just means work remains; a `done` or `finding` there is a lie —
  fix the status or write the test.
- Anything in (4) is an orphan: either the document dropped a case or a test name
  has a typo. Report it; never delete a test to make the list clean.
- Anything printed by (6) must be resolved before reporting. A ledger that claims
  `done` without a test is worse than a pending case.
- The count of (5) must equal the count of IDs minus the pending ones.
- (7) must be reported with the exact command and the exact counts. "Tests pass"
  without a command is not a report.

## Report

```
unit-test-impl — docs/tests/cryo-store.md

Runner:       python3 -m unittest discover -s tests -v
Cases:        14 total — 9 done, 1 finding, 1 blocked, 3 pending → 11 done, 1 finding, 1 blocked, 1 pending
Written:      UT-CRYO-STORE-003, -004
Findings:     UT-CRYO-STORE-007 — cryo_store.py:56 returns 0 for a missing file,
              document says it raises FileNotFoundError. Test kept.
Blocked:      UT-CRYO-STORE-011 — `then` does not pin the sort order. Needs a decision.
Suite:        12 tests — 11 passed, 1 failed (finding above)
Next action:  1 pending case (under-specified → blocked resolution needed)
```

Findings get their own section and their own line in `## Progress`. They are the
part of the run a human actually reads.

## Hard rules

- **Never edit production code.** Not to make a test pass, not "while you're
  there". A failing test on existing code is a `finding`.
- **Never hide a case.** No `skip`, `xfail`, `only`, `t.Skip`, `@Ignore`, early
  `return`, or commented-out assertion.
- **Never weaken an assertion to get green.** If the expected value is wrong, the
  document is wrong — report it and mark the case `blocked`.
- **One case, one test.** If a case needs two assertions about different
  behaviors, the document needs two cases; say so.
- **The ID literal is non-negotiable.** A test without it is invisible to every
  check in this skill.
- **No new dependencies without approval.** If the project has no runner, use the
  zero-install harness and record it in `framework:`.
- **No sleeps, no real network, no writes outside the temp dir.** Same policy the
  plan was written under; violating it here invalidates the case.
- **Commit tests and the document, nothing else.** `git status` after a run should
  show test files plus the plan document.
- **Stop at the gate.** A draft document, a broken ledger, or an ambiguous case is
  a conversation, not a workaround.

## Troubleshooting

| Problem | Response |
|---------|----------|
| Document has no `pending` cases | Nothing to do. Report counts; suggest `unit-test-plan` for the next unit |
| A case needs a dependency the substitution map does not cover | Mark it `blocked` with the missing substitution in `notes:`. The plan is incomplete |
| The project has no tests at all | Create the minimal structure for the detected harness, put the fakes in one support file, and record the runner in `framework:` |
| Two cases would produce nearly identical tests | Report it — one of them is redundant. Do not merge them silently |
| Test passes but you suspect it is vacuous | Replace the unit's body with a stub **in a scratch copy** and confirm the test fails. If it still passes, the case is bad: mark it `blocked` and say why |
| Suite was already red before you started | Report the baseline failure first. Your cases are not responsible for it, and the report must say so |
| The user asks to just fix the failing code | Out of scope for this skill. Record the `finding`, then fix it as a separate, deliberate change with its own plan |
| Runner config exists but the suite does not run | Stop. Fixing the harness is a prerequisite, not part of writing tests |

## Pair with

`unit-test-plan` — produced the document this skill consumes. Its contract
(frontmatter, ID grammar, field list, status enum) is what every check above
assumes; if the document deviates, the gate in step 3 is where it gets caught.

A document plus a green suite plus a clean verification run is a closed loop. A
document plus tests with no status updates is a half-finished job that will be
re-litigated by the next session.
