---
name: structured-docs
description: A standard layout for the docs/ directory of a code base, where a file's path tells you its role (spec, ADR, how-to, work item) and its authority (whether it can be built on without re-verifying against the code). Use when creating, moving, or organizing documentation, when deciding where a new document belongs, or when judging whether an existing doc is trustworthy.
---

# Structured Code Docs

Always use the standard layout for `docs/` below, so that a file's role and authority can be inferred from its path in the file tree.

- **'role'**: the kind of document -- e.g. a spec, ADR, how-to, work item, etc. -- and therefore whether it refers to state of affairs in the past or in the present. The path determines the role.
- **'authority'**: Whether you can build on the file's content without re-verifying it against the code. Everything in docs/ outside docs/dev/ carries high authority.

## Two regimes

Everything in `docs/` outside `dev/` is reference material and may be built on without re-verification. Human and agent both take pains to keep it current: drift between docs and code is a bug and gets corrected, stale files are removed, and 'less is more' thinking is applied to avoid churn.

`dev/` is the workspace for doing the work, e.g. decomposing a complex plan into multiple files, even multiple 'slices' (sub-plans). Files here make no authority promise. Finished work moves to `work/completed/`.

## Standard layout for `docs/`

```
./  # repository root
  README.md  # entrypoint for humans. Short sections: what, (why), how to get started. Always reference docs/ files instead of duplicating content.
  CONTRIBUTING.md  # how to get started contributing. brief!
  CHANGELOG.md  # all notable changes to the project (see /changelog-md skill)
  docs/
    index.md  # directory listing (see /index-md skill)
    glossary.md  # project-specific jargon must be defined here.
    architecture.md  # high-level architecture of the project (see /architecture-md skill)
    ...  # further reference files, e.g. api.md
    explanation/  # optional. Diataxis concept. focus: Understanding.
      <slug>.md  # e.g. why-x-does-it-this-way.md
    how-to-guides/  # optional. Diataxis concept. focus: goal.
      <slug>.md  # e.g. how-to-setup-mcp-server.md
    specs/  # optional. specs describe capabilities.
      <slug>.md  # e.g. issue-deletion.md
    adrs/  # optional. decision records
      <NNNN>-<slug>.md  # e.g. 0001-no-soft-deletions.md
    dev/  # developer workspace -- no authority promise (see 'Two regimes')
      work/  # work items (mostly plans)
        active/
          <slug>/  # e.g. fix-bad-exception-handling/. every file within is optional:
            slices/  # split large work items over 'slices' (sub-plans)
              <slug>/
            index.md  # in case of many files, directory listing: paths + descriptions.
            proposal.md  # context, problem, the 'why'
            design.md  # approach, verification
            requirements.md  # acceptance criteria
            research.md  # what the agent learns from web searches
            gotchas.md  # sharp edges encountered while working
            progress.md  # a rough overview of progress. Not a to-do list!
            specs/  # if the work affects reference specs in docs/specs/
              # Note: load /spec-driven-dev skill when working with specs.
              <spec-name>.delta.md  # 'delta' because only *difference* w.r.t. spec is described.
        completed/
          <iso-date>-<work-slug>/  # e.g. 2026-03-20-fix-bad-exception-handling/ (prepend date to previously active work slug)
        backlog.md  # optional. a good place to log ideas for future improvements
      references/
        ...  # fetched material, e.g. pydantic-llms.txt from https://pydantic.dev/llms.txt
        generated/  # fetched and synthesized by agent
          <slug>.md  # e.g. db-schema.md
```

## Principles

- **Less is more**: The more detail you write, the more information can go stale.
- **Use a persistent task tracker**: Tasks survive session termination. Respect the human's preference. If none found, ask how they prefer tasks be tracked and whether tasks may be referred to from reference docs. Persist the answer in the main project memory file (AGENTS.md or CLAUDE.md). Fallback case: markdown checklist in a tasks.md; depending on granularity, combine with agent's builtin task/todo tools (if available).
- **Keep UPPERCASE.md** files to a minimum. When everything screams 'IMPORTANT', nothing is important.

## Advanced

### Monorepos

Each project in a monorepo gets its own `docs/`, following this layout. The top-level `docs/` brings together cross-cutting information only, e.g. system architecture spanning projects, org-wide ADRs. If it applies to a single project, it belongs in that project's `docs/`.

## Further reading

- [Diataxis](https://diataxis.fr) -- prior art: `explanation/` and `how-to-guides/` borrow its vocabulary of documentation modes.
