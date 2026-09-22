## REPLACE

### OLD

- `<memory-metadata>` closes the block: agent id, a `MEMORY_DIR: <worktree
  path>` line stating the binding explicitly, compile time (UTC), memory
  HEAD (short), count of entries staged in `reference/history/`, and the
  consolidation queue depth (count of `session-*` branches).

### NEW

- `<memory-metadata>` closes the block: agent id, a `MEMORY_DIR: <worktree
  path>` line stating the binding explicitly, compile time (UTC), memory
  HEAD (short), an injection accounting line (system/ tier characters and
  total compiled characters against the 24,000 cap; the total may drift a
  few characters from validate's exact measure), count of entries staged
  in `reference/history/`, and the consolidation queue depth (count of
  `session-*` branches).

Reason: the injection's cost was invisible to the agent -- the caps bind
only when crossed, and nothing below them shows the spend. The accounting
line is the number the brevity conventions refer to.
