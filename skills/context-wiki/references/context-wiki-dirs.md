# Telling an agent where the wikis are

Each person clones context wikis to a folder of their own choice. A path
written into a shared file would be wrong on most machines. Keep the paths
in an environment variable instead. Each machine gets its own list.

`CONTEXT_WIKI_DIRS` lists this machine's context-wiki folders, separated by
colons. The order does not matter.

```sh
export CONTEXT_WIKI_DIRS="$HOME/wikis/acme-wiki:$HOME/wikis/acme-eng-wiki"    # bash, zsh
set -gx CONTEXT_WIKI_DIRS "$HOME/wikis/acme-wiki:$HOME/wikis/acme-eng-wiki"    # fish
```

Then tell the agent about the variable in its user-level instructions, for
example `~/.claude/CLAUDE.md` for Claude Code:

```markdown
Context wikis may exist in the folders named in `$CONTEXT_WIKI_DIRS` (a
colon-separated list). Read the variable when you need context beyond this
project. Load the context-wiki skill, then start at each wiki's README.md.
```

This works with any agent that can run a shell command. The agent can read
the wikis' files, but a wiki's skills, rules and AGENTS.md do not load on
their own. For Claude Code, [claude-integration.md](claude-integration.md)
loads them too.
