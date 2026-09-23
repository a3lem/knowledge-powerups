---
title: Status
description: Closing state of the reorg at archival
---

# Status

Archived complete on 2026-09-23. Merged into main as 2c44f04 from branch
`worktree-fundamental-reorg`; ticket akps-9c6e closed.

Every step in approach.md landed. Verified before merging (2026-09-22):

- The generator's 172 tests pass from `clis/index-gen/`, again on merged
  main.
- A Claude Code install from the branch (marketplace added from the local
  directory, both plugins installed at local scope, then removed) lists all
  seven base skills by their new names, grouped ones included. The cache
  holds the whole repo; the index-md symlink survives as a relative link
  and resolves; agent-memory's symlink arrives as a real file and
  `memoryctl` finds it. The generator runs from both cached locations.
- `npx skills add` finds 14 skills (7 base minus context-wiki, plus
  agent-memory's 8), copies real files including `references/` and
  `scripts/`, and the copied generator runs.
- No reference to an old plugin name or path remains outside `docs/archive/`.

Reconciled at merge: main's index.md wording for glossary and architecture
was already carried by the rewrites; the two docs-conventions work items
moved to `docs/wip/` with a note mapping the old skill names.

Not done here: re-adding the marketplace on the maintainer's machine under
its new name `knowledge-powerups`, by the human's choice. And
`skills/context-wiki/SKILL.md` still has an empty description, so
`npx skills` skips it; that is akps-468d's skill to write.
