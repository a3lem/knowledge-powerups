---
title: Status
description: Closing state of the handover item at archival
---

# Status

Archived complete on 2026-09-21. The item's job was to carry the 2026-07-21
handover into this repo and track what it asked for. That job is done: the
repo is well past the handover, and the tree the handover sketches no longer
exists.

Delivered since the handover: agent-memory built and at 0.3.0;
docs-conventions, index-md and incremental-specs written; the marketplace
and all five per-plugin manifests and READMEs in place; the top-level README
written.

Four threads were still live at archival and were promoted to tickets rather
than buried here. [still-todo.md](still-todo.md) records the disposition of
every item; the live ones are:

- akps-468d -- the two context-wikis skills are still empty files, though
  the plugin ships in `marketplace.json`.
- akps-efa9 -- the wiki companion CLI's fate.
- akps-90a6 -- lifecycle rule for `docs/resources/`. Design notes moved to
  `plugins/docs-conventions/docs/wip/resources-lifecycle/`.
- akps-5c01 -- the docs-versus-wiki promotion rule is missing from
  `using-docs`.

Three items were resolved by deciding not to do them: PHILOSOPHY.md,
`examples/`, and the cross-store README sections whose ticket (akps-f110)
was cancelled in July.

Read [handover.md](handover.md) for the settled decisions and Adriaan's
working preferences, not for the repo layout. Its tree predates the renames:
`foundations/`, `simple-specs/` and `structured-docs/` are all gone, and its
docs-layout section was superseded on 2026-09-15 when `docs/dev/` was
dissolved into `wip/`, `archive/` and `resources/` -- see
[plugins/docs-conventions/docs/decisions/0001-flat-docs-layout.md](../../../../plugins/docs-conventions/docs/decisions/0001-flat-docs-layout.md).
Some of its open questions were answered elsewhere: `slices/` is in the
using-docs layout, and `reference/` index files came back on 2026-07-30.
