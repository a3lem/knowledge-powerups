---
title: Hand-written descriptions in index.md
description: Let humans describe files that carry no frontmatter, and keep those descriptions across regeneration.
---

# Goal: Hand-written descriptions in index.md

Ticket: akps-2dcc.
Spec: `plugins/index-md/docs/specs/directory-index.md`.
Delta: `specs/directory-index.delta.md`, to be applied once the change is
implemented and verified.

## Problem

`generate_index.py` derives each entry from the source file's frontmatter.
Files that carry none -- images, scripts, CSVs, `.md` files nobody gave a
frontmatter block -- have nothing to derive from. Two gaps follow:

When such a file is listed, its title is reset to the filename on every run.
Verified 2026-09-15: a hand-written `[Release runner](run.sh)` came back as
`[run.sh](run.sh)`. The description survived; the title did not. A missing
description is reported only in terminal output, so the gap is invisible in
the file itself.

Which files get listed is out of scope: `--include` keeps its current
behaviour.

Descriptions already merge additively, so half the machinery exists. The
other half doesn't, and nothing tells a reader which parts of the file they
may safely edit.

## Desired outcome

A human writes descriptions and nothing else. The generator writes links,
never prose, and never silently discards what a human wrote.

No new markup, and `index.md` drops frontmatter entirely -- it becomes plain
markdown that names and describes itself the way any other document does:

```markdown
# docs                                  <- title. Yours. The generator writes
                                           the directory's name here when it
                                           creates the file, then never touches
                                           it. The parent's index uses it as
                                           this directory's label.

Project documentation and specs.        <- description. Yours, entirely.
                                           Absent until you write it, and
                                           reported as a gap until you do. The
                                           parent's index uses it as this
                                           directory's description.

- [Architecture](architecture.md): how the pieces fit
- [architecture.png](architecture.png): <!-- to-do -->
- [wip](wip/): work items in progress
                                        ^- the list. The generator's. It writes
                                           every link, merges in titles and
                                           descriptions, and drops entries whose
                                           file is gone. Descriptions you type
                                           here are kept; <!-- to-do --> marks
                                           one still missing.

<!-- pinned -->
- [legacy](legacy.md): frozen wording   <- pinned. Yours. Copied through
                                           verbatim, in the order you wrote it.
                                           Never regenerated, never reordered,
                                           never dropped.
```

The annotations are for this document. A real `index.md` carries no such
comments -- the only marker in the file is `<!-- pinned -->`, and only when a
directory has something pinned.


- The H1 is the directory's title. The parent's `index.md` reads it as the
  label for this directory's entry.
- The first paragraph is the directory's description. The parent reads it as
  that entry's description -- the bottom-up propagation `-r` already relies
  on, moved from the frontmatter field to the paragraph.
- Both the title and the description are hand-written and survive every run.
  A directory with no description has no paragraph at all -- the H1 is
  followed straight by the list.
- Free-form prose beyond the description paragraph stays an error. A second
  paragraph is neither a description nor a list entry, so a multi-paragraph
  essay fails on that rule alone.
- A description longer than 250 characters is reported under
  `needs attention:`. The generator still writes the index -- a wordy
  description is a style problem to fix at the source, not a reason to abort
  a `-r` run over a whole tree. 250 is set from measurement: across 27
  hand-written doc descriptions in this repo the median is 66 characters and
  the longest is 175, so the cap clears every real one and bites only on an
  essay. The check applies to every description at its source, which is the
  same string the parent index propagates.

This drops the only reason `index.md` needed frontmatter. Every markdown file
in the tree can now name itself the same way -- H1 for the title, first
paragraph for the description -- with frontmatter an accepted alternative on
ordinary `.md` files rather than a requirement anywhere.

- Every child of the directory gets a line -- subdirectory, `.md` file, or
  any file matching the include set.
- An entry with no description anywhere is emitted with a `<!-- to-do -->`
  placeholder, so the gap is visible in the file rather than only in
  terminal output.
- Titles merge on the same rule as descriptions, with one test: did the file
  name itself? Frontmatter `title` or a first `# heading` wins. If the
  fallback would be the bare filename, the index's text wins.
- When a source file's frontmatter replaces what the index said, the run
  reports both strings under `changed:` -- no diagnosis, since an updated
  frontmatter and an edited index look identical from one snapshot.

## Success criteria

- An image listed via `--include '*.png'` carries a `<!-- to-do -->`
  description, and keeps the sentence a human writes there across repeated
  runs.
- A hand-written title for a file with no frontmatter survives regeneration;
  a title for a file that has frontmatter is overwritten by it.
- Deleting a file removes its entry; the run reports the drop, and names the
  bare entry that appeared alongside it so a rename doesn't silently eat a
  description.
- Bare entries appear in the `needs attention:` report; routine frontmatter
  updates appear under `changed:` and not as warnings.
- `--refresh-only` run by machinery produces the same result as a manual run,
  with no flags passed.
