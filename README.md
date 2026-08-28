# Agent Knowledge Plugins

Claude Code plugins for storing and organizing what an agent learns, so that
knowledge compounds across sessions instead of being re-derived in each one.

## Why

An LLM is a static artifact. It knows what was trained into its weights and
what fits in the context window, and it forgets a session the moment the
session ends. Every agent harness answers this with some form of simulated
memory, and a cottage industry of memory products offers to do it better.

What users actually want is narrower than "memory": never onboarding an agent
onto the same thing twice, never re-explaining a particularity of their
context, never paying again for exploration already done.

These plugins take a conventions-first approach. Knowledge lives in plain
markdown in git, and the convention -- where a file sits, what its path
implies -- carries the meaning that a database schema would otherwise carry.
Two rules drive the layouts:

1. For any piece of knowledge, there is exactly one obvious place to put it,
   so nothing is duplicated.
2. A file's location says whether it can be trusted without re-checking.

## The plugins

Three knowledge stores, each answerable to something different:

- **[docs-conventions](plugins/docs-conventions/)** -- a standard layout for a
  repository's `docs/`, where a file's path tells you its role and its
  authority. A docs file is wrong when it disagrees with the code.
- **[context-wikis](plugins/context-wikis/)** -- git-tracked wikis that
  accumulate knowledge across projects, shareable and layerable. A wiki note
  is wrong when it disagrees with the world. *Not yet written.*
- **[agent-memory](plugins/agent-memory/)** -- the agent's own store,
  compiled into its system prompt each session and maintained by the agent
  itself. A memory is wrong when it disagrees with the agent's history or the
  human's preferences.

Two supporting conventions:

- **[incremental-specs](plugins/incremental-specs/)** -- reference specs kept
  current through spec deltas, for code bases that are never done.
- **[index-md](plugins/index-md/)** -- generated per-directory tables of
  contents, so a file tree is navigable without opening every file.

## Getting started

Add the marketplace, then install what you need:

```
/plugin marketplace add a3lem/knowledge-powerups
/plugin install docs-conventions
```

The plugins are independent. Installing one without its siblings loses
guidance, never function; each plugin's README states what it expects.

## Docs

- [docs/architecture.md](docs/architecture.md) -- what this repository holds
  and how the plugins relate.
- [docs/glossary.md](docs/glossary.md) -- the cross-cutting vocabulary.
- [docs/explanation/](docs/explanation/) -- the reasoning behind particular
  design decisions.
