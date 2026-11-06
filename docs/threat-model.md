# Threat Model: Secrets Vault

> **Purpose:** Name the assets, trust boundaries, attackers and threats for the Secrets vault, and say plainly which ones the current code handles and which it doesn't.
> **Scope:** The vault (`app/services/secrets/`), the primitives that protect it (`app/core/security.py`), and the auth, backup and MCP paths that can reach it. Mechanism details are in [crypto-design.md](crypto-design.md), and gap IDs (G1–G15) refer to its §9.
> **Status:** Current as of 2026-11-06. This expands the short threat model in [Security.md](Security.md) and doesn't replace it.

---

## 1. System context

- A single-user, self-hosted FastAPI backend on SQLite (`/data/forge.db`, `Settings.database_path`), with a Next.js frontend behind the bundled Nginx (`docker-compose.yml`).
- One operator, who is also the only user. There are no accounts, roles or tenants.
- Forge doesn't terminate TLS itself. The session cookie's `Secure` flag is off by default (`session_cookie_secure=False`, `app/core/config.py`).

## 2. Assets

| ID | Asset | Where it lives |
|---|---|---|
| A1 | Secret plaintext values and metadata (username / url / notes) | Ciphertext in `secrets`, `secret_versions`. Plaintext exists only in process memory during a request. |
| A2 | Provider API keys (Model Playground) | Ciphertext in `provider_credentials.encrypted_api_key` |
| A3 | `FORGE_MASTER_KEY` / derived root key | Env var, `.env`, or the `FORGE_MASTER_KEY_FILE` file. Process memory (`_root_key` lru_cache). |
| A4 | Master password | Typed by the user. Only the Argon2id hash is stored (`app_config.master_password_hash`). |
| A5 | Session cookie `forge_session` | Browser, in transit |
| A6 | MCP bearer tokens | Held by the MCP client. HMAC hash in `mcp_tokens.token_hash`. |
| A7 | Vault metadata: secret names, types, folders, tags, timestamps, activity messages | **Plaintext** in SQLite and in backup JSON |
| A8 | Backup bundle | Downloaded JSON file, wherever the user puts it |

## 3. Trust boundaries

1. **Browser ↔ backend:** HTTP(S), authenticated by the session cookie (`app/api/deps.py::require_auth`).
2. **MCP client ↔ backend:** bearer token, only if `FORGE_MCP_ENABLED=true`. The vault is excluded from the MCP surface.
3. **Backend process ↔ storage:** SQLite file and Docker volume `forge-data`. Assumed readable by anyone who gets the disk or a backup.
4. **Backend process ↔ its environment:** where `FORGE_MASTER_KEY` comes from. Trusted.
5. **Backend ↔ third-party LLM providers:** decrypted provider API keys leave the process here, on purpose, and only to their own provider (see [Security.md](Security.md) "Outbound network calls").

## 4. Attackers in scope

| ID | Attacker | Capability assumed |
|---|---|---|
| X1 | **Data thief** | Has a copy of `forge.db`, a volume snapshot, or a backup JSON. Doesn't have `FORGE_MASTER_KEY`. |
| X2 | **Network attacker on the LAN / path** | Can reach the HTTP port, and can sniff traffic if TLS isn't used |
| X3 | **Malicious web page** in the user's browser | Can make cross-site requests (CSRF-style). Can't read responses without CORS. |
| X4 | **Cookie thief** | Got a `forge_session` value once (shared machine, sniffed HTTP, browser-profile theft) |
| X5 | **Compromised or over-broad MCP client** | Holds a valid MCP token |
| X6 | **DB tamperer** | Has write access to `forge.db` but not to the key or process |

### Out of scope (explicitly not defended)

Taken from [Security.md](Security.md) and confirmed by the design:

- **Host compromise:** root, a shell as the app user, memory dumps, swap, core files, `docker inspect` (which shows the `FORGE_MASTER_KEY` env var). The key and decrypted values are in process memory (G13).
- **Malicious operator.** The operator holds the key by design.
- **Supply-chain compromise** of PyNaCl, libsodium, FastAPI, etc.
- **Multi-user isolation.** There's only one user.

## 5. Threats and current status

