# Folder structure

```
forge/
├── backend/
│   ├── app/
│   │   ├── main.py              FastAPI app factory, lifespan (migrations, cleanup threads)
│   │   ├── core/                 config, security (encryption/sessions), errors, version
│   │   ├── database/              async SQLAlchemy engine/session
│   │   ├── models/                 SQLModel tables — single source of truth for schema
│   │   ├── schemas/                Pydantic request/response models, per feature
│   │   ├── services/               business logic, one subpackage per feature
│   │   │   ├── secrets/
│   │   │   ├── notes/
│   │   │   ├── generators/
│   │   │   ├── crypto/
│   │   │   ├── converters/         cron parsing + a small provider registry (providers/) wrapping ingest/
│   │   │   ├── ingest/             ported from the standalone Ingest project
│   │   │   ├── search/
│   │   │   └── settings/
│   │   └── api/
│   │       ├── deps.py             auth dependency, session helpers
│   │       ├── router.py           aggregates every feature router under /api
│   │       └── routes/             one router file per feature
│   ├── alembic/                    migrations
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   │   ├── (auth)/                 setup, unlock — no sidebar
│   │   └── (app)/                  every real page — wrapped in AuthGate + shell
│   ├── features/                   one folder per feature: api.ts + components
│   │   ├── secrets/
│   │   ├── notes/
│   │   ├── generators/
│   │   ├── crypto/
│   │   ├── converters/
│   │   ├── utilities/
│   │   ├── ingest/
│   │   ├── workbench/
│   │   ├── search/
│   │   ├── settings/
│   │   └── auth/
│   ├── components/
│   │   ├── ui/                     shadcn/ui primitives (Base UI-based)
│   │   ├── app-shell/               sidebar, topbar, mobile nav
│   │   └── command-palette/         ⌘K provider + dialog
│   ├── lib/                         api client, nav registry, formatting, utils
│   ├── hooks/
│   └── Dockerfile
│
├── docker/
│   └── nginx.conf                   single-entrypoint reverse proxy for production
├── docs/                            this folder
├── docker-compose.yml
└── .env.example
```

## Conventions

- **Features don't import from each other.** `features/secrets` never imports
  from `features/notes`, and vice versa. Anything genuinely shared (the API
  client, formatting helpers, shared UI) lives in `lib/` or `components/`.
- **`api.ts` is the only file in a feature that knows backend endpoint
  shapes.** Pages and components call hooks it exports
  (`useSecrets`, `useSecretsMutations`, ...), never `fetch` directly.
- **Backend routers are thin.** Validation lives in Pydantic schemas,
  business logic lives in `services/`, routers just wire the two together
  and shape the HTTP response.
- **Models are the schema source of truth.** The initial Alembic migration
  builds tables from `SQLModel.metadata` directly rather than duplicating
  column definitions by hand; every migration after that is explicit (see
  [Database.md](Database.md)).
