---
title: Memory link style
description: Why links inside an agent's memory are root-relative [[path]] wikilinks while wikis keep markdown links -- the audience rule, canonical spellings, and typed edges
---

# Memory link style

Inside an agent's memory, a link to another memory file is a wikilink whose payload is the path from the memory root, extension included:

```
[[reference/projects/klassifai/document-types.md]]
```

An optional alias serves sentences that need to flow: `[[reference/projects/klassifai/document-types.md|the document-types notes]]`. Ordinary markdown links are reserved for targets outside the memory root -- URLs, tickets, files in some repo. The `[[name]]` form is not used at all. One authored style, applied consistently; mixing styles is disallowed.

Three decisions are folded into that rule -- path over name, root-relative over file-relative, wikilink over markdown link -- and each has its own reason.

## The audience rule

Who reads a store decides its link style. A context wiki is read by humans through standard renderers, so it uses standard markdown links. Memory is read by the agent and rewritten by machinery -- consolidation, defragmentation, validation -- so it uses the form those tools can treat mechanically. The same rule decides the two stores in opposite directions; the difference is deliberate (for now, at least).

The one part of memory meant for human and navigational reading, the generated `index.md` files, keeps markdown links. Those are regenerated whenever the tree changes, so they cannot go stale, and the consistency rule governs authored prose, not generated navigation.

## Path, not name

`[[name]]` links resolve by search: the reader (or tool) must find the file whose frontmatter carries that name, and must trust that names are unique. That holds in a flat store -- Claude Code's auto-memory links by name and gets away with it -- but a nested tree reuses stems freely (`index.md`, `overview.md`) and grows too large to police name uniqueness by hand. A path resolves by concatenation with the memory root, which the compiled prompt displays. No search, no uniqueness assumption, no ambiguity.

## Root-relative, not file-relative

Root-relative paths give every file exactly one link spelling in the whole tree. Two things follow:

- Finding all inbound links to a file is a single exact-string grep.
- Moving or renaming a file during defragmentation is a find-and-replace: rewrite the one spelling, done. Applying the change requires no judgment -- the same property spec deltas demand of their operations.

File-relative paths have neither property. A file's inbound links are spelled differently by every linker (`../a.md`, `../../x/a.md`), so finding them means resolving each candidate. And a move silently breaks the moved file's own outgoing links, which root-relative links survive.

## Wikilink, not markdown link

**Syntax partitions link-space.** Memory files legitimately contain markdown links to the outside world. If store-internal references used the same syntax, every tool that touches the link graph -- link validation, the defrag rewriter, a graph builder -- would have to classify each markdown link by probing its target: memory edge or external pointer? Reserving `[[...]]` for memory edges makes the rule syntactic. Every wikilink must resolve under the memory root; every markdown link is ignored by memory tooling. One regex separates the jurisdictions.

**No label residue.** A markdown label is mandatory, and in practice it usually restates the filename: `[document types](reference/.../document-types.md)` buys no readability, and after a rename the label drifts silently -- a mechanical rewriter updates the path but cannot know whether the words still describe the file. A bare wikilink contains zero judgment; rewriting `[[old-path]]` to `[[new-path]]` is a total substitution with nothing left to go stale. Labeling is opt-in via the alias, so an aliased link marks the one place where words were chosen deliberately -- exactly the links worth a second look after a rename.

**Relation words stay in the document's voice.** Compare:

```
details: [[reference/projects/klassifai/document-types.md]]

[details](reference/projects/klassifai/document-types.md)
```

In the first line, the word and the link have separate jobs: "details" names the relation in prose, and the link mentions the file by address. In the second, the word moves into the anchor slot, which collapses what the target is and why it is pointed at into a single word. A wikilink is an identifier; a markdown link is a display string with a pointer attached.

The separation yields typed edges for free: `details:`, `source:`, `supersedes:`, `see also:` -- relation words sitting as plain prose next to identical link tokens, all mineable with one pattern. A consolidation pass can build the memory graph, edge types included, from a single regex. Anchor text offers a miner nothing to hold, because it stores the relation word and the target name in the same slot.

## Costs accepted

- GitHub and plain markdown renderers do not linkify `[[...]]`, so browsing raw memory loses click-through navigation. The reader that matters is the agent, and the generated indexes cover human navigation.
- Prose integration costs an alias. In memory this is the minority case: system files are capped at 2,200 characters, and their links are mostly trailing pointers or related-file lists, not clauses woven into argument.

## Enforcement

The convention is part of the memory contract, but validation enforces the form, not resolution: every `[[...]]` in the store must be a root-relative path -- an absolute path or an escape blocks the turn -- while the target may not exist yet. A dangling link is a forward pointer: it marks a file worth writing, and consolidation either writes the file or drops the pointer. The cost of allowing them: a `[[name]]`-form link is mechanically indistinguishable from a forward pointer, so the path form is kept by convention and by consolidation's sweep, not by the validator. Run from a Stop hook, form violations block the turn instead of accumulating.
