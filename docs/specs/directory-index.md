---
title: Directory index
description: Per-directory INDEX.md files, generated from what a directory contains.
---

# Directory Index

A directory carries an `INDEX.md` listing what it contains, so a reader opens
only what is relevant instead of crawling the tree. The list is generated from
the directory's members; the descriptions come from the members themselves.

Indexes exist for progressive disclosure, and an agent pays for every one it
reads. That budget is what the format defends: one line per member, a
description short enough to skim, and no prose around the list.

## Format

- An index file is named `INDEX.md` and sits in the directory it describes.
  The name is uppercase, like `README.md` and `AGENTS.md`, because the file
  describes the directory rather than being one of its documents. It also
  sorts to the top of a listing, and a lowercase `index.md` stays free for
  ordinary use, such as a static site's home page. [cy7d8]
- The name is matched exactly, by the entries the directory lists, never by
  asking the filesystem whether a path exists. On a case-insensitive
  filesystem that question answers yes for `INDEX.md` when only `index.md`
  is there. `Index.md` and every other spelling is an ordinary file. [730xy]
- On a case-insensitive filesystem, a file with another spelling, such as
  `Index.md`, occupies the name, and writing `INDEX.md` would overwrite it.
  When the generator would write the index, such a file is a fatal error
  naming it. The legacy `index.md` is the exception, handled under
  Migration. [fa97n]
- An `INDEX.md` carries no frontmatter. It is plain markdown throughout: an
  H1, an optional description paragraph, the list, and whatever the pinned
  block holds. [er5xx]
- The body is an H1, an optional one-paragraph description, and a flat list of
  entries, one per listed member. A `<!-- pinned -->` marker and a second list
  may follow. [r6han]
- An entry reads `- [label](href): description`. When no description is known
  the position is filled with the `<!-- to-do -->` placeholder rather than left
  off, so every entry has the same shape. [2tsi8]
- The H1 is the directory's title. The generator writes the directory's own
  name there when it creates the file and never touches it again; from then on
  it is hand-written. The parent directory's index reads it as the label for
  this directory's entry. [v2b9h]
- An `INDEX.md` with no H1 has one restored as the directory's own name, noted
  under `changed:`. The generator declines to overwrite a title someone chose;
  it does not decline to replace one that is not there, since the parent's
  listing depends on it. [iw1z3]
- An H1 that no longer matches its directory's name is left alone. A title
  differing from the path is normal -- `wip/` titled "Work in progress" -- so
  the generator cannot tell a deliberate divergence from a forgotten rename
  and does not guess, and it does not try to detect the rename either. [054pu]
- Entries in the managed list are sorted case-insensitively by their label,
  with the member's filename as the tiebreak. The list is read, so it is
  ordered by what a reader sees, not by a filename they cannot predict.
  Subdirectories are not grouped separately: one flat alphabetical list, with
  the trailing slash marking a directory. Entries in the pinned block keep the
  order they were written in. [1ny6c]

## Which members are listed

- A subdirectory is listed, with href `<name>/`. [gc28b]
- A `.md` file other than `INDEX.md` is listed, with href `<name>`. [0xe5b]
- Any other file is listed only when it matches an `--include` glob, or when
  it already appears in the index. [zpon0]
- A member whose name starts with a dot is never listed, and neither is
  `INDEX.md` itself. [cck6q]
- Above the marker an entry names a direct member of this directory: one path
  segment, with a trailing slash for a directory. An entry whose href is
  anything else -- a path into a subdirectory, a `../` path, a URL -- is
  dropped and reported, along with one whose member no longer exists. The
  managed list is an index of this directory's files; a link to anything else
  belongs in the pinned block. [k5zgu]

## Excluded members

- `--exclude GLOB` (repeatable) leaves members out, matched the way
  `.gitignore` matches: a pattern with no slash matches a member's name at
  any depth, a pattern with a slash before its end matches the member's path
  relative to the named directory, and a trailing slash restricts the pattern
  to directories. `--exclude inbox/` leaves out every directory named
  `inbox`. [ozoa9]
- An excluded member is never listed. An excluded directory is not descended
  into: with `-r` it gets no `INDEX.md`, and one already inside it is left
  untouched. [4is8i]
