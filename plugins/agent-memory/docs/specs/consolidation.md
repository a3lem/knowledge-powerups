---
title: Consolidation
description: The memory agent's maintenance pass over the queued session branches -- unify, refine, accept, with transcript mining on demand
---

# Consolidation

A single memory agent performs every memory operation beyond a session's
inline writes. It works on memory from outside: no compiled memory in its
context, conventions preloaded from the keeping-memories skill, all versions
of the store weighed as candidate texts against the evidence (transcripts,
dates, git history).

- The agent never sees compiled memory: the SubagentStart hook skips it
  (agent_type `memory`, plugin-scoped included), and a scheduled headless
  run sets `MEMORY_CONSOLIDATING=1` so SessionStart injects nothing and
  creates no worktree.
- Consolidation is distinct processes, not a fixed pipeline: unify, refine,
  and mine interleave freely, and the one ordering constraint is that
  accepting requires a unified tree. `/consolidate` runs a full pass; an
  optional process word (`mine`, `unify`, `refine`) limits it to that
  process.
- Each process's procedure lives in its skill (`mine-history`, `unify`,
  `refine`); the memory agent preloads all three, and the human may hand
  the same skills to a different runner.
- Unify: every queued session branch that is not discarded -- branches of
  still-active sessions included -- merges into a `consolidate-<run>`
  branch off main, checked out in the `main/` checkout, where a bare
  `memoryctl validate` binds to the unified tree. Each merge commit's
  message records the session id and its transcript path, so the
  transcript stays minable after the branch and worktree are gone.
  Differences between branches are resolved there, with transcripts as
  evidence.
- Refine: semantic care of the tree -- contradictory facts reconciled,
  duplicates collapsed, misfiled content re-homed, episodic detail
  distilled to what generalizes, the irrelevant forgotten. The test for
  structure is one question, one home. `memoryctl validate` passes before
  every commit. Refinement is not confined to the pass: light forms run
  inline in sessions, and the agent may refine main directly between
  passes.
- Forgetting is a first-class operation: a deliberate deletion states its
  reason in the deleting commit's message, and nothing deliberately
  forgotten is re-added from a transcript unless evidence postdating the
  forget overturns it.
- Mine: on-demand evidence retrieval from a session's transcript --
  settling a contradiction, fleshing out an underdefined memory,
  distilling patterns the inline writes missed. Not a mandatory stage;
  skim signals decide depth: a long transcript with few memory commits, or
  user corrections mid-session. Findings become commits message-prefixed
  `distill session <id>`, on the session's branch while it exists and on
  the unified tree after. Transcripts expire with the harness's retention
  period (30 days by default); a session worth close mining gets it while
  its log exists.
- Accept: the `main/` checkout switches back to main and merges
  `consolidate-<run>`, which is then deleted; main receives exactly one
  merge per pass. Sessions never commit to main; only the memory agent
  does.
- Discarded sessions (see the session-lifecycle spec) are skipped: not
  unified, not mined.
- Clean-up runs last; its marker-driven rules live in the
  session-lifecycle spec.
- A merge conflict is resolved with judgment and evidence, never blind; an
  unresolvable one aborts the merge and stops with an explanation.
- A crashed pass leaves main untouched and a dangling `consolidate-<run>`
  branch; the next pass resumes or discards it.
- All commits are authored as the agent.
