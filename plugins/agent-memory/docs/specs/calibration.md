---
title: Calibration
description: Reviewing memories with the human -- grading both their truth and the agent's stated confidence
---

# Calibration

`/calibrate` reviews memories with the human: the agent presents what it
believes, states how certain it is, and the human grades it. Sampling, not
an audit. The pass runs in the main session, not the memory agent: only
the main loop converses with the human.

- The agent selects memories by consequence and age; `system/` outranks
  `reference/`.
- Memories are presented in small batches as plain conversation, each with
  its source: which file, and which session or commit wrote it when git
  history says so cheaply.
- Before each verdict the agent states its own confidence.
- Each verdict is acted on in the same turn: false memories are fixed or
  deleted, with inbound links rewritten on a deletion; confirmed ones
  stand; unresolved ones are marked as disputed where they live.
- Confident-and-wrong outcomes are recorded (a self-correction under
  `system/core/` or a dated `reference/history/` note), not just
  corrected.
- Scope: the human is the authority on facts about themselves, about the
  world, and over the whole persona -- told or agent-added, a verdict on
  a persona line is applied as given. The persona exists to serve the
  cooperation, so the human's needs decide it.
- The pass ends with counts: confirmed, corrected, deleted, disputed.