- An excluded member does not make its directory index-worthy. [9l8o1]
- An entry naming an excluded member is dropped from the managed list and
  reported with its full text, as when its member is gone. This is the one
  exception to [33f4e]. To list an excluded member anyway, pin it. [3lree]
- `--exclude` wins over `--include`. [0qc1r]

## Where label and description come from

- A subdirectory's label comes from the H1 of its own `INDEX.md`, and its
  description from that file's first paragraph. A directory with no
  description has no paragraph: the H1 is followed straight by the
  list. [ht9j1]
- A `.md` file's label comes from its frontmatter `title`, else its first H1,
  else its filename. [w768b]
- `name` is accepted in place of `title` in frontmatter. [em1ax]
- A `.md` file's description comes from its frontmatter `description`. [87rk6]
- A first paragraph is read as a description only in an `INDEX.md`, whose
  format defines it as one. In any other markdown file the paragraph is
  ignored: it was not written for this tool, and a sentence lifted out of
  prose would enter the index as a description nobody wrote or
  checked. [dmi28]
- A file that is neither a directory nor a `.md` file is labelled with its
  filename minus its last suffix: `diagram.png` becomes `diagram`,
  `data.tar.gz` becomes `data.tar`, and a name with no suffix at all is used
  unchanged. Two members whose labels collide once the suffix is dropped are
  reported. [8yx76]

## Description length

- A description the generator copies into an index from somewhere else is
  subject to a length cap: a member's frontmatter, a subdirectory's paragraph,
  and this directory's own paragraph, which the parent's index copies. An
  index exists to be read cheaply, so a long description costs its readers
  regardless of who wrote it. The entry is still written; the overrun is
  reported, naming the file to shorten rather than the index that surfaced
  it. [y6yp7]
- A description that lives only where it is displayed is outside the cap: an
  entry's index-only text, and a pinned entry's description. Each has one
  possible author, the person who typed it into that file, and is copied
  nowhere. The length of such a description is that author's call. [kp37v]
- `--max-desc-len` sets the cap, so a caller can pick the budget its readers
  can afford. It defaults to 250 characters: across 27 hand-written doc
  descriptions in this repo the median is 66 and the longest 175, so the
  default clears real descriptions and catches essays. [qp54q]

## Merging with what the index already says

- A description in the member's own frontmatter wins over the one the index
  carries: the file is the authority on itself. [2kbkz]
- A description that exists only in the index body is kept, since another
  author may have written it there. [irr1y]
- A label the index already carries is kept when the member did not name
  itself, that is when the label would otherwise fall back to the filename. A
  member that does name itself, through frontmatter `title` or a first H1,
  wins over the index. [24inj]
- An entry whose member still exists is never dropped, even when the member
  falls outside the include set. [33f4e]
- An entry whose member no longer exists is dropped, and the drop is reported
  with the entry's full text. Everything outside the pinned block may be
  dropped -- that is the contract, and pinning is how a line is kept. Quoting
  the text is a courtesy, not a guarantee: it leaves the description
  recoverable from the run's output. [f0lcv]
- No description is invented: an entry with none in any source gets the
  `<!-- to-do -->` placeholder and nothing else. [7fv84]
- An entry with no description in any source is written with a `<!-- to-do -->`
  placeholder in the description position, so the gap is visible in the file
  and not only in terminal output. [ltfx3]
- `<!-- to-do -->` is read back as no description, never as one a human
  wrote. [yf2xo]
- The body admits four things and nothing else: the H1, one description
  paragraph, entry lines, and a single `<!-- pinned -->` marker. Anything
  further -- more prose, a section heading, a second marker -- is a fatal
  error naming the file. A second paragraph is neither a description nor an
  entry, so a multi-paragraph description fails on this rule. [y5kyl]

## The pinned block

- A `<!-- pinned -->` marker may follow the list. Entries below it are copied
  through verbatim: never relabelled, never re-described, never reordered,
  never dropped. It is the escape hatch for a member whose own frontmatter is
  wrong and not yours to fix. [e8wxq]
- A member listed in the pinned block is left out of the managed list, so no
  member is listed twice. [caa4b]
