---
name: using-docs
description: A standard layout for the docs/ directory of a code base, where a file's path tells you its role (spec, ADR, how-to, work item) and its authority (whether it can be built on without re-verifying against the code). Use when creating, moving, or organizing documentation, when deciding where a new document belongs, or when judging whether an existing doc is trustworthy.
---

# Using docs/

Always use the standard layout for `docs/` below, so that a file's role and authority can be inferred from its path in the file tree.

- **'role'**: the kind of document -- e.g. a spec, ADR, how-to, work item, etc. The path determines the role.
- **'authority'**: Whether you can build on the file's content without re-verifying it against the code. Everything in docs/ outside docs/dev/ carries high authority.

## The journey and the present

`dev/` holds the journey: the work in flight, and the record of work already done. Everything in `docs/` outside `dev/` describes the present state of the world.

Files outside `dev/` are reference material and may be built on without re-verification. Human and agent both take pains to keep them current: drift between docs and code is a bug and gets corrected, stale files are removed, and 'less is more' thinking is applied to avoid churn. A reference file that has stopped being true is wrong. Delete it; git keeps the copy. Before deleting, promote whatever outlives it -- the reason a thing went away is usually an ADR.

`dev/` makes no authority promise. It is the workspace for doing the work, e.g. decomposing a complex plan into multiple files, even multiple 'slices' (sub-plans). Live work sits directly in `dev/work/`; finished and dropped work moves to `dev/archive/work/`.

Only the journey is archived. A reference file is current or it is gone, so nothing from outside `dev/` moves into `archive/`.

## Frontmatter

Reference `.md` files carry two frontmatter fields:

```
---
title: Issue deletion
description: What deleting an issue does and doesn't remove
---
```

They tell a reader what the file is about without opening it, and they make index.md files generatable instead of hand-maintained (see /index-md:index-md skill). Deliberately absent: `type` (the path already encodes a file's role) and dates (git records them).

## Standard layout for `docs/`

```
./  # repository root
  README.md  # entrypoint for humans. Short sections: what, (why), how to get started. Always reference docs/ files instead of duplicating content.
  CONTRIBUTING.md  # how to get started contributing. brief!
  CHANGELOG.md  # all notable changes to the project (see /changelog-md skill)
  docs/
    index.md  # optional. directory listing; can be generated (see /index-md:index-md skill)
    glossary.md  # project-specific jargon must be defined here.
    architecture.md  # high-level architecture of the project (see /architecture-md skill)
    philosophy.md  # optional. design principles and high-level goals -- one-line claims, each linking to an explainer (e.g. in explanation/)
    ...  # reference files, e.g. api.md. Succinctly describes the machinery. Should be austere. Reference material is consulted, not 'read'.
    explanation/  # optional. Diataxis concept. focus: user understanding.
      <slug>.md  # e.g. why-x-does-it-this-way.md
    how-to-guides/  # optional. Diataxis concept. focus: user goal.
      <slug>.md  # e.g. how-to-setup-mcp-server.md
    specs/  # optional. specs describe capabilities.
      <slug>.md  # e.g. issue-deletion.md
    adrs/  # optional. decision records
      <NNNN>-<slug>.md  # e.g. 0001-no-soft-deletions.md
    dev/  # the journey -- no authority promise (see 'The journey and the present')
      work/  # work in flight, e.g. plans, investigations. holds live items only
        <slug>/  # e.g. fix-bad-exception-handling/. every file within is optional:
          slices/  # optional. split large work items into 'slices' (sub-items, same files)
            <slug>/
          index.md  # only needed in case of non-obvious files
          plan.md  # goal + approach in one file, for simple work items only
          goal.md  # problem context, desired outcome, success criteria -- the why and the what
          approach.md  # the how: assumptions, decisions, verification
          status.md  # recommended: few sentences explaining where are we now. Useful when revisiting work.
          requirements.md  # only when acceptance criteria outgrow goal.md, or when no specs are in use
          research.md  # what the agent learns from web searches
          gotchas.md  # sharp edges encountered while working
          specs/  # if the work affects reference specs in docs/specs/
            # Note: load /incremental-specs:using-specs skill when working with specs.
            <spec-name>.delta.md  # 'delta' because only *difference* w.r.t. spec is described.
        backlog.md  # optional. a good place to log ideas for future improvements
      archive/  # the journey, once it is over. created on demand
        work/
          completed/
            <iso-date>-<work-slug>/  # e.g. 2026-03-20-fix-bad-exception-handling/ (prepend date to the live work slug)
          abandoned/
            <iso-date>-<work-slug>/  # dropped or superseded; describes code that was never written
      references/
        ...  # fetched material, e.g. pydantic-llms.txt from https://pydantic.dev/llms.txt
        generated/  # fetched and synthesized by agent
          <slug>.md  # e.g. db-schema.md
```

## Work items

The files listed under `<slug>/` are suggestions; a work item may contain any files. A work item has either plan.md or goal/approach/status, never both. Default to goal/approach/status; plan.md is for a simple item that can likely be completed in a single short session. If such an item grows beyond that, split plan.md into goal/approach/status and delete it. Use whatever section structure seems appropriate, unless the human has instructed you to use a particular template.

### States

A work item sits in exactly one of three places, and that place is its status:

- `dev/work/<slug>/` -- being worked on. Blocked, paused, and waiting-on-someone all count as live; record the reason in status.md.
- `dev/archive/work/completed/<iso-date>-<slug>/` -- the work landed. The item describes code that exists, though it may have drifted since.
- `dev/archive/work/abandoned/<iso-date>-<slug>/` -- the work stopped and won't resume. Superseded counts. The item describes code that was never written, so never read it as a record of the codebase.

Three states, no more. Extra directories for finer status turn the file tree into a state machine somebody has to maintain, and status.md already covers the nuance.

Live items sit directly in `work/`, so `ls docs/dev/work/` is the list of what is in flight and a search under `work/` returns live material only. The two archive buckets sit outside `work/` so that a bucket name can never collide with a work slug.

Before abandoning, promote whatever outlives the item: "we decided not to do X because Y" is an ADR, and a sharp edge someone will hit again belongs in reference docs. Then move the item and move on. `abandoned/` exists to keep `work/` accurate at the cost of one `git mv` -- it isn't there to preserve plans.

## Principles

- **Less is more**: The more detail you write, the more information can go stale.
- **Use a persistent task tracker**: Tasks survive session termination. Respect the human's preference. If none found, ask how they prefer tasks be tracked and whether tasks may be referred to from reference docs. Persist the answer in the main project memory file (AGENTS.md or CLAUDE.md). Fallback case: markdown checklist in a tasks.md; depending on granularity, combine with agent's builtin task/todo tools (if available).
- **Keep UPPERCASE.md** files to a minimum. When everything screams 'IMPORTANT', nothing is important.

## Advanced

### Monorepos

Each project in a monorepo gets its own `docs/`, following this layout. The top-level `docs/` brings together cross-cutting information only, e.g. system architecture spanning projects, org-wide ADRs. If it applies to a single project, it belongs in that project's `docs/`.

## Further reading

- [Diataxis](https://diataxis.fr) -- prior art: `explanation/` and `how-to-guides/` borrow its vocabulary of documentation modes.
