# Roadmap

## Known gaps (not implemented, tracked honestly rather than stubbed)

- **PGP** — Crypto currently covers AES-256-GCM, RSA, and ECDSA, but not
  PGP/GPG. A correct implementation needs a real keyring model (not just a
  keypair), which is a meaningfully larger feature than the others; see
  [DecisionLog.md](DecisionLog.md).
- **YAML / XML / CSV converters** — JSON, regex, URL, Unicode, cron, diff,
  and timestamp converters are in; YAML↔JSON, XML↔JSON, and CSV↔JSON are
  not yet. Same shape as the JSON tool once added (see
  [Contributing.md](Contributing.md)).
- **Pagination** — Vault and Notes list endpoints return everything in one
  response. Fine at the scale of a personal vault; would need cursor-based
  pagination before it's fine at thousands of entries.
- **Nested folders in the Vault UI** — the backend model supports
  `parent_id` nesting; the sidebar currently renders folders as a flat list.
- **Rate limiting** — see [Security.md](Security.md) for why this is
  currently a deployment-time concern (VPN/reverse-proxy) rather than
  built in.

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
