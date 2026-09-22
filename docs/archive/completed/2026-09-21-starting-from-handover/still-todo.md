---
title: Still to do
description: Handover items not yet addressed, as of 2026-07-21
---

# Still to do

Unaddressed items from [handover.md](handover.md). Where a ticket exists,
details live there.

Final state at archival, 2026-09-21. `[x]` done, `[>]` promoted to a ticket
and still live, `[~]` resolved by deciding not to do it.

## Wiki (context-wikis)

- [>] Write the context-wikis main skill, and the open-knowledge-format
  skill (both files still empty). Promoted to akps-468d, which carries the
  settled decisions.
- [>] Decide the companion CLI's fate: per-directory index generation is now
  covered by `cli/generate_index.py`; whole-wiki index aggregation and
  surfacing `status: draft` pages are still unbuilt. Promoted to akps-efa9.

## Agent memory

- [x] Build the agent-memory skills: `system/` (prompt-injected, size-constrained) vs `reference/` (paths in prompt, content on demand) vs `skills/` (procedural memory). (keeping-memories written 2026-07-26; consolidation delivered with the memory agent; akps-8e51 closed as v0.1 on 2026-07-29.)
- [x] Encode: wikis live outside memory, memory links to them (mounting was retracted); history compaction, dreaming, and defragmentation are one primitive under different names. (Both in keeping-memories.)
- [x] `reference/` per-directory index.md was an open question; answered yes at first, then reversed on 2026-07-27 (akps-4e8e): the injected index compiles from each file's frontmatter, no index file at rest. Re-revised 2026-07-30 (akps-45ab): index.md returns with an authored frontmatter description (compile's source for directory entries) and a generated body for on-disk traversal.

## Conventional docs

- [>] Lifecycle rule for `docs/resources/` (it will accumulate) -- handover
  open question 3. Promotion *into* it was settled on 2026-09-15; removal
  was not. Design notes promoted to
  `plugins/docs-conventions/docs/wip/resources-lifecycle/`, tracked as
  akps-90a6.
- [>] The promotion rule is not in the skill yet: knowledge learned during a
  work item gets reiterated in docs (when about this code) or filed in the
  wiki (when true beyond the repo). Promoted to akps-5c01.

## Cross-cutting

- [~] Per-pillar "what belongs here, what doesn't" sections + cross-store
  comparison in the top-level README. akps-f110 was cancelled on 2026-07-30
  as unclear what to do with it; not revived here. Start a fresh ticket if
  it comes back.
- [x] Fill the two `<!-- TODO -->` example sections in the using-specs skill. (Naming resolved 2026-07-23 via akps-f6ca: plugin conventional-docs -> docs-dir-conventions, skills using-docs + using-specs; prefix-relative skill names.)
- [~] PHILOSOPHY.md appears in the handover's repo tree but does not exist.
  Decided by default: it was never written, akps-f110 that would have
  absorbed it is cancelled, and the top-level README stands on its own.
- [x] Packaging: all five `.claude-plugin/plugin.json` manifests exist, all
  five plugins have a README stating dependencies, and the top-level README
  is written. (Verified 2026-09-21.)
- [~] `examples/` is empty -- decide what belongs there. Decided by
  default: the directory does not exist and nothing has needed it.
