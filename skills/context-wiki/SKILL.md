---
name: context-wiki
description: Interact with a 'context wiki' as a reader or contributor. Also load when $CONTEXT_WIKI_DIRS appears in instructions, when a folder's AGENTS.md says it is a context wiki, or when setting up context wikis for an agent.
---

# Context Wiki

Capture and refine knowledge in bundles of collaboratively edited, interlinked markdown files,
with the primary purpose of providing additional contextual information to LLM-based AI agents.

We denote these bundles of knowledge as 'context wikis'.

Context wikis are co-creative, maintained by both humans and AI agents. They are also multiplayer,
maintained by multiple humans and those humans' AI agents at once.

They are the ideal place for knowledge that generalizes across individual projects or code repositories. They provide an alternative to inefficient scenarios such as these:

1. A human explaining their working context over and over to the AI: e.g., organization, customers, domain, constraints, external systems, etc.
2. The previous point (1) multiplied by each human member of the same team.

An agent can have access to multiple context wikis, each with a different scope. A first wiki could be shared among all employees of a company. A second wiki could be meant only for the company's software engineers. And a third, final wiki could belong to an individual software engineer.

## Setup

On each machine, the environment variable `CONTEXT_WIKI_DIRS` lists that machine's context wikis, separated by colons. To tell any agent about the wikis, follow [references/context-wiki-dirs.md](references/context-wiki-dirs.md). For Claude Code, [references/claude-integration.md](references/claude-integration.md) also loads each wiki's skills, rules and AGENTS.md.

To create a new context wiki, follow [references/init-wiki.md](references/init-wiki.md).

## Structure

### File tree

A context wiki is a local folder tree of interlinked markdown files.  It is
tracked by git, making distributed collaborative editing trivial. The wiki root
is the root of the git repo. The directory structure is free: agents organize
notes however makes sense for the knowledge being captured. For instance,
subdirectories are permitted.

To link to a file, use standard markdown links (as opposed to `[[name]]` links, as used by e.g. Obsidian). Both absolute (relative to root `/` of context wiki repo) and relative link forms are accepted.

### Reserved folder: $ROOT/skills/

