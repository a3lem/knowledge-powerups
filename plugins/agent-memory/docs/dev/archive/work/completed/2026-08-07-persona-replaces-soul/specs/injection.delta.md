## REPLACE

### OLD

- `system/` is rendered in full: `soul.md` first, then files before
  subdirectories, directories as nested tags. Each file renders as
  `<{name}><path>$MEMORY_DIR/<rel></path><description>...</description>`
  followed by its body verbatim.

### NEW

- `system/` is rendered in full: `persona.md` first, then files before
  subdirectories, directories as nested tags. Each file renders as
  `<{name}><path>$MEMORY_DIR/<rel></path><description>...</description>`
  followed by its body verbatim. A legacy `soul.md` gets no special
  treatment: it renders as an ordinary `system/` file until the agent
  migrates it.

Reason: persona replaces soul (work item 2026-08-07-persona-replaces-soul).
