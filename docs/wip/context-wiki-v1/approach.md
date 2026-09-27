---
title: Approach
description: How v1 of the context-wiki skill is built -- small steps, with the draft SKILL.md setting direction
---

# Approach

Build slowly. Each step adds one small detail to `SKILL.md`, and Adriaan
reviews it before the next. When in doubt, leave it out: a detail can be
added later, but one that ships becomes a convention people rely on.

## Direction

The draft `SKILL.md` at commit `44f0f57` sets the direction. It outranks
the 2026-07-21 handover
(`docs/archive/completed/2026-09-21-starting-from-handover/handover.md`)
and the description of ticket akps-468d wherever they disagree.
[specs/context-wiki.delta.md](specs/context-wiki.delta.md) states what the
draft implies as a spec.

Design as though agent-memory does not exist; Adriaan has used it less than
he expected. Nothing in v1 defers to it or coordinates with it.

Left out of v1, though the handover settled them. Each returns only if a
real need shows up:

- `raw/` and `output/` directories beside the clone.
- `sources/` ingestion notes with content hashes.
- `status: draft` frontmatter.
- `<subject>-wiki` repository naming.
- A whole-wiki index CLI (ticket akps-efa9).
- The name "wiki" in place of "context wiki".

## Reading of the work-item analysis

Adriaan's comments on
[resources/work-item-knowledge-analysis.md](resources/work-item-knowledge-analysis.md),
2026-09-27. Leanings, not yet spec:

- Facts about external systems fit a context wiki owned by the dev team.
- Facts about the organization fit a context wiki.
- Lessons about the human-agent collaboration fit the user's personal
  context wiki.
- Empirical results are a tricky case, close to a research log. A quoted
  result means little once it is detached from its context.
- Uncertainty belongs in the wording ("probably", "we assume"), not in a
  confidence field.
- A correction replaces the old belief rather than keeping it marked as
  superseded. A model that reads the old belief can be misled by it even
  when it is flagged.

## Verification

Read `SKILL.md` against the spec, statement by statement. Then have a
fresh agent, given only the skill, add an entry to a scratch wiki, and check
the result against the spec.
