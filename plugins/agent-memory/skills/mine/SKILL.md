---
name: mine
description: Load this skill when mining a session transcript for evidence -- settling a contradiction between memories, fleshing out an underdefined memory, or distilling patterns a session's inline writes missed. The mine process of memory consolidation; runs on demand, not as a stage.
---

# Mine

Mining reads a conversation log to pull evidence into memory. It is on
demand: nothing requires a transcript to be mined before its branch
unifies, and a transcript can still be mined after its branch is gone. It
normally runs in the memory agent -- a session injected with its own
memories should not weigh them against the record that produced them.

## When to mine

- A contradiction needs settling: two memories, or two branches, disagree,
  and the transcripts hold the ground truth.
- A memory is underdefined: a fact was filed without the context that
  makes it usable, and the session that taught it holds more.
- A learning pass: distill what the session's inline writes missed --
  corrections absorbed without filing, preferences shown rather than
  stated, failure patterns for `system/core/`.

Skim by default; read closely on signals: a long transcript with few
memory commits, or the user correcting the agent mid-session. The user's
turns are the highest-signal lines.

## Finding the transcript

The worktree's `.session` file holds the transcript path while the
worktree exists; after the janitor removes it, the unify commit message
for that session holds the same path. Transcripts are JSONL, one event
per line. The harness prunes them after a retention period (30 days by
default) -- a session that deserves close mining should get it while its
log exists.

## What leaves the pass

Findings become commits message-prefixed `distill session <id>`: on the
session's branch while it exists, on the unified tree after. Provenance
is that commit structure, not citations inside files. Write findings by
the keeping-memories conventions: the general fact, dated when it
matters, never a replay of events the log already records.

One rule binds mining absolutely: a deliberate forget stands. Before
re-adding a fact found in a transcript, check the history for its
deletion and the reason the deleting commit states
(`git log --diff-filter=D` finds deletions); re-add only on evidence
that postdates the forget.
