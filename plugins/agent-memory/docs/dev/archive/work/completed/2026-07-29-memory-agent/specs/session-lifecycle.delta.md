Stacks on the session-lifecycle spec created by the session-worktrees work
item; apply that one first.

Archive note (2026-07-29): the /merge, /discard, and janitor bullets were
applied to `docs/specs/session-lifecycle.md` (the janitor one adjusted:
force-removal is allowed for a discarded session, per the agent
definition). Two claims were not applied. "A session started with
`MEMORY_ENABLED=0` is equivalent to one discarded at birth" -- no branch or
worktree exists to discard, and the spec already says such a session leaves
no trace. The forgetting bullet ("the deleting commit says so") -- sessions
never run git on memory, and the Stop hook's commit message is fixed, so no
commit can carry the reason; if forget-suppression is wanted, it needs a
mechanism first.

## ADD

- `/merge` merges a session's branch into main immediately, without mining
  or cross-branch comparison. The branch remains afterward -- still queued
  for mining. A clean merge is a prescribed, mechanical git operation; a
  conflict is handed to the memory agent's judgment, never resolved blind.
- `/discard` marks a session's worktree (a `.discard` file); the mark is
  undoable until swept. Marked sessions are skipped by consolidation and
  deleted by the janitor. A session started with `MEMORY_ENABLED=0` is
  equivalent to one discarded at birth.
- The janitor deletes a branch and its worktree only when the session is
  not live (transcript mtime past threshold) and the branch is either
  discarded or both merged and mined. Dirty worktrees are never
  force-removed.
- Remembering and forgetting individual memories happen in conversation,
  not through commands. A user-requested forget is honored the same turn;
  the deleting commit says so, so consolidation does not resurrect the
  fact from other branches or transcripts.
