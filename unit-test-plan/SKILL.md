---
name: unit-test-plan
description: >-
  Design a unit-test case document before any test is written: read a target
  module, package, or CLI, inventory its units, map the external dependencies to
  substitutes, and emit numbered cases with given/when/then, an observable
  result, and a per-case status. Language-agnostic. Use when the user says
  `/unit-test-plan` or asks to plan unit tests, enumerate test cases, decide what
  to test, or produce a test plan for existing code. Planning only — writes no
  test code.
disable-model-invocation: true
---

# unit-test-plan — Case Design Before Test Code

Sister skill to `unit-test-impl`. This skill answers **what to test and how you
would know it worked**, and writes the answer down as one reviewable document.
It never writes a test, never runs a test, and never claims a case is done.

**The case document is the contract.** Everything downstream — the tests, the
ledger, the report, a different agent picking the work up next week — reads that
file. A case that is vague in the document becomes a guess in the code.

## Inputs

Invoked as `/unit-test-plan <target>`.

| Flag | Purpose |
|------|---------|
| `--out PATH` | Where to write the document. Default `docs/tests/<slug>.md` |
| `--mode retrofit\|greenfield` | `retrofit` (default): code exists, derive cases from intended vs actual behavior. `greenfield`: code does not exist yet, derive from the spec |
| `--policy strict-unit\|pragmatic` | `strict-unit` (default): no network, clock, disk, DB, subprocess. `pragmatic`: temp files and real fixtures allowed, network and DB still out |
| `--spec PATH` | Behavior spec, README section, help text, or issue description |
| `--diff REF` | Scope the inventory to symbols touched by a diff, branch, or PR |

**Target resolution.** A file, a directory, a package, or a CLI plugin folder.
If only a target is given, derive cases from the code. If a `--spec` is also
given, **the spec wins for intended behavior** and the code is cross-checked
against it — a disagreement is a finding, not a case. If `--diff` is given,
inventory only the touched symbols; the rest of the module is context, not scope.

## Workflow

1. **Resolve the target and its slug.** Slug is the target path compressed to
   uppercase `[A-Z0-9-]`, max 12 characters: `plugins/cryo/cryo_store.py` →
   `CRYO-STORE`; `src/auth/session.ts` → `AUTH-SESSION`. Every case ID starts
   with it (`UT-CRYO-STORE-001`), so documents from the same repo can never
   collide.
2. **Detect the language and the existing test setup.** Signals, in order: a
   runner config file; existing test files; the language's default harness.
   Record what you found in the frontmatter (`language:`, `framework:`). If the
   project has no tests at all, say so and pick the zero-install harness — do not
   introduce a dependency without asking the user.
3. **Inventory the units.** Every public function, class, method, or CLI
   subcommand with an externally visible contract. One line each: *what it
   promises*. Include how many tests it has today (usually zero — that number is
   the point of the exercise). Private helpers belong to the unit that uses them
   unless they carry real logic of their own.
4. **Build the substitution map.** List every external dependency the units
   touch — network client, clock, filesystem root, environment variable,
   subprocess, database, randomness — and how each will be replaced, and where
   it gets injected. A dependency you cannot substitute is a case that moves to
   out-of-scope, not a case you pretend to test. Recipes per language:
   [references/boundary-substitution.md](references/boundary-substitution.md).
5. **Derive cases per unit.** Use
   [references/case-taxonomy.md](references/case-taxonomy.md). Floor per unit:
   one happy path, one error path, two edges — or a written reason in `notes:`
   why fewer.
6. **Run the anti-vacuity check on every case.** *If the implementation were
   replaced by a stub, would this case fail?* If no, the case asserts nothing —
   rewrite it or drop it.
7. **Write the document** from the template below. Every case is emitted as
   `status: pending`.
