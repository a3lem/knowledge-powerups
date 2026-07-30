---
title: Injection
description: How memory is compiled into the prompt at session and subagent start
---

# Injection

`memoryctl compile` prints the memory as one block; a SessionStart hook puts
it in the system prompt, so awareness of memory never depends on loading a
skill.

- The block is wrapped in `<agent-memory agent="<agent-id>" root="<store
  path>">`. The `root` attribute carries the literal path for tools that do
  not expand environment variables.
- The block opens with `<memory-instructions>`: the body is bare prose from
  the plugin's `prompts/injected-instructions.md`; compile adds the
  wrapping tag at render time, as it does for every other tag.
- `system/` is rendered in full: `soul.md` first, then files before
  subdirectories, directories as nested tags. Each file renders as
  `<{name}><path>$MEMORY_DIR/<rel></path><description>...</description>`
  followed by its body verbatim.
- `reference/` renders as `<memory-index>`: labels and descriptions only, no
  contents, with a note saying files are read on demand. A file's
  description comes from its own frontmatter; a directory's comes from the
  authored frontmatter of its `index.md` (without one, the entry is
  name-only). The generated body of an `index.md` is never injected, and
  `index.md` files are omitted from the file listing -- their description
  already sits on the directory line.
- The index is pruned below `reference/projects/`: project names and
  descriptions appear, their contents do not.
- `skills/` renders as `<memory-skills>`, one `name -- description` line per
  skill. The roster reflects the session's branch; loadable skills come from
  main via `.claude/skills` discovery (see the memory-store spec).
- `<memory-metadata>` closes the block: agent id, a `MEMORY_DIR: <worktree
  path>` line stating the binding explicitly, compile time (UTC), memory
  HEAD (short), count of entries staged in `reference/history/`, and the
  consolidation queue depth (count of `session-*` branches).
- The `root` attribute and `$MEMORY_DIR` refer to the session's worktree,
  not the `main/` checkout; a session only ever sees its own branch.
- `memoryctl subagent-context`, run by a SubagentStart hook, injects the
  same compiled block into every subagent via JSON
  `hookSpecificOutput.additionalContext` (SubagentStart stdout is not added
  to context), with the read-only preamble from
  `prompts/subagent-preamble.md` in place of the maintenance instructions.
  The memory agent (`agent_type` `memory`, plugin-scoped included) is
  skipped: consolidation works from the outside view.
- `memoryctl env` prints `export MEMORY_DIR=<session worktree>` plus
  forwarding exports for `MEMORY_ROOT_DIR` and `MEMORY_AGENT_ID`, and for
  `MEMORY_SESSION`, `MEMORY_SESSION_ID`, and `MEMORY_SESSION_DIR` when
  set; a SessionStart hook appends them to
  `$CLAUDE_ENV_FILE`, so shell commands run with the configuration the
  hook resolved. The exports carry resolved values -- a setting read from
  `<cwd>/.agents/memory.conf` is forwarded as its environment variable, so
  Bash commands see the same configuration wherever they cd to.
- With `MEMORY_SESSION=` (set empty), compile binds `main/` and swaps the
  maintenance instructions for the read-only preamble in
  `prompts/sessionless-preamble.md`; `MEMORY_DIR` then names the `main/`
  checkout, and nothing is created or committed.
- `compile` and `subagent-context` produce no output when
  `MEMORY_ENABLED=0`.
- When the store does not exist, compile prints nothing and exits clean;
  env still prints its exports -- the variables cost nothing and name
  where the store will live. Hooks never fail for a user without this
  agent's memory.
