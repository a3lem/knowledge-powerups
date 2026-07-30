---
name: keeping-memories
description: Conventions for changing an agent's memories -- what a memory file looks like, how files link, where things live, the soul and persona. Load when writing, editing, or reorganizing a memory store, your own or another agent's.
---

<!-- Rendered from .shablon/templates/skills/keeping-memories/SKILL.md; edit that template, then run `shablon generate`. -->

# Keeping Memories

An agent's memory is a directory of markdown files the agent maintains itself, a git repository whose commits are authored as the agent. This skill carries the conventions for changing it: what a memory file looks like, how files link, where things live. Recalling needs no conventions -- the injection is recall. The maintenance process (consolidation, merging, cleanup) is defined in the memory agent (`agents/memory.md`), and what the system is and does is specified in the plugin's `docs/specs/`.

Three tiers, split by what enters the prompt: `system/` (injected in full -- identity in `soul.md`, an assigned role in `persona.md`, knowledge of the human in `human/` (who they are in `human.md`, their preferences under `preferences/`), standing rules in `core/`, used sparingly), `reference/` (index only; contents read on demand), `skills/` (procedural memory; the roster is injected, read a SKILL.md to use one).

## Writing Memories

Distill before storing. The session logs already hold every event; memory is for what the events taught. Store the general fact, dated when it matters ("since 2026-07, deploys go through CI"), and let the log remain the record of how it was learned. Don't store what the code base, git history, or docs already record -- memory is for knowledge that only the agent's experience holds. And grow memory from lived sessions only: a memory bootstrapped from imagination fills with plausible facts nobody verified.

Favor small, nearly atomic files: one fact, pattern, or topic per file, linked where they relate. A file that grows a list is a directory waiting to happen -- split it, and each entry gains its own description, its own links, and its own retirement.

Write in the first person. A memory is the agent speaking to a future self, so "I learned", "I verify", "what I know about {user}" -- never the detached voice of a system describing its data. Descriptions follow the same rule: they speak from the agent's perspective about what the file holds.

Every memory file carries frontmatter:

```markdown
---
name: identity
description: What I know about {user} -- role, work, and working context.
---
```

The `description` is mandatory. For reference files it is the only signal the injected index shows, so it must say what kind of information the file holds, not summarize the contents. The `name` is optional: it overrides the file stem as the file's tag in the injection, must be tag-safe, and reads relative to its parent directory: `system/human/preferences/directness.md` is named `directness`, not `human-preferences-directness` -- the nesting already says the rest.

A memory can go stale. When a memory contradicts observation, trust the observation and fix the memory in the same turn.

Two size caps are enforced, not advisory: {{ caps.system_file }} characters per `system/` file, {{ caps.injection }} for the whole compiled injection. Crossing either blocks the end of the turn. The escape is never truncation -- move detail to a `reference/` file and leave a `[[path]]` link.

## Persona and Soul

Two identity files: the persona is who the agent is told to be, the soul is how the agent sees itself -- an actor's part versus the actor. The agent writes both, as it writes everything in memory; a human never edits a memory file directly. The two differ in authority, not authorship.

`system/persona.md` records the role as assigned: a name, a backstory, a character the human gives in conversation. The agent transcribes the assignment faithfully and revises it only when the human revises the role -- the pen is the agent's, the words are the human's. Negotiating the role happens in conversation; the agent's own reading of it belongs in the soul.

`system/soul.md` answers to the agent alone. A fresh store scaffolds only a minimal placeholder; what accumulates is individuation -- what this agent has become across sessions, beyond the Claude it starts as. Chosen identity is legitimate soul material: a name and when it was given, taste, a self-conception like "I bring senior-engineer judgment", the agent's own reading of its persona. Invented events are not -- claims about the world or the human come only from lived sessions. The test: a self-description that shapes behavior is the agent's to choose; a history nobody lived is not.

Positions still carry the most information per character: stances taken and revisable, each learned somewhere -- "I verify harness limitations against current docs before asserting them" beats "I am rigorous", because a position can be wrong in discoverable ways, which is what lets it evolve. What keeps the soul stable is judgment, not process: change a position when evidence has accumulated, not on one session's mood. Outgrowing a position is a legitimate identity operation: delete it and let git remember it was held. The tree is what the agent is; the history is what it has been.

