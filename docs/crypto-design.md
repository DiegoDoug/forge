# Crypto Design: Secrets Vault

> **Purpose:** Describe exactly what cryptography protects the Secrets vault (and the credentials that share its primitive), as implemented today.
> **Scope:** `backend/app/core/security.py`, `backend/app/core/config.py`, `backend/app/services/secrets/`, `backend/app/services/settings/`, `backend/app/services/model_playground/credentials.py`, `backend/app/services/mcp/tokens.py`. The user-facing Crypto *tools* (`backend/app/services/crypto/service.py`) are covered in §8 only to show they are separate.
> **Status:** Current as of 2026-11-06. Every statement cites code; if the code changes, update this file.
> **Companion:** [threat-model.md](threat-model.md). [Security.md](Security.md) gives the higher-level summary.

---

## 1. Summary

| Concern | What the code does | Where |
|---|---|---|
| Root key source | Operator-supplied string `FORGE_MASTER_KEY`, or file contents of `FORGE_MASTER_KEY_FILE` | `Settings.resolved_master_key`, `app/core/config.py` |
| Root key derivation | One pass of unkeyed, unsalted BLAKE2b with a 32-byte digest. **No key stretching.** | `_derive_key`, `app/core/security.py` |
| Cipher (vault at rest) | PyNaCl `SecretBox` = XSalsa20-Poly1305 (authenticated encryption), random 24-byte nonce per encryption | `VaultCrypto.encrypt` / `decrypt` |
| What is encrypted | Secret value, secret metadata (username / url / notes), every historical version, Model Playground provider API keys | `services/secrets/service.py`, `services/model_playground/credentials.py` |
| Master password | Argon2id via `nacl.pwhash.argon2id.str` at PyNaCl default (INTERACTIVE) limits; only the hash is stored | `hash_master_password` / `verify_master_password` |
| Session tokens | `"<expiry>.<hex HMAC-SHA256>"`, keyed with BLAKE2b(root key ‖ password hash) | `issue_session_token` / `verify_session_token` |
| MCP bearer tokens | `secrets.token_urlsafe(32)`, stored as HMAC-SHA256(root key, token) | `generate_mcp_token` / `hash_mcp_token` |

Libraries, from `backend/requirements.txt`: `pynacl>=1.5,<2` (libsodium bindings) for everything above; `cryptography>=42,<44` and `pyjwt>=2.9,<3` are used only by the Crypto tools (§8).

The **master password does not encrypt anything.** It only decides whether a browser gets a session. All at-rest encryption is keyed only by `FORGE_MASTER_KEY`.

---

## 2. Root key: source and storage

### 2.1 Loading (`app/core/config.py`)

- `Settings` is a `pydantic_settings.BaseSettings` with `env_prefix="FORGE_"` and `env_file=".env"`. So `master_key` comes from the `FORGE_MASTER_KEY` env var or a `.env` file in the working directory.
- `Settings.resolved_master_key` returns `_read_secret_file(master_key_file) or master_key`. `_read_secret_file` reads the file as UTF-8 and calls `.strip()` on it.
  - If `FORGE_MASTER_KEY_FILE` is set but the path **doesn't exist or isn't a regular file**, `_read_secret_file` returns `None` and the code **silently falls back** to `FORGE_MASTER_KEY`. No warning is logged.
  - If neither is set, it raises `RuntimeError` with instructions to generate one with `openssl rand -base64 32`.
- `docker-compose.yml` passes the key as an environment variable: `FORGE_MASTER_KEY: "${FORGE_MASTER_KEY:?...}"`, so Compose refuses to start without it.
- Format isn't validated. Any non-empty string is accepted, including short or low-entropy ones. `backend/tests/conftest.py` uses `"test-only-master-key-do-not-use-in-prod"`.

### 2.2 Derivation (`app/core/security.py`)

```python
def _derive_key(secret: str) -> bytes:
    return hashlib.blake2b(secret.encode("utf-8"), digest_size=nacl.secret.SecretBox.KEY_SIZE).digest()

@lru_cache
def _root_key() -> bytes:
    return _derive_key(get_settings().resolved_master_key)
```

- `SecretBox.KEY_SIZE` is 32 bytes, so the root key is BLAKE2b-256(UTF-8 of the master key string).
- **No salt, no personalization, no work factor.** This is a hash, not a password KDF. The module docstring and `config.py` comment both call it "stretched". That's inaccurate: BLAKE2b compresses the string to a fixed length but adds no brute-force cost. The design is only sound if `FORGE_MASTER_KEY` already has high entropy (the documented `openssl rand -base64 32` gives about 256 bits).
- `_root_key()` is `@lru_cache`d, so the key is derived once per process and held as a Python `bytes` object for the life of the process. Nothing zeroes it.
- The same 32-byte root key is used directly for three purposes (no domain-separated subkeys):
  1. the SecretBox key (§3),
  2. input to the session-token HMAC key (§5),
  3. the HMAC key for MCP token hashes (§6).

