# Deployment

## Docker Compose (recommended)

```bash
cp .env.example .env
# edit .env: set FORGE_MASTER_KEY
docker compose up --build -d
```

This starts three containers — `backend`, `frontend`, `nginx` — and one
named volume, `forge-data`, mounted at `/data` in the backend container. It
holds the SQLite database, uploaded-file scratch space, and Ingest job
artifacts. Everything else is stateless and can be recreated freely.

Forge is served on `http://localhost:${FORGE_PORT:-8585}`.

## Required configuration

`FORGE_MASTER_KEY` is the only required setting. Generate one with:

```bash
openssl rand -base64 32
```

This key encrypts every vault secret at rest and signs session cookies. It
never touches the database — losing it means losing access to every stored
secret, with no recovery path. Treat it like a root password: store it in a
password manager or your infrastructure's secret store, not just in `.env`
on the host.

## Docker Secrets

For orchestrators that support secret files (Swarm, some Compose setups),
set `FORGE_MASTER_KEY_FILE` to a path instead of `FORGE_MASTER_KEY` directly
— the file's contents win over the environment variable if both are set.

## TLS

Forge itself doesn't terminate TLS. Put it behind a reverse proxy that does
(Caddy, Traefik, Nginx Proxy Manager, Cloudflare Tunnel, Tailscale) and once
traffic is HTTPS end-to-end, set:

```
FORGE_SESSION_COOKIE_SECURE=true
```

Leaving this `false` (the default) over plain HTTP is intentional — a
`Secure` cookie is silently dropped by browsers on non-HTTPS origins, which
would otherwise brick login for the common "just run it on my LAN" case.

## Backups

Two options, both accessible from **Settings → Backup** in the UI:

- **Application-level export**: a JSON bundle of folders/tags/secrets
  (still encrypted — useless without `FORGE_MASTER_KEY`) and notes. Safe to
  store anywhere; doesn't touch the live database file.
- **Volume-level backup**: snapshot the `forge-data` volume directly
  (`docker run --rm -v forge-data:/data -v $(pwd):/backup alpine tar czf
  /backup/forge-data.tgz /data`) while the backend is stopped, for a
  full point-in-time copy including anything outside the app-level export.

## Vision-assisted Ingest (optional)

Off by default. Enabling it lets Ingest use a vision-capable LLM to caption
images and transcribe scanned/image-only PDFs, which MarkItDown's
text-extraction-only pipeline otherwise returns empty for. Uses the OpenAI
client interface, so any OpenAI-compatible endpoint works.

```
FORGE_VISION_ENABLED=1
FORGE_VISION_API_KEY=sk-...
FORGE_VISION_BASE_URL=            # blank = OpenAI; set for Azure/OpenRouter/local vLLM
```

Any failure (bad key, rate limit, timeout) falls back to the normal
MarkItDown output rather than failing the conversion.

## Updating

```bash
git pull
docker compose up --build -d
```

Migrations run automatically on backend startup — there's no separate
migration step.

## Health checks

Both `backend` and `frontend` containers define a `HEALTHCHECK`
(`/health` and `/` respectively). `docker compose ps` reflects their status;
`frontend` and `nginx` wait for `backend` to report healthy before starting.
