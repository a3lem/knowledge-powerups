---
title: Claude Code harness facts
description: Verified behaviors of the Claude Code harness that plugins in this repo depend on
---

# Claude Code Harness Facts

Facts verified 2026-07-27 against current docs and issue tracker, during the
agent-memory build. Each was checked because guessing about the harness has
burned us before. Re-verify against current docs when a fact is load-bearing
for new work; note the date when you add one.

## Hook input

- Every hook event receives JSON on stdin with common fields: `session_id`,
  `prompt_id`, `transcript_path`, `cwd`, `permission_mode`,
  `hook_event_name`. No environment variable carries the session id; stdin
  is the only delivery path.
- SessionStart adds `source` (`startup` | `resume` | `clear` | `compact` |
  `fork`), `model`, `agent_type`, `session_title`. It fires on resume and
  after compaction, and also in headless `-p` mode.
- Stop adds `stop_hook_active`, `last_assistant_message`,
  `background_tasks`, `session_crons`.
- Multiple hook commands on one event share one stdin -- a command chain
  must capture it once (`json=$(cat)`) and re-feed each step.

## CLAUDE_ENV_FILE

- Writable from SessionStart, Setup, CwdChanged, and FileChanged hooks
  only.
- Persisted variables reach Bash tool commands only ("sourced before each
  Bash command"); hook commands are covered by neither doc passage.
  Clarification was requested and closed unresolved
  ([#19357](https://github.com/anthropics/claude-code/issues/19357)).
- It has arrived empty in the field: for plugin-installed hooks
  ([#11649](https://github.com/anthropics/claude-code/issues/11649),
  v2.0.36, closed without a stated fix version) and generally
  ([#15840](https://github.com/anthropics/claude-code/issues/15840)).
  Guard with `[ -n "${CLAUDE_ENV_FILE}" ]` and never make a hook's
  correctness depend on it.

## SubagentStart

Verified 2026-07-28 against the hooks doc, for subagent memory injection.

- Receives the common fields plus `agent_id` and `agent_type`
  (plugin-scoped agents appear as `plugin:agent`).
- Stdout is NOT added to the subagent's context -- SessionStart is the
  exception there, not the rule. Context injection works only via JSON
  `hookSpecificOutput.additionalContext`.
- Cannot block or modify the subagent: exit 2 shows stderr only (rendered
  in the subagent's own transcript from v2.1.199).

## Skills from --add-dir

Verified 2026-07-29 (skills doc + live headless probe), for memory skill
discovery.

- `--add-dir` and `/add-dir` load `.claude/skills/` from each added
  directory -- an explicit exception to the "access, not configuration"
  rule. `permissions.additionalDirectories` in settings.json grants file
  access only and loads no skills.
- `.claude/skills` may itself be a directory-level symlink: probed live
  with a symlinked tier behind `--add-dir`; the skill was discovered. (The
  docs only bless per-skill-entry symlinks explicitly.)
- Edits under a watched `.claude/skills/` (added dirs included) take
  effect within the session; a top-level skills directory created after
  launch needs a restart to be watched.
- Other configuration (commands, output styles, CLAUDE.md by default) is
  NOT loaded from added directories.
- `--add-dir` takes multiple values: a trailing positional prompt after it
  is swallowed. In `-p` mode, pipe the prompt on stdin instead.

## Transcripts

- Stored at `~/.claude/projects/<project-slug>/<session-id>.jsonl`, where
  the slug is the working directory path with non-alphanumerics replaced
  by `-`. The filename equals the session id. The path is stable across
  resumes.

## Subagents

- Custom agents spawned via the Agent tool start fresh and receive:
  CLAUDE.md (every level), a git status snapshot, skills preloaded via
  `skills:` frontmatter, and a sibling roster. They do NOT receive
  SessionStart hook output, conversation history, or output styles.
  (Built-in Explore and Plan agents omit CLAUDE.md and git status too.)
  Consequence: context injected by SessionStart hooks is invisible to
  subagents -- isolation is the default.
- Plugin agent frontmatter supports `name`, `description`, `model`,
  `effort`, `maxTurns`, `tools`, `disallowedTools`, `skills`, `memory`,
  `background`, `isolation`. Plugin-shipped agents cannot declare `hooks`
  (security restriction).
- `SubagentStart`/`SubagentStop` fire at the parent level;
  `PreToolUse`/`PostToolUse` fire inside a subagent's own loop. `Stop` in
  a CLI-defined agent's frontmatter converts to `SubagentStop`.

Sources: [hooks](https://code.claude.com/docs/en/hooks),
[subagents](https://code.claude.com/docs/en/subagents),
[sessions](https://code.claude.com/docs/en/sessions),
[plugins reference](https://code.claude.com/docs/en/plugins-reference).
