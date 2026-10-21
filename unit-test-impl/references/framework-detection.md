# Framework detection — which runner, and why

The case document already records a runner in its `framework:` field. Read that
first. When it is missing (new document, hand-written plan), detect it here.

Order of precedence — stop at the first hit:

1. **Explicit config** — `pytest.ini`, `jest.config.js`, `phpunit.xml`, `pom.xml`, `go.mod`, `*.csproj`, `.mocharc.*`, `vitest.config.*`.
2. **Existing tests** — a `tests/`, `spec/`, `__tests__/`, `t/` directory, or `*_test.go`, `*.bats`, `test_*.py` files.
3. **Language default** — the zero-install harness for the language (see below).

Never mix two runners in one repository without a reason written down. A repo
where `pytest` and `unittest` both run is a repo where half the tests silently
never execute.

## Signal → framework → command

| Signal | Framework | Run command | Test file naming |
|--------|-----------|-------------|------------------|
| `pytest.ini`, `[tool.pytest]`, `conftest.py` | pytest | `python3 -m pytest -q` | `test_*.py` |
| `tests/` with `import unittest` | unittest | `python3 -m unittest discover -s tests -v` | `test_*.py` |
| `*.bats`, `bats` in CI | bats | `bats -r tests/` | `*.bats` |
| `tests/*.sh` with `set -e` + exit codes | plain bash | `bash tests/run.sh` (see harness below) | `tests/*_test.sh` |
| `go.mod` | go test | `go test ./...` | `*_test.go` |
| `Cargo.toml` | cargo test | `cargo test` | inline `#[cfg(test)]` or `tests/*.rs` |
| `jest.config.*`, `package.json` → `jest` | jest | `npx jest` | `*.test.ts`, `__tests__/*.ts` |
| `vitest.config.*` | vitest | `npx vitest run` | `*.test.ts`, `*.spec.ts` |
| `package.json` scripts `test: node --test` | node test runner | `node --test` | `*.test.mjs`, `*.test.js` |
| `.mocharc.*` | mocha | `npx mocha` | `test/*.js` |
| `pom.xml` | maven surefire | `mvn -q test` | `src/test/java/**/*Test.java` |
| `build.gradle`, `gradlew` | gradle test | `./gradlew test` | `src/test/java/**/*Test.java` |
| `phpunit.xml`, `vendor/bin/phpunit` | phpunit | `vendor/bin/phpunit` | `tests/**/*Test.php` |
| `Gemfile` + `spec/` | rspec | `bundle exec rspec` | `spec/**/*_spec.rb` |
| `*.csproj` | dotnet test | `dotnet test` | `*Tests.csproj` |
| `pytest` in `pyproject.toml` + `test_*.py` | pytest | `python3 -m pytest -q` | `test_*.py` |
| Docker-only project with a `test` service | compose | `docker compose run --rm test` | per the image |

## Zero-install fallbacks

When there is no runner at all, pick the one that adds no dependency. Prefer these
over asking for an install:

| Language | Harness | Notes |
|----------|---------|-------|
| Python | `unittest` | `python3 -m unittest discover -s tests -v`; no `pip` needed |
| Node ≥ 18 | `node --test` | Built in; `node --test tests/*.test.js` |
| Go | `go test` | Always present with the toolchain |
| Rust | `cargo test` | Same |
| Bash | exit-code harness | 5 lines, below |
| Anything else | Ask the user | Do not guess a framework into a project that has none |

### Plain-bash harness

```bash
#!/usr/bin/env bash
# tests/run.sh — exit 0 only if every case function passes
set -u
fails=0
for f in tests/*_test.sh; do
  # shellcheck source=/dev/null
  . "$f"
done
for fn in $(declare -F | awk '{print $3}' | grep '^ut_'); do
  if "$fn"; then echo "ok   $fn"; else echo "FAIL $fn"; fails=$((fails+1)); fi
done
[ "$fails" -eq 0 ] || { echo "$fails failing"; exit 1; }
```

Each case is a function with a behavioral name, and the canonical case ID
(`UT-<SLUG>-<NNN>`, uppercase, hyphens) in a comment on the line directly above it.
The ID string is the contract; the function name is for humans. Keep both, and do
not lowercase the ID in the comment — `grep` is case-sensitive.

## Adding a runner — ask first

If the project has no runner and the zero-install option is genuinely inadequate,
present the choice instead of installing:

```
No test runner in this repo.
  a) Use <zero-install harness> — no new dependency  (default)
  b) Add <runner> — needs <install command>, adds a dev dependency
  c) You install it, I write the tests against it
```

A skill that quietly adds `jest` to someone's project has changed the project,
not tested it.

## Record what you chose

Write the runner into the document's `framework:` field, and use the exact command
in `## Progress`. The next session should not have to re-detect anything — and the
report's suite line must be a command someone can paste and run.
