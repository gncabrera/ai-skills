# Case taxonomy — how to find the cases that matter

A case list is only as good as the questions asked while building it. This file
is the question bank: case types first, then the hunt checklist, then the smells
that mean a case is not really a case.

Use it as a checklist, not a template. Not every category applies to every unit —
but skipping one should be a decision, not an oversight.

---

## Case types

Every case carries exactly one `type:`.

### `happy` — the documented path

The input the unit was written for, with the state it expects. One per unit
minimum. Assert the **value**, not that it ran: `div(10, 2)` is `5.0`, not "no
exception".

### `edge` — a valid input at a boundary

Inputs that are legal but sit at the edge of the contract: zero, one, N, N+1,
empty string, empty list, maximum length, minimum permitted value, a single
element versus many. Two per unit minimum. Edges are where off-by-one lives.

### `error` — an invalid input or a violated precondition

What the unit promises when it cannot do its job. Assert the **type and message**
of the error, or the exit code — not merely that something went wrong. A unit
that throws `TypeError: unsupported operand` on bad input is not handling the
error, it is leaking it; that distinction belongs in the case.

### `regression` — a bug that already happened

For retrofit work this is the highest-value type: every bug found while reading
the code becomes a case that pins the fixed behavior. In the document, add the
`notes:` line with what went wrong, so the case is not deleted later by someone
who thinks it is redundant.

### `contract` — the shape other code depends on

Serialization format, JSON keys, CLI flags and their defaults, exit codes,
public function signatures, ordering guarantees, idempotency of a repeated call.
These cases exist to fail loudly when someone "cleans up" an interface that
consumers rely on.

---

## Hunt checklist

Work through these against each unit. Each entry: what to look for, and what the
assertion ends up looking like.

### 1. Absent or empty

`None`/`null`, `""`, `[]`, `{}`, a file with zero bytes, a directory with no
entries.

> `parse("")` returns an empty structure, not a crash. `load_dir(empty_dir)`
> returns `[]`, not `None`.

### 2. Single versus many

One element and many elements behave differently in almost every loop that
special-cases the first item.

> `join([a])` has no separator; `join([a, b])` has exactly one.

### 3. Boundaries — 0, 1, N, N+1

Whatever the limit is, test the limit, one below, and one above.

> `page_size=100` with 100 items returns 100; with 101 returns 100 and a cursor.

### 4. Duplicates

The same value twice, the same key in two sources, the same file listed twice.

> `unique([1, 1])` has length 1; `merge(a, a)` does not double-count.

### 5. Ordering and stability

Is the output sorted, or insertion-ordered, or arbitrary? If arbitrary, assert on
the **set**, never on the sequence.

> `list_tags()` returns a set equal to `{a, b}`, not a list in a specific order.

### 6. Unicode and multibyte

Accented characters, emoji, combining marks, right-to-left text, a string whose
length in bytes differs from its length in characters.

> `slugify("Café Münster")` is `"cafe-munster"`; `len_utf8("ñ")` is 2, not 1.

### 7. Whitespace and case

Leading/trailing spaces, tabs, internal double spaces, mixed case, a trailing
newline.

> `parse_flags(" --json ")` behaves the same as `parse_flags("--json")`.

### 8. Numeric limits

Zero, negative where positive is expected, the maximum representable value,
overflow, integer versus float division, rounding at the half.

> `div(1, 3)` compared with tolerance; `div(1, 0)` raises, does not return `inf`.

### 9. Wrong type or malformed input

A string where a list belongs, a float where an int belongs, truncated JSON,
a CSV row with too many columns.

> `parse("{\"a\":")` raises `JsonDecodeError` naming the position.

### 10. Permission denied

Read-only file, unreadable directory, a path the process may not traverse.
(Permission cases usually require a real filesystem — check whether the policy
allows it, or move to out-of-scope.)

> `write(path_in_readonly_dir)` surfaces the OS error, not a generic failure.

### 11. Missing file or directory

The path does not exist, the parent does not exist, the path is a directory when
a file was expected.

> `load("/nope.json")` raises `FileNotFoundError` with the path in the message.

### 12. Partial failure and rollback

The third of five items fails. Was the first two's work left behind, or rolled
back? Both answers can be correct — the case pins which one this unit promises.

> `write_all([ok, ok, bad])` leaves the target directory unchanged.

### 13. Idempotency and retry

Calling twice, retrying after a timeout, replaying the same request.

> `touch_state(x)` twice produces the same state and one journal entry.

### 14. Timeout and cancellation

A dependency that never answers, a signal mid-operation, a deadline that expires.

> `fetch(timeout=0)` raises `Timeout`, and the connection is closed.

### 15. Invalid state transitions

The operation is legal in state A but not in state B, and the unit must refuse.

> `seal(volume)` on an `open` volume refuses with a named reason; on a `sealed`
> volume it is a no-op or an error — pick one, then pin it.

### 16. Schema and backwards compatibility

An old input format, a missing optional field, an extra unknown field, a version
bump in the payload.

> `load_state({"schema": 1, ...})` refuses, naming the expected schema.

### 17. Documented versus actual (retrofit only)

Read the help text, the README, the error messages, the docstring — then run the
code mentally. Where they disagree, you have found either a bug or a stale
document. Both are findings; the case is written against the documented
behavior.

---

## Case smells

A case with one of these is worse than no case, because it produces green that
means nothing.

| Smell | Why it is wrong | Fix |
|-------|-----------------|-----|
| Two assertions about different behaviors | Which one failed is ambiguous, and one ficha = one test later | Split into two cases |
| The case restates the signature (`given: a string`, `when: call it`, `then: returns a string`) | Asserts types, not behavior | Name the specific input and the specific expected output |
| Asserts a mock was called instead of an outcome | Tests the test, not the unit | Assert the returned value or the state change; the call is incidental |
| Cannot fail — would pass against `return None` | Vacuous | Rewrite so a stub fails it |
| Requires a specific locale, timezone, or username | Fails on the next machine | Pin `TZ`/`LC_ALL` in the case, or move to out-of-scope |
| Depends on wall-clock time or a random value | Flaky by construction | Inject the clock; seed the generator and record the seed |
| Asserts on log text or a timestamp | Coupled to formatting nobody promised | Assert the observable result |
| Covers "everything else" | A dustbin case that never gets read | Delete it or name the behavior |

---

## Floor per unit

1 `happy`, 1 `error`, 2 `edge` — or a `notes:` line explaining why fewer.

A unit with only happy-path cases has a case list, not a test plan. A unit with
thirty cases has a scope problem: pick the ones that protect behavior someone
would notice breaking.
