# Knowledge Powerups

Skills for storing and organizing what a coding agent learns, so that
knowledge compounds across sessions instead of being re-derived in each one.

## Why

An LLM is a static artifact. It knows what was trained into its weights and
what fits in the context window, and it forgets a session the moment the
session ends. Every agent harness answers this with some form of simulated
memory, and a cottage industry of memory products offers to do it better.

What users actually want is narrower than "memory": never onboarding an agent
onto the same thing twice, never re-explaining a particularity of their
context, never paying again for exploration already done.

These skills take a conventions-first approach. Knowledge lives in plain
markdown in git, and the convention -- where a file sits, what its path
implies -- carries the meaning that a database schema would otherwise carry.
Two rules drive the layouts:

1. For any piece of knowledge, there is exactly one obvious place to put it,
   so nothing is duplicated.
2. A file's location says whether it can be trusted without re-checking.

## The skills

One plugin, `knowledge-powerups`, holds every skill. They are grouped by the
knowledge store they serve.

**[code-docs](skills/code-docs/)** -- a repository's `docs/`. A docs file is
wrong when it disagrees with the code.

- `docs-folder` -- a standard layout for `docs/`, where a file's path tells
  you its role (spec, decision record, how-to, work item) and its authority
  (whether you can build on it without re-verifying against the code). Also
  how work items under `docs/wip/` are created, resumed and archived, and
  how to adopt the layout in a new or existing repository, with a scaffold
  script for the baseline files.
- `architecture-md` -- what belongs in `docs/architecture.md`, following
  matklad's ARCHITECTURE.md.
- `changelog-md` -- maintaining `CHANGELOG.md` per Keep a Changelog 1.1.0.
- `decision-records` -- when a decision is worth recording, and the minimal
  format for `docs/decisions/<NNNN>-<slug>.md`.
- `incremental-specs` -- spec-driven development for code bases that are
  never done. Reference specs in `docs/specs/` describe current behavior;
  spec deltas ride along with a planned change and describe only the
  difference; statement codes such as `[2b342]` link tests and code to the
  statements they enforce. Bundles a generator for the codes.

**[tools](skills/tools/)** -- skills the others lean on.

- `index-md` -- per-directory `index.md` tables of contents that make a file
  tree discoverable without opening every file. The title and description
  are written by hand; the list is generated and merged additively, so
  hand-written labels survive. The generator is stdlib-only Python and ships
  inside the skill.

**[context-wiki](skills/context-wiki/)** -- a git-tracked wiki that
accumulates knowledge across projects, shareable and layerable. A wiki note
is wrong when it disagrees with the world. *Not yet written.*

## Companion plugins

Optional plugins that hook into the agent harness, each a separate
marketplace entry under [plugins/](plugins/). They build on the base skills
and lose guidance, never function, when those are absent.

- **[agent-memory](plugins/agent-memory/)** -- the agent's own store,
  compiled into its system prompt each session by hooks and maintained by
  the agent itself. A memory is wrong when it disagrees with the agent's
  history or the human's preferences.

## Getting started

As a Claude Code plugin:

```
/plugin marketplace add a3lem/knowledge-powerups
/plugin install knowledge-powerups
/plugin install agent-memory      # optional companion
```

As plain skills, for any agent that reads `SKILL.md` files:

```
npx skills add a3lem/knowledge-powerups
```

## Docs

- [docs/architecture.md](docs/architecture.md) -- what this repository holds
  and how the base plugin, the shared CLIs and the companions relate.
- [docs/glossary.md](docs/glossary.md) -- the cross-cutting vocabulary.
- [docs/specs/](docs/specs/) -- reference specs, e.g. for the index
  generator.
- [docs/decisions/](docs/decisions/) -- decision records.
- [docs/explanation/](docs/explanation/) -- the reasoning behind particular
  design decisions.
