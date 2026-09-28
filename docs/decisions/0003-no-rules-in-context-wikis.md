---
title: No rules in context wikis
description: Why a context wiki carries no always-loaded agent rules, and conventions ship as plugins instead
---

# No rules in context wikis

A context wiki has no `rules/` folder and no `.claude/rules` symlink.
Adding a wiki to a session makes knowledge and task-specific skills
available; it must not change how the agent behaves across the board.
Decided on 2026-09-28.

Rules in a wiki caused three problems:

- **Surprise.** Someone adds a wiki for its knowledge and their agent
  starts acting differently.
- **Uneven loading.** Claude Code loads rules from an added directory only
  when `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` is set, so two
  people with the same wiki could get different behavior without knowing
  it.
- **Stacking.** Rules from a company wiki and a team wiki load together,
  and a conflict between them goes unnoticed.

The legitimate use -- a dev team sharing Python conventions -- is better
served by a plugin. A repository enables the plugin in its committed
`.claude/settings.json`, so the conventions apply to that codebase and
nowhere else, and enabling it is a visible choice. Plugin releases also
match the pace at which a team changes conventions: rarely and on purpose.
The wiki can still hold an entry explaining the conventions and why the
team chose them, linking to the plugin rather than copying its rules.

Skills stay. A skill acts only when a task matches its description, and the
skill listing shows which skills exist. Wiki skills are procedures an agent
writes down after it needed several tries, captured as work happens, and
making each one a plugin release would mean most never get written. A skill
whose description applies to every task is a rule and does not belong.

`AGENTS.md` stays too. It mainly describes the wiki, and any instructions
in it concern the wiki itself. Without rules, the launcher no longer needs
`CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD`; `AGENTS.md` then loads when
an agent works inside the wiki, which was always its main job.
