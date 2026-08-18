# Agentic Review — Phase 11, Milestone 1 (MCP Foundation)

> **Reviewer:** Independent agentic review session, no prior context on this implementation.
> **Scope:** Milestone 1 only (transport, auth, scope enforcement, handshake — zero MCP tools). Per `09_IMPLEMENTATION_TASKS.md` §0 and `IMPLEMENT.md`, this review does not self-grade the implementer's own report; every claim below was independently re-derived from the actual code, actual test runs, and (where practical) actual empirical probes against a running app instance.
> **Date:** 2026-08-18 (initial pass); re-verified same day after fixes.

**Verdict:** PASS

> First pass below reached **PASS WITH REQUIRED FIXES** (one BLOCKER, one MAJOR, two MINOR). All required fixes were applied and independently re-verified — not taken on the implementer's description — see **§5 Fix Verification**. The original findings are kept intact below for institutional memory, per instruction; §5 is the current, authoritative status.

---

## 1. What was checked

Read, in order: `IMPLEMENT.md`, `01_SPEC.md` (§1, §3, §4 in full), `03_BACKEND.md` §1–4, `06_API.md` §4a, `08_ACCEPTANCE.md` §1, `09_IMPLEMENTATION_TASKS.md` §0 + Milestone 1, `VERIFICATION_CONTRACT.md`, ADR-0018, ADR-0019.

Then, independently, without trusting the docs' claims:

