# Status -- growth check calibration

Implemented, uncommitted. Scope held to plan.md and
`specs/session-lifecycle.delta.md`.

## What changed, per file

- `scripts/memoryctl.py`
  - `SYSTEM_GROWTH_FLOOR = 300` beside `MAX_SYSTEM_FILE_CHARS`, with the
    reason in a comment: growth below it is not worth a turn's attention.
  - `cmd_system_delta` always exits 0. A block is one JSON object on
    stdout -- `decision: block`, `reason` the report, `systemMessage` the
    human's one-liner -- and silence is no output on either stream. All
    the earlier gates (`stop_hook_active`, no worktree, no HEAD, total
    <= 0) are untouched and still silent.
  - Trigger: `total >= SYSTEM_GROWTH_FLOOR` or a grown file crossing half
    the per-file cap (`size - delta <= 1100 < size`). The per-file loop
    computes the before-size as `size - delta`, so no extra git calls.
  - New helper `growth_report(lines, past_half)` builds the model-facing
    text: the numbers, the question, the headroom sentence (chosen by
    whether any grown file now sits past half its cap), the anti-fragment
    guard, the closing line.
  - Docstring entry for `system-delta` rewritten (it claimed exit 2); the
    subparser help now reads "block once via hook JSON".
- `hooks/hooks.json` -- Stop chain tests system-delta's stdout instead of
  its exit code; single `json=$(cat)` capture and the `python3
  "${CLAUDE_PLUGIN_ROOT}/..."` shape preserved.
- `docs/specs/session-lifecycle.md` -- the Stop bullet replaced with the
  delta's NEW text, verbatim.
- `docs/architecture.md` -- the `system-delta` verb line: net growth
  "past a floor, blocking once as Stop-hook JSON".
- `skills/refine/SKILL.md` (direct edit) -- **Condense** keeps whole
  sentences: a note is still a sentence, and compression that grinds prose
  into fragments or coins shorthand loses the memory.
- `.shablon/templates/skills/keeping-memories/SKILL.md` -- "State the fact
  in whole sentences and stop", with the fragment clause.
- `.shablon/templates/docs/how-to-guides/verify-the-plugin.md` -- the Stop
  chain snippet matches the new hook shape (and notes exit 2 belongs to
  validate alone); the growth-check section rewritten around the JSON
  expectations, the floor, the crossing case, and commit being skipped.
- `.shablon/vars.py` -- `caps.system_file_half` and `growth.floor`, so the
  how-to's numbers stay sourced from memoryctl like the caps already were.
- Rendered surfaces refreshed with `shablon generate`.

## The report as the model sees it

`reason`, for a turn that grew one file by 500 chars to 1,287:

```
Memory check: this turn added characters to system/, which is read in full in every session.
- system/soul.md: +500 chars, now 1,287 / 2,200 (58% of the cap)
Added in total: 500 chars -- 23% of one file's 2,200-char budget.
Are the additions worth their permanent place in the injection?
system/soul.md sits past half its cap, where the room that is left is worth guarding: look there first, and move detail that can be read on demand into reference/.
A trim drops content or moves it to reference/; whole sentences stay whole. Compressing prose into fragments or coined shorthand loses the memory rather than shortening it.
Trimming and confirming are both answers; either one ends the turn.
```

The headroom line for the healthy case -- every grown file under half its
cap, the shape the live incident had:

```
Every file that grew is under half its cap, so there is room: confirming the additions is the expected answer, unless something in them is detail that belongs in reference/ instead, read on demand rather than in every prompt.
```

Two or more files past half read "`a` and `b` sit past half their cap".
`systemMessage` is always `agent-memory: system/ grew this turn; asked the
agent to weigh the additions.`

## Verification

Fixture store at a temp `MEMORY_ROOT_DIR` (no live store touched); the
chain run as the exact `hooks.json` command string via `sh -c`.

1. Below the floor (+120, no crossing): no output, exit 0, commit lands,
   worktree clean.
2. +299: silent, commit lands. +300: blocks. The floor is inclusive.
3. +500: one JSON object on stdout, nothing on stderr, chain exit 0;
   `json.loads` gives exactly `decision`/`reason`/`systemMessage`; the
   reason carries the opening line, the per-file line, the total, the
   question, a headroom sentence, the `reference/` pointer, the
   anti-fragment guard, and the closing line; no commit, worktree stays
   dirty.
4. The continuation (`stop_hook_active: true`) on that same dirty tree:
   silent, exit 0, the commit lands.
5. Crossing: 1,090 -> 1,140 chars blocks on a +50 turn, far under the
   floor, and the report names the file as past half. The same file grown
   another 50, already past half, is silent again.
6. Shrinkage, no edit, and a net-zero move between two `system/` files:
   silent, exit 0, commit behaves as before.
7. Gates with growth pending: `MEMORY_ENABLED=0`, `MEMORY_SESSION=`
   (empty), unknown session id -- all silent, exit 0.
8. A validate violation (a 2,400-char `system/` file) still exits 2
   through the new chain, prints the cap message on stderr, prints nothing
   on stdout, and commits nothing.
9. `shablon generate` twice: the second run reports every surface
   unchanged.
10. Em-dash sweep (em and en dash) over every touched file: 0 hits.
11. `ruff check` clean on memoryctl and vars.py; the one `ruff format`
    diff left in memoryctl predates this work.

## Open, for the next live session

The JSON contract is verified; the UI chrome around it is not, and cannot
be headlessly. What a `decision: block` from a Stop hook actually renders
as -- whether `systemMessage` replaces the "Stop hook error" framing and
the raw command dump the incident showed -- has to be observed in a real
session. If the chrome still reads as an error, the fix is presentation
in the harness, not another change to the report.
