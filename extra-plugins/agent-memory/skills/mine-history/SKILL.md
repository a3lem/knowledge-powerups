---
name: mine-history
description: Mine a conversation transcript for evidence -- settle a contradiction between memories, flesh out an underdefined memory, distill patterns the session's inline writes missed. The mine process of memory consolidation, run on demand, not as a stage. Load when memory work needs a session's log.
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
turns are the highest-signal lines. The agent's own turns are the weaker
material: they are claims it made at the time, not ground truth, and they
carry no more authority than the memories they produced. A confident
assertion in the transcript settles nothing on its own -- what settles a
contradiction is what the user said, what the tools returned, or what the
work went on to show.

## Delegating the skim

A skim is extraction, not judgment, and a smaller model does it well.
When several transcripts need skimming, delegate: run a headless helper
per transcript --

    MEMORY_ENABLED=0 claude -p --model haiku < prompt-with-transcript

-- asking for candidate facts, corrections, and contradiction evidence,
each with the transcript line that supports it. `MEMORY_ENABLED=0`
keeps the helper from leaving a session branch of its own. What the
helper returns is candidate material only: judging it against the store
and filing it stays with you.

## Finding the transcript

The worktree's `.session` file holds the transcript path while the
worktree exists; after clean-up removes it, the unify commit message
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
