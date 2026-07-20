# Doc Chunks

> **Purpose:** Small, composable Markdown fragments (a standard warning banner, a standard "Known Issues" block, a standard cross-reference footer) that get pasted into multiple docs, kept here so they stay identical everywhere they're used.
> **Scope:** Fragments only, not full documents. A fragment should be a handful of lines, not a whole template — full document templates belong in [`../prompts/`](../prompts/README.md) or the phase template shape defined in [`../../02_ROADMAP.md`](../../02_ROADMAP.md).
> **Ownership:** TODO — assign an owner.
> **Status:** Active
> **Version:** 0.2.0
> **Last Updated:** 2026-07-20
> **Depends On:** —
> **Supersedes:** —

---

## 1. Available chunks

| Chunk | Use when |
|---|---|
| [DOC_HEADER.md](DOC_HEADER.md) | Starting any new `forge-docs` file — the canonical Purpose/Scope/Ownership/Status/Version/Last Updated/Depends On/Supersedes block, plus the semantic-versioning convention for documents. |

## 2. Candidate chunks (not yet extracted)

- [ ] TODO: A standard "TODO placeholder" checklist item format.
- [ ] TODO: A standard "this document is a template placeholder" banner (currently duplicated by hand in every unfilled phase doc).

## 3. Usage

Reference [`DOC_HEADER.md`](DOC_HEADER.md) when starting a new document. Copy the block verbatim and fill in its fields — don't invent a variant shape.

## 4. Cross-references

- [../README.md](../README.md)
