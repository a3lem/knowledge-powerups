New capability -- no reference spec exists yet. On completion this delta
becomes `docs/specs/context-wiki.md`, with `title` and `description`
frontmatter added.

## ADD

# Context Wiki

A context wiki is a bundle of interlinked markdown files that gives AI
agents context beyond a single project. Humans and their agents maintain it
together, and several people may edit it at once. An agent may read several
context wikis, each with its own scope: one for a whole company, one for its
engineers, one for a single person.

- A context wiki is a folder tree of markdown files tracked by git. Its
  root is the root of the git repository. [2lj7x]
- The directory structure is free: contributors organize notes however
  suits the knowledge, subdirectories included. [vo3qh]
- A note is any markdown file in the wiki other than `index.md` and
  `README.md`. [e6x5v]
- Every note has YAML frontmatter with a `title` and a one-line
  `description`. [v4qra]
- A note may add `tags`, a list of strings, to its frontmatter. [js1ub]
- Files link to each other with standard markdown links, never `[[name]]`
  wikilinks. [h8tl5]
- A link's href is either relative to the linking file or rooted at the
  wiki root with a leading `/`. Both forms are valid. [kg637]
- Every directory, the root included, has an `index.md` that follows
  `docs/specs/directory-index.md`. [d6hpr]
- The root has a `README.md`. [np06x]
