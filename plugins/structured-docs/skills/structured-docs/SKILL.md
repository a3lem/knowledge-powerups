---
name: structured-docs
description: A system of organization for code base documentation.
---

# Structured Code Docs

Always use standard layout for `docs/`, so that the role and reliability of a file can be inferred from its path in the file tree.

- **'role'**: the kind of document -- e.g. a spec, ADR, how-to, work item, etc. -- and therefore whether it refers to state of affairs in the past or in the present. The path determines the role.
- **'authority'**: Whether you can build on the file's content without re-verifying it against the code. Everything in docs/ outside docs/dev/ carries high authority.

## Standard layout for `docs/`

Note: `?` after the file/folder means 'optional'.

```
./docs/
  index.md  # directory listing (see /index-md skill)
    glossary.md  # project-specific jargon must be defined here.
  architecture.md  # describe the high-level architecture of the project
  ... 
  ... # reference files, e.g. api.md
  explanation/ ?  # Diataxis concept. focus: Understanding.
    <slug>.md  # e.g. why-x-does-it-this-way.md
  how-to-guides/ ?  # Diataxis concept. focus: goal.
    <slug>.md   # e.g. how-to-setup-mcp-server.md
  specs/ ?
    <slug>.md  # e.g. issue-deletion.md. Specs describe capabilities.
  adrs/ ?  # decision records
    <\d{4}>-<slug>.md  # e.g. 0001-no-soft-deletions.md
  # IMPORTANT: everything **above** can be treated as trustworthy. Both human
  # and agent take pains to ensure the information is current, reflecting the
  # state of code base. Drift is treated as a bug and corrected. Stale files are
  # removed. 'Less is more' thinking is applied to avoid churn.
  # CONTRAST: `dev/` (below). Workspace for developers to organize work,
  # e.g. decompose a complex plan into multiple files, even multiple 'slices'
  # (sub-plans). There is no authority promise. Files in this directory are meant
  # for 'doing the work'. Information that is no longer relevant is archived
  # in `history/`.
  dev/
    work/  # work items (mostly plans)
      active/
        <slug>/  # e.g. fix-bad-exception-handling/
          slices/ ?  # optional: split large work items over 'slices'
            <slug>/
          index.md ?  # in case of many files, directory listing: paths + descriptions.
          proposal.md ?  # context, problem, the 'why'
          design.md ?  # approach, verification
          requirements.md ?  # acceptance criteria
          research.md ?  # what the agent learns from web searches
          gotchas.md ?  # sharp edges encountered while working
          progress.md ? # a rough overview of progress. Not a to-do list!
          specs/ ?  # if the work affects reference specs in docs/specs/
            # Note: load /spec-driven-dev skill when working with specs.
            <spec-name>.delta.md  # 'delta' because only *difference* w.r.t. spec is described.
      completed/
        <iso-date>-<work-slug>/  # e.g. 2026-03-20-fix-bad-exception-handling/ (prepend date to previously active work slug)
      backlog.md ? # a good place to log ideas for future improvements
    references/
      ... # e.g. pydantic-llms.txt, fetched from https://pydantic.dev/llms.txt
      generated/  # fetched and synthesized by agent
        <slug>.md  # e.g. db-schema.md
CONTRIBUTING.md  # how to get started contributing. brief!
CHANGELOG.md  # All notable changes to the project
README.md  # Entrypoint for humans. Short sections: what, (why), how to get started. Always reference docs/ files instead of duplicating content.
```

## Principles

- **Less is more**: The more detail you write, the more information can go stale.
- **Use a dedicated task tracker**: Respect the human's preference. If none found, ask how they prefer tasks be tracked and whether tasks may be referred to from reference docs. Persist the answer in the main project memory file (AGENTS.md or CLAUDE.md).
- **Keep UPPERCASE.md** files to a minimum. When everything screams 'IMPORTANT', nothing is important.

## Details

### architecture.md

## Advanced

### Monorepos




## Web Links

- [Diataxis -- Recognizing the distinct needs of different documentation users](https://diataxis.fr)
- [Keep a changelog](https://keepachangelog.com/en/1.1.0/)
- [architecture.md](https://matklad.github.io/2021/02/06/ARCHITECTURE.md.html)
