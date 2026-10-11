# code-knowledge

Skills that turn the tacit knowledge built up across the software
development lifecycle into files in a repository's `docs/`. A file's path
tells you what kind of document it is and whether you can build on it
without checking it against the code.

## Skills

- `/docs-folder` -- the layout of `docs/`: where specs, decision records,
  how-tos and work items go, and how much to trust each. Also how to adopt
  the layout in a new or existing repository.
- `/architecture-md` -- what belongs in `docs/architecture.md`, following
  matklad's ARCHITECTURE.md.
- `/changelog-md` -- maintaining `CHANGELOG.md` per Keep a Changelog 1.1.0.
- `/decision-records` -- when a decision is worth recording, and the format
  for `docs/decisions/<NNNN>-<slug>.md`.
- `/incremental-specs` -- spec-driven development for code bases that keep
  changing. Reference specs describe current behavior, spec deltas describe
  a planned change, and statement codes such as `[2b342]` link tests and
  code to the statements they enforce.

`/docs-folder` can generate `INDEX.md` files with `/index-md` from the
[context-wikis](../context-wikis/) plugin, if it is installed.

## Getting started

Ask your agent to set up `docs/` in your repository. If the repository has
no `docs/`, the agent creates the baseline files. If it already has docs,
the agent proposes where each file should go, and moves them once you
agree.
