New capability -- no reference spec exists yet. On completion this delta
becomes `docs/specs/context-wiki.md`, with `title` and `description`
frontmatter added.

`INDEX.md` anticipates a change on another worktree that renames `index.md`
to `INDEX.md`. Until it lands, `docs/specs/directory-index.md` still says
`index.md`.

## ADD

# Context Wiki

A context wiki is a bundle of interlinked markdown files that gives AI
agents context beyond a single project. Humans and their agents maintain it
together, and several people may edit it at once. An agent may read several
context wikis, each with its own scope: one for a whole company, one for its
engineers, one for a single person.

## Layout

- A context wiki is a folder tree of markdown files tracked by git. Its
  root is the root of the git repository. [2lj7x]
- The directory structure is free: contributors organize entries however
  suits the knowledge, subdirectories included. [vo3qh]
- `skills/` at the root is reserved for agent skills in the agentskills.io
  format. [2zrwu]
- `.agents/skills` and `.claude/skills` at the root are symlinks to
  `skills/`, so a harness that is given the wiki's path discovers its
  skills. [d6fhh]
- `rules/` at the root is reserved for rules: instructions an agent follows
  in every session. Each rule states its reason. [qn3xr]
- `.claude/rules` at the root is a symlink to `rules/`. [uy73p]

## Entries

- An entry is any markdown file in the wiki other than the `INDEX.md`
  files, the special files at the root (`README.md`, `AGENTS.md`,
  `CLAUDE.md`, `TAGS.md`, `TYPES.md`, `GLOSSARY.md`) and the files under
  `skills/` and `rules/`. [e6x5v]
- An entry is about one thing, and is either a description or a
  record. [1m1ll]
- A description is about something that stays true for a while. It is kept
  current: when that thing changes, the description is edited. [k5pku]
- A record is about something that happened. It is not updated later. Its
  date is the one git records; it carries no date of its own. When the
  event happened on another day, the text says when. [o5xuu]
- A person's preference is written as a fact about that person, with its
  reason, not as a bare instruction. [a43p7]
- Uncertainty is expressed in the wording ("probably", "we assume"), not in
  frontmatter fields. [ryd73]
- Every entry has YAML frontmatter with a `title` and a one-line
  `description`. [v4qra]
- An entry may add `tags`, a list of strings, to its frontmatter. [js1ub]
- An entry may add `type`, a single string, to its frontmatter. [mlt87]

## Links

- Files link to each other with standard markdown links, never `[[name]]`
  wikilinks. [h8tl5]
- A link's href is either relative to the linking file or rooted at the
  wiki root with a leading `/`. Both forms are valid; the rooted form is
  preferred. [kg637]
- A link may point to a file that does not exist yet. [vesh6]

## Special files

- Every directory with two or more children has an `INDEX.md` that follows
  `docs/specs/directory-index.md`. [d6hpr]
- The root has a `README.md`. [np06x]
- The root has an `AGENTS.md`, and `CLAUDE.md` at the root is a symlink to
  it. `AGENTS.md` says that the folder is a context wiki, that agents
  should load the context-wiki skill, and that `README.md` is the place to
  start. [ib29y]
- The root has a `TAGS.md` listing every tag the wiki uses, sorted, one
  `- <tag>: <definition>` line per tag. [ebmk8]
- A wiki whose entries use `type` has a `TYPES.md` at the root, listing
  every type in the same format as `TAGS.md`. [3kurm]
- Jargon used across the wiki is defined in a sorted `GLOSSARY.md` at the
  root. Jargon includes abbreviations, new terms, and ordinary words used
  in a narrower sense than usual. [c7o8m]

## Changes

- A new tag, type or term is defined in `TAGS.md`, `TYPES.md` or
  `GLOSSARY.md` in the same commit that introduces it. [lx2pj]
- Moving an entry updates every link to it and the `INDEX.md` of both the
  old and the new folder, in the same commit. [1zqn1]
- An agent does not push to the remote, or update its local copy from the
  remote, without the user's permission. [2nc44]

## Setup

- A machine lists the folders of its context wikis in the environment
  variable `CONTEXT_WIKI_DIRS`, separated by colons. The order has no
  meaning. [r83n8]
