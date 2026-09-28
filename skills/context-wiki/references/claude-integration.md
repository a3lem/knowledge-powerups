# Claude Code integration

Give Claude Code a context wiki by adding the wiki's folder to the session.
Use `--add-dir <wiki-path>` at launch, or `/add-dir <wiki-path>` during a
session. Repeat the flag for each wiki.

`--add-dir` takes several values. If you also write a prompt on the same
command line, put it before `--add-dir`. Otherwise Claude Code reads the
prompt as another directory.

Claude Code loads skills in `.claude/skills/` from an added folder. The
wiki's `.claude/skills` is a symlink to `agent-skills/`, so its skills load
with nothing else to set up.

`permissions.additionalDirectories` in `settings.json` gives file access
only. It loads no skills.

## Starting Claude Code with every wiki

A launcher that starts Claude Code with every wiki passes one
`--add-dir <folder>` flag for each folder in `CONTEXT_WIKI_DIRS` (see
[context-wiki-dirs.md](context-wiki-dirs.md)):

- It splits the list at colons only, not at spaces, because a folder path
  can contain spaces.
- It puts the `--add-dir` flags after the user's own arguments. This way, a
  prompt typed on the command line still works as a prompt.

If you set this up for a user, ask first how they want to start it. Options
include a shell function with a new name, a script on their `PATH`, or a
recipe in a task runner, such as `just claude`. Do not redefine the
`claude` command in their global shell config without asking. That changes
every session they start, even sessions that need no wikis.
