---
title: Architecture
description: what the repository holds and how the plugins relate to each other
---

# Architecture

## Bird's eye view

This repository is a Claude Code plugin marketplace. The product is
knowledge conventions: bodies of knowledge an agent loads as skills, so that
what one session learns is findable by the next. Each plugin owns one
convention and the vocabulary that goes with it.

Five plugins, split by which knowledge store they serve and by audience.
`docs-conventions` and `incremental-specs` serve a code base's `docs/` and
concern engineers; `context-wikis` and `agent-memory` serve stores that
outlive any single repository; `index-md` is used by all of them. A
non-engineer can install the wiki and memory plugins alone.

## Codemap

- **marketplace.json** (`.claude-plugin/`) -- the marketplace manifest: the
  five plugin entries and their descriptions. Each plugin carries its own
  `plugin.json` with an independent version.
- **generate_index.py** (`cli/`) -- the only shared executable in the repo.
  It regenerates the body of a directory's `index.md` from the child files'
  frontmatter, merging additively rather than overwriting. Stdlib-only, so
  any plugin can shell out to it without an install step.
- **docs-conventions** -- knowledge-only. `using-docs` holds the layout
  itself; `architecture-md`, `changelog-md`, and `adrs` cover individual
  parts of it; `adopt-conventions` is the one procedural skill, and the
  repository's only shell script sits under it.
- **incremental-specs** -- knowledge-only. One skill, `using-specs`, which
  declares `docs-conventions:using-docs` as a prerequisite. This is the one
  hard dependency between plugins.
- **index-md** -- one skill wrapping `cli/generate_index.py`. The skill
  assumes the repository checkout, since the script lives two levels above
  the plugin root.
- **context-wikis** -- two skills, both still empty. The conventions are
  decided but unwritten; see the `starting-from-handover` work item.
- **agent-memory** -- the only plugin with moving parts. `memoryctl.py`
  holds the deterministic verbs, `hooks.json` compels them at session
  boundaries, and the skills plus the `memory` agent carry the judgment. Its
  own `docs/architecture.md` describes the three layers.

## Cross-cutting concerns

- **Knowledge before procedure.** A skill leads with the convention; acting
  on it is a separate step. This is why plugin names carry the noun
  (`docs-conventions`) and skill names only distinguish siblings
  (`using-docs`).
- **Plugins do not import each other.** `incremental-specs` names a
  prerequisite skill, and `agent-memory` calls `cli/generate_index.py`, but
  no plugin reads another plugin's files. Installing one plugin without its
  siblings degrades guidance, never function.
- **Rendered surfaces.** In `agent-memory` only, several files are generated
  from `.shablon/templates/` with facts pulled from `memoryctl.py`, so the
  enforcing code is their single source. Those files carry a header saying
  so. Edit the template, then run `shablon generate`.
- **This repository follows its own conventions.** `docs-conventions`
  governs the `docs/` trees here, including the plugins' own. A monorepo
  gives each project its own `docs/`; this top-level one carries
  cross-cutting material only.
