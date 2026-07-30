#!/usr/bin/env python3
"""Regenerate the body of a directory's index.md from the directory's contents.

The frontmatter of index.md (title, description) is authored by hand. The body
is derived: a subdirectory contributes the title + description from its own
index.md frontmatter; a .md file contributes the ones from its frontmatter,
falling back to its first heading, then its filename. Other files are listed
only when matched by an --include pattern, or when already present in the index.

Regeneration is additive, not destructive: a description that exists only in
the current index.md body is kept; the source file's frontmatter wins when
both exist; entries whose file still exists are never dropped, entries whose
file is gone are. The script refuses to touch a body containing content it
cannot merge (prose, section headings).

An existing index.md is always regenerated. Creating a missing one depends on
mode: without -r, the named directory simply gets one. With -r, a directory
only gets one when it holds something index-worthy -- a subdirectory with an
index.md, or a .md file carrying both title and description. Bottom-up order
makes worthiness propagate: one documented file deep in the tree pulls
index.md files up its ancestor chain. -r --no-strict indexes every directory.
--refresh-only never creates: only existing index.md files are regenerated --
the mode for machinery (a created index.md needs its description authored).

Usage: generate_index.py DIRECTORY [-r] [--no-strict] [--refresh-only] [--include GLOB]...
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Iterator
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path

FM_DELIMITER = "---"

ENTRY_RE = re.compile(
    r"^[-*]\s+\[(?P<label>.+?)\]\((?P<href>.+?)\)\s*(?:[-:]\s+(?P<desc>.+?))?\s*$"
)


@dataclass
class Frontmatter:
    # None means the field is absent from the source file: it is never
    # invented, only reported.
    title: str | None
    description: str | None
    raw: str  # the original frontmatter block, delimiters included, verbatim


@dataclass
class ExistingEntry:
    label: str
    href: str  # as written in the index, trailing slash and all
    description: str | None  # None: the current index lists this entry bare


@dataclass
class Entry:
    label: str
    href: str
    description: str | None  # None: no source has a description yet
    expects_description: bool


def parse_frontmatter(text: str) -> Frontmatter | None:
    """Return the leading frontmatter block of a file, or None if absent."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FM_DELIMITER:
        return None
    for idx in range(1, len(lines)):
        if lines[idx].strip() != FM_DELIMITER:
            continue
        fields: dict[str, str] = {}
        for line in lines[1:idx]:
            if ":" in line and not line.startswith((" ", "\t")):
                key, _, value = line.partition(":")
                fields[key.strip()] = value.strip().strip("'\"")
        title = fields.get("title") or fields.get("name") or None  # 'name' accepted leniently
        return Frontmatter(
            title=title,
            description=fields.get("description") or None,
            raw="\n".join(lines[: idx + 1]),
        )
    return None


def parse_body(body: str) -> dict[str, ExistingEntry] | None:
    """Map href (sans trailing /) -> existing entry. None if unmergeable."""
    entries: dict[str, ExistingEntry] = {}
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "#" or stripped.startswith("# "):
            continue
        match = ENTRY_RE.match(stripped)
        if match is None:
            return None
        href = match.group("href")
        entries[href.rstrip("/")] = ExistingEntry(
            label=match.group("label"),
            href=href,
            description=match.group("desc"),
        )
    return entries


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def merged_description(source: str | None, prev: ExistingEntry | None) -> str | None:
    """The source frontmatter wins; otherwise keep what the index already says."""
    if source is not None:
        return source
    if prev is not None:
        return prev.description
    return None


def entry_for_subdir(subdir: Path, prev: ExistingEntry | None) -> Entry:
    href = f"{subdir.name}/"
    child_index = subdir / "index.md"
    fm: Frontmatter | None = None
    if child_index.is_file():
        fm = parse_frontmatter(child_index.read_text(encoding="utf-8"))
    label = fm.title if fm is not None and fm.title is not None else subdir.name
    source_description = fm.description if fm is not None else None
    return Entry(label, href, merged_description(source_description, prev), expects_description=True)


def entry_for_md_file(path: Path, prev: ExistingEntry | None) -> Entry:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is not None and fm.title is not None:
        label = fm.title
    else:
        heading = first_heading(text)
        label = heading if heading is not None else path.name
    source_description = fm.description if fm is not None else None
    return Entry(label, path.name, merged_description(source_description, prev), expects_description=True)


def collect_entries(
    directory: Path, existing: dict[str, ExistingEntry], include: list[str]
) -> tuple[list[Entry], list[str]]:
    """Entries for the new body (sorted), plus stale entries that were dropped."""
    keyed: list[tuple[str, Entry]] = []
    seen: set[str] = set()
    for child in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if child.name.startswith(".") or child.name == "index.md":
            continue
        prev = existing.get(child.name)
        if child.is_dir():
            entry = entry_for_subdir(child, prev)
        elif child.suffix == ".md":
            entry = entry_for_md_file(child, prev)
        elif any(fnmatch(child.name, pattern) for pattern in include):
            description = prev.description if prev is not None else None
            entry = Entry(child.name, child.name, description, expects_description=False)
        else:
            continue
        seen.add(child.name)
        keyed.append((child.name.lower(), entry))

    stale: list[str] = []
    for key, prev in existing.items():
        if key in seen:
            continue
        if (directory / key).exists():
            # The file exists but falls outside the include set: another
            # agent put it here on purpose -- keep the entry as-is.
            keyed.append((key.lower(), Entry(prev.label, prev.href, prev.description, expects_description=False)))
        else:
            stale.append(f"[{prev.label}]({prev.href})")
    keyed.sort(key=lambda pair: pair[0])
    return [entry for _, entry in keyed], stale


