# 02 — Roadmap

> **Purpose:** Sequence the vision in [00_VISION.md](00_VISION.md) into ordered, buildable phases.
> **Scope:** Cross-phase sequencing and dependency ordering. Per-phase detail lives in `implementation/Phase-XX-*/`.
> **Ownership:** TODO — assign a roadmap owner.
> **Status:** Draft — Phase 01 released; Phase 02 current
> **Version:** 0.3.0
> **Last Updated:** 2026-07-21
> **Depends On:** [00_VISION.md](00_VISION.md)
> **Supersedes:** —

---

## 1. How to read this roadmap

Each phase below links to its full spec folder under [`implementation/`](implementation/). A phase is **not** authorized for implementation until its `01_SPEC.md` and `08_ACCEPTANCE.md` are filled in and its `README.md` Definition of Complete is agreed — see [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md).

## 2. Shipped foundation (pre-FDK)

The following already exist in the application and are **not** re-specified here; they're the base the phases below extend. Source of truth for these remains [`../docs/`](../docs/).

- [x] Secrets (encrypted secrets, renamed from Vault per [ADR-0006](decisions/0006-vault-renamed-to-secrets.md) — executed as part of Phase 01/T1; `/vault` and `/api/vault` remain as compatibility aliases)
- [x] Notes (sticky board)
- [x] Documents (rich text editor + export)
- [x] Generators (passwords, UUIDs, NanoIDs, keys)
- [x] Crypto (Base64, hashing, AES-GCM, JWT, RSA, ECDSA)
- [x] Converters (JSON, regex, URL/Unicode, cron, diff, timestamps)
- [x] Utilities (QR, checksums, color, timezone)
- [x] Ingest (document → Markdown pipeline)
- [x] Workbench (replaced Dashboard outright per [ADR-0001](decisions/0001-workbench-replaces-dashboard.md) — executed as Phase 01, released as `v0.1.0-workbench`), Search (dedicated page, Phase 01/T2), Settings, Auth

## 3. Phase sequence

| # | Phase | Proposed relationship to shipped foundation | Status |
|---|-------|----------------------------------------------|--------|
| 01 | [Workbench](implementation/Phase-01-Workbench/README.md) | Replaces Dashboard outright with a panel-based, extensible home workspace (see [ADR-0001](decisions/0001-workbench-replaces-dashboard.md), [ADR-0002](decisions/0002-workbench-panel-architecture.md)) | ✓ Complete — 🔒 released & frozen as `v0.1.0-workbench` |
| 02 | [Project Initialization Engine](implementation/Phase-02-Project-Initialization-Engine/README.md) | New — generates FDK phase scaffolds and AI project instruction files (CLAUDE.md/AGENTS.md/instructions.md) as zip downloads | **Current** — implementation complete, pending Release Candidate audit + Owner Sign-off (not yet merged) |
| 03 | [Prompt Studio](implementation/Phase-03-Prompt-Studio/README.md) | New — authoring/versioning workspace for LLM prompts | Not started |
| 04 | [Universal Converter](implementation/Phase-04-Universal-Converter/README.md) | Unifies Converters + Ingest into one format-conversion surface | Not started |
| 05 | [Model Playground](implementation/Phase-05-Model-Playground/README.md) | New — test/compare LLM providers and models | Not started |
| 06 | [Projects](implementation/Phase-06-Projects/README.md) | New — cross-feature project/workspace grouping | Not started |
| 07 | [Knowledge Hub](implementation/Phase-07-Knowledge-Hub/README.md) | Unifies Notes + Documents + Ingest output into a searchable knowledge base | Not started |
| 08 | [Developer Toolkit](implementation/Phase-08-Developer-Toolkit/README.md) | Consolidates Generators + Crypto + Utilities under one umbrella | Not started |

> **TODO:** The "proposed relationship" column is the Lead Architect's inference from the shipped feature set, not a ratified decision. Confirmed correct for Phase 01 (now released). Confirm or correct the remaining phases with the project owner before each begins.

## 4. Sequencing rationale (draft)

- Phases 01–02 are foundational (workspace shell + project scaffolding) and should land before phases that assume a "project" concept (06, 07).
- Phases 03 and 05 (Prompt Studio, Model Playground) share LLM-provider plumbing — TODO: confirm whether they should be built together or 05 first as the provider-integration base.
- Phases 04, 07, 08 are consolidations of existing features and carry lower architectural risk — candidates to interleave with the higher-risk new phases (01, 02, 03, 05, 06) for momentum.

This ordering is a **draft proposal**, not a commitment. Phase 01 shipped in this position without issue. TODO: run a sequencing review before Phase 02 kicks off.

- [ ] TODO: [ADR-0005](decisions/0005-projects-primary-organizational-unit.md) affirms Projects as Forge's primary organizational unit going forward — revisit whether Phase 06's position in this sequence still reflects that priority, or whether it should move earlier once Phase 01/02 land.

## 5. Known gaps in the shipped foundation

Tracked in detail in [`../docs/Roadmap.md`](../docs/Roadmap.md): PGP support, list-endpoint pagination, nested Vault folders in the UI, and rate limiting. These are candidates to fold into whichever phase touches their feature area (e.g. pagination work naturally lands during Phase 06 Projects or Phase 07 Knowledge Hub).

## 6. TODO

- [ ] TODO: Get roadmap ordering ratified by the project owner.
- [ ] TODO: Attach target quarters/dates once ownership and capacity are known — deliberately omitted for now to avoid a fake sense of schedule certainty.
- [ ] TODO: Re-evaluate this roadmap after each phase's checkpoint (see [10_CHECKPOINT_PROTOCOL.md](10_CHECKPOINT_PROTOCOL.md)).

## 7. Cross-references

- [00_VISION.md](00_VISION.md)
- [implementation/](implementation/) — full phase specs
- [09_CLAUDE_CODE_RULES.md](09_CLAUDE_CODE_RULES.md) — when a phase is authorized to start
- [../docs/Roadmap.md](../docs/Roadmap.md) — shipped-application known gaps