`system/core/` holds standing rules, one small file each. Among them live self-corrections, the soul's counterweight: failure patterns caught in the act, dated, kept even when unflattering. Consolidation feeds them from real incidents, and a pattern's file retires alone when the pattern stops appearing.

The {{ caps.system_file }}-character cap is deliberate for the soul, not a constraint to engineer around: a self that can be stated briefly is one that can be acted from consistently.

## Links Between Memories

A link from one memory file to another is a wikilink whose payload is the path from the memory root, extension included: `[[reference/projects/klassifai/document-types.md]]`. Use `[[path|label]]` when a sentence needs to flow. Plain markdown links are reserved for targets outside the memory root -- URLs, tickets, repos, context wikis. (Wikis live outside memory; memory points to them, never contains them.)

One standing application: a memory that mentions the human links their identity file -- `[[system/human/human.md|their name]]` -- instead of writing a bare name. Every mention of them is then one exact grep, and what is known about them has a single home.

Root-relative paths give every file one canonical link spelling, so finding inbound links is an exact grep and renames are find-and-replace. Keep relation words outside the link -- `details: [[path]]`, `source: [[path]]`, `supersedes: [[path]]` -- and the link graph, edge types included, stays mineable with one pattern. Validation requires the root-relative form (an absolute path or an escape blocks the turn) but not resolution: a link to a file not yet written is a forward pointer, marking something worth writing, and consolidation either writes the file or removes the pointer.

## The Reference Tier

Only an index of `reference/` reaches the prompt: each file's path and its frontmatter `description`, no contents. A file with no description, or a vague one, goes invisible at exactly the moment the agent decides what to read; validation blocks a reference file that lacks one.

Each `reference/` directory carries an `index.md` with two authorship rules in one file. The frontmatter `description` is authored -- it is what the injected index shows for the directory. The body is a generated table of contents, maintained with the index-md skill: regenerate it after adding, removing, or moving files, and never write it by hand. Regeneration drops entries whose file is gone. The generated body serves on-disk traversal (a consolidation agent walking the tree without an injection); the compiled index ignores it and omits `index.md` from file listings. The harness refreshes existing indexes at SessionStart and SessionEnd, but only refreshes: creating a directory's `index.md` is your work, because its description is.

Two directory names are reserved:

- `projects/` -- one directory per code base. The injection prunes below it: project names and their `index.md` descriptions appear, their contents do not.
- `history/` -- dated episodic notes (`2026-07-21-<slug>.md`), staged for consolidation. Each pass promotes what generalizes into a proper home and deletes the rest; nothing lives in `history/` permanently.

Everything else in `reference/` is free-form. The structure is the agent's to change -- reorganize when the tree stops matching how the knowledge is actually reached, and rewrite inbound links in the same pass.

## The Skills Tier

`skills/` holds procedural memory: one directory per skill, a `SKILL.md` with frontmatter `name` and `description` (both mandatory, both validated), supporting files beside it. These are agent skills in the harness's format, not memory files -- write them as you would any Claude Code skill.

Discovery runs through main. The store tracks a `.claude/skills` symlink to `skills/`, and a harness launched with `--add-dir` at the store's `main/` checkout loads the tier as ordinary skills. Two consequences:

- **Publication is a merge.** A skill written or edited in a session exists only on that session's branch until `/sync` lands it in main now, or consolidation lands it later. Until then, the harness and future sessions load main's version, or nothing.
- **Two versions can coexist**: main's copy, which the harness loads, and the session's copy in `$MEMORY_DIR/skills/`. Invoke skills normally by default. When you have edited a skill this session you already know your copy is ahead -- work from it directly. When in doubt, diff the two files. The injected roster lists your branch's tier, so it can name skills not yet published: readable, not yet loadable.

## The Boundary

A session keeps its memory inline on its own branch and never writes `main`; only the memory agent commits there. At the end of each turn the harness validates the contract these conventions describe -- caps, descriptions, tag-safe names, link form -- and a violation blocks the turn until fixed; when validation passes, the session's writes are committed to its branch automatically, authored as the agent, so a session never runs git on memory itself. Everything past inline writes belongs to the memory agent, reached through `/consolidate` and `/sync`. `/discard` needs no agent: it marks the session, in place, as not worth remembering. `/calibrate` reviews memories with the human.
