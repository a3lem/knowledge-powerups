---
title: Memory store
description: Layout and content rules for an agent's memory directory
---

# Memory Store

An agent's memory is a git repository of markdown files at
`$MEMORY_ROOT_DIR/<agent-id>/`, maintained by the agent itself.

- The memory root defaults to `~/.agents/memories/` and the agent id to
  `my-claude`; the environment variables `MEMORY_ROOT_DIR` and
  `MEMORY_AGENT_ID` override them.
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
  (`system/human/identity.md` renders as `identity`, not `human-identity`).
- Files in `system/` are capped at 2,200 characters each; the compiled
  injection is capped at 24,000 characters in total.
- `system/soul.md` holds identity, written as positions, not traits. It is
  edited like any other memory file. A fresh store scaffolds a minimal
  template soul; positions grow from lived sessions.
- `reference/history/` holds dated episodic notes named
  `YYYY-MM-DD-<slug>.md`, staged for consolidation; nothing lives there
  permanently.
- `reference/projects/` holds one directory per code base.
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
- A `reference/projects/<name>/` directory contains a `<name>.md` file
  describing the project; its `description` doubles as the directory's entry
  in the injected index.
