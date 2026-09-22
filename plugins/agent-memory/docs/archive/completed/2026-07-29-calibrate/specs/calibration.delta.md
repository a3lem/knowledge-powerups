New capability -- no reference spec exists yet. On completion this delta
becomes `docs/specs/calibration.md`. Replaces the unspecced fact-check
skill.

Archive note (2026-07-29): applied as `docs/specs/calibration.md`, with one
correction: soul proposals were dropped from the design, so "staged as a
proposal, not applied as a verdict" became what the shipped skill says --
feedback on the soul is input the agent weighs and folds in itself.

## ADD

# Calibration

`/calibrate` reviews memories with the human: the agent presents what it
believes, states how certain it is, and the human grades it. Sampling, not
an audit.

- The agent selects memories by consequence and age; `system/` outranks
  `reference/`.
- Memories are presented in small batches as plain conversation, each with
  its source (which file, and where it came from when git history says).
- Before each verdict the agent states its own confidence.
- Each verdict is acted on in the same turn: false memories are fixed or
  deleted; confirmed ones stand; unresolved ones are marked as disputed
  where they live.
- Confident-and-wrong outcomes are recorded (self-corrections or a dated
  history note), not just corrected.
- Scope: the human is the authority on facts about themselves and about
  the world. The soul is the agent's own to revise; feedback on it is
  treated as input -- staged as a proposal, not applied as a verdict.
- The pass ends with counts: confirmed, corrected, deleted, disputed.
