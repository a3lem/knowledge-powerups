---
name: index-md
description: The index.md convention -- a per-directory listing that makes information discoverable without opening every file. Use when creating or updating an index.md, adding files to an indexed directory, or improving an agent's ability to navigate any file tree (docs/, a wiki, agent memory, references).
---

# `index.md` -- a directory's table of contents

An `index.md` is a tool for discoverability: frontmatter stating the directory's purpose, then one line per entry with a link and a description. A reader -- in practice usually an agent -- reads the index and opens only what is relevant, instead of crawling the tree. This is progressive disclosure, and it pays off in any file tree an agent works in: `docs/`, a wiki, agent memory, fetched references.

Not to be confused with the `index.md` of static site generators, which is a page, not a listing. The two coexist: SSGs read `title:` frontmatter too.

## Template

```
---
title: <directory name>
description: <what purpose does the directory serve? one sentence>
---

# <title>

- [<entry title>](<relative-path>): <one-line description>
- [<subdir title>](<subdir>/): <one-line description>
```

## Authoring vs. generation

The frontmatter is authored by hand. The body is derived from the directory's contents:

- subdirectory -> `title` + `description` from that directory's own `index.md` frontmatter
- `.md` file -> `title` + `description` from its frontmatter; no frontmatter is fine -- the title falls back to the file's first heading, then its filename
- any other file -> listed by filename, but only when it matches an `--include` pattern or is already present in the index

```sh
uv run python ${CLAUDE_PLUGIN_ROOT}/skills/index-md/scripts/generate_index.py <dir>                    # one directory
uv run python ${CLAUDE_PLUGIN_ROOT}/skills/index-md/scripts/generate_index.py <dir> -r                 # whole tree, bottom-up
uv run python ${CLAUDE_PLUGIN_ROOT}/skills/index-md/scripts/generate_index.py <dir> --include '*.py'   # also list matching files (repeatable)
```

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

The source file's frontmatter remains the preferred home for a description: a description living only in the index survives regeneration, but nothing ties it to the file it describes. To correct a listing durably, fix the source file's frontmatter and regenerate.

## Inspiration

- [llms.txt](https://llmstxt.org) -- the inspiration: the same idea, applied per directory instead of per website.
- [OKF spec, section 6](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) also specifies index files, with one difference: OKF gives them no frontmatter. Ours carry `title` and `description` so that a parent directory's index has somewhere to read a subdirectory's description from.