### 2.3 Where the key is *not*

- It's not written to the database. No model has a column for it. `AppConfig` (`app/models/app_config.py`) stores only `master_password_hash`.
- It's not in backup exports (`services/settings/backup.py` serializes only ciphertext, base64-encoded).

---

## 3. Cipher: `VaultCrypto` (`app/core/security.py`)

```python
class VaultCrypto:
    def __init__(self) -> None:
        self._box = nacl.secret.SecretBox(_root_key())

    def encrypt(self, plaintext: bytes) -> bytes:
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        return self._box.encrypt(plaintext, nonce)

    def decrypt(self, blob: bytes) -> bytes:
        return self._box.decrypt(blob)
```

- **Algorithm:** libsodium `crypto_secretbox`, i.e. XSalsa20 stream cipher + Poly1305 MAC (encrypt-then-MAC, authenticated).
- **Nonce:** 24 random bytes from `nacl.utils.random` (libsodium `randombytes_buf`, the OS CSPRNG), fresh on every call. XSalsa20's 192-bit nonce makes random nonces safe at any realistic volume. `tests/test_security.py::test_vault_crypto_ciphertext_is_nondeterministic` checks that two encryptions of the same plaintext differ.
- **Stored format:** `SecretBox.encrypt(plaintext, nonce)` returns `nonce (24 B) ‖ MAC (16 B) ‖ ciphertext`. That whole blob goes into the `bytes` column as-is. **No version byte or key identifier** is in the blob.
- **No associated data.** SecretBox has no AAD parameter, and the code doesn't bind the ciphertext to its row id, column, or secret id (see §9, gap G4).
- **Decryption failure:** `SecretBox.decrypt` raises `nacl.exceptions.CryptoError` on a MAC mismatch. Nothing in `services/secrets/` catches it, so it reaches the catch-all `Exception` handler in `app/core/errors.py::register_exception_handlers`, which returns a generic 500 `internal_error`.
- `get_vault_crypto()` is also `@lru_cache`d: one `VaultCrypto` (and one `SecretBox`) per process.
- String helpers: `encrypt_str` / `decrypt_str` UTF-8 encode/decode around the above.

### 3.1 What goes through `VaultCrypto`

| Data | Column | Code path |
|---|---|---|
| Secret value | `secrets.encrypted_value` | `services/secrets/service.py::create_secret`, `update_secret` |
| Secret metadata (`SecretMetadata`: `username`, `url`, `notes`) serialized as JSON | `secrets.encrypted_metadata` | `_encrypt_metadata` / `_decrypt_metadata` |
| Historical values | `secret_versions.encrypted_value` | `create_secret` writes the first version. `update_secret` copies the *previous* ciphertext into a new `SecretVersion` before replacing the value. |
| Model Playground provider API keys | `provider_credentials.encrypted_api_key` | `services/model_playground/credentials.py::create_or_replace_credential`, `decrypt_api_key` |

### 3.2 What is *not* encrypted (stored in plaintext in SQLite)

From `app/models/secrets.py` and `app/models/model_playground.py`:

- `secrets.name`, `type`, `folder_id`, `project_id`, `favorite`, `created_at`, `updated_at`
- `secret_versions.created_at` and the `secret_id` link
- all of `folders` (name, hierarchy) and `tags` (name, color), plus `secret_tag_links`
- `provider_credentials.provider`, `label`, `base_url`
- `activity_log` messages, which embed the secret name (e.g. `Revealed "<name>"` in `get_secret`)

`list_secrets` searches by `Secret.name.ilike(...)` in SQL, which only works because names are plaintext.

---

## 4. Master password (Argon2id)

`app/core/security.py`:

```python
def hash_master_password(password: str) -> str:
    return nacl.pwhash.argon2id.str(password.encode("utf-8")).decode("ascii")

def verify_master_password(password: str, password_hash: str) -> bool:
    try:
        return nacl.pwhash.verify(password_hash.encode("ascii"), password.encode("utf-8"))
    except nacl.exceptions.InvalidkeyError:
        return False
```

