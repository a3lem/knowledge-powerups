<!-- Rendered from .shablon/templates/README.md; edit that template, then run `shablon generate`. -->
# Agent Memory

Persistent, self-maintained memory for an agent: a git repository of
markdown the agent owns, compiled into its system prompt each session and
kept honest by an enforced contract. See [docs/](docs/) for the
architecture, specs, and glossary.

## Setup

By default, an agent's memory is stored at `{{ defaults.root }}/<agent-id>/`,
which holds exactly two directories: `main/`, the main branch's checkout, and
`worktrees/`, the per-session checkouts beside it.

- `MEMORY_AGENT_ID` sets `<agent-id>` (default `{{ defaults.agent_id }}`).
- `MEMORY_ROOT_DIR` moves the root (default `{{ defaults.root }}`).
- `MEMORY_ENABLED=0` is the kill switch: every hook becomes a silent no-op
  and the session leaves no memory trace.

No further setup: the first session scaffolds the store, and hooks handle
injection, validation, and end-of-turn commits from then on.

The index-md plugin is a companion: reference directories keep generated
`index.md` tables of contents. The hooks refresh them at SessionStart and
SessionEnd through the repo's shared `cli/generate_index.py`, and the
memory skills invoke the index-md skill for creation and manual
regeneration.

## Skills

To make the agent's own skills loadable, launch Claude Code with the store
on `--add-dir`:

    claude --add-dir {{ defaults.root }}/<agent-id>/main

`main/` carries a tracked `.claude/skills` symlink pointing the harness at
the `skills/` tier, so the agent's skills load like any others. Only `--add-dir` (or `/add-dir`) loads skills;
`permissions.additionalDirectories` in settings.json grants file access
without loading them.

A skill the agent writes during a session lives on that session's branch
and becomes loadable only once it reaches main: `/sync` now, or the next
consolidation. Session branches inherit the symlink too, so a branch can be
pointed at the same way for testing.

## Commands

- `/consolidate` -- full maintenance pass over the queued session branches
  (or one process: mine, unify, refine).
- `/sync` -- share this session's memory into main now, when it merges
  cleanly.
- `/discard` -- mark this session not worth remembering.
- `/calibrate` -- review memories with the human, grading both their truth
  and the agent's confidence in them.

## Generated surfaces

This README, the injected instructions, the keeping-memories skill, the
memory-store and validation specs, and the verify how-to are rendered
from `.shablon/templates/`. Facts like the size caps and store defaults
come from memoryctl.py through `.shablon/vars.py`, so the enforcing code
is their single source. Edit the template, never the rendered file, and
run `shablon generate`; the verify how-to's static checks catch a
mismatch.
