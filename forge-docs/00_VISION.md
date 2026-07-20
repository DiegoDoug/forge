# 00 — Vision

> **Purpose:** Define why Forge exists and the north star every future decision is measured against.
> **Scope:** Product-level vision only. Feature specifics live in [11_PROJECT_STRUCTURE.md](11_PROJECT_STRUCTURE.md) and `/forge-docs/implementation/`. Process/execution vision (how Claude Code works within this repo) lives in [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md).
> **Ownership:** TODO — assign a product owner (currently unowned; the Lead Architect role is filling this gap).
> **Status:** Draft
> **Version:** 0.1.0
> **Last Updated:** 2026-07-20
> **Depends On:** —
> **Supersedes:** —

---

## 1. Statement

Forge is a **self-hosted developer toolbox**: a single Docker Compose deployment that replaces a dozen SaaS tabs (password manager, notes app, JWT debugger, converter sites, snippet vault, document converter) with one application a developer owns, runs on their own hardware, and never has to trust a third party with.

Every feature in Forge exists to answer one question: *"Why am I opening a website for this when it could just live here?"*

## 2. Why this matters

- **Data ownership.** Secrets, notes, and documents never leave the operator's infrastructure.
- **No subscription sprawl.** One deployment replaces many single-purpose tools.
- **Offline-capable.** A LAN deployment with no internet dependency should work fully.
- **Composability.** Tools that developers reach for daily (hashing, encoding, JWT, converters) should share one auth session, one search index, one command palette — not live in a dozen disconnected browser tabs.

## 3. North star

> A developer should be able to `docker compose up` once and never need another developer-tools website again.

## 4. Non-goals

- Forge is **not** a multi-user SaaS product. It is single-tenant by design — see [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md).
- Forge is **not** trying to replace full IDEs, ticket trackers, or CI systems.
- Forge does not aim for feature parity with any single competitor (Bitwarden, DevToys, Notion, etc.) — it aims to cover the *intersection* of tools a working developer uses most often.

## 5. Horizon

The current shipped surface (Vault, Notes, Documents, Generators, Crypto, Converters, Utilities, Ingest, Dashboard, Search, Settings) is the foundation. The next horizon — tracked as formal phases under `/forge-docs/implementation/` — extends Forge from a *utility toolbox* into a *developer workbench*: project-scoped organization, AI-assisted prompt/model tooling, and a unified conversion/knowledge layer. See [02_ROADMAP.md](02_ROADMAP.md).

## 6. TODO

- [ ] TODO: Get explicit sign-off from the project owner on the "north star" statement above.
- [ ] TODO: Define success metrics for the vision (what does "years of development" actually optimize for — feature count? reliability? adoption?).
- [ ] TODO: Revisit non-goals annually; confirm they still hold as the Phase 01–08 roadmap lands.

## 7. Cross-references

- [01_PRODUCT_PRINCIPLES.md](01_PRODUCT_PRINCIPLES.md) — the operating principles derived from this vision.
- [02_ROADMAP.md](02_ROADMAP.md) — how the vision becomes sequenced work.
- [03_ARCHITECTURE.md](03_ARCHITECTURE.md) — the technical shape that serves this vision.
- [../docs/Roadmap.md](../docs/Roadmap.md) — existing known-gaps roadmap for the shipped application.
