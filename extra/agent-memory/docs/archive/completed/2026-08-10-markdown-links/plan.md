# Rooted markdown links replace wikilinks

Decision (2026-08-10), from the link-convention review: in-store links
change spelling, from root-relative wikilinks to markdown links with
rooted hrefs -- `[human](/system/human/human.md)`. The href is a URL
whose base is the store root (the checkout): leading `/`, full path,
extension included. Root-relative addressing survives unchanged -- one
canonical spelling per file, inbound links found by one grep, renames
fixed by substitution, links that survive file moves and text
transplants, forward pointers -- only the syntax carrying it changes.

Why: every tool reads a markdown href as a path and disagrees only on
the base (GitHub and Gitea resolve a leading `/` at the repo root; site
generators at the site root; the shell at the OS root, failing loudly),
while wikilink resolution fragments across the ecosystem -- Obsidian
searches the vault, GitHub wiki uses flat page titles, Logseq resolves
names rather than paths, MediaWiki reads a leading slash as a subpage.
And one syntax now covers everything: rooted hrefs for authored in-store
links, relative hrefs where a maintainer guarantees them (generated
`index.md` bodies), full URLs for external targets. The two-syntax
dialect and its index.md exception retire together.

## The convention

- Authored in-store links: `[label](/path/from/root.md)`. Rooted at the
  checkout root, so `$MEMORY_DIR` + href concatenates to the absolute
  path verbatim. Extension included.
- The label is required: the linked word when the sentence flows
  (`the [human](/system/human/human.md)`), the filename when nothing
  better fits (`[human.md](/system/human/human.md)`). No empty labels.
  Convention, not validated.
- Forward pointers stay legal: a rooted href to a file not yet written
  marks something worth writing.
- Generated `index.md` bodies keep their relative child links: the
  generator re-derives them on every refresh, and an index moves with
  its children. `cli/generate_index.py` is untouched.
- External targets: full URLs, unchecked.
- Wikilinks retire. Any `[[...]]` outside fenced or inline code is a
  violation.

## Validation

Replaces the wikilink rule, same exclusions (fenced and inline code):

- `[[...]]` -- violation: "legacy wikilink -- write
  `[label](/path-from-root)`".
- An href with a URI scheme, or protocol-relative `//` -- external,
  unchecked. A same-file anchor (`#...`) -- unchecked.
- An href with a leading `/` -- in-store: the normalized path must stay
  inside the store; escapes are violations. Resolution is not checked --
  forward pointers are legal.
- Any other href (a relative path) -- violation in a memory file, legal
  in an `index.md`, whose generated body links its children relatively.

## Files

- `scripts/memoryctl.py` -- `WIKILINK_RE` becomes markdown-link
  extraction; `wikilink_problems` becomes `link_problems` implementing
  the rules above; `HUMAN_TEMPLATE`'s mention rule respelled; module
  docstring line updated.
- `.shablon/templates/prompts/injected-instructions.md` -- the link
  paragraph rewritten: rooted-href convention, label rule, relative
  hrefs only in generated index bodies, URLs external; the human-mention
  rule respelled. This is a swap -- aim for net-zero growth or less.
- `.shablon/templates/skills/keeping-memories/SKILL.md` -- "Links
  Between Memories" rewritten; the `[[path]]` mention in the caps
  paragraph respelled.
- `.shablon/templates/docs/specs/memory-store.md` -- two REPLACEs
  (delta included).
- `.shablon/templates/docs/specs/validation.md` -- one REPLACE (delta
  included).
- `.shablon/templates/docs/how-to-guides/verify-the-plugin.md` -- the
  validation trigger list respelled for the new checks.
- `skills/calibrate/SKILL.md` (direct edit) -- the inbound `[[links]]`
  mention respelled.
- `docs/glossary.md` (direct edit) -- the forward-pointer entry
  respelled: a rooted link to a file not yet written.
- Rendered surfaces via `shablon generate` at the plugin root.

## Constraints

- Prose style: spaced double hyphen ` -- `, never an em-dash; each
  file's register preserved.
- After the change, `[[` appears on living surfaces only where the
  legacy check is named (memoryctl's violation message and test
  fixtures, the validation spec, the verify how-to); "wikilink"
  likewise. Everything else spells the new convention.
- memoryctl stays stdlib-only, typed, plain `python3`; fixture stores
  only, never `~/.agents/memories/`.
- Existing statics intact: command roster, `python3` in hooks, em-dash
  sweep zero.

## Verification

- Fixture store: rooted links validate clean; a `[[wikilink]]` exits 2
  naming the legacy rule; a relative href in a memory file exits 2; the
  same href in an `index.md` body passes; a `/../` escape exits 2;
  URLs and `#` anchors are ignored; links inside fenced and inline code
  are ignored.
- Fresh scaffold: `HUMAN_TEMPLATE` carries the rooted spelling and the
  scaffolded store validates clean.
- `shablon generate` idempotent; spec deltas apply verbatim
  (check_deltas.py against the rendered specs).
