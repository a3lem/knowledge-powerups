# Status -- rooted markdown links replace wikilinks

Implemented and committed (`aaabab6`). Scope held to plan.md and the two
spec deltas. One wording fix landed on top of the delegated
implementation (below).

## What changed, per file

- `scripts/memoryctl.py`
  - `WIKILINK_RE` replaced by `MARKDOWN_LINK_RE` (href capture stops at
    whitespace or the closing paren, so an optional "title" stays out),
    `LEGACY_WIKILINK_RE` (any `[[...]]`), and `URI_SCHEME_RE`.
  - `wikilink_problems` becomes `link_problems`, the plan's four rules:
    `[[...]]` is a legacy violation naming the rewrite; scheme'd,
    protocol-relative, and `#`-anchor hrefs are unchecked; a rooted href
    must normalize to a path inside the store; a relative href is a
    violation outside an `index.md`. The existing `strip_code`
    fenced/inline-code exclusion is reused. Resolution stays unchecked.
  - `HUMAN_TEMPLATE` writes `[human](/system/human/human.md)`; the module
    docstring's validate entry names markdown links with rooted hrefs.
- `.shablon/templates/prompts/injected-instructions.md` -- the link
  paragraph swapped: rooted markdown links, label with the linked word,
  relative hrefs for generated index.md bodies, full URLs external, the
  human-mention rule respelled in place. 4,260 -> 4,257 characters,
  net -3.
- `.shablon/templates/skills/keeping-memories/SKILL.md` -- "Links Between
  Memories" rewritten for the rooted form (label rule with the filename
  fallback, `$MEMORY_DIR` plus href, relation-word examples respelled);
  the caps paragraph's escape link respelled.
- `.shablon/templates/docs/specs/memory-store.md` -- two REPLACEs, per
  the delta.
- `.shablon/templates/docs/specs/validation.md` -- one REPLACE, per the
  delta.
- `.shablon/templates/docs/how-to-guides/verify-the-plugin.md` -- the
  validation trigger list now names the legacy wikilink, the escaping
  href, and the relative href, and the exit-0 cases (forward pointer,
  index.md relative, URL, anchor, code).
- `skills/calibrate/SKILL.md` (direct edit) -- inbound links respelled as
  `[label](/path)`.
- `docs/glossary.md` (direct edit) -- forward pointer: "a rooted link to
  a file not yet written".
- Rendered surfaces refreshed with `shablon generate`.

Post-delegation fix: keeping-memories said external targets "are full
URLs"; a ticket is not a URL, so it now reads "are linked with full
URLs" and the redundant "URLs" left the example list.

## Verification

Fixture stores under a temp `MEMORY_ROOT_DIR`; no live store touched.

1. Spec deltas applied verbatim: all three REPLACE blocks, OLD absent
   and NEW present character-for-character in the rendered specs
   (scripted comparison).
2. Fourteen validate cases: rooted links, forward pointers, rooted
   hrefs with anchors, URLs, `mailto:`, protocol-relative, `#` anchors,
   and links inside fenced or inline code all exit 0; wikilinks (bare,
   labeled, and inside an index.md), a relative href in a memory file,
   and a `/../` escape all exit 2 with the expected message.
3. Fresh scaffold validates clean -- the new `HUMAN_TEMPLATE` link
   passes its own checks.
4. `shablon generate` idempotent; `python3 -m py_compile` clean.
5. Em-dash sweep zero. `[[` and "wikilink" survive only where the
   legacy check is named: memoryctl's regex, comment, docstring, and
   violation message; the validation spec's legacy sentence; the
   memory-store spec's "Wikilinks are legacy" sentence (delta-mandated);
   the verify how-to trigger list.
6. Statics intact: the roster still names `/consolidate`, `/sync`,
   `/discard`, `/calibrate`; `hooks.json` still invokes `python3`.
