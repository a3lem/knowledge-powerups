# Approach: The Memory Agent

## Decisions already settled (design discussion 2026-07-26/27)

- One agent, modes via spawn prompt; stages of /consolidate are arguments,
  not commands (a command promises an independent user story; mine and
  combine don't have one).
- Agent front door for /merge and /discard, with judgment on tap when a
  merge isn't clean.
- memoryctl's surface stays small: a new CLI verb only when hooks need
  deterministic stdin plumbing. Everything agent-facing is a mini skill
  over plain git -- the skill prescribes the exact commands, the agent
  runs them with Bash.
- Pipeline: mine (transcripts → distill commits, per session branch) →
  combine (branches into `consolidate-<run>`, cross-branch differences
  resolved there) → refine (semantic reconciliation and defrag on the
  combined tree) → merge (one merge into main). Refine after combine:
  reorganizing per-branch does the work twice and then re-conflicts it.
- Provenance lives in commit structure ("distill session S"), not per-fact
  citations in files.
- Mining is cheap by default (skim), escalating on signals: long transcript
  with few memory commits, user corrections mid-session, a pending soul
  proposal needing testimony.
- Soul proposals ratify on repetition across sessions; single-testimony
  proposals wait. `MEMORY_CONSOLIDATING=1` opens the soul gate and
  suppresses injection -- one variable marks "working on memory from
  outside."

## Build steps

1. No new memoryctl verbs. The operations are prescribed git one-liners
   in the skills and agent prompt: merge (attempt `git merge`, abort on
   any conflict and stop), discard (`touch "$MEMORY_DIR/.discard"`),
   janitor (delete branches and worktrees that are discarded or
   merged-and-mined and whose `.session` transcript mtime says not-live;
   never `--force`), status (`git branch --list 'session-*'` plus
   proposal counts). Escape hatch: promote an operation to a CLI verb
   only when its bash proves error-prone in practice.
2. `agents/memory.md`: frontmatter `skills: [keeping-memories]`, restricted
   tools (Read, Edit, Write, Bash, Grep, Glob), model inherited. Definition
   prompt: outside-view doctrine, the pipeline, ratify-on-repetition,
   validate before every commit, commit as the agent, janitor last, never
   touch live or dirty worktrees.
3. Thin skills: consolidate (spawn agent with stage word), merge, discard.
4. Rewrite keeping-memories's Lifecycle section and the command roster in
   prompts/injected-instructions.md.

## Open questions

- SubagentStop hook as a second seatbelt (validate after agent runs):
  plugin-level SubagentStop exists; check matcher support at build time.
- A separate cheap transcript-miner subagent: deferred until skimming costs
  bite; requires verifying whether a plugin agent may itself spawn agents.

## Verification

Fixture with two fake session branches and hand-written transcript stubs:
run the full pass, assert the success criteria in goal.md. Crash the pass
mid-refine (kill it) and assert main unchanged, then resume.
