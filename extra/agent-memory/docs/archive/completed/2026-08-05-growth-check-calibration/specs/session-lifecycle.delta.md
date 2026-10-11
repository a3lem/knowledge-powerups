## REPLACE

### OLD

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

### NEW

- At Stop, validation runs first; a violation blocks the turn (exit 2)
  and nothing is committed. When it passes and the turn's uncommitted
  writes grew `system/` past a floor -- 300 net characters in total, or
  any grown file crossing half its 2,200-character cap --
  `memoryctl system-delta` blocks once, as hook JSON (`decision:
  block`, with a `systemMessage` one-liner for the human), not as an
  error: a growth report per changed file with headroom against the
  cap, and the question whether the additions are worth their permanent
  place in the injection. Confirming is a legitimate answer -- the
  expected one while files sit under half cap -- and a trim drops or
  moves content, never compresses sentences into fragments. Commit is
  skipped on a block, so a trim lands in the turn's single auto-commit;
  the continuation's Stop passes through (`stop_hook_active`) and then
  `memoryctl commit` commits the worktree's uncommitted writes to the
  session's branch, authored as the agent, message `inline writes,
  session <id>`. Additions under the floor, net shrinkage, or no
  `system/` edits: the check is silent and commit runs directly. The
  session never runs git on memory itself.

Reason: observed live -- the exit-2 path rendered the reflection as
"Stop hook error" and primed an over-trim into fragments while every
file sat under 20% of cap. The check becomes hook JSON with a floor and
wording that names the expected answer; validate alone keeps exit 2.