- Read every file in the diff line by line: `backend/app/mcp/auth.py`, `backend/app/mcp/server.py`, `backend/app/main.py`, `backend/app/services/mcp/tokens.py`, `backend/app/models/mcp_token.py`, `backend/app/api/routes/mcp_tokens.py`, `backend/app/schemas/mcp_tokens.py`, `backend/app/core/config.py`, `backend/app/core/security.py`, `backend/app/core/errors.py`, `backend/app/api/deps.py` (confirmed unmodified), `backend/alembic/versions/0010_mcp_tokens.py`, `backend/alembic/versions/0001_initial_schema.py` (to verify the migration-guard claim), `docker/nginx.conf`, `docker-compose.yml`, `.env.example`, `backend/app/models/activity.py`, `backend/app/models/__init__.py`, `backend/app/api/router.py`.
- Ran `git status` / `git diff --stat` / `git status --porcelain` against `backend/app/api/deps.py`, `backend/app/api/routes/`, and the whole repo to independently confirm the declared file scope (§4 of `VERIFICATION_CONTRACT.md`) matches reality exactly. It does.
- Ran the four new test modules directly: `cd backend && .venv/Scripts/python.exe -m pytest tests/test_mcp_tokens_service.py tests/test_mcp_tokens_migration.py tests/test_mcp_tokens_api.py tests/test_mcp_server.py -v` — **29/29 passed**, confirmed myself, not taken on faith.
- Ran the full backend suite: `.venv/Scripts/python.exe -m pytest -q` — **all green**, no failures, no regressions.
- Ran the FDK verifier suite: `.venv/Scripts/python.exe -m pytest tools/tests -q` — **113/113 passed**, matching the contract's claim.
- Ran `docker build -t forge-mcp-m1-review-check ./backend` — **succeeded (exit 0)**, confirming the `mcp` PyPI dependency installs and the image builds cleanly with the new code, independently of the implementer's own build claim.
- Grepped every import statement in `backend/app/mcp/` and `backend/app/services/mcp/` for `services.secrets`, `services.crypto`, `services.settings` — **none found**. Confirmed the architectural boundary holds.
- Confirmed zero tools/resources are registered anywhere under `backend/app/mcp/` (no `tools/` subpackage exists yet, no `server.tool()`/`add_tool()` call site) — matches the milestone's "zero tools" requirement exactly.
- **Wrote and ran an independent empirical probe** (not part of the implementer's test suite) against a freshly built app instance to directly test the "cookie OR bootstrap" dual-auth claim for `POST /api/mcp/tokens` — completed first-run setup, obtained a real `forge_session` cookie, and called the route with the cookie only, no `Authorization` header. This is what surfaced the Blocker below.
- Traced migration `0010`'s existence-guard back to `0001_initial_schema.py` to determine whether it masks a genuine production-upgrade bug or only accommodates synthetic test fixtures (§5 of the task brief). Read the two migration test files it was written to fix (`test_projects_migration.py`, `test_knowledge_migration.py`) to confirm they hand-build partial schemas without `activity_log`.
- Read `app/mcp/server.py`'s DNS-rebinding-disable comment and independently judged the reasoning (§4 of the task brief).

## 2. Findings (as of the initial pass — see §5 for current/fixed status)

### BLOCKER — FIXED, see §5

**B1 — The "cookie OR bootstrap" dual-auth model for `POST/GET/DELETE /api/mcp/tokens` is non-functional; the cookie half never works.**

- **File:** `backend/app/api/routes/mcp_tokens.py`, `_require_session_or_bootstrap` (lines 22–43).
- **Root cause:** `require_auth` (`backend/app/api/deps.py`) declares `forge_session: Annotated[str | None, Cookie()] = None`. FastAPI only resolves `Cookie()`/`Header()`/`Query()` markers into actual request values when a function is wired into a route's dependency graph via `Depends(...)`. `_require_session_or_bootstrap` instead calls `await require_auth(session)` as a **plain Python coroutine call**, passing only `session`. `forge_session` therefore always receives its literal default, `None`, regardless of what cookie the browser actually sent. Inside `require_auth`, `not forge_session` is then always `True`, so it **always** raises `UnauthorizedError` — the `try/except AppError: pass` in `_require_session_or_bootstrap` silently swallows this every single time, and execution unconditionally falls through to `require_bootstrap_auth`.
- **Verified empirically, not just by reading the code.** I built a fresh app instance, completed `/api/setup` to obtain a real, valid `forge_session` cookie (confirmed present in the client's cookie jar), then called `POST /api/mcp/tokens` with that cookie and **no** `Authorization` header:
  ```
  setup status: 200
  cookies: {'forge_session': '1787106544.934b75a...'}
  cookie-only provisioning status: 401
  body: {"error":{"code":"unauthorized","message":"Invalid bootstrap token"}}
  ```
  The error message itself proves the code path: it is the exact string `require_bootstrap_auth` raises when no bearer token is present, meaning the request fell all the way through the "valid session" branch and failed only on the bootstrap check — a legitimate, freshly-authenticated owner's browser session was rejected outright.
- **Why this is a Blocker, not a Major:** this is not a peripheral nice-to-have. `01_SPEC.md` §4.3.1, ADR-0019 §2, `06_API.md` §4a, and `IMPLEMENT.md`'s own task table (M1-T4a: "`AuthDep` (cookie) alternative") all state this as a required, already-designed capability, not an aspiration. Worse, the **documented recommended hardening step** — `.env.example`'s own step 3, `docs/Deployment.md`, `01_SPEC.md` §4.3 — is "provision a token, then set `FORGE_MCP_BOOTSTRAP_ENABLED=false`." Once an operator follows that documented advice, **the only credential that was ever able to reach this route (bootstrap) is now disabled, and the cookie fallback that was supposed to remain available never worked in the first place.** The practical consequence: after following Forge's own documented hardening instructions, the owner has no way to provision a second token, list existing tokens, or revoke a compromised one through their own logged-in browser session — short of re-enabling the bootstrap credential (undoing the hardening) or hand-editing the database. This is a broken core guarantee of the milestone's own design, not a hypothetical edge case.
- **Why it wasn't caught:** `backend/tests/test_mcp_tokens_api.py` has ten tests, every one of them authenticates via `BOOTSTRAP_HEADERS`. Not one test in the entire diff calls any of the three `/api/mcp/tokens` routes using a `forge_session` cookie with no `Authorization` header. `test_mcp_server.py::test_browser_session_cookie_cannot_authenticate_against_mcp` tests the cookie against `/mcp` (correctly expecting 401 there), which is a different route entirely and does not exercise this code path at all. This is precisely the test gap the review brief asked me to check for ("is the cookie OR bootstrap dual-auth logic... fully exercised?") — it is not, and the reason it wasn't tested is that testing it honestly would have caught this.
- **Suggested fix:** wire `require_auth` as an actual FastAPI sub-dependency (e.g. give `_require_session_or_bootstrap` a `forge_session: Annotated[str | None, Cookie()] = None` parameter of its own and call `verify_session_token` /`settings_service.get_config` directly, or restructure as two separate `Depends`-based dependencies FastAPI can OR together via a small custom combinator), then add a test that authenticates with cookie-only (no `Authorization` header) and asserts success.

### MAJOR — FIXED, see §5

**M1 — `CURRENT_STATE.md` was not actually updated to reflect Milestone 1 completion, despite the verification contract checking it off.**

- **Files:** `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md`; contrast with `VERIFICATION_CONTRACT.md` §7, line `[x] CURRENT_STATE.md — updated to reflect Milestone 1 completion.`
- `CURRENT_STATE.md`'s content is unchanged from the pre-authorization planning stage: `## 1. Lifecycle stage` still reads **"Specification... has not been Authorized, no implementation task has started"**; `## 2. What exists right now` still says **"No application code has been written, modified, or committed for this phase. No migration exists. No `backend/app/mcp/` package exists. No ADR has been created."**; `## 3. What does NOT exist yet` still lists `IMPLEMENT.md` as **"not created"**. All of these statements are now false — `IMPLEMENT.md` exists and records Milestone 1 as authorized and complete, the migration exists, `backend/app/mcp/` exists, and both ADRs exist. This is a genuine discrepancy between what the verification contract claims was done (§7, checked `[x]`) and what the repository actually contains — exactly the class of "does the contract overstate what was verified" issue this review was asked to check for.
- **Impact:** doesn't compromise the security model, but it does mean anyone who reads `CURRENT_STATE.md` (the doc explicitly designed to be the "living snapshot of where this phase actually is") to get oriented on this phase's status would be actively misled into thinking Milestone 1 hasn't started.
- **Suggested fix:** rewrite `CURRENT_STATE.md`'s §1–§4 to reflect the actual Milestone 1 Implementation-stage status before this gate is re-run.

### MINOR

**m1 — Bootstrap token comparison is not constant-time. — FIXED, see §5**

- **File:** `backend/app/mcp/auth.py`, `require_bootstrap_auth`, line: `if not token or not expected or token != expected:`.
- This is a plain Python `!=` string comparison, which short-circuits on the first differing byte. Every other secret-comparison in this same phase (`verify_session_token` in `backend/app/core/security.py`, which the MCP work sits directly beside) correctly uses `hmac.compare_digest`. The bootstrap token is the single highest-privilege MCP credential (it can mint arbitrary-scope persistent tokens) and — per B1 above — is likely to remain the *only* working credential for this route for some operators in practice, making it more attractive as a target than the spec assumed.
- Practical exploitability over a real network (nginx + TLS termination in front, per Forge's documented deployment model) is low — network jitter typically swamps single-byte timing signal — so this is not rated as a Blocker, but it is a real, fixable inconsistency with the codebase's own established pattern for comparing secrets.
- **Suggested fix:** `hmac.compare_digest(token.encode(), expected.encode())` (guarding both against `None` first, as the code already does).

**m2 — Live Docker/nginx verification for AC1a/AC2/AC18 was manual, not automated.**

- `VERIFICATION_CONTRACT.md` §5 is explicit and honest about this ("Manually performed, not mechanically re-run by this contract") rather than silently omitting it, and `09_IMPLEMENTATION_TASKS.md` reserves a real `docker compose up --build` integration pass for Milestone 5 (M5-T5) — so this is a documented, accepted gap given the milestone's own scope, not an undisclosed one. I independently ran `docker build` (not `docker compose up`) and confirmed the image builds and the `mcp` dependency installs cleanly, which covers the Build-verifier-equivalent claim but not the live-proxy/handshake claims. Flagging only as a reminder that AC2's nginx-level 404 and AC1a's live-Docker rejection remain unverified by anything except human observation during implementation — acceptable for M1, should not be allowed to remain manual by M5.

## 3. Things independently verified and found solid (not padded — these were genuinely checked, not assumed)

- **AC1a (the milestone's single most important property) holds.** Read `McpBearerAuthMiddleware` line by line — there is no code path, fallback, or `or`-branch anywhere in it that accepts the bootstrap token; it only ever calls `tokens_service.verify()` against the `mcp_tokens` table. Confirmed by the passing `test_bootstrap_token_is_never_accepted_by_mcp_itself` test, and by manual code inspection finding no bypass.
- **`AuthDep`/`require_auth`/`api/deps.py` are genuinely untouched** — `git diff backend/app/api/deps.py` is empty, confirmed directly, not inferred from the contract's own claim.
- **No scope creep.** `git status --porcelain` across the whole repo matches `VERIFICATION_CONTRACT.md` §4's declared file list exactly — no Notes/Documents/Projects/Knowledge service file touched, no `frontend/` change, no MCP tool file created anywhere.
- **Zero MCP tools registered**, confirmed by absence of a `tools/` subpackage and no `server.tool()`/`add_tool()` call sites anywhere in the diff.
- **No import of `services/secrets`, `services/crypto`, or `services/settings`** anywhere in `backend/app/mcp/` or `backend/app/services/mcp/` — grepped every import line in both packages directly.
- **The migration-guard "fix" is correct, not bug-masking.** Traced `0001_initial_schema.py` and confirmed `activity_log` is created unconditionally via `SQLModel.metadata.create_all()` on every real install (fresh or historical), so migration `0010`'s `if "activity_log" in inspector.get_table_names()` guard is always true on any genuine upgrade path and only ever skips on the two migration tests' synthetic partial-schema fixtures (`test_projects_migration.py`, `test_knowledge_migration.py`, confirmed by reading their fixture setup — neither creates an `activity_log` table). This is a correct, narrowly-scoped fix, not a masked production bug.
- **The DNS-rebinding-disable trade-off (`app/mcp/server.py`) is reasoned soundly.** DNS-rebinding protection exists to stop a malicious webpage from using a victim's browser (with its ambient cookies/credentials) to reach a local, unauthenticated MCP server via a spoofed `Host` header. Forge's MCP auth is a static bearer token the operator manually configures into the Claude client — a malicious webpage cannot obtain or attach that token regardless of what `Host` header it sends, so the SDK's Host-allowlist heuristic protects against a threat model that doesn't apply here, while a real allowlist would break Forge's actual multi-hostname deployment model (LAN IP / Tailscale / reverse-proxied domain). I agree with the documented reasoning; this is not a bypass of the real auth boundary (`McpBearerAuthMiddleware`, which still runs unconditionally in front of it).
- **The `Depends`-to-ASGI-middleware deviation is a faithful adaptation, not a weakening.** Confirmed the enforcement guarantee (every request authenticated before any MCP protocol processing) holds by direct code reading and by the passing `test_missing_authorization_header_is_rejected_before_any_protocol_processing` test.
- **`last_used_at` write-throttling (AC4a) is real, not merely eventually-correct** — read `touch_last_used` and its two dedicated tests; the throttle window is enforced by comparing against the stored timestamp before writing, not by any client-side rate limit.
- **AC19 (auth-scheme independence) holds in both directions** — verified by the passing tests and independently confirmed the reasoning: `McpBearerAuthMiddleware` never reads cookies, `AuthDep` never reads the `Authorization` header.
- Genuinely tried to break the bootstrap-token exclusion (AC1a) by re-reading `McpBearerAuthMiddleware`, `require_mcp_auth`'s absence of any bootstrap-checking branch, and `tokens_service.verify()`'s query (`WHERE token_hash == candidate_hash AND revoked_at IS NULL`) — a bootstrap token's HMAC hash simply doesn't exist as a row in `mcp_tokens`, so there is no way for it to verify successfully there. Found no bypass.

## 4. Original release recommendation (first pass — superseded by §5/§6)

Milestone 1's actual security-critical foundation — the part the milestone exists to prove, i.e. that the bootstrap token can never reach `/mcp` and that `/mcp` itself is properly gated by a revocable, scoped, independently-authenticated bearer token — is solid, and I was unable to find any bypass after genuinely trying. The architecture (ADR-0018/0019), scope discipline (zero tools, zero touched files outside the declared list), and regression posture (142 tests green across the new suites, the full backend suite, and the FDK tools suite; a clean Docker build) are all real, independently confirmed, not just self-reported. However, Blocker B1 is a genuine, empirically-verified break in one of the two authentication paths the milestone's own task table (M1-T4a) commits to building, with a direct, documented operational consequence (the recommended post-provisioning hardening step leaves the owner locked out of managing their own tokens through the browser). This is squarely within Milestone 1's scope to fix — it does not require touching anything from Milestone 2 — so it should be repaired and this gate re-run, not treated as good enough to proceed past. **Milestone 2 should not be authorized until B1 is fixed, a regression test for the cookie-authenticated path is added and passing, and (while touching the same file) M1's contract is corrected — `CURRENT_STATE.md` genuinely updated (Major M1) and, ideally, the bootstrap comparison hardened to `hmac.compare_digest` (Minor m1).** None of these require new scope, new tools, or anything beyond what Milestone 1 already committed to; once fixed and re-verified, I would expect this to reach a clean PASS.

## 5. Fix verification (second pass — independently re-checked, not taken on the fix description's word)

For each fix, I re-read the actual current code (not the diff description supplied to me) and independently re-ran or re-derived the evidence.

### B1 (BLOCKER — cookie auth was dead code): confirmed fixed

- **Code re-inspected:** `backend/app/api/routes/mcp_tokens.py::_require_session_or_bootstrap` now declares `forge_session: Annotated[str | None, Cookie()] = None` on its own signature (line 24) and calls `await require_auth(session, forge_session)` (line 51), passing the FastAPI-resolved cookie value through explicitly instead of letting it default to `None` inside a bare coroutine call. This is the correct fix for the root cause I identified — `_require_session_or_bootstrap` itself is wired via `Depends(...)` at the router level, so FastAPI does resolve `Cookie()`/`Header()` markers declared directly on *its* signature; the bug was specifically that `require_auth`'s own cookie marker was unreachable when called as a plain function, and that is exactly what changed.
- **Independently re-ran the same empirical probe I used to originally find the bug** (not the implementer's new test — a second, self-written script): built a fresh app instance with `FORGE_MCP_BOOTSTRAP_TOKEN` **unset entirely** (to prove the cookie path works with zero dependency on bootstrap being configured at all, not merely "also" works), completed `/api/setup` to obtain a real `forge_session` cookie, and called all three routes with the cookie only, no `Authorization` header:
  ```
  setup status: 200
  cookies: {'forge_session': '1787107029.5587e1c9...'}
  cookie-only provisioning status: 201
  body: {"id":"24d28844f460411697529ea4234b6c46","name":"cookie-test-2","scopes":["forge:read"],...,"token":"jhyGLDALKdk_..."}
  cookie-only list status: 200
  cookie-only revoke status: 204
  ```
  All three previously-401 outcomes now succeed. This directly falsifies the original Blocker.
- **Ran the implementer's added regression test** — `test_mcp_tokens_api.py::test_browser_session_alone_can_provision_a_token_with_no_bootstrap_header` — read it in full (it also asserts a cookie-authenticated `GET /api/mcp/tokens` succeeds and lists the newly-created token) and confirmed it passes.
- **Full suite re-run:** `tests/test_mcp_tokens_service.py`, `test_mcp_tokens_migration.py`, `test_mcp_tokens_api.py`, `test_mcp_server.py` together: **30/30 passed** (29 before + the 1 new regression test). Full backend suite (`pytest -q`, whole `backend/`): all green, exit code 0, no failures. FDK tools suite (`pytest tools/tests -q`): **113/113 passed**, unchanged from before — confirms the fix introduced no regressions anywhere else.
- **Conclusion: B1 is genuinely fixed**, verified by independent code reading, an independently-authored empirical reproduction, and a full regression run — not by trusting the fix description.

### M1 (MAJOR — `CURRENT_STATE.md` staleness): confirmed fixed

- Re-read `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md` in full. §1 now reads "Implementation — Milestone 1 complete, Milestone 2 not authorized" (previously "Specification... not yet Authorized"). §2 now lists the actual shipped artifacts (`backend/app/mcp/`, the token service, the route, the migration, the nginx/compose changes, the new FDK verifier, the five new test modules, the doc updates) instead of asserting "no application code has been written." §4 correctly states the milestone checkpoint was reached and Milestone 2 requires separate explicit authorization, consistent with `IMPLEMENT.md`. §5 records both findings from this review (B1 and the timing-comparison minor) as institutional memory, with an accurate account of what each was and how it was fixed.
- No remaining false statements found in the file against the actual repository state I independently inspected earlier in this review.
- **Conclusion: M1 is genuinely fixed.**

### m1 (MINOR — non-constant-time bootstrap comparison): confirmed fixed

- Re-read `backend/app/mcp/auth.py::require_bootstrap_auth`. The comparison is now `hmac.compare_digest(token, expected)`, guarded by the pre-existing `not token or not expected` short-circuit (so `compare_digest` is never called with `None`). This matches `verify_session_token`'s existing pattern in `app/core/security.py` exactly, as suggested.
- **Conclusion: m1 is genuinely fixed.** (Not required for PASS per my original recommendation, but applied anyway and verified correct.)

### Full regression confirmation (independent of the targeted test re-runs above)

- `cd backend && .venv/Scripts/python.exe -m pytest -q` — full backend suite, re-run after all three fixes: all green, exit code 0.
- `.venv/Scripts/python.exe -m pytest tools/tests -q` — FDK verifier suite, re-run after all three fixes: **113 passed**, unchanged.
- No file outside the three fixes' expected scope (`backend/app/api/routes/mcp_tokens.py`, `backend/app/mcp/auth.py`, `backend/tests/test_mcp_tokens_api.py`, `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md`) was touched by this round — consistent with "repair only Milestone 1 scope" (`IMPLEMENT.md` Quality Gates §4).

## 6. Current release recommendation

All findings from the first pass have been independently re-verified as genuinely fixed — not merely reported as fixed. The BLOCKER (B1) was root-caused correctly (the fix addresses exactly the FastAPI-DI mechanism that caused the original failure, not a superficial patch), is proven by an empirical reproduction I wrote myself against the current code (not just the implementer's own regression test, though that one is also solid and adds `GET` coverage), and comes with no regressions across 30 targeted tests, the full backend suite, and the FDK tools suite. The MAJOR (M1) is a straightforward documentation correction, re-read in full and confirmed accurate against the repository state established earlier in this review. The MINOR (m1) was fixed as a bonus, correctly. Milestone 1's vertical slice — transport, auth (including the now-genuinely-dual-path token provisioning route), scope enforcement groundwork, and a zero-tool MCP handshake — is proven end-to-end, with no bypass of the bootstrap-token exclusion found after deliberately trying, no scope creep, and no architectural drift. **Milestone 2 (Knowledge CRUD) is clear to be authorized as a separate, explicit owner act**, per `IMPLEMENT.md`'s requirement that this review, not the implementing session, be the one to say so.
