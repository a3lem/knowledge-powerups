---
title: Knowledge in work items without a durable home
description: Analysis by the ai-lab-bb session (2026-09-25) of what work items learn that no store keeps, with design ideas; input, not decisions
---

# Knowledge in work items without a durable home

Received 2026-09-25 as a cross-session message from session ai-lab-bb
(ai-lab repo), written with Adriaan. Kept verbatim as input for the
context-wiki skill. Nothing here is decided.

Scope of the analysis: work items (docs/dev/work, docs/wip, and their
archives) in ai-lab, ai-apps and agent-knowledge-plugins. 18 archived items,
114 work-item files.

## Findings

- Archived items are write-once. 16 of 18 have exactly one commit, which is
  the move into the archive. Almost nothing live links to them: 1 open
  ticket (and its path is broken), plus 1 active item.
- Most archives came from bulk migrations, not from normal lifecycle.
  ai-apps archived 4 items on 2026-08-11, and agent-memory archived 9 on
  2026-09-22.
- Spec deltas are merged reliably where the delta workflow runs. In
  agent-knowledge-plugins, 18 of 21 delta files match the current specs.
  The rest are probably superseded by later deltas.
- Decisions and lessons are NOT promoted. None of the three repos has a
  real decisions/ practice outside agent-knowledge-plugins' single ADR.
  ai-apps ADR-001 is still in docs/dev/archive/legacy/, although a closed
  ticket said to promote it. ai-lab's form-type-split rationale exists only
  in its archive.
- The using-docs convention asks for promotion before ABANDON. On COMPLETE,
  it asks only that reference docs are applied. It does not require ADRs or
  lessons.

## Kinds of knowledge in work items

These kinds HAVE a home:

- the change -> code
- behavior -> specs
- decision + why -> ADR (the home exists but is underused)
- local sharp edge -> comment, assert, or test
- task state and plans -> the tracker, and they expire at close

These kinds have NO home (examples are real):

1. Facts about external systems that the repo does not own. prd_main:
   array_length('{}',1) is NULL, entity_annotation.page is 1-based.
   Document AI: the regional endpoint is mandatory, and v1 drops
   descriptions. pgvector/Qdrant behavior. These are already reused across
   items: the extraction benchmark cites form-fill-benchmark's
   db-findings.md, and a ticket cites another repo's approach.md D12.
2. Empirical results, including negative ones. "The log transform beats the
   bit code, mAP 0.9514 vs 0.9450." "The angle delimiter gives no recall
   gain and +16% tokens, so skip it." A result is conditional on dataset,
   model, and date. It is not a decision.
3. Beliefs with uncertainty. "Survey findings are leads, not facts." "The
   labels are a proxy for same-template."
4. Corrections. "The earlier 0-based-tenant reading was wrong; the gate
   rejected 1,624 docs for nothing." Nothing marks the old belief as
   superseded.
5. Patterns across repos. "The silent drop is a class, not an incident."
   "Verify a port by reproduction." Today these go ad hoc into the
   workspace CLAUDE.md, with no limit.
6. Environment facts. fish rejects VAR=value cmd; the sandbox cannot read
   ~/.config/gcloud. These are user-level facts that leak into project
   gotchas.
7. Facts about the organization: ownership, and which team decides what.
8. Lessons about the human-agent collaboration: preferences, and recurring
   agent errors.

Why these have no home: a home gives an anchor (where the knowledge
applies), a trigger for invalidation (when to check it again), and an
owner. Code-anchored knowledge gets all three from the code. The kinds
above have none, so they cannot be told apart from stale material.

## Design ideas

Adriaan's meta-goal: build on past learnings without collector's fallacy.

- Work item = episodic memory. Facts and beliefs = semantic memory. Tests,
  checklists, and skills = procedural memory. Consolidate at close, and
  then let the episode go (git keeps it).
- Store claims, not documents. Each claim is one assertion with: scope
  (system, path, or repo), provenance (commit or date), confidence
  (verified, observed, or believed), and status (current, or
  superseded-by).
- A contradiction replaces the old claim. It is not appended.
- Retrieval is by scope. An agent that touches prd_main queries sees the
  prd_main claims only.
- Promotion deletes. When code, an assert, or a test enforces a claim,
  remove the prose. When a pattern becomes a checklist or skill, remove the
  prose.
- Closing a work item emits a short claim diff for the human to review ("3
  new, 1 superseded, 1 promoted to test"). After that, the item can be
  deleted.
- Candidate homes: a per-system field guide at workspace level
  (db-findings.md is a seed); a results register with conditions (ai-lab
  docs/dev/studies/ is a seed); user-level memory for environment and
  collaboration lessons.
- Use an order of strength for placement: code/assert > test/CI > local
  comment > nearest AGENTS.md > spec/ADR > archive. A lesson that exists
  only in the archive is "identified", not "learned".
