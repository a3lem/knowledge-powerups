---
title: Session lifecycle
description: How a session's memory branch is born, used, committed, and queued
---

# Session Lifecycle

A session works on its own branch of the memory store in a git worktree
and never writes main; only the memory agent commits there. The branch
list is the consolidation queue.

- With `MEMORY_ENABLED=0`, every memoryctl subcommand exits 0 with no output
  and no side effects: no injection, no worktree, no branch, no validation.
- When the store does not exist, the first session creates it: a `main/`
  checkout holding three tiers and their reserved subdirectories (kept on
  every branch via `.gitkeep`), minimal templates for the soul and human
  identity, git init, and a first commit authored as the agent, with
  `worktrees/` beside it for the session checkouts.
- At SessionStart the worktree `worktrees/session-<id>` on branch
  `session-<id>` (branched from main) is created if missing and reused if
  present -- so resume continues where the session left off. A deleted
  worktree is reattached to its surviving branch; only when the branch
  too is gone does a resume start fresh off current main.
- The session layer is configurable. `MEMORY_SESSION=` (set empty) runs
  the session with no branch or worktree: memory is injected read-only
  from main, and `worktree`, `commit`, and `session-end` are no-ops.
  `MEMORY_SESSION_ID=<id>` pins the session id -- it beats the hook JSON,
  the `--session` flag still wins -- so sessions started with the pin
  share one branch and worktree. `MEMORY_SESSION_DIR=<path>` puts the
  worktree at an explicit path instead of `worktrees/session-<id>`, a
  debugging aid; branch name, markers, and auto-commit are unchanged.
- SessionStart also ensures the worktree carries the skills tier and the
  `.claude/skills` discovery symlink, healing stores that predate them; the
  auto-commit carries the link onto the branch, and the next merge lands it
  in main, where discovery actually looks.
- SessionStart and SessionEnd refresh the generated index.md bodies in the
  worktree's `reference/` tree (`memoryctl index`, refresh-only: an
  index.md is never created by machinery, since creation means authoring
  its description). A SessionStart refresh is committed by the turn's
  auto-commit; a SessionEnd refresh stays uncommitted until unify's
  commit-leftovers step picks it up.
- `MEMORY_DIR` points at the session's worktree and is exported via
  `$CLAUDE_ENV_FILE`, together with the `MEMORY_*` configuration the hook
  resolved (`MEMORY_ROOT_DIR`, `MEMORY_AGENT_ID`), so Bash commands see
  the same configuration the hook did.
- At Stop, validation runs first; when it passes, `memoryctl commit` commits
  the worktree's uncommitted writes to the session's branch, authored as the
  agent, message `inline writes, session <id>`. A violation blocks the turn
  and nothing is committed. The session never runs git on memory itself.
- A session commits only to its own branch; nothing a session does touches
  main. Main changes only through the memory agent: merges from
  consolidation and sync, and refinement commits between passes.
- Liveness is marked, not guessed: SessionStart writes an untracked
  `.active` file in the worktree and SessionEnd removes it
  (`memoryctl session-end`). The transcript path is recorded in the
  untracked `.session` file, refreshed at every SessionStart. A crashed
  session leaves `.active` behind; its branch then lingers until the
  session is resumed and ended properly, or discarded.
- `/sync` merges the session's branch into main immediately when the merge
  is clean, without mining or cross-branch reconciliation -- performed by
  the memory agent, which commits any uncommitted worktree writes first.
  The branch remains afterward, still queued. A conflict aborts the sync:
  cross-branch disagreement is consolidation work.
- `/discard` marks the session's worktree with an untracked `.discard`
  file; the mark is undoable until swept. Marked sessions are skipped by consolidation
  and deleted by clean-up.
- Clean-up (the last process of a pass, performed by the memory agent)
  reads the two markers; no timers. Neither `.active` nor `.discard`: the branch --
  confirmed merged into main -- and its worktree are removed, and a later
  resume starts fresh off current main. `.discard` alone: branch and
  worktree are removed by force, content and all. Both markers: left for
  a future pass. `.active` alone: content unified, branch and worktree
  stay. The `consolidate-<run>` branch is deleted once its merge lands.
  Beyond `.discard`, nothing is removed by force.
- When `MEMORY_CONSOLIDATING=1`, SessionStart performs no injection and no
  worktree creation, and `commit`, `session-end`, `index`, and
  `subagent-context` are no-ops: a
  consolidation process never sees compiled memory and never writes as a
  session.
