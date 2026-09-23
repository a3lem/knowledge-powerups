---
title: Architecture
description: what the repository holds and how the base plugin, the shared CLIs and the companion plugins relate
---

# Architecture

## Bird's eye view

This repository is one Claude Code plugin, `knowledge-powerups`, together
with the marketplace that serves it. The product is knowledge conventions:
bodies of knowledge an agent loads as skills, so that what one session
learns is findable by the next. The repo root is the plugin root, so
`.claude-plugin/` holds both the marketplace manifest and the plugin
manifest, and everything the plugin ships sits at the top level.

Skills are grouped by the knowledge store they serve. `skills/code-docs/`
serves a code base's `docs/` and concerns engineers; `skills/context-wiki/`
serves a store that outlives any single repository; `skills/tools/` holds
what the other groups lean on. Plugins that need harness integration
(hooks, agents) live under `plugins/` as optional companions, each its own
marketplace entry, so the base plugin stays knowledge-only.

## Codemap

- **.claude-plugin/** -- `marketplace.json` lists the base plugin with
  source `./` and each companion with source `./plugins/<name>`.
  `plugin.json` names every skill directory explicitly, because grouped
  skills sit one level deeper than Claude Code scans on its own.
- **skills/code-docs/** -- five knowledge skills for `docs/`. `docs-folder`
  holds the layout itself and, under `references/`, the procedure for
  adopting it, with the scaffold script under `scripts/`.
  `architecture-md`, `changelog-md` and `decision-records` cover individual
  parts of the layout. `incremental-specs` declares `docs-folder` as a
  prerequisite and bundles `gen-spec-codes.py`.
- **skills/tools/index-md/** -- one skill wrapping the index generator. Its
  `scripts/generate_index.py` is a symlink into `clis/index-gen/`; an
  installed copy of the skill carries the file itself.
- **skills/context-wiki/** -- one skill, still empty. The conventions are
  decided but unwritten; see ticket akps-468d.
- **clis/index-gen/** -- `generate_index.py`, the only shared executable in
  the repo. It regenerates the list in a directory's `index.md` from the
  directory's members, merging additively rather than overwriting: a
  hand-written label or description survives, and a `<!-- pinned -->` block
  is copied through untouched. Stdlib-only, so a copy runs anywhere
  `python3` does. Covered by `test_generate_index.py`, whose tests cite the
  statements they verify in `docs/specs/directory-index.md`.
- **plugins/agent-memory/** -- the companion with moving parts.
  `memoryctl.py` holds the deterministic verbs, `hooks.json` compels them at
  session boundaries, and the skills plus the `memory` agent carry the
  judgment. It reaches the generator through a symlink in its `scripts/`
  that the installer dereferences. Its own `docs/architecture.md` describes
  the three layers.
- **docs/** -- this repository's own docs, following `docs-folder`.
  `specs/` and `decisions/` hold the base plugin's reference material.

## Cross-cutting concerns

- **Knowledge before procedure.** A skill leads with the convention; acting
  on it is a separate step. A procedure that belongs to a convention ships
  inside that skill as a reference file, as adopting the layout does inside
  `docs-folder`, rather than as a skill of its own. Skill names carry the
  noun (`docs-folder`, `index-md`); the plugin prefix is the same for all.
- **One plugin, so cross-skill references resolve.** `incremental-specs`
  names `docs-folder` as a prerequisite and `docs-folder` points at
  `index-md`; both live in the same plugin, so a reference never dangles.
  A companion names base skills by full name and degrades to guidance-only
  when the base plugin is absent.
- **Two installers, one wording.** A Claude Code install copies the whole
  repo into the plugin cache, so `clis/` travels with the skills. An
  `npx skills` install copies a single skill directory and dereferences
  symlinks, so a skill that needs an executable keeps a symlink to it under
  its own `scripts/` and names it relative to its own base directory, never
  through `${CLAUDE_PLUGIN_ROOT}`.
- **Rendered surfaces.** In `agent-memory` only, several files are generated
  from `.shablon/templates/` with facts pulled from `memoryctl.py`, so the
  enforcing code is their single source. Those files carry a header saying
  so. Edit the template, then run `shablon generate`.
- **This repository follows its own conventions.** `docs-folder` governs
  the `docs/` trees here. A companion under `plugins/` is a project of its
  own and keeps its own `docs/`; this top-level one carries the base
  plugin's material and anything cross-cutting.