- `argon2id.str` is called with no explicit limits, so it uses PyNaCl's defaults `OPSLIMIT_INTERACTIVE` / `MEMLIMIT_INTERACTIVE` (confirmed in the installed `nacl/pwhash/argon2id.py`). libsodium defines these as opslimit 2, memlimit 64 MiB. Those are libsodium's own constants, not something Forge configures.
- The output is a self-describing PHC-style string (`$argon2id$v=19$m=...,t=...,p=...$salt$hash`) with a random salt chosen by libsodium. It's stored in `AppConfig.master_password_hash`.
- `nacl.pwhash.verify` reads the algorithm and parameters from the stored string, so raising the limits later would still verify old hashes.
- Length rules (`app/schemas/auth.py`): `min_length=8`, `max_length=256` for setup, unlock and change. There's no other strength check.
- Flow (`app/services/settings/service.py`):
  - `complete_setup` hashes and stores the password, and refuses (`ConflictError`) once a hash exists.
  - `verify_unlock` calls `verify_master_password`.
  - `change_master_password` verifies the current password, then replaces the hash. **No ciphertext is re-encrypted**, because the password isn't part of the data key.
- No rate limiting or lockout on `/api/auth/unlock` (`app/api/routes/auth.py`). [Security.md](Security.md) lists this as intentionally out of scope.

---

## 5. Session tokens

`app/core/security.py`:

```python
def _session_secret(password_hash: str) -> bytes:
    return hashlib.blake2b(_root_key() + password_hash.encode("utf-8"), digest_size=32).digest()

def issue_session_token(password_hash, ttl_minutes):
    expiry = int(time.time()) + ttl_minutes * 60
    sig = hmac.new(_session_secret(password_hash), str(expiry).encode(), hashlib.sha256).hexdigest()
    return f"{expiry}.{sig}"
```

- Token = `<unix expiry>.<hex HMAC-SHA256(key, ascii(expiry))>`.
- HMAC key = BLAKE2b-256(root key ‖ current Argon2id hash string), a plain concatenation passed to unkeyed BLAKE2b.
- `verify_session_token` checks expiry against `time.time()`, recomputes the HMAC, and compares with `hmac.compare_digest` (constant-time).
- The token carries no identity or nonce. Two tokens issued in the same second with the same TTL are identical.
- Cookie (`app/api/deps.py::session_cookie_kwargs`): name `forge_session`, `httponly=True`, `samesite="lax"`, `secure=FORGE_SESSION_COOKIE_SECURE` (default `False`), `max_age = session_ttl_minutes * 60`, where `session_ttl_minutes` defaults to 720 (12 h).
- `require_auth` (`app/api/deps.py`) verifies the cookie against the current `master_password_hash` on every authenticated request.
- Revocation:
  - Changing the master password changes `password_hash`, which invalidates **all** tokens.
  - Changing `FORGE_MASTER_KEY` also invalidates all tokens.
  - `/api/auth/lock` only calls `response.delete_cookie(...)`. The token itself stays valid until expiry if someone has a copy (see threat model T6).

---

## 6. MCP bearer tokens (shares the root key)

- `generate_mcp_token()` returns `secrets.token_urlsafe(32)` (256 bits).
- `hash_mcp_token(token)` returns `hmac.new(_root_key(), token, sha256).hexdigest()`, stored in `mcp_tokens.token_hash` and looked up by exact equality (`services/mcp/tokens.py::verify`).
- The bootstrap token (`FORGE_MCP_BOOTSTRAP_TOKEN` / `_FILE`) is compared in plaintext with `hmac.compare_digest` in `app/mcp/auth.py`.
- Because the root key is the HMAC key, rotating `FORGE_MASTER_KEY` invalidates every stored MCP token.
- Per [Security.md](Security.md) and the static check in `tests/test_mcp_tools_static_checks.py`, no MCP tool imports the secrets service or `app/services/crypto/`.

---

## 7. Backups (`app/services/settings/backup.py`)

- `export_backup` (GET `/api/settings/backup`, auth required) returns JSON with each secret's `encrypted_value`, `encrypted_metadata`, and every version's `encrypted_value`, base64-encoded. Names, types, folders, tags and notes are in **plaintext** in the bundle.
- The bundle has **no extra encryption, signature or MAC**. Its confidentiality depends entirely on the per-field SecretBox ciphertext.
- `import_backup` (POST `/api/settings/backup/import`) **deletes all** secrets, versions, tags, folders and notes, then inserts the bundle's rows. It doesn't check that the ciphertext decrypts under the current key. A bundle from an instance with a different `FORGE_MASTER_KEY` imports "successfully" and then fails at reveal time with a 500 (§3).
- Not in the bundle: `provider_credentials`, `mcp_tokens`, `AppConfig` (master password hash), `secrets.project_id`. Version `created_at` is exported but not restored on import (the model default `utcnow()` is used instead).

