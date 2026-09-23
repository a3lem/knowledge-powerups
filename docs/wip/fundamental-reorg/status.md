---
title: Status
description: Where the reorg stands
---

# Status

Steps 1 through 7 of approach.md are done on branch
`worktree-fundamental-reorg` (from main at c986737); step 8 is partly done.
Tracked as ticket akps-9c6e. Nothing is committed yet: the whole change set
is staged in the worktree.

Verified on 2026-09-22:

- The generator's 172 tests pass from `clis/index-gen/`.
- A Claude Code install from the worktree (marketplace added from the local
  directory, both plugins installed at local scope, then removed again)
  lists all seven base skills by their new names, including the grouped
  ones. The cache holds the whole repo; the index-md symlink survives as a
  relative link and resolves; agent-memory's symlink arrives as a real file
  and `memoryctl` finds it. The generator runs from both cached locations.
- `npx skills add <worktree>` finds 14 skills (7 base minus context-wiki,
  plus agent-memory's 8), copies real files including `references/` and
  `scripts/`, and the copied generator runs.
- No reference to an old plugin name or path remains outside `docs/archive/`
  and this item.

Noted, not fixed: `skills/context-wiki/SKILL.md` has an empty description,
so `npx skills` skips it with a warning while Claude Code lists it. That is
akps-468d's skill to write.

Left for the human:

- Commit the staged change set.
- Reconcile with main before merging. Main carries uncommitted edits to
  `docs/glossary.md` and `docs/architecture.md` (both files are rewritten
  here), the deletion of the empty `open-knowledge-format` skill (also done
  here), and two untracked work items under
  `plugins/docs-conventions/docs/wip/`, which need a new home under
  `docs/wip/` since that plugin directory is gone.
- After merging, re-add the marketplace on this machine: the old
  registration `agent-knowledge-plugins` points at the main checkout and
  the manifest is now named `knowledge-powerups`.
- Then archive this item.
