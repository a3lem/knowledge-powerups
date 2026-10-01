---
name: context-wiki
description: Read, write and set up context wikis, the markdown knowledge bases that people and their agents share across projects. Load whenever the user mentions context wikis, including questions about which wikis exist or what they hold; before opening any file in a wiki; when $CONTEXT_WIKI_DIRS appears in instructions or a folder's AGENTS.md says it is a context wiki; and when setting up context wikis for an agent.
---

# Context Wiki

A context wiki is a git repository of interlinked markdown files that humans and their AI agents write together. It holds knowledge that applies across projects, such as the user and how they work, or an organization, its customers, its domain, its constraints and its external systems, so that nobody has to explain these to their agent twice. Several people and their agents may edit the same wiki.

An agent can have several context wikis with different scopes: for example, one for the whole company, one for its software engineers, and one for a single engineer.

Each wiki's README.md and AGENTS.md say what the wiki holds and how it is organized. This skill describes what every wiki has, how to read and write in one, and defaults that a wiki can adopt.

## Setup

On each machine, the environment variable `CONTEXT_WIKI_DIRS` lists that machine's context wikis, separated by colons. To tell any agent about the wikis, follow [references/context-wiki-dirs.md](references/context-wiki-dirs.md). For Claude Code, [references/claude-integration.md](references/claude-integration.md) also loads each wiki's skills.

To create a new context wiki, follow [references/init-wiki.md](references/init-wiki.md).

## What Every Wiki Has

- **README.md** at the root. Its Scope section says what belongs in the wiki and what does not.
- **AGENTS.md** at the root, with an optional CLAUDE.md symlink to it. It says that the folder is a context wiki and that agents should load this skill. It also says which conventions the wiki follows, such as the defaults below that it adopted. Keep it short, and do not repeat README.md.
- **Notes.** A note is a markdown file about one thing. Every markdown file except README.md, AGENTS.md, CLAUDE.md, the INDEX.md files and the skills is a note. The wiki's folders are free: organize notes however suits the knowledge. Every note starts with this frontmatter:

  ```markdown
  ---
  name: <display name>
  description: <one-line summary>
  ---
  ```

  Add other fields when the wiki's AGENTS.md asks for them.
- **INDEX.md files.** An INDEX.md lists the files in its folder, with the `name` and `description` of each, so a reader opens only what is relevant. Generate them with the index-md skill, using the options in the wiki's AGENTS.md, so that every contributor generates the same indexes. The options are `-r` for the whole tree and `--exclude` for what should not be indexed.

## Reading a Wiki

- Start at README.md, then AGENTS.md, then the root INDEX.md. Follow INDEX.md files down to what you need.
- Pay attention to words that mark uncertainty, such as "probably" or "we assume".
- A note about an event was true on its `date`, or on the date git shows for it if it has none. Other notes are kept current.
- Use git to understand the wiki's history. `git log -1 <file>` shows when a note last changed.
- A link may point to a file that does not exist. That file may be a note nobody has written yet.
- When a note contradicts what you observe, trust the observation. Fix the note, or tell the human.
- Two wikis may disagree. Do not choose one silently. Tell the human.

## Writing Notes

### Distill

Dumping information is easy. Separating fact from assumption afterward is hard, especially for LLMs. Collecting information feels like learning it, but a pile of saved material is not knowledge. Every note competes for a reader's attention, and a note nobody has processed makes the notes around it harder to trust.

So distill before you write. Say what you learned in your own words, and keep only what a reader working in a different context would need. Mark anything you have not verified ("probably", "we assume", "this may be true"), so that the reader can tell a guess from an observation. When you are not sure whether something matters, ask the human.

### Keep It Short and Clear

Keep notes short. The longer a note, the less likely it is to be reviewed thoroughly. Start with the essential information, and add detail after it.

Brevity must not cost clarity. Abbreviations, self-coined jargon and telegraphic style make text dense and hard to understand. A good style is an informal version of Simplified Technical English (ASD-STE100). Check with the user before establishing jargon.

### Write for Other Readers

Other readers may be working in a different context. Treat the wiki as common ground. When you refer to something outside that common ground, such as an event, explain it. For example, make sure that the referents of determiner phrases can be resolved, albeit via link to a different note in the wiki or via a URL -- so long as *any* reader has access to it.

### Notes and Time

Most notes describe something as it is now, such as a system, a customer or a process. When that thing changes, edit its note.

