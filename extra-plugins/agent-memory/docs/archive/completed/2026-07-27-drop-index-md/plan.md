# Drop index.md From The Memory Store

Ticket: akps-4e8e. Settled in design discussion 2026-07-27.

## Goal

Remove `index.md` files from the memory store entirely. Descriptions already
live in every file's frontmatter, so the injected reference index can be
compiled straight from the tree -- no stored index artifact, nothing to go
stale, and the whole "index.md missing or out of date" failure class
disappears because the index never exists at rest.

## Approach

- `memoryctl compile`: build `<memory-index>` from each reference file's own
  frontmatter `description`. Delete `INDEX_ENTRY_RE`, `dir_description`,
  `dir_entries`, and the index.md fallbacks in `file_description`.
- Pruned directories (`reference/projects/<name>/`) take their description
  from a `<name>.md` file inside them (e.g. `projects/klassifai/klassifai.md`),
  which fits the sibling-relative naming rule. No file, no description --
  name-only entry.
- `memoryctl validate`: `description` becomes mandatory for `reference/`
  files too (it is now their only visibility signal), same as `system/`.
- using-memory skill: rewrite The Reference Tier section; drop the index-md
  prerequisite. The plugin no longer depends on the index-md plugin at all.
- Fixture: delete its index.md files, add `klassifai.md` / project files,
  re-verify compile and validate against it.

## Verification

Compile output for the fixture shows the same index entries as before minus
index.md itself; validate flags a reference file stripped of its
description; no reference to index-md remains in the plugin.

## Specs

- [specs/injection.delta.md](specs/injection.delta.md)
- [specs/memory-store.delta.md](specs/memory-store.delta.md)
- [specs/validation.delta.md](specs/validation.delta.md)
