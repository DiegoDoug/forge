# Phase 11 — Claude MCP / Second Brain — README

> **Purpose:** Entry point for Phase 11 — objective, scope, deliverables, and completion criteria.
> **Scope:** This phase only. Cross-phase sequencing lives in the roadmap.
> **Ownership:** Project owner — this entire phase requires explicit owner Authorization before implementation begins (see §3 "Before starting a phase" in `../README.md`), and explicit owner sign-off after Milestone 5's automated RC review, per §17 of the planning brief this phase was scoped from.
> **Status:** 📝 **Specification — produced by a one-shot planning session, NOT yet Authorized, NOT started.** No application code has been written or modified for this phase. See `CURRENT_STATE.md`.
> **Last Updated:** 2026-08-18

---

## A note on process

This spec package was produced by a single planning session that inspected the repository (backend architecture, auth model, service layer, database, forge-docs conventions, and the FDK verification framework) and wrote up an implementation-ready plan in one pass, rather than through the usual incremental drafting-with-the-owner cycle used for Phases 01–09. This is closer to Phase 10's exception than to the norm — but unlike Phase 10, this phase has **not been implemented**; it is Specification-stage only, and per `../../09_CLAUDE_CODE_RULES.md` §2/§3 it may not be Authorized or started without the project owner reviewing and explicitly approving it first.

## Objective

Make Forge Claude's persistent knowledge substrate by exposing a scoped, semantic MCP (Model Context Protocol) interface over Forge's existing Notes, Documents, Projects, and Knowledge Hub capabilities — so a Claude session (today or in a future session) can search, read, create, and organize knowledge in Forge, and can capture session context/decisions so a later session can retrieve them.

MCP is an **interface to Forge's existing application capabilities, not a second implementation of Forge's business logic.** MCP tools call the same service-layer functions the REST API already calls (`backend/app/services/notes`, `documents`, `projects`, `knowledge`), reusing the same Pydantic/SQLModel schemas wherever practical.

## Scope

**In scope:**

- [ ] An MCP server, mounted in-process inside the existing FastAPI backend (see `01_SPEC.md` §1 for the architecture decision and rejected alternative).
- [ ] Streamable HTTP transport, reachable through the existing nginx reverse proxy alongside the REST API.
- [ ] A new bearer-token authentication path, independent of the browser session cookie, with `forge:read` / `forge:write` / `forge:delete` scopes (see `01_SPEC.md` §4).
- [ ] A small, semantic MCP tool surface over Notes, Documents, Projects, and Knowledge Hub linking/tagging — full contract in `06_API.md`.
- [ ] `forge_context`, a Claude-oriented aggregate retrieval tool built on the existing FTS5 search and Knowledge Hub query layer — no new search index, no embeddings/vector search.
- [ ] Session/decision capture, implemented as ordinary Notes with a reserved tag convention — no new persistence model.
- [ ] Reuse of the existing `ActivityLog` service for an MCP-originated audit trail, with an added `source` distinction.
- [ ] Five implementation milestones, each gated by an independent automated review, and a mandatory human review gate after the final milestone's RC review — before any release/freeze action.

**Out of scope (see `01_SPEC.md` §2 for the full list with reasoning):**

- [ ] The Secrets/vault service and anything crypto-adjacent to it (`forge:secrets` scope is *defined* but implemented by nothing in this phase).
- [ ] Settings, backup/import/export, and master-password operations.
- [ ] Embeddings or vector search — the existing SQLite FTS5 index is sufficient for this phase's retrieval needs.
- [ ] A new "memory database" — session/decision capture reuses Notes.
- [ ] OAuth 2.0 for MCP auth — a static, revocable bearer token fits Forge's single-tenant, self-hosted deployment model; OAuth is flagged as a possible future hardening step, not built here.
- [ ] Any frontend surface beyond a minimal token-management view, which is itself deferred to Milestone 5 as an open question (see `01_SPEC.md` §4.6) rather than committed scope.

## Relationship to the shipped application

Phase 11 sits **beside** the REST API, not inside the frontend. It adds one new backend subsystem (`backend/app/mcp/`) that calls into the same `services/notes`, `services/documents`, `services/projects`, and `services/knowledge` modules the existing `api/routes/*.py` routers already call — see `03_BACKEND.md` for the exact reuse map. It introduces one new database concept (MCP access tokens) and no changes to the Notes/Documents/Projects/Knowledge data model.

