## ADD

- `compile` produces no output when `MEMORY_ENABLED=0` or
  `MEMORY_CONSOLIDATING=1`.
- The `root` attribute and `$MEMORY_DIR` refer to the session's worktree,
  not the store root; a session only ever sees its own branch.
- The block shows the binding explicitly: `<memory-metadata>` carries a
  `MEMORY_DIR: <worktree path>` line matching the export persisted to
  `$CLAUDE_ENV_FILE`, so the agent reads the assignment rather than
  inferring it from the `root` attribute.
