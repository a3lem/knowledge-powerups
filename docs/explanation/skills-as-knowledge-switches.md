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

- **Names**: every skill ships in the one plugin, so the full name is `knowledge-powerups:<skill>` and the skill name alone must carry the noun that names the knowledge (`docs-folder`, `index-md`, `incremental-specs`). A noun commits to neither mode. A verb such as "adopt" or "generate" would commit to mode 1, which is why a procedure lives inside its knowledge skill as a reference file rather than as a skill of its own.
- **Descriptions**: triggering runs on the description, so the description must name both modes. Compare docs-folder: "...or when judging whether an existing doc is trustworthy."
