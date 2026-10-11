# Knowledge Powerups

Every session with an agent should build on past sessions, instead of using
precious tokens to discover the same information over and over. The fastest
way to make knowledge compound is to let the agent record and organize it.
This repo gives your agent the skills to do this in a structured way, so
that bullshit doesn't accumulate and that you can still see the forest for
the pile of markdown files.

## Plugins

If you write software, install `code-knowledge` and `context-wikis`. If you
don't, `context-wikis` is all you need. Install `agent-memory` once you want
to go further.

| Plugin | For | What you get |
|--------|-----|--------------|
| [code-knowledge](plugins/code-knowledge/) | software engineers | the knowledge that usually stays in engineers' heads, written down in `docs/`: how the code is organized, why it was built this way, what changed, and what it should do |
| [context-wikis](plugins/context-wikis/) | anyone who works with an agent | knowledge about you, your team, your customers and your systems, in wikis that you, your colleagues and all your agents share across projects |
| [agent-memory](extra/agent-memory/) | power users (extension) | your agent's own memory, loaded into every session and kept up by the agent itself |

Each plugin's README lists its skills and how to start.

## Install

In Claude Code:

```
/plugin marketplace add a3lem/knowledge-powerups
/plugin install code-knowledge
/plugin install context-wikis
/plugin install agent-memory
```

For any other agent that reads `SKILL.md` files:

```
npx skills add a3lem/knowledge-powerups
```

Before version 0.2.0, one plugin named `knowledge-powerups` held every
skill. If you installed it, uninstall it and install the plugins above.

## How it works

Knowledge lives in plain markdown files in git, and where a file sits says
what it is. Two rules keep the pile in check:

1. Each piece of knowledge has exactly one obvious place, so nothing gets
   written down twice.
2. A file's location says whether you can trust it, so an agent knows when
   to check before building on it.

## Contributing

[docs/architecture.md](docs/architecture.md) explains how the repository is
organized. [docs/](docs/) also holds the glossary, specs and decision
records.
