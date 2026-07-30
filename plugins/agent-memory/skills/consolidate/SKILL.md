---
name: consolidate
description: Load this skill when the user invokes /consolidate or asks to consolidate, unify, refine, or mine agent memory -- the memory agent's maintenance pass over the queued session branches. An optional process word (mine, unify, refine) limits the pass to that process; no word runs a full pass, which closes by accepting the result into main.
---

# Consolidate

Consolidation belongs to the memory agent, not this loop: only an agent with no
injected memory can weigh every branch even-handedly. This command spawns it.

Spawn the `memory` agent (Agent tool, subagent_type `memory`). Give it in the
prompt:

- The mode: the process word from the arguments -- `mine`, `unify`, or
  `refine` -- or, with no argument, `full` for a whole pass: unify the queued
  branches, refine the result, accept it into main, clean up, mining
  transcripts along the way where evidence is needed.
- The store root: `$MEMORY_ROOT_DIR/$MEMORY_AGENT_ID` (both are exported for
  shell commands).

Do not touch the store yourself. When the agent returns, relay its report:
what it unified, what it refined and forgot, what landed in main, and what
clean-up removed.
