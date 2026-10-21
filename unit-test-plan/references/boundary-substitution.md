# Boundary substitution — keeping a test a unit test

A unit test observes one unit with every external boundary replaced. This file is
how to do that in each language, and — just as important — when to stop trying.

---

## The policy

| Rule | Why |
|------|-----|
| No network | A unit test that opens a socket is an integration test with extra steps, and it fails on the build machine |
| No real clock | `now()` makes the same test pass today and fail on the 31st |
| No writes outside a temp dir | Tests that leave files behind poison the next run |
| No `sleep` | A test that waits is a test that flakes |
| No subprocess to a real service | Same as network, with a shell in the middle |
| No database | Schema, state, and ordering make it non-repeatable |
| Deterministic ordering | If order is not part of the contract, assert on sets, not sequences |
| Seeded randomness | Record the seed in the failure message so a red test is reproducible |
| `TZ=UTC`, `LC_ALL=C` | Half the "works on my machine" stories start here |

If a case cannot be written under these rules, it moves to
`## Out of scope → integration`. That is a legitimate answer, not a failure.

---

## What to replace, and where to inject it

| Dependency | Fake | Injection point |
|------------|------|-----------------|
| HTTP client | Stub object returning fixed payloads, or a transport-level fake | Constructor argument, module import, or a client factory |
| Clock | A callable returning a fixed `datetime` | Passed in as `now` / `clock`; default to the real one at the call site |
| Filesystem root | A temp directory created per test | Path parameter, not a module-level constant |
| Environment variables | A patched mapping | Test-scoped fixture that saves and restores |
| Subprocess | A fake runner recording `(argv, env)` | Injected function, or a fake binary on `PATH` |
| Randomness | A seeded generator | Injected `rng`; print the seed on failure |
| Database | An in-memory repository implementing the same interface | Repository port passed to the unit |
| Queue / broker | A list-based fake with `publish`/`consume` | Client injected at construction |

The rule underneath all of them: **the boundary must be injected, not imported
inside the function body.** A unit that reaches for a global client cannot be
tested strictly, and that is a design finding to report in the plan — not a
reason to monkeypatch the world.

---

## Python

```python
# Injection over patching: the unit receives what it uses.
def fetch_user(client, user_id, *, now=lambda: datetime.now(timezone.utc)):
    return client.get(f"/users/{user_id}")

class FakeClient:
    def __init__(self, payload): self.payload, self.calls = payload, []
    def get(self, path):
        self.calls.append(path)
        return self.payload

def test_fetch_user_returns_name():
    c = FakeClient({"name": "pepe"})
    assert fetch_user(c, 7)["name"] == "pepe"
    assert c.calls == ["/users/7"]          # call detail is incidental, asserted once
```

When injection is impossible (third-party import inside the function), patch at
the seam and restore it — `unittest.mock.patch` as a context manager, never as a
decorator on a class (shared state across methods):

```python
with mock.patch("app.settings.SESSION", fake_session):
    ...
```

Temp files: `tmp_path` (pytest) or `tempfile.TemporaryDirectory()` (stdlib).
Env vars: `mock.patch.dict(os.environ, {...}, clear=False)`.

---

## Node / TypeScript

```ts
// Parameter injection — no mocking library needed.
export function total(items: Item[], tax: (n: number) => number) {
  return items.reduce((a, i) => a + i.price, 0) * (1 + tax(0));
}

// Module-level seams only when unavoidable:
vi.mock("./api", () => ({ getUser: async () => ({ name: "pepe" }) }));
```

Prefer a hand-written fake object over a mocking framework when the interface is
small: the fake is readable, typed, and survives a refactor. Use `vi.mock` /
`jest.mock` for modules the unit imports directly.

---

## Go

```go
type Clock interface{ Now() time.Time }

type Store struct{ clock Clock }              // injected

type fakeClock struct{ t time.Time }
func (f fakeClock) Now() time.Time { return f.t }

func TestStore_CreatedAt(t *testing.T) {
    s := Store{clock: fakeClock{t: time.Unix(0, 0)}}
    if got := s.CreatedAt(); !got.Equal(time.Unix(0, 0)) { t.Fatalf("got %v", got) }
}
```