Status key: **Mitigated** = the code defends against it. **Partial** = it defends with caveats. **Gap** = it doesn't defend. **Accepted** = left undefended on purpose, with the reason documented.

### T1. X1 steals the database or a backup and wants secret values

- **Mitigation:** values, metadata, versions and provider keys are SecretBox ciphertext (`VaultCrypto`). The key isn't in the DB or the bundle (crypto-design §2.3, §7).
- **Caveats:**
  - Security rests entirely on the entropy of `FORGE_MASTER_KEY`. There's no work factor (G1) and no entropy check (G8), so a guessable key such as `dev-only-key-change-me` from `handout.md` can be brute-forced offline: each guess costs one BLAKE2b hash and one SecretBox open attempt.
  - If the thief also gets `.env` (often on the same host or in the same backup set), everything decrypts. The master password adds no protection here (G5).
- **Status:** **Partial.** Strong with a random 256-bit key, weak otherwise.

### T2. X1 learns what the user stores, without decrypting

- Names, types, folders, tags, timestamps, provider labels and base URLs, and activity log messages (`Revealed "<name>"`) are all plaintext in the DB and the backup (G6).
- **Status:** **Gap.** An attacker learns which services and accounts the user holds credentials for, and when they were used.

### T3. X1 cracks the master password hash offline

- Argon2id at INTERACTIVE limits (G10), with an 8-character minimum and no strength rule (`app/schemas/auth.py`).
- **Impact is limited:** the password isn't the data key. Cracking it gives a login to a *running* instance, not plaintext from the stolen DB. It matters if the user reuses the password elsewhere.
- **Status:** **Partial.**

### T4. X2 brute-forces `/api/auth/unlock`

- Each guess costs an Argon2id verify on the server (about 64 MiB of memory), which slows guessing somewhat. There's no rate limit, lockout or delay (`app/api/routes/auth.py`).
- **Status:** **Accepted** (documented in [Security.md](Security.md) "Things intentionally out of scope"). The mitigation is a deployment step: a rate-limiting reverse proxy or VPN.

### T5. X2 sniffs traffic

- Over plain HTTP, the master password (at unlock), the session cookie, and revealed secret values all cross the network in cleartext. `Secure` is off by default.
- **Status:** **Gap by default.** Mitigated only when the operator deploys TLS and sets `FORGE_SESSION_COOKIE_SECURE=true` ([Deployment.md](Deployment.md)).

### T6. X4 replays a stolen session cookie

