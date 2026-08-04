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

## Outbound network calls

Forge is self-hosted-first (see [`../forge-docs/01_PRODUCT_PRINCIPLES.md`](../forge-docs/01_PRODUCT_PRINCIPLES.md) §1.2) — every feature must work with zero internet access, and any feature that calls out to a third-party service must be opt-in and degrade to "disabled," never to a broken app.

Two features currently make outbound calls, both to third-party LLM providers:

- **Ingest's optional vision-LLM path** (`app/services/ingest/vision.py`). A single API key, configured once via `FORGE_VISION_API_KEY` (an environment variable, never touched by the UI or stored in the database). Disabled unless both `FORGE_VISION_ENABLED=1` and a key are set. What leaves the instance: image bytes / PDF page renders and a fixed transcription prompt, sent to whatever `base_url` is configured (OpenAI by default, or any OpenAI-compatible endpoint).
- **Model Playground** (`app/services/model_playground/`, see [`../forge-docs/implementation/Phase-05-Model-Playground/`](../forge-docs/implementation/Phase-05-Model-Playground/)). Unlike Ingest's vision path, this feature is UI-configurable: a user adds a per-provider API key from the Model Playground page itself, no redeploy required. Providers: OpenAI, Anthropic, DeepSeek, Kimi (Moonshot), GLM (Zhipu), Gemini, and a user-configurable "Custom (OpenAI-compatible)" endpoint (ADR-0012, extended by [ADR-0013](../forge-docs/decisions/0013-model-playground-deepseek-and-openai-compatible-providers.md)). What leaves the instance: the prompt text the user submits, sent to whichever provider(s)/model(s) they selected for that run (plus a fixed one-word test prompt for the connection-test endpoint, §"Connection test" below).
- **Projects' AI quick-run** (`app/services/projects/service.py::run_project_prompt`, Phase 06, see [ADR-0014](../forge-docs/decisions/0014-project-data-model-shape.md)) is not a third outbound-call implementation — it stores a project's default provider/model as plain strings (never a credential) and calls Model Playground's own `runs.create_run()` directly for the actual network call. Same credential lookup, same adapters, same timeout/error handling as above; Projects adds zero new outbound-call code paths.

Rules that apply to both, and to any future outbound-call feature:

- **Never sent, regardless of feature:** `FORGE_MASTER_KEY`, the master password or its hash, any Secrets/Vault value, or one provider's API key when calling a different provider.
- **Opt-in, not on-by-default:** with no key configured, the feature is simply absent/disabled — the rest of the app functions normally (per [`../forge-docs/01_PRODUCT_PRINCIPLES.md`](../forge-docs/01_PRODUCT_PRINCIPLES.md) §1.2).
- **Credential storage:** provider API keys are encrypted at rest with the same `VaultCrypto` primitive (`app/core/security.py`) Secrets uses, decrypted only in-memory at the moment of the outbound call, and never echoed back by any API response after creation (write-only, like a password field) — see [ADR-0011](../forge-docs/decisions/0011-model-playground-provider-credential-security.md) for the full design rationale. This does not extend to a credential's `base_url` (Custom provider only) — that's an endpoint address, not a secret, and is safely echoed back so the UI can show what's configured.
- **Failure isolation:** every outbound call has a hard timeout (60s for a run, 20s for a connection test) and a provider failure/timeout produces a user-legible, per-call error — never a stack trace, and never one provider's failure blocking or corrupting another's result in the same operation.

### Connection test

`POST /api/model-playground/providers/test-connection` lets a user validate a provider/API key/base URL/model combination before saving it. It's stateless: the request body carries a not-yet-saved API key (and, for the Custom provider, a not-yet-saved `base_url`), makes exactly one real outbound call through the same adapter path a run would use, and returns success/failure — nothing is written to the database, and neither the key nor the raw provider exception text is ever logged or returned (same `to_user_message` mapping runs use).

### `base_url` and SSRF

The Custom (OpenAI-compatible) provider accepts a user-supplied `base_url`, validated only for well-formedness (`http://`/`https://` scheme, non-empty, length-capped) — no allowlist of hosts or IP ranges is enforced. This is a deliberate decision, not an oversight: Forge's threat model above already establishes that the operator configuring this value is the same trusted, single operator the whole instance defends around (not a lower-trust multi-tenant user pivoting the server's network position), and Forge already has a live precedent for exactly this input shape — `FORGE_VISION_BASE_URL` — which is equally unrestricted and explicitly intended to support pointing at self-hosted/local OpenAI-compatible servers (Ollama, vLLM, LM Studio, etc.), a legitimate use case that a private-IP/loopback block would break. See [ADR-0013](../forge-docs/decisions/0013-model-playground-deepseek-and-openai-compatible-providers.md) §4 for the full assessment; if Forge's threat model ever changes (e.g. multi-tenancy is added), this decision must be revisited.

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
