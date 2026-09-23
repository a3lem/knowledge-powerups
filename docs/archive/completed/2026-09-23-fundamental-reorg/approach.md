---
title: Approach
description: Design decisions, the migration plan in order, and how each step is verified
---

# Approach

## Design

**One base plugin at the repo root.** `.claude-plugin/` holds both
`marketplace.json` and `plugin.json`. The marketplace lists
`knowledge-powerups` with `"source": "./"` and each companion with
`"source": "./plugins/<name>"`. Precedent and installer behaviour are in
research.md.

**Skill groups are directories, declared in the manifest.** `plugin.json`
lists every grouped skill directory under `skills`, because Claude Code only
scans one level on its own. A group is for people reading the repo; the
agent sees `knowledge-powerups:<skill-name>`, so names stay unique across
groups and the description does the disambiguating.

**Skill names change where the plugin name used to carry meaning.** With
one plugin, `using-docs` loses the `docs-conventions:` prefix that told the
reader what docs. Renames:

| today | new |
|---|---|
| docs-conventions:using-docs | docs-folder |
| docs-conventions:adopt-conventions | folded into docs-folder, see below |
| docs-conventions:architecture-md | architecture-md |
| docs-conventions:changelog-md | changelog-md |
| docs-conventions:decision-records | decision-records |
| incremental-specs:using-specs | incremental-specs |
| index-md:index-md | index-md |
| context-wikis:context-wikis | context-wiki |

Every existing skill survives except `adopt-conventions`, which stops being
a skill of its own. Its procedure becomes a reference file under
`docs-folder/references/adopting.md`, and `scaffold_docs.sh` moves to
`docs-folder/scripts/`. The `docs-folder` SKILL.md points at both.

**Shared executables live in `clis/`, source of truth, reached two ways.**
Under Claude Code the whole repo is the plugin, so
`${CLAUDE_PLUGIN_ROOT}/clis/index-gen/generate_index.py` resolves. Under
`npx skills` only the skill directory travels, so `skills/tools/index-md/`
carries a symlink `scripts/generate_index.py -> ../../../../clis/index-gen/generate_index.py`
that the installer turns into a copy. The SKILL.md names the script by its
path relative to the SKILL.md and never through the variable, so one wording
serves both installs. The generator stays stdlib-only and single-file so
the copy is self-contained.

`agent-memory` reaches the generator the same way: a symlink inside
`plugins/agent-memory/scripts/` to `../../../clis/index-gen/generate_index.py`.
It targets elsewhere in the same marketplace, so a marketplace install
dereferences it. `memoryctl.py` resolves the generator next to itself
instead of four levels up.

**Per-plugin docs fold into the top-level `docs/`** for everything that
joins the base plugin. The monorepo rule in `docs-folder` ("each project
gets its own docs/") no longer applies to skills that are one project.
`plugins/agent-memory/docs/` stays, since it remains its own plugin.

**Not touched by this item.** The content of any SKILL.md beyond path and
name references. The context-wiki skill body (ticket akps-468d). The wiki
companion plugin (ticket akps-efa9). `agent-memory` internals beyond the
generator path.

## Plan

Each step leaves the tree consistent enough to commit. Verification is
listed with the step that makes it possible.

1. **Move the generator.** `git mv cli clis/index-gen`. Fix the test's
   run instructions. Verify: `cd clis/index-gen && python3 -m unittest -v`.
2. **Create the base plugin.** Write `.claude-plugin/plugin.json`
   (`knowledge-powerups`, version 0.1.0, `skills` list). Rewrite
   `marketplace.json`: rename the marketplace to `knowledge-powerups`, one
   entry with `source: "./"`, one for `agent-memory`, drop the four absorbed
   plugins. The maintainer's machine needs a marketplace re-add afterwards;
   nobody else has installed from it yet.
3. **Move the skills.** `git mv` each skill directory into its group,
   rename directories per the table, and update the `name` field in each
   frontmatter. Fold `adopt-conventions` into `docs-folder` as described
   under Design. Delete the four absorbed plugins' `.claude-plugin/` and
   README.md after folding their content (step 6).
4. **Rewire references.** Replace every `/docs-conventions:`,
   `/incremental-specs:`, `/index-md:` and `/context-wikis:` skill reference
   with `/knowledge-powerups:<new-name>`. Replace the
   `${CLAUDE_PLUGIN_ROOT}/../../cli/...` lines in the index-md SKILL.md with
   the relative-path wording and add the symlink. In `agent-memory`, add the
   symlink, point `INDEX_GENERATOR` at it, and update the README,
   architecture, spec, how-to and the `.shablon` templates that name
   `cli/generate_index.py`; regenerate with `shablon generate`. Verify:
   `grep -rn 'cli/generate_index\|CLAUDE_PLUGIN_ROOT}/\.\.' .` is empty
   outside `docs/archive/`.
5. **Fold the docs.** `git mv plugins/docs-conventions/docs/decisions/0001-flat-docs-layout.md docs/decisions/` and
   `plugins/index-md/docs/specs/directory-index.md docs/specs/`. Move the
   two plugins' `docs/archive/completed/` items under the top-level
   archive, keeping their date prefixes. Update the statement references in
   the generator's tests if the spec path is cited there.
6. **Rewrite the top-level docs.** README: one install command, the skill
   list grouped as in the tree, companions as a separate section.
   architecture.md: new bird's eye view and codemap. glossary.md: the
   index.md entry and any plugin-name terms. Fold each absorbed README's
   useful content into the README or the relevant SKILL.md before deleting
   it.
7. **Verify installs.** From a clean marketplace registration:
   `/plugin marketplace add` from the local directory, install
   `knowledge-powerups` and `agent-memory`, confirm every skill is listed
   with the expected name, run the index-md skill on a scratch directory.
   Then `npx skills add <local path>` into a scratch project and confirm
   the grouped skills appear and the copied `scripts/generate_index.py` is
   a real file that runs. Record the result in status.md.
8. **Reconcile with main** (see status.md), archive this item, and bump
   `agent-memory` to 0.3.1 for the generator path change.

## Decided on review (2026-09-22)

- All existing skills survive. `adopt-conventions` alone is demoted to a
  reference file inside `docs-folder`.
- The marketplace is renamed to `knowledge-powerups` in step 2.
- No placeholder for `plugins/context-wiki-companion/`; that is akps-efa9's
  job.

## Possible follow-up, not part of this item

The Claude Code plugin layout lists a `bin/` directory whose executables
are put on PATH while the plugin is enabled. If that holds, a
`bin/index-gen` wrapper would let the index-md skill run `index-gen <dir>`
as a plain command under a plugin install, with no path in the SKILL.md at
all. It would not help an `npx skills` install, which has no PATH
mechanism, so the relative-path symlink from this plan stays regardless.
Untested; one experiment during step 7 settles whether it is worth adding.
