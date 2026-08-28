# Status

Live. This item carries the original handover into the repo and tracks what
it asked for; it stays open until [still-todo.md](still-todo.md) is empty.

Done since the handover: agent-memory is built and at 0.3.0, docs-conventions
and index-md and incremental-specs are written, the marketplace and
per-plugin manifests are wired up.

Outstanding, roughly in the order they block each other:

- The context-wikis skills are still empty files. Nothing else waits on
  them, but the plugin ships in `marketplace.json` in that state.
- `docs/dev/references/` has no lifecycle rule, and the promotion rule
  (knowledge learned during a work item goes to docs or to the wiki) is not
  in the using-docs skill yet.
- Cross-store boundary guidance for the top-level README and the pillar
  plugins -- ticket akps-f110, in progress.
- `examples/` and `PHILOSOPHY.md` appear in the handover's repo tree and
  exist nowhere; both need a decision, not work.

Read [handover.md](handover.md) for the settled decisions and Adriaan's
working preferences, not for the repo layout: the tree it sketches predates
the renames, and `foundations/`, `simple-specs/` and `structured-docs/` are
all gone. Some of its open questions have since been answered elsewhere --
`slices/` is in the using-docs layout, and `reference/` index files came
back on 2026-07-30.
