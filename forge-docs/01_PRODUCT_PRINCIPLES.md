# 01 — Product Principles

> **Purpose:** Encode the recurring judgment calls that should stay consistent across every feature, phase, and Claude Code session.
> **Scope:** Product and design principles. Engineering conventions live in [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md); architectural principles live in [03_ARCHITECTURE.md](03_ARCHITECTURE.md).
> **Ownership:** TODO — assign a product owner.
> **Status:** Draft
> **Last Updated:** 2026-07-20

---

## 1. Principles

### 1.1 Single-tenant by design

Forge gates the whole instance with one master password. Multi-user/RBAC is explicitly **not planned** — it would change the auth model fundamentally, not extend it. Do not add user accounts, roles, or per-user data partitioning without a full architecture review and a new ADR in [`/forge-docs/decisions/`](decisions/README.md).

### 1.2 Self-hosted first, cloud-optional

Every feature must work fully on a LAN with no internet access. Optional cloud-dependent features (e.g. vision-LLM assistance for Ingest, future Model Playground providers) must degrade gracefully to "disabled" rather than breaking the app when no API key is configured.

### 1.3 Honest gaps over fake completeness

If a feature can't be built to a real standard, it is **left out and tracked**, not shipped shallow. Precedent: PGP was left out of Crypto rather than shipped as a keypair-only, non-interoperable stand-in. Apply the same standard to every new phase — a documented TODO beats a convincing-looking stub.

### 1.4 Modular monolith, not microservices

One backend process, one frontend process, one database. Splitting a feature into its own service requires a proven need for independent scaling or a different runtime — not just "it feels like it should be separate." See [03_ARCHITECTURE.md](03_ARCHITECTURE.md).

### 1.5 Feature isolation in code

Features do not import from each other's internals. Anything genuinely shared lives in `lib/`, `components/`, or a backend `core/` module. This keeps the monolith's internal boundaries real even without process boundaries.

### 1.6 Security by default, not by configuration

Encryption at rest, session auth, and safe defaults must not depend on an operator remembering to flip a flag. Where a security/usability tradeoff is genuinely environment-dependent (e.g. the `Secure` cookie flag on non-TLS LAN deployments), the default favors a working, honestly-documented posture over a textbook default that silently breaks the app — see [`../docs/DecisionLog.md`](../docs/DecisionLog.md).

### 1.7 One command palette, one search, one session

New features plug into the existing cross-cutting systems (⌘K command palette, global search, auth session) instead of building parallel ones. A new phase that needs "its own search" or "its own auth" is a signal to stop and reconsider the design.

### 1.8 Documentation-first

No implementation work begins without a spec. Every phase under `/forge-docs/implementation/` must have its `01_SPEC.md` and `08_ACCEPTANCE.md` filled in before `IMPLEMENT.md` authorizes work. See [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md).

## 2. Checklist for evaluating new feature ideas

- [ ] Does it work with zero internet access? If not, does it degrade gracefully?
- [ ] Does it require multi-user assumptions? If yes — stop, this needs an ADR.
- [ ] Can it be built completely, or does it need to be scoped down and the gap tracked honestly?
- [ ] Does it reuse the existing auth/search/command-palette systems?
- [ ] Does it fit inside the modular monolith, or does it have a real, provable reason not to?

## 3. TODO

- [ ] TODO: Ratify these principles with the project owner — currently derived from observed precedent in `../docs/DecisionLog.md`, not an explicit charter.
- [ ] TODO: Define an explicit process for principle exceptions (who can approve one, and where it gets recorded).

## 4. Cross-references

- [00_VISION.md](00_VISION.md)
- [03_ARCHITECTURE.md](03_ARCHITECTURE.md)
- [07_CODING_STANDARDS.md](07_CODING_STANDARDS.md)
- [../docs/DecisionLog.md](../docs/DecisionLog.md) — precedent these principles are distilled from.
- [decisions/README.md](decisions/README.md) — where new architectural exceptions get recorded.
