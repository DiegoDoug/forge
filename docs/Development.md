# Development

## Prerequisites

- Python 3.12+
- Node.js 20+
- `ffmpeg` on your PATH (audio transcription in Ingest)

## Backend

```bash
cd backend
python -m venv .venv
./.venv/Scripts/activate   # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

# Required: a root key. Any string works locally — it's stretched into a
# proper key — but use a real random one outside local dev.
export FORGE_MASTER_KEY="dev-only-key-change-me"
export FORGE_DATA_DIR=./.dev-data

python -m uvicorn app.main:app --reload --port 8000
```

Migrations run automatically on startup (`alembic upgrade head`, invoked from
`app/main.py`'s lifespan). To create a new migration after changing a model
in `app/models/`:

```bash
alembic revision --autogenerate -m "add foo column"
```

Review the generated migration before committing — autogenerate is a
starting point, not a guarantee, especially for SQLite (limited `ALTER
TABLE` support means many changes need `batch_alter_table`, which
`render_as_batch=True` in `alembic/env.py` already handles).

## Frontend

```bash
cd frontend
npm install
npm run dev
```

By default this proxies `/api/*` to `http://localhost:8000` (see
`next.config.ts`). Point it elsewhere with `BACKEND_INTERNAL_URL`.

The frontend dev server and `npm run build` **must not run at the same
time** — both write to `.next/`, and running them concurrently corrupts the
build cache (you'll see `ENOENT ... _buildManifest.js.tmp` errors). Stop the
dev server before running a production build.

## Adding a shadcn/ui component

```bash
cd frontend
npx shadcn@latest add <component>
```

This project's shadcn setup uses **Base UI** (not Radix) under the hood.
Two API differences worth knowing before copying patterns from Radix-based
shadcn examples:

- Composition uses `render={<Element />}` instead of `asChild`:
  ```tsx
  <DialogTrigger render={<Button variant="outline" />}>Open</DialogTrigger>
  ```
- `onValueChange` on `Select`/`Tabs`-style components is typed
  `(value: string | null, ...) => void` (nullable), not
  `(value: string) => void` — guard before passing directly to a
  `Dispatch<SetStateAction<string>>`.

## Adding a feature

See [Contributing.md](Contributing.md) for the standard shape of a new
feature (backend service + schema + route, frontend `api.ts` + page).

## Running both together

There's no dev-mode Docker Compose profile — run `uvicorn --reload` and
`npm run dev` directly, side by side. Docker Compose is for the production
build only (see [Deployment.md](Deployment.md)).
