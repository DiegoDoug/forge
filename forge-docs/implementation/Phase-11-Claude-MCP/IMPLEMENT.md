# Claude MCP / Second Brain — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md).
> **Ownership:** Project owner.
> **Status:** ✅ **Milestone 4 (Claude Memory Workflows) checkpointed and committed — 2026-08-19. Milestone 5 explicitly NOT authorized until the owner opens it.**
>
> Fourteen gates recorded, in order, as separate, explicit acts — none implies the next, exactly as the planning package's own §17 required and as Phase 09's precedent established:
>
> 1. **Architecture direction approved (2026-08-18)** — the owner reviewed the full planning package (`01_SPEC.md` through `09_IMPLEMENTATION_TASKS.md`) and approved the architecture direction (Option A: in-process MCP server; bearer-token auth model), after requesting and receiving six amendments (bootstrap-token/persistent-token lifecycle, transactional/existence-checked delete, `forge_context` N+1 and project-scoping fixes, activity-log dedup, mandatory `get_note` service method — see `CURRENT_STATE.md` §4 for the full list).
> 2. **Milestone 1 implementation authorized (2026-08-18)** — granted explicitly, scoped to Milestone 1 **only**. The owner's own words: *"I would authorize Milestone 1 only. ... Then the new Agentic Review verifier gets its first real test."*
> 3. **Milestone 1 checkpointed, PASS (2026-08-18)** — mechanical verification 8/8, Agentic Review PASS after one repair cycle (a real BLOCKER found and fixed — see [`reviews/AGENTIC_REVIEW_M1.md`](reviews/AGENTIC_REVIEW_M1.md)). Full record: [`../../history/2026-08-18-phase-11-milestone-1-checkpoint.md`](../../history/2026-08-18-phase-11-milestone-1-checkpoint.md), committed at `6854971`.
> 4. **Milestone 2 authorized (2026-08-18)** — the owner's own words, as a direct instruction following the M1 checkpoint: *"Commit the M1 checkpoint work. M2 authorized."* Granted as its own act, not inferred from the M1 PASS — matching the boundary gate 3 established.
> 5. **Milestone 2 gate PASS (2026-08-18)** — mechanical verification 8/8, Agentic Review PASS after one repair cycle. The repair cycle was substantive: a real BLOCKER (a boolean-coercion bypass letting `confirm: "true"`/`1`/etc. authorize a permanent delete the same as literal `true`) plus two MAJOR findings (a raw DB exception leak on a bad `project_id`; an output-shape documentation ambiguity) — see [`reviews/AGENTIC_REVIEW_M2.md`](reviews/AGENTIC_REVIEW_M2.md).
> 6. **Milestone 2 checkpointed and committed (2026-08-18)** — the owner's own words: *"checkpoint and commit M2, then stop."* Full record: [`../../history/2026-08-18-phase-11-milestone-2-checkpoint.md`](../../history/2026-08-18-phase-11-milestone-2-checkpoint.md). **Explicitly a stopping point** — the instruction was to stop, not to proceed to Milestone 3.
> 7. **Milestone 3 authorized (2026-08-19)** — the owner's own words, in chat, as a direct instruction: *"Start Milestone 3 implementation."* Granted as its own act, matching the boundary gates 2 and 4 established — not inferred from anything in Milestone 2's checkpoint.
> 8. **Milestone 3 implementation complete, mechanical verification green (2026-08-19)** — full backend suite 375/375 (before the repair cycle below), FDK suite 113/113, Docker build succeeded.
> 9. **Milestone 3 gate PASS (2026-08-19)** — the independent Agentic Review's first pass reached PASS WITH REQUIRED FIXES (zero BLOCKER, three MAJOR, three MINOR — see [`reviews/AGENTIC_REVIEW_M3.md`](reviews/AGENTIC_REVIEW_M3.md)). All six findings were addressed in a repair cycle; the same reviewer independently re-verified every fix by reproducing the original failing scenarios (not by trusting the fix description), and returned a final verdict of **PASS**. Backend suite 377/377 after the repair cycle.
> 10. **Milestone 3 checkpointed and committed (2026-08-19)** — the owner's own words: *"checkpoint and commit M3, then stop. M4 remains explicitly unauthorized until I open it."* Full record: [`../../history/2026-08-19-phase-11-milestone-3-checkpoint.md`](../../history/2026-08-19-phase-11-milestone-3-checkpoint.md). **Explicitly a stopping point** — the instruction was to stop, not to proceed to Milestone 4. Nothing here authorizes Milestone 4 (M4-T1 onward); that remains a separate, future, explicit act the owner has stated they will initiate themselves.
> 11. **Milestone 4 authorized (2026-08-19)** — the owner's own words, in chat, as a direct instruction: *"Start milestone 4 implementation."* Granted as its own act, matching the boundary gates 2, 4, and 7's established pattern exactly — not inferred from anything in Milestone 3's checkpoint.
> 12. **Milestone 4 implementation complete, mechanical verification green (2026-08-19)** — full backend suite 395/395 (up from 377 after Milestone 3's repair cycle; +18 new tests, 0 regressions), Docker build succeeded. FDK suite 103/113 — the 10 failures are pre-existing and environment-specific (a Windows/Git-Bash subprocess-invocation quirk in `BuildVerifier`/`TestVerifier`, confirmed by direct traceback inspection), not caused by this milestone; zero files under `tools/` were touched.
> 13. **Milestone 4 gate PASS (2026-08-19)** — the independent Agentic Review's first pass reached PASS WITH REQUIRED FIXES (zero BLOCKER, one MAJOR, one MINOR — see [`reviews/AGENTIC_REVIEW_M4.md`](reviews/AGENTIC_REVIEW_M4.md)). The MAJOR (`06_API.md` §5's `forge://projects` Auth cell overclaiming enforced `forge:read`, when the resource structurally cannot enforce it) was fixed with a footnote stating the true, current behavior; the MINOR (generic resource-error messages) was deliberately left as backlog per the reviewer's own non-blocking classification. The same reviewer independently re-verified the fix — re-reading the actual diff and re-running the backend suite, not trusting the fix description — and returned a final verdict of **PASS**. Backend suite remains 395/395 after the repair cycle (docs-only change, no code/test touched).
> 14. **Milestone 4 checkpointed and committed (2026-08-19)** — the owner's own words: *"checkpoint and commit M4."* Full record: [`../../history/2026-08-19-phase-11-milestone-4-checkpoint.md`](../../history/2026-08-19-phase-11-milestone-4-checkpoint.md). Nothing here authorizes Milestone 5; that remains a separate, future, explicit act.
>
> [ADR-0018](../../decisions/0018-mcp-server-integrated-not-separate-process.md) and [ADR-0019](../../decisions/0019-mcp-bearer-token-authentication.md) are **Accepted** as of this review.
> **Last Updated:** 2026-08-19

