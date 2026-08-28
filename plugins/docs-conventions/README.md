# docs-conventions

A standard layout for a repository's `docs/`, where a file's path tells you
two things without opening it:

- **role** -- what kind of document it is: spec, ADR, how-to, explanation,
  work item.
- **authority** -- whether you can build on it without re-verifying against
  the code. Everything outside `docs/dev/` promises to be current; `dev/`
  promises nothing.

Convention over configuration, applied to documentation. `explanation/` and
`how-to-guides/` borrow their vocabulary from [Diataxis](https://diataxis.fr).

## Skills

- `using-docs` -- the layout itself, plus how work items under
  `docs/dev/work/` are created, resumed, and archived. The catch-all skill;
  the others are narrower.
- `adopt-conventions` -- set the layout up in a repository, greenfield or
  brownfield. Ships a companion scaffold script.
- `architecture-md` -- what belongs in `docs/architecture.md`, following
  matklad's ARCHITECTURE.md.
- `changelog-md` -- maintaining `CHANGELOG.md` per Keep a Changelog 1.1.0.
- `adrs` -- when a decision is worth an ADR, and the minimal format for
  `docs/adrs/<NNNN>-<slug>.md`.

## Dependencies

None. `index-md` is a natural companion if you want generated `index.md`
tables of contents, and `incremental-specs` names `using-docs` as a
prerequisite for the `docs/specs/` part of the layout.
