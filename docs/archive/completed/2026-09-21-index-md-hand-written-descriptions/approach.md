---
title: Approach
description: Why the design uses no markers, and the marker schemes that were considered and dropped.
---

# Approach

The starting proposal was a marker that switches generation off for a range
of lines -- `<!-- manual -->` / `<!-- auto -->`, or a pragma applying to the
line below it. The design converged on no markers at all. Each scheme was
dropped for a concrete reason, recorded here so they are not re-proposed.

## Rejected: paired manual fences

`<!-- index-md:manual -->` ... `<!-- /index-md:manual -->` around hand-written
blocks. Rejected as too heavy to type and remember for the frequency of use.

## Rejected: ownership inferred from the link target

"The generator owns lines linking to files in this directory, everything else
passes through." Fails on the motivating case: an image is a file in this
directory, so a hand-placed `[diagram](diagram.png)` under a `## Figures`
heading gets pooled, sorted, and relocated into the main list. Link target
does not separate machine-written from hand-written -- an image link looks
identical either way.

## Rejected: never relocate an existing line

Preserves hand-placement without markup, but gives up "re-running normalizes
the file" and needs positional bookkeeping for every entry. Made moot once
the generator lists every local file, since there are then no hand-written
local entries to protect.

## Rejected: `---` separating generated from manual

Its only remaining tenant was links pointing outside the directory, and
`index.md` tracks only files in its own directory. With that constraint the
zone below the rule is empty, so the rule holds nothing.

## Rejected: comments grouping generated and hand-edited entries

`<!-- generated -->` / `<!-- manually edited -->` over two blocks, so a reader
can see which descriptions are safe to edit. Rejected: both markers are
advisory, so someone editing under `<!-- generated -->` still learns nothing
until the next run reverts them. It also breaks the flat alphabetical list,
and entries migrate between blocks whenever a source file gains frontmatter --
positions shifting for reasons unrelated to the directory's contents.

## Rejected: telling the author to edit the source file

An earlier version of the `changed:` report said "edit docs/glossary.md
instead". From a single snapshot the generator cannot tell an edited index
from an updated frontmatter, and updating frontmatter is the normal workflow,
so that message would be wrong most of the time. The report states the fact
and quotes both strings instead.

## Rejected: writing descriptions back into source frontmatter

Would make an index edit do what the author meant, but a tool that
regenerates an index quietly modifying other files is a much larger contract
than this one has.

## What remains

Extending the additive merge to titles, and listing non-`.md` files by
default, together solve the original problem with no syntax. The marker
schemes were all attempts to mark provenance; provenance turned out to be
derivable from whether the source file names itself.

## Decided: index.md carries no frontmatter

The H1 is the title and the first paragraph is the description, each read by
the parent directory's index. Frontmatter would repeat both, and the
repetition is what drove the H1 back and forth between "directory name",
"frontmatter title", and a constant like "Directory Index". Removing
frontmatter removes the choice.

Considered and dropped along the way: a constant H1 (`# Directory Index`),
which duplicates the static line two lines below it and leaves nothing in the
body identifying which directory you are looking at; and dropping the H1
altogether, which reads oddly for a standalone markdown file.

Keeping frontmatter had one argument -- a per-directory home for `--include`
patterns. That was scope creep on my part: which files get listed is a
separate question, and `--include` keeps its current behaviour.

## Decided: no free-form prose beyond the description

The body holds a title, an optional description paragraph, and the list.
Nothing else. Reading-order guidance belongs in the entry it is about --
`- [Architecture](architecture.md): how the pieces fit -- read this first` --
not in a paragraph of its own.

A fixed caption line (`Files/folders in this directory:`) was specced and then
dropped. Once the first paragraph is the description, the caption occupies the
same slot, so the parser would have to match it by exact text to avoid
propagating boilerplate up to the parent as a real description. That branch
exists only because the line exists. A heading naming a directory above a
list of links into that directory needs no caption; if the hint is ever wanted
it belongs in the skill, not copied into every file in the tree.

## Decided: one marker, `<!-- pinned -->`, and only where a boundary is invisible

Markers came back, narrowed to one job. Pinning is the escape hatch the design
otherwise lacks: when a member's own frontmatter is wrong and the file is not
yours to fix -- vendored, generated, someone else's repo -- "the file is the
authority on itself" leaves no move. Moving the entry below the marker freezes
it.

An `<!-- auto -->` / `<!-- manual -->` pair was considered and cut to one.
`<!-- auto -->` would label the list as machine territory, which is false and
backwards: that list is exactly where a human is meant to type, filling in
`<!-- to-do -->` gaps, and those edits are preserved. A label warning people
away from the one place they should write is worse than no label.

The count follows from which boundaries a reader cannot see. Prose to list is
visible in the markdown -- a paragraph and a list item do not look alike.
Managed list to pinned list is invisible, since both are list items. One
ambiguous boundary, one marker.

Note that the file has four zones, not two, and only one belongs to the
generator: the H1 is written once at creation and then hand-owned, the
description paragraph is hand-written throughout, the list is managed, and the
pinned block is copied through. "Everything above the marker is generated" is
wrong, and the annotated template in `goal.md` exists to stop that reading.

## Decided: never lift a description out of prose

`index-md` is an add-on, so it meets markdown files written without any
knowledge of it. The label chain reflects that: frontmatter `title`/`name`,
else the first H1, else the label the index already carries, else the
filename. Each rung is the document naming itself, so borrowing is safe.

Descriptions stop earlier. Frontmatter `description` wins, then whatever the
index already carries, then the `<!-- to-do -->` placeholder. A first
paragraph is never read.

Taking the first sentence of a first paragraph was specced and then dropped.
It fills the index with descriptions nobody wrote and nobody checked, and the
report cannot tell a serviceable borrowed sentence from a bad one -- so the
only entries flagged would be the ones that had nothing at all, which is
exactly backwards. A placeholder says "no description yet" honestly; a lifted
sentence says "described" falsely.

`index.md` is the exception, and the add-on framing is the reason. Its format
defines the first paragraph as the description, so there it is authoritative.
In a file written for some other purpose the same paragraph is a guess.

## Decided: cap the description at 250 characters

A validator keeps a description from growing into an essay that bloats the
parent's list. The cap comes from measurement, not taste: 27 hand-written doc
descriptions in this repo have a median of 66 characters and a maximum of 175.
The 300-460 character outliers were all `SKILL.md` and agent frontmatter,
where length is functional -- a different genre, excluded.

It reports rather than fails. The generator's job is to write the index, and
aborting a `-r` run over a tree because one file is wordy blocks unrelated
work.
