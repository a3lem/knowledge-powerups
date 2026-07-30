---
name: sync
description: Load this skill when the user invokes /sync or asks to share this session's memory now -- land the current session's branch in main immediately when it merges cleanly, without waiting for a consolidation pass. The branch stays queued.
---

# Sync

/sync lands this session's memory in main now, so a parallel or later session
sees it without waiting for consolidation. It is also how a skill written this
session becomes loadable: the harness discovers skills from main. It shares
content only -- no mining, no cross-branch reconciliation -- and the branch
survives, still queued.

The current session's branch is named by its `MEMORY_DIR`: the worktree is
`worktrees/session-<id>` under the store root, so the branch is
`session-<id>`.

Spawn the `memory` agent (Agent tool, subagent_type `memory`) with mode `sync`
and that branch name. Its prescribed sequence: first commit any uncommitted
writes in the session's worktree, authored as the agent (the end-of-turn
auto-commit usually leaves it clean, but a sync of stale state shares
nothing); then, from the store's `main/` checkout, attempt `git merge` of the
session branch into main, authored as the agent. A clean merge lands in
seconds. A conflict aborts the sync -- the agent reports the disagreement and
leaves the resolution to a consolidation pass. Relay its report.