`$ROOT/skills/` contains agent skills (agentskills.io). Whereas context wikis serve mostly as a kind of 'semantic' memory (capturing distilled, reusable knowledge), this particular directory offers 'procedural' knowledge -- how to perform tasks, especially tasks the agent needed several attempts to figure out. `$ROOT/skills/` must always be symlinked to from `$ROOT/.{agents,claude}/skills`, so that when the context wiki path is registered with the agent session (e.g. as with Claude Code CLI's `--add-dir` option), the skills are discoverable by the agent harness. 

### Reserved folder: $ROOT/rules/

`$ROOT/rules/` holds rules. A rule is a short instruction that an agent must follow in every session, whatever the task.

`$ROOT/.claude/rules` must be a symlink to `$ROOT/rules/`. This lets Claude Code load the rules when the wiki is added to a session. It works only when an environment variable is set. See [references/claude-integration.md](references/claude-integration.md).

Rules load into every session of everyone who uses the wiki, so keep them few and short. Most knowledge belongs in entries instead. An agent reads an entry only when it is relevant. A rule is for something that must hold every time. Give each rule a reason.

### Wiki Entries

Each entry is a markdown (.md) file about one thing.

Most entries are descriptions. A description is about something that stays true for a while. Examples: a system, a customer, a person and their working style, a team, a process, a term, or a recurring problem and its fix. Keep descriptions current. When something changes, edit the description.

Write a person's preferences as facts about that person, with the reason: "Adriaan prefers small commits, so each one is easy to review", not "Make small commits." A reader of several wikis then knows whose preference it is. The reason helps them use it in new situations.

Some entries are records. A record is about something that happened, such as a meeting, an experiment, or an incident. Do not update a record later. Git history shows when it was written. If the event happened on a different day, write that date in the text.

If a record teaches something lasting, write that in a description and link to the record.

The special files below and the files under `skills/` are not entries.

Every entry in the wiki **must** have these YAML frontmatter fields. The INDEX.md files are generated from these fields. Exceptions: INDEX, SKILL.md, and all 'special' files below.

```markdown
---
title: <display name>
description: <one-line summary>
---
```

These additional fields are optional:

```yaml
tags: [<tag>, <tag>, ...]
type: <type-name>
```

### Special Files

All special files are in the wiki's root, except INDEX.md.

#### INDEX.md -- directory listings

Every (sub)directory with two or more children has an INDEX.md. Generated with the /index-md skill, an INDEX.md gives an overview of its sibling files. LLMs should read INDEX.md first to orient themselves.

#### README.md

Every context wiki should have a top-level README.md.

Suggested format (all sections are optional):

```
# [Wiki Name]

[Intro sentence]

## Scope

[What belongs here, what doesn't]

## Tips for Readers

[Help your audience]

## Rules for Contributors

[Guard against noise]
```

#### AGENTS.md

Every context wiki has a top-level AGENTS.md. `$ROOT/CLAUDE.md` is a symlink to it.

Agents read it when they work inside the wiki. Claude Code also loads it when the wiki is added to a session. See [references/claude-integration.md](references/claude-integration.md).

Keep it short. It should say:

- the folder is a context wiki
- agents should load the context-wiki skill
- README.md is the place to start

Do not repeat what README.md says.

#### TAGS.md

A sorted definition list of tags used in the wiki. Format:

```plain
# Tags

- <tag>: <definition>
- ...
```

#### TYPES.md

If the wiki uses the `type` frontmatter field, a sorted definition list of types. Similar format to TAGS.md.

#### GLOSSARY.md

A sorted glossary of jargon used across the wiki, formatted similarly to TAGS.md and TYPES.md. Beside abbreviations and novel terms, jargon also counts as terms used in a more specific meaning in the current domain context.

## Tips for Readers

- Start at the README.md, then scan INDEX.md files.
- Pay attention to linguistic markers of uncertainty.
- Read a record as true on the date that git shows for it. A description is kept current.
- Use git to understand the wiki's history. `git log -1 <file>` shows when an entry last changed.
- A link may point to a file that does not exist. That file may be an entry nobody has written yet.
- When an entry contradicts what you observe, trust the observation. Fix the entry, or tell the human.
- Two wikis may disagree. Do not choose one silently. Tell the human.

## Rules for AI Contributors

### Writing

Dumping information is easy. Separating fact from assumption afterward is hard, especially for LLMs. The "collector's fallacy" teaches us that collecting information feels like learning it, but a pile of saved material is not knowledge. Every entry in the wiki competes for a reader's attention, and an entry nobody has processed makes the entries around it harder to trust. So distill before you write: say what you learned in your own words, keep only what a reader working in a different context would need, and mark anything you have not verified ("probably", "we assume", "there are indications that", "this may be true") so the reader can tell a guess from an observation, and especially from a hard fact. A human operator is always available to provide clarity about what information is or isn't important. Before you write a claim as a hard fact, check it with the human.

Keep entries short on average. The longer a wiki entry, the less likely it is to be reviewed thoroughly. Always start with essential information, adding detail later if space permits. Brevity should not come at the cost of clarity, however. Abbreviations, self-coined jargon, and telegraphic writing style, for example, increase lexical density and hinder proper understanding. A helpful writing style is an informal version of Simplified Technical English (ASD-STE100). 

Understand that other readers may be working in a different context. Treat the context wiki as a shared common ground. Be careful with referring to information, e.g. events, that doesn't belong to this common ground, unless you contextualize it. You can try using a light subagent to test the 'self-evidence' of a bit of information before committing it to the wiki.

### Organizing Information

#### Finding the right place

First choose the wiki. The Scope section of each wiki's README.md says what belongs there.

Within the wiki, follow the INDEX.md files down to the closest folder. Before you add an entry, look for an existing entry about the same thing, and update that one instead. Keep one thing per entry. Create a new folder only when several entries will share it.

#### Tags, types and jargon

Reuse an existing tag or type before you add a new one. When you add a new tag, type or term, define it in TAGS.md, TYPES.md or GLOSSARY.md in the same commit.

#### Moving an entry

Prefer links that start with `/`. Each target then has one link spelling, so a search for its path finds every link to it. Such links also keep working when the file that contains them moves.

To move an entry:

1. Move it with `git mv`.
2. Search the wiki for the old path, and update every link to it. A relative link can be spelled in several ways, so also search for the file name.
3. Regenerate INDEX.md in the old folder and in the new folder.
4. Commit all of this together.

### Collaborating through Git

Commit frequently, staging only files that you have changed. However, do not push to the remote without permission from the user. Keep commit messages short.

Before you make changes, check for updates on the remote. Fetch again regularly after that. Ask the user for permission before you update the local version with a rebase. Most conflicts come from editing an old copy.

Conflicts are inevitable. Resolve mechanical conflicts independently. Where information contradicts, try to infer resolution from context. If contradictions cannot be resolved, consult the human for help. Contradiction resolution should be mentioned in commit messages.




