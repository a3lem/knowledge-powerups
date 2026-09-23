---
title: Goal
description: Why adopting repos need a way to catch up when the layout changes
---

# Goal

## The problem

The `using-docs` layout changes as we learn where it works and where it
falls short. On 2026-09-15 `docs/dev/` was dissolved, `work/` became `wip/`,
`adrs/` became `decisions/` and `how-to-guides/` became `how-tos/`. Earlier
rounds moved things too. More rounds will follow.

Every repository that adopted an earlier version is now shaped by a layout
the skill no longer describes. Nothing tells it so. Two failures follow, and
the first is the one we are actually seeing:

1. **Split trees.** An agent loads the current skill in an old repo, sees
   `docs/dev/work/`, follows the skill anyway, and creates `docs/wip/`
   beside it. The repo now holds both. That is worse than either layout on
   its own.
2. **Frozen trees.** The agent copies whatever the repo already does and the
   old layout persists indefinitely.

A library solves this with a migration guide, because two things hold there
that do not hold here: the consumer's lockfile states which version it uses,
and upgrading is a deliberate act. A skill changes underneath its adopters
silently, and no adopting repo records which version it adopted.

## Desired outcome

An agent working in a repo that adopted the conventions can tell whether the
repo is behind, and if it is, has instructions specific enough to act on
without re-deriving the change.

## Success criteria

- A repo records which version of the layout it follows.
- The skill states its own version somewhere the model reliably sees.
- A log of layout changes exists, newest first, with each entry written as
  steps to run rather than prose describing what changed.
- Newly onboarded repos get the marker written for them, so the scheme does
  not only work for repos onboarded after it ships.
- No new skill. See [approach.md](approach.md) for why.
