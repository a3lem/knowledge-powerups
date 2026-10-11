# Borrow letta-code prompt practices

Ticket: akps-97b1. Source: the letta-code system prompt
(letta-ai/letta-code@1315d7d, `src/agent/prompts/letta.md`), reviewed
2026-08-01. Seven prompt-level borrows plus one README addition. Two
larger ideas are split off as decision tickets and are NOT part of this
work item: a machine check for secret shapes in validate (akps-cb20) and
recall as a session capability (akps-36b2).

## The borrows

1. **Secrets rule.** Memory never stores credentials, API keys, or
   tokens: the store is a git repository that may leave the machine.
   Convention only for now -- no validate check (akps-cb20 decides that).
   Lands in the injected instructions, keeping-memories (Writing
   Memories), and the memory-store spec (see `specs/memory-store.delta.md`).

2. **Active recall directive.** The injection's recall guidance is
   passive ("read a file when its description is relevant"). Add the
   active rule: an unfamiliar name, project, or concept is a cue to
   search memory (grep the store, walk the index) before concluding you
   don't know it. Lands in the injected instructions, first paragraph.

3. **Compile-time semantics.** State that the injection is compiled at
   session start: a memory edit binds future sessions, not the current
   prompt -- write for your future self, and keep acting on the decision
   now. The skill-version subtlety is already covered; this generalizes
   it. Lands in the injected instructions.

4. **Soul adherence and change-ordering.** Act from the soul; where it
   conflicts with the model's defaults, the soul wins. A deliberate
   deviation is a revision: record it in soul.md first, then act.
   Carve-out: honoring an explicit request about tone, format, or detail
   is not an identity deviation and needs no memory write. Lands in the
   injected instructions (soul paragraph) and keeping-memories (The
   Soul). Restrained wording -- adherence, not letta's MUST/NEVER tone.

5. **Actionable metadata.** `<memory-metadata>` shows the consolidation
   queue depth and staged-history count, but nothing consumes them. Add
   one line to the injected instructions: when the queue or staging runs
   deep, suggest /consolidate to the human.

6. **Memory / skill / harness-config triage.** A lesson that must hold
   deterministically (a check to run every time, a permission, a
   safety rule) belongs in harness configuration -- hooks, permissions --
   not in memory; a reusable procedure is a skill; knowledge that shapes
   judgment is a memory. This hands the plugin's own thesis ("the
   harness compels, the model judges") to the agent as guidance for its
   own lessons. Lands in keeping-memories (Writing Memories).

7. **Transcript provenance.** In mine-history's skim guidance, note the
   complement of "the user's turns are the highest-signal lines": the
   agent's own turns are claims it made, not ground truth, and carry no
   more authority than the memory they produced.

Plus: **README, scheduled consolidation.** Document the sleep-schedule
pattern: consolidation can run on a cron/routine via headless
`claude -p /consolidate`; the queue depth in the metadata is the signal
for an on-demand pass. Short paragraph near the Commands section.

## Files

Rendered surfaces are edited via their templates, then `shablon generate`
at the plugin root (see the use-shablon skill if needed):

- `.shablon/templates/prompts/injected-instructions.md` -- items 1-5.
- `.shablon/templates/skills/keeping-memories/SKILL.md` -- items 1, 4, 6.
- `.shablon/templates/docs/specs/memory-store.md` -- item 1, per the delta.
- `.shablon/templates/README.md` -- scheduled consolidation.
- `skills/mine-history/SKILL.md` -- item 7, direct edit (not templated).

## Spec assessment

- `memory-store.md`: ADD one convention bullet (secrets). Delta in
  `specs/memory-store.delta.md`.
- `validation.md`: unchanged -- no machine check added.
- `injection.md`: unchanged -- it specifies the block structure, not the
  instruction prose.
- `consolidation.md`, `session-lifecycle.md`, `calibration.md`: unchanged.
- Soul adherence stays out of the memory-store spec: the spec describes
  the soul's content and authority; adherence is behavioral guidance and
  lives in prompts and the skill.

## Constraints

- The injected instructions count against the 24,000-char injection cap
  in every session. Keep the additions tight: aim for at most ~10 lines
  across items 1-5, folded into existing paragraphs where they fit.
- Prose style: spaced double hyphen ` -- `, never an em-dash; match the
  existing second-person voice of the instructions and the existing
  register of each file. No letta phrasing imported verbatim where it
  reads as sloganeering ("you are the tokens").
- After rendering: `shablon generate` run again reports every surface
  unchanged; `git status` shows template and rendered file moving in
  pairs; the static checks in
  `docs/how-to-guides/verify-the-plugin.md` pass (no spaced em-dashes,
  roster names exactly the four commands).
