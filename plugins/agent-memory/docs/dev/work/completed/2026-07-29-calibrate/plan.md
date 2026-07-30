# Rename fact-check To /calibrate, Add Confidence Grading

Ticket: akps-40f2.

## Goal

The interactive audit stays in the main loop (only the main agent can
converse with the human), but "fact-check" undersells it: the human grades
true-false *and* the agent's stated certainty, which is calibration in the
forecasting sense. Approved 2026-07-27.

## Approach

- `git mv skills/fact-check skills/calibrate`; frontmatter name and
  description updated.
- Add the confidence step to the skill: before each verdict the agent
  states how certain it is; verdict plus prior confidence are recorded, so
  miscalibration (confident and wrong) is visible, not just wrongness.
- Miscalibration worth remembering feeds a self-correction file under
  `system/core/` or a dated `reference/history/` note -- existing
  conventions, no new machinery.
- Update the roster line in
  `prompts/injected-instructions.md`.
- Scope rule is unchanged and restated in the skill: the human is the
  authority on facts about themselves and the world; feedback on the soul
  is input, not verdict.

## Verification

Dry run against the fixture: one deliberately false memory planted; the
session surfaces it with a stated confidence, records the verdict, fixes
the memory in the same turn.

## Specs

- [specs/calibration.delta.md](specs/calibration.delta.md)
