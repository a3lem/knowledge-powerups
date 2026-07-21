---
name: scaffold
description: Sets up the structured-docs layout in a repository's docs/ directory. Use when the user asks to set up, initialize, or scaffold docs/, to adopt the structured-docs layout in an existing project, or to create a standard documentation structure for a new one.
---

# Scaffold docs/

Set up a repository's `docs/` directory to follow the standard layout. The layout itself is defined in the `structured-docs` skill -- consult it there; it is not repeated here.

## Steps

1. **Inspect first.** Look at the target repo's `docs/` (if any) before changing anything.

2. **Greenfield** -- no `docs/`, or an empty one: run the companion script.

   ```sh
   ${CLAUDE_PLUGIN_ROOT}/skills/scaffold/scripts/scaffold_docs.sh <repo-root>
   ```

   It creates the baseline (index.md, glossary.md, architecture.md, the `dev/` workspace) and nothing more: the optional reference dirs (explanation/, how-to-guides/, specs/, adrs/) are created on demand, when the first file needs one. The script is idempotent and never overwrites an existing file.

3. **Brownfield** -- `docs/` exists with content: follow 'Adopting in an existing project' below. Nothing moves before the human approves the plan.

4. **Finish by hand.** The script leaves placeholders only. Write a one-line description per entry in `docs/index.md`, and seed `architecture.md` with the project's actual high-level structure -- read the code first, don't fabricate.

## Adopting in an existing project

Existing docs were written with intent, and the human knows which files still matter. Input from the human is valued here: adoption is a collaboration, not an autonomous cleanup.

1. **Survey.** List every file under the existing `docs/` and infer each one's role (reference, how-to, explanation, spec, ADR, work notes, stale).
2. **Draft a migration plan.** For each file: keep in place, move to a named new path, or flag. A file whose role is unclear gets a question, not a guess. Content that looks stale is flagged as a removal candidate -- removal is the human's call.
3. **Present the plan and request approval.** Clearly convey what will change: what moves where, what stays, what is flagged and why. Wait for approval before touching anything.
4. **Execute.** Apply the approved moves (`git mv` where possible, to preserve history), run the companion script to fill in the missing baseline, then finish by hand (step 4 above).

Mind authority when placing files: everything outside `dev/` promises to be current. A file that has not been verified against the code goes under `dev/` (or stays flagged), not into the reference tree.
