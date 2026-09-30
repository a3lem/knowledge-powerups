---
name: index-md
description: Create or refresh INDEX.md files -- per-directory tables of contents that make file trees discoverable to agents. Use when a directory should be navigable without opening every file, when files were added, removed, or renamed in a directory that has an INDEX.md, when migrating an older lowercase index.md, or when asked to improve discoverability of docs/, a wiki, agent memory, or a reference collection.
---

# Index Files

An `INDEX.md` gives its directory a table of contents, so a reader opens only
what is relevant instead of crawling the tree. The name is uppercase, like
`README.md` and `AGENTS.md`: the file describes the directory rather than being
one of its documents, it sorts to the top of a listing, and a lowercase
`index.md` stays free for ordinary use. It is plain markdown -- no
frontmatter -- and it has four parts with three different owners:

```markdown
# docs                                    <- title. Yours.

Project documentation and specs.          <- description. Yours.

- [Architecture](architecture.md): how the pieces fit
- [architecture.png](architecture.png): <!-- to-do -->
- [wip](wip/): work items in progress
                                          ^- the list. The generator's.

<!-- pinned -->
- [Upstream](https://example.com/): the spec we follow
                                          ^- pinned. Yours.
```

**The title** is the H1. The generator writes the directory's own name there
when it creates the file, and never touches it again. The parent directory's
index reads it as this directory's label.

**The description** is the first paragraph, and it is yours entirely. It is
absent until you write it, and reported as a gap until you do. The parent's
index reads it as this directory's description -- that is how a description
propagates up the tree.

**The list** belongs to the generator. It writes every link, merges in labels
and descriptions, sorts by label, and drops entries whose file is gone. A
description you type here is kept. `<!-- to-do -->` marks one still missing.

**The pinned block** is yours, copied through verbatim and never reordered or
dropped. Use it for a link the generator would otherwise manage badly or throw
away: a member whose own frontmatter is wrong and not yours to fix, or a link
to anything that is not a file in this directory.

## Procedure

1. Generate. Never write the list by hand. The generator is
   `scripts/generate_index.py` next to this SKILL.md (stdlib-only, plain
   `python3`). Resolve it against the base directory reported when this
   skill was loaded; in the repo checkout the file is a symlink into
   `clis/index-gen/`, and an installed copy of the skill carries the file
   itself.

   ```sh
   python3 <skill-base-dir>/scripts/generate_index.py <dir>                    # one directory
   python3 <skill-base-dir>/scripts/generate_index.py <dir> -r                 # whole tree, bottom-up
   python3 <skill-base-dir>/scripts/generate_index.py <dir> --include '*.png'  # also list matching files (repeatable)
   python3 <skill-base-dir>/scripts/generate_index.py <dir> -r --exclude inbox/  # leave members out (repeatable)
   ```

   `--exclude` matches the way `.gitignore` does: a pattern with no slash
   matches a name at any depth, one with a slash matches the path from `<dir>`,
   and a trailing slash matches directories only. An excluded directory is not
   descended into. It wins over `--include`.

   `--refresh-only` regenerates existing files and never creates one -- the
   mode for machinery, since a new `INDEX.md` needs its description authored.
   `--max-desc-len N` sets the description budget (default 250).

2. Write the description paragraph for any index the run reports without one.

3. Fill the `<!-- to-do -->` gaps. The report names where each belongs, because
   the right place depends on what the entry points at:

   - a `.md` file -> `description` in its frontmatter
   - a subdirectory -> the paragraph in that directory's own `INDEX.md`
   - anything else -> here in this index, since the file cannot carry text

## Where labels and descriptions come from

- A subdirectory contributes the H1 and first paragraph of its own `INDEX.md`.
- A `.md` file contributes its frontmatter `title` (or `name`) and
  `description`. Without either the label falls back to its first H1, then its filename. A first
  paragraph is **not** read as a description outside an `INDEX.md` -- lifting a
  sentence out of someone's prose would fill the index with descriptions nobody
  wrote.
- Any other file is labelled with its filename minus the last suffix
  (`diagram.png` -> `diagram`), and is listed only when it matches an
  `--include` pattern or already appears in the index.

## What survives regeneration

- A description you typed into the index is kept. The member's own frontmatter
  wins when both exist -- the file is the authority on itself -- and the run
  reports both strings without claiming which one moved.
- A label you typed is kept, unless the member names itself through frontmatter,
  an H1, or its own `INDEX.md`.
- Above the marker the list indexes this directory's members and nothing else.
  An entry for a member that still exists is never dropped, not even one outside
  the `--include` set, unless it is excluded. Everything else goes: a vanished member, a `../` path, a
  path into a subdirectory, a URL, a link to a section of a file. Each drop is
  reported with the entry's full text, so the description survives in the run's
  output. Pinning is how you keep such a line.
- Nothing is invented. An entry with no description anywhere gets the
  placeholder and nothing else.
- Prose beyond the description paragraph, a section heading, or a second
  `<!-- pinned -->` marker is a fatal error -- the generator will not guess
  where to put your text.

## When an INDEX.md is created

- Without `-r`, the named directory simply gets one; the request was explicit.
- With `-r`, a directory is skipped unless it holds something index-worthy: a
  subdirectory with an `INDEX.md`, or a `.md` file carrying both a title and a
  description. Otherwise the index would say no more than `ls` does.
- Bottom-up order makes worthiness propagate: one documented file deep in the
  tree pulls `INDEX.md` files up its ancestor chain, and unrelated directories
  stay untouched.
- `-r --no-strict` indexes every directory.

## Reading the report

`changed:` is what the run did to text that already existed. `needs attention:`
is what you may want to fix -- an index without a description, a placeholder
still to fill, a dropped entry, a description over the budget, two files whose
labels collide, a pinned link whose target is missing, a subdirectory whose
index still carries the old `index.md` name.

A pinned link to a file that no longer exists is reported and never removed.
That is the one way an `INDEX.md` can end up pointing at nothing, so fix it when
you see it.

## Legacy files

Two kinds of older index are fatal errors naming `--migrate`: one still named
`index.md`, and one carrying frontmatter. That flag converts either, or both at
once, in the same pass that regenerates the file. `index.md` is renamed to
`INDEX.md`. The frontmatter block is removed, and it supplies only what the body
lacks. The body wins, and anything the frontmatter did not contribute is quoted
in the report before it is discarded. A file the generator cannot parse is left
exactly as it was, name included.

On a case-insensitive filesystem, git (with `core.ignorecase`, the default
there) does not notice a rename that only changes case. Record it by hand:

```sh
git rm --cached -q <dir>/index.md && git add <dir>/INDEX.md
```

Next to an `INDEX.md`, a lowercase `index.md` is an ordinary member, listed like
any other `.md` file. That can only happen on a case-sensitive filesystem. On a
case-insensitive one (macOS by default), a file spelled `Index.md` or similar
holds the name, so the generator refuses to write `INDEX.md` over it.