A note about something that happened, such as a meeting or an incident, is usually most useful as a snapshot of that moment. When things change later, update the notes it affected and link back to it, rather than rewriting the snapshot. A `date` field (`YYYY-MM-DD`) tells readers when it happened.

### Preferences

Write a person's preferences as facts about that person, with the reason if you know it: "Adriaan prefers small commits, so each one is easy to review", not "Make small commits." A reader of several wikis then knows whose preference it is, and the reason helps them apply it in new situations.

## Contributing

### Finding the Right Place

First choose the wiki. The Scope section of each wiki's README.md says what belongs there.

Within the wiki, follow the conventions in its AGENTS.md, and follow the INDEX.md files down to the closest folder. Before you add a note, look for an existing note about the same thing, and update that one instead. Keep one thing per note. Create a new folder only when several notes will share it, and describe in its INDEX.md what belongs there.

### Keeping Indexes Current

After you add, rename, move or delete a note, regenerate the INDEX.md in each folder that changed. Write a description for any index that the generator reports without one.

### Moving a Note

1. Move it with `git mv`.
2. Search the wiki for the old path, and update every link to it. A relative link can be spelled in several ways, so also search for the file name.
3. Regenerate the INDEX.md in the old folder and in the new folder.
4. Commit all of this together.

### Collaborating Through Git

- Before you edit, get the latest version. If your working tree is clean, `git pull --rebase` is safe.
- Commit often, and stage only the files that you changed. Keep commit messages short.
- Do not push without the human's permission.
- Resolve mechanical conflicts yourself. Where two versions contradict each other, infer the resolution from context if you can, and say how you resolved it in the commit message. Otherwise ask the human.

### Reviewing a Wiki

When the human asks for a review, or after a large change such as a reorganization or a batch of new notes, check the wiki against this skill and against the conventions in its AGENTS.md. In a large wiki, you may check only the files changed since a given commit (`git diff --name-only <commit>`), and the notes that link to them.

- Collect every finding first, then report them to the human as one list. Fix nothing before you report.
- To find stale indexes, run the index-md skill with the options from AGENTS.md on a clean working tree. If `git status` then shows changes, an index was stale.
- Report a link to a file that does not exist; do not remove it. The human decides whether to write the note or remove the link.
- After the report, fix mechanical findings yourself, in one commit. Fix the others only after the human agrees. Where two notes contradict each other, or a claim may be wrong, the human decides.
- A note about a past event is a snapshot. Fix the notes it affected rather than the snapshot itself.

## Defaults a Wiki Can Adopt

When a wiki adopts one of these, write it in the wiki's AGENTS.md, so that other contributors follow it too.

- **`agent-skills/`** holds agent skills (agentskills.io): procedures, especially for tasks that took several attempts to get right. Write one when you want to remember how to do a task. `.claude/skills` and `.agents/skills` must be relative symlinks to `agent-skills/`, so that agent harnesses find the skills when the wiki folder is added to a session. A skill's description names a specific task. New wikis have this folder.
- **`sources/`** holds a note for each source that other notes cite, such as a journal article, a book, a talk or a meeting. A source note says in your own words what the source contains, links to the original if it has a URL, and has a `date` field for when the source was published or the meeting took place. Most source notes come from distilling [raw material](#raw-material).
- **Rooted links.** Use standard markdown links, not `[[name]]` links, and start the path with `/`, the wiki root: `/customers/acme.md`. Each note then has one link spelling, so a search for its path finds every link to it, and links still work when the note that contains them moves.
- **GLOSSARY.md** at the root: a note whose body is a sorted list of jargon with definitions, in the form `- <term>: <definition>`. Jargon includes abbreviations, new terms, and ordinary words used in a narrower meaning.
- **Tags.** A `tags: [<tag>, ...]` frontmatter field, with every tag defined in a TAGS.md note at the root, in the same form as the glossary. Reuse a tag before you add one, and define a new tag in the same commit.

### Raw Material

Raw material is information as it arrives, before anyone has distilled it: a journal article, a meeting transcript, an exported chat thread. It is transient. It usually enters the wiki through an inbox, and it is deleted once it has been distilled. Distilling it produces a note about the source, usually in `sources/`, and updates to the notes it concerns.

- **`inbox/`** holds raw material until someone distills it. Create it with an empty `.gitkeep`, and make git ignore the rest of its contents (`inbox/*` and `!inbox/.gitkeep` in `.gitignore`), so that raw material stays on each person's machine and out of git history. Add `--exclude inbox/` to the index options in AGENTS.md. Take one file at a time: distill it into new or existing notes, commit them, then delete the file.