Interfaces live at the consumer, not the producer. Temp dirs: `t.TempDir()`.
HTTP: `httptest.NewServer` for a real transport with a fake server — but that is
a boundary test; prefer a fake client for a unit.

---

## Java

```java
class ReportTest {
  @TempDir Path tmp;                       // real dir, isolated per test

  @Test void writesOneLinePerRow() throws IOException {
    var clock = Clock.fixed(Instant.EPOCH, ZoneOffset.UTC);
    var report = new Report(clock, tmp);
    report.write(List.of(new Row("a")));
    assertEquals(1, Files.readAllLines(tmp.resolve("report.txt")).size());
  }
}
```

Constructor injection; hand-written fakes for small interfaces; Mockito **only**
if the project already depends on it. Never `mockStatic` on the class under test.

---

## C#

```csharp
public interface IClock { DateTime UtcNow { get; } }

public sealed class Report(IClock clock) {
    public string Stamp() => clock.UtcNow.ToString("O");
}

[Fact]
public void Stamp_uses_injected_clock() {
    var r = new Report(new FrozenClock(new DateTime(2026, 1, 1, 0, 0, 0, DateTimeKind.Utc)));
    Assert.StartsWith("2026-01-01T00:00:00", r.Stamp());
}
```

Interfaces plus small hand-written fakes; `dotnet test` as the runner. Avoid
static/ambient dependencies — they are the C# version of the global client.

---

## Bash

Bash has no mocking. Two techniques, and one honest limit.

### Technique 1 — extract the pure function and source it

```bash
# script.sh
quote_remote() { printf '%q' "$1"; }

# script_test.sh
source ./script.sh                       # functions only, no main
[ "$(quote_remote 'a b')" = "a\\ b" ] || { echo "FAIL"; exit 1; }
```

Guard the entry point so sourcing does not execute the script:

```bash
[ "${BASH_SOURCE[0]}" = "$0" ] && main "$@"
```

### Technique 2 — `PATH` shims

Prepend a temp directory of fake executables, then drive the real script:

```bash
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/bin" "$tmp/out"

cat > "$tmp/bin/lsblk" <<'FAKE'
#!/usr/bin/env bash
printf '%s\n' '{"blockdevices": [{"name": "sdb", "serial": "ZA29MA0D"}]}'
FAKE
chmod +x "$tmp/bin/lsblk"

PATH="$tmp/bin:$PATH" TMPDIR="$tmp/out" \
  ./volume.sh status >"$tmp/out/stdout" 2>"$tmp/out/stderr"
rc=$?

[ "$rc" -eq 0 ] || { echo "FAIL: rc=$rc"; cat "$tmp/out/stderr"; exit 1; }
grep -q 'ZA29MA0D' "$tmp/out/stdout" || echo "FAIL: serial not in output"
```

Rules for shims: fake by **behavior** (`lsblk` returns JSON on stdout), capture
stdout and stderr to files so you can assert on both, never let the script see the
real environment (`TMPDIR`, `HOME` inside the temp dir), and assert the exit code
before anything else.

### The honest limit

A script that is 90% calls to external commands is integration. Shimming six
binaries to observe a seventh line of output produces a test that breaks every
time the script's output format changes, while proving almost nothing about the
logic. Write the case under `## Out of scope → integration`, and extract the
logic that is worth testing.

---

## Determinism checklist

Before a case is accepted, it must survive:

- two consecutive runs, in either order, in the same workspace
- a different timezone (`TZ=America/Argentina/Buenos_Aires`)
- a different locale (`LC_ALL=C` and `LC_ALL=en_US.UTF-8`)
- a different working directory
- a fresh temp directory
- parallel execution alongside the rest of the suite

If any of those changes the result, the case is not a case yet.
