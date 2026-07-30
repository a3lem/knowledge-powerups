---
name: discard
description: Load this skill when the user invokes /discard or says this session is not worth remembering -- mark the current session so consolidation skips it and clean-up deletes it. Undoable until swept.
---

# Discard

/discard marks the current session not worth remembering. No agent is needed --
it is one touch, in this session's own worktree.

Run:

    touch "$MEMORY_DIR/.discard"

`$MEMORY_DIR` is this session's worktree, exported for shell commands. Then
tell the user: the session is marked -- consolidation will skip it, clean-up
will delete its branch and worktree once the session has ended, and the mark is
undoable by removing `$MEMORY_DIR/.discard` before the sweep.
