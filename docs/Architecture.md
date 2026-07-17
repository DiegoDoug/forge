# Architecture

Forge is a **modular monolith**: one FastAPI process, one Next.js process,
one SQLite database. No microservices, no message queue, no external
dependencies beyond what ships in the containers.

## Why a monolith

At the scale of a single-user (or small-team) self-hosted toolbox, splitting
Vault/Notes/Generators/etc. into separate services would add operational
complexity (service discovery, inter-service auth, distributed transactions)
with no corresponding benefit — every feature shares the same database, the
same auth session, and the same deploy lifecycle. A modular monolith gets the
organizational benefits of separation (isolated feature folders, clear
service boundaries in code) without the deployment cost.

## Request flow

```
Browser
  │  https://forge.example.com/
  ▼
Nginx (docker/nginx.conf)
  ├── /            → frontend:3000  (Next.js, SSR + client app)
  └── /api/*       → backend:8000   (FastAPI)
                        │
                        ▼
                     SQLite (single file, /data/forge.db)
                        │
                        ▼
                     /data volume (uploads, ingest job scratch space)
```

In development there is no Nginx — `next dev` proxies `/api/*` to the
backend itself via `next.config.ts` rewrites, so the frontend always talks to
a same-origin `/api/...` path regardless of environment. This is what lets
session cookies work without CORS configuration in both modes.

## Backend layout

```
backend/app/
  core/        settings, security (encryption, sessions), error handling
  database/    async SQLAlchemy engine/session
  models/      SQLModel table definitions (single source of truth for schema)
  schemas/     Pydantic request/response models (never expose ORM objects directly)
  services/    business logic, one subpackage per feature (vault, notes, ingest, …)
  api/routes/  thin FastAPI routers — validate input, call a service, shape output
```

Routers stay thin on purpose: anything with a decision to make (encryption,
validation beyond types, cross-entity logic) lives in `services/`, so it's
testable without spinning up HTTP.

## Frontend layout

```
frontend/
  app/(auth)/      setup, unlock — no sidebar, no auth required
  app/(app)/       every real feature page — wrapped in AuthGate + shell
  features/*/      api.ts (typed fetch + React Query hooks) + feature components
  components/      shared UI: shadcn primitives, app shell, command palette
  lib/              api client, nav registry, formatting helpers
```

Each `features/<name>/api.ts` is the only place that knows the shape of that
feature's backend endpoints — pages and components import hooks from it
rather than calling `fetch` directly.

## Auth model

Forge is single-tenant: one master password gates the whole instance.
`FORGE_MASTER_KEY` (an operator secret, never stored in the database)
encrypts vault values at rest and signs session cookies; the master password
only decides whether the *current browser* gets a session. See
[Security.md](Security.md) for the full model.

## Ingest

The `/ingest` feature is a direct port of the standalone
[Ingest](https://github.com/DiegoDoug/Ingest) project's conversion pipeline
(`app/services/ingest/`) — MarkItDown-based document→Markdown conversion, an
in-memory job store with TTL cleanup, and optional vision-LLM assistance for
scanned PDFs/images. It's intentionally *not* persisted to the database:
uploads and results are scratch data, unlike vault secrets and notes.
