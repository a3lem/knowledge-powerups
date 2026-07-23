---
name: index-md
description: Create or refresh index.md files -- per-directory tables of contents that make file trees discoverable to agents. Use when a directory should be navigable without opening every file, when files were added, removed, or renamed in a directory that has an index.md, or when asked to improve discoverability of docs/, a wiki, agent memory, or a reference collection.
---

# Index Files

An index file (`index.md`) gives its parent directory a table of contents so that a reader opens only what is relevant instead of crawling the tree. The format is easy to intuit:

```
---
title: <directory name>
description: <what purpose does the directory serve? one sentence>
---

# <title>

- [<entry title>](<relative-path>): <one-line description>
- [<subdir title>](<subdir>/): <one-line description>
```

## Procedure

1. Author the frontmatter by hand: `title`, and a one-sentence `description`. This is the only hand-written part.

2. Generate the body -- never write it by hand:

   ```sh
   uv run python ${CLAUDE_PLUGIN_ROOT}/skills/index-md/scripts/generate_index.py <dir>                    # one directory
   uv run python ${CLAUDE_PLUGIN_ROOT}/skills/index-md/scripts/generate_index.py <dir> -r                 # whole tree, bottom-up
   uv run python ${CLAUDE_PLUGIN_ROOT}/skills/index-md/scripts/generate_index.py <dir> --include '*.py'   # also list matching files (repeatable)
   ```

3. Read the script's "needs attention" report and fix gaps at the source: add `description` frontmatter to the file (or to the subdirectory's own index.md) and regenerate. Put a description directly in the index body only when the source cannot carry one (e.g. a non-md file).

## Generation rules

The body is derived from the directory's contents:

- subdirectory -> `title` + `description` from that directory's own `index.md` frontmatter
- `.md` file -> `title` + `description` from its frontmatter; no frontmatter is fine -- the title falls back to the file's first heading, then its filename
- any other file -> listed by filename, but only when it matches an `--include` pattern or is already present in the index

Regeneration is additive, not destructive:

- A description in the source file's frontmatter wins when the index disagrees -- the file is the authority on itself.
- A description that exists only in the index body is kept: another agent may have written it there.
- An entry whose file still exists is never dropped, even when the file falls outside the include set; only entries whose file is gone are dropped.
- Nothing is invented: an entry with no description anywhere is listed bare and reported.
- The script adds frontmatter to an index.md that lacks it, and refuses to touch a body it cannot merge (prose, section headings) -- update those by hand.

Creation is constrained so the file tree doesn't get polluted. An existing index.md is always regenerated; creating a missing one depends on mode:

- Without `-r`, the named directory simply gets one -- the request was explicit.
- With `-r`, a directory is skipped unless it holds something index-worthy: a subdirectory with an index.md, or a `.md` file carrying both `title` and `description`. Otherwise the index would say no more than `ls` does.
- Bottom-up order makes worthiness propagate: one documented file deep in the tree pulls index.md files up its ancestor chain, and unrelated directories stay untouched.
- `-r --no-strict` lifts the constraint and indexes every directory.
