---
name: Architecture
description: what the repository holds and how the two core plugins, the shared CLIs and the extension plugins relate
---

# Architecture

## Bird's eye view

This repository is a Claude Code marketplace, `knowledge-powerups`, that
serves several plugins. The product is knowledge conventions: bodies of
knowledge an agent loads as skills, so that what one session learns is
findable by the next.

The core plugins under `plugins/` are split by audience. `context-wikis`
serves a store that outlives any single repository, and is useful to
anyone who works with an agent, engineer or not. `code-knowledge` serves a
code base's `docs/` and concerns engineers, who usually install both.
Plugins for power users that need harness integration (hooks, agents) live
under `extra/` as extensions, each its own marketplace entry, so the core
plugins stay knowledge-only.

## Codemap

- **.claude-plugin/** -- `marketplace.json` lists each plugin with its
  directory as source: `./plugins/<name>` for the core plugins,
  `./extra/<name>` for extensions. Each plugin keeps its skills in its own
  `skills/`, which Claude Code scans without a list in `plugin.json`.
- **plugins/context-wikis/skills/context-wiki/** -- one skill. `SKILL.md`
  holds what every wiki has, the writing guidance, and defaults a wiki can
  adopt. `references/` covers setup: the `CONTEXT_WIKI_DIRS` variable,
  loading wikis into Claude Code, and creating a wiki, with `init-wiki.sh`
  under `scripts/`. It has no spec in `docs/specs/`: the skill is itself
  the natural-language statement of the conventions.
- **plugins/context-wikis/skills/index-md/** -- the index generator and the
  one skill that runs it. `scripts/generate_index.py` regenerates the list
  in a directory's `INDEX.md` from the directory's members, merging
  additively rather than overwriting: a hand-written label or description
  survives, and a `<!-- pinned -->` block is copied through untouched.
  Stdlib-only, so a copy runs anywhere `python3` does. Other skills reach
  it through `/context-wikis:index-md`, never by path.
  `tests/test_generate_index.py` covers it, and its tests cite the
  statements they verify in `docs/specs/directory-index.md`. It ships with
  context wikis because every wiki depends on it; for the other plugins it
  is optional.
- **plugins/code-knowledge/skills/** -- five knowledge skills for `docs/`.
  `/docs-folder` holds the layout itself and, under `references/`, the
  procedure for adopting it, with the scaffold script under `scripts/`.
  `/architecture-md`, `/changelog-md` and `/decision-records` cover
  individual parts of the layout. `/incremental-specs` declares
  `/docs-folder` as a prerequisite and bundles `gen-spec-codes.py`.
  `drafts/` holds skills that are not shipped yet.
- **extra/agent-memory/** -- the extension with moving parts.
  `memoryctl.py` holds the deterministic verbs, `hooks.json` compels them at
  session boundaries, and the skills plus the `memory` agent carry the
  judgment. Its hooks run the generator outside any skill, so it reaches
  the file through a symlink in its `scripts/` into
  `plugins/context-wikis/skills/index-md/scripts/`, which the installer
  dereferences. Its own `docs/architecture.md` describes the three layers.
- **docs/** -- this repository's own docs, following `/docs-folder`.
  `specs/` and `decisions/` hold the core plugins' reference material.

## Cross-cutting concerns

- **Knowledge before procedure.** A skill leads with the convention; acting
  on it is a separate step. A procedure that belongs to a convention ships
  inside that skill as a reference file, as adopting the layout does inside
  `/docs-folder`, rather than as a skill of its own. Skill names carry the
  noun (`docs-folder`, `index-md`).
- **Hard dependencies stay inside one plugin.** `/incremental-specs` names
  `/docs-folder` as a prerequisite, and `/context-wiki` cannot work without
  `/index-md`; each pair ships in the same plugin, so these references never
  dangle. A reference across plugins is optional: `/docs-folder` points at
  `/context-wikis:index-md` for generating indexes, and the `agent-memory`
  skills invoke the index-md skill. Both degrade to guidance-only when
  `context-wikis` is absent.
- **Two installers, one wording.** A Claude Code install copies a plugin's
  directory into the plugin cache, dereferencing symlinks within the
  marketplace. An `npx skills` install copies a single skill directory and
  also dereferences symlinks. So a skill keeps its executables under its
  own `scripts/` and names them relative to its own base directory, never
  through `${CLAUDE_PLUGIN_ROOT}`.
- **Rendered surfaces.** In `agent-memory` only, several files are generated
  from `.shablon/templates/` with facts pulled from `memoryctl.py`, so the
  enforcing code is their single source. Those files carry a header saying
  so. Edit the template, then run `shablon generate`.
- **This repository follows its own conventions.** `/docs-folder` governs
  the `docs/` trees here. An extension under `extra/` is a project of its
  own and keeps its own `docs/`; this top-level one carries the core
  plugins' material and anything cross-cutting.
