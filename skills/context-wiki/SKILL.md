---
name: context-wiki
description: 
---

# Context Wiki

Capture and refine knowledge in bundles of collaboratively edited, interlinked markdown files,
with the primary purpose of providing additional contextual information to AI agents.

Because of this purpose, they are denoted as 'context wikis'.

Context wikis are co-creative, maintained by both humans and AI agents. They are also multiplayer,
maintained by multiple humans and those humans' AI agents at once.

They are the ideal place for knowledge that generalizes across individual projects or code repositories. They provide an alternative to inefficient scenarios such as these:

1. A human explaining their working context over and over to the AI: e.g., organization, customers, domain, constraints, external systems, etc.
2. The previous point (1) multiplied by each human member of the same team.

An agent can have access to multiple context wikis, each with a different scope. A first wiki could be shared among all employees of a company. A second wiki could be meant only for the company's software engineers. And a third, final wiki could belong to an individual software engineer.

## Structure

### Folder tree

A context wiki is a local folder tree of interlinked markdown files. It is tracked by git, making distributed collaborative editing trivial. The directory structure is free: agents organize notes however makes sense for the knowledge being captured. For instance, subdirectories are permitted.

To link to a file, use standard markdown links (as opposed to `[[name]]` links, as used by e.g. Obsidian). Both absolute (relative to root `/` of context wiki repo) and relative link forms are accepted.

### File frontmatter

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
```

### Directory listings

Every (sub)directory in the context wiki must have an index.md (use /index-md) listing the files and subdirectories in that directory. This speeds up file discovery.

### README.md

Every context wiki should have a top-level README.md.

Recommended format:

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

## Guidelines for Contributors

Beware "collector's fallacy". Dumping information is easy. Separating fact from assumption afterward is hard. 





