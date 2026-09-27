---
title: Goal
description: Why the context-wiki skill gets a first version, and what done looks like
---

# Goal

`skills/context-wiki/SKILL.md` is a draft with an empty description, so the
plugin ships a skill that installers skip and agents never load.

A context wiki is a git-tracked folder of interlinked markdown files that
gives AI agents context beyond a single project: the organization, its
customers, the domain, constraints, external systems. Without one, each
human explains that context to their agent over and over, and each member
of a team does it again.

The idea is small, and v1 should read that way. The skill explains it in
plain terms and states only the conventions a contributor needs.

## Success criteria

- `SKILL.md` has a description, and `npx skills add` picks the skill up.
- `SKILL.md` agrees with `docs/specs/context-wiki.md`.
- The top-level README, `docs/architecture.md` and `docs/glossary.md` no
  longer describe the skill as unwritten, and say nothing the spec
  contradicts.
