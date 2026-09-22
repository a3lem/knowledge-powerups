## REPLACE

### OLD

- `system/human/human.md` is the human's identity file (who they are:
  name, role, working context); `system/human/preferences/` holds their
  preferences, one small file each. A memory that mentions the human
  writes `the [[system/human/human.md|human]]`, never their name -- the
  name lives only in `human.md`, and every mention of them is one exact
  grep.

### NEW

- `system/human/human.md` is the human's identity file (who they are:
  name, role, working context); `system/human/preferences/` holds their
  preferences, one small file each. A memory that mentions the human
  writes `the [human](/system/human/human.md)`, never their name -- the
  name lives only in `human.md`, and every mention of them is one exact
  grep.

Reason: rooted markdown links replace wikilinks (work item
2026-08-10-markdown-links). The standing application keeps its meaning;
only the spelling changes.

## REPLACE

### OLD

- A link from one memory file to another is a wikilink whose payload is the
  path from the memory root (the checkout), extension included:
  `[[reference/projects/klassifai/document-types.md]]`, optionally
  `[[path|label]]`. The target need not exist yet: an unresolved link is a
  forward pointer to a file worth writing. Markdown links are reserved for
  targets outside the store.

### NEW

- A link from one memory file to another is a markdown link whose href is
  rooted at the checkout: leading `/`, full path, extension included --
  `[details](/reference/projects/klassifai/document-types.md)`. The label
  is required -- the linked word when the sentence flows, the filename
  when nothing better fits; convention, not validated. `$MEMORY_DIR` plus
  the href is the absolute path. The target need not exist yet: an
  unresolved link is a forward pointer to a file worth writing. Relative
  hrefs belong only to generated `index.md` bodies; targets outside the
  store use full URLs. Wikilinks are legacy and rejected by validation.

Reason: rooted markdown links replace wikilinks (work item
2026-08-10-markdown-links). Root-relative addressing and forward-pointer
semantics survive; the syntax changes to the form every tool reads as a
path, and one syntax now covers authored, generated, and external links.
