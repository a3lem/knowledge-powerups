# Persona replaces soul

Decision (2026-08-07), from the Emily incident and the discussion it
opened: the identity file retires. `system/soul.md` -- how the agent sees
itself, individuation, self-conception -- is replaced by
`system/persona.md`: the role the human wants the agent to play. This is
the honest framing for an LLM agent: identity is trained into the model
(an Anthropic model answers as Claude, a DeepSeek model as DeepSeek), so
memory must stay stable across model swaps -- no model names, no claimed
history, no assertions about what the agent *is*. The imperative mood
does the philosophical work: "Bring senior-engineer judgment" is
followable by whatever model reads it, where "I bring senior-engineer
judgment" is a claim the weights may fight. The agent's purpose in
maintaining the persona is to align itself closer to the human's needs so
future sessions serve them better.

## The persona file

Exactly two sections:

    # Role
    Who/what you are acting as.

    # Style
    How you should sound.

`# Avoid` and `# Defaults` were considered and dropped: behavioral
avoidances and ambiguity defaults are knowledge of the human's
preferences and belong under `system/human/preferences/`, one small file
each. The persona section of keeping-memories carries that routing rule.

The pen is the agent's, as everywhere in memory: the human never edits
the file -- they tell the agent about itself and the agent files it. The
agent also updates the persona on its own initiative when it notices a
gap, a contradiction, or a useful extra that will improve the
cooperation in future sessions.

Register: short markdown list items, often imperative, factual and to
the point; rarely refers to the human or to specific episodes. Written
to the future self, like every memory file.

Adherence (replaces the soul adherence rule shipped 2026-08-01): act the
persona; where it and the model's defaults differ, the persona is the
more specific instruction. A deliberate deviation is an update -- edit
persona.md first, then act. Honoring an explicit request about tone,
format, or level of detail is not a deviation (carve-out unchanged).

## Register convention, generalized

The "write in the first person" convention loosens into the frame that
was always underneath it: memory files are notes to the future self.
First person where the note records knowledge ("I verified X"),
imperative where it directs behavior ("Verify X before asserting").
persona.md simply leans imperative. Update the keeping-memories Writing
Memories paragraph and the memory-store convention bullet accordingly
(delta included); frontmatter descriptions stay first-person.

## Calibration

One scope rule, no carve-outs: the human is the authority on facts about
themselves, about the world, and over the whole persona -- told or
agent-added, a verdict on a persona line is applied as given. The
persona exists to serve the cooperation. Delta included; the calibrate
skill's scope paragraph follows suit.

## Migration and compatibility

Compile stops special-casing `soul.md` and renders `persona.md` first
instead. A legacy store still carrying `soul.md` compiles clean --
soul.md becomes an ordinary system/ file until the agent migrates its
content into persona.md (and preferences/ or core/ where it belongs) as
authored work in a session. No machinery migrates it. Scaffolding
creates `system/persona.md` from a new `PERSONA_TEMPLATE` (frontmatter
description + the two headers, placeholder text, no model name anywhere
-- the current SOUL_TEMPLATE's "Claude" violates the model-swap
principle and must not survive into the new template).

## Files

- `scripts/memoryctl.py` -- `PERSONA_TEMPLATE` replaces `SOUL_TEMPLATE`;
  scaffold writes `system/persona.md`; compile renders persona first;
  comments and docstring follow.
- `.shablon/templates/prompts/injected-instructions.md` -- the soul
  paragraph becomes the persona paragraph (role, two sections, telling
  vs filing, own-initiative updates, adherence, preferences routing);
  the "first person" line becomes the notes-to-self register line.
  Aim for net-zero growth: this is a swap, not an addition.
- `.shablon/templates/skills/keeping-memories/SKILL.md` -- "The Soul"
  section becomes "The Persona"; tier list line ("identity in
  `soul.md`") updated; the register paragraph generalized; the
  cap-is-deliberate line re-targeted at the persona.
- `skills/calibrate/SKILL.md` (direct edit) -- scope paragraph.
- `docs/glossary.md` -- the soul entry becomes the persona entry.
- `docs/architecture.md` -- "the soul" mention in the skills layer line.
- Spec deltas, applied exactly: `memory-store` (three REPLACEs, via
  template), `injection`, `session-lifecycle`, `calibration` (direct).
- `.shablon/templates/docs/how-to-guides/verify-the-plugin.md` --
  bootstrap expectations name persona.md.
- Rendered surfaces via `shablon generate`.

## Constraints

- Prose style: spaced double hyphen ` -- `, never an em-dash; each
  file's register preserved. No "north star" or other imported imagery
  in repo prose: say "the human's needs decide" plainly.
- The word "soul" disappears from the living surfaces. After the change,
  a case-insensitive grep for "soul" over the plugin hits only
  `docs/dev/work/` history (completed items, this plan, delta OLD
  blocks) and git history.
- memoryctl stays stdlib-only, typed; fixture stores only, never
  `~/.agents/memories/`.

## Verification

- Fresh scaffold: `system/persona.md` exists with the two headers and a
  frontmatter description; no model name anywhere in the scaffolded
  store; compile renders `<persona>` first.
- Legacy fixture (soul.md present, no persona.md): compile clean,
  soul.md rendered as an ordinary system block; validate passes.
- Growth check and accounting line unaffected (persona.md is a normal
  system/ file to them).
- `shablon generate` idempotent; em-dash sweep zero; the "soul" sweep
  above; existing statics (roster, python3) intact.
