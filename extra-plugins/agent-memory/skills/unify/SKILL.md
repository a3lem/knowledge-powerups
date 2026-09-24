---
name: unify
description: Merge queued session branches into one candidate tree on consolidate-<run>, recording each session's transcript path and resolving cross-branch differences with evidence. The unify process of memory consolidation; load when unifying session branches.
---

# Unify

Unifying turns the queue of session branches into one candidate tree on a
`consolidate-<run>` branch. It runs in the memory agent: no injected
memory, every branch weighed as a candidate text, never from inside a
session.

## Choreography

Work in the store's `main/` checkout -- the directory is not the branch,
and working there lets a bare `memoryctl validate` bind to the tree being
built:

    git switch -c consolidate-<run> main

Then, for each branch in `git branch --list 'session-*'`:

- Skip a branch whose worktree holds `.discard`: discarded sessions are
  not unified, not mined.
- Include branches of still-active sessions (worktree holds `.active`);
  their later writes are caught by a later pass.
- For an ended session, first commit any uncommitted writes left in its
  worktree, authored as the agent -- a crashed session may have left
  some. Leave an active session's worktree alone; its own Stop hook
  commits.
- Merge with `git merge --no-commit session-<id>`, resolve what
  conflicts, run `memoryctl validate`, then commit with a message that
  records the session id and its transcript path (from the worktree's
  `.session` file):

      unify session <id>

      transcript: <path>

  That record is what keeps the transcript minable after the branch and
  worktree are gone.

## Resolving differences

A textual conflict is git showing a real disagreement: resolve it with
evidence -- the transcripts (mine them), dates in the text, git
history -- never by picking a side blind. Recency wins only when the
evidence says the newer claim superseded the older, not merely followed
it. If the evidence cannot settle it, `git merge --abort`, stop, and
explain.

Branches also disagree without conflicting: two sessions filing
overlapping facts in different files merge cleanly and leave the tree
inconsistent. Note such overlaps as you merge; reconciling them is
refine work on the unified tree.

One class of conflict is mechanical, not a disagreement: `index.md`
bodies are generated listings, so when branches conflict there, take
either side and regenerate with the index-md skill after the merge.
Judgment applies only to the authored frontmatter description.
