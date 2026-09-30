---
title: Context wikis get recommended defaults
description: Why the context-wiki skill requires a small core and only suggests the rest, superseding the fixed layout of 0002
---

# Context wikis get recommended defaults

A context wiki is a collection of markdown files, and other files, with
`INDEX.md` files for progressive disclosure. The context-wiki skill requires
only what an agent needs before it has read anything, and suggests the rest.
Each wiki's `README.md` and `AGENTS.md` say which suggestions it follows.
Decided on 2026-09-30. Supersedes
[0002](0002-flat-context-wiki-layout.md).

Required in every wiki:

- `README.md` and `AGENTS.md` at the root, with `CLAUDE.md` a symlink to
  `AGENTS.md`. They are where an agent learns what goes on in this wiki.
- `name` and `description` frontmatter on every note, and `INDEX.md` files
  generated from it. Notes use `name`, as skills do, instead of `title`.

Also firm: the writing guidance (distill, keep entries short, mark guesses,
write for a reader in another context), and no always-loaded agent rules
([0003](0003-no-rules-in-context-wikis.md)).

Everything else is a suggestion with a reason: a skills folder with its
`.claude/skills` and `.agents/skills` symlinks, a `sources/` folder with a
`date` field for distilled material, an `inbox/` for raw material, rooted
links, a glossary, tags. `init-wiki.sh` creates only the root files and the
skills folder with its symlinks. It no longer creates `inbox/`, `sources/`
or `TAGS.md`.

## Why

A review of the skill on 2026-09-28 found that every inconsistency in it
was a rule stated in more than one place:

- 0002 required every tool that walks entries to skip `agent-skills/` and
  `inbox/`. SKILL.md, the lint checklist and 0002 said so; no tool did, and
  the index generator created index files inside `agent-skills/`.
- SKILL.md and the lint checklist said `INDEX.md`; the generator wrote
  `index.md`.
- The `.gitignore` template existed in two copies that had drifted apart,
  and the lint checklist pointed to a third place that no longer held it.

Fixed conventions also cost every contributor upkeep that few readers used:
tags and types each needed a definition file kept in sync in the same
commit, and records needed an immutability check that lint could not run,
because nothing marked a file as a record. `sources/` imposed one way of
working on everyone who adopted the skill.

A small core means fewer rules to state twice. A suggestion a wiki adopts
is written once, in that wiki's `AGENTS.md`.

## Considered options

- **A `wiki/` content folder** beside `agent/skills/` and `inbox/`, so tools
  index one folder and need no exclusion list. It fixed the exclusion
  problem but kept the skill in charge of the layout. With the layout a
  suggestion, the generator's `--exclude` option handles whatever a wiki
  wants left out.
- **Optional but recommended tags and types.** In a shared wiki, some
  contributors tag and some do not, so a reader cannot trust a filter by
  tag. A wiki that wants tags states in its `AGENTS.md` that its notes carry
  them.
- **A pre-commit hook in every wiki** that keeps `INDEX.md` files current.
  Git does not activate hooks in a fresh clone, so each clone needs a setup
  step. Parked as an idea (ticket akps-39ff).
