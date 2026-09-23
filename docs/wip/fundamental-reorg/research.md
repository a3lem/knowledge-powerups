---
title: Research
description: Verified facts about how Claude Code and npx skills install what this repo ships
---

# Research

Gathered 2026-09-22. Sources are the official docs, three public repos, and
the installed `skills` CLI (v1.5.23) and Claude Code plugin cache on the
maintainer's machine. Each finding says which.

## Claude Code plugins

- **A repo root can be both marketplace and plugin.** `.claude-plugin/`
  holds `marketplace.json` and `plugin.json` side by side, and the
  marketplace entry uses `"source": "./"`. Seen in obra/superpowers,
  obra/episodic-memory, and anthropics/skills (raw manifests fetched from
  GitHub main). The docs neither show nor forbid it. Authoritative by
  example; these repos are widely installed.
- **Skill paths can be listed explicitly.** Both `plugin.json` and a
  marketplace entry accept a `skills` list of directories. anthropics/skills
  defines five plugins from the same `./` root by giving each entry its own
  list, e.g. `["./skills/xlsx", "./skills/docx"]`. Docs: the field "adds to
  the default `skills/` scan". This is how a grouped layout such as
  `skills/code-docs/<name>/` is declared.
- **Default discovery is one level.** Without the list, only
  `skills/<name>/SKILL.md` is found. Docs, plugins-reference.
- **Install copies the plugin directory** into
  `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/`. With source
  `./` the whole repo is the plugin, so `clis/` and `plugins/` are copied
  too. Only root-level component directories are loaded from the copy.
  Docs plus the maintainer's cache: the cached `index-md` 0.1.0 holds only
  README, `.claude-plugin/`, `skills/`.
- **Symlinks at install** (docs, plugins-reference): a link whose target is
  inside the plugin is kept as a relative link; a link to elsewhere in the
  same marketplace is dereferenced and the content copied; a link outside
  the marketplace is dropped. Paths written with `../` outside the plugin
  are rejected. This is the sanctioned way for a companion plugin under
  `plugins/` to reach `clis/`.
- **`bin/` is added to PATH.** The plugins-reference layout lists
  `bin/  # Plugin executables added to PATH`. Not tested here. If it works
  as described, a skill can call `index-gen` by name under Claude Code
  instead of through `${CLAUDE_PLUGIN_ROOT}`.
- **A local-directory marketplace still copies.** The docs say a relative
  source in a marketplace added from a local directory loads in place, but
  the step 7 test on 2026-09-22 (Claude Code 2.1.278) copied both plugins
  into `~/.claude/plugins/cache/knowledge-powerups/`, with the symlink
  behaviour described above. Observed, not explained.
- **Renaming the marketplace** changes the key installed plugins are
  registered under in `installed_plugins.json`, so existing installs need a
  re-add. Observed in the maintainer's `~/.claude/plugins/`.

## npx skills (the `skills` CLI)

Read from the installed package source, `dist/cli.mjs`, v1.5.23.

- **Discovery**: walks `skills/` up to three levels deep, and also reads the
  `skills` lists from `.claude-plugin/marketplace.json` entries and
  `.claude-plugin/plugin.json`. Grouped skills are found without help.
- **Copy**: copies only the skill directory. Every symlink is dereferenced
  (`cp` with `dereference: true`), broken links are skipped with a warning,
  and `__pycache__`, `__pypackages__`, `.git` and `metadata.json` are
  excluded.
- **No `CLAUDE_PLUGIN_ROOT`**: the skill lands in `~/.agents/skills/<name>/`
  with a symlink from `~/.claude/skills/`. Nothing tells the skill where it
  is except the path Claude Code loaded it from.

## Consequence for the shared CLI

Under Claude Code, `clis/index-gen` is inside the plugin and reachable as
`${CLAUDE_PLUGIN_ROOT}/clis/index-gen/...`. Under `npx skills` only the
skill directory travels, so the skill needs a symlink into `clis/` that the
installer turns into a private copy. The SKILL.md must therefore describe
the script's location relative to itself, not through the variable.
