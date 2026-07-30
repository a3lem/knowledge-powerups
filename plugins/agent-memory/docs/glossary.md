---
title: Glossary
description: memory-system jargon, defined in one place
---

# Glossary

- **memory store** -- an agent's memory at `$MEMORY_ROOT_DIR/<agent-id>/`:
  a git repository of markdown files, maintained by the agent itself. The
  store holds exactly `main/` (the main checkout, git dir inside) and
  `worktrees/` (the session checkouts beside it).
- **memory tier** -- one of the store's three top-level directories, split
  by what enters the prompt: `system/` (injected in full), `reference/`
  (index only), `skills/` (procedural).
- **memory injection** -- the compiled `<agent-memory>` block a SessionStart
  hook puts in the system prompt (and a SubagentStart hook hands to
  subagents, read-only).
- **validation contract** -- the rules a Stop hook enforces at the end of
  every turn (size caps, descriptions, link form, skill frontmatter); exit
  2 blocks the turn. "The contract" in these docs means this.
- **auto-commit** -- the Stop hook's second step: once validation passes,
  the session's writes are committed to its branch, authored as the agent.
- **inline habits** -- memory maintenance the session does itself, without
  ceremony: file a fact, fix a stale memory, leave a forward pointer.
- **forward pointer** -- a wikilink to a file not yet written; legal, and a
  marker for consolidation to write the file or drop the link.
- **memory agent** -- the one subagent performing every memory operation
  beyond inline habits. Runs without memory injection, so no version of the
  store is privileged.
- **consolidation** -- the memory agent's maintenance pass (command
  `/consolidate`): unify the queued session branches, refine the tree,
  accept the result into main, mining transcripts on demand along the
  way. Colloquially: sleep.
- **unifying** -- merging the queued session branches into
  `consolidate-<run>`, differences resolved with transcripts as evidence;
  each merge commit records the session id and transcript path.
- **refining** -- semantic care of the tree: reconcile, deduplicate,
  re-home, distill, forget. Light forms run inline in sessions; the agent
  may also refine main between passes.
- **mining** -- reading a session transcript for evidence; on demand, not
  a stage. Possible as long as the transcript exists, even after the
  branch is gone.
- **accepting** -- the pass's closing merge of `consolidate-<run>` into
  main; the only merge main receives per pass.
- **consolidation queue** -- the list of `session-*` branches; a branch
  exists exactly as long as its session is unprocessed. Its depth is shown
  in `<memory-metadata>`.
- **consolidate-<run>** -- the staging branch where a pass assembles
  everything before main receives its single merge; deleted once that
  merge lands.
- **janitor** -- the memory agent's final duty in a pass (not a separate
  agent), driven by the `.active` and `.discard` markers: an ended,
  unified session's branch and worktree go; a discarded ended session
  goes by force; anything still active stays.
- **skill discovery** -- the harness loads agent skills from
  `.claude/skills/` of every `--add-dir` directory; the store tracks that
  path as a symlink to `skills/`. Since `--add-dir` points at the store's
  `main/` checkout, a skill becomes loadable when it lands in main.
- **session liveness** -- whether a session might still write: the
  worktree's untracked `.active` file, written at SessionStart and removed
  at SessionEnd.
- **persona** -- `system/persona.md`: who the agent is told to be -- name,
  backstory, character, recorded by the agent as the human assigns it in
  conversation. The pen is the agent's, the words are the human's; the
  agent's own reading of the role lives in the soul.
- **soul** -- `system/soul.md`: how the agent sees itself -- positions,
  taste, self-conception, its reading of any assigned persona. Answers to
  the agent alone; chosen identity belongs there, invented events do not.
  Kept stable by judgment, not machinery.
- **/sync (command)** -- lands the session's branch in main now, when it
  merges cleanly; a conflict aborts and waits for consolidation. The
  branch stays queued.
- **/discard (command)** -- marks a session as not worth remembering:
  skipped by consolidation, deleted by the janitor, undoable until swept.
- **calibration** -- the interactive audit (command `/calibrate`) where the
  human grades memories (true-false) and the agent's stated confidence in
  them.
