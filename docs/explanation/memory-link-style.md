---
title: Memory link style
description: Why links inside an agent's memory are markdown links with hrefs rooted at the store -- path over name, root-relative over file-relative, and why the wikilink form was retired
---

# Memory link style

Inside an agent's memory, a link to another memory file is a markdown link whose href is rooted at the store checkout: leading `/`, full path, extension included.

```
[details](/reference/projects/klassifai/document-types.md)
```

The label is required -- the linked word when the sentence flows, the filename when nothing better fits. `$MEMORY_DIR` plus the href is the absolute path on disk. Relative hrefs belong only to generated `index.md` bodies; targets outside the store use full URLs.

Three decisions are folded into that rule -- path over name, root-relative over file-relative, markdown link over wikilink -- and each has its own reason. The first two have held since the beginning. The third reversed on 2026-08-10; the last section says why.

## Path, not name

`[[name]]` links resolve by search: the reader (or tool) must find the file whose frontmatter carries that name, and must trust that names are unique. That holds in a flat store -- Claude Code's auto-memory links by name and gets away with it -- but a nested tree reuses stems freely (`index.md`, `overview.md`) and grows too large to police name uniqueness by hand. A path resolves by concatenation with the memory root, which the compiled prompt displays. No search, no uniqueness assumption, no ambiguity.

## Root-relative, not file-relative

Root-relative paths give every file exactly one link spelling in the whole tree. Two things follow:

- Finding all inbound links to a file is a single exact-string grep.
- Moving or renaming a file during defragmentation is a find-and-replace: rewrite the one spelling, done. Applying the change requires no judgment -- the same property spec deltas demand of their operations.

File-relative paths have neither property. A file's inbound links are spelled differently by every linker (`../a.md`, `../../x/a.md`), so finding them means resolving each candidate. And a move silently breaks the moved file's own outgoing links, which root-relative links survive. Rooted hrefs also survive a text transplant: a paragraph moved between files carries working links with it.

## Markdown link, not wikilink

The store used `[[root/relative/path.md]]` until 2026-08-10. The argument for it was syntactic partitioning: memory files legitimately link to the outside world, so reserving `[[...]]` for store-internal edges let one regex separate the jurisdictions, and a bare wikilink carried no label to drift after a rename.

Both benefits turned out to be available more cheaply.

**Every tool already reads an href as a path.** Renderers disagree only on the base a leading `/` resolves against: GitHub and Gitea use the repository root, site generators the site root, a shell the OS root, where it fails loudly. Wikilink resolution fragments instead of shifting -- Obsidian searches the vault, GitHub wiki uses flat page titles, Logseq resolves names rather than paths, MediaWiki reads a leading slash as a subpage. A wrong base is a systematic offset a reader corrects once; a different resolution rule per tool cannot be corrected at all.

**The href shape partitions link-space just as well.** External targets carry a URI scheme or a protocol-relative `//`, in-store links carry a leading `/`, and a same-file anchor starts with `#`. Validation classifies by inspecting the first characters of the href -- no probing of targets, no ambiguity -- so the wikilink syntax was buying a partition the href already provided.

**One syntax replaced two.** The old rule needed an exception for generated `index.md` bodies, which link their children relatively; that made the store a two-dialect document set, and every tool touching it had to know which dialect a given file spoke. Rooted hrefs for authored links, relative hrefs in generated index bodies, full URLs outward: the dialect and its exception retired together.

## Costs accepted

The label is now mandatory, and a mechanical rewriter can update the path but cannot know whether the words still describe the file. That is the one piece of judgment the wikilink form removed and this one restores; consolidation catches drift, validation does not check labels at all.

Typed edges survive the change. `details: [document types](/reference/.../document-types.md)` still puts the relation word in the document's voice, next to a link that mentions the file by address, and still mines with one pattern. The anchor slot now holds a display string as well, so a miner reads two words where it used to read one.

## Enforcement

Validation enforces form, not resolution. Every markdown link in the store is checked by its href, with fenced and inline code excluded: rooted hrefs must normalize to a path inside the store, escapes are violations, and a relative href is a violation in a memory file but legal in an `index.md`. A `[[...]]` anywhere is a legacy violation naming its replacement.

Resolution is deliberately unchecked. A dangling link is a forward pointer: it marks a file worth writing, and consolidation either writes the file or drops the pointer. Run from a Stop hook, form violations block the turn instead of accumulating.
