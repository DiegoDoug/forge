# Phase 11 — Claude MCP / Second Brain — README

> **Purpose:** Entry point for Phase 11 — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** Project owner — this entire phase requires explicit owner Authorization before implementation begins (see §3 "Before starting a phase" in `../README.md`), and explicit owner sign-off after Milestone 5's automated RC review, per §17 of the planning brief this phase was scoped from.
> **Status:** 🔒 **Released & Frozen.** Committed to `master` at `8d8ddd8`, tagged `v0.11.0`, 2026-08-20. The owner completed the mandatory human review gate item by item in chat, then granted explicit release authorization — see `IMPLEMENT.md`'s human review gate record. Per `../../13_PHASE_LIFECYCLE.md` §4, this directory now accepts bug fixes only. End-of-phase release notes moved to [`../../history/Phase-11/10_RELEASE_NOTES.md`](../../history/Phase-11/10_RELEASE_NOTES.md).
> **Last Updated:** 2026-08-20

---

## A note on process

This spec package was produced by a single planning session that inspected the repository (backend architecture, auth model, service layer, database, forge-docs conventions, and the FDK verification framework) and wrote up an implementation-ready plan in one pass, rather than through the usual incremental drafting-with-the-owner cycle used for Phases 01–09. This is closer to Phase 10's exception than to the norm — but unlike Phase 10, this phase has **not been implemented**; it is Specification-stage only, and per `../../09_CLAUDE_CODE_RULES.md` §2/§3 it may not be Authorized or started without the project owner reviewing and explicitly approving it first.

## Objective

Make Forge Claude's persistent knowledge substrate by exposing a scoped, semantic MCP (Model Context Protocol) interface over Forge's existing Notes, Documents, Projects, and Knowledge Hub capabilities — so a Claude session (today or in a future session) can search, read, create, and organize knowledge in Forge, and can capture session context/decisions so a later session can retrieve them.

MCP is an **interface to Forge's existing application capabilities, not a second implementation of Forge's business logic.** MCP tools call the same service-layer functions the REST API already calls (`backend/app/services/notes`, `documents`, `projects`, `knowledge`), reusing the same Pydantic/SQLModel schemas wherever practical.

## Scope

**In scope:**

- [x] An MCP server, mounted in-process inside the existing FastAPI backend (see `01_SPEC.md` §1 for the architecture decision and rejected alternative).
- [x] Streamable HTTP transport, reachable through the existing nginx reverse proxy alongside the REST API.
- [x] A new bearer-token authentication path, independent of the browser session cookie, with `forge:read` / `forge:write` / `forge:delete` scopes (see `01_SPEC.md` §4).
- [x] A small, semantic MCP tool surface over Notes, Documents, Projects, and Knowledge Hub linking/tagging — 18 tools total, full contract in `06_API.md`.
- [x] `forge_context`, a Claude-oriented aggregate retrieval tool built on the existing FTS5 search and Knowledge Hub query layer — no new search index, no embeddings/vector search.
- [x] Session/decision capture, implemented as ordinary Notes with a reserved tag convention — no new persistence model.
- [x] Reuse of the existing `ActivityLog` service for an MCP-originated audit trail, with an added `source` distinction.
- [x] Five implementation milestones, each gated by an independent automated review, and a mandatory human review gate after the final milestone's RC review — before any release/freeze action.

**Out of scope (see `01_SPEC.md` §2 for the full list with reasoning):**

