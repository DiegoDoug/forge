# 11 — Project Structure

> **Purpose:** Physical map of the repository, including both the shipped application and the FDK documentation system itself.
> **Scope:** Directory-level structure only. Conventions for *why* it's organized this way live in [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md) and [03_ARCHITECTURE.md](03_ARCHITECTURE.md).
> **Ownership:** TODO — assign an owner.
> **Status:** Current as of FDK scaffold creation
> **Last Updated:** 2026-07-20

---

## 1. Repository root

```
forge/
├── backend/            FastAPI application — see §2
├── frontend/            Next.js application — see §3
├── docker/               nginx.conf — production reverse proxy config
├── docker-compose.yml
├── .env.example
├── docs/                 user-facing documentation for the shipped app (see docs/README.md)
├── forge-docs/           the FDK — this documentation-first engineering system
│   ├── 00_VISION.md .. 11_PROJECT_STRUCTURE.md
│   ├── templates/        reusable templates (project-initialization, chunks, workflows, prompts, assets)
│   ├── decisions/         architecture decision records (ADRs)
│   ├── history/           checkpoint log — durable record of every session checkpoint
│   └── implementation/    Phase-01-Workbench .. Phase-08-Developer-Toolkit
└── .claude/               Claude Code session templates + launch config
```

## 2. Backend (`backend/`)

```
backend/
├── app/
│   ├── main.py           FastAPI app factory, lifespan (migrations, cleanup threads)
│   ├── core/              settings, security, error handling, version
│   ├── database/          async SQLAlchemy engine/session
│   ├── models/            SQLModel tables — schema source of truth
│   ├── schemas/           Pydantic request/response models, per feature
│   ├── services/          business logic, one subpackage per feature
│   │   ├── vault/ notes/ generators/ crypto/ converters/ documents/
│   │   ├── ingest/         ported from the standalone Ingest project
│   │   └── search/ settings/
│   └── api/
│       ├── deps.py         auth dependency, session helpers
│       ├── router.py       aggregates every feature router under /api
│       └── routes/          one router file per feature
├── alembic/               migrations
├── requirements.txt
└── Dockerfile
```

## 3. Frontend (`frontend/`)

```
frontend/
├── app/
│   ├── (auth)/            setup, unlock — no sidebar
│   └── (app)/             every real page — wrapped in AuthGate + shell
├── features/               one folder per feature: api.ts + components
│   ├── vault/ notes/ documents/ generators/ crypto/ converters/
│   ├── utilities/ ingest/ dashboard/ search/ settings/ auth/
├── components/
│   ├── ui/                 shadcn/ui primitives (Base UI-based)
│   ├── app-shell/           sidebar, topbar, mobile nav
│   └── command-palette/     ⌘K provider + dialog
├── lib/                     api client, nav registry, formatting, utils
├── hooks/
└── Dockerfile
```

## 4. Documentation systems (`docs/` vs. `forge-docs/`)

These are deliberately separate and serve different audiences:

| | `docs/` | `forge-docs/` |
|---|---|---|
| Audience | End users / operators / contributors reading about the shipped app | Claude Code sessions and maintainers driving future development |
| Content | Architecture, Security, Database, API, Deployment, Development, Contributing, DecisionLog, Roadmap, FolderStructure — **as the app exists today** | Vision, principles, roadmap, phase specs, execution contracts — **how future work gets planned and built** |
| Changes when | The shipped app's behavior changes | A new phase is planned, specified, or executed |

Do not duplicate content between them — `forge-docs/` documents should link to `docs/` for current-state detail rather than restating it (see cross-references throughout `forge-docs/00_VISION.md` through `11_PROJECT_STRUCTURE.md`).

## 5. Implementation phases (`forge-docs/implementation/`)

Each `Phase-XX-Name/` directory is self-contained and follows the same 12-file structure. See [02_ROADMAP.md](02_ROADMAP.md) for the phase list and sequencing.

## 6. TODO

- [ ] TODO: Update this document any time a top-level directory is added or removed — it's the map, it must not go stale.
- [ ] TODO: Add a `packages/` or `shared/` note if cross-app shared code is ever introduced (none exists today; features are isolated per [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md)).

## 7. Cross-references

- [../docs/FolderStructure.md](../docs/FolderStructure.md) — the pre-existing, detailed version of §2–§3 above
- [03_ARCHITECTURE.md](03_ARCHITECTURE.md)
- [02_ROADMAP.md](02_ROADMAP.md)
- [implementation/](implementation/)
