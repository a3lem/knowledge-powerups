## DELETE

- Every `reference/` directory carries an `index.md`: hand-written
  frontmatter (`title`, `description`), generated body (see the
  index-md skill).

Reason: descriptions live in each file's frontmatter and the injected index
is compiled from the tree, so a stored index can only duplicate or drift.

## REPLACE

### OLD

- Files in `system/` additionally require a `description` and are capped at
  2,200 characters each.

### NEW

- Every memory file requires a `description` in its frontmatter; for
  `reference/` files it is the only signal the injected index shows.
- Files in `system/` are capped at 2,200 characters each.

## ADD

- A `reference/projects/<name>/` directory contains a `<name>.md` file
  describing the project; its `description` doubles as the directory's entry
  in the injected index.
