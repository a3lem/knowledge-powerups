---
title: Plan
description: When a file leaves docs/resources/, and what has to be recorded for that question to be answerable
---

# Lifecycle rule for `docs/resources/`

Handover open question 3, carried out of `starting-from-handover` when that
item was archived on 2026-09-21. Tracked as akps-90a6.

Unverified: `docs/resources/` has no real contents anywhere yet, so none of
this has been tested against a directory that has actually accumulated.

## Goal

`docs/resources/` holds fetched and generated material and has no removal
rule, so it grows without bound. Promotion *into* it was settled on
2026-09-15 -- a work item's `resources/` promotes only what outlives the
item. Removal was not.

## What is settled

- A resource does not answer to this repo's code, so the test that governs
  reference material ("delete it when it disagrees with the code") gives no
  answer here. A resource goes stale against a version and a date instead.
- Where the source carries a version, that beats a date. Comparing
  `pydantic-2.11-llms.txt` against the lockfile is mechanical. A date only
  says how old a file is, not whether it is wrong. Date is the fallback for
  sources with no version.
- Modification is the one fact neither git nor a re-fetch can recover. A
  resource trimmed to part of its source has to say so, or a reader
  concludes the source lacked what was cut.
- `generated/` is a different case with an easier rule: it derives from the
  code, so it is regenerated or deleted, never repaired by hand. A file that
  cannot say how to regenerate it is not generated material -- it is
  unverified prose, and it should be verified into the reference tree or
  deleted.

## Open

1. **Where the vintage marker lives.** In the file or folder slug
   (`pydantic-2.11-llms.txt`), or in a `docs/resources/index.md`. Both are
   viable. Adriaan's call on 2026-09-16 was to leave this open until the
   directory has real contents to test against.
2. **Whether admission is the better lever.** Possibly the rule should be
   that fetched material goes to `wip/<slug>/resources/` by default and dies
   with the item, and only reaches `docs/resources/` when re-fetching is
   expensive or impossible -- auth, rate limits, a source liable to vanish.
   If that holds, removal mostly takes care of itself and this work item
   shrinks to one sentence.
3. **Whether a removal trigger is needed at all**, beyond acting when you
   open a resource and find it describes a version you are not on. A
   scheduled sweep is the alternative, and nobody runs those.
