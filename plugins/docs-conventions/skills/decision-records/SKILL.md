---
name: decision-records
description: Guidance for writing decision records under docs/decisions/ -- when a decision is worth recording, how they are numbered, and the minimal format. Use when recording a decision, adding or superseding a decision record, or judging whether a decision warrants one.
---

# docs/decisions/

A decision record records that a decision was made and why. The value is in the record, not in filling out sections: a single paragraph is a complete record.

Files are `docs/decisions/<NNNN>-<slug>.md`, e.g. `0001-no-soft-deletions.md`. The number is the highest existing one plus one, zero-padded to four. Create `docs/decisions/` when the first record needs it, not before.

These are ADRs (architecture decision records) without the assumption that every decision worth recording is architectural. Half of what belongs here is not: a compliance constraint, a deliberate deviation from the obvious path, a rejected library. Hence `decisions/`.

## When to write one

All three must hold:

1. **Hard to reverse** -- changing your mind later costs something real.
2. **Surprising without context** -- a future reader will look at the code and wonder why it was done this way.
3. **A real trade-off** -- there were genuine alternatives, and one was picked for specific reasons.

If the decision is easy to reverse, skip it; it will just get reversed. If it isn't surprising, nobody will wonder. If there was no alternative, there is nothing to record beyond doing the obvious thing.

What usually qualifies:

- **Architectural shape** -- "the write model is event-sourced, the read model is projected into Postgres".
- **Integration patterns** -- "ordering and billing talk over domain events, never synchronous HTTP".
- **Technology choices that carry lock-in** -- database, message bus, auth provider, deployment target. Not every library, only the ones that would take a quarter to swap out.
- **Boundaries and ownership** -- "customer data belongs to the customer service; everyone else references it by ID". The explicit no's are worth as much as the yes's.
- **Deliberate deviations from the obvious path** -- "manual SQL instead of an ORM, because X". These stop the next engineer from 'fixing' something that was intentional.
- **Constraints invisible in the code** -- a compliance rule, a partner API's latency budget.
- **Rejected alternatives whose rejection is subtle** -- record why GraphQL lost to REST, or someone proposes GraphQL again in six months.

Dropped work is a common source: "we decided not to do X because Y" outlives the work item it came from, and the item itself gets deleted (see /using-docs skill).

## Format

```md
---
title: No soft deletions
description: Why deleted rows leave the database instead of being flagged
---

# No soft deletions

<1-3 sentences: the context, the decision, and the reason.>
```

Add a section only when it earns its place; most records need none:

- **Considered options** -- when the rejected alternatives are worth remembering.
- **Consequences** -- when the downstream effects are non-obvious.
- **`status:` frontmatter** (`proposed`, `accepted`, `superseded by 0007`) -- when decisions get revisited.

## Drafting inside a work item

A decision taken while doing a piece of work is drafted at `docs/wip/<work-slug>/decisions/<slug>.md` and promoted to `docs/decisions/` when the work lands. Drafts carry no number: assigning it at promotion keeps two concurrent work items from claiming the same one. Promote with `git mv` and add the number to the filename then.

## Superseding

A decision record records a decision at a point in time, so it stays true even after the decision is reversed. This is the exception to the rule that a stale reference file gets deleted. Don't rewrite a record to match a newer decision and don't delete it: write a new record, and note in the old one which record replaced it.

Because records are never edited in place, they have no delta form. A draft that reverses `0003` is an ordinary draft that says so.

## Further reading

- [ADR format](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/ADR-FORMAT.md) -- Matt Pocock's minimal-ADR guidance; source of the three tests above.