- [x] The Secrets/vault service and anything crypto-adjacent to it (`forge:secrets` scope is *defined* but implemented by nothing in this phase) — confirmed, held for all five milestones by a recursive static import-boundary check.
- [x] Settings, backup/import/export, and master-password operations.
- [x] Embeddings or vector search — the existing SQLite FTS5 index is sufficient for this phase's retrieval needs.
- [x] A new "memory database" — session/decision capture reuses Notes.
- [x] OAuth 2.0 for MCP auth — a static, revocable bearer token fits Forge's single-tenant, self-hosted deployment model; OAuth is flagged as a possible future hardening step, not built here.
- [x] A frontend surface beyond token management — a Settings-page UI for issuing/revoking MCP tokens was built in Milestone 5 (the owner's resolution of the `01_SPEC.md` §4.6 open question); no other new frontend surface exists.

## Relationship to the shipped application

Phase 11 sits **beside** the REST API, not inside the frontend. It adds one new backend subsystem (`backend/app/mcp/`) that calls into the same `services/notes`, `services/documents`, `services/projects`, and `services/knowledge` modules the existing `api/routes/*.py` routers already call — see `03_BACKEND.md` for the exact reuse map. It introduces one new database concept (MCP access tokens) and no changes to the Notes/Documents/Projects/Knowledge data model.

Related backend: `backend/app/services/notes/`, `backend/app/services/documents/`, `backend/app/services/projects/`, `backend/app/services/knowledge/`, `backend/app/services/search/`, `backend/app/services/activity.py`, `backend/app/core/security.py`, `backend/app/api/deps.py`.

## Deliverables

- [x] `backend/app/mcp/` — server bootstrap, 5 tool modules (18 tools total), 1 resource module, MCP-specific auth dependency.
- [x] `backend/app/models/mcp_token.py` — one additive model (`McpToken`).
- [x] `backend/alembic/versions/` — one additive migration (`mcp_tokens` table + `activity_log.source` column). No further migrations needed through Milestone 5.
- [x] `backend/app/core/config.py` additions — `mcp_enabled`, `mcp_bootstrap_enabled`, `mcp_bootstrap_token` / `_file`.
- [x] `backend/app/services/mcp/` — token issuance/verification/revocation/listing service, scope checks (`app/mcp/auth.py::require_scope`).
- [x] `docker/nginx.conf` change — `/mcp` proxied to the backend; verified end-to-end (handshake, tools/list, resources/list) against a real `docker compose up --build` stack in Milestone 5.
- [x] `backend/tests/test_mcp_*.py` — unit, integration, security, authorization-matrix, and audit-completeness tests (469 backend tests total, 0 failures).
- [x] A new FDK verifier (`tools/fdk_verification/verifiers/agentic_review.py`) supporting the "Agentic Review" gate — used at every one of the five milestone gates.
- [x] Documentation: this folder's full doc set, plus `docs/Security.md`, `docs/Deployment.md`, `docs/API.md`, `docs/MCP_Usage.md` (new), `.env.example`, and ADR-0018/ADR-0019 (accepted). `forge-docs/02_ROADMAP.md` §3's Phase 11 row remains deliberately deferred to the Released/Frozen stage, per this repo's own convention (an unauthorized-for-release phase doesn't get a roadmap row yet). `docs/Architecture.md` was reviewed and found already accurate — its `/mcp` description is architecture-level (mount point, shared process) and was never milestone/tool-count-specific, so nothing there had gone stale.

## Dependencies

**Phase 07 (Knowledge Hub) — satisfied.** Phase 11 reads and writes through `services/knowledge/service.py` exactly as it exists today (tags, links, `list_knowledge`). No changes to Phase 07's data model or service surface are required.

**Phase 06 (Projects) — satisfied.** Phase 11's `forge_context` and project-scoped tools rely on the existing `project_id` nullable FK on Notes/Documents and `services/projects/service.py`, unchanged.

No other phase is a dependency. Phase 05 (Model Playground)'s provider/credential plumbing is **not** reused — Phase 11's auth model is deliberately independent (see `01_SPEC.md` §4), because Model Playground's credentials are for Forge calling *out* to LLM providers, while Phase 11 is about an LLM calling *in* to Forge.

## Milestones

- [x] **Milestone 1 — MCP Foundation.** Server, transport, auth/scopes, config, health/handshake, Docker wiring. No CRUD tools yet. Gate: independent Agentic Review — **PASS** (one repair cycle; a real BLOCKER found and fixed). Checkpointed, committed at `6854971`.
- [x] **Milestone 2 — Knowledge CRUD.** `forge_get/create/update/delete_note`, same for documents, `forge_list/get/create/update_project`. Gate: Agentic Review — **PASS** (one repair cycle; a real BLOCKER — a `confirm` boolean-coercion bypass — found and fixed). Checkpointed, committed at `4cf1bd2`.
- [x] **Milestone 3 — Search, Context & Knowledge Graph.** `forge_search`, `forge_context`, `forge_link_items`, `forge_unlink_items`. Gate: Agentic Review — **PASS** (one repair cycle; 3 MAJOR + 3 MINOR found and fixed). Checkpointed, committed.
- [x] **Milestone 4 — Claude Memory Workflows.** `forge_capture_session`/`forge_capture_decision`, resource exposure (`forge://projects`, `forge://projects/{id}`), multi-session continuity test (AC14). Gate: Agentic Review — **PASS** (one repair cycle; 1 MAJOR + 1 MINOR found, MAJOR fixed). Checkpointed, committed at `936c13c`.
- [x] **Milestone 5 — Production Hardening & Release.** Token-management Settings UI (owner-resolved open question), full authorization matrix (18 tools × 3 scopes × correct/wrong/zero, 469 backend tests total), audit-logging completeness pass, Docker production wiring verified against a real `docker compose up --build` stack, release artifacts. Gate: final Agentic RC Review — **PASS** (one repair cycle; a real MAJOR — a Secrets-exclusion regression test that never created a Secret — found and fixed; see `reviews/AGENTIC_REVIEW_M5.md`). The mandatory **human review gate** (§17 of the planning brief, checklist in `IMPLEMENT.md`) is the one remaining step, not self-certified by this session.

