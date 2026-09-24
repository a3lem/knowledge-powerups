# Status -- persona replaces soul

Implemented, uncommitted, stacked on the uncommitted growth-check
calibration work. Scope held to plan.md and the four spec deltas.

## What changed, per file

- `scripts/memoryctl.py`
  - `PERSONA_TEMPLATE` replaces `SOUL_TEMPLATE`: a frontmatter
    description plus `# Role` and `# Style`, one placeholder line each, in
    the notes-to-self register and leaning imperative. No model is named
    anywhere in it -- the old template's "Claude" is gone.
  - The comment above it carries the reason: identity is trained into the
    model, so the file must hold when the model changes.
  - `scaffold_store` writes `system/persona.md`; its docstring names the
    template persona.
  - `render_system` renders `persona.md` first and skips it in the walk.
    The soul special case is gone entirely: a legacy `soul.md` is an
    ordinary `system/` file, sorted with its peers.
  - Module docstring's `compile` entry names `persona.md` first.
- `.shablon/templates/prompts/injected-instructions.md`
  - The soul paragraph is replaced by the persona paragraph: the role the
    human wants played, the two sections, they tell and you file,
    own-initiative updates, act-the-persona adherence with the
    update-before-deviating rule, avoidances and ambiguity defaults routed
    to `system/human/preferences/`.
  - "write them in the first person, descriptions included" becomes the
    notes-to-self register line; the descriptions rule survives in the
    next sentence, which already says "from your perspective".
  - The wikilink paragraph was rewrapped where the swap left short lines;
    no wording changed there.
- `.shablon/templates/skills/keeping-memories/SKILL.md`
  - Frontmatter description: "the soul" -> "the persona".
  - Tier list: "identity in `soul.md`" -> "the persona in `persona.md`".
  - Writing Memories: "Write in the first person" generalizes to "Write
    notes to the future self" -- first person for knowledge, imperative
    for direction, descriptions still first person.
  - "The Soul" -> "The Persona", rewritten: the two sections and the
    register; the preferences routing rule; the pen and the
    own-initiative clause; the no-identity/model-swap rationale (stated
    without naming any model); adherence with the explicit-request
    carve-out; `system/core/` kept, minus the "soul's counterweight"
    phrase; the cap-is-deliberate line re-aimed at the persona.
    Dropped with the soul: individuation, chosen identity, and the
    positions paragraph.
- `skills/calibrate/SKILL.md` (direct edit) -- the scope paragraph is the
  calibration delta's NEW bullet, with the file path named as before.
- `docs/glossary.md` -- the **soul** entry becomes **persona**, in place.
- `docs/architecture.md` -- skills layer: "tiers, the soul" -> "tiers, the
  persona".
- `.shablon/templates/docs/how-to-guides/verify-the-plugin.md` -- bootstrap
  expects the template persona (`system/persona.md`, two headers, no model
  named, injected first) beside the human identity.
- Spec deltas applied verbatim: `memory-store` (three REPLACEs, via its
  template), `injection`, `session-lifecycle`, `calibration` (direct).
- Rendered surfaces refreshed with `shablon generate`.

## PERSONA_TEMPLATE

```
---
description: The role I'm asked to play -- what to act as, and how to sound.
---

# Role

- Nothing assigned yet. File what to act as here, one short line each.

# Style

- Nothing assigned yet. File how to sound here, one short line each.
```

## The persona paragraph, as injected

```
The persona (system/persona.md) is the role the human wants played, in two
sections: # Role, what you act as; # Style, how you sound. They tell you and
you file it; you also update it when a gap, contradiction, or useful extra
would serve the next session. Act the persona: where it and your defaults
differ, it is the more specific instruction; a deliberate deviation is an
update -- edit persona.md first, then act. Avoidances and ambiguity defaults
are preferences: system/human/preferences/.
```

The register line it travels with: "These are your memories, notes to your
future self: first person for knowledge, imperative for direction."

`prompts/injected-instructions.md`: 4,163 -> 4,260 characters, +97. A swap,
not an addition -- the persona paragraph runs 41 characters over the soul
paragraph it replaces and the register line 26 over "write them in the first
person, descriptions included".

## Verification

Fixture stores under a temp `MEMORY_ROOT_DIR`; no live store touched.

1. Fresh scaffold: `main/system/persona.md` exists with the frontmatter
   description and both headers; the tree is otherwise unchanged
   (`.gitkeep`s, `human.md`, the two seeded `index.md`s). Compile's system
   tags come out `persona, core, human` -- `<persona>` first. Validate
   exits 0.
2. Case-insensitive sweep for "claude" and "soul" over every tracked file
   of the scaffolded store: zero hits. (The store's tracked
   `.claude/skills` symlink path is the harness's discovery convention,
   not content, and is unrelated to the model name.)
3. Legacy fixture -- `persona.md` removed, a described `soul.md` committed
   in its place: compile exits 0 with `soul` rendered as an ordinary
   `system/` block, validate exits 0.
4. Ordering, with `persona.md` present alongside `aardvark.md`, `soul.md`,
   `zebra.md`: tags come out `persona, aardvark, soul, zebra, core, human`
   -- persona first, soul plainly alphabetical among its peers, no special
   case left.
5. Growth check: +421 characters into `persona.md` blocks with the
   system-delta JSON (`decision`, `reason`, `systemMessage`), exit 0, the
   report naming `system/persona.md: +421 chars, now 665 / 2,200`. A
   14-character edit stays silent, exit 0. persona.md is an ordinary
   `system/` file to the check, as intended.
6. Case-insensitive "soul" sweep over the plugin: hits only under
   `docs/dev/work/` -- plus one deliberate hit, `docs/specs/injection.md`,
   where the injection delta's NEW text spells out that a legacy `soul.md`
   gets no special treatment. That mention is required by the delta,
   applied exactly; the plan's sweep constraint did not anticipate it.
7. `shablon generate` twice: every surface `unchanged` on the second run.
8. Em-dash and en-dash sweep over every changed file: zero.
9. Statics intact: the injected roster still names `/consolidate`,
   `/sync`, `/discard`, `/calibrate`; `hooks.json` still invokes
   `python3`, never `uv run`.
10. `ruff check` clean on `scripts/memoryctl.py` and `.shablon/vars.py`;
    memoryctl's imports are still stdlib only.

## Migration, for a live store

No machinery migrates an existing `soul.md`. It keeps compiling as an
ordinary `system/` file; moving its content into `persona.md`,
`system/human/preferences/`, or `system/core/` is authored work for a
session.
