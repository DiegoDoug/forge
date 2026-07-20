# Forge Documentation

> **Purpose:** Index of user-facing, current-state documentation for the shipped Forge application.
> **Scope:** Documents describing the application as it exists today — architecture, security, deployment, database, API, and contribution guidance. For how *future* development is planned and executed, see the FDK at [`../forge-docs/`](../forge-docs/00_VISION.md) instead.
> **Ownership:** TODO — assign a docs owner.
> **Status:** Current
> **Last Updated:** 2026-07-20

---

## 1. What's here

This folder documents Forge as it exists today, for anyone deploying, operating, contributing to, or auditing the application.

| Document | Covers |
|---|---|
| [Architecture.md](Architecture.md) | System shape, request flow, backend/frontend layout, auth model |
| [FolderStructure.md](FolderStructure.md) | Full repository directory layout and code conventions |
| [Database.md](Database.md) | Schema, migrations, data lifecycle |
| [API.md](API.md) | Endpoint reference |
| [Security.md](Security.md) | Auth model, encryption at rest, threat model |
| [Deployment.md](Deployment.md) | Docker Compose deployment, environment configuration |
| [Development.md](Development.md) | Local dev setup |
| [Contributing.md](Contributing.md) | Contribution guidelines |
| [DecisionLog.md](DecisionLog.md) | Notable past decisions and why |
| [Roadmap.md](Roadmap.md) | Known gaps and near-term plans for the shipped app |

## 2. Where to start

- **Deploying Forge?** Start with [Deployment.md](Deployment.md), then [Security.md](Security.md).
- **Contributing code?** Start with [Development.md](Development.md), then [Contributing.md](Contributing.md) and [FolderStructure.md](FolderStructure.md).
- **Understanding how it's built?** Start with [Architecture.md](Architecture.md).
- **Planning new features?** This folder isn't the right place — see [`../forge-docs/00_VISION.md`](../forge-docs/00_VISION.md) and the phase specs under [`../forge-docs/implementation/`](../forge-docs/implementation/).

## 3. Relationship to `forge-docs/`

See [`../forge-docs/11_PROJECT_STRUCTURE.md`](../forge-docs/11_PROJECT_STRUCTURE.md) §4 for the full explanation. In short: this folder (`docs/`) is the record of what Forge *is*; `forge-docs/` is the system that plans and drives what Forge *becomes*. Keep content in exactly one of the two — cross-link rather than duplicate.

## 4. TODO

- [ ] TODO: Add a changelog or release-notes document once versioned releases begin.

## 5. Cross-references

- [../README.md](../README.md) — top-level project README (install/quickstart)
- [../forge-docs/00_VISION.md](../forge-docs/00_VISION.md)
- [../forge-docs/11_PROJECT_STRUCTURE.md](../forge-docs/11_PROJECT_STRUCTURE.md)
