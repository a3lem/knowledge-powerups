---
title: Memory store
description: Layout and content rules for an agent's memory directory
---

<!-- Rendered from .shablon/templates/docs/specs/memory-store.md; edit that template, then run `shablon generate`. -->

# Memory Store

An agent's memory is a git repository of markdown files at
`$MEMORY_ROOT_DIR/<agent-id>/`, maintained by the agent itself.

- The memory root defaults to `{{ defaults.root }}/` and the agent id to
  `{{ defaults.agent_id }}`; the environment variables `MEMORY_ROOT_DIR` and
  `MEMORY_AGENT_ID` override them, as do `ROOT_DIR` and `AGENT_ID` entries
  in `<cwd>/.agents/memory.conf` (the environment wins).
- The store holds exactly two top-level directories: `main/`, the main
  branch's checkout with the git dir inside it, and `worktrees/`, the
  session checkouts beside it -- checkouts never nest. Content rules below
  apply within a checkout.
- A checkout has three content directories, split by what enters the prompt:
  `system/` (injected in full), `reference/` (index only), `skills/`
  (procedural; roster injected, contents read on demand). Each tier and
  reserved subdirectory carries a `.gitkeep` so the layout survives onto
  every branch and worktree.
- `system/` reserves two subdirectories: `human/` for knowledge of the
  human, `core/` for standing rules -- self-corrections among them.
- `system/human/human.md` is the human's identity file (who they are:
  name, role, working context); `system/human/preferences/` holds their
  preferences, one small file each. A memory that mentions the human
  writes `the [[system/human/human.md|human]]`, never their name -- the
  name lives only in `human.md`, and every mention of them is one exact
  grep.
- Every memory file requires a `description` in its frontmatter; for
  `reference/` files it is the only signal the injected index shows.
- Memory files are written in the first person, descriptions included:
  the agent speaking about what it knows, not a system describing its
  data. Convention, not validated.
- Memory favors small, nearly atomic files -- one fact, rule, or pattern
  per file, linked where they relate -- over files that accumulate lists.
  Convention, not validated.
- A memory file may carry a frontmatter `name` matching
  `^[A-Za-z][A-Za-z0-9._-]*$`; it overrides the file stem as the file's tag
  in the injection and reads relative to its parent directory
  (`system/human/preferences/directness.md` renders as `directness`, not
  `human-preferences-directness`).
- Files in `system/` are capped at {{ caps.system_file }} characters each; the compiled
  injection is capped at {{ caps.injection }} characters in total.
- `system/soul.md` is the agent's single identity file: how it sees
  itself -- positions, taste, self-conception -- and any role the human
  assigns (name, backstory, character), recorded as given and kept apart
  from what the agent makes of it. Chosen identity belongs there,
  invented events do not. A human never edits a memory file directly.
- A fresh store scaffolds minimal template versions of the soul and the
  human identity file; everything real accumulates from lived
  sessions.
- `reference/history/` holds dated episodic notes named
  `YYYY-MM-DD-<slug>.md`, staged for consolidation; nothing lives there
  permanently.
- `reference/projects/` holds one directory per code base.
- A `reference/` directory carries an `index.md`: its frontmatter
  `description` is authored and is what the injected index shows for the
  directory; its body is a generated table of contents (the shared
  `cli/generate_index.py`, reached via the index-md skill or
  `memoryctl index`), regenerated after files are added, removed, or
  moved -- never written by hand. An entry whose file is gone is dropped
  on regeneration. SessionStart and SessionEnd refresh existing indexes;
  creating one is authored work. The scaffold seeds `index.md` for the
  two reserved reference directories.
- A link from one memory file to another is a wikilink whose payload is the
  path from the memory root (the checkout), extension included:
  `[[reference/projects/klassifai/document-types.md]]`, optionally
  `[[path|label]]`. The target need not exist yet: an unresolved link is a
  forward pointer to a file worth writing. Markdown links are reserved for
  targets outside the store.
- Each `skills/<dir>/SKILL.md` carries frontmatter `name` and `description`;
  these are agent skills, not memory files.
- `.claude/skills` is a tracked symlink to `skills/`, so Claude Code
  launched with `--add-dir <store>/main` discovers the tier as agent skills
  (verified live: discovery follows the directory-level symlink). Discovery
  sees the `main/` checkout, so a session's new or edited skills become
  loadable only after they land in main.
- Commits are authored as the agent (`<agent-id> <agent-id>@agents.local`).