---

## 8. Crypto tools are separate (`app/services/crypto/service.py`)

These are developer utilities behind `AuthDep` at `/api/crypto/*`. The module docstring says "nothing here touches the master key", and the code agrees: nothing in it imports `app.core.security`.

- AES-256-GCM with a key from PBKDF2-HMAC-SHA256 (310,000 iterations, 16-byte random salt, 12-byte random nonce): `_derive_aes_key`, `aes_encrypt`, `aes_decrypt`
- RSA-OAEP (SHA-256, 2048/3072/4096), ECDSA P-256/SHA-256, HS256/384/512 JWT, plain hashes (including MD5/SHA-1)

These run **on the server**. Passphrases, plaintexts and private keys are sent in the request body. Generated private keys are returned unencrypted (`NoEncryption()`). None of this output is persisted.

---

## 9. Known gaps (honest list)

| # | Gap | Evidence | Impact |
|---|---|---|---|
| G1 | **No KDF work factor on the root key.** BLAKE2b is applied once, with no salt. | `_derive_key` | A weak `FORGE_MASTER_KEY` can be brute-forced offline from any stolen ciphertext. Only random keys are safe. Comments that say "stretched" overstate this. |
| G2 | **No key rotation.** There's no tooling to re-encrypt under a new key, and the blob has no key id or version byte. | `VaultCrypto`, models | Changing `FORGE_MASTER_KEY` makes every secret, version and provider key undecryptable, and invalidates all sessions and MCP tokens. |
| G3 | **One key, three uses, no domain separation** (encryption, session HMAC input, MCP HMAC key). | `_root_key` callers | Not a known practical break with these primitives, but it doesn't follow key-separation practice and ties every rotation together. |
| G4 | **Ciphertext isn't bound to its row** (no AAD). | `VaultCrypto.encrypt` | Someone with DB write access can swap `encrypted_value` blobs between secrets, or move a provider key blob into a secret, and decryption still succeeds. |
| G5 | **Master password isn't part of the encryption key.** | `security.py` docstring, `change_master_password` | Stolen DB + leaked `FORGE_MASTER_KEY` = full plaintext, whatever the password. The running server can decrypt with no user present. |
| G6 | **Metadata is in plaintext** (names, types, folders, tags, timestamps, activity messages, provider labels and base URLs). | §3.2 | A DB or backup leak shows which services you hold credentials for. |
| G7 | **`FORGE_MASTER_KEY_FILE` fails silently.** A missing file falls back to the env var. | `_read_secret_file` | A misconfigured secret mount can run Forge on an unintended key (e.g. a dev value in `.env`) without warning. |
| G8 | **No minimum entropy or length check on `FORGE_MASTER_KEY`.** | `resolved_master_key` | Combined with G1, weak keys are accepted. |
| G9 | **Logout doesn't revoke the token.** Tokens are stateless and deterministic, valid for up to 12 h by default. | `lock`, `issue_session_token` | A copied cookie keeps working after "Lock" until it expires or the password changes. |
| G10 | **Argon2id uses INTERACTIVE limits** (the library default, not tuned). | `hash_master_password` | Weaker against an offline guess attack on a stolen `master_password_hash` than the MODERATE/SENSITIVE presets. The password gates the UI, not the data, so the impact is limited. |
| G11 | **Backup bundles aren't authenticated as a whole, and import doesn't verify decryptability.** | `backup.py` | A tampered or wrong-key bundle replaces all vault data and fails only at reveal time. |
| G12 | **Version reveals aren't audited.** `GET /secrets/{id}/versions/{vid}` decrypts without an `ActivityLog` row (`get_secret(reveal=True)` does log). | `routes/secrets.py::reveal_version`, `service.reveal_version` | Incomplete audit trail for plaintext access. |
| G13 | **Keys sit in process memory with no zeroing.** | `lru_cache` on `_root_key`, `get_vault_crypto` | Expected for this design. Memory dumps or swap reveal the key (out of scope per the threat model). |
| G14 | **Decryption errors become generic 500s.** | `errors.py` catch-all | Fine for confidentiality, but tampering or a key mismatch shows up as "unexpected error" rather than a clear integrity failure. |
| G15 | **No tests for tamper detection or wrong-key rejection** on `VaultCrypto`. `tests/test_security.py` covers only round-trip and nonce randomness. | `tests/test_security.py` | The authenticated-encryption property is relied on but not asserted. |
