# Security

## Threat model

Forge assumes:

- A single trusted operator/user per instance (no multi-tenancy, no RBAC).
- The primary risk is **database or backup theft** — someone getting a copy
  of `forge.db` or a JSON backup export without also having
  `FORGE_MASTER_KEY`.
- The secondary risk is **unauthorized network access** to a running
  instance (someone on the same LAN, or the internet if misconfigured).

It does **not** defend against a compromised host (root access, memory
dumps) or a malicious operator — at that point the master key and an
unlocked session are both available in-process anyway.

## Encryption at rest

Secret values and metadata are encrypted with **PyNaCl's SecretBox**
(XSalsa20-Poly1305, authenticated) before they're written to SQLite. The key
is derived from `FORGE_MASTER_KEY` via BLAKE2b (`app/core/security.py`) —
any string works, but a high-entropy random value
(`openssl rand -base64 32`) is what you should actually use.

The key **never touches the database**. It lives only in the backend
process's environment. This is the whole point: a stolen `forge.db` file (or
a stolen JSON backup export) is ciphertext without it.

`SecretVersion` rows (edit history) are encrypted the same way — old values
aren't recoverable without the same key, and deleting a secret's versions
happens via normal cascade delete, not a separate "purge" step.

## Authentication

Single-user, password-gated:

1. First run: **Settings-free setup flow** (`/setup`) hashes a
   user-chosen master password with **Argon2id** (via `nacl.pwhash`) and
   stores only the hash (`AppConfig.master_password_hash`).
2. Unlocking (`/unlock`) verifies the password against that hash and issues
   a session token: `"<expiry>.<hmac>"`, HMAC-SHA256-signed with a key
   derived from `FORGE_MASTER_KEY` + the current password hash
   (`issue_session_token` / `verify_session_token`).
3. The token is set as an **httpOnly, SameSite=Lax** cookie. It's stateless
   — there's no server-side session table — so changing the master password
   invalidates every existing session for free (the HMAC key changes).

Every API route except `/health`, `/version`, `/api/setup/*`, and
`/api/auth/*` requires a valid session (`AuthDep` in `app/api/deps.py`).

### Why not just rely on `FORGE_MASTER_KEY` for login?

Because it's meant to be a long-lived infrastructure secret (set once in
`.env`, rarely typed), not something you enter to unlock the UI daily. The
master password is the day-to-day credential; `FORGE_MASTER_KEY` is what
makes stolen data useless without it.

## Transport security

Forge doesn't terminate TLS itself — see [Deployment.md](Deployment.md).
`FORGE_SESSION_COOKIE_SECURE` defaults to `false` so plain-HTTP LAN
deployments aren't silently broken (a `Secure` cookie is dropped by browsers
on non-HTTPS origins); set it to `true` once you're behind TLS.

## Input handling

- All request bodies are validated through Pydantic schemas — nothing
  reaches a service function unvalidated.
- Uploaded filenames (Ingest) are sanitized (`_safe_name` in
  `app/api/routes/ingest.py`): directory components stripped, unsafe
  characters replaced, length-capped.
- File uploads are size- and count-capped (`FORGE_MAX_UPLOAD_FILE_SIZE_MB`,
  `FORGE_MAX_UPLOAD_BATCH_FILES` via `app/core/config.py`).
- Errors never leak stack traces or internals to the client — the global
  exception handler (`app/core/errors.py`) logs the full exception
  server-side and returns a generic `internal_error` envelope.

## Things intentionally out of scope

- **CSRF tokens**: the session cookie is `SameSite=Lax`, and every
  state-changing endpoint requires `Content-Type: application/json`, which
  browsers won't send cross-site without a preflight that Forge doesn't
  answer permissively (no CORS headers in production, since frontend and
  backend are same-origin behind Nginx). This is standard protection for a
  same-origin single-page app; a dedicated CSRF token was judged unnecessary
  complexity for a single-user tool with no cross-origin API consumers by
  default.
- **Rate limiting / brute-force lockout** on `/api/auth/unlock`: this is a
  self-hosted, typically LAN-only or single-operator tool. If you expose it
  to the internet, put it behind a reverse proxy that rate-limits, or use a
  VPN (Tailscale, WireGuard) instead.
- **PGP**: evaluated for the Crypto tools and deliberately left out rather
  than shipped half-working — see [DecisionLog.md](DecisionLog.md).
