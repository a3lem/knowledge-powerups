---
title: Status
description: Where the migration design stands
---

# Status

Drafting. Nothing implemented; no files outside this work item have changed.

The shape is agreed: a version marker in the adopting repo, a version stated
in the skill body, and a newest-first log of executable migration steps in a
reference file under `using-docs/`. No new skill, and `adopt-conventions`
keeps its onboarding-only scope apart from one new step (write the marker).

Six questions are open, listed in [approach.md](approach.md). The first one
is the one that matters: nothing triggers the version check. The rest of the
design works only if an agent thinks to compare the repo's marker against
the skill's version, and no mechanism makes it do that. An always-on
instruction in `using-docs` would fire in every repo every session, almost
always to confirm nothing is wrong. Settle that before building anything
else -- if it has no acceptable answer, the log is written for a reader who
never arrives.

Tracked as akps-c281.

Once the design settles, the first log entry is already known: the
2026-09-15 change recorded in
[decisions/0001-flat-docs-layout.md](../../decisions/0001-flat-docs-layout.md),
plus the `adrs/` -> `decisions/` and `how-to-guides/` -> `how-tos/` renames.
