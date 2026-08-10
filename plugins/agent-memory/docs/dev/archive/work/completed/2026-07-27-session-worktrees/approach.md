# Approach: Session Worktrees

## Decisions already settled (design discussion 2026-07-26/27)

- Branch-per-session; main is merge-only for everyone.
- Branch list is the consolidation queue; no sessions.tsv -- an append-only
  shared file is the one guaranteed merge conflict in the system.
- Session liveness is transcript mtime (`~/.claude/projects/*/<id>.jsonl`),
  maintained by the harness every turn; no lock files or heartbeats of our
  own.
- Deleting a merged, clean worktree is safe at any moment because resume
  recreates it from current main (SessionStart fires on resume and after
  compaction).
- The kill switch is one check in memoryctl's main, gating every subcommand.

## Build steps

1. `memoryctl worktree` -- the one new CLI verb; hooks need deterministic
   stdin-JSON plumbing, and everything agent-facing stays plain git in
   skills. Reads `session_id` and `transcript_path` from the hook JSON on
   stdin (`--session <id>` override for manual runs). When the store
   itself is missing, scaffolds it first (three tiers, a minimal template
   soul -- "newly initialized; positions not yet learned" -- git init,
   first commit authored as the agent; no content invention, content
   grows from lived sessions); there is no separate init command. Then
   create-if-missing `worktrees/session-<id>` on branch `session-<id>`
   off main; records the transcript path in the worktree as an untracked
   `.session` file, refreshed on every fire. Prints the worktree path.
   Recording the path also decouples the janitor from any one harness's
   transcript layout: different harnesses (Claude Code, pi) store
   transcripts in different places, and the memory store should outlive
   all of them.
2. `memoryctl env` becomes session-aware: it emits
   `export MEMORY_DIR=<worktree path>` derived from the stdin
   `session_id`, and forwards the `MEMORY_*` configuration the hook
   resolved (`MEMORY_ROOT_DIR`, `MEMORY_AGENT_ID`) as further export
   lines -- Bash tool commands then run with exactly the configuration
   the hook saw.
3. Hook chain (SessionStart): worktree → env → compile, in that order; all
   skipped when `MEMORY_ENABLED=0` or `MEMORY_CONSOLIDATING=1`. Idempotent
   across every `source` that fires it: startup, resume, clear, compact,
   fork.
4. `compile` renders `<path>` elements against `$MEMORY_DIR` as today; the
   `root` attribute carries the worktree path.
5. Stop-hook `validate` finds the worktree from the `session_id` in its own
   stdin, never from `$MEMORY_DIR` -- so each concurrent session validates
   exactly its own worktree.

## Verified harness facts (2026-07-27, hooks + sessions docs)

- Every hook event receives `session_id`, `transcript_path`, and `cwd` as
  JSON on stdin -- Stop included. No environment variable carries the
  session id; stdin is the only delivery path.
- `CLAUDE_ENV_FILE` is writable from SessionStart (and Setup, CwdChanged,
  FileChanged) hooks only, and both doc passages scope the persisted
  variables to Bash tool commands ("sourced before each Bash command";
  "for subsequent bash commands"). Hook commands are covered by neither --
  hence step 5. Clarification was requested and closed unresolved
  (anthropics/claude-code#19357).
- Responsibility split: the SessionStart hook sets up everything while all
  inputs are known -- worktree, `.session`, env exports -- from stdin
  (`session_id`, `transcript_path`) plus `MEMORY_ROOT_DIR` and
  `MEMORY_AGENT_ID`. After that, each consumer uses its own channel: the
  agent builds Bash calls to memoryctl from the exported `$MEMORY_DIR`;
  hook commands read their own stdin; the janitor reads `.session` files.
  The injection's `root` attribute is the fallback when an env export
  failed, not a co-equal path source.
- Risk, sized accordingly: `CLAUDE_ENV_FILE` has arrived empty in the
  field -- for plugin hooks specifically (#11649, v2.0.36, closed without
  a stated fix version) and generally (#15840). One preflight check on
  the installed version; not an architectural hedge.
- `transcript_path` is `~/.claude/projects/<project-slug>/<session-id>.jsonl`:
  the filename equals the session id and the path is stable across resumes.
  The janitor reads the worktree's recorded `.session` path, with a
  filename glob as fallback -- sound because of the naming guarantee.
- SessionStart `source` values: `startup`, `resume`, `clear`, `compact`,
  `fork`. `/clear` starts a new session id, so it opens a new branch and
  the old one simply stays queued.

## Verification

Fixture-based, scripted: fake two session ids, run the hook chain for each,
commit in both worktrees, assert branches diverge and main is untouched.
Then the resume cases and both env-var gates from goal.md.

Plus one live check on the installed Claude Code version: confirm this
plugin's SessionStart hook actually receives a non-empty
`CLAUDE_ENV_FILE` (see the risk above), and that a session still
functions when it doesn't -- no `$MEMORY_DIR`, paths built from the
`root` attribute alone.