- A pinned entry may point anywhere -- a member, a path elsewhere in the repo,
  a URL. The managed list tracks only this directory's members; the pinned
  block is hand-owned and carries no such restriction. The generator neither
  validates nor rewrites what it finds there. [z9bzy]
- A pinned entry whose target is a repository path that does not resolve is
  reported, not removed: the generator deletes what it wrote and reports on
  what you wrote. A target it cannot check, such as a URL, is passed over in
  silence rather than guessed at. [2fxrs]
- The pinned block holds entry lines only. Prose or a section heading below
  the marker is the same fatal error as prose above it. [3ibxv]

## When an INDEX.md is created

- An existing `INDEX.md` is always regenerated. [1t1n1]
- Without `-r`, the named directory gets an `INDEX.md` whether or not it
  already has one. [6a8xt]
- With `-r`, every subdirectory is processed, bottom-up. [6f4vl]
- With `-r`, a directory without an `INDEX.md` gets one only when it holds
  something index-worthy: a subdirectory that has an `INDEX.md`, or a `.md`
  file carrying both a title and a description. [6w3gg]
- Bottom-up order propagates worthiness: one documented file deep in the tree
  pulls `INDEX.md` files up its ancestor chain, and unrelated directories stay
  untouched. [ijy2l]
- `-r --no-strict` creates an `INDEX.md` in every directory, worthy or
  not. [vcv98]
- `--refresh-only` regenerates existing `INDEX.md` files and never creates
  one. [u417b]

## Migration

- A directory holding `index.md` and no `INDEX.md` has a legacy index,
  written under the old name. Processing it is a fatal error naming the file
  and the `--migrate` flag, as frontmatter is. [2m10w]
- `--migrate` renames a legacy `index.md` to `INDEX.md` and regenerates it in
  the same pass, reporting the rename under `changed:`. A legacy file that
  also carries frontmatter has both converted at once. [gjr1n]
- A directory holding both `index.md` and `INDEX.md`, which only a
  case-sensitive filesystem allows, has no legacy index: `INDEX.md` is the
  index and `index.md` is an ordinary member. [6nvhr]
- A subdirectory with a legacy index is reported under `needs attention:`,
  naming `--migrate`, when its parent is indexed. The parent does not read
  the legacy file; the entry it already carries keeps its label and
  description. [kwt4a]
- Frontmatter in an `INDEX.md` is a fatal validation error naming the file and
  the `--migrate` flag. The generator never converts a file's structure
  without being asked. [s1lmg]
- `--migrate` converts each `INDEX.md` it processes: the frontmatter block is
  removed, and it supplies only what the body lacks -- the `title` becomes the
  H1 when there is no H1, the `description` becomes the paragraph when there is
  no paragraph. The body wins wherever both carry something, and whatever the
  frontmatter contributed nothing to is reported under `changed:` along with the
  conversion, so no text disappears unrecorded. The run then regenerates as
  usual, so migrating and refreshing are one pass. [6g8s7]
- `--migrate` converts only a file whose body is otherwise parseable. One
  carrying unmergeable content is the same fatal error as before, and it is
  neither renamed nor stripped of its frontmatter, so no file is left
  half-converted. [vew0l]

## Reporting

- Every run prints how many directories it indexed, and how many it skipped as
  unworthy. [871yq]
- The report has two sections. `changed:` records what the run did to text
  that already existed. `needs attention:` lists gaps: an index without a
  description, an entry still carrying the placeholder, a dropped stale entry,
  a description over the length cap, a colliding label. [wk9pu]
- When a member's own description replaces what the index carried, the run
  reports both strings under `changed:`, quoting the old and the new. It draws
  no conclusion about which was edited: an updated source and a hand-edited
  index are indistinguishable from a single run. [w1j5d]
- An entry carrying the `<!-- to-do -->` placeholder is reported whatever the
  member's file type, so the report is the list of descriptions still to
  write. Each one names where its description belongs: a subdirectory's in
  that directory's own `INDEX.md`, a `.md` file's in its frontmatter, and any
  other file's in this index, since the file cannot carry one. The placeholder
  itself stays uniform -- the entry's href already says which case it is. [8rs97]
