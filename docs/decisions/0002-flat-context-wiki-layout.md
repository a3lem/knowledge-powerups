---
name: Flat context wiki layout
description: Why entries stay at a context wiki's root, next to agent-skills/, sources/ and inbox/
---

# Flat context wiki layout

Superseded by [0004](0004-context-wiki-recommended-defaults.md): the layout
became a suggestion.

A context wiki keeps its entries at the root of its repository. The folders
with a fixed meaning sit beside them: `agent-skills/` (formerly `skills/`)
for skills the harness discovers, `sources/` for notes on citable sources,
and `inbox/` for raw material waiting to be ingested. Decided on
2026-09-28.

The layout was judged on these criteria:

1. Reserved names do not collide with names a topic folder might use,
   because agents organize entries freely.
2. Humans can see everything agents load. People co-edit wikis in Finder or
   Obsidian, and both hide dot-folders.
3. Only paths that agent harnesses already read.
4. Short absolute links, with one spelling per target.
5. "The wiki" means one thing: the repository.
6. Few reserved names, nesting levels and symlinks.

The flat layout meets all six. Its cost is that tools which walk the
entries, such as the INDEX.md generator or a future lint, must skip
`agent-skills/` and `inbox/`.

## Considered options

- **`skills/` and `rules/` at the root** (the previous layout). Both are
  plausible topic names: an HR wiki could want `skills/` for a skills
  matrix, a compliance wiki `rules/` for policy. Renaming to
  `agent-skills/` removes the collision; `rules/` was dropped for other
  reasons, see [0003](0003-no-rules-in-context-wikis.md).
- **`.agents/skills/` and `.agents/rules/`.** Hidden from the humans who
  edit the wiki, and no harness reads `.agents/rules/`.
- **One `system/` folder for everything the harness reads.** Removes only
  two of about nine reserved root names, and `system/` collides with an
  ordinary topic folder such as `systems/`.
- **Entries under `entries/` (or `wiki/`), harness files at the root.** The
  strongest alternative while `rules/` and `skills/` could collide with
  topic names. It puts `/entries/` in front of every absolute link and adds
  a level to every entry path. Naming the folder `wiki/` would also make
  "the wiki" mean both the repository and a folder in it. Once `rules/` was
  dropped and skills got a distinctive name, it had nothing left to gain.

## Sources and inbox

`sources/` holds notes on sources that other entries cite: articles,
books, talks, meetings. Most arrive through the inbox, but a note can also
be written directly. An optional `date` field holds the source's own date
(publication, or when the meeting took place). The ingestion date is not
written down, since it is the note's commit date. Only notes whose names
would otherwise repeat, such as meetings, get a date in their file name.

`inbox/` is emptied after ingestion and is gitignored apart from a
`.gitkeep`. Each person has their own inbox, so two agents never ingest the
same file, and raw material such as meeting transcripts never leaves the
machine until it has been distilled. This departs from Karpathy's
[LLM wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f),
which keeps its raw sources as an immutable archive: in a wiki shared by a
team, that archive raises size and privacy problems.
