---
name: context-wiki
description: Interact with a 'context wiki' as a reader or contributor. 
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

## Structure

### Folder layout

A context wiki is a local folder tree of interlinked markdown files. It is tracked by git, making distributed collaborative editing trivial. The directory structure is free: agents organize notes however makes sense for the knowledge being captured. For instance, subdirectories are permitted.

To link to a file, use standard markdown links (as opposed to `[[name]]` links, as used by e.g. Obsidian). Both absolute (relative to root `/` of context wiki repo) and relative link forms are accepted.

### Reserved folder: $ROOT/skills/

`$ROOT/skills/` contains agent skills (agentskills.io). Whereas context wikis serve mostly as a kind of 'semantic' memory (capturing distilled, reusable knowledge), this particular directory offers 'procedural' knowledge -- how to perform tasks, especially tasks the agent needed several attempts to figure out. `$ROOT/skills/` must always be symlinked to `$ROOT/.{agents,claude}/skills`, so that when the context wiki path is registered with the agent session (e.g. as with Claude Code CLI's `--add-dir` option), the skills are discoverable by the agent harness. 

### Wiki Entries

Each entry in the wiki is markdown (.md) file. It can 

Every note file in the wiki **must** have these YAML frontmatter fields:

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

A sorted glossary of jargon used across the wiki. Beside abbrevations and novel terms, jargon also counts as terms used in a more specific meaning in the current domain context.

## Tips for Readers

- Start at the README.md, then scan INDEX.md files.
- Pay attention to linguistic markers of uncertainty.
- Use git to understand the wiki's history.

## Rules for AI Contributors

Dumping information is easy. Separating fact from assumption afterward is hard, especially for LLMs. The "collector's fallacy" teaches us that collecting information feels like learning it, but a pile of saved material is not knowledge. Every note in the wiki competes for a reader's attention, and a note nobody has processed makes the notes around it harder to trust. So distill before you write: say what you learned in your own words, keep only what a reader working in a different context would need, and mark anything you have not verified ("probably", "we assume", "there are indications that", "this may be true") so the reader can tell a guess from an observation, and especially from a hard fact. A human operator is always available to provide clarity about what information is or isn't important. You are recommended to engage in Q&A with the human before persisting hard claims.

Keep entries short on average. The longer a wiki entry, the less likely it is to be reviewed thoroughly. Always start with essential information, adding detail later if space permits. Brevity should not come at the cost of clarity, however. Abbreviations, self-coined jargon, and telegraphic writing style, for example, increase lexical density and hinder proper understanding. A helpful writing style is an informal version of Simplified Technical English (ASD-STE100). 

Understand that other readers may be working in a different context. Treat the context wiki as a shared common ground. Be careful with referring to information, e.g. events, that doesn't belong to this common ground, unless you contextualize it. You can try using a light subagent to test the 'self-evidence' of a bit of information before comitting it to the wiki.

