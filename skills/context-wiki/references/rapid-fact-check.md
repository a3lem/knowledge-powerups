# Fact-checking a wiki with rapid Q&A

Use this guide when the human asks for a fact-checking round. You ask about
statements in the wiki, one at a time. The human answers in a few words. You
write the result into the wiki after each answer.

## Choose what to ask about

Ask in this order:

1. Statements with an annotation that names the human, such as
   `<!-- @ask: niels -->`.
2. Items in a list of unconfirmed facts, such as `facts-to-check.md` in an
   inbox. Ask first about items that conflict with a note, or that appear
   in more than one place. An item may belong in a different wiki than the
   one that holds it.
3. Random statements. Let a command pick a line, not you:
   `git grep -n . -- '*.md' ':!*INDEX.md' | sort -R | head -n 1`
   Ask about the statement on that line. If the line holds no statement,
   such as a heading, ask about the nearest one.

Before you ask about a statement, read the note that holds it, so that you
know what the wiki already says.

Tell the human how to answer: "yes", "no", a correction, "skip", "drop", or
the name of someone to ask.

## Ask

- Ask one question in each message. Name the claim, and give its source and
  its age when they help.
- Ask a closed question when the claim is specific. Ask an open question
  when you do not know the answer. A closed question that suggests a detail
  can make the human agree with a guess. Do not put a guess in a question.
- When the human asks you to explain, read the former text in git or the
  source, and quote it. Do not guess.
- When the human says that a topic is not theirs, stop asking about that
  topic. Skip the other items on it.

## Act after each answer

| Answer | Action |
|---|---|
| Confirmed, or a correction | Write the fact in the right note, in the words of the human. Delete the item from the list. |
| Confirmed in part | Write only the confirmed part. Keep the rest in the list, and write next to it what the human confirmed. |
| "Unsure", "skip" | Leave the item unchanged. |
| "Ask Niels" | Write the fact in the right note, marked as uncertain, and add `<!-- @ask: niels -->` after it. Delete the item from the list. |
| "Drop" | Delete only the part that the question covered. |
| "History" | Keep the item. Write next to it that it is history, and what source must supplement it. |
| Extra information | Write it too. Ask nothing more about it. |

- The human may say that the fact belongs in another wiki. Follow that.
- The human may state a rule, for example which folders to use as a source.
  Put the rule in the wiki's AGENTS.md.
- Add a line to the note's References: the name of the human, the date, and
  what they confirmed. This is the basis of the statement.
- When the human answers a statement that has an annotation, remove the
  annotation.
- Do not add details that the human did not give.
- When you add a note, add it to the INDEX.md of its folder.
- When a confirmed fact contradicts another note, update that note, or tell
  the human.

## Keep the pace

- After each answer, tell the human in one sentence what you changed. Then
  ask the next question.
- Do not read a file again when you only edited it.
- After many questions, give a short status: what changed, how many items
  remain, and what is uncommitted. Ask whether to continue or to commit.
- Commit only when the human asks. A raw-material inbox is not in git, so
  the list changes do not appear in the commit.
