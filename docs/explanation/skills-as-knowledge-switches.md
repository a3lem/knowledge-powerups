---
title: Skills as knowledge switches
description: A skill is a body of knowledge the human switches on -- the two modes such a skill serves, and what that means for names and descriptions
---

# Skills as knowledge switches

A skill is a body of knowledge the human switches on. Acting on that knowledge is a second, separate step, so a knowledge skill leads with the convention itself; procedural detail is not frontloaded.

## Two modes

When a knowledge skill is active, "use it" can mean two things:

1. **Practitioner**: create or change artifacts following the convention -- lay out docs/, write a spec delta.
2. **Cognizant reader**: correctly interpret artifacts an earlier session left behind -- a `.delta.md` is not the reference spec; a file under `dev/` carries no authority promise.

Mode 2 exists whenever practice leaves artifacts that a later agent needs the skill to interpret. Spec deltas qualify. index.md files do not: a table of contents explains itself.

## Consequences

- **Names**: the canonical full name is `plugin:skill`. The plugin carries the noun that names the knowledge (`docs-conventions`, `index-md`); a skill name only distinguishes a skill from its siblings (`using-docs`, `architecture-md`, `adopt-conventions`). "Using" suits the catch-all skill because it excludes neither mode; a more specific verb would commit to mode 1.
- **Descriptions**: triggering runs on the description, so the description must name both modes. Compare using-docs: "...or when judging whether an existing doc is trustworthy."
