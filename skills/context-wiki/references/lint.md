# Linting a context wiki

A lint is a check of the whole wiki against the conventions in SKILL.md. Run one
when the human asks for it, or after a large change such as a migration or
a batch of ingests.

Work through the checklist below. Some checks are mechanical: the answer is
yes or no. Others need judgment. Collect every finding first, then report
them to the human as one list, grouped by check. Fix nothing before you
report.

After the report:

- Fix mechanical findings yourself, in one commit, unless the human says
  otherwise.
- Fix judgment findings only after the human agrees. Where two entries
  contradict each other, or a claim may be wrong, the human decides.
- Never rewrite the content of a record to fix a finding. A record may be
  moved, and its frontmatter may be completed.

In a large wiki, you may lint only the files that changed since a given
commit (`git diff --name-only <commit>`). Also check the entries that link
to those files.

## Layout

- [ ] `.agents/skills` and `.claude/skills` are symlinks to
      `../agent-skills`.
- [ ] `CLAUDE.md` is a symlink to `AGENTS.md`.
- [ ] `.gitignore` contains the lines from the `.gitignore` section of
      SKILL.md.
- [ ] Git tracks nothing in `inbox/` except `.gitkeep`
      (`git ls-files inbox`).
- [ ] `README.md` exists and has a Scope section.
- [ ] `AGENTS.md` is short, and its instructions are about working in the
      wiki.

## Frontmatter

- [ ] Every entry has a `title` and a `description`.
- [ ] Each `description` is one line and says what the entry is about.
- [ ] Every tag used is defined in `TAGS.md`, and every tag defined there
      is used.
- [ ] Every type used is defined in `TYPES.md`, and every type defined
      there is used.
- [ ] Each `date` field has the form `YYYY-MM-DD` and holds the date of
      the source or the event, not the date the entry was written.

## Records and sources

- [ ] No record was changed after it was written, apart from moves and
      frontmatter. `git log --follow -p -- <file>` shows its history.
- [ ] A record whose event happened on a different day than the record was
      written has a `date` field.
- [ ] Every note under `sources/` is about a source, and has a `date` field
      when the source's date is known.
- [ ] Only source notes whose names would otherwise repeat, such as
      meetings, have a date in their file name.
- [ ] Each source note is cited by at least one entry. A source note that
      nothing cites may still be useful, but report it.

## Links

- [ ] All links are standard markdown links. There are no `[[...]]`
      links.
- [ ] Links to files that do not exist are reported, not removed. Such a
      link may point to an entry nobody has written yet. Ask the human
      whether to write the entry or remove the link.
- [ ] Entries that no other entry links to are reported. Links from
      INDEX.md files do not count, since every entry has one.

## Indexes

- [ ] Every folder with two or more children has an INDEX.md, except
      `agent-skills/`, `inbox/` and the folders inside them.
- [ ] Every INDEX.md is current. Run the index-md generator: if it changes
      anything, the index was stale.
- [ ] No INDEX.md entry carries a `<!-- to-do -->` placeholder.

## Content

These checks need judgment. Report what you find and why.

- [ ] Each entry is about one thing. Two entries about the same thing
      should be merged.
- [ ] No two entries contradict each other. Do not choose a side: report
      both entries.
- [ ] Descriptions are current. A description that a newer record or
      source note contradicts is probably stale.
- [ ] Guesses are marked as guesses ("probably", "we assume"). A claim
      stated as a hard fact with no source or evidence is reported.
- [ ] Preferences are written as facts about a person, with a reason, not
      as commands.
- [ ] Jargon is defined in `GLOSSARY.md`, including terms used in a
      narrower meaning than usual.
- [ ] Entries are short, and start with the essential information.
- [ ] Each entry fits the Scope section of the README. An entry that
      belongs in another wiki is reported.
- [ ] Each skill's description names a specific task.
