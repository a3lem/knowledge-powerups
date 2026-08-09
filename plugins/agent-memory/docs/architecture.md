---
title: Architecture
description: what the plugin consists of and how the pieces connect
---

# Architecture

Persistent, self-maintained memory for an agent: a git repository of
markdown the agent owns, compiled into its system prompt each session and
kept honest by an enforced contract.

Three layers, three kinds of authority:

- **memoryctl** (`scripts/memoryctl.py`) -- the deterministic verbs:
  `worktree` (create-if-missing session worktree, scaffolding the store
  itself on first use and ensuring the `.claude/skills` discovery
  symlink), `env` (print the `MEMORY_DIR` and `MEMORY_*`
  export lines), `compile` (print the injection), `validate` (check the
  contract, exit 2 on violations), `system-delta` (report the turn's net
  growth in `system/` past a floor, blocking once as Stop-hook JSON),
  `commit` (commit the session worktree's writes, authored as the agent),
  `session-end` (drop the
  worktree's `.active` liveness lock), `index` (refresh the generated index.md
  bodies in the worktree's `reference/`, via the repo's shared
  `cli/generate_index.py`), `subagent-context` (print the
  SubagentStart JSON that carries the injection to subagents). Stdlib-only,
  run with plain `python3`, silent no-op when memory is disabled or no
  store exists. The surface stays deliberately small: a new verb only when
  hooks need deterministic stdin plumbing; the memory agent's operations
  are plain git, prescribed by skills.
- **hooks** (`hooks/hooks.json`) -- the compulsion: SessionStart runs
  worktree → index → env → compile as one command (stdin captured once),
  so by default every session gets its own branch, fresh index bodies,
  its env exports, and its injection; SubagentStart injects the same block into
  subagents (read-only preamble, memory agent skipped); SessionEnd
  refreshes the index bodies again and drops the session's `.active`
  liveness lock; Stop validates the session's worktree -- exit 2 blocks
  the turn -- and, when clean, commits the session's writes. The model
  isn't trusted to respect its own limits; the harness compels them.
- **skills and the agent** -- the judgment: `keeping-memories` carries the
  save-side conventions (writing rules, links, tiers, the persona);
  `mine-history`, `unify`, and `refine` carry each consolidation
  process's procedure,
  preloaded by the `memory` agent (`agents/memory.md`) and loadable by
  any runner the human prefers; `calibrate` runs the interactive audit
  with the human; `consolidate`, `sync`, and `discard` are the thin
  command surface, the first two dispatching to the memory agent, which
  performs every operation beyond a session's inline writes from the
  outside view.
  The always-injected instructions are not a skill: they live as bare
  prose in `prompts/`, and compile wraps them in their tag at render time.

Behavior per capability is specified in [specs/](specs/).
