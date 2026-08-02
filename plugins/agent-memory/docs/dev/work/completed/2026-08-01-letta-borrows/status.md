# Status: Borrow letta-code prompt practices

Done -- all seven borrows plus the README addition landed, rendered surfaces
regenerated from their templates. Not archived (the memory-store delta still
needs merging into docs/specs/ -- a separate step). Nothing committed.

## What changed

- `.shablon/templates/prompts/injected-instructions.md` -- items 1-5, folded
  into existing paragraphs, no new headers:
  - first paragraph gains the active-recall rule (an unfamiliar name,
    project, or concept is a cue to search memory before concluding you
    don't know it);
  - the maintenance paragraph gains the secrets rule, placed after the
    human-name rule it resembles;
  - the skills paragraph opens with compile-time semantics (this block was
    compiled at session start, so a memory written now binds future
    sessions), which generalizes the skill-version subtlety that follows;
  - the soul paragraph gains adherence and change-ordering (the soul is the
    more specific instruction; a deliberate departure is recorded in
    soul.md before it is acted on);
  - the command paragraph gains the metadata-driven suggestion (a deep
    consolidation queue or staged history is a cue to suggest /consolidate).
- `.shablon/templates/skills/keeping-memories/SKILL.md` -- items 1, 4, 6.
  Writing Memories gains two paragraphs: never store a secret (with what
  memory may hold instead: where the secret lives, named not quoted), and
  the memory/skill/harness-config triage -- a lesson that has to hold every
  time belongs in hooks and permissions, a repeated procedure is a skill,
  knowledge that shapes judgment is a memory. The Soul gains one paragraph
  after the positions paragraph: adherence, revision-before-behavior, and
  the carve-out for an explicit request about tone, format, or detail.
- `.shablon/templates/docs/specs/memory-store.md` -- the ADD bullet from
  `specs/memory-store.delta.md`, verbatim, beside the other "Convention,
  not validated" bullets (first person, atomic files).
- `.shablon/templates/README.md` -- a paragraph after the Commands list on
  scheduled consolidation: headless `claude -p /consolidate` on a cron job
  or routine as the agent's sleep cycle, with the metadata counts as the
  signal for a pass between scheduled runs.
- `skills/mine-history/SKILL.md` -- direct edit (not templated). The skim
  guidance now carries the complement of "the user's turns are the
  highest-signal lines": the agent's own turns are claims it made at the
  time, no more authoritative than the memories they produced.

Rendered pairs regenerated with `shablon generate` at the plugin root:
README.md, docs/specs/memory-store.md, prompts/injected-instructions.md,
skills/keeping-memories/SKILL.md.

## Verification

- Injected instructions: 3,107 -> 3,917 characters (+810), 49 -> 59 lines
  (+10) -- within the ~10-line, ~900-character budget for items 1-5. The
  compiled injection cap (24,000) has ample headroom.
- `shablon generate` run a second time reports every surface `unchanged`.
- `git status --porcelain`: four templates paired with their four rendered
  files, plus `skills/mine-history/SKILL.md` and this work item directory.
  Nothing else.
- Em-dash sweep over all changed files: zero hits, spaced or not; every new
  dash is the spaced double hyphen.
- Injected roster still names exactly `/consolidate`, `/sync`, `/discard`,
  `/calibrate` -- no new command names introduced.

## Out of scope, as planned

No validate check for secret shapes (akps-cb20 decides that) and no recall
capability (akps-36b2). `validation.md`, `injection.md`, `consolidation.md`,
`session-lifecycle.md`, and `calibration.md` are unchanged.
