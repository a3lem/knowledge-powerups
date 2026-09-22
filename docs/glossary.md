---
title: Glossary
description: cross-cutting jargon used across the plugins, defined in one place
---

# Glossary

Terms that span the plugins. Vocabulary belonging to a single plugin is
defined in that plugin's own glossary, e.g.
[plugins/agent-memory/docs/glossary.md](../plugins/agent-memory/docs/glossary.md).

- **knowledge store** -- one of the three places knowledge is kept, each
  answerable to something different: **docs** (a repository's `docs/`, wrong
  when it disagrees with the code), a **context wiki** (a git-tracked bundle
  of markdown, wrong when it disagrees with the world), and **agent memory**
  (the agent's own store, wrong when it disagrees with the agent's history
  and the human's preferences). What a file answers to decides which store
  it belongs in.
- **role** -- what kind of document a file is: spec, decision record,
  how-to, explanation, work item. The path assigns it; nothing in the file
  declares it.
- **authority** -- whether a file may be built on without re-verifying it
  against the code. Everything in `docs/` carries full authority except
  `wip/`, `archive/` and `resources/`, which promise nothing. Chosen over
  "reliability".
- **work item** -- a unit of work in flight, held as a directory under
  `docs/wip/<slug>/`. Its location is its status: live in `wip/`, otherwise
  under `docs/archive/completed/` with an ISO date prepended to the slug.
  Dropped work is not archived -- what outlives it is promoted, and the
  directory is deleted.
- **slice** -- a sub-item of a large work item, in
  `<slug>/slices/<slug>/`, holding the same files as its parent.
- **reference spec** -- a spec in `docs/specs/` describing a capability's
  current behavior. Current or deleted; never archived.
- **decision record** -- a numbered file in `docs/decisions/` recording that
  a decision was made and why. An ADR without the assumption that the
  decision is architectural. Never edited in place: a reversal is a new
  record naming the one it supersedes.
- **spec delta** -- a `<spec-name>.delta.md` inside a work item, describing
  only the *difference* a planned change makes to a reference spec, in
  `ADD` / `REPLACE` / `DELETE` / `RENAME` operations quoted closely enough
  to apply mechanically. Archived with its work item once applied.
- **index.md** -- a directory's table of contents, generated from the child
  files' frontmatter by `cli/generate_index.py` rather than maintained by
  hand.
- **knowledge skill** -- a skill that carries a body of knowledge the human
  switches on, as opposed to a procedure the agent runs. It serves two
  modes: writing artifacts that follow the convention, and reading
  artifacts an earlier session left behind. See
  [explanation/skills-as-knowledge-switches.md](explanation/skills-as-knowledge-switches.md).
- **OKF (Open Knowledge Format)** -- the markdown conventions a context
  wiki follows, including the frontmatter `description` field that drives
  progressive disclosure.