def index_worthy(directory: Path) -> bool:
    """Would an index.md say more than `ls` does?"""
    for child in directory.iterdir():
        if child.name.startswith("."):
            continue
        if child.is_dir():
            if (child / "index.md").is_file():
                return True
        elif child.suffix == ".md" and child.name != "index.md":
            fm = parse_frontmatter(child.read_text(encoding="utf-8"))
            if fm is not None and fm.title is not None and fm.description is not None:
                return True
    return False


def render(frontmatter_raw: str, title: str, entries: list[Entry]) -> str:
    lines = [frontmatter_raw, "", f"# {title}", ""]
    for entry in entries:
        if entry.description is not None:
            lines.append(f"- [{entry.label}]({entry.href}): {entry.description}")
        else:
            lines.append(f"- [{entry.label}]({entry.href})")
    return "\n".join(lines).rstrip("\n") + "\n"


def process_directory(
    directory: Path, include: list[str], create_always: bool, refresh_only: bool
) -> tuple[bool, list[str]]:
    """Regenerate directory/index.md in place. Returns (written, warnings)."""
    assert directory.is_dir(), directory
    dir_name = directory.resolve().name  # Path(".").name is "" -- resolve first
    assert dir_name, directory
    warnings: list[str] = []
    index_path = directory / "index.md"

    if not index_path.is_file():
        if refresh_only:
            return False, []
        if not create_always and not index_worthy(directory):
            return False, []

    fm: Frontmatter | None = None
    body = ""
    if index_path.is_file():
        text = index_path.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        body = text[len(fm.raw) :] if fm is not None else text

    existing = parse_body(body)
    if existing is None:
        raise SystemExit(
            f"error: {index_path} contains content the generator cannot merge "
            "(prose or section headings); update it by hand"
        )

    if fm is None:
        # The directory name is real data; the description is not ours to
        # invent -- leave it empty and report it.
        fm = Frontmatter(
            title=dir_name,
            description=None,
            raw=f"{FM_DELIMITER}\ntitle: {dir_name}\ndescription:\n{FM_DELIMITER}",
        )
        verb = "frontmatter added" if index_path.is_file() else "created"
        warnings.append(f"{index_path}: {verb} -- author its description")
    elif fm.description is None:
        warnings.append(f"{index_path}: frontmatter has no description")

    entries, stale = collect_entries(directory, existing, include)
    for entry in entries:
        if entry.expects_description and entry.description is None:
            warnings.append(f"{directory / entry.href}: no description")
    for dropped in stale:
        warnings.append(f"{index_path}: dropped stale entry {dropped}")

    title = fm.title if fm.title is not None else dir_name
    index_path.write_text(render(fm.raw, title, entries), encoding="utf-8")
    return True, warnings


def iter_dirs_bottom_up(root: Path) -> Iterator[Path]:
    for child in sorted(root.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir() and not child.name.startswith("."):
            yield from iter_dirs_bottom_up(child)
    yield root


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="directory whose index.md to (re)generate")
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="index every subdirectory too, bottom-up; skips directories with "
        "nothing index-worthy (see --no-strict)",
    )
    parser.add_argument(
        "--no-strict",
        action="store_true",
        help="with -r: create an index.md in every directory, worthy or not",
    )
    parser.add_argument(
        "--refresh-only",
        action="store_true",
        help="only regenerate existing index.md files; never create one",
    )
    parser.add_argument(
        "--include",
        action="append",
        default=[],
        metavar="GLOB",
        help="also list files matching this pattern (repeatable), e.g. --include '*.py'",
    )
    args = parser.parse_args()
    directory: Path = args.directory
    include: list[str] = args.include
    if not directory.is_dir():
        raise SystemExit(f"error: not a directory: {directory}")

    create_always = not args.recursive or args.no_strict
    targets = list(iter_dirs_bottom_up(directory)) if args.recursive else [directory]
    warnings: list[str] = []
    written = 0
    for target in targets:
        wrote, target_warnings = process_directory(
            target, include, create_always, args.refresh_only
        )
        written += int(wrote)
        warnings.extend(target_warnings)

    noun = "directory" if written == 1 else "directories"
    skipped = len(targets) - written
    summary = f"indexed {written} {noun}"
    if skipped:
        summary += f", skipped {skipped} with nothing index-worthy (--no-strict overrides)"
    print(summary)
    if warnings:
        print("needs attention:")
        for warning in warnings:
            print(f"  {warning}")


if __name__ == "__main__":
    main()
