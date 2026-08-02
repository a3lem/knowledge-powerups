## REPLACE

### OLD

- At Stop, validation runs first; when it passes, `memoryctl commit` commits
  the worktree's uncommitted writes to the session's branch, authored as the
  agent, message `inline writes, session <id>`. A violation blocks the turn
  and nothing is committed. The session never runs git on memory itself.

### NEW

- At Stop, validation runs first; a violation blocks the turn and nothing
  is committed. When it passes and the turn's uncommitted writes added net
  characters to `system/`, `memoryctl system-delta` blocks once with a
  growth report -- per changed file, the net characters added and the
  file's new size as a percentage of the 2,200-character cap, plus the
  total -- asking whether the additions respect the injection's limited
  budget; trimming and confirming are both legitimate answers. The
  continuation's Stop passes through (`stop_hook_active` in the hook
  JSON). Then `memoryctl commit` commits the worktree's uncommitted
  writes to the session's branch, authored as the agent, message `inline
  writes, session <id>`. No `system/` additions, or net shrinkage: the
  check is a no-op. The session never runs git on memory itself.

Reason: brevity work item. A per-turn reflection on system/ growth, at the
one moment the harness can still reach the model, ordered so a trim in the
continuation lands in the same auto-commit.
