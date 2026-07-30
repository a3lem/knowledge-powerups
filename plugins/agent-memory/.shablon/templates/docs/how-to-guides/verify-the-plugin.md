---
title: Verify the plugin
description: Scripted checks that prove memoryctl, the hooks, and the consolidation choreography behave to spec
---

<!-- Rendered from .shablon/templates/docs/how-to-guides/verify-the-plugin.md; edit that template, then run `shablon generate`. -->

# How To Verify The Plugin

Run these after touching memoryctl, hooks.json, or the agent definition.
All checks run against a fixture store -- a real git repo playing the role
of an agent's memory. Never run destructive checks against a live store:
clone it first (`git clone <store> <tmp>`; clones bring `main` only, fetch
other branches explicitly: `git fetch origin session-x:session-x`).

Environment for every command:

```sh
export MEMORY_ROOT_DIR=<dir containing the fixture>
export MEMORY_AGENT_ID=<fixture dir name>
CTL="python3 plugins/agent-memory/scripts/memoryctl.py"
```

## The SessionStart chain

Feed hand-built hook JSON on stdin, with a temp file standing in for
`CLAUDE_ENV_FILE`:

```sh
JSON='{"session_id":"t1","transcript_path":"/tmp/t1.jsonl","hook_event_name":"SessionStart","source":"startup"}'
ENVF=$(mktemp)
echo "$JSON" | $CTL worktree          # prints the worktree path
echo "$JSON" | $CTL index             # silent; refreshes reference/ index bodies
echo "$JSON" | $CTL env >> "$ENVF"
echo "$JSON" | $CTL compile | head
```

Expect: `worktrees/session-t1` exists on branch `session-t1`; `.session`
in it holds the transcript path and `.active` sits beside it (the
exclude file covers all three session markers, `.discard` included, so
none reaches git status); the env file has `MEMORY_DIR` (worktree
path) plus `MEMORY_ROOT_DIR` and `MEMORY_AGENT_ID`, never
`MEMORY_CONSOLIDATING`; compile's `root` attribute is the worktree and
`<memory-metadata>` shows the `MEMORY_DIR:` line and the consolidation
queue depth.

Concurrency and resume: run the chain for two ids, commit a distinct file
in each worktree, assert the branches diverge and main is untouched.
Re-run the chain for one id: worktree reused, `.session` refreshed,
`.active` rewritten. Delete a worktree and branch, re-run: fresh branch
off current main.

## The SessionEnd hook

```sh
echo "$JSON" | $CTL index
echo "$JSON" | $CTL session-end
```

Expect: `.active` gone from the worktree, `.session` untouched. A second
run, and a run for a session with no worktree, exit 0 silently.

`index` regenerates the body of every existing `index.md` under the
worktree's `reference/` and prints nothing to stdout (at SessionStart,
stdout belongs to the injection). It never creates an index.md -- drop a
described file into a directory without one and assert none appears --
and with the shared `cli/generate_index.py` missing it skips with a
stderr note, exit 0.

Bootstrap: point `MEMORY_ROOT_DIR` at an empty temp dir, run the chain,
expect a store whose root lists exactly `main/` and `worktrees/`: `main/`
holds the git dir, the three tiers with their reserved subdirectories
(`system/human/`, `system/human/preferences/`, `system/core/`,
`reference/projects/`, `reference/history/`, each with a `.gitkeep`), the
template soul and human identity (`system/human/human.md`,
injected under tag `identity`), seeded `index.md` files in
`reference/projects/` and `reference/history/`, and one
commit authored as the agent; the session worktree sits beside it with the
full layout present, since `.gitkeep` rides the branch.

Index rendering: a reference directory's line in `<memory-index>` carries
the description from its `index.md` frontmatter; `index.md` itself never
appears as a file entry, and its generated body is never injected.

## The Stop chain

Dirty the worktree, then run the hook's exact shape:

```sh
echo "$JSON" | $CTL validate && echo "$JSON" | $CTL commit
```

Expect: with a contract violation present, validate exits 2 and no commit
happens; once clean, the worktree's writes land as one commit on
`session-t1`, author `<agent-id> <agent-id>@agents.local`, message
`inline writes, session t1`, and the worktree reads clean. A second run is
a no-op.

