---
name: architecture-md
description: Guidance for writing docs/architecture.md, the high-level architecture overview of a code base. Use when creating an architecture overview, updating one after a large refactor, or deciding what belongs in it versus elsewhere in docs/.
---

# architecture.md

`docs/architecture.md` bridges the gap between an occasional contributor and a core developer: it answers "where's the thing that does X?". Worth writing once a project passes roughly 10k lines.

## Rules

- Only specify things that are unlikely to change, and don't try to keep the file synchronized with the code -- revisit it a couple of times a year, at big refactors.
- **Name** important files, modules, and types, but do not link them: links go stale, a name is found with symbol search.
- The codemap describes coarse-grained modules and how they relate: a map of a country, not an atlas of its states.
- Call out architectural invariants explicitly, especially those expressed as an *absence* ("X never imports Y") -- absences cannot be discovered by reading code.
- Point out boundaries between layers and systems; a boundary constrains every implementation behind it.
- Keep it short: every recurring contributor has to read it.

## Suggested sections

Not everything needs all three; start with what the project has to say.

- **Bird's Eye View** -- the problem being solved and the shape of the solution, in a few paragraphs.
- **Codemap** -- coarse-grained modules, their purpose, and how they relate.
- **Cross-Cutting Concerns** -- e.g. testing, error handling, observability.

## Further reading

- [ARCHITECTURE.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html) -- matklad's case for the file; source of this guidance.
