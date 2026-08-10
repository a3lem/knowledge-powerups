# Status -- brevity for system-level memories

Implemented on top of the uncommitted letta-borrows changes; nothing was
reverted or committed.

## What changed, per file

- `scripts/memoryctl.py`
  - `render_metadata(mem, total)` gains the accounting line, between the
    memory HEAD line and the staged-history count:
    `injection: 6,120 / 24,000 chars, system/: 971`. The system/ figure is
    the rendered tier -- what actually enters the prompt.
  - `compile_memory` assembles through a local `assemble()` helper: one
    probe assembly carries the cap where the total goes (the same width as
    any total under it), and the reported size is that probe's length. The
    measured drift is 1 character on the fixture; exactness stays
    validate's job.
  - `SOUL_TEMPLATE` 461 -> 368 chars, `HUMAN_TEMPLATE` 453 -> 403 chars.
    Same content, notes register, frontmatter untouched; both still teach
    their rules (soul: assigned role recorded as given, chosen identity
    mine, no invented history; human: name only here, elsewhere the
    `[[system/human/human.md|human]]` link, preferences one per file).
  - New verb `system-delta` with helpers `head_blob`, `head_system_files`,
    `system_char_deltas`, and `cmd_system_delta`; docstring entry between
    `validate` and `commit`; `--stop-hook-active` flag on its subparser;
    `stop_hook_active` read from the hook JSON in `main()`.
- `hooks/hooks.json` -- Stop chain is now
  `validate && system-delta && commit`, same single stdin capture, same
  `python3 "${CLAUDE_PLUGIN_ROOT}/..."` shape.
- `.shablon/templates/prompts/injected-instructions.md` -- items 2 and 3,
  folded into the closing sentence of the maintenance paragraph: the
  terse rule, the metadata pointer, and demotion merged with the existing
  cap escape. Net +4 rendered lines, +246 chars.
- `.shablon/templates/skills/keeping-memories/SKILL.md` -- a "Write
  tersely" paragraph in Writing Memories (with the reason: system/ read
  every session, economy as the contract's spirit) and a demotion
  paragraph after the caps paragraph.
- `skills/refine/SKILL.md` (direct edit) -- the **Condense** operation
  after Split, and the standing no-net-growth goal for a pass beside the
  validate line.
- `.shablon/templates/docs/how-to-guides/verify-the-plugin.md` -- the
  accounting line added to the SessionStart expectations, the Stop chain
  snippet updated, and a new "The system/ growth check" section (block
  with numbers, `stop_hook_active` pass-through, the no-op cases).
- `docs/architecture.md` -- `system-delta` in the memoryctl verb list.
- Spec deltas applied exactly: `docs/specs/injection.md`,
  `docs/specs/session-lifecycle.md`, `docs/specs/consolidation.md`
  (direct), `.shablon/templates/docs/specs/memory-store.md` (templated).
- Rendered surfaces refreshed with `shablon generate`.

## system-delta semantics as built

- Trigger: positive total net character delta across `system/`, working
  tree against HEAD. A file HEAD lacks counts in full; a deleted file
  counts negative; net zero or negative is a silent exit 0, so moving
  content between `system/` files never blocks.
- Report to stderr, exit 2: per grown file the characters added and the
  new size against the 2,200 cap with a percentage, then the total added
  as a percentage of that per-file budget, then the question.
- Loop guard: `stop_hook_active: true` in the Stop hook JSON exits 0
  immediately.
- Gates first, all silent exit 0: `MEMORY_ENABLED=0`, `MEMORY_SESSION=`
  (empty), no session worktree, no resolvable HEAD.

## The `stop_hook_active` doc finding

Verified against the current hooks documentation
(https://code.claude.com/docs/en/hooks.md, fetched 2026-08-01): the field
exists and is spelled `stop_hook_active`. The docs state, for Stop:
"In addition to the common input fields, Stop hooks receive
`stop_hook_active`, `last_assistant_message`, `background_tasks`, and
`session_crons`. The `stop_hook_active` field is `true` when Claude Code
is already continuing as a result of a stop hook. Check this value or
process the transcript to avoid blocking on a condition that will never
resolve. Claude Code overrides the hook and ends the turn after 8
consecutive blocks." SubagentStop receives the same field. (A first pass
by a docs-lookup agent reported the field absent; the direct fetch and
grep of the page contradict that, so the plan's assumption holds.)

## Verification

Fixture store at a temp `MEMORY_ROOT_DIR`, hand-built hook JSON, the
Stop chain run in its exact shape.

1. Bootstrap: store scaffolds, worktree `session-t1` created.
2. Clean tree: chain exits 0.
3. Growth: new `system/core/deploys.md` (328 chars) plus 53 chars appended
   to `soul.md` -> exit 2, nothing committed. Numbers checked by hand
   against `wc -c` and `git show HEAD:system/soul.md` (368 -> 421):
   ```
   Memory check: this turn added characters to system/, which is read in full in every session.
   - system/core/deploys.md: +328 chars, now 328 / 2,200 (15% of the cap)
   - system/soul.md: +53 chars, now 421 / 2,200 (19% of the cap)
   Added in total: 381 chars -- 17% of one file's 2,200-char budget.
   Do the additions respect the injection's limited token budget? Trimming them and confirming they earn their place are both answers; either one ends the turn.
   ```
4. Same tree with `"stop_hook_active":true`: no report, exit 0, the
   auto-commit lands (`inline writes, session t1`), worktree clean.
5. Shrink a `system/` file: exit 0, commit lands.
6. No `system/` edits (a `reference/history/` file only): exit 0.
7. Net-zero move (55 chars out of `hotfixes.md` into `deploys.md`): exit
   0, commit lands. Net-negative (a `system/` file deleted, a smaller one
   added, net -19): exit 0.
8. Gates: `MEMORY_ENABLED=0` and `MEMORY_SESSION=` silent exit 0 with
   growth pending; unknown session id silent exit 0;
   `--stop-hook-active` exit 0. Growth still blocks on the next ungated
   run.
9. `compile` on the fixture: `injection: 6,120 / 24,000 chars,
   system/: 971` against an exact 6,119 -- 1 char of drift, stable across
   repeated runs. Sessionless compile and `subagent-context` both carry
   the line.
10. Regressions: an oversized `system/` file still fails validate with the
    cap message; validate exits 0 once removed.
11. `shablon generate` twice: second run reports every surface
    `unchanged`.
12. Em-dash sweep (em and en dash) over every touched file and the whole
    plugin: 0 hits.
13. Statics: the injected roster names exactly `/consolidate`, `/sync`,
    `/discard`, `/calibrate`; `hooks.json` invokes `python3` and never
    `uv run`.
14. `prompts/injected-instructions.md`: 3,917 -> 4,163 chars.
