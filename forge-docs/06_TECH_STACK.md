# 06 — Tech Stack

> **Purpose:** Canonical, current list of every technology Forge depends on, so future phases add to it deliberately rather than by accident.
> **Scope:** Runtime and build-time dependencies. Coding conventions for using them live in [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md).
> **Ownership:** TODO — assign a tech-stack owner (typically the lead maintainer).
> **Status:** Current as of last dependency read — re-verify against `package.json` / `requirements.txt` before trusting for a new phase's dependency decisions.
> **Last Updated:** 2026-07-20

---

## 1. Frontend

| Layer | Choice | Notes |
|---|---|---|
| Framework | Next.js 15 (App Router, Turbopack) | `next dev --turbopack` / `next build --turbopack` |
| UI runtime | React 19 | |
| Language | TypeScript | |
| Component library | shadcn/ui on `@base-ui/react` | style `base-nova`, see [05_DESIGN_SYSTEM.md](05_DESIGN_SYSTEM.md) |
| Styling | Tailwind CSS v4 (`@tailwindcss/postcss`) | + `tailwind-merge`, `tw-animate-css`, `@tailwindcss/typography` |
| Data fetching / cache | TanStack Query v5 | + devtools in development |
| Forms & validation | `react-hook-form` + `zod` + `@hookform/resolvers` | |
| Drag & drop | `@dnd-kit/core`, `/sortable`, `/modifiers` | powers the Notes board |
| Code editor | `@monaco-editor/react` | |
| Command palette | `cmdk` | ⌘K global palette |
| Animation | `framer-motion` | |
| Markdown | `react-markdown` + `remark-gfm` | |
| Diffing | `diff` | powers the diff viewer converter |
| Data formats | `yaml`, `papaparse`, `fast-xml-parser` | YAML/CSV/XML converters |
| QR codes | `qrcode.react` | |
| Theming | `next-themes` | light/dark |
| Toasts | `sonner` | |
| Icons | `lucide-react` | |
| Dates | `date-fns` | |

## 2. Backend

| Layer | Choice | Notes |
|---|---|---|
| Framework | FastAPI | `uvicorn[standard]` ASGI server |
| Validation | Pydantic v2 + `pydantic-settings` | |
| ORM / models | SQLModel | single source of truth for schema |
| Database | SQLite via `aiosqlite` | one file, no external DB server |
| Migrations | Alembic | explicit after the initial migration |
| Auth / crypto | `pynacl`, `cryptography`, `pyjwt` | encryption at rest, session signing, JWT tools |
| Cron parsing | `croniter` | powers the cron converter |
| QR generation | `qrcode[pil]` | |
| Document conversion | `markitdown[all]` | Ingest pipeline (ported project) |
| Document export | `python-docx`, `beautifulsoup4`, `markdownify`, `reportlab` | Documents tab export formats |
| Optional vision-LLM | `openai`, `pymupdf` | disabled unless configured — see [`../docs/Security.md`](../docs/Security.md) |

## 3. Infrastructure

| Layer | Choice | Notes |
|---|---|---|
| Containerization | Docker + Docker Compose | single `docker compose up --build` |
| Reverse proxy | Nginx | production only; `docker/nginx.conf` |
| Dev proxy | Next.js rewrites | development only, avoids CORS |

## 4. Adding a new dependency

Before adding anything to this stack for a new phase:

- [ ] Confirm it has no hard runtime dependency on external network access (violates [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md) §1.2) unless the feature is explicitly optional/cloud-assisted.
- [ ] Confirm it doesn't duplicate an existing dependency's job (e.g. don't add a second HTTP client, a second form library, a second date library).
- [ ] Add it to the table above in the same PR that introduces it.
- [ ] If it's a new *category* of dependency (e.g. an LLM provider SDK for Model Playground/Prompt Studio), record the decision in [`decisions/README.md`](decisions/README.md).

## 5. Anticipated additions (not yet added — TODO)

- [ ] TODO: LLM provider SDK(s) for Model Playground / Prompt Studio (Phase 03, 05) — provider(s) not yet chosen.
- [ ] TODO: Confirm whether Universal Converter (Phase 04) needs any new format libraries beyond what Converters/Ingest already cover.

## 6. Cross-references

- [03_ARCHITECTURE.md](03_ARCHITECTURE.md)
- [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md)
- [../frontend/package.json](../frontend/package.json)
- [../backend/requirements.txt](../backend/requirements.txt)
- [decisions/README.md](decisions/README.md)
