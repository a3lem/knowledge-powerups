New capability -- no reference spec exists yet. On completion this delta
becomes `docs/specs/consolidation.md`.

Archive note (2026-07-29): applied as `docs/specs/consolidation.md`, with
two corrections against the shipped code. Soul proposals were dropped from
the design, so the ratification bullet and the "pending soul proposal"
mining signal were not applied. "The agent sets `MEMORY_CONSOLIDATING=1`
for its whole run" was replaced by what actually happens: the SubagentStart
hook skips the memory agent, and only a scheduled headless run sets the
variable.

## ADD

# Consolidation

A single memory agent performs every memory operation beyond a session's
inline writes. It works on memory from outside: no compiled memory in its
context, conventions preloaded from the keeping-memories skill, all versions of
the store weighed as candidate texts against evidence.

- The agent sets `MEMORY_CONSOLIDATING=1` for its whole run.
- `/consolidate` runs four stages in order; an optional stage word
  (`mine`, `combine`, `refine`) limits the pass to that stage.
- Mine: for each queued session branch, distill the session transcript into
  commits on that branch, message-prefixed `distill session <id>` --
  provenance is commit structure, not citations in files. Mining skims by
  default and escalates only on signals (long transcript with few memory
  commits, user corrections, a pending soul proposal).
- Combine: session branches merge into a `consolidate-<run>` branch off
  main; differences between branches are resolved there, with transcripts
  as evidence.
- Refine: semantic reconciliation and defrag run on the combined tree.
  `memoryctl validate` passes before every commit.
- Merge: main receives exactly one merge per pass. Nothing else ever
  commits to main.
- Soul proposals are ratified only during consolidation and only on
  repeated testimony across sessions; a single-testimony proposal stays
  staged. Declining is allowed and recorded.
- Discarded sessions (see session-lifecycle) are skipped entirely: not
  mined, not combined.
- The janitor runs last; its deletion rules live in the session-lifecycle
  spec.
- A crashed pass leaves main untouched and a dangling `consolidate-<run>`
  branch; the next pass resumes or discards it.
- All commits are authored as the agent.
