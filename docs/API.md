# API

Forge's backend is a documented REST API — interactive docs are always
available at **`/docs`** (Swagger UI) and **`/redoc`**, generated from the
FastAPI route definitions and Pydantic schemas, so this file is a map, not a
full reference.

## Conventions

- All endpoints except `/health`, `/version`, `/api/setup/*`, and
  `/api/auth/*` require a valid session cookie (see
  [Security.md](Security.md)).
- Request/response bodies are JSON except file uploads (`multipart/form-data`
  on `POST /api/ingest/jobs`) and file downloads.
- Errors always come back as:
  ```json
  { "error": { "code": "not_found", "message": "Secret not found", "details": null } }
  ```
  `code` is machine-readable (`not_found`, `unauthorized`, `setup_required`,
  `conflict`, `validation_error`, `app_error`, `internal_error`,
  `http_error`); `message` is human-readable; `details` is present for
  validation errors (a list of Pydantic error objects).
- List endpoints return arrays directly (not wrapped in `{data: [...]}`) —
  there's no pagination yet (see [Roadmap.md](Roadmap.md)).

## Endpoint groups

| Prefix | Covers |
|---|---|
| `/health`, `/version`, `/system/status` | Unauthenticated health/version/storage info |
| `/api/setup`, `/api/auth` | First-run setup, unlock/lock, session check, password change |
| `/api/secrets` | Secrets, folders, tags, version history (`/api/vault` still resolves as a temporary compatibility alias, see [DecisionLog.md](DecisionLog.md)) |
| `/api/generators` | Password/UUID/NanoID/random-bytes/API-key/JWT-secret generation, entropy estimate |
| `/api/crypto` | Base64, hashing, AES-256-GCM, JWT decode/verify/build, RSA, ECDSA |
| `/api/converters` | Cron expression parsing (other converters run client-side) |
| `/api/notes` | Note CRUD + full-text search |
| `/api/documents` | Document CRUD, full-text search, and multi-format export (txt/md/doc/docx/pdf/xml) |
| `/api/ingest` | Document upload → Markdown conversion jobs, preview, save-to-notes |
| `/api/search` | Combined secrets + notes + documents search for the command palette |
| `/api/dashboard` | Aggregated recent activity/notes/secrets/storage for the home page |
| `/api/settings` | Theme, backup export/import, about |

## Example

```bash
# Unlock (stores the session cookie in cookies.txt)
curl -c cookies.txt -X POST http://localhost:8585/api/auth/unlock \
  -H "Content-Type: application/json" \
  -d '{"master_password": "..."}'

# Generate a password
curl -b cookies.txt -X POST http://localhost:8585/api/generators/password \
  -H "Content-Type: application/json" \
  -d '{"length": 24}'
```

## Why no versioned API path (`/api/v1/...`)

Forge's frontend and backend are always deployed together as one unit —
there's no independent third-party API consumer to protect from breaking
changes. If that changes, versioning gets added at that point rather than
speculatively.
