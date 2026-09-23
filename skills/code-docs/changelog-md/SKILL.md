---
name: changelog-md
description: Guidance for maintaining CHANGELOG.md following the Keep a Changelog convention. Use when recording a notable change, cutting a release, marking a yanked release, or creating a changelog for a project that lacks one.
---

# CHANGELOG.md

`CHANGELOG.md` at the repository root is a curated list of notable changes per release, written for humans -- it is not a dump of `git log`, which is full of noise.

## Format (Keep a Changelog 1.1.0)

- An `[Unreleased]` section at the top accumulates changes for the next release; on release it becomes a new version section.
- One section per released version, newest first: `## [x.y.z] - YYYY-MM-DD` (ISO 8601 dates only).
- Group entries under six categories: `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`.
- Mark pulled releases with a `[YANKED]` tag: `## [0.0.5] - 2014-12-13 [YANKED]`.
- State whether the project follows Semantic Versioning.

## Rules

- Every released version gets an entry. A selectively-maintained changelog is worse than none: readers treat an incomplete one as authoritative.
- Never omit deprecations and removals -- upgrading users need breaking changes spelled out.
- Add to `[Unreleased]` as part of completing work, not retroactively at release time.

## Further reading

- [Keep a changelog](https://keepachangelog.com/en/1.1.0/) -- the convention this file follows; source of this guidance.
