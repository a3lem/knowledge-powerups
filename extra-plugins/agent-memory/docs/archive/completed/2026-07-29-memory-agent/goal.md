# Goal: The Memory Agent

Ticket: akps-1b82.

## Problem

All memory maintenance beyond a session's inline writes needs a home. The
main agent can't do it: its own memory is injected into its context, which
biases any reconciliation toward the version it "remembers." And the
maintenance work -- mining transcripts, merging branches, defragmenting the
tree, ratifying soul proposals -- needs the whole repo in view, which no
single session has.

## Desired outcome

One subagent, `agents/memory.md`, performs every memory operation beyond
inline habits. It works from outside: no memory injection (harness default
for subagents -- verified against docs 2026-07-27), conventions preloaded
via `skills: [keeping-memories]`, all versions of the store met as candidate
texts weighed by evidence. The user-facing surface is four commands:
/consolidate (with optional stage word), /merge, /discard, /calibrate --
the first three fronted by this agent, /calibrate staying in the main loop
(only the main agent can converse with the human).

## Success criteria

- `/consolidate` runs mine → combine → refine → merge over the queued
  branches of the fixture and produces: distill commits on session branches,
  a `consolidate-<run>` staging branch, one merge into main, ratified or
  explicitly deferred soul proposals, and a clean queue afterward.
- `/consolidate refine` touches structure only -- no transcripts read.
- `/merge` lands a session's content in main within seconds when clean, and
  hands conflicts to the agent instead of failing.
- `/discard` marks a session; consolidation then skips it and the janitor
  eventually deletes it; the mark is undoable until swept.
- A crashed pass leaves main untouched and is resumable.
- keeping-memories's Lifecycle section describes this design (the "one activity
  under three names" paragraph is gone), and the injected instructions list
  the real command roster.
