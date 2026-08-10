## REPLACE

### OLD

- Every wikilink anywhere in the store (fenced and inline code excluded)
  must be in root-relative form: absolute paths and escapes are violations
  ("must be a path from the memory root"). Resolution is not checked -- a
  link to a file not yet written is a legal forward pointer.

### NEW

- Every markdown link anywhere in the store (fenced and inline code
  excluded) is checked by its href. An href with a URI scheme or a
  protocol-relative `//`, and a same-file anchor (`#...`), are external
  or local and unchecked. A rooted href (leading `/`) is an in-store
  link: its normalized path must stay inside the store -- escapes are
  violations. Resolution is not checked: a link to a file not yet
  written is a legal forward pointer. A relative href is a violation in
  a memory file and legal in an `index.md`, whose generated body links
  its children relatively. A wikilink (`[[...]]`) is a legacy violation:
  rewrite as `[label](/path-from-root)`.

Reason: rooted markdown links replace wikilinks (work item
2026-08-10-markdown-links). The checked property is the same -- in-store
links carry one canonical root-relative address -- restated for the new
syntax, with the wikilink form itself now the violation.
