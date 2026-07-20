# 03 — Architecture

> **Purpose:** Describe the system shape every phase must fit into.
> **Scope:** High-level system architecture and integration points for new phases. Full current-state detail lives in [`../docs/Architecture.md`](../docs/Architecture.md); this document is the FDK-level entry point that stays stable while that one describes the living implementation.
> **Ownership:** TODO — assign a technical architecture owner.
> **Status:** Draft (reflects shipped system; forward-looking sections are proposals)
> **Version:** 0.2.0
> **Last Updated:** 2026-07-20
> **Depends On:** [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md)
> **Supersedes:** —

---

## 1. Current system shape

Forge is a **modular monolith**: one FastAPI process, one Next.js process, one SQLite database, fronted by Nginx in production (Next.js dev-server rewrites in development). No microservices, no message queue, no external runtime dependencies beyond what ships in the containers. Full detail: [`../docs/Architecture.md`](../docs/Architecture.md).

```
Browser
  │
  ▼
Nginx (production) / Next.js dev rewrites (development)
  ├── /            → frontend (Next.js, SSR + client app)
  └── /api/*       → backend (FastAPI)
                        │
                        ▼
                     SQLite (single file)
                        │
                        ▼
                     /data volume (uploads, ingest scratch space)
```

### 1.1 Backend layout

```
backend/app/
  core/        settings, security (encryption, sessions), error handling
  database/    async SQLAlchemy engine/session
  models/      SQLModel table definitions — single source of truth for schema
  schemas/     Pydantic request/response models
  services/    business logic, one subpackage per feature
  api/routes/  thin FastAPI routers
```

### 1.2 Frontend layout

```
frontend/
  app/(auth)/      setup, unlock — no sidebar, no auth required
  app/(app)/       every real feature page — wrapped in AuthGate + shell
  features/*/      api.ts (typed fetch + React Query hooks) + feature components
  components/      shared UI: shadcn primitives, app shell, command palette
  lib/             api client, nav registry, formatting helpers
```

### 1.3 Auth model

Single-tenant. `FORGE_MASTER_KEY` (operator secret, never stored in the database) encrypts vault values at rest and signs session cookies. The master password only decides whether the current browser gets a session. Full model: [`../docs/Security.md`](../docs/Security.md).

## 2. Architectural invariants (do not violate without an ADR)

- One database, one deploy lifecycle, no per-feature services.
- Features never import from each other's internals — see [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md).
- Routers stay thin; all decision-making logic lives in `services/`.
- Models (`SQLModel`) are the schema source of truth; migrations are explicit after the initial one.
- Session-cookie behavior favors working-on-LAN over textbook-secure-by-default (documented exception, not a bug) — see [`../docs/DecisionLog.md`](../docs/DecisionLog.md).

## 3. Integration points for new phases

Every phase under [`implementation/`](implementation/) must state, in its own `03_BACKEND.md` / `04_DATABASE.md`, how it plugs into this shape:

- [ ] Does it add a new `services/<feature>/` subpackage, or extend an existing one? (Prefer extending for consolidation phases like Developer Toolkit / Universal Converter.)
- [ ] Does it add new tables? If so, an Alembic migration is required — no direct schema edits.
- [ ] Does it need a new external dependency (e.g. an LLM SDK for Prompt Studio / Model Playground)? Record it in [06_TECH_STACK.md](06_TECH_STACK.md) and justify it in a decision record.
- [ ] Does it introduce a provider/API-key concept (Model Playground)? This is new territory for Forge — requires its own security review against [`../docs/Security.md`](../docs/Security.md).

## 4. Open architectural questions

- [ ] TODO: **Capability Registry** — [ADR-0008](decisions/0008-capability-registry-direction.md) (Proposed, not Accepted) sketches generalizing Phase 01's Panel Registry into a unified registry for panels, pages, commands, workflow nodes, and more — see [`architecture/CAPABILITY_REGISTRY.md`](architecture/CAPABILITY_REGISTRY.md). Deliberately deferred until a second real registry-shaped need exists; do not build against it yet.
- [ ] TODO: Where does "Project" (Phase 06) live in the data model — a new top-level table that Vault/Secrets/Notes/Documents gain an optional foreign key to, or a purely client-side grouping?
- [ ] TODO: Model Playground and Prompt Studio will need outbound network calls to third-party LLM providers — this is a first for Forge (currently only Ingest's optional vision-LLM path does this). Needs an explicit "outbound network calls" section added to Security.md.
- [ ] TODO: Does Knowledge Hub introduce a new search index, or extend the existing FTS5 setup used by Notes?

## 5. TODO

- [ ] TODO: Ratify the invariants in Section 2 as hard rules vs. guidelines.
- [ ] TODO: Produce a component diagram once Phase 01–02 land (current diagram is request-flow only).

## 6. Cross-references

- [../docs/Architecture.md](../docs/Architecture.md) — living, detailed architecture of the shipped app
- [../docs/Security.md](../docs/Security.md)
- [../docs/Database.md](../docs/Database.md)
- [06_TECH_STACK.md](06_TECH_STACK.md)
- [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md)
- [11_PROJECT_STRUCTURE.md](11_PROJECT_STRUCTURE.md)
- [decisions/README.md](decisions/README.md)