8. **Self-check before presenting** — the one-liners in
   [Self-check](#self-check).
9. **Present and promote.** Show the case count by type and the open questions.
   The document stays `status: draft` until the user says it is right; then set
   `status: ready`.
10. **Hand off.** Point at [Handoff to another tool](#handoff-to-another-tool)
    if the tests will be written somewhere else.

## The case document

Frontmatter — every value is a quoted string (an unquoted YAML date parses as a
date object and breaks every consumer that expects a string):

```yaml
---
plan: "unit-tests"
slug: "CRYO-STORE"
target: "plugins/cryo/cryo_store.py"
language: "python"
framework: "unittest"
mode: "retrofit"
policy: "strict-unit"
created: "2026-10-21"
status: "draft"
---
```

Two statuses live in this document and they are not the same thing:

| Scope | Field | Values | Written by | Question it answers |
|---|---|---|---|---|
| Document | frontmatter `status` | `draft`, `ready`, `implemented` | this skill creates it, the user promotes it to `ready`, `unit-test-impl` sets `implemented` | Has a human signed off, and is it all built? |
| Case | `- status:` in each ficha | `pending`, `done`, `finding`, `blocked`, `skipped` | **this skill only ever writes `pending`**; `unit-test-impl` owns the rest | What happened to this specific case? |

```
pending ──test written, green─────────────────► done
pending ──test written, red on existing code──► finding    (test kept, bug reported)
pending ──case under-specified────────────────► blocked    (requires notes:)
pending ──approved exclusion──────────────────► skipped    (requires notes:)
done    ──behavior changed, test removed──────► pending    (re-plan; never delete silently)
```

- `done` and `finding` both mean *a test containing that exact ID exists*.
  `blocked` and `skipped` mean there is no test and there will not be one until
  someone acts.
- `blocked` and `skipped` **require** a non-empty `notes:`. A silent skip is how
  a coverage report starts lying.
- The document may only reach `status: implemented` with zero `pending`, zero
  `finding`, zero `blocked`.

Case heading grammar — this is the whole parser contract:

```
### UT-<SLUG>-<NNN> — <title>
```

`UT-`, the slug from the frontmatter, a 3-digit number starting at `001` with no
gaps in intent (renumbering breaks traceability, so don't). The line must start
at column 1.

Required fields per case:

- `status:` one of the five values above
- `type:` `happy` | `edge` | `error` | `regression` | `contract`
- `priority:` `P0` | `P1` | `P2`
- `target:` the symbol — `file::function`, `file::Class.method`, or a CLI
  subcommand
- `given:` preconditions and state, in one sentence
- `when:` exactly one action, with the literal input value
- `then:` the observable result — return value, exception type and message,
  exit code, stdout/stderr content, or resulting file state. "It works" and "no
  error" are not observables
- `substitutes:` what is replaced, or the literal word `none`

Optional: `source:` (code `file:line` or spec reference), `notes:` (why the case
exists, or the reason for `blocked`/`skipped`).

## Document template

````markdown
---
plan: "unit-tests"
slug: "<SLUG>"
target: "<path>"
language: "<language>"
framework: "<runner>"
mode: "retrofit"
policy: "strict-unit"
created: "<YYYY-MM-DD>"
status: "draft"
---

# Unit test cases — <target>

## Scope

**In scope:** <units covered by this document>

**Out of scope → integration:** <behavior that needs real I/O, one line of reason each>

## Unit inventory

| Unit | Contract (one line) | Tests today |
|------|--------------------|-------------|
| `<symbol>` | <what it promises> | 0 |

## Substitution map

| Dependency | Fake | Injected at |
|------------|------|-------------|
| <e.g. HTTP client> | <stub object returning fixed payloads> | <constructor arg / module import> |

## Cases

### UT-<SLUG>-001 — <title>

- status: pending
- type: happy
- priority: P0
- target: `<file>::<symbol>`
- given: <preconditions>
- when: <one action with the literal input>
- then: <observable result>
- substitutes: <dependency, or none>
- source: `<file>:<line>`
- notes: <why this case exists>

## Findings

<Bugs or suspicious behavior spotted while reading the code. Empty for greenfield.>

## Open questions

1. <Blocking ambiguity, or "none">

## Definition of done

<N> cases, each mapped to exactly one test containing its exact ID (in the test
name, or in the comment on the line above where the language forbids hyphens),
suite green or every red test recorded as a `finding`. No `pending`, no `blocked`.

## Progress

- Cases: <N> total — 0 done, 0 finding, 0 blocked, <N> pending
- Suite: not run yet
- Next action: run `unit-test-impl` on this document
````

`## Progress` is derived, never hand-authored to taste: its counts must equal the
counts of the fichas above it, and `unit-test-impl` rewrites it after every run.
That block is what lets a fresh session resume in five seconds.

One naming expectation lives in this document and in the executor: each case is
implemented by exactly one test that contains the **exact canonical ID**, uppercase
with hyphens. Where the language forbids a hyphen in an identifier (Python, Go,
Java, C#, bash), the ID goes in a comment on the line above the test. A test
carrying only `ut_my_slug_001` in its function name is invisible to every coverage
check, so the plan should state the expectation in `## Definition of done` rather
than leave it to chance.

## Handoff to another tool

The document is also a prompt. To hand the work to Cursor, Codex, Claude Code, or
any other agent, point it at the file with:

```
Read docs/tests/<slug>.md. Implement its `pending` cases following the
unit-test-impl rules: one test per case, the exact case ID in the test name or the
comment above it, never edit production code, and flip each case's status as you go.
```

Three conditions, or the ledger becomes fiction:

1. The document must be `status: ready` before it leaves your hands.
2. The receiving tool must uphold the status semantics — if it silently writes
   `done` without running a test, the next reader has no way to tell.
3. If it cannot uphold them, let it generate tests only, and let `unit-test-impl`
   own every status transition.

## Scope discipline

A strict unit test observes one unit with every external boundary replaced. When
a behavior only exists through real I/O — a real mount, a real port, a real
schema migration — the honest move is to write it under
`## Out of scope → integration` with one line of reason, not to mock the world
until the test looks like a unit test. Reconciliation against real systems is a
different job with a different failure mode.

Bash is where this bites hardest: a script that is 90% external commands is
integration, and no amount of `PATH` juggling changes that. Two legitimate
options, in order of preference:

1. **Extract the pure logic** into a function and test that function with `source`
   plus arguments.
2. **`PATH` shims** — a temp directory of fake binaries prepended to `PATH`, with
   `TMPDIR` isolated and stdout/stderr captured to files. Use this when you must
   drive the script's own dispatch.

Details and code for both: [references/boundary-substitution.md](references/boundary-substitution.md).

## Guardrails

- Never write test code. Not a snippet, not "for illustration".
- Never write a status other than `pending`. You ran no tests, so you know nothing
  about outcomes. `done` from the planning side is a lie with extra steps.
- No case without an observable `then`. "Returns without error" is not an
  observable.
- Never mock the unit under test. If the only way to observe it is to fake it, it
  belongs in out-of-scope.
- One behavior per case. Two assertions in one ficha means two cases.
- Never renumber existing IDs. If a case is wrong, edit it; if it is obsolete,
  say so in `notes:` and mark it `skipped`. Numbers are references.
- No placeholders left in a document you call `ready`. `<...>` is for the
  template only.
- No log-text or timestamp assertions. They pass on your machine and fail on the
  next one.
- Never invent a framework. If the project has none, say so and use the
  zero-install harness.

## Self-check

Run these before presenting the document. Each one catches a specific way the
contract breaks:

```bash
doc=docs/tests/<slug>.md

# 1. Every case has a well-formed ID and they are contiguous from 001
grep -oE '^### (UT-[A-Z0-9-]+-[0-9]{3})' "$doc" | awk '{print $2}' | sort

# 2. No case is missing a required field
grep -cE '^- (status|type|priority|target|given|when|then|substitutes):' "$doc"

# 3. Every case is pending (anything else means this document was not written by this skill)
grep -cE '^- status: pending$' "$doc"

# 4. blocked/skipped carry a reason
awk '/^### UT-/{id=$2; st=""} /^- status:/{st=$3} /^- notes:/{if(st=="blocked"||st=="skipped") print id": ok"}' "$doc"

# 5. No leftover placeholders
grep -n '<[A-Za-z]' "$doc" || echo "clean"
```

Counts from (1) and (3) must be equal. If (4) prints nothing and the document has
`blocked` or `skipped` cases, those cases are undocumented decisions.

## Troubleshooting

| Problem | Response |
|---------|----------|
| Target is a whole repo | Split it. One document per package or CLI verb; the slug keeps them apart |
| Module is all I/O with no pure logic | Say so. Propose extracting the pure part and write cases for that; record the rest as out-of-scope with reasons |
| A unit needs six fakes to test | Suspicious. Usually a missing seam — check whether one fake can stand in for the boundary instead of six |
| Spec and code disagree | Record it in `## Findings`, write the case against the spec, and flag it in the open questions. Do not silently encode the current behavior |
| User wants every branch covered | Branches are not cases. Ask what behavior each branch exists to protect; if the answer is "none", that is the finding |
| Project has no test runner | Use the zero-install harness for the language and record it in `framework:`. Ask before adding a dependency |

## Pair with

`unit-test-impl` — consumes this document, writes one test per case, owns the
status transitions, and rewrites `## Progress`. A document that is never handed
to it is a design exercise, which is still cheaper than 40 tests nobody wanted.
