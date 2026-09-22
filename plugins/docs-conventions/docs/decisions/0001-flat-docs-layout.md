---
title: Flat docs layout
description: Why docs/dev/ was dissolved into wip/, archive/ and resources/
---

# Flat docs layout

`docs/dev/` used to group everything that made no authority promise: work in
flight, the archive, and fetched material. One directory boundary was the
whole authority rule, which was its appeal. It was dissolved on 2026-09-15
into three top-level directories -- `wip/`, `archive/` and `resources/` --
because the paths it produced were long enough to be quoted wrongly from
memory (`docs/dev/archive/work/completed/<date>-<slug>/` is five levels
before the item starts) and because `dev/` named an audience rather than a
kind of content.

The cost is real and was accepted: the authority rule is now an enumeration
of three directories instead of one, so a reader must know all three rather
than one.

## Considered options

Keeping `dev/` and only shortening the archive path was the obvious smaller
move. It was rejected because `dev/work/` and `dev/references/` have nothing
in common beyond the promise they don't make, and grouping them under a name
that suggests "developer documentation" invited exactly that misreading.

`docs/references/` for in-repo material was proposed alongside
`docs/resources/` for fetched material, and dropped: "reference material",
"reference file" and "reference spec" already name the authoritative tree
throughout the conventions, so a low-authority `references/` would have
collided with the vocabulary head-on.
