# Phase 11 — Implementation Task Breakdown

> **Purpose:** Ordered, granular, independently-verifiable tasks, milestone by milestone, each with an automated Agentic Review gate.
> **Status:** Draft — pending Authorization. **No task below has been started.**
> **Last Updated:** 2026-08-18

---

## 0. How the Agentic Review gate works (read this before Milestone 1)

`tools/fdk_verification/` today has **no agentic/LLM review verifier** — every existing verifier (`Specification`, `Architecture`, `Build`, `Test`, `Regression`, `Code Quality`, `Documentation`, `UX`) is mechanical: git diff/status, checkbox parsing, shell exit codes, regex marker scans (confirmed by direct inspection of `tools/fdk_verification/verifiers/*.py`). `RepairLoop`'s `on_remediation` hook and the framework's own `15_VERIFICATION_FRAMEWORK.md` §10 both explicitly flag "an orchestrating skill/command that launches subagents via Agent/Workflow" as **not yet built** — this is a real, named gap, not an oversight in this plan.

**Smallest viable extension (this is what Milestone 1 Task M1-T7 builds):**

1. A new verifier module, `tools/fdk_verification/verifiers/agentic_review.py`, implementing the existing `Verifier` Protocol (`name: str`, `run(contract, workspace_root) -> VerifierResult`) — no change to `Orchestrator`/`ReferenceOrchestrator`/`pipeline.py`, which are already generic over whatever is in the verifier registry (`verifiers/__init__.py`'s `default_registry()`).
2. `AgenticReview.run()` invokes a Claude Code subagent (via this session's own `Agent`/`Workflow` tool access — the same mechanism a Claude Code session already has, not a new external dependency) with a prompt built from: the milestone's spec sections, the task list, the actual `git diff` for this milestone, and prior milestones' findings. The subagent is instructed to look for exactly the failure classes listed in the planning brief §18 (technically-implemented-but-wrong requirements, missing edge cases, security bypasses, scope expansion, duplicated logic, contract inconsistencies, authorization gaps, regressions, undocumented behavior, test gaps, architectural drift) and to return a structured verdict.
3. The verdict is mapped to `VerifierResult(name="Agentic Review", status=PASS|FAIL, findings=[...])` — `PASS WITH REQUIRED FIXES` (per the brief's §Milestone-1 gate wording) is represented as `FAIL` with findings listed as required fixes, since the underlying framework's `build_report` only recognizes binary PASS/FAIL at the report level (confirmed — no `PASS_WITH_FIXES` status exists in `report.py`). This is a **documented mapping**, not a silent narrowing of the brief's three-way outcome — "PASS WITH REQUIRED FIXES" is communicated in the rendered findings/recommendations text even though the machine-readable status is binary.
4. `"Agentic Review"` is added to `contract.CANONICAL_VERIFIERS` and to each milestone's `VERIFICATION_CONTRACT.md` §9 (Required Verification Agents).
5. This verifier is declared **required** in every milestone's contract, alongside whichever of the 8 existing verifiers are applicable (Build/Test only if `§5 Required Validation Commands` declares real commands; UX is always `NOT_APPLICABLE` for this backend-only phase per the existing stub's own documented behavior — declaring it is harmless but it will never gate anything, which should be stated explicitly in each contract rather than silently omitted).

**This is the smallest extension, not a parallel framework** — it reuses `Orchestrator`, `contract.py`'s parsing/validation, `report.py`'s rendering, and `pipeline.persist_reports`'s history-archiving, exactly as-is. Only one new verifier module is added.

## Milestone 1 — MCP Foundation

**Scope:** prove exactly this narrow vertical slice, per owner review — no Notes/Documents/Projects CRUD tools yet:

```text
Claude
  ↓
Streamable HTTP
  ↓
nginx
  ↓
FastAPI /mcp
  ↓
Bearer authentication (persistent token, provisioned via bootstrap — never the bootstrap token itself)
  ↓
scope enforcement
  ↓
MCP handshake/tool discovery (zero content tools registered — an empty, correctly-shaped tool list)
  ↓
Forge
```

This is deliberately the smallest possible end-to-end proof: a human provisions a real credential (via the bootstrap flow), Claude connects with it through the full transport/proxy/auth stack, and the MCP handshake succeeds — with zero opportunity for a CRUD-tool bug to mask a foundational transport/auth problem. Milestone 2 is not authorized to start until this slice is proven, per the Agentic Review gate below.

| ID | Objective | Files | Depends on | Tests | Docs |
|---|---|---|---|---|---|
| M1-T1 | New ADRs: MCP-in-process decision, MCP auth-scheme decision (`01_SPEC.md` §1, §4, §7) | `decisions/00XX-*.md` (×2) | — | — | ADRs themselves |
| M1-T2 | `McpToken` model + migration + `activity_log.source` column | `models/mcp_token.py`, `models/__init__.py`, `alembic/versions/00XX_mcp_tokens.py` | M1-T1 | Migration up/down/up test | `04_DATABASE.md` (already drafted) |
| M1-T3 | Config additions (`mcp_enabled`, `mcp_bootstrap_enabled`, `mcp_bootstrap_token[_file]`) | `core/config.py` | — | Config unit test | `03_BACKEND.md` (already drafted) |
| M1-T4 | `services/mcp/tokens.py` — issue/verify/revoke/list/touch_last_used (throttled — §4.3 of `01_SPEC.md`) | `services/mcp/tokens.py` | M1-T2, M1-T3 | Unit tests §1 of `07_TESTING.md`, incl. the throttling test (AC4a) | — |
| M1-T4a | `POST/GET/DELETE /api/mcp/tokens` — provisioning route, `require_bootstrap_auth` (bootstrap-only, never accepted by `/mcp`) + `AuthDep` (cookie) alternative | `app/api/routes/mcp_tokens.py`, `app/mcp/auth.py` (`require_bootstrap_auth`) | M1-T4 | AC1a, AC1b, AC1c | `01_SPEC.md` §4.3.1 (already drafted) |
| M1-T5 | `app/mcp/auth.py` — `require_mcp_auth`, `require_scope` (persistent tokens only — no bootstrap fallback in this dependency, ever) | `app/mcp/auth.py` | M1-T4a | Unit + security tests §1/§3, incl. AC1a | — |
| M1-T6 | MCP server bootstrap — mount Streamable HTTP app at `/mcp`, gated by `mcp_enabled`; health/handshake only, zero tools registered yet | `app/mcp/server.py`, `main.py` | M1-T5 | MCP contract smoke test (connect with a provisioned persistent token + empty tool list) §5 of `07_TESTING.md` | — |
| M1-T7 | New `Agentic Review` verifier + contract-format update | `tools/fdk_verification/verifiers/agentic_review.py`, `verifiers/__init__.py`, `contract.py` (`CANONICAL_VERIFIERS`), `implementation/VERIFICATION_CONTRACT_TEMPLATE.md` | — (independent of M1-T1..T6) | `tools/tests/` addition proving the new verifier satisfies the `Verifier` Protocol and integrates with `Orchestrator` | `15_VERIFICATION_FRAMEWORK.md` update noting the new verifier |
| M1-T8 | `docker/nginx.conf` `/mcp` location block, `docker-compose.yml` env additions | `docker/nginx.conf`, `docker-compose.yml` | M1-T6 | Deployment tests §6 of `07_TESTING.md` | `docs/Deployment.md` (incl. "disable bootstrap after first provisioning" operational note) |
| M1-T9 | `VERIFICATION_CONTRACT.md` for Milestone 1, filled in (not template placeholders) | `VERIFICATION_CONTRACT.md` | M1-T1..T8 | — | contract itself |

**Gate — Agentic Review (Milestone 1):** independently inspects architecture (does `/mcp` genuinely share the FastAPI process and services, per `01_SPEC.md` §1, rather than quietly becoming a separate process?), security (is `require_mcp_auth` unreachable without a valid, non-revoked, *persistent* token — specifically confirming the bootstrap token is rejected by every `/mcp` route, not just untested; is `AuthDep`/`require_auth` provably untouched?), MCP protocol correctness (does the handshake conform to Streamable HTTP per the researched spec?), transport, Docker, regressions (existing test suite still green), documentation. **Pass/fail:** PASS only if every AC-equivalent check above is met with no BLOCKER-class finding (per `12_BUG_CLASSIFICATION.md`); PASS WITH REQUIRED FIXES if only MAJOR/MINOR findings remain (fixes applied, re-verified, before Milestone 2 starts); FAIL returns to M1-T1..T9 for rework.

## Milestone 2 — Knowledge CRUD

**Scope:** `forge_get/create/update/delete_note`, same for documents, `forge_list/get/create/update_project`.

| ID | Objective | Files | Depends on | Tests | Docs |
|---|---|---|---|---|---|
| M2-T0 | `source: str = "ui"` parameter added to `notes_service`/`documents_service`/`projects_service`'s create/update/delete functions, threaded into each function's existing internal `activity.record(...)` call | `services/notes/service.py`, `services/documents/service.py`, `services/projects/service.py` | M1 gate PASS | Regression test confirming every existing (non-MCP) caller is unaffected by the new default; unit test confirming `source="mcp"` reaches the logged row | `01_SPEC.md` §4.5 (already drafted) |
| M2-T1 | `notes_service.get_note` addition (parity with Documents) — **required**, no ORM-bypass alternative permitted in any tool handler | `services/notes/service.py` | M1 gate PASS | Unit test + AC20 static check | `06_API.md` (already drafted) |
| M2-T2 | `app/mcp/tools/notes.py` — 4 tools. `forge_delete_note` implements the corrected 3-step sequence: `get_note` (existence check, no mutation) → `purge_links_for` (staged, no commit) → `delete_note(..., source="mcp")` (stages + commits both atomically) | `app/mcp/tools/notes.py` | M2-T0, M2-T1 | Integration tests incl. the orphan-link regression guard AND the existence-check-first guard (AC7a) (`07_TESTING.md` §2) | — |
| M2-T3 | `app/mcp/tools/documents.py` — 4 tools, identical corrected delete sequence against `documents_service` | `app/mcp/tools/documents.py` | M2-T0 | Same pattern, incl. AC7a | — |
| M2-T4 | `app/mcp/tools/projects.py` — 4 tools (list/get/create/update, no delete), `source="mcp"` threaded on create/update | `app/mcp/tools/projects.py` | M2-T0 | Integration tests | — |
| M2-T5 | Tool registry wiring — register all 12 tools with `server.py`, scope-gate each per `01_SPEC.md` §4.4's table | `app/mcp/tools/__init__.py`, `server.py` | M2-T2..T4 | MCP contract tests §5 | — |
| M2-T6 | `VERIFICATION_CONTRACT.md` update for Milestone 2 | `VERIFICATION_CONTRACT.md` | M2-T1..T5 | — | — |

**Gate — Agentic Review (Milestone 2):** tool contracts match `06_API.md` exactly (name/schema/scope drift check), CRUD correctness against real data, service-layer reuse (no duplicated business logic — spot-check that tool handlers call services, not raw SQL/ORM per AC20), authorization (scope table enforced per-tool, not just per-connection), data integrity (the orphan-link regression test AND the existence-check-first guard both exist and pass — AC7/AC7a), audit correctness (exactly one `ActivityLog` row per mutation, not two — AC18), error semantics match `06_API.md`, regressions.

## Milestone 3 — Search, Context & Knowledge Graph

**Scope:** `forge_search`, `forge_context`, `forge_link_items`, `forge_unlink_items`.

| ID | Objective | Files | Depends on | Tests | Docs |
|---|---|---|---|---|---|
| M3-T0a | `project_id: str | None = None` param added to `notes_service.search_notes`/`documents_service.search_documents`, applied inside the FTS query before `LIMIT 50` | `services/notes/service.py`, `services/documents/service.py` | M1 gate PASS | AC13a — assert project-scoped results are complete, not post-filtered-and-truncated | `01_SPEC.md` §5.2 (already drafted) |
| M3-T0b | `knowledge_service.list_links_for_items(session, items)` — batch link retrieval, one query for a whole result set | `services/knowledge/service.py` | M1 gate PASS | AC13b — query-count assertion at 50+50 matched items | `03_BACKEND.md` §2.1 (already drafted) |
| M3-T1 | `app/mcp/tools/search.py` — `forge_search` (calls the two FTS functions directly, never `global_search`; passes `project_id` through per M3-T0a) | `app/mcp/tools/search.py` | M3-T0a | AC12 test — assert no Secret data in output even with a crafted query matching a real secret's name | — |
| M3-T2 | `forge_context` composition — uses `list_links_for_items` (M3-T0b), not one `list_links` call per matched item | `app/mcp/tools/search.py` | M3-T0a, M3-T0b, M2 gate PASS (needs project/knowledge tools' underlying services proven) | AC11, AC13, AC13a, AC13b tests | — |
| M3-T3 | `app/mcp/tools/knowledge.py` — `forge_link_items`, `forge_unlink_items` | `app/mcp/tools/knowledge.py` | M2 gate PASS | Relink-normalization test (`07_TESTING.md` §2) | — |
| M3-T4 | Tool registry wiring for the 4 new tools | `app/mcp/tools/__init__.py` | M3-T1..T3 | Contract tests | — |
| M3-T5 | `VERIFICATION_CONTRACT.md` update for Milestone 3 | `VERIFICATION_CONTRACT.md` | M3-T1..T4 | — | — |

**Gate — Agentic Review (Milestone 3):** retrieval correctness (does `forge_context`'s output actually match what the cited services would independently return for the same input?), ranking (confirms no undocumented custom scoring was introduced beyond FTS5's own `rank`), context quality, performance (no N+1 query explosion in `forge_context`'s per-result tag/link lookups — spot-check query count), authorization, **information leakage** (this is the gate that must independently re-verify AC10/AC12 — zero Secret data reachable, checked adversarially, not just by re-running the same test the implementer wrote), relationship traversal correctness, search regressions, tool ergonomics (are tool descriptions clear enough for an LLM caller, per the brief's semantic-not-mechanical framing?).

## Milestone 4 — Claude Memory Workflows

**Scope:** `forge_capture_session`, `forge_capture_decision`, resource exposure, multi-session continuity proof.

| ID | Objective | Files | Depends on | Tests | Docs |
|---|---|---|---|---|---|
| M4-T1 | `app/mcp/tools/memory.py` — 2 tools, reserved-tag convention | `app/mcp/tools/memory.py` | M2 gate PASS (needs `forge_create_note` + tagging proven) | Unit + integration | `01_SPEC.md` §9 (already drafted) |
| M4-T2 | `app/mcp/resources.py` — `forge://projects`, `forge://projects/{id}` | `app/mcp/resources.py` | M2 gate PASS | Contract tests §5 | `06_API.md` §5 (already drafted) |
| M4-T3 | Cross-session continuity test (AC14) — write in one simulated MCP session/connection, read in a second, independent one | `backend/tests/test_mcp_memory_continuity.py` | M4-T1, M3 gate PASS | AC14 itself | — |
| M4-T4 | Claude-oriented usage documentation — how a Claude session should use `forge_context`/`forge_capture_decision` together, worked example | `docs/MCP_Usage.md` (new) | M4-T1..T3 | — | new doc |
| M4-T5 | `VERIFICATION_CONTRACT.md` update for Milestone 4 | `VERIFICATION_CONTRACT.md` | M4-T1..T4 | — | — |

**Gate — Agentic Review (Milestone 4):** persistence correctness, cross-session context retrieval (re-runs AC14 independently), duplicate-data behavior (does repeated capture of similar decisions create sprawl with no dedup story — flag as a finding if so, not necessarily a blocker), auditability, security (still no Secrets path), usability from Claude's perspective (are the two memory tools' descriptions unambiguous about when to use which), prompt/resource design, regressions.

## Milestone 5 — Production Hardening & Release

**Scope:** token lifecycle, full authorization matrix, audit completeness, Docker production wiring, full regression + security suite, release artifacts.

| ID | Objective | Files | Depends on | Tests | Docs |
|---|---|---|---|---|---|
| M5-T1 | Resolve the token-management-UI open question (`08_ACCEPTANCE.md` §6) with the owner; implement whichever is chosen | `services/mcp/tokens.py` extension + (UI or CLI script) | Owner decision | New tests per chosen path | `docs/Security.md` update |
| M5-T2 | Full authorization matrix test — every tool × every scope combination × valid/invalid/revoked token | `backend/tests/test_mcp_authz_matrix.py` | M2, M3, M4 gates PASS | AC1-AC5, AC19 exhaustively | — |
| M5-T3 | Audit completeness pass — every write/delete tool confirmed to log `source="mcp"`; confirm reads' logging decision from `08_ACCEPTANCE.md` §6 is implemented consistently | `app/mcp/tools/*.py` (verification, likely no new code if M2-M4 followed the pattern) | M1-T2 | AC18 | — |
| M5-T4 | Full regression + security suite run against the complete phase | — | M5-T1..T3 | All of `07_TESTING.md` | — |
| M5-T5 | `docker/nginx.conf`/`docker-compose.yml` production-path verification (actual `docker compose up --build`, not just unit tests) | — | M1-T8 | Deployment tests §6 | `docs/Deployment.md` |
| M5-T6 | Release artifacts: `10_RELEASE_NOTES.md`, final `CURRENT_STATE.md`, `VERIFICATION_CONTRACT.md` closed out | `10_RELEASE_NOTES.md`, `CURRENT_STATE.md` | M5-T1..T5 | — | release docs |

**Gate — Agentic Review (Milestone 5, final RC audit):** the full-phase audit per the brief's §16 Milestone 5 list — security review, token lifecycle, authorization matrix, destructive operations, audit logging, Docker deployment, documentation completeness, integration tests, regression suite, performance, observability, release artifacts. Produces an explicit release recommendation (PASS / PASS WITH REQUIRED FIXES / FAIL) per §0's mapping.

## The mandatory human review gate (after Milestone 5's PASS)

Per the planning brief §17 — **not automatable, not skippable, and this planning session does not attempt to satisfy it in advance.** The project owner must review, at minimum:

- [ ] MCP architecture (Option A decision and its trade-off, §1 of `01_SPEC.md`)
- [ ] Authentication model (bearer-token scheme, §4.1-4.3)
- [ ] Authorization/scopes (the scope table, §4.4, and whether `forge:secrets` should remain permanently unimplemented or ever be built)
- [ ] Tool surface (`06_API.md` in full — is anything missing that should exist, or present that shouldn't?)
- [ ] Data exposure (confirm the Secrets/Settings/Crypto exclusion is acceptable, and remains acceptable if the owner's usage patterns differ from what this planning session assumed)
- [ ] Destructive operations (`01_SPEC.md` §6 — is `confirm: true` sufficient, or does the owner want soft-delete added as a real Notes/Documents feature change in a future phase?)
- [ ] Claude workflow (`docs/MCP_Usage.md` from M4-T4 — does it actually reflect how the owner wants to use this?)
- [ ] Deployment model (§5 of `03_BACKEND.md` — is exposing `/mcp` through the same reverse proxy as the rest of Forge acceptable given the owner's actual network topology?)
- [ ] Final automated review report (Milestone 5's Agentic RC Review output, in full, not just its PASS/FAIL headline)
- [ ] Acceptance criteria (`08_ACCEPTANCE.md`, all of them, individually)

Only after explicit human approval does this phase proceed to Forge's normal Release/Freeze workflow (tag, merge, roadmap update, archive to `history/Phase-11/`) — per `09_CLAUDE_CODE_RULES.md` §3/§7 and `13_PHASE_LIFECYCLE.md`, no automated process in this repository is authorized to perform that step on its own, regardless of how many Agentic Review gates passed.

## Cross-references

- [01_SPEC.md](01_SPEC.md)
- [06_API.md](06_API.md)
- [07_TESTING.md](07_TESTING.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md)
- [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md)
- [../../12_BUG_CLASSIFICATION.md](../../12_BUG_CLASSIFICATION.md)
