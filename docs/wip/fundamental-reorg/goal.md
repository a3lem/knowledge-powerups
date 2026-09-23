---
title: Goal
description: Why the repo becomes one skills plugin plus optional companions, and what done looks like
---

# Goal

## Problem

The repo ships five micro-plugins from one marketplace. In practice the
skills are what get used; the plugins are packaging. That packaging costs
more than it returns:

- Five manifests, five READMEs, five version numbers, and five install
  commands for what a user experiences as one set of conventions.
- Skills that refer to each other (`using-docs` -> `index-md`,
  `using-specs` -> `using-docs`) resolve only when the user installed the
  sibling plugin. A skill pointing at a missing skill fails quietly: the
  agent reads the instruction and improvises.
- The one shared executable, `cli/generate_index.py`, sits outside every
  plugin, so an installed plugin cannot reach it. The `index-md` skill is
  broken as installed today: its cached copy calls
  `${CLAUDE_PLUGIN_ROOT}/../../cli/generate_index.py` and there is no
  `cli/` two levels up. `agent-memory` has the same defect through
  `memoryctl.py`, which resolves the generator relative to the repo checkout.
- `agent-memory`, the only plugin with hooks, adds complexity most users of
  the conventions do not want. It should be opt-in, not a peer.

The repo is also distributed as plain skills through `npx skills`, and that
path matters as much as the Claude Code plugin path.

## Desired outcome

One base plugin, `knowledge-powerups`, whose root is the repo root, holding
every knowledge skill. Companion plugins with harness integration (hooks,
agents, MCP) live under `plugins/` as separate, optional marketplace entries.
Shared executables live under `clis/` and are reachable from every skill
under both installers.

Target layout:

```text
<ROOT>/
  .claude-plugin/
    marketplace.json   # entries: knowledge-powerups (source ./) and the companions
    plugin.json        # the base plugin; lists the grouped skill paths
  skills/
    code-docs/         # a group of related skills, not a plugin
      docs-folder/
      architecture-md/
      decision-records/
      incremental-specs/
      ...              # remaining docs-conventions skills, see approach.md
    tools/
      index-md/
    context-wiki/
  clis/
    index-gen/         # today's cli/generate_index.py and its test
  plugins/
    agent-memory/
    context-wiki-companion/   # future; not created by this item
  docs/
```

## Success criteria

- `/plugin install knowledge-powerups` from the marketplace yields every
  skill, each invocable as `knowledge-powerups:<name>`, on a clean machine.
- `npx skills add <repo>` lists every skill, including the grouped ones.
- The `index-md` skill runs the generator successfully under both installers.
- `agent-memory` installs and its hooks find the generator.
- Every cross-skill reference resolves inside the base plugin.
- Top-level README, architecture.md, and glossary.md describe the new
  layout and nothing of the old one.
- The generator's tests pass from their new location.
