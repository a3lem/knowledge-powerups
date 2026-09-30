---
name: context-wiki
description: Interact with a 'context wiki' as a reader or contributor to build up a reusable knowledge base. Also load when $CONTEXT_WIKI_DIRS appears in instructions, when a folder's AGENTS.md says it is a context wiki, or when setting up context wikis for an agent.
---

# Context Wiki

A context wiki is a git repository of interlinked markdown files that humans and their AI agents write together. It holds knowledge that applies across projects, such as an organization, its customers, its domain, its constraints and its external systems, so that nobody has to explain these to their agent again. Several people and their agents may edit the same wiki.

An agent can have several context wikis with different scopes: for example, one for the whole company, one for its software engineers, and one for a single engineer.

## Setup

On each machine, the environment variable `CONTEXT_WIKI_DIRS` lists that machine's context wikis, separated by colons. To tell any agent about the wikis, follow [references/context-wiki-dirs.md](references/context-wiki-dirs.md). For Claude Code, [references/claude-integration.md](references/claude-integration.md) also loads each wiki's skills.

To create a new context wiki, follow [references/init-wiki.md](references/init-wiki.md).

## Structure

A context wiki is a local folder tree of interlinked markdown files. It is tracked by git, making distributed collaborative editing trivial. The wiki root is the root of the git repo.

### Entries

Each entry (also called a 'note') is a markdown file (.md) about one thing.

Most entries are descriptions. A description is about something that stays true for a while. Examples: a system, a customer, a person and their working style, a team, a process, a term, or a recurring problem and its fix. Keep descriptions current. When something changes, edit the description.

Write a person's preferences as facts about that person, with the reason: "Adriaan prefers small commits, so each one is easy to review", not "Make small commits." A reader of several wikis then knows whose preference it is. The reason helps them use it in new situations.

Some entries are records. A record is about something that happened, such as a meeting, an experiment, or an incident. Do not update a record later. Git history shows when it was written. If the event happened on a different day, put that date in the `date` field.

If a record teaches something lasting, write that in a description and link to the record.

Special files are not entries.

Every entry **must** have these YAML frontmatter fields. The INDEX.md files are generated from these fields.

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
date: <YYYY-MM-DD>
```

Set `date` to when the source was published or the event took place, not to when the entry was written.

### Links

To link to a file, use standard markdown links (as opposed to `[[name]]` links, as used by e.g. Obsidian). Both absolute (relative to root `/` of context wiki repo) and relative link forms are accepted.

### Folders

The directory structure is free: agents organize entries however makes sense for the knowledge being captured, in the root and in subdirectories. The folders below have a fixed meaning. Do not use their names for anything else.

#### Conventional Paths

Some kinds of entries have a fixed place:

- `sources/` holds notes on sources that other entries can cite, such as an article, a book, a talk or a meeting. A source note says what the source contains, in your own words, and links to the original if it has a URL. Most source notes come from the inbox (see [Ingesting from the Inbox](#ingesting-from-the-inbox)), but you can also write one directly.

  Organize `sources/` in subfolders by kind, e.g. `sources/literature/` and `sources/meetings/`. Name a source note after its source, e.g. `sources/literature/karpathy-llm-wiki.md`. Add the date in front of the name only when names would otherwise repeat, as with meetings: `sources/meetings/2026-09-20-acme-kickoff.md`.

#### Reserved Folders

These folders hold files that are not entries. Do not put entries in them.

- `inbox/` holds raw material waiting to be ingested: a clipped article, a meeting transcript, an exported chat thread. Git ignores everything in it except `.gitkeep`, so each person has their own inbox, and raw material stays on their machine. Ingestion empties it; see [Ingesting from the Inbox](#ingesting-from-the-inbox).
- `agent-skills/` contains agent skills (agentskills.io). Whereas context wikis serve mostly as a kind of 'semantic' memory (capturing distilled, reusable knowledge), this particular directory offers 'procedural' knowledge -- how to perform tasks, especially tasks the agent needed several attempts to figure out. `.agents/skills` and `.claude/skills` must be symlinks to `agent-skills/`, so that when the context wiki path is registered with the agent session (e.g. as with Claude Code CLI's `--add-dir` option), the skills are discoverable by the agent harness.

  A skill's description must name a specific task.

### Special Files

All special files are in the wiki's root, except INDEX.md.

#### INDEX.md -- Directory Listings

Every (sub)directory with two or more children has an INDEX.md, except `agent-skills/`, `inbox/` and the folders inside them. Generated with the /index-md skill, an INDEX.md gives an overview of its sibling files. LLMs should read INDEX.md first to orient themselves.

#### README.md

Every context wiki has a top-level README.md. Its Scope section says what belongs in the wiki and what does not. Contributors read it to choose a wiki.

#### AGENTS.md

Every context wiki has a top-level AGENTS.md, and a top-level CLAUDE.md that is a symlink to it.

Agents read it when they work inside the wiki.

It should include:

- the folder is a context wiki
- agents should load the context-wiki skill

It may also give instructions about working in this wiki, such as how it organizes its entries. It can also serve as a more general 'memory' for AI agents.

Do not repeat what README.md already says.

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
- Read a record as true on its `date`, or on the date that git shows for it if it has none. A description is kept current.
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

#### Finding the Right Place

First choose the wiki. The Scope section of each wiki's README.md says what belongs there.

Within the wiki, follow the INDEX.md files down to the closest folder. Before you add an entry, look for an existing entry about the same thing, and update that one instead. Keep one thing per entry. Create a new folder only when several entries will share it.

#### Ingesting from the Inbox

Take one file from `inbox/` at a time:

1. Read it, and discuss with the human what matters in it.
2. Write a source note under `sources/` in your own words. Keep only what a reader of this wiki needs. Link to the original if it has a URL.
3. Update the entries that the source changes, and link each one to the source note.
4. Commit, then delete the file from `inbox/`. Git ignores the inbox, so the deletion needs no commit.

If nothing in the file is worth keeping, delete it without writing a source note.

#### Tags, Types and Jargon

Reuse an existing tag or type before you add a new one. When you add a new tag, type or term, define it in TAGS.md, TYPES.md or GLOSSARY.md in the same commit.

#### Moving an Entry

Prefer links that start with `/`. Each target then has one link spelling, so a search for its path finds every link to it. Such links also keep working when the file that contains them moves.

To move an entry:

1. Move it with `git mv`.
2. Search the wiki for the old path, and update every link to it. A relative link can be spelled in several ways, so also search for the file name.
3. Regenerate INDEX.md in the old folder and in the new folder.
4. Commit all of this together.

### Linting

To check a wiki's health, follow the checklist in [references/lint.md](references/lint.md).

### Collaborating through Git

Commit frequently, staging only files that you have changed. However, do not push to the remote without permission from the user. Keep commit messages short.

Before you make changes, check for updates on the remote. Fetch again regularly after that. Ask the user for permission before you update the local version with a rebase. Most conflicts come from editing an old copy.

Conflicts are inevitable. Resolve mechanical conflicts independently. Where information contradicts, try to infer resolution from context. If contradictions cannot be resolved, consult the human for help. Contradiction resolution should be mentioned in commit messages.