- The token is valid until `expiry` (12 h default). `/api/auth/lock` only deletes the browser's copy (G9). There's no server-side session list to revoke one session.
- Full revocation is possible only by changing the master password (which changes the HMAC key) or `FORGE_MASTER_KEY`.
- The token isn't bound to IP, user-agent or a nonce.
- **Status:** **Partial.** HttpOnly blocks JavaScript theft (XSS can't read it), but replay of a copied cookie works.

### T7. X3 makes cross-site requests (CSRF)

- `SameSite=Lax` on the cookie (`session_cookie_kwargs`), so browsers don't send it on cross-site POST/PATCH/DELETE subrequests.
- CORS middleware is added only when `FORGE_CORS_ORIGINS` is set (`app/main.py::create_app`). When it is set, `allow_credentials=True` with `allow_methods=["*"]` and `allow_headers=["*"]` for those origins, so every listed origin must be trusted.
- There's no CSRF token. GET `/api/secrets/{id}?reveal=true` is a state-reading GET. Lax cookies *are* sent on top-level GET navigations, but without CORS the attacking page can't read the response.
- **Status:** **Mitigated for default config** (empty CORS list). Depends on the operator not listing untrusted origins.

### T8. X5 (MCP) exfiltrates vault contents

- No MCP tool imports the secrets service or crypto tools, and a recursive static test enforces this (`tests/test_mcp_tools_static_checks.py`). The `forge:secrets` scope exists but no tool uses it.
- MCP token hashes are HMAC-keyed on the root key (crypto-design §6), so a dumped `mcp_tokens` table can't be checked offline without the key.
- **Status:** **Mitigated** (structural exclusion). Revisit before any vault-touching MCP tool ships.

### T9. X6 tampers with ciphertext in the DB

- Changing bytes inside a blob → Poly1305 rejects it, `CryptoError`, generic 500 (G14). **Detected.**
- Swapping whole blobs between rows or columns (secret A's value into secret B, an old version into the current value, a provider key into a secret) → **decrypts cleanly**, because there's no AAD or row binding (G4).
- Deleting `secret_versions` rows, or editing plaintext columns (names, folder, tags), → not detectable.
- **Status:** **Partial.** Bit-level integrity is protected. Structural integrity isn't.

### T10. Malicious or wrong backup import

- `import_backup` wipes all vault and notes data and inserts whatever the bundle has. It doesn't check the bundle's integrity or whether it decrypts under the current key (G11). Auth is required (`routes/settings.py` uses `AuthDep`), so this needs a session (X4) or the user being tricked into importing a file.
- Same blob-swap issue as T9.
- **Status:** **Gap**. Destructive with no confirmation token or pre-import validation in the backend.

### T11. Root key misconfiguration

- A missing `FORGE_MASTER_KEY_FILE` silently falls back to `FORGE_MASTER_KEY` (G7). An operator who thinks they moved to Docker secrets may still be running on an old or dev env value.
- Losing the key is unrecoverable, and there's no rotation path (G2). Rotating means losing every encrypted value plus all sessions and MCP tokens.
- **Status:** **Gap** (operational).

### T12. Plaintext exposure through logs or responses

- `services/secrets/` has no logging calls. Unhandled exceptions are logged server-side with a generic client message (`app/core/errors.py`).
- Values come back only from `GET /secrets/{id}?reveal=true` and `GET /secrets/{id}/versions/{vid}`. Create and update responses return `value=None` (`routes/secrets.py`).
- Reveal of the current value writes an `ActivityLog` row. Reveal of a historical version does **not** (G12).
- **Status:** **Partial.** No plaintext leak found, but the audit trail is incomplete.

### T13. Crypto tools mistaken for client-side encryption

- `/api/crypto/*` (AES, RSA, ECDSA, JWT) runs on the server. Passphrases, plaintexts and private keys are sent in request bodies, over HTTP unless TLS is set up (crypto-design §8). Generated private keys come back unencrypted.
- These tools don't touch the vault key or vault data.
- **Status:** **Accepted by design**, but users should know that "encrypt with a passphrase" here isn't end-to-end.

## 6. Summary matrix

| Threat | Status | Main gap(s) |
|---|---|---|
| T1 DB/backup theft → values | Partial | G1, G5, G8 |
| T2 DB/backup theft → metadata | Gap | G6 |
| T3 Offline password crack | Partial | G10 |
| T4 Online unlock brute force | Accepted | (no rate limit) |
| T5 Traffic sniffing | Gap by default | Secure cookie off, no TLS in-app |
| T6 Cookie replay | Partial | G9 |
| T7 CSRF | Mitigated (default config) | CORS list must be trusted |
| T8 MCP exfiltration | Mitigated | n/a |
| T9 DB tampering | Partial | G4 |
| T10 Backup import abuse | Gap | G11 |
| T11 Key misconfig / rotation | Gap | G2, G7 |
| T12 Plaintext in logs/audit | Partial | G12 |
| T13 Server-side crypto tools | Accepted | n/a |

## 7. Suggested hardening, roughly by value per effort

These are suggestions, not commitments. None of them is implemented.

1. Refuse to start when `FORGE_MASTER_KEY_FILE` is set but unreadable, and warn on short keys (G7, G8).
2. Add `VaultCrypto` tests for tampered-ciphertext and wrong-key rejection (G15).
3. Log an `ActivityLog` row on version reveal (G12).
4. Derive separate subkeys from the root key for encryption, session HMAC and MCP HMAC (e.g. BLAKE2b with `person=` / `key=`, or HKDF) (G3).
5. Bind ciphertext to its row: move to `crypto_aead_xchacha20poly1305_ietf` with AAD = table/column/row id, and add a version byte to the blob (G4, and prepares for G2).
6. Add a key-rotation command that re-encrypts all rows under a new key (G2).
7. Validate backup bundles before the destructive delete, at least by trial-decrypting one blob (G11).
8. Use a server-side session id (or a per-session nonce plus a revocation list) so Lock really revokes (G9).
9. Consider encrypting secret names and metadata, at the cost of losing SQL `ilike` search (G6).
