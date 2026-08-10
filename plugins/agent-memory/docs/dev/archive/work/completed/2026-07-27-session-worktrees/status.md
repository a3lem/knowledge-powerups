# Status: Session Worktrees

Done -- implemented in memoryctl.py and hooks.json, verified against the
fixture store. Not yet archived (the .delta.md files still need merging into
docs/specs/ -- a separate step).

## What landed

- `memoryctl worktree` -- the one new verb. Reads session_id/transcript_path
  from hook JSON on stdin (`--session`/`--transcript` overrides). Scaffolds
  the store when absent (three tiers, template soul, git init -b main, first
  commit authored as the agent), then create-if-missing the worktree
  `worktrees/session-<id>` on branch `session-<id>` off main, reused if
  present. Rewrites the untracked `.session` transcript pointer every fire and
  prints the worktree path.
- `env` is session-aware: `export MEMORY_DIR=<worktree>` plus forwarded
  `MEMORY_ROOT_DIR` and `MEMORY_AGENT_ID` (never `MEMORY_CONSOLIDATING`).
- `validate` is session-aware: validates the session's worktree when its
  stdin carries a session id whose worktree exists, else the store root.
- `compile` binds to the worktree: `root` attribute and a new
  `MEMORY_DIR: <worktree>` line in `<memory-metadata>` both name it. Silent
  under `MEMORY_CONSOLIDATING=1`.
- Global gates in main(): `MEMORY_ENABLED=0` makes every subcommand a silent
  no-op with no side effects; `MEMORY_CONSOLIDATING=1` makes `worktree` a
  no-op and silences `compile` (env/validate unaffected).
- hooks.json: SessionStart is now a single command that captures stdin once
  and sequences worktree -> env -> compile, with the `CLAUDE_ENV_FILE` guard
  and `|| true` resilience; only compile writes to the hook's stdout. Stop
  pipes its stdin through to `validate` unchanged.
- `worktrees/` and `.session` are kept out of git status via
  `.git/info/exclude` (local-only), not a tracked `.gitignore` that would
  ride onto every branch.

## Verification

Six scripted checks against the fixture store, all green: two concurrent
sessions diverge with main untouched; resume reuses the worktree and
deleted-worktree resume branches fresh off main; store-missing bootstrap;
both env-var gates; session-scoped validate (exit 2, store root untouched);
compile shows the MEMORY_DIR binding. A `session-demo-a` worktree with one
agent-authored commit is left in the fixture as evidence.
