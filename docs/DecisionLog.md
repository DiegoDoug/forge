# Decision log

Notable decisions and why, especially where they deviate from or add detail
beyond the original project brief.

## Modular monolith over microservices

The brief called for this explicitly; noted here because it's worth stating
*why* it still holds even as features accumulate: every feature shares one
database, one auth session, and one deploy lifecycle. Splitting Vault into
its own service would mean either duplicating auth or building
service-to-service auth for zero user-facing benefit. Revisit only if a
feature genuinely needs independent scaling or a different runtime.

## Session cookie `Secure` flag defaults to `false`

Found via live testing, not designed upfront: the first working version
defaulted `secure=(environment == "production")`, which is the textbook
choice — and it silently broke login, because a `Secure` cookie is dropped
by browsers on plain-HTTP origins, and Forge's default deployment (LAN,
self-hosted, no TLS) is exactly that. Changed to an explicit
`FORGE_SESSION_COOKIE_SECURE` flag, default `false`, documented in
[Security.md](Security.md) and [Deployment.md](Deployment.md). This is the
kind of bug that only shows up when you actually drive the auth flow
end-to-end rather than trust the code by inspection.

## Master password (Argon2id hash) separate from `FORGE_MASTER_KEY`

The brief mentions both "Master key: FORGE_MASTER_KEY" and a "Master
Password" setting without specifying the relationship. Design chosen: they
serve different purposes and are deliberately independent —
`FORGE_MASTER_KEY` is an infrastructure secret (encrypts data at rest, set
once via env/Docker secret) and the master password is the day-to-day login
credential (Argon2id-hashed, changeable without re-encrypting the vault).
Bitwarden-style separation: losing the login password doesn't have to mean
losing the data, and rotating the login password doesn't require decrypting
and re-encrypting every secret.

## Alembic's initial migration builds tables from `SQLModel.metadata`

Normally an anti-pattern (migrations should be explicit, reviewable DDL),
but justified for exactly one migration: the *first* one, where the models
already are the reviewable source of truth and hand-transcribing ~10 tables
into `op.create_table()` calls would be pure duplication with no safety
benefit. Every migration after `0001` is a normal explicit revision — see
[Database.md](Database.md).

## SQLite FTS5 for Notes, plain `LIKE` for Vault names

Notes content is exactly the kind of unstructured text FTS5 is for.
Vault secret *values* are never indexed in any form (they're encrypted, and
indexing plaintext defeats the point); vault secret *names* are short enough
that a `LIKE` scan is fine and avoids maintaining a second FTS index with
its own trigger set for marginal benefit.

## Ingest is ported, not rewritten — and not persisted to the database

The brief was explicit: study the existing project, reuse its code, don't
rewrite it. `app/services/ingest/{jobs,converter,postprocess,vision}.py` are
close ports of the standalone Ingest project's modules, adapted only to
read from Forge's central `Settings` instead of their own `config.py`. Job
state stays in-memory with TTL cleanup (unchanged from upstream) rather than
moving to the database — uploads and converted output are scratch data by
design (self-cleaning was a stated feature of the original), unlike vault
secrets and notes, which are meant to persist indefinitely.

## PGP left out rather than shipped partial

Crypto tools cover AES-256-GCM, RSA-OAEP, ECDSA, and JWT — all backed by the
`cryptography` library's well-audited primitives, each independently
testable and complete. PGP is a different shape of problem (a keyring model,
not just a keypair; ASCII-armor; compatibility with GnuPG's format
expectations) that would either be shipped shallow (encrypt/decrypt with a
single keypair, no keyring, technically "PGP-flavored" but not
interoperable with real PGP tooling) or would need meaningfully more scope
than the rest of Crypto combined. Left out and tracked in
[Roadmap.md](Roadmap.md) rather than shipped as something that looks
complete but isn't.

## Nginx included despite being marked optional in the brief

Chosen because it directly serves the brief's own "docker compose up
--build... open http://localhost:PORT, that's it" requirement: one exposed
port instead of two, and a natural place to add TLS later without touching
the app containers. In dev (no Nginx), the frontend's own Next.js rewrites
do the same job, so the routing logic isn't duplicated conceptually — just
implemented twice for the two different deployment shapes.

## Generators run server-side, not in the browser

`crypto.getRandomValues` would work fine for most of these client-side. Kept
server-side instead for one reason: consistency. Every generator hits the
same `services/generators/service.py`, tested once, with one CSPRNG source
(`secrets`/`os.urandom`), rather than duplicating "is this actually
cryptographically random" reasoning across a Python implementation and a
JS one. Converters/Utilities that don't touch secrets or randomness (JSON
formatting, regex testing, color conversion, checksums via Web Crypto) run
client-side instead, where a network round-trip would only add latency for
no security benefit.
