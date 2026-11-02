# Forge — Project Handout

> Orientation document for a new developer or AI agent working in this repository. Complements, does not replace, `docs/` (shipped-app reference) and `forge-docs/` (development methodology and phase history) — see §12 for how those three doc sets relate.

## 1. Project Overview

Forge is a self-hosted "developer toolbox" web app: a password/secrets manager, a sticky-note board, a rich-text document editor, a universal format converter, and a set of crypto/generator utilities, unified behind one login and one command palette. Single-tenant (one master password gates the whole instance), meant to run on hardware the user controls (Docker Compose, no required external services).

Stack, confirmed from manifests: **FastAPI** (Python, `backend/requirements.txt`) + **SQLite** (via `aiosqlite`/SQLModel) on the backend, **Next.js 15 / React 19 / TypeScript** (`frontend/package.json`) on the frontend, **nginx** as the single production entrypoint (`docker/nginx.conf`, `docker-compose.yml`).

As of this writing the repo is mid-implementation of **Phase 11 (Claude MCP / Second Brain)** — an MCP server (`backend/app/mcp/`) letting Claude use Forge as persistent knowledge storage. Two of five planned milestones are committed (see `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md`); this is the newest, least-stable area of the codebase.

## 2. Repository Mental Model

One FastAPI process, one Next.js process, one SQLite file, fronted by nginx in production. No microservices, no message queue — confirmed explicitly in `docs/Architecture.md` ("Why a monolith").

```
Browser ──▶ nginx (docker/nginx.conf) ──┬─▶ / ───────▶ frontend:3000 (Next.js)
                                         ├─▶ /api/* ──▶ backend:8000 (FastAPI) ──▶ SQLite (/data/forge.db)
                                         └─▶ /mcp ────▶ backend:8000 (same process — MCP, off by default)
```

