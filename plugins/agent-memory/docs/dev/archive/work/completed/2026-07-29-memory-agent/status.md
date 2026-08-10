# Status: The Memory Agent

Built. Stacks on [session-worktrees](../session-worktrees/goal.md), whose
session-lifecycle spec has landed.

Correction (2026-07-29, at archive time): soul proposals were dropped after
this was written. The shipped `agents/memory.md` carries no
ratify-on-repetition rule and `memoryctl validate` has no soul gate -- the
soul is edited like any other memory file. The "ratify-on-repetition" claim
under Delivered and the "Soul gate" check under Verified describe an
earlier build.

## Delivered

- `agents/memory.md` -- the one memory agent. Frontmatter `name: memory`,
  `tools: Read, Edit, Write, Bash, Grep, Glob`, `skills: [keeping-memories]`, no
  model override. Body carries the outside-view doctrine: no privileged copy
  of the store, `MEMORY_CONSOLIDATING=1` per Bash chain, the
  mine -> combine -> refine -> merge pipeline, ratify-on-repetition for soul
  proposals, skip discarded sessions, janitor last (never `--force`), crash
  recovery, commit as the agent, conflicts resolved by judgment.
- Three thin command skills, each pure dispatch:
  `skills/consolidate/SKILL.md` (spawn agent with the stage word or `full`),
  `skills/merge/SKILL.md` (spawn agent, mode `merge`, current session's
  branch), `skills/discard/SKILL.md` (direct `touch "$MEMORY_DIR/.discard"`,
  no agent).
- Rewrote keeping-memories's `## The Lifecycle` section: inline habits, the
  end-of-turn contract, the memory agent as outside view, the four stages,
  `/merge` as content-now-mining-later, `/discard`, the janitor, main as a
  pure merge log. The "one activity under three names" paragraph is gone.
- Updated the command roster in
  `prompts/injected-instructions.md` to name
  `/consolidate`, `/merge`, `/discard`, `/calibrate`.

## Verified (on a clone of the fixture; the real store was never touched)

- Full combine -> refine -> merge choreography over two queued session
  branches with plain git and `MEMORY_CONSOLIDATING=1 memoryctl validate`
  before every commit: main's first-parent log gained exactly one merge
  commit, both session branches read as merged, validate exits 0 on the
  final main.
- Janitor: merged session branches deleted with plain `-d`; session branch
  list empty afterward.
- Soul gate: with `MEMORY_CONSOLIDATING=1` an edited `soul.md` validates 0;
  without it, exit 2.
- Static checks: no em-dashes, `skills: [keeping-memories]` present, roster names
  the four commands.

## Not built (deferred, per approach.md open questions)

- No new memoryctl verbs -- every operation stayed a prescribed git
  one-liner in the skills and agent prompt. Promote to a CLI verb only if the
  bash proves error-prone in practice.
- SubagentStop hook as a second validation seatbelt: not added.
- A separate cheap transcript-miner subagent: not added; mining lives in the
  one agent for now.
