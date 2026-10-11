# context-wikis

A context wiki is a git repository of markdown notes that people and their
agents write together. It holds knowledge that applies across projects,
such as who you are and how you work, or your organization, its customers
and its systems. An agent can read several wikis at once, each with its own
scope: for example, one for a company, one for a team and one for a single
person.

## Skills

- `/context-wiki` -- how to read, write and maintain a context wiki: what
  every wiki has, how to write notes that others can trust, and defaults a
  wiki can adopt.
- `/index-md` -- generates `INDEX.md` files, per-folder tables of contents
  that let an agent find a note without opening every file. Every wiki uses
  it. It works on any folder of markdown, not only wikis.

## Getting started

Ask your agent to:

- **Create a wiki.** It asks where the wiki goes, what belongs in it and
  who shares it, then sets up the folder.
- **Connect your wikis.** It sets up the `CONTEXT_WIKI_DIRS` environment
  variable, which lists the wikis on your machine, and tells your agent to
  read it. In Claude Code, it also shows how to load each wiki's skills.
- **Add or update notes**, in your own words or from material such as a
  meeting transcript or an article.
- **Review the wiki** for stale indexes, broken links and statements without
  a source.
- **Run a fact-checking round**: the agent asks about statements in the
  wiki one at a time, you answer in a few words, and it updates the notes.

The [skill itself](skills/context-wiki/SKILL.md) holds the full
conventions.