- **Data enters** through `frontend/features/<name>/api.ts` (typed fetch wrappers) → `backend/app/api/routes/<name>.py` (thin routers) → `backend/app/services/<name>/service.py` (business logic, where validation and side effects actually happen) → `backend/app/models/` (SQLModel tables, the schema source of truth) → SQLite.
- **Auth** is a single stateless HMAC session cookie (`forge_session`), enforced per-router via a FastAPI dependency (`AuthDep` in `backend/app/api/deps.py`) — see `docs/Security.md`.
- **Persistence** is one SQLite file at `FORGE_DATA_DIR/forge.db`; migrations run automatically at backend startup (`alembic upgrade head`, invoked from `app/main.py`'s lifespan) — there is no separate migration step to remember.
- **External services** are opt-in and off by default: an optional vision-LLM for OCR (`FORGE_VISION_*`), optional Model Playground provider credentials (OpenAI/Anthropic/etc., user-configured in the UI, not env vars), and the optional MCP server (`FORGE_MCP_ENABLED`).
- **Tests** live in `backend/tests/` (pytest, 30 files) and `tools/tests/` (a separate, self-contained test suite for the FDK verification framework — see §12). The frontend has **no test framework** (confirmed: no test script in `frontend/package.json`, no test files under `frontend/`) — this is a known, documented gap, not an oversight to silently work around.
- **Configuration** is environment variables (`.env`, from `.env.example`) read by `backend/app/core/config.py`'s `pydantic_settings` `Settings` class — there is no separate YAML/JSON app-config file.

This is not a monorepo in the workspace-tooling sense (no shared `package.json` workspaces, no Turborepo/Nx) — it's two independently-run apps (`backend/`, `frontend/`) plus a `tools/` directory that is infrastructure for *this repo's own development process*, not part of the shipped product.

## 3. Repository Map

| Path | Responsibility | Notes |
|---|---|---|
| `backend/app/main.py` | FastAPI app factory, lifespan (runs migrations, starts cleanup threads, conditionally mounts `/mcp`) | Entry point for understanding backend startup |
| `backend/app/core/` | `config.py` (env-driven settings), `security.py` (encryption + session/token primitives), `errors.py` (exception → HTTP envelope mapping), `version.py` | Read `config.py` first to find every env var the app actually reads |
| `backend/app/database/` | Async SQLAlchemy engine/session factory | `get_sessionmaker()`/`get_engine()` are `lru_cache`d singletons — tests must `.cache_clear()` them when isolating env/data-dir per test |
| `backend/app/models/` | SQLModel tables — schema source of truth. New tables/columns need an Alembic migration, not hand-edited SQL | Every model must be imported in `models/__init__.py` or the initial migration's `create_all()` won't see it |
| `backend/app/schemas/` | Pydantic request/response models, one file per feature | ORM objects are never returned directly from a route — always shaped through here |
| `backend/app/services/<feature>/service.py` | Business logic, one subpackage per feature (`secrets`, `notes`, `documents`, `projects`, `knowledge`, `search`, `settings`, `mcp`, `model_playground`, `prompt_studio`, `converters`, `ingest`, `generators`, `crypto`, `project_init`) | This is what gets unit-tested — routers should stay thin |
| `backend/app/api/routes/<feature>.py` | One thin router per feature, registered in `backend/app/api/router.py` | Validation lives in `schemas/`, logic in `services/`; routers just wire the two together |
| `backend/app/api/deps.py` | `AuthDep`/`require_auth` (browser session), `SessionDep` | Applied via `dependencies=[AuthDep]` on almost every router |
| `backend/app/mcp/` | MCP server: `auth.py` (bearer-token auth, independent of `AuthDep`), `server.py` (mounts `/mcp`), `tools/` (one module per domain, e.g. `notes.py`, `documents.py`, `projects.py`) | Newest, actively-changing subsystem — see §10 |
| `backend/alembic/versions/` | Migrations, applied automatically at startup — 10 as of this writing | `alembic revision --autogenerate -m "..."` then review by hand (SQLite's limited `ALTER TABLE` needs `batch_alter_table` for some changes) |
| `backend/tests/` | pytest suite, 30 files, mirrors `services/`/`api/routes/` one-to-one in most cases | Run with `backend/.venv/Scripts/python.exe -m pytest` (Windows) |
| `frontend/app/(app)/<feature>/page.tsx` | One route per top-level feature; `(auth)/` holds the pre-login setup/unlock screens | App Router, route groups don't affect the URL |
| `frontend/features/<feature>/` | `api.ts` (typed fetch + React Query hooks — the *only* file that knows backend endpoint shapes) + feature components | Features never import from each other; anything shared goes in `lib/` or `components/` |
| `frontend/components/ui/` | shadcn/ui primitives, built on **Base UI** (not Radix) despite the shadcn CLI | `render={<X/>}` composition, not `asChild` — see `docs/Development.md` |
| `frontend/lib/nav-registry.ts` | Single source driving both the sidebar and the ⌘K command palette | Add a top-level feature here or it won't be reachable from the UI |
| `docker/nginx.conf`, `docker-compose.yml`, `.env.example` | Production topology and required/optional env vars | No dev-mode compose profile exists — see §5 |
| `docs/` | Shipped-app reference documentation (Architecture, API, Database, Security, Deployment, Contributing, Development) | Read this before `forge-docs/` for "how does the app work" questions |
| `forge-docs/` | This project's own FDK (development methodology): numbered root docs (vision → coding standards → verification framework), `implementation/Phase-NN-*/` per-phase specs, `decisions/` (ADRs), `history/` (checkpoints, frozen-phase archives) | Read this for "why was it built this way" and "what's the process for changing it" |
| `tools/fdk_verification/` | A self-contained Python package implementing this repo's own automated phase-verification framework | Not application code — infrastructure for the `forge-docs/` process. Has its own `tools/tests/` |

## 4. Architecture

- **Backend feature isolation**: each feature's logic lives in exactly one `services/<name>/` subpackage; routers stay thin. Enforced by convention and reviewed manually (`docs/Contributing.md`), not by a lint rule.
- **Frontend feature isolation**: `features/<name>/` directories never import each other. `api.ts` is the single boundary between a feature and the backend — components call its exported hooks, never `fetch` directly.
- **Two independent auth models, as of Phase 11**: the browser uses a stateless HMAC session cookie (`AuthDep`, `backend/app/api/deps.py`); the MCP surface uses a separate bearer-token scheme (`backend/app/mcp/auth.py`) with its own provisioning route (`POST /api/mcp/tokens`). These are deliberately independent — neither credential type satisfies the other's dependency. See `docs/Security.md` and `forge-docs/decisions/0019-mcp-bearer-token-authentication.md`.
- **Secrets/Crypto/Settings are excluded from the MCP surface entirely** — no file under `backend/app/mcp/` imports from `services/secrets`, `services/crypto`, or `services/settings`. This boundary is enforced by an automated test (`backend/tests/test_mcp_tools_static_checks.py`), not just convention — a meaningful signal that it's treated as security-load-bearing, not stylistic.
- **Models are the schema source of truth**: the first Alembic migration builds tables from `SQLModel.metadata` directly; every migration since is hand-written and additive.
- **No versioned API path** (`/api/v1/...`) — a deliberate choice, explained in `docs/API.md`.

## 5. Development Workflow

Commands verified against actual manifests/scripts — nothing here is assumed from convention.

**Backend** (from `docs/Development.md`):
```bash
cd backend
python -m venv .venv && ./.venv/Scripts/activate   # Windows; `source .venv/bin/activate` elsewhere
pip install -r requirements.txt
export FORGE_MASTER_KEY="dev-only-key-change-me"
export FORGE_DATA_DIR=./.dev-data
python -m uvicorn app.main:app --reload --port 8000
```
Migrations run automatically on startup. After changing a model in `app/models/`:
```bash
alembic revision --autogenerate -m "add foo column"   # then review the generated file by hand
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev       # next dev --turbopack
```
Other scripts, verbatim from `frontend/package.json`: `npm run build` (`next build --turbopack` — this is also the type-check step, since Next.js runs `tsc` as part of build; there is no separate `typecheck` script), `npm run start` (`next start`), `npm run lint` (`eslint`). **Do not run `npm run dev` and `npm run build` at the same time** — both write to `.next/` and will corrupt each other's cache.

**Backend tests**:
```bash
cd backend
.venv/Scripts/python.exe -m pytest            # full suite, 30 files
.venv/Scripts/python.exe -m pytest tests/test_notes_service.py -v   # targeted
```
`pytest.ini` sets `testpaths = tests`, `asyncio_mode = auto` — async `def test_...` functions work without a decorator.

**FDK-framework tests** (not application tests — validates `tools/fdk_verification/` itself):
```bash
backend/.venv/Scripts/python.exe -m pytest tools/tests -q   # run from repo root
```

**No frontend test command exists** — there is no test framework installed. Validation for frontend changes today is `npm run build` (type errors) + `npm run lint` + manual exercise in the browser.

**Full stack (production-shaped)**:
```bash
cp .env.example .env   # set FORGE_MASTER_KEY
docker compose up --build
# → http://localhost:${FORGE_PORT:-8585}
```
There is **no dev-mode Docker Compose profile** — Compose is for the production-shaped build only; local development runs `uvicorn --reload` and `npm run dev` side by side (`docs/Development.md`).

**No CI configuration exists in this repository** (`.github/workflows/` and equivalents are absent) — validation is currently run manually, locally, per the commands above.

## 6. Configuration

Single mechanism: environment variables, loaded by `backend/app/core/config.py`'s `pydantic_settings.Settings` (prefix `FORGE_`, optional `.env` file). `.env.example` at the repo root is the canonical list of what exists — do not duplicate its content here as it changes; summary of the categories:

- **Required**: `FORGE_MASTER_KEY` — root encryption key for secrets-at-rest and session signing. No default; the app will refuse to start meaningfully without it. `FORGE_MASTER_KEY_FILE` is the Docker-secrets-file alternative (file wins if both set).
- **Deployment**: `FORGE_PORT` (nginx's published port, default 8585), `FORGE_SESSION_COOKIE_SECURE` (default `false` — deliberately, so plain-HTTP LAN use isn't silently broken; flip to `true` once behind real TLS).
- **Optional, off by default**: `FORGE_VISION_ENABLED`/`FORGE_VISION_API_KEY`/`FORGE_VISION_BASE_URL` (vision-LLM OCR assist for Ingest); `FORGE_MCP_ENABLED`/`FORGE_MCP_BOOTSTRAP_ENABLED`/`FORGE_MCP_BOOTSTRAP_TOKEN[_FILE]` (the MCP server — see `docs/Security.md`'s "MCP access" section for the full provisioning flow before touching this).
- **Provider credentials for Model Playground/Prompt Studio** (OpenAI/Anthropic/etc.) are **not** environment variables — they're entered through the UI and encrypted at rest with the same primitive Secrets uses.

Local dev additionally needs `FORGE_DATA_DIR` (where the SQLite file and uploads live — not required in the Docker path, where it's fixed to `/data`).

**Never commit `.env`** — it's gitignored and, in this working copy, already contains a real value; do not read or print it. Secrets that must be obtained rather than guessed (a real `FORGE_MASTER_KEY` for anything beyond local dev, provider API keys) should come from whoever owns the deployment, not be invented.

## 7. Conventions

Extracted from `docs/Contributing.md`, `docs/Development.md`, and observed code — not invented:

- **Backend**: type-annotated Python, `from __future__ import annotations` everywhere **except** files with SQLModel `Relationship()` fields (breaks forward-reference resolution for `list["Secret"]`-style generics under this project's pinned SQLAlchemy version — see `app/models/secrets.py` for the exception in practice).
- **Frontend**: TypeScript, no `any`. Compose shadcn/Base UI primitives for interactive elements rather than raw HTML.
- **No commented-out code, no `TODO` placeholders left in shipped code** — stated explicitly as a rule in `docs/Contributing.md`. (Note: `forge-docs/` planning documents *do* use `TODO:`/`[ ]` markers extensively — that convention applies to application code, not planning docs.)
- **No placeholder/mocked implementations** — if something is out of scope, it's left out and the gap is documented (see `docs/DecisionLog.md` for real examples), not stubbed.
- **Adding a feature** follows a fixed shape on both sides — see `docs/Contributing.md` §"Adding a new tool/feature" for the exact backend (model → migration → schema → service → route → router registration) and frontend (`api.ts` → components → page → `nav-registry.ts`) sequence. Don't improvise a different shape without a reason.
- **Git history is fact**: recent commits and `forge-docs/history/*-checkpoint.md` files are a more reliable record of *why* something is the way it is than inferring intent from code alone, especially in `backend/app/mcp/` (built across two recent, heavily-reviewed milestones — see `forge-docs/implementation/Phase-11-Claude-MCP/`).

## 8. Testing & Validation

Smallest-to-largest, adapted to what actually exists:

1. **Targeted backend test**: `pytest tests/test_<feature>_service.py -v` for the service you touched.
2. **Full backend suite**: `pytest` from `backend/` — must stay green; this repo's own process treats an unexplained regression here as a blocker (see `forge-docs/implementation/Phase-11-Claude-MCP/VERIFICATION_CONTRACT.md` for a real, recent example of this being enforced).
3. **Frontend build**: `npm run build` in `frontend/` — the only type-checking step that exists; treat a failure here the same as a failing test.
4. **Frontend lint**: `npm run lint`.
5. **Manual exercise**: for any frontend change, there is no automated substitute — actually click through the affected page(s). For any backend change, exercise the endpoint directly (curl, or the interactive docs at `/docs`) rather than trusting the UI alone (`docs/Contributing.md`'s explicit advice).
6. **FDK framework tests** (`pytest tools/tests`) only matter if you touched `tools/fdk_verification/` itself — unrelated to application correctness.

What does **not** exist: any frontend test runner, any CI pipeline, any automated end-to-end/browser test suite. Coverage claims should be scoped to "the backend service layer has pytest coverage" — nothing broader is currently true.

## 9. Common Change Paths

| Task | Where |
|---|---|
| Add a backend feature/endpoint | `backend/app/models/` (if persisted) → migration → `backend/app/schemas/<feature>.py` → `backend/app/services/<feature>/service.py` → `backend/app/api/routes/<feature>.py` → register in `backend/app/api/router.py` |
| Add a frontend page/feature | `frontend/features/<feature>/api.ts` → components in the same folder → `frontend/app/(app)/<feature>/page.tsx` → add to `frontend/lib/nav-registry.ts` if top-level |
| Change a data model | `backend/app/models/<file>.py`, then `alembic revision --autogenerate`, review, then update the corresponding `schemas/` file |
| Add a dependency (backend) | `backend/requirements.txt` (runtime) or `requirements-dev.txt` (test-only) |
| Add a dependency (frontend) | `npm install <pkg>` in `frontend/` (updates `package.json`/`package-lock.json`) |
| Add a shadcn/ui component | `cd frontend && npx shadcn@latest add <component>` — see `docs/Development.md` for the Base UI composition differences vs. stock shadcn docs |
| Change deployment/proxy behavior | `docker/nginx.conf`, `docker-compose.yml` |
| Add/modify an MCP tool | `backend/app/mcp/tools/<domain>.py`, following the `register(server)` convention in `_common.py`; add tests in `backend/tests/test_mcp_tools_*.py` |
| Update process/planning docs | `forge-docs/implementation/Phase-NN-*/` for an active phase; `forge-docs/decisions/` for a new ADR |

## 10. Sensitive & Protected Areas

**Do not hand-edit**:
- `backend/alembic/versions/*.py` after it's been applied/committed — write a new migration instead.
- `frontend/.next/`, `backend/.venv*/`, `**/__pycache__/`, `frontend/node_modules/` — all generated/vendored, all gitignored.
- `.env` — real secrets for this working copy; gitignored, never commit it, never print its contents.

**Extra care required**:
- `backend/app/core/security.py` — encryption-at-rest and session/token primitives. Changes here affect every stored secret and every active session.
- `backend/app/services/secrets/` and `backend/app/services/crypto/` — the credential vault and crypto-primitive toolkit. `backend/app/mcp/` must never import from either (enforced by a static test, §4) — do not weaken that boundary casually.
- `backend/app/mcp/` generally — actively developed across recent milestones with a documented pattern of independent adversarial review before each milestone was accepted (see `forge-docs/implementation/Phase-11-Claude-MCP/reviews/`); changes here should get the same scrutiny, not less, because it's newer and less "settled" than the rest of the app.
- `backend/app/api/deps.py` (`AuthDep`/`require_auth`) — the entire browser-auth boundary; every router except `/health` and the pre-login auth routes depends on it.
- `docker/nginx.conf`, `docker-compose.yml`, `.env.example` — production topology and the required-secret contract; a mistake here is a deployment-breaking or security-relevant change, not a local-only one.
- `forge-docs/decisions/*.md` (ADRs) and frozen phases under `forge-docs/implementation/` — these represent settled decisions; don't silently contradict or reopen one without following this repo's own process (`forge-docs/13_PHASE_LIFECYCLE.md`, `forge-docs/09_CLAUDE_CODE_RULES.md`).

## 11. AI Agent Guidance

- **Start here, in order**: this file → `docs/Architecture.md` (system shape) → the specific `docs/*.md` for the subsystem you're touching → the relevant `backend/app/services/<feature>/service.py` or `frontend/features/<feature>/api.ts` (actual behavior, more authoritative than any doc if they disagree — see §13 below).
- **Treat as authoritative**: `backend/app/models/` (schema truth), `backend/app/core/config.py` (what env vars actually exist), `frontend/lib/nav-registry.ts` (what's actually reachable in the UI), `.env.example` (what config actually exists — not `docs/Deployment.md`'s prose, which can drift).
- **Treat as primary implementation code**: `backend/app/services/**`, `backend/app/api/routes/**`, `frontend/features/**`. Treat `backend/app/schemas/**` and `frontend/app/**` (pages) as thinner, derivative layers.
- **Do not modify casually**: everything in §10. If a task seems to require touching `security.py`, the Secrets/Crypto boundary, or `AuthDep`, stop and confirm scope before proceeding — these are exactly the areas this repo's own process (`forge-docs/09_CLAUDE_CODE_RULES.md`) requires asking about first.
- **Validate with the real commands in §5/§8**, not assumed ones — there is no `npm test`, no CI, and no `typecheck` script; `npm run build` is the type-check step.
- **Avoid unnecessary architectural changes**: this repo enforces feature isolation (frontend features never import each other; backend routers stay thin) by convention and manual review, not tooling — a change that reaches across a feature boundary "just this once" is a real regression here, not a style nit. If genuinely touching `backend/app/mcp/`, read `forge-docs/implementation/Phase-11-Claude-MCP/CURRENT_STATE.md` first — it records exactly what's built, what isn't, and what's been explicitly deferred, so as not to re-derive (or contradict) recent, reviewed decisions.
- **This repo has its own planning/verification methodology** (`forge-docs/`) distinct from ad hoc changes — for anything larger than a small fix, check whether it belongs in that process (an active phase's task list, a new ADR) rather than as a standalone edit.

## 12. Known Gaps / Uncertainty

- **No CI/CD pipeline exists.** All validation described in §8 is manual. If automated CI is expected, it has not been set up in this repository as of this writing.
- **No frontend test framework.** Confirmed both by the absence of any test script/files and by `forge-docs/07_CODING_STANDARDS.md` line 38, which flags it as an open TODO: *"confirm current test tooling/coverage expectations (none observed in the current stack table)... a testing library has not yet been added for the frontend."* Not something to silently "fix" by inventing a framework choice unasked.
- **`docs/FolderStructure.md` is somewhat stale** — it predates several newer backend service subpackages (`knowledge`, `projects`, `model_playground`, `prompt_studio`, `mcp`) and frontend features that exist in the current tree. This handout's §3 reflects the current, verified structure; treat `FolderStructure.md` as directionally correct but not exhaustive.
- **`forge-docs/` vs `docs/` boundary**: `docs/` is the shipped-app reference (how Forge works); `forge-docs/` is this project's own development methodology and phase-by-phase history (why/how it was built, in what order, under what process). Both are real and current, but they answer different questions — check `docs/` first for "how does X work," `forge-docs/` for "what's the plan/status for Y" or "why was Z decided this way."
- **`backend/app/mcp/` is the least stable area.** Two of five planned milestones are implemented as of this writing; the tool surface, scope model, and even some audit-logging behavior have changed at least once already based on adversarial review findings (see `forge-docs/implementation/Phase-11-Claude-MCP/reviews/`). Confirm current state against `CURRENT_STATE.md` in that folder rather than assuming this handout's description stays accurate indefinitely.
- **`.claude/` is gitignored local tooling** (skills, worktrees, session templates) — not part of the shipped repository structure; observed in this working copy but should not be assumed present in a fresh clone.
