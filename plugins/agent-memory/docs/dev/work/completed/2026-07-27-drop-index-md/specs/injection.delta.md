## REPLACE

### OLD

- `reference/` renders as `<memory-index>`: labels and descriptions only, no
  contents, with a note saying files are read on demand. Descriptions come
  from each directory's `index.md`.

### NEW

- `reference/` renders as `<memory-index>`: labels and descriptions only, no
  contents, with a note saying files are read on demand. Descriptions come
  from each file's own frontmatter; no index file exists at rest.

## REPLACE

### OLD

- The index is pruned below `reference/projects/`: project names and
  descriptions appear, their contents do not.

### NEW

- The index is pruned below `reference/projects/`: project names and
  descriptions appear, their contents do not. A project directory's
  description comes from the `<name>.md` file inside it (e.g.
  `projects/klassifai/klassifai.md`); without one, the entry is name-only.
