# Brevity for system-level memories

Observed: system/ memories trend verbose, and every character of system/
is read in every session. The caps are hard thresholds with no signal
below them; the prompts ask for distilled content but not economical
prose; the scaffold templates model flowing prose; the injection's cost
is invisible to the agent. Five soft measures plus one reflection hook.
Lowering the caps stays in reserve, revisited after a few consolidation
passes.

## The measures

1. **Visible spend.** `<memory-metadata>` gains an accounting line:
   system/ tier characters and total compiled characters against the
   24,000 cap (e.g. `injection: 18,340 / 24,000 chars, system/: 9,120`).
   Implementation note: the line measures a block it is part of --
   measure the assembly with a placeholder and accept a few chars of
   drift, or report the pre-metadata size. Exactness is validate's job,
   not this line's.

2. **Terse, said explicitly.** Injected instructions: one or two
   sentences -- memories are notes to a future self, not essays; state
   the fact and stop; the metadata line shows what the injection costs.
   keeping-memories (Writing Memories): a short paragraph with the same
   rule and the reason (system/ is read every session; economy is part
   of the contract's spirit even where it is not validated). The
   additions must themselves be brief.

3. **Demotion habit.** system/ holds only what must shape every session.
   When a system/ file grows explanation, the explanation moves to
   reference/ and a link stays. One sentence in the injected
   instructions, folded where the cap escape is already described; a
   sentence or two in keeping-memories.

4. **Condense as a refine operation.** New operation in the refine
   skill beside Distill and Split: rewrite a verbose memory tersely,
   same facts, fewer characters. Standing goal for a pass: system/ ends
   no larger than it started unless new facts earned the growth.

5. **Terse scaffold templates.** `SOUL_TEMPLATE` and `HUMAN_TEMPLATE` in
   memoryctl.py are flowing prose; the store's first files are the
   exemplar future writes imitate. Rewrite both tersely -- same content,
   notes register -- so the store models the style from session one.

6. **Growth reflection hook (the human's design, a variation on a cap
   change).** At Stop, after validate passes and before commit: if the
   turn's uncommitted writes added net characters to system/, block once
   with a report -- per changed file, net characters added and the
   file's new size as a percentage of the 2,200 per-file cap, plus the
   total added -- and the question whether the additions respect the
   injection's limited budget. Trimming and confirming are both
   legitimate answers; the wording must not demand shrinkage. No edits
   in system/, or net shrinkage: no-op.

   Mechanics: a new memoryctl verb (working name `system-delta`),
   inserted in the Stop chain: `validate && system-delta && commit`.
   Report to stderr, exit 2 to block -- the plugin's established
   pattern. Net chars per file = working tree vs HEAD (`git show
   HEAD:<path>`); a new file counts in full. Loop guard: the Stop hook
   JSON carries `stop_hook_active: true` when the turn is already a
   stop-hook continuation -- exit 0 immediately then, so the
   continuation commits. All global gates apply (MEMORY_ENABLED=0,
   sessionless, missing store or worktree: silent no-op).

## Files

- `scripts/memoryctl.py` -- metadata accounting line (1), template
  rewrite (5), new `system-delta` verb + docstring entry (6).
- `hooks/hooks.json` -- Stop chain gains `system-delta` between
  validate and commit (6).
- `.shablon/templates/prompts/injected-instructions.md` -- items 2, 3.
- `.shablon/templates/skills/keeping-memories/SKILL.md` -- items 2, 3.
- `skills/refine/SKILL.md` -- item 4 (direct edit, not templated).
- `.shablon/templates/docs/how-to-guides/verify-the-plugin.md` -- a
  verification section for the growth hook and the accounting line.
- `docs/architecture.md` -- memoryctl verb list gains `system-delta`.
- Rendered surfaces via `shablon generate`.

## Spec assessment

- `injection.md`: metadata bullet gains the accounting line. Delta in
  `specs/injection.delta.md`.
- `session-lifecycle.md`: the Stop bullet gains the growth check between
  validation and commit. Delta in `specs/session-lifecycle.delta.md`.
- `consolidation.md`: the refine bullet gains condensing and the
  no-net-growth goal. Delta in `specs/consolidation.delta.md`.
- `memory-store.md`: one terseness convention bullet. Delta in
  `specs/memory-store.delta.md`.
- `validation.md`: unchanged -- the growth check is reflection, not a
  contract violation; nothing new blocks as invalid.
- `calibration.md`: unchanged.

## Constraints

- Injected-instructions additions for items 2-3: at most ~5 lines. The
  brevity instruction may not itself be verbose.
- Prose style: spaced double hyphen ` -- `, never an em-dash; match each
  file's register.
- memoryctl stays stdlib-only, plain `python3`, silent no-op on every
  gate; match the existing code style (type hints, asserts, specific
  exceptions).
- The growth-hook question must read as a check, not a reprimand;
  confirming and stopping is an expected outcome.
- Verification: the fixture-store checks in verify-the-plugin for the
  new verb (block on growth with correct numbers, pass-through on
  `stop_hook_active`, no-op on shrinkage/no-edit/gates), `shablon
  generate` idempotent, no em-dashes, existing static checks intact.
