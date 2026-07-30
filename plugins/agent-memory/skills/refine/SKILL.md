---
name: refine
description: Improve a memory tree in place -- reconcile contradictions, deduplicate, re-home misfiled content, distill episodic detail, forget the irrelevant. The refine process of memory maintenance; load when refining. Deep passes run in the memory agent, on the unified tree or directly on main.
---

# Refine

Refining is semantic care of the tree, and the one process that is never
finished. Light forms run inline in any session: fix a wrong memory the
turn you notice it, split a file that grows a list. The deep forms below
need the whole store in view and run in the memory agent -- on the
unified tree during a consolidation pass, or directly on main between
passes.

Run `memoryctl validate` and let it pass before every commit.

## The operations

**Reconcile.** When two files state incompatible facts, find which one
the evidence supports: dates in the text, the git history of each claim,
the transcripts (mine them). The loser is corrected or deleted in the
same commit; leaving both standing is the one wrong outcome.

**Deduplicate.** One fact, one home. When the same fact lives in two
files, keep it where it is reached and link from the other -- or delete
the copy outright when the link adds nothing.

**Re-home.** The test for structure is one question, one home: small
linked files are fine; content is scattered when answering one question
means assembling files that do not point to each other. Move the
content, then rewrite every inbound link in the same pass --
root-relative link form makes finding them an exact grep.

**Distill.** Episodic detail becomes the general fact, dated when it
matters, and the episode is dropped -- the transcript remains the record
of how it was learned. `reference/history/` is drained this way every
pass: promote what generalizes into a proper home, delete the rest;
nothing lives there permanently.

**Forget.** Deletion is a memory operation, not damage. Delete what is
stale, superseded, or no longer worth carrying, and state the reason in
the deleting commit's message -- that record is what stops mining from
resurrecting it. Memory is not append-only; a tree that only grows stops
being read.

**Split.** A `system/` file pressing its 2,200-character cap, or any
file grown into a list, splits into small linked files -- each gains its
own description, its own links, its own retirement.

After any operation that adds, removes, or moves files, regenerate the
affected `index.md` bodies with the index-md skill -- their generated
listings are part of the tree's consistency, and a removed directory
disappears from its parent's index on regeneration.
