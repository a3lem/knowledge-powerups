New capability -- no reference spec exists yet. On completion this delta
becomes `docs/specs/session-lifecycle.md`.

## ADD

# Session Lifecycle

A session works on its own branch of the memory store in a git worktree;
main receives merges only. The branch list is the consolidation queue.

- With `MEMORY_ENABLED=0`, every memoryctl subcommand exits 0 with no output
  and no side effects: no injection, no worktree, no branch, no validation.
- When the store does not exist, the first session creates it: three tiers,
  a minimal template soul, git init, and a first commit authored as the
  agent.
- At SessionStart the worktree `worktrees/session-<id>` on branch
  `session-<id>` (branched from main) is created if missing and reused if
  present -- so resume continues where the session left off, and resume
  after worktree deletion lands on a fresh branch off current main.
- `MEMORY_DIR` points at the session's worktree and is exported via
  `$CLAUDE_ENV_FILE`, together with the `MEMORY_*` configuration the hook
  resolved (`MEMORY_ROOT_DIR`, `MEMORY_AGENT_ID`), so Bash commands see
  the same configuration the hook did.
- A session commits only to its own branch. Nothing commits to main;
  main's history is merge commits only.
- A session's liveness signal is its transcript's mtime
  (`~/.claude/projects/*/<session-id>.jsonl`); no other lock exists.
- When `MEMORY_CONSOLIDATING=1`, SessionStart performs no injection and no
  worktree creation: a consolidation process never sees compiled memory.
