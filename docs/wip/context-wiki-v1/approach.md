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

Left out of v1, though the handover settled them. Each returns only if a
real need shows up:

- `raw/` and `output/` directories beside the clone.
- `sources/` ingestion notes with content hashes.
- `status: draft` frontmatter.
- `<subject>-wiki` repository naming.
- A whole-wiki index CLI (ticket akps-efa9).
- The name "wiki" in place of "context wiki".

## Reconciled with existing conventions

- The draft requires frontmatter on "every note file". `index.md` carries
  no frontmatter under `docs/specs/directory-index.md` [er5xx], and the
  draft's README template has none either, so the spec defines a note as
  any markdown file other than `index.md` and `README.md`. Unconfirmed by
  Adriaan.
- The draft accepts file-relative links as well as links rooted at the
  wiki root. Agent memory allows only rooted links. The wiki follows the
  draft; the difference is deliberate.

## Open

- What happens to the glossary's OKF entry, which the draft never
  mentions.

## Verification

Read `SKILL.md` against the spec, statement by statement. Then have a
fresh agent, given only the skill, add a note to a scratch wiki, and check
the result against the spec.
