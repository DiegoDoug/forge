# Claude MCP / Second Brain — IMPLEMENT

> **Purpose:** The execution contract for this phase — a Claude Code session must read this in full before writing any code for this phase.
> **Scope:** This phase only. Inherits from, and never overrides, the repo-wide rules in [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md).
> **Ownership:** Project owner.
> **Status:** ✅ **Milestone 2 (Knowledge CRUD) checkpointed and committed — 2026-08-18. Milestone 3 NOT authorized.**
>
> Six gates recorded, in order, as separate, explicit acts — none implies the next, exactly as the planning package's own §17 required and as Phase 09's precedent established:
>
> 1. **Architecture direction approved (2026-08-18)** — the owner reviewed the full planning package (`01_SPEC.md` through `09_IMPLEMENTATION_TASKS.md`) and approved the architecture direction (Option A: in-process MCP server; bearer-token auth model), after requesting and receiving six amendments (bootstrap-token/persistent-token lifecycle, transactional/existence-checked delete, `forge_context` N+1 and project-scoping fixes, activity-log dedup, mandatory `get_note` service method — see `CURRENT_STATE.md` §4 for the full list).
> 2. **Milestone 1 implementation authorized (2026-08-18)** — granted explicitly, scoped to Milestone 1 **only**. The owner's own words: *"I would authorize Milestone 1 only. ... Then the new Agentic Review verifier gets its first real test."*
> 3. **Milestone 1 checkpointed, PASS (2026-08-18)** — mechanical verification 8/8, Agentic Review PASS after one repair cycle (a real BLOCKER found and fixed — see [`reviews/AGENTIC_REVIEW_M1.md`](reviews/AGENTIC_REVIEW_M1.md)). Full record: [`../../history/2026-08-18-phase-11-milestone-1-checkpoint.md`](../../history/2026-08-18-phase-11-milestone-1-checkpoint.md), committed at `6854971`.
> 4. **Milestone 2 authorized (2026-08-18)** — the owner's own words, as a direct instruction following the M1 checkpoint: *"Commit the M1 checkpoint work. M2 authorized."* Granted as its own act, not inferred from the M1 PASS — matching the boundary gate 3 established.
> 5. **Milestone 2 gate PASS (2026-08-18)** — mechanical verification 8/8, Agentic Review PASS after one repair cycle. The repair cycle was substantive: a real BLOCKER (a boolean-coercion bypass letting `confirm: "true"`/`1`/etc. authorize a permanent delete the same as literal `true`) plus two MAJOR findings (a raw DB exception leak on a bad `project_id`; an output-shape documentation ambiguity) — see [`reviews/AGENTIC_REVIEW_M2.md`](reviews/AGENTIC_REVIEW_M2.md).
> 6. **Milestone 2 checkpointed and committed (2026-08-18)** — the owner's own words: *"checkpoint and commit M2, then stop."* Full record: [`../../history/2026-08-18-phase-11-milestone-2-checkpoint.md`](../../history/2026-08-18-phase-11-milestone-2-checkpoint.md). **Explicitly a stopping point** — the instruction was to stop, not to proceed to Milestone 3. Nothing here authorizes Milestone 3 (M3-T1 onward); that remains a separate, future, explicit act.
>
> [ADR-0018](../../decisions/0018-mcp-server-integrated-not-separate-process.md) and [ADR-0019](../../decisions/0019-mcp-bearer-token-authentication.md) are **Accepted** as of this review.
> **Last Updated:** 2026-08-18

---

## Role

You are implementing Phase 11 — Claude MCP / Second Brain, acting as the engineer of record. You are bound by [`../../09_CLAUDE_CODE_RULES.md`](../../09_CLAUDE_CODE_RULES.md) at all times; this document adds phase-specific and milestone-specific detail only. **The active milestone is Milestone 2 — Knowledge CRUD** (§"Milestone 2" below). Milestone 1's rules are kept as historical record immediately below; do not re-execute them, and do not treat their "Autonomy Rules" as governing Milestone 2 work — Milestone 2 has its own.

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

## Cross-references

- [README.md](README.md) · [01_SPEC.md](01_SPEC.md) · [03_BACKEND.md](03_BACKEND.md) · [06_API.md](06_API.md) · [08_ACCEPTANCE.md](08_ACCEPTANCE.md) · [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md) · [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md) · [CURRENT_STATE.md](CURRENT_STATE.md)
- [../../decisions/0018-mcp-server-integrated-not-separate-process.md](../../decisions/0018-mcp-server-integrated-not-separate-process.md)
- [../../decisions/0019-mcp-bearer-token-authentication.md](../../decisions/0019-mcp-bearer-token-authentication.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md) · [../../10_CHECKPOINT_PROTOCOL.md](../../10_CHECKPOINT_PROTOCOL.md) · [../../13_PHASE_LIFECYCLE.md](../../13_PHASE_LIFECYCLE.md) · [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md)
