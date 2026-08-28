---
title: Still to do
description: Handover items not yet addressed, as of 2026-07-21
---

# Still to do

Unaddressed items from [handover.md](handover.md). Where a ticket exists, details live there.

## Wiki (context-wikis)

- [ ] Write the context-wikis main skill. Settled decisions to encode: the repo *is* the wiki (no nested `wiki/`); `raw/` and `output/` as untracked sibling directories; `sources/` ingestion notes that stand alone (origin, content hash, summary); `status: draft` frontmatter instead of a `drafts/` folder; standard markdown links, not wikilinks; `<subject>-wiki` repo naming; wikis layer (personal + company).
- [ ] Write the open-knowledge-format skill (file exists, empty).
- [ ] Decide the companion CLI's fate: per-directory index generation is now covered by ' generator; still unbuilt are whole-wiki index aggregation and surfacing `status: draft` pages.

## Agent memory

- [x] Build the agent-memory skills: `system/` (prompt-injected, size-constrained) vs `reference/` (paths in prompt, content on demand) vs `skills/` (procedural memory). (keeping-memories written 2026-07-26; consolidation delivered with the memory agent; akps-8e51 closed as v0.1 on 2026-07-29.)
- [x] Encode: wikis live outside memory, memory links to them (mounting was retracted); history compaction, dreaming, and defragmentation are one primitive under different names. (Both in keeping-memories.)
- [x] `reference/` per-directory index.md was an open question; answered yes at first, then reversed on 2026-07-27 (akps-4e8e): the injected index compiles from each file's frontmatter, no index file at rest. Re-revised 2026-07-30 (akps-45ab): index.md returns with an authored frontmatter description (compile's source for directory entries) and a generated body for on-disk traversal.

## Conventional docs

- [ ] Lifecycle rule for `docs/dev/references/` (it will accumulate) -- handover open question 3, still open.
- [ ] The promotion rule is not in the skill yet: knowledge learned during a work item gets reiterated in docs (when about this code) or filed in the wiki (when true beyond the repo).

## Cross-cutting

- [ ] Per-pillar "what belongs here, what doesn't" sections + cross-store comparison in the top-level README -> akps-f110.
- [x] Fill the two `<!-- TODO -->` example sections in the using-specs skill. (Naming resolved 2026-07-23 via akps-f6ca: plugin conventional-docs -> docs-dir-conventions, skills using-docs + using-specs; prefix-relative skill names.)
- [ ] PHILOSOPHY.md appears in the handover's repo tree but does not exist; decide whether the top-level README absorbs it (per akps-f110) or it gets written.
- [ ] Packaging: `.claude-plugin/plugin.json` manifests; per-plugin READMEs stating dependencies (the audience bundles need restating now that foundations is gone); top-level README last, once everything settles.
- [ ] `examples/` is empty -- decide what belongs there.
