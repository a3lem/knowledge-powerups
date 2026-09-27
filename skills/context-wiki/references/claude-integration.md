# Claude Code integration

Give Claude Code a context wiki by adding the wiki's folder to the session.
Use `--add-dir <wiki-path>` at launch, or `/add-dir <wiki-path>` during a
session. Repeat the flag for each wiki.

`--add-dir` takes several values. If you also write a prompt on the same
command line, put it before `--add-dir`. Otherwise Claude Code reads the
prompt as another directory.

What Claude Code loads from an added folder:

- Skills in `.claude/skills/` load by default. The wiki only needs a
  `.claude/skills` symlink to `skills/`.
- `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/*.md` and
  `CLAUDE.local.md` load only when the environment variable
  `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` is `1`. Without it, Claude
  Code ignores these files and does not say so. The wiki's `AGENTS.md` and
  rules reach the session only through these files.

`permissions.additionalDirectories` in `settings.json` gives file access
only. It loads no skills, rules or `CLAUDE.md`.

## Starting Claude Code with every wiki

A launcher that starts Claude Code with every wiki does three things:

- It passes one `--add-dir <folder>` flag for each folder in
  `CONTEXT_WIKI_DIRS` (see [context-wiki-dirs.md](context-wiki-dirs.md)).
  It splits the list at colons only, not at spaces, because a folder path
  can contain spaces.
- It sets `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`.
- It puts the `--add-dir` flags after the user's own arguments. This way, a
  prompt typed on the command line still works as a prompt.

If you set this up for a user, ask first how they want to start it. Options
include a shell function with a new name, a script on their `PATH`, or a
recipe in a task runner, such as `just claude`. Do not redefine the
`claude` command in their global shell config without asking. That changes
every session they start, even sessions that need no wikis.
