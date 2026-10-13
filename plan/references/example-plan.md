# Example Plan (filled)

A realistic plan produced by `/plan "add rate limiting to the login endpoint"`.
Use it as a reference for the level of detail, the machine-readable `checks`
blocks, confidence tags, and wave structure a good plan should have.

---

# Plan: Add rate limiting to the login endpoint

## Execution Contract
> For the executor (may be a different model/session with no chat context).
- Read this plan top to bottom; assume **no** chat-only context exists.
- Execute **wave by wave**, and within a wave, issue by issue.
- After each issue, run its `checks` block; do not start the next issue until all pass.
- Only touch files listed in that issue's `files`.
- Treat `confidence: low` issues as risky: re-verify assumptions before coding; stop and report if reality differs.
- If a check fails or a decision is ambiguous, **stop and report** — do not guess.
- **Checkpoint:** commit at the end of each wave (`git commit -m "wave <n>: <summary>"`) so every wave is a rollback point.
- **Environment:** build `npm run build` · test `npm test` · lint/typecheck `npm run lint && npm run typecheck` · runtime `Node 20`

## Context
The `/api/login` endpoint has no rate limiting, so credential-stuffing attacks
can hammer it freely. We add a per-IP fixed-window limiter (5 attempts / 15 min)
backed by the existing Redis client, applied as Express middleware, returning
`429` with a `Retry-After` header when exceeded.

## Files to Modify
| File | Change |
|------|--------|
| `src/middleware/rateLimit.ts` | **NEW** — fixed-window limiter middleware |
| `src/routes/auth.ts` | Apply `rateLimit` to the `POST /login` route |
| `src/config/limits.ts` | **NEW** — window/limit constants |
| `test/middleware/rateLimit.test.ts` | **NEW** — unit tests |
| `test/routes/auth.test.ts` | Add 429-path integration test |

## Boundaries
**Always:** reuse the existing `redisClient` from `src/lib/redis.ts`; keep the 200 path unchanged.
**Ask first:** changing the limit/window defaults or applying limiting to other routes.
**Never:** add a new Redis connection or a new dependency.

## Baseline Audit
| Metric | Command | Result |
|--------|---------|--------|
| Existing middleware files | `rg --files src/middleware` | 3 files |
| Redis client entrypoint | `rg -n "createClient" src/lib/redis.ts` | `redis.ts:8` |
| Current login route tests | `rg -c "POST /login" test/routes/auth.test.ts` | 4 |

## Issues
### Issue 1: Add rate-limit config constants
- **Files:** `src/config/limits.ts`
- **Dependencies:** none
- **Confidence:** high
- **Acceptance:** exports `LOGIN_MAX_ATTEMPTS` (5) and `LOGIN_WINDOW_SECONDS` (900).
- **Description:** create the config module with the two constants and a short doc comment.
- **Checks:**
  ```yaml
  - type: files_exist
    paths: ["src/config/limits.ts"]
  - type: content_check
    file: src/config/limits.ts
    pattern: "LOGIN_MAX_ATTEMPTS = 5"
  ```

### Issue 2: Implement the rate-limit middleware
- **Files:** `src/middleware/rateLimit.ts`, `test/middleware/rateLimit.test.ts`
- **Dependencies:** Issue 1
- **Confidence:** high
- **Acceptance:** middleware increments a per-IP Redis key, allows the first 5 requests, and responds `429` + `Retry-After` on the 6th within the window.
- **Description:** implement `rateLimit(req,res,next)` using `redisClient.incr` + `expire`; reuse `LOGIN_*` constants. Cover allow, block, and window-reset cases in the test.
- **Checks:**
  ```yaml
  - type: content_check
    file: src/middleware/rateLimit.ts
    pattern: "export function rateLimit"
  - type: tests
    command: npm test -- rateLimit
  ```

### Issue 3: Wire middleware into the login route
- **Files:** `src/routes/auth.ts`, `test/routes/auth.test.ts`
- **Dependencies:** Issue 2
- **Confidence:** low
- **Acceptance:** `POST /login` runs `rateLimit` before the handler; the 6th rapid request from one IP returns `429`; valid logins still return `200`.
- **Description:** import and attach `rateLimit` to the login route only. Add an integration test that fires 6 requests and asserts the `429`. (Low confidence: confirm the router mounts middleware per-route vs. globally.)
- **Checks:**
  ```yaml
  - type: content_check
    file: src/routes/auth.ts
    pattern: "rateLimit"
  - type: tests
    command: npm test -- auth
  - type: lint
    command: npm run lint && npm run typecheck
  ```

## Execution Order
**Wave 1** (parallel): Issue 1
**Wave 2** (after Wave 1): Issue 2
**Wave 3** (after Wave 2): Issue 3

## File-Conflict Matrix
| File | Issues that touch it | Resolution |
|------|----------------------|------------|
| (none shared) | — | issues own disjoint files; safe to run in dependency order |

## Verification
1. Unit tests: `npm test -- rateLimit`
2. Full suite: `npm test`
3. Lint/typecheck: `npm run lint && npm run typecheck`

## Next Steps
- Review and approve
- Implement Wave 1 → 2 → 3, committing after each wave