Related backend: `backend/app/services/notes/`, `backend/app/services/documents/`, `backend/app/services/projects/`, `backend/app/services/knowledge/`, `backend/app/services/search/`, `backend/app/services/activity.py`, `backend/app/core/security.py`, `backend/app/api/deps.py`.

## Deliverables

- [ ] `backend/app/mcp/` — new package: server bootstrap, tool handlers, resource handlers, MCP-specific auth dependency.
- [ ] `backend/app/models/mcp_token.py` — one additive model (`McpToken`).
- [ ] `backend/alembic/versions/00XX_mcp_tokens.py` — one additive migration.
- [ ] `backend/app/core/config.py` additions — `mcp_enabled`, `mcp_bootstrap_token` / `_file`.
- [ ] `backend/app/services/mcp/` — token issuance/verification/revocation service, scope checks.
- [ ] `docker/nginx.conf` change — proxy `/mcp` to the backend (documented in `03_BACKEND.md` §5, not applied during this planning session).
- [ ] `backend/tests/test_mcp_*.py` — unit, integration, security, and MCP-contract tests per `07_TESTING.md`.
- [ ] A new FDK verifier (or documented extension) supporting an "Agentic Review" gate — see `09_IMPLEMENTATION_TASKS.md` Milestone 1 and the Verification Strategy note in `08_ACCEPTANCE.md` §5.
- [ ] Documentation: this folder's full doc set, plus updates to `docs/API.md`, `docs/Architecture.md`, `docs/Security.md`, `docs/Deployment.md`, `forge-docs/02_ROADMAP.md` §3 (Phase 11 row), and a new ADR (see `01_SPEC.md` §7).

## Dependencies

**Phase 07 (Knowledge Hub) — satisfied.** Phase 11 reads and writes through `services/knowledge/service.py` exactly as it exists today (tags, links, `list_knowledge`). No changes to Phase 07's data model or service surface are required.

**Phase 06 (Projects) — satisfied.** Phase 11's `forge_context` and project-scoped tools rely on the existing `project_id` nullable FK on Notes/Documents and `services/projects/service.py`, unchanged.

No other phase is a dependency. Phase 05 (Model Playground)'s provider/credential plumbing is **not** reused — Phase 11's auth model is deliberately independent (see `01_SPEC.md` §4), because Model Playground's credentials are for Forge calling *out* to LLM providers, while Phase 11 is about an LLM calling *in* to Forge.

## Milestones

- [ ] **Milestone 1 — MCP Foundation.** Server, transport, auth/scopes, config, health/handshake, Docker wiring. No CRUD tools yet. Gate: independent Agentic Review — architecture, security, transport, auth, Docker, regressions.
- [ ] **Milestone 2 — Knowledge CRUD.** `forge_get/create/update/delete_note`, same for documents, `forge_list/get/create/update_project`. Gate: Agentic Review — tool contracts, service-layer reuse, authorization, data integrity, regressions.
- [ ] **Milestone 3 — Search, Context & Knowledge Graph.** `forge_search`, `forge_context`, `forge_link_items`, `forge_unlink_items`. Gate: Agentic Review — retrieval correctness, ranking, information leakage, tool ergonomics.
- [ ] **Milestone 4 — Claude Memory Workflows.** `forge_capture_session`/`forge_capture_decision`, resource exposure (`forge://projects`, `forge://projects/{id}`), multi-session continuity documentation. Gate: Agentic Review — persistence correctness, cross-session retrieval, auditability.
- [ ] **Milestone 5 — Production Hardening & Release.** Token lifecycle (rotation/revocation), full authorization matrix, audit logging completeness, Docker production wiring, full regression + security test pass, release artifacts. Gate: final Agentic RC Review, then the mandatory **human review gate** (§17 of the planning brief) before any release/merge/tag action.

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

- [ ] All deliverables above are shipped and meet `../../08_DEFINITION_OF_DONE.md`.
- [ ] `08_ACCEPTANCE.md` criteria are fully checked off and independently verified per `VERIFICATION_CONTRACT.md`.
- [ ] `CURRENT_STATE.md` reflects reality with no stale "In Progress" items.
- [ ] All five milestone Agentic Review gates reached PASS (not PASS-WITH-REQUIRED-FIXES left unresolved).
- [ ] The human review gate (post-Milestone-5) is explicitly signed off by the project owner — this phase may not self-release.

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
