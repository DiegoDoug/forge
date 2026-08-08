# Roadmap

## Known gaps (not implemented, tracked honestly rather than stubbed)

- **PGP** — Crypto currently covers AES-256-GCM, RSA, and ECDSA, but not
  PGP/GPG. A correct implementation needs a real keyring model (not just a
  keypair), which is a meaningfully larger feature than the others; see
  [DecisionLog.md](DecisionLog.md).
- **Pagination** — Secrets and Notes list endpoints return everything in one
  response. Fine at the scale of a personal secrets store; would need
  cursor-based pagination before it's fine at thousands of entries.
- **Nested folders in the Secrets UI** — the backend model supports
  `parent_id` nesting; the sidebar currently renders folders as a flat list.
- **Rate limiting** — see [Security.md](Security.md) for why this is
  currently a deployment-time concern (VPN/reverse-proxy) rather than
  built in.
- **`/system/status` is unreachable in production** — 🟡 MAJOR, found
  2026-08-06 during the Phase 09 audit and confirmed at runtime. The backend
  serves `GET /system/status` (`app/api/routes/health.py`) mounted at the
  root, without the `/api` prefix. But `docker/nginx.conf` proxies only
  `/api/` and `/health`, so the request falls through to the frontend and
  returns a 404 with an HTML body. The Settings → About card's storage row
  has therefore never rendered in a production deployment.

  Phase 09 fixed the *development* path by adding a rewrite to
  `frontend/next.config.ts`. It deliberately did **not** touch
  `docker/nginx.conf`, which is inspect-only under that phase's contract.

  **The fix, approved 2026-08-06:** mirror the existing `/health` block in
  `docker/nginx.conf`:

  ```nginx
  location /system/status {
      proxy_pass http://backend:8000/system/status;
  }
  ```

  Deliberately *not* fixed by repointing Settings at `/api/workbench`, which
  returns an identical `storage` object today. That would couple Settings to
  an endpoint whose primary responsibility is something else, and the two
  payloads are only incidentally identical — they can drift. The
  misconfiguration is in nginx; the frontend architecture is correct and
  stays as it is. See
  [`../forge-docs/implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md`](../forge-docs/implementation/Phase-09-Frontend-Reimagine/00_AUDIT.md)
  §3.2.

## Near-term

- Command palette: deep-link results (secrets/notes) currently navigate to
  the feature page with a `?open=` query param; extending this pattern to
  generators/converters/utilities (e.g. "jump straight to the JWT tool with
  a token pre-filled") is straightforward but not done.
- Export/import for individual Notes (Markdown file, not just full-instance
  backup).
- Hash Compare as a standalone Utilities tool (currently covered by the
  "verify" mode of the Crypto Hash tool).

## Explicitly not planned

- Multi-user / RBAC — Forge is single-tenant by design (see
  [Security.md](Security.md)). Multi-user support would change the auth
  model fundamentally, not extend it.
- Kubernetes manifests — Docker Compose is the deployment target; see
  [Architecture.md](Architecture.md) for why a modular monolith doesn't need
  orchestration at this scale.
