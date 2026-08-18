# ADR-0018 — Forge's MCP server runs in-process inside the FastAPI backend, not as a separate service

> **Purpose:** Record the decision that Phase 11 (Claude MCP / Second Brain) mounts its MCP server as a module inside the existing `backend` FastAPI process, rather than standing up a second process/container.
> **Scope:** MCP transport/process architecture only. Not the full Phase 11 spec — that's [`../implementation/Phase-11-Claude-MCP/01_SPEC.md`](../implementation/Phase-11-Claude-MCP/01_SPEC.md).
> **Ownership:** Project owner (architecture direction approved 2026-08-18; Milestone 1 authorized 2026-08-18)
> **Status:** Accepted
> **Version:** 0.1.0
> **Last Updated:** 2026-08-18
> **Depends On:** [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md), [../implementation/Phase-11-Claude-MCP/01_SPEC.md](../implementation/Phase-11-Claude-MCP/01_SPEC.md)
> **Supersedes:** —

---

## 1. Context

Phase 11 gives Claude a scoped interface to Forge's Notes/Documents/Projects/Knowledge Hub via MCP (Model Context Protocol). The planning brief's core principle is that MCP tools must call the *same service layer* the REST API already calls, not a second implementation of Forge's business logic. `03_ARCHITECTURE.md` describes Forge today as one modular monolith: one FastAPI process, one Next.js process, one SQLite database, no microservices. Adding a persistent, remotely-reachable MCP endpoint is new territory — this ADR settles where that endpoint's code actually runs before any of it is written, per `09_CLAUDE_CODE_RULES.md` §3 ("any decision that would need a `decisions/` entry").

## 2. Decision

**The MCP server runs inside the existing `backend` FastAPI process**, as a new package `backend/app/mcp/`, mounted as an ASGI sub-application at `/mcp` alongside the existing `/api/*` REST surface and `/health`. It shares the same `AsyncSession` factory (`app/database/session.py`), the same `services/*` modules, and the same `app/core/config.py` settings object as the REST API. No new container, no new Docker service, no new inter-process boundary.

## 3. Alternatives considered

- **A separate process reaching Forge's SQLite file directly.** Rejected: SQLite is single-writer, single-migration-owner by design in this codebase (`main.py::_run_migrations()` runs synchronously at the one process's startup). A second process opening the same file would need its own migration ownership and would have to reimplement every service-layer invariant (e.g. `knowledge_service.purge_links_for`'s orphan-link prevention, `ActivityLog` audit writes) — exactly the "second implementation of Forge's business logic" this phase is built to avoid.
- **A separate process calling Forge's own REST API over HTTP.** Rejected: avoids the DB-sharing problem but replaces direct service calls with network calls to Forge's own API, requiring either a second copy of the browser-session auth flow or a bespoke bypass, doubles latency per tool call, and needs its own Docker service, health check, and redeploy story. It does not meaningfully reduce blast radius either — whoever holds valid MCP credentials reaches the same service layer and the same database either way, so the isolation would be nominal, not real.

## 4. Consequences

- `backend/app/mcp/` imports `services/notes`, `services/documents`, `services/projects`, `services/knowledge`, and `services/activity` directly — the "MCP calls the same service layer" principle is enforced structurally (same process, same import graph), not by convention.
- Forge's entire security model (`FORGE_MASTER_KEY`, Argon2id password hash, HMAC session tokens in `app/core/security.py`) stays in one process; the new MCP bearer-token scheme (ADR-0019) is one more FastAPI-adjacent auth path in that same process, not a cross-process trust handshake.
- Deployment cost is one nginx `location /mcp` block (mirroring the existing `/api/*` block) rather than a new service, network, or health check.
- **Accepted trade-off:** a vulnerability in the MCP library or a bug in a tool handler runs with the same process privileges as the REST API — there is no process-level sandbox between them. This is mitigated, not eliminated, by excluding Secrets/Settings/Crypto entirely from the MCP surface (`01_SPEC.md` §2), by the scoped bearer-token model (ADR-0019), and by MCP-originated writes being distinguishable in `ActivityLog` via a `source` column. `backend/app/mcp/` is factored as its own package specifically so it *could* be extracted into a separate process later if a future phase's threat model demands it — but that extraction is not attempted now, and no code in this phase depends on staying in-process in a way that would make extraction structurally harder than it already is for any other `services/*` consumer.
- This does not change `03_ARCHITECTURE.md`'s "one deploy lifecycle, no microservices" invariant — it is upheld, not exempted from.

## 5. Cross-references

- [../01_PRODUCT_PRINCIPLES.md](../01_PRODUCT_PRINCIPLES.md)
- [../03_ARCHITECTURE.md](../03_ARCHITECTURE.md)
- [0019-mcp-bearer-token-authentication.md](0019-mcp-bearer-token-authentication.md)
- [../implementation/Phase-11-Claude-MCP/01_SPEC.md](../implementation/Phase-11-Claude-MCP/01_SPEC.md)
- [../implementation/Phase-11-Claude-MCP/03_BACKEND.md](../implementation/Phase-11-Claude-MCP/03_BACKEND.md)
