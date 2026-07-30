---
title: Validation
description: The enforced memory contract -- what blocks a turn and why
---

<!-- Rendered from .shablon/templates/docs/specs/validation.md; edit that template, then run `shablon generate`. -->

# Validation

`memoryctl validate` checks the store against the contract and exits 2 with a
problem list when it is violated, 0 otherwise. A Stop hook runs it at the end
of every turn, so violations block the turn until fixed -- the contract is
compelled by the harness, not requested of the model. When it passes, the
same hook commits the session's writes (see the session-lifecycle spec).

- A `system/` file over {{ caps.system_file }} characters is a violation; the message directs
  to condensing or moving detail to `reference/`, never truncation.
- A compiled injection over {{ caps.injection }} characters in total is a violation; the
  remedy is the same -- `reference/` is indexed, not injected.
- A `system/` or `reference/` file without a `description` in its
  frontmatter is a violation: for `reference/` files the description is the
  only thing that makes them findable in the injected index.
- A `system/` file whose effective tag name (frontmatter `name`, falling
  back to the file stem) is not a valid XML tag name is a violation.
- A `skills/` entry without a `SKILL.md`, or one missing frontmatter `name`
  or `description`, is a violation: these are agent skills, and the roster
  renders from those fields.
- Every wikilink anywhere in the store (fenced and inline code excluded)
  must be in root-relative form: absolute paths and escapes are violations
  ("must be a path from the memory root"). Resolution is not checked -- a
  link to a file not yet written is a legal forward pointer.
- When the store or its `system/` directory does not exist, validate checks
  what exists and otherwise passes: a missing store never blocks a turn.