## The SubagentStart hook

```sh
echo '{"session_id":"t1","agent_type":"Explore"}' | $CTL subagent-context
echo '{"session_id":"t1","agent_type":"agent-memory:memory"}' | $CTL subagent-context
```

Expect: the first prints JSON whose
`hookSpecificOutput.additionalContext` holds the compiled block with the
read-only preamble; the second prints nothing (the memory agent stays
uninjected, plugin-scoped or not).

## Skills discovery

After bootstrap: `.claude/skills` is a tracked symlink
(`git ls-files --stage .claude/skills` shows mode 120000) with target
`../skills`, inherited by every worktree and resolving to the worktree's
own tier. Simulate a legacy store (`git rm -r .claude`, commit as the
agent), start a new session: the worktree self-heals the link and the Stop
chain commits it to the branch.

End to end, drop a distinctively named skill into a fixture store's
`main/skills/`, then:

```sh
echo "Is a skill named <name> available? Answer YES or NO." \
  | claude -p --model haiku --add-dir <store>/main
```

Expect YES, and NO without the flag. (Verified 2026-07-29: discovery
follows the directory-level symlink; pipe the prompt on stdin, since
`--add-dir` consumes trailing arguments.)

## The gates

- `MEMORY_ENABLED=0`: every subcommand silent, exit 0, no store created
  in a fresh temp dir.
- `MEMORY_CONSOLIDATING=1`: `worktree` creates nothing, `compile` and
  `subagent-context` emit nothing, `commit`, `session-end`, and `index`
  are no-ops; `env` and `validate` unaffected.
- `MEMORY_SESSION=` (set empty): `worktree` prints nothing and creates
  nothing; `compile` binds `main/` with the read-only preamble; `env`
  points `MEMORY_DIR` at `main/` and forwards the switch; `commit` and
  `session-end` exit 0 silently.
- `MEMORY_SESSION_ID=pinA`: the chain builds `worktrees/session-pinA`
  whatever the stdin id says, and the auto-commit message names `pinA`;
  an explicit `--session` still wins over the pin.
- `MEMORY_SESSION_DIR=<path>`: worktree, markers, and auto-commit land at
  `<path>`, on branch `session-<id>`; `env` binds `MEMORY_DIR` to it.

## The contract

Each violation must exit 2 naming the file, and exit 0 once fixed:
an oversized `system/` file (>{{ caps.system_file }} chars); a compiled injection over
{{ caps.injection }} chars total (a dozen near-cap `system/` files trigger it); a memory
file without `description` frontmatter; an absolute or root-escaping
`[[wikilink]]`; a `skills/` entry without `SKILL.md` or missing `name` or
`description` frontmatter. A dangling-but-root-relative wikilink must
exit 0 -- forward pointers are legal. Validate with session JSON on stdin
binds to that session's worktree; a manual run (no stdin) binds to `main/`,
and a violation in a session worktree must not implicate it.

## The consolidation choreography

On a clone with two `session-*` branches:

```sh
git switch -c consolidate-r1 main
git merge --no-commit session-a   # then: $CTL validate; commit
git merge --no-commit session-b   # same
# refine commits here, validate before each
git switch main && git merge --no-ff consolidate-r1
git branch -d consolidate-r1
```

Each unify commit's message must record the session id and transcript
path. Expect: main's first-parent log gained exactly one merge commit;
both session branches appear in `git branch --merged main`; validate
exits 0 on final main. Clean-up: for a worktree without `.active`,
`git branch -d` (never `-D`, except for a discarded session) removes the
merged branch and the worktree; a worktree still holding `.active` stays,
branch included.

## Static checks

`shablon generate`, run at the plugin root, reports every surface
`unchanged` and leaves `git status` clean -- the templates under
`.shablon/templates/` are the authored source for the rendered
surfaces, so an edit made to a rendered file instead of its template
shows up here as a diff.

No spaced em-dashes in any skill, agent, or doc prose (` -- ` only); the
injected roster names exactly `/consolidate`, `/sync`, `/discard`,
`/calibrate`; the agent frontmatter preloads the conventions skill; hooks
invoke `python3`, not `uv run`.
