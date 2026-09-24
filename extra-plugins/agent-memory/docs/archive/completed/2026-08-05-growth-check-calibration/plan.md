# Growth check calibration: presentation, floor, wording

Observed live (2026-08-02): system-delta rendered as "Stop hook error"
with the raw command line dumped, and the block primed an over-trim -- a
five-line soul entry compressed into fragments ("the ML-vet years")
although every grown file sat under 20% of its cap. Three fixes. The
check's design is otherwise unchanged: block once, net-growth trigger,
`stop_hook_active` pass-through.

## 1. Presentation: hook JSON, not exit 2

A reflection question is not an error; only validate keeps exit 2.
When system-delta decides to block it prints Stop-hook JSON to stdout
and exits 0:

    {"decision": "block", "reason": "<the report>",
     "systemMessage": "agent-memory: system/ grew this turn; asked the
     agent to weigh the additions."}

`reason` reaches the model; `systemMessage` gives the human a calm
one-liner instead of the error dump. When not blocking it prints
nothing, exits 0.

The Stop chain must still skip commit on a block, so a trim lands in the
turn's single auto-commit (continuation's Stop commits, as now). Exit
codes no longer carry that signal, so the hook tests stdout -- shape:

    json=$(cat); printf '%s' "$json" | ... validate \
      && out=$(printf '%s' "$json" | ... system-delta) \
      && if [ -n "$out" ]; then printf '%s' "$out"; \
         else printf '%s' "$json" | ... commit; fi

(Use if/else, not `&& ... || ...`.) Validate's exit-2 path is untouched.

Note: the docs specify the JSON contract's model-facing behavior; the
UI chrome for a JSON block is not promised. Implement per the contract
and record in status.md that the live rendering is to be observed in the
next real session.

## 2. Floor: fire only when the growth is worth a question

Block when either holds, otherwise stay silent and commit as normal:

- total net characters added to system/ >= 300
  (`SYSTEM_GROWTH_FLOOR = 300` in memoryctl, defined beside the caps);
- a grown file crossed half its per-file cap this turn
  (`len(before) <= MAX_SYSTEM_FILE_CHARS // 2 < len(after)`).

Net shrinkage and no-edit turns stay no-ops as before. The +1-char nag
disappears; approaching the cap still gets attention exactly once, at
the crossing.

## 3. Wording: expected answers and an anti-fragment guard

The report keeps its opening line, per-file lines, and total. It gains:

- Headroom framing with an expected answer. All grown files under half
  cap: confirming is the expected answer unless something belongs in
  reference/ instead. A file past half cap: name it and point at
  moving detail to reference/.
- The anti-fragment guard: a trim drops or moves content -- whole
  sentences stay whole; never compress prose into fragments or coined
  shorthand.
- Close as before: either answer ends the turn.

Same guard where the trim behavior is taught:

- refine skill, Condense: same facts, fewer characters, whole
  sentences; compression that coins shorthand loses the memory.
- keeping-memories, the terse paragraph: state the fact in whole
  sentences and stop.

## Files

- `scripts/memoryctl.py` -- JSON block output in `cmd_system_delta`,
  `SYSTEM_GROWTH_FLOOR`, half-cap crossing, report wording, docstring
  entry (currently says exit 2).
- `hooks/hooks.json` -- Stop chain per the shape above.
- `skills/refine/SKILL.md` -- Condense guard (direct edit).
- `.shablon/templates/skills/keeping-memories/SKILL.md` -- whole-sentences
  touch in the terse paragraph.
- `.shablon/templates/docs/how-to-guides/verify-the-plugin.md` -- rewrite
  the growth-check section: JSON expectations, floor cases, crossing
  case, commit skipped on block.
- `docs/architecture.md` -- the system-delta verb line (drops exit 2,
  gains the JSON block).
- Rendered surfaces via `shablon generate`.

## Spec assessment

- `session-lifecycle.md`: the Stop bullet -- floor, JSON presentation,
  commit skipped on block. Delta in `specs/session-lifecycle.delta.md`.
- All other specs unchanged: the trigger, the caps, and validate's exit-2
  contract did not move.

## Constraints

- Prose style: spaced double hyphen ` -- `, no em-dashes; match each
  file's register. The report is read by an agent mid-work: calm,
  concrete, no reprimand.
- memoryctl stays stdlib-only, typed, silent on every gate.
- Fixture-store testing only (temp MEMORY_ROOT_DIR); never touch a live
  store under ~/.agents/memories/.
- Verification matrix: below-floor addition -> silent, commit lands;
  >= 300 total -> JSON block on stdout (parse it: decision, reason,
  systemMessage present; reason carries per-file lines, headroom
  sentence, anti-fragment guard), commit skipped; small addition that
  crosses half cap -> blocks; `stop_hook_active` continuation -> silent,
  commit lands; shrinkage, no-edit, and every global gate -> silent;
  validate violation still exits 2 through the new chain; `shablon
  generate` idempotent; no em-dashes.
