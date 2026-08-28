# incremental-specs

Spec-driven development for code bases that are never done.

A spec describes a capability's behavior -- the *what*, not the *how* -- and
serves as long-term documentation. Software keeps changing, so a spec that no
longer matches the code is worse than no spec. This plugin keeps the two in
step by splitting them:

- **reference specs** in `docs/specs/` describe current behavior. They are
  current or they are deleted.
- **spec deltas** ride along with a planned change, describing only the
  *difference* it makes, in `ADD` / `REPLACE` / `DELETE` / `RENAME`
  operations quoted closely enough to apply mechanically. Once applied, the
  delta is archived with the work item.
- **statement codes** link code to spec. A behavior statement ends in a
  random 5-character tag (`[2b342]`); tests and implementation sites reference
  it with a `spec: 2b342 (docs/specs/<capability>.md)` comment. Deltas quote
  statements codes-included, so applying a delta names exactly which codes it
  touched -- grep those across the repo and the references stay in sync.

## Skills

- `using-specs` -- what counts as a spec, how deltas are written and applied,
  statement codes and how code references them, and where everything lives.
  Bundles `scripts/gen-spec-codes.py`, a small CLI that prints random
  statement codes (`-k N` for a batch, default 1).

## Dependencies

Requires **docs-conventions**: `using-specs` declares
`docs-conventions:using-docs` as a prerequisite skill, and the file locations
it uses (`docs/specs/`, `docs/dev/work/<slug>/specs/`) come from that layout.
