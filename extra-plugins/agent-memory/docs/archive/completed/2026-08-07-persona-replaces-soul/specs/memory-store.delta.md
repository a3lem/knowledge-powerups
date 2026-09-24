## REPLACE

### OLD

- Memory files are written in the first person, descriptions included:
  the agent speaking about what it knows, not a system describing its
  data. Convention, not validated.

### NEW

- Memory files are notes to the agent's future self: first person where
  a note records knowledge ("I verified X"), imperative where it directs
  behavior ("Verify X before asserting") -- never the detached voice of
  a system describing its data. Descriptions stay first-person.
  Convention, not validated.

## REPLACE

### OLD

- `system/soul.md` is the agent's single identity file: how it sees
  itself -- positions, taste, self-conception -- and any role the human
  assigns (name, backstory, character), recorded as given and kept apart
  from what the agent makes of it. Chosen identity belongs there,
  invented events do not. A human never edits a memory file directly.

### NEW

- `system/persona.md` is the role the human wants the agent to play,
  exactly two sections: `# Role` (who/what the agent acts as) and
  `# Style` (how it should sound). Short list items, often imperative;
  rarely refers to the human or to episodes. No identity claims: the
  model brings its own trained identity, and memory must stay stable
  across model swaps -- no model names, no claimed history. The human
  never edits the file: they tell the agent about itself and the agent
  files it, and the agent also updates it on its own initiative when a
  gap, contradiction, or useful extra would improve future sessions.
  Behavioral avoidances and ambiguity defaults are preferences and live
  under `system/human/preferences/`, not in the persona.

## REPLACE

### OLD

- A fresh store scaffolds minimal template versions of the soul and the
  human identity file; everything real accumulates from lived
  sessions.

### NEW

- A fresh store scaffolds minimal template versions of the persona and
  the human identity file; everything real accumulates from lived
  sessions.

Reason: persona replaces soul (work item 2026-08-07-persona-replaces-soul).
The identity file retires in favor of an identity-free role file, and the
first-person convention generalizes to the notes-to-self frame that was
always underneath it.
