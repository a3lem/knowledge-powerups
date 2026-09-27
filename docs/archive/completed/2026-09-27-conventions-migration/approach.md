---
title: Approach
description: What is settled about the migration log, and what still needs thought
---

# Approach

Unverified against practice. Nothing here has been tried on a real repo that
is actually behind.

## Settled

**A reference file, not a new skill.** A skill loads when its description
matches something the user asked for. Nobody asks to upgrade their docs
conventions -- the agent finds the mismatch while doing other work. A skill
described as "use when a repo's docs predate the current conventions" can
never trigger, because the agent chooses its skills before it has looked at
the repo. So the log has to be reachable from `using-docs`, which loads
whenever anyone touches `docs/`.

**`adopt-conventions` keeps its single job.** Widening it to cover upgrades
was considered and rejected on the same argument: nobody asks to upgrade, so
the procedure would sit in a skill that does not load at the moment it is
needed. The upgrade procedure is four steps -- read the entries newer than
the repo's version, run the `git mv` commands, sweep for references to the
old paths, update the marker -- which fits beside the entries it acts on.

One step does belong in `adopt-conventions`: write the version marker when
onboarding a repo. Without it, the scheme fails for every repo onboarded
from now on. That is onboarding, not upgrading.

**Version the layout, not the plugin.** A fix to `changelog-md` bumps the
`docs-conventions` plugin version and would mint a migration section with
nothing in it. The layout needs its own number.

**Harness-agnostic placement.** Plugin manifests are specific to one agent
harness; skills should not depend on them. The
[agentskills.io specification](https://agentskills.io/specification) puts a
version under `metadata.version` in SKILL.md frontmatter. Same argument for
the repo marker: prefer AGENTS.md over CLAUDE.md, since AGENTS.md is the
cross-harness convention and CLAUDE.md can import it.

**State the version in the skill body too.** Frontmatter may never reach the
model; the body always does. Putting the layout version in the prose means
one side of the comparison is always visible, and the agent only has to find
the other side in AGENTS.md.

**Entries are executable, and not every change earns one.** Only changes
that make an existing repo *wrong* need an entry. A new optional directory
needs none -- old repos simply do not have it.

**Newest first.** The reader scans down until reaching their own version,
then stops.

## Open

1. **The check has no trigger.** Everything above assumes the agent thinks
   to compare the two versions. Nothing makes it. An explicit instruction in
   `using-docs` ("on first touching `docs/` in a session, compare the marker
   against the version below") would fire every session in every repo,
   including the large majority that are already current. That cost is paid
   constantly for a check that matters rarely. No good answer yet. This is
   the weakest joint in the whole design and probably the thing to think
   about first.
2. **Repos with no marker.** Everything that adopted the conventions before
   markers existed has none. Options: infer the version from the shape of
   the tree (`docs/dev/` present means pre-2026-09-15), treat "no marker" as
   "oldest known", or ask the human. Inference is attractive because the
   layout changes are all structural, but it needs the log to carry a
   recognisable fingerprint per version, which is extra work per entry.
3. **Is AGENTS.md right?** It is the only file the agent reads
   unconditionally, which is the whole argument for it. But the marker is a
   fact about `docs/`, not an instruction to the agent, and some repos have
   no AGENTS.md. `docs/index.md` frontmatter was the alternative considered;
   rejected because index.md is optional in the layout. Worth revisiting.
4. **Version format.** A plain incrementing integer, semver, or the date of
   the change. Date needs no separate registry and every change has one.
   Integer reads more clearly as "you are two behind". Undecided.
5. **Approval.** A migration moves files. `adopt-conventions` requires human
   approval before moving anything in a brownfield repo; the same rule
   probably applies here, but "probably" is doing real work in that
   sentence. An agent that silently restructures `docs/` mid-task while
   doing something unrelated would be worse than the split tree we are
   trying to prevent.
6. **Where the log file lives.** `using-docs/migrations.md` is assumed
   throughout. Not seriously examined against alternatives.

## Files this would touch

- `plugins/docs-conventions/skills/using-docs/SKILL.md` -- version in body
  and in `metadata.version`, pointer to the log.
- `plugins/docs-conventions/skills/using-docs/migrations.md` -- new. The log
  plus the four-step procedure.
- `plugins/docs-conventions/skills/adopt-conventions/SKILL.md` -- write the
  marker when onboarding.
