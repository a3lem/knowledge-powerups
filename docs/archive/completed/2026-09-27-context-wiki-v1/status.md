---
title: Status
description: Closing state of v1 of the context-wiki skill at archival
---

# Status

Archived complete on 2026-09-27, on branch `context-wiki-v1`. Tracked as
akps-468d.

`SKILL.md` has a description and covers, beyond Adriaan's own draft:
entries as descriptions and records, preferences written as facts with
their reason, the `rules/` folder, `AGENTS.md`, and a Setup section with
three references -- `CONTEXT_WIKI_DIRS` for any agent,
`claude-integration.md` for Claude Code, and `init-wiki.md` with the
`init-wiki.sh` script for creating a wiki. The script was tested on a fresh
folder, a re-run, a clone, a folder inside another repository, a
conflicting file, and macOS bash 3.2.

The spec delta was dropped instead of applied, by Adriaan's choice: a
natural-language spec adds nothing to a natural-language skill, and the
skill holds all of it. So goal.md's criterion that `SKILL.md` agrees with
`docs/specs/context-wiki.md` no longer applies, and approach.md's link to
the delta points at nothing. The README and `docs/architecture.md` now
describe the skill as written.

Not done: the verification in approach.md, where a fresh agent given only
the skill adds an entry to a scratch wiki. The root `INDEX.md` a new wiki
needs depends on the pending rename of `index.md` to `INDEX.md` on the
`uppercase-index-md` branch; until it lands, the index-md generator writes
`index.md`.