> Each milestone completion is a checkpoint trigger — see `../../10_CHECKPOINT_PROTOCOL.md` §1. Each milestone's Agentic Review gate must reach PASS before the next milestone starts; see `09_IMPLEMENTATION_TASKS.md` for exact gate criteria per milestone.

## Risks

**Technical**

- [ ] No existing per-token revocation mechanism exists in Forge (session tokens are stateless HMACs, revoked only by rotating the master password). Phase 11 must introduce the first DB-backed, individually revocable credential in the codebase. See `01_SPEC.md` §4.3.
- [ ] `services/knowledge/service.py`'s `purge_links_for` is called by the **route layer**, not by `notes_service.delete_note` / `documents_service.delete_document` themselves. MCP delete-tool handlers must replicate this orchestration explicitly or they will leave orphaned `knowledge_links` rows. See `03_BACKEND.md` §2.
- [ ] Deletion in Forge is hard-delete with no trash/undo for Notes/Documents (Projects unscope rather than delete children; only `archived` is soft). An MCP delete tool has no safety net beyond what this phase adds. See `01_SPEC.md` §6 (CRUD safety).
- [ ] The FDK verification framework (`tools/fdk_verification/`) has no existing "agentic/LLM review" verifier — everything today is mechanical (git diff, checkbox parsing, shell exit codes). Milestone 1 must define the smallest viable extension rather than build a parallel review framework. See `09_IMPLEMENTATION_TASKS.md` M1-T7.

**Product / Security**

- [ ] Exposing Secrets (even read-only) via MCP would let a compromised or over-broad Claude session exfiltrate the entire encrypted vault in one loop, since `FORGE_MASTER_KEY` is a single symmetric key with no per-secret scoping. This phase excludes Secrets entirely; `forge:secrets` scope exists in the model but is implemented by zero tools. See `01_SPEC.md` §2, §4.4.
- [ ] `services/crypto/service.py` (distinct from the vault) accepts/returns raw key material as plain arguments — if ever exposed via MCP, conversation transcripts could carry raw private keys. Deferred entirely, not partially exposed. See `01_SPEC.md` §2.

## Definition of Complete

- [x] All deliverables above are shipped and meet `../../08_DEFINITION_OF_DONE.md`.
- [x] `08_ACCEPTANCE.md` criteria are fully checked off and independently verified per `VERIFICATION_CONTRACT.md`.
- [x] `CURRENT_STATE.md` reflects reality with no stale "In Progress" items.
- [x] All five milestone Agentic Review gates reached PASS (not PASS-WITH-REQUIRED-FIXES left unresolved) — confirmed for all five, including Milestone 5's whole-phase RC review (see `reviews/AGENTIC_REVIEW_M5.md`).
- [x] The human review gate (post-Milestone-5) is explicitly signed off by the project owner — **complete, 2026-08-20**, item by item, in chat. Full record in `IMPLEMENT.md`. Phase 11 is clear for release; this phase still does not self-release — that remains the owner's own act.

## Cross-references

- [CURRENT_STATE.md](CURRENT_STATE.md)
- [01_SPEC.md](01_SPEC.md)
- [03_BACKEND.md](03_BACKEND.md)
- [04_DATABASE.md](04_DATABASE.md)
- [06_API.md](06_API.md)
- [07_TESTING.md](07_TESTING.md)
- [08_ACCEPTANCE.md](08_ACCEPTANCE.md)
- [09_IMPLEMENTATION_TASKS.md](09_IMPLEMENTATION_TASKS.md)
- [VERIFICATION_CONTRACT.md](VERIFICATION_CONTRACT.md)
- [../../02_ROADMAP.md](../../02_ROADMAP.md)
- [../../09_CLAUDE_CODE_RULES.md](../../09_CLAUDE_CODE_RULES.md)
- [../../15_VERIFICATION_FRAMEWORK.md](../../15_VERIFICATION_FRAMEWORK.md)
