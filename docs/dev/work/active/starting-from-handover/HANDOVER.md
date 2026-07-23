# Handover: agent-knowledge-plugins

For the next agent working in this repo. Adriaan (software engineer, founder at klassif.ai) is building a methodology for AI-assisted knowledge work, plus the Claude plugins that implement it. The design phase is largely done; you are entering the execution phase, working directly inside `agent-knowledge-plugins/`.

## The core idea

Agents lack the implicit world-model a human engineer carries. The methodology makes that missing context explicit and discoverable, in three git-friendly stores:

1. **Docs** -- the `docs/` directory in a codebase. Reference-grade: it must reflect the state of the code.
2. **Wiki** -- a git-tracked bundle of interlinked markdown files (OKF format), maintained by human and agent together, accumulating knowledge across projects. "Context wiki" is pitch language; in specs, say "wiki".
3. **Agent memory** -- the agent's own space, e.g. `.agents/memories/<id>/`.

The test for where a piece of knowledge belongs is what it answers to: a docs file is wrong when it disagrees with the code; a wiki note is wrong when it disagrees with the world; a memory is wrong when it disagrees with the agent's actual history and the human's preferences.

## Settled decisions

### Vocabulary

- **Role**: what kind of document a file is (spec, ADR, how-to, work item, archive), and therefore what tense it speaks in and when to reach for it. The path assigns the role.
- **Authority** (chosen over "reliability"): whether you may build on a file without re-verifying it against the code. Everything in `docs/` outside `dev/` carries full authority; `dev/` promises nothing. Do not introduce "relevance" as a third dimension -- it follows from role.
- One-line pitch for the docs approach: "a standard layout for `docs/` where a file's path tells you its role and authority." Convention over configuration, applied to documentation. Diátaxis is prior art to cite, not to fold into the name.

### Docs layout

- Reference material (glossary, architecture, `explanation/`, `how-to-guides/`, `specs/`, `adrs/` with `NNNN-slug` numbering) is held to "less is more": more content means more to correct when the code changes.
- Work items live under `docs/dev/work/active/<slug>/` and move to `docs/dev/work/completed/<iso-date>-<slug>/` on completion. This was decided over a `history/work/` archive: a work item stays under `work/` its whole life, completion changes status not category, and there was no second category to justify `history/`. Datestamp is added at completion. (Precedent: OpenAI's harness-engineering post uses the same active/completed split.)
- Reference knowledge learned during a work item gets reiterated in the docs when it's about this code, or filed in the wiki when it's true beyond this repo.
- `docs/dev/references/` holds fetched and generated material (e.g. `pydantic-llms.txt`, `generated/db-schema.md`).

### Wiki layout

- The repo **is** the wiki -- no nested `wiki/` directory. `raw/` (immutable originals) and `output/` (generated, reproducible) are conventional **sibling** directories outside the clone, known to the tooling, never tracked by git. This avoids binary bloat and the `wiki/wiki/` awkwardness.
- `sources/` inside the wiki holds ingestion notes about raw material. Each note must stand alone: origin, content hash, enough summary to be useful, so the raw file is a local cache, not a citation target.
- Draft status is frontmatter (`status: draft`), not a `drafts/` folder -- moving files breaks inbound links. Folders for lifecycle, links for structure, frontmatter for metadata.
- Standard markdown links, not wikilinks.
- Repo naming: subject plus `-wiki`, no format infix. Planned: `klassifai-wiki` (company), `klassifai-eng-wiki` (engineering), `adriaan-wiki` (personal). Wikis layer: an agent can reference both a personal and a company wiki.
- The planned companion CLI generates the full index from directory `index.md` files and the `description` frontmatter field (OKF progressive disclosure). It should also surface `status: draft` pages.

### Agent memory

Three parts under the agent's memory root:

- `system/` -- injected into the system prompt, size-constrained per file. Three kinds: about the human, about the agent, core. By editing these the agent shapes its future identity.
- `reference/` -- only file paths appear in the system prompt; content is read on demand. Per-directory `index.md` with descriptions is still undecided (see open questions).
- `skills/` -- procedural memory, following Anthropic's agent skills spec.

Memory mounts the wiki repos rather than embedding them, preserving authority boundaries: docs are human-final, the wiki is collaborative, memory is agent-owned. History compaction, agent dreaming, and Letta-style defragmentation are one primitive under different names; treat them as such.

## The repo you're in

```
agent-knowledge-plugins/
├── examples/
├── PHILOSOPHY.md
├── plugins/
│   ├── agent-memory/       # memory block (renamed from auto-memory)
│   ├── context-wikis/      # wiki block
│   ├── foundations/        # shared substrate: index-md and okf skills
│   ├── simple-specs/       # spec-driven-dev skill (renamed from how-to)
│   └── structured-docs/    # docs block: structured-docs and scaffold skills
└── README.md
```

- The marketplace was renamed from `knowledge-management-plugins` to `agent-knowledge-plugins` ("knowledge management" reads as enterprise SharePoint vocabulary).
- Plugin boundaries follow audiences, not code size: a non-engineer takes `foundations` + `context-wikis` + `agent-memory`; an engineer adds `structured-docs` and `simple-specs`. Keep the optional plugins truly standalone; each README must state its dependencies, `foundations` included.
- `structured-docs` kept its name even though "conventional docs" was argued to be the better term for the methodology. If you touch naming, raise it rather than silently renaming either way.

## Open questions

1. Inside a work item: is there a `README.md`? A `slices/` directory for subplans? Both carried question marks in the last layout draft.
2. `reference/` memory: per-directory `index.md` listings -- Adriaan is on the fence.
3. Whether `docs/dev/references/` needs a lifecycle rule of its own (it will accumulate).
4. `simple-specs`: the "simple" qualifier may age badly, same argument that retired "auto-memory". Not yet decided.
5. Marketplace name candidates `knowledge-plugins`, `agent-knowledge`, `docs-wiki-memory` were discussed; `agent-knowledge-plugins` won for now.

## How to work with Adriaan

- Framework first, implementation second. He pushes back when conversation drifts to schema specifics before the concept is settled.
- Short, direct answers. He corrects over-claims; don't inflate.
- He narrows progressively: broad framing, then comparison, then a concrete recommendation. Give him real trade-offs, then a position.
- Naming standard: plain, established words over coinages. Formats and mechanisms don't belong in names; purpose does.