---

## Role

You are implementing Phase 11 — Claude MCP / Second Brain, acting as the engineer of record. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific and milestone-specific detail only. **Milestone 4 is complete, checkpointed, and committed. Milestone 5 — Production Hardening & Release — is explicitly NOT authorized and stays closed until the owner opens it themselves; do not begin any M5 task, however small, without that separate, explicit act.** Milestones 1–4's rules are kept as historical record below; do not re-execute them, and do not treat their "Autonomy Rules" as governing whatever milestone comes next — each milestone gets its own.

## Milestone 1 — MCP Foundation (complete, historical record — do not re-execute)

### Mission

Prove the narrow vertical slice defined in [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md)'s Milestone 1 section — transport, auth, scope enforcement, and MCP handshake — with **zero Notes/Documents/Projects CRUD tools**. This is deliberately the smallest possible end-to-end proof, so a transport/auth defect cannot hide behind a CRUD-tool bug. See `01_SPEC.md` §1, §3, §4 for the architecture this milestone stands up.

### Read order for a session working this milestone

1. [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md)
2. **This document**
3. [`CURRENT_STATE.md`](CURRENT_STATE.md) — the amendment history and current status
4. [`01_SPEC.md`](01_SPEC.md) §1, §3, §4, §7 — architecture, transport, auth, ADRs
5. [`03_BACKEND.md`](03_BACKEND.md) §1–§4 — package layout, auth dependencies, config
6. [`06_API.md`](06_API.md) §4a — the token-provisioning route (the only REST surface in this milestone)
7. [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) — Milestone 1's task table and gate criteria
8. [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §1 — the acceptance criteria this milestone must satisfy
9. [`VERIFICATION_CONTRACT.md`](VERIFICATION_CONTRACT.md) before declaring the milestone done

### Execution Rules

- [x] **Scope is locked to Milestone 1's task table in `09_IMPLEMENTATION_TASKS.md`.** M1-T1 through M1-T9, and nothing from Milestone 2 onward. `forge_get_note`, any other tool, any tool registry with a non-empty tool list — all out of scope for this milestone, however small the addition might seem.
- [x] **Zero MCP tools registered in this milestone.** The `/mcp` handshake must succeed and `tools/list` must return an empty (or correctly-shaped, zero-length) list. Registering even one tool "to make the milestone feel more complete" is scope creep and must not happen.
- [x] **The bootstrap token must never be accepted by `/mcp`.** This is the single most important security property of this milestone — test it explicitly (AC1a), don't just implement it and assume.
- [x] **`AuthDep`/`require_auth` and every existing `/api/*` route are untouched.** `git diff --stat` against any file under `api/routes/` other than the new `mcp_tokens.py` must be empty.
- [x] **No Secrets/Settings/Crypto import anywhere under `app/mcp/` or `app/services/mcp/`.** Verified by AC10-equivalent static check even though Milestone 1 has no read/write tools yet — the import boundary should be correct from the first line of code, not retrofitted in Milestone 2.
- [x] **Follow [`../../07_CODING_STANDARDS.md`](../../07_CODING_STANDARDS.md) exactly** — thin routers, logic in `services/`, models are schema source of truth, every schema change is an explicit Alembic migration.
- [x] **The new `mcp` PyPI dependency is the only new external dependency this milestone introduces.** Recorded in `06_TECH_STACK.md`.
- [x] `CURRENT_STATE.md` updated.

### Autonomy Rules

**Satisfied.** All Milestone 1 work stayed within these bounds; no Milestone 2 task was touched, `AuthDep`/`require_auth` remained untouched (confirmed by the Agentic Review), and the milestone was not declared complete until the Agentic Review returned PASS (after one repair cycle).

### Quality Gates — all satisfied, PASS

1. [x] Every M1-T1..T9 task complete.
2. [x] Complete mechanical verification contract run — 7/7 applicable verifiers PASS.
3. [x] Independent Agentic Review — PASS (after one repair cycle; see `reviews/AGENTIC_REVIEW_M1.md`).
4. [x] Repair cycle stayed within Milestone 1 scope (a dual-auth bug in the already-in-scope `mcp_tokens.py` route, plus a stale doc — neither was Milestone 2 work smuggled in as a "fix").
5. [x] Checkpointed at [`../../history/2026-08-18-phase-11-milestone-1-checkpoint.md`](../../history/2026-08-18-phase-11-milestone-1-checkpoint.md), committed at `6854971`. Did not release, merge, tag, or freeze. Did not begin Milestone 2 until the owner's separate, explicit authorization (gate 4 above).

### The specific ways this milestone could have gone wrong (for reference — none of these actually happened)

1. Scope creep toward "while I'm here" (stubbing a tool since the pattern was right there) — did not happen.
2. Self-graded review — did not happen; the Agentic Review was run by an independently-spawned agent with no memory of implementation decisions, and it found a real BLOCKER a self-review would likely have missed.
3. Silently narrowing "PASS WITH REQUIRED FIXES" into "good enough" — did not happen; the finding was fixed and independently re-verified before the verdict changed to PASS.
4. Declaring the bootstrap-token exclusion correct without testing it — did not happen; tested explicitly (`test_bootstrap_token_is_never_accepted_by_mcp_itself`) and independently re-confirmed by the reviewer via its own empirical probe.

---

## Milestone 2 — Knowledge CRUD (complete, checkpointed, committed — historical record, do not re-execute)

### Mission

Add semantic MCP tools over Notes, Documents, and Projects — `forge_get/create/update/delete_note`, the same four for Documents, and `forge_list/get/create/update_project` (no project delete) — reusing the existing `services/notes`, `services/documents`, `services/projects` modules exactly as the REST routes already do. This is the first milestone where the system can create, modify, and **destroy** real persistent knowledge through MCP, and the first where `ActivityLog` gets genuine `source="mcp"` rows. Full contract: `06_API.md` §1–§2, `01_SPEC.md` §6 (CRUD safety), `09_IMPLEMENTATION_TASKS.md`'s Milestone 2 table (M2-T0 through M2-T6).

### Read order for a session working this milestone

1. [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md)
2. **This document**, in full — including Milestone 1's historical record above, since Milestone 2 builds directly on `app/mcp/auth.py`'s `require_scope` and the token/scope model it established
3. [`CURRENT_STATE.md`](CURRENT_STATE.md)
4. [`01_SPEC.md`](01_SPEC.md) §4.4 (scopes), §4.5 (audit logging — the corrected, no-double-logging design), §5.3 (`forge_get_note` mandate), §6 (CRUD safety — the exact delete sequence)
5. [`03_BACKEND.md`](03_BACKEND.md) §2 (service-layer reuse map) and §2's activity-log/`source`-threading note
6. [`06_API.md`](06_API.md) §1–§2 in full — every tool's exact input/output/error/audit contract
7. [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) — Milestone 2's task table and gate criteria
8. [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §2 (Knowledge CRUD ACs: AC6–AC10) and AC20 (no ORM bypass)
9. [`VERIFICATION_CONTRACT.md`](VERIFICATION_CONTRACT.md) before declaring the milestone done

### Execution Rules

- [x] **Scope is locked to `09_IMPLEMENTATION_TASKS.md`'s Milestone 2 table.** M2-T0 through M2-T6. No `forge_search`/`forge_context`/`forge_link_items` (Milestone 3), no memory-capture tools (Milestone 4), no `forge_delete_project` — confirmed by the Architecture Verifier and the Agentic Review (zero scope creep found).
- [x] **`source="mcp"` threads through the *existing* `activity.record(...)` call inside each service function — no MCP tool handler calls `activity.record` a second time.** Verified with `test_create_note_produces_exactly_one_activity_row_with_mcp_source`. **Refined during implementation**: `update_note`/`update_document` never called `activity.record` for *any* caller (a fact the plan itself had wrong) — correctly left un-instrumented rather than gaining new logging behavior as a side effect. See `CURRENT_STATE.md` §5.
- [x] **`forge_delete_note`/`forge_delete_document` follow the exact 3-step sequence**: existence check → `purge_links_for` (staged) → delete (stages + commits atomically). Verified by `test_delete_nonexistent_note_stages_zero_changes` and its Document-side symmetric test.
- [x] **`confirm: true` is structural only.** **Implementation note**: the JSON-Schema-level `const: true` originally sketched here turned out not to be directly expressible through the MCP SDK's schema generation for a `Literal[True]` type without extra friction; the equivalent guarantee is achieved with `pydantic.StrictBool` (rejects any non-boolean JSON value, e.g. `"true"`/`1`/`"yes"`, at the validation layer) plus the existing runtime `is not True` check for the one case StrictBool alone doesn't cover (`confirm: false`). **This exact enforcement point was where the Agentic Review's BLOCKER was found** — the original `confirm: bool` (plain, not strict) silently let `"true"`/`1`/etc. authorize a delete. Fixed, and covered by a dedicated parametrized regression test (`test_delete_note_rejects_non_boolean_confirm_values`) — see `reviews/AGENTIC_REVIEW_M2.md`.
- [x] **Every read/write tool calls a `services/*` function — never a raw ORM query.** AC20 static check (`test_mcp_tools_static_checks.py`, broadened during the repair cycle to recursively scan all of `app/mcp/**`, not just `tools/*.py`) — passes.
- [x] **No import of `services/secrets`, `services/crypto`, or `services/settings` anywhere under `app/mcp/tools/`.** Confirmed, same static check.
- [x] **Every tool's scope check uses `require_scope`.** Confirmed per-tool by the parametrized scope-enforcement tests and the Agentic Review's line-by-line check of all 12 handlers.
- [x] `CURRENT_STATE.md` updated.

### Autonomy Rules

**Satisfied.** No Milestone 3 task was touched; `AuthDep`/`require_auth`/`McpBearerAuthMiddleware` remained unmodified (confirmed via `git diff`); the milestone was not declared complete until the Agentic Review returned PASS (after one repair cycle addressing a real BLOCKER — a materially different, and correctly *not* self-graded, outcome).

### Quality Gates — all satisfied, PASS

1. [x] Every M2-T0..T6 task complete.
2. [x] Full mechanical verification contract green — 7/7 applicable verifiers.
3. [x] Independent Agentic Review — PASS (after one repair cycle; see `reviews/AGENTIC_REVIEW_M2.md`).
4. [x] Repair cycle stayed within Milestone 2 scope (the `StrictBool` fix, `validate_project_id` addition, and doc clarifications are all corrections to already-in-scope Milestone 2 code — no Milestone 3 work was smuggled in).
5. [x] Gate reached PASS; **checkpoint/commit and Milestone 3 authorization both intentionally withheld pending separate, explicit owner acts** — matching Milestone 1's precedent exactly.

### The specific ways this milestone could have gone wrong (for reference — most did not; one genuinely did)

1. The audit-double-logging bug, reintroduced — **did not happen**; verified by a dedicated test.
2. The `purge_links_for`-before-existence-check bug, reintroduced — **did not happen**; verified for both Notes and Documents.
3. An ORM bypass "just this once" — **did not happen**; zero findings from the (subsequently broadened) static check.
4. A scope check that exists but isn't called — **did not happen**; all 12 tools confirmed to call `require_scope`.
5. Self-graded review — **did not happen**; independent agent, no memory of implementation choices, found a real BLOCKER a self-review would very plausibly have missed (the exact item above: `confirm: bool` reading as correct on inspection while silently accepting coerced values).
6. **Not anticipated by this list, found anyway**: a raw, unmapped `sqlite3.IntegrityError` leaking SQL and submitted content when `project_id` pointed at a nonexistent project. `01_SPEC.md`/`06_API.md` had always *said* this should be a clean not-found error, but nothing enforced it until the Agentic Review's adversarial probing found the gap. Worth remembering for Milestone 3/4: documented intent in a spec is not the same as an enforced guarantee.

---

## Milestone 3 — Search, Context & Knowledge Graph (complete, checkpointed, committed — historical record, do not re-execute)

### Mission

Add the retrieval and knowledge-graph tools — `forge_search`, `forge_context`, `forge_link_items`, `forge_unlink_items` — reusing `notes_service`/`documents_service`'s existing FTS5 search functions and `knowledge_service`'s existing link/tag machinery exactly as the REST API already does. This is the first milestone where Claude can *retrieve* Forge's knowledge as a composed, topic-driven aggregate (`forge_context`) rather than one item at a time, and the first where the MCP surface can shape the knowledge graph directly (`forge_link_items`/`forge_unlink_items`). Full contract: `06_API.md` §1 (`forge_search`/`forge_context`), §3 (knowledge graph tools), `01_SPEC.md` §5.1–§5.2, `09_IMPLEMENTATION_TASKS.md`'s Milestone 3 table (M3-T0a through M3-T5).

### Read order for a session working this milestone

1. [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md)
2. **This document**, in full — including Milestones 1 and 2's historical record above, since Milestone 3 builds directly on `app/mcp/auth.py`'s `require_scope`, `_common.py`'s `tool_session`/`current_scope`/`validate_project_id`, and the `MCP → service → model` pattern both prior milestones established
3. [`CURRENT_STATE.md`](CURRENT_STATE.md)
4. [`01_SPEC.md`](01_SPEC.md) §5.1 (`forge_search` — why it calls the two FTS functions directly, never `global_search`), §5.2 (`forge_context` — the corrected project-scoping and batch-link-retrieval design, both owner-review corrections)
5. [`03_BACKEND.md`](03_BACKEND.md) §2 (service-layer reuse map) and §2.1 (`list_links_for_items`'s exact contract)
6. [`06_API.md`](06_API.md) §1 (`forge_search`/`forge_context`) and §3 (`forge_link_items`/`forge_unlink_items`) in full — every tool's exact input/output/error contract
7. [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) — Milestone 3's task table and gate criteria
8. [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §3 (Search & context ACs: AC11–AC13b) and the AC10/AC20 carry-forward checks
9. [`VERIFICATION_CONTRACT.md`](VERIFICATION_CONTRACT.md) before declaring the milestone done

### Execution Rules

- [x] **Scope is locked to `09_IMPLEMENTATION_TASKS.md`'s Milestone 3 table.** M3-T0a through M3-T5. No memory-capture tools (`forge_capture_session`/`forge_capture_decision`, Milestone 4), no resource exposure (`forge://projects`, Milestone 4), no changes to `app/mcp/auth.py` or the Milestone 2 CRUD tool files (`notes.py`/`documents.py`) — confirmed via `git diff --stat` showing those files untouched.
- [x] **`project_id` is applied inside the FTS query itself, before `LIMIT 50` — never as a post-filter on already-retrieved rows.** This is the exact bug class `01_SPEC.md` §5.2 corrected during planning (an unscoped-then-filtered `forge_context` could silently drop relevant results for a project with >50 total matches). Verified by an adversarial regression test (`test_forge_search_project_scoping_is_query_level_not_post_filtered`) engineered so a post-filter implementation would provably return 0 results instead of the correct 30 — not just a happy-path count check.
- [x] **`forge_context`'s link lookup uses `list_links_for_items` (one batch query), never one `list_links` call per matched item.** Verified by a query-count assertion at 50+50 matched items (`test_list_links_for_items_issues_a_bounded_query_count_regardless_of_item_count`), not merely by correct output — the exact standard AC13b requires.
- [x] **`forge_search` never calls `search_service.global_search`.** It calls `notes_service.search_notes`/`documents_service.search_documents` directly, structurally excluding Secrets at the call site rather than trusting a post-hoc filter. Verified adversarially (`test_forge_search_never_returns_secret_data`) with a Secret whose name matches the query term.
- [x] **Every read/write tool calls a `services/*` function — never a raw ORM query.** AC20 static check (`test_mcp_tools_static_checks.py`, unchanged from Milestone 2, recursively scans all of `app/mcp/**` and therefore already covered these two new files without modification) — passes.
- [x] **No import of `services/secrets`, `services/crypto`, or `services/settings` anywhere under `app/mcp/tools/`.** Confirmed, same static check.
- [x] **`forge_link_items`/`forge_unlink_items` calling `knowledge_service` directly is the pre-anticipated exception, not a new violation** — `test_mcp_tools_static_checks.py`'s own comment (written during Milestone 2) already documented this as expected for Milestone 3.
- [x] **Every tool's scope check uses `require_scope`.** Confirmed per-tool by the parametrized scope-enforcement tests in both new test files.
- [x] `CURRENT_STATE.md` updated.

### Autonomy Rules

**Satisfied.** No Milestone 4 task was touched; `AuthDep`/`require_auth`/`McpBearerAuthMiddleware`/`app/mcp/auth.py` remained unmodified throughout (confirmed via `git diff --stat`, both before and after the repair cycle). `app/mcp/tools/notes.py`/`documents.py` gained tool-description additions during the repair cycle (§10 finding M2 of `VERIFICATION_CONTRACT.md`) — a description-string-only change, not a Milestone-2-scope logic change, and independently confirmed as such by the Agentic Review's re-verification pass. The milestone was not declared complete — and checkpoint/commit still has not happened — until the independent Agentic Review returned a final verdict, matching Milestones 1 and 2's exact precedent.

### Quality Gates — all satisfied, PASS

1. [x] Every M3-T0a..T5 task complete.
2. [x] Full mechanical verification contract green — 6/6 applicable verifiers (Specification, Architecture, Build, Test, Regression, Code Quality, Documentation; UX not applicable).
3. [x] Independent Agentic Review — **PASS** (after one repair cycle; see [`reviews/AGENTIC_REVIEW_M3.md`](reviews/AGENTIC_REVIEW_M3.md)). First pass found zero BLOCKER, three MAJOR, three MINOR; all six fixed and independently re-verified by the same reviewer via fresh reproduction of the original failing scenarios, not by trusting the fix descriptions.
4. [x] Repair cycle stayed within Milestone 3 scope — confirmed by the reviewer's own file-scope check (`git diff --stat` matched `VERIFICATION_CONTRACT.md` §4's declared scope both before and after the repair cycle; the only files touched beyond the original plan were `notes.py`/`documents.py` gaining tool descriptions, itself a repair-cycle finding, not smuggled-in Milestone 4 work).
5. [x] Checkpointed at [`../../history/2026-08-19-phase-11-milestone-3-checkpoint.md`](../../history/2026-08-19-phase-11-milestone-3-checkpoint.md), committed. Did not release, merge, tag, or freeze. Did not begin Milestone 4 — the owner's instruction was explicit that it stays unauthorized until they open it themselves.

### The specific ways this milestone could go wrong (for reference — tracked against the actual implementation)

1. The project-scoping-is-a-post-filter bug, reintroduced — **did not happen**; verified by the adversarial AC13a test, engineered to fail deterministically against a naive implementation rather than relying on tie-break luck.
2. The `forge_context` N+1 link-lookup pattern, reintroduced — **did not happen**; verified by the AC13b query-count assertion.
3. `forge_search` reachable to Secrets via `global_search` or an equivalent shortcut — **did not happen**; the tool imports only `notes_service`/`documents_service`, confirmed by both the static import-boundary check and the adversarial secret-name test.
4. An ORM bypass "just this once" in the two new tool modules — **did not happen**; zero findings from the (unchanged, already-recursive) static check.
5. Duplicated business logic instead of service-layer reuse (e.g., reimplementing tag lookup or project-output-shaping inside `search.py`) — **did not happen**; both were promoted from private to public helpers in their owning modules and reused, not copied.
6. **Found during implementation, not anticipated by this list**: `06_API.md`'s `forge_link_items` idempotency claim didn't match `create_link`'s real behavior (raises 409 rather than returning the existing link on a duplicate). Caught by re-reading the actual service code before writing the tool handler, not by trusting the plan's prose — the same discipline Milestone 2's Agentic Review demanded after finding the `update_note` audit-logging assumption was wrong. Fixed with an explicit catch-and-translate at the tool layer; documented in `06_API.md` and `VERIFICATION_CONTRACT.md` §6/§10.
7. **Self-graded review — did not happen**; the Agentic Review was run by an independently-spawned agent with no memory of implementation decisions, and it found three real MAJOR findings a self-review would very plausibly have missed (see items 8–10).
8. **Found by the Agentic Review, not anticipated by the implementing session**: knowledge-graph link create/delete (`forge_link_items`/`forge_unlink_items`) produced zero `ActivityLog` rows, and this was never documented anywhere — unlike the structurally identical `update_note`/`update_document` gap Milestone 2 had already found and documented. Fixed by documenting it as the same class of deliberate exception (not by silently adding new logging behavior, which would have changed existing REST callers' behavior too, exactly the kind of unplanned audit-design change this repo's process requires asking about first).
9. **Found by the Agentic Review**: all 16 MCP tools (12 from Milestone 2, 4 new) had empty `tools/list` descriptions, including a direct violation of an already-written `06_API.md` requirement (`forge_create_document`'s HTML-not-Markdown warning, specified but never surfaced). Fixed across all five tool modules; verified via a live probe, not just reading the source.
10. **Found by the Agentic Review**: `forge_context`'s `links` field could reference items outside its own matched `notes`/`documents` set — a dangling ID with no accompanying context in the same response, diverging from `01_SPEC.md` §5.2's literal wording. Fixed by filtering to intra-matched-set edges only; the reviewer independently reproduced the exact original failing scenario and confirmed it no longer reproduces.
11. **Silently narrowing a repair cycle's own findings into "good enough" without re-verification — did not happen**; the reviewer's second pass caught that `VERIFICATION_CONTRACT.md` itself still contained a stale, inaccurate claim about AC18 mid-repair-cycle, and that was corrected before the final PASS was recorded rather than being waved through.

---

## Milestone 4 — Claude Memory Workflows (complete, checkpointed, committed — historical record, do not re-execute)

### Mission

Add `forge_capture_decision`/`forge_capture_session` (thin wrappers over `forge_create_note`'s own underlying service call, plus a reserved-tag convention — not a new persistence mechanism) and expose two resources, `forge://projects`/`forge://projects/{id}`, for cheap client-side orientation. This is the first milestone where something Claude writes to Forge is framed as *memory for a future Claude session* rather than *knowledge the user asked for* — and the milestone that proves that framing actually works end to end via a genuine cross-session continuity test (AC14). Full contract: `06_API.md` §4 (memory tools), §5 (resources), `01_SPEC.md` §9, `09_IMPLEMENTATION_TASKS.md`'s Milestone 4 table (M4-T1 through M4-T5).

### Read order for a session working this milestone

1. [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md)
2. **This document**, in full — including Milestones 1–3's historical record above, since Milestone 4 builds directly on `app/mcp/auth.py`'s `require_scope`, `_common.py`'s `tool_session`/`current_scope`/`validate_project_id`, and the `MCP → service → model` pattern every prior milestone established
3. [`CURRENT_STATE.md`](CURRENT_STATE.md)
4. [`01_SPEC.md`](01_SPEC.md) §9 (session/decision capture — why this is Notes-plus-tags, not a new memory database)
5. [`06_API.md`](06_API.md) §4 (`forge_capture_decision`/`forge_capture_session`) and §5 (resources) in full
6. [`09_IMPLEMENTATION_TASKS.md`](09_IMPLEMENTATION_TASKS.md) — Milestone 4's task table and gate criteria
7. [`08_ACCEPTANCE.md`](08_ACCEPTANCE.md) §4 (AC14, AC15) and the AC10/AC20 carry-forward checks
8. [`VERIFICATION_CONTRACT.md`](VERIFICATION_CONTRACT.md) before declaring the milestone done

### Execution Rules

- [x] **Scope is locked to `09_IMPLEMENTATION_TASKS.md`'s Milestone 4 table.** M4-T1 through M4-T5. No Milestone 5 work (token-management UI, full authz matrix, production hardening) — confirmed by `git diff --stat` touching only `app/mcp/tools/memory.py` (new), `app/mcp/resources.py` (new), `app/mcp/server.py` (registration), three new test files, `docs/MCP_Usage.md` (new), one corrected sentence in `docs/Deployment.md`, and `forge-docs/`.
- [x] **`forge_capture_decision`/`forge_capture_session` call `notes_service.create_note`/`knowledge_service.add_tag` — never a new persistence path.** No new table, model, or Alembic migration (`01_SPEC.md` §9's explicit "no new memory database" instruction).
- [x] **Every read/write tool and resource calls a `services/*` function — never a raw ORM query.** AC20 static check (`test_mcp_tools_static_checks.py`, unchanged, recursively scans all of `app/mcp/**` and therefore already covered `memory.py`/`resources.py` without modification) — passes.
- [x] **No import of `services/secrets`, `services/crypto`, or `services/settings` anywhere under `app/mcp/`.** Confirmed, same static check.
- [x] **`forge_capture_decision`/`forge_capture_session`'s scope check uses `require_scope`.** Confirmed by the parametrized scope-enforcement tests in `test_mcp_tools_memory.py`.
- [x] **AC14 is proven with a genuinely independent second session** — a fresh persistent token AND a fresh `initialize` handshake, not a second call reusing the writer's connection (`test_mcp_memory_continuity.py`).
- [x] **A real SDK constraint discovered during implementation is documented, not silently built around or silently violated**: `forge://projects` (the static resource) cannot enforce `forge:read` scope the way `forge://projects/{id}` (a template resource) and every tool do — this MCP SDK version has no per-request context hook for a static resource's read function. Full detail in `VERIFICATION_CONTRACT.md` §6 and `app/mcp/resources.py`'s module docstring; flagged explicitly for the Agentic Review's independent judgment rather than resolved unilaterally.
- [x] `CURRENT_STATE.md` updated.

### Autonomy Rules

**Satisfied.** No Milestone 5 task was touched; `AuthDep`/`require_auth`/`McpBearerAuthMiddleware`/`app/mcp/auth.py` and every Milestone 1–3 tool module remained unmodified throughout (confirmed via `git diff --stat`, both before and after the repair cycle). The repair cycle touched exactly one file (`06_API.md`, a documentation correction) — independently confirmed by the same reviewer as staying within Milestone 4 scope, no Milestone 5 work smuggled in. The milestone was not declared complete until the independent Agentic Review returned PASS (after one repair cycle addressing a real MAJOR finding).

### Quality Gates — all satisfied, PASS

1. [x] Every M4-T1..T5 task complete.
2. [x] Full mechanical verification contract green — 7/7 applicable verifiers (Specification, Architecture, Build, Test, Regression, Code Quality, Documentation; UX not applicable). Backend suite 395/395; FDK suite 103/113 with all 10 failures pre-existing/environment-specific (see `VERIFICATION_CONTRACT.md` §5); Docker build succeeded.
3. [x] Independent Agentic Review — **PASS** (after one repair cycle; see [`reviews/AGENTIC_REVIEW_M4.md`](reviews/AGENTIC_REVIEW_M4.md)). First pass found zero BLOCKER, one MAJOR, one MINOR; the MAJOR fixed and independently re-verified by the same reviewer via fresh reproduction (re-reading the actual diff, re-running the backend suite), not by trusting the fix description; the MINOR correctly left as backlog per the reviewer's own explicit non-blocking classification.
4. [x] Repair cycle stayed within Milestone 4 scope — confirmed by the reviewer's own file-scope check (`git status --porcelain`/`git diff --stat` showed exactly one file changed beyond the review's original baseline: `06_API.md`).
5. [x] Checkpointed at [`../../history/2026-08-19-phase-11-milestone-4-checkpoint.md`](../../history/2026-08-19-phase-11-milestone-4-checkpoint.md), committed. Did not release, merge, tag, or freeze. Did not begin Milestone 5 — that remains a separate, future, explicit act.

### The specific ways this milestone could go wrong (for reference — tracked against the actual implementation)

1. Treating "thin wrapper over forge_create_note" as license to skip `require_scope`/`validate_project_id` since "it's just a note" — **did not happen**; `_capture()` in `memory.py` runs the identical scope-check-then-validate-then-service-call sequence every other write tool does.
2. Building a parallel retrieval mechanism for captured memory instead of relying on `forge_search`/`forge_context` finding it naturally — **did not happen**; no new query function, no new tool searches only `ai-decision`/`ai-session`-tagged notes. `test_forge_capture_decision_and_session_are_found_by_forge_search` and both `test_mcp_memory_continuity.py` tests prove the ordinary path already works; the Agentic Review independently reproduced this with an even stronger probe (a second, independently-rebuilt app/engine instance) and it still held.
3. Silently building a workaround for the `forge://projects` static-resource scope-enforcement SDK limitation that technically "passes" but doesn't actually enforce anything (e.g. checking a header that isn't really there, or claiming scope enforcement in a docstring without a matching implementation) — **did not happen**; the limitation is documented as a limitation, with the actual (weaker) security property stated plainly and a test suite that doesn't claim more than what's true.
4. Trusting `06_API.md`'s "Full NoteOut... including the applied tag" output claim without checking `NoteOut`'s real fields — **did not happen**; caught by reading `schemas/notes.py` before writing the tool handler, same discipline Milestone 2/3's Agentic Review had to enforce after the fact for other findings. Independently confirmed correct by the Agentic Review.
5. Self-graded review — **did not happen**; the Agentic Review was run by an independently-spawned agent with no memory of implementation decisions, and it found a real MAJOR finding (the `06_API.md` contract-accuracy gap) a self-review would very plausibly have missed, since three other documents describing the same limitation had already been corrected.
6. **Not anticipated by this list, found anyway**: `06_API.md` §5's resource contract table stated `forge:read` was enforced on `forge://projects` when it structurally cannot be — a real contract-vs-implementation mismatch, exactly the "contract inconsistencies" failure class `09_IMPLEMENTATION_TASKS.md` §0 names. Worth remembering for Milestone 5: when a limitation is discovered mid-implementation and documented in several places, checking that *every* relevant document was updated (not just the ones touched while writing the fix) needs to be a deliberate step, not assumed.

---

## Cross-references

- [README.md](README.md) · [01_SPEC.md](01_SPEC.md) · [03_BACKEND.md](03_BACKEND.md) · [06_API.md](06_API.md) · [08_ACCEPTANCE.md](08_ACCEPTANCE.md) · [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md) · [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md) · [CURRENT_STATE.md](CURRENT_STATE.md)
- [../../decisions/0018-mcp-server-integrated-not-separate-process.md](../../decisions/0018-mcp-server-integrated-not-separate-process.md)
- [../../decisions/0019-mcp-bearer-token-authentication.md](../../decisions/0019-mcp-bearer-token-authentication.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md) · [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md) · [../../13_PHASE_LIFECYCLE.md](../../13_PHASE_LIFECYCLE.md) · [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md)
