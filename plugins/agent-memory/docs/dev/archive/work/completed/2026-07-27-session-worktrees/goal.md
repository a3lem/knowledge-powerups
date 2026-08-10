# Goal: Session Worktrees

Ticket: akps-5405.

## Problem

The prototype has one writer working directly on main. The settled design
needs many: parallel sessions, a fast-path merge, and a consolidation agent,
without two writers ever sharing a branch. It also needs a store that
bootstraps itself and a harness-level kill switch.

## Desired outcome

Each session works on its own branch `session-<id>` in a worktree
`worktrees/session-<id>`, created at SessionStart if missing. The branch
list becomes the consolidation queue: branch exists ⇔ session unprocessed.
Main receives merges only. The store scaffolds itself on first use
(inside the worktree verb's create-if-missing path -- no separate init
command), and
`MEMORY_ENABLED=0` disables every entry point silently.

## Success criteria

- Two concurrent sessions write and commit without touching each other.
- Killing a session and resuming it later lands in the same worktree;
  resuming after its worktree was deleted lands in a fresh branch off
  current main, without error.
- With no store present, the first session creates one (tiers, template
  soul, git init, first commit authored as the agent) and works normally.
- With `MEMORY_ENABLED=0`: no injection, no worktree, no branch, no
  validation -- the session leaves no memory trace.
- With `MEMORY_CONSOLIDATING=1`: no injection and no worktree, so a
  headless consolidation run never sees compiled memory.
