# Developer Toolkit — API

> **Purpose:** Endpoint contract for this phase — every route, its request/response shape, and its auth requirement.
> **Scope:** API contract only. Implementation detail lives in 03_BACKEND.md.
> **Ownership:** TODO — assign a phase owner.
> **Status:** Approved in principle by the project owner 2026-08-05 — "existing Generator/Crypto API contracts unchanged" is confirmed.
> **Last Updated:** 2026-08-05

---

## 1. Endpoints

**No new, changed, or removed endpoint.** This phase adds zero backend routes. The existing endpoints below are listed for completeness — unchanged, at their current paths — since [`01_SPEC.md`](01_SPEC.md) §3 requirement 7 makes their continued, unmodified operation an explicit functional requirement:

| Method | Path | Request | Response | Auth |
|--------|------|---------|----------|------|
| POST | `/api/generators/password` | `PasswordGenerateIn` | `GeneratedValueOut` | session required |
| POST | `/api/generators/uuid4` | — | `GeneratedValueOut` | session required |
| POST | `/api/generators/uuid7` | — | `GeneratedValueOut` | session required |
| POST | `/api/generators/nanoid` | `NanoIdGenerateIn` | `GeneratedValueOut` | session required |
| POST | `/api/generators/random-bytes` | `RandomBytesGenerateIn` | `GeneratedValueOut` | session required |
| POST | `/api/generators/api-key` | `ApiKeyGenerateIn` | `GeneratedValueOut` | session required |
| POST | `/api/generators/jwt-secret` | `JwtSecretGenerateIn` | `GeneratedValueOut` | session required |
| POST | `/api/generators/entropy` | `EntropyEstimateIn` | `EntropyOut` | session required |
| POST | `/api/crypto/base64/encode` \| `/decode` | `Base64In` | `TextOut` | session required |
| POST | `/api/crypto/hash` \| `/hash/verify` | `HashIn` / `VerifyHashIn` | `HashOut` / `VerifyOut` | session required |
| POST | `/api/crypto/aes/encrypt` \| `/decrypt` | `AesEncryptIn` / `AesDecryptIn` | `AesEncryptOut` / `TextOut` | session required |
| POST | `/api/crypto/jwt/decode` \| `/verify` \| `/build` | `JwtDecodeIn` / `JwtVerifyIn` / `JwtBuildIn` | `JwtDecodeOut` / `JwtVerifyOut` / `TextOut` | session required |
| POST | `/api/crypto/rsa/keypair` \| `/encrypt` \| `/decrypt` | `RsaKeypairIn` / `RsaEncryptIn` / `RsaDecryptIn` | `KeypairOut` / `TextOut` / `TextOut` | session required |
| POST | `/api/crypto/ecc/keypair` \| `/sign` \| `/verify` | — / `EccSignIn` / `EccVerifyIn` | `KeypairOut` / `TextOut` / `VerifyOut` | session required |

Utilities has no endpoints today and gains none.

## 2. Schemas

No new Pydantic request/response schema is introduced. `backend/app/schemas/generators.py` and `backend/app/schemas/crypto.py` are unmodified.

## 3. Error handling

Unchanged — every existing error case and HTTP status code for the endpoints above stays exactly as shipped, since no route handler is modified.

## 4. Rate limiting / abuse considerations

None beyond the existing deployment-level posture in [`../../../docs/Security.md`](../../../docs/Security.md). This phase introduces no new attack surface (no new endpoint, no new outbound call, no new persistence) — same conclusion Universal Converter reached for the equivalent question in its own `06_API.md`.

## 5. TODO

- [ ] None — this document explicitly states "no change," per [`04_DATABASE.md`](04_DATABASE.md)'s precedent, rather than being left as an unfilled placeholder.

## 6. Cross-references

- [03_BACKEND.md](03_BACKEND.md)
- [05_COMPONENTS.md](05_COMPONENTS.md)
- [../../../docs/API.md](../../../docs/API.md)
- [../../../docs/Security.md](../../../docs/Security.md)
