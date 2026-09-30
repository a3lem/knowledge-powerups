# Linting a context wiki

A lint checks a wiki against what every wiki has, against the conventions its
own AGENTS.md lists, and against the writing guidance in SKILL.md. Run one
when the human asks for it, or after a large change such as a reorganization
or a batch of new notes.

Work through the checklist below. Some checks are mechanical: the answer is
yes or no. Others need judgment. Collect every finding first, then report
them to the human as one list, grouped by check. Fix nothing before you
report.

After the report:

- Fix mechanical findings yourself, in one commit, unless the human says
  otherwise.
- Fix judgment findings only after the human agrees. Where two notes
  contradict each other, or a claim may be wrong, the human decides.
- Never rewrite the content of a record to fix a finding. A record may be
  moved, and its frontmatter may be completed.

In a large wiki, you may lint only the files that changed since a given
commit (`git diff --name-only <commit>`). Also check the notes that link to
those files.

## What Every Wiki Has

- [ ] `README.md` exists and has a Scope section.
- [ ] `AGENTS.md` exists, and `CLAUDE.md` is a symlink to it.
- [ ] `AGENTS.md` is short, and says which conventions the wiki follows.
- [ ] Every note has a `name` and a `description`.
- [ ] Each `description` is one line and says what the note is about.
- [ ] Every `INDEX.md` is current. Run the index generator with the wiki's
      `--exclude` patterns: if it changes anything, an index was stale.
- [ ] No `INDEX.md` entry carries a `<!-- to-do -->` placeholder.

## The Wiki's Own Conventions

- [ ] Each convention listed in `AGENTS.md` holds. For example: if the wiki
      keeps skills in `agent-skills/`, `.claude/skills` and `.agents/skills`
      are relative symlinks to it; if it has an `inbox/`, git tracks
      nothing in it except `.gitkeep` (`git ls-files inbox`); if it uses
      tags, every tag is defined in `TAGS.md`.
- [ ] The wiki follows no convention that `AGENTS.md` does not list. Report
      one you find, so that the human can add it to `AGENTS.md` or drop it.

## Links

- [ ] Links to files that do not exist are reported, not removed. Such a
      link may point to a note nobody has written yet. Ask the human
      whether to write the note or remove the link.

## Writing

These checks need judgment. Report what you find and why.

- [ ] Each note is about one thing. Two notes about the same thing should
      be merged.
- [ ] No two notes contradict each other. Do not choose a side: report
      both notes.
- [ ] Descriptions are current. A description that a newer record
      contradicts is probably stale.
- [ ] Guesses are marked as guesses ("probably", "we assume"). A claim
      stated as a hard fact with no source or evidence is reported.
- [ ] Preferences are written as facts about a person, with a reason, not
      as commands.
- [ ] Notes are short, and start with the essential information.
- [ ] Each note fits the Scope section of the README. A note that belongs
      in another wiki is reported.
- [ ] Each skill's description names a specific task.
