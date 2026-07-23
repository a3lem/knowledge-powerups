---
title: Still to do
description: Handover items not yet addressed, as of 2026-07-21
---

# Still to do

Unaddressed items from [HANDOVER.md](HANDOVER.md). Where a ticket exists, details live there.

## Wiki (context-wikis)

- [ ] Write the context-wikis main skill. Settled decisions to encode: the repo *is* the wiki (no nested `wiki/`); `raw/` and `output/` as untracked sibling directories; `sources/` ingestion notes that stand alone (origin, content hash, summary); `status: draft` frontmatter instead of a `drafts/` folder; standard markdown links, not wikilinks; `<subject>-wiki` repo naming; wikis layer (personal + company).
- [ ] Write the open-knowledge-format skill (file exists, empty).
- [ ] Decide the companion CLI's fate: per-directory index generation is now covered by ' generator; still unbuilt are whole-wiki index aggregation and surfacing `status: draft` pages.

## Agent memory

- [ ] Build the agent-memory skills: `system/` (prompt-injected, size-constrained) vs `reference/` (paths in prompt, content on demand) vs `skills/` (procedural memory).
- [ ] Encode: memory mounts wikis rather than embedding them; history compaction, dreaming, and defragmentation are one primitive under different names.
- [ ] `reference/` per-directory index.md was an open question; answered yes in practice (Adriaan's own memory tree has them) -- write it down.

## Conventional docs

- [ ] Lifecycle rule for `docs/dev/references/` (it will accumulate) -- handover open question 3, still open.
- [ ] The promotion rule is not in the skill yet: knowledge learned during a work item gets reiterated in docs (when about this code) or filed in the wiki (when true beyond the repo).

## Cross-cutting

- [ ] Per-pillar "what belongs here, what doesn't" sections + cross-store comparison in the top-level README -> akps-f110.
- [x] Fill the two `<!-- TODO -->` example sections in the using-specs skill. (Naming resolved 2026-07-23 via akps-f6ca: plugin conventional-docs -> docs-dir-conventions, skills using-docs + using-specs; prefix-relative skill names.)
- [ ] PHILOSOPHY.md appears in the handover's repo tree but does not exist; decide whether the top-level README absorbs it (per akps-f110) or it gets written.
- [ ] Packaging: `.claude-plugin/plugin.json` manifests; per-plugin READMEs stating dependencies (the audience bundles need restating now that foundations is gone); top-level README last, once everything settles.
- [ ] `examples/` is empty -- decide what belongs there.
