#!/usr/bin/env python3
"""Regenerate the list in a directory's index.md from the directory's contents.

An index.md is plain markdown: an H1, an optional one-paragraph description,
the list, and an optional `<!-- pinned -->` marker with a hand-owned list below
it. The H1 and the paragraph are hand-written -- the generator writes the
directory's own name as the H1 when it creates the file and never touches it
again. Everything else in the body is derived: a subdirectory contributes the
H1 and first paragraph of its own index.md; a .md file contributes its
frontmatter title + description, the label falling back to its first heading,
then its filename. A first paragraph counts as a description only in an
index.md, whose format defines it as one. Other files are listed only when
matched by an --include pattern, or when already present in the index, and are
labelled with their filename minus its last suffix.

Regeneration is additive, not destructive: a description that exists only in
the current index.md is kept, and so is a label, unless the member names itself
through frontmatter, an H1, or its own index.md. The source file's frontmatter
wins when both exist. The managed list indexes this directory's members and
nothing else: an entry naming a member that is still there is never dropped,
not even one outside the --include set, and every other entry is dropped and
reported with its full text -- a link to anything but a member belongs in the
pinned block. An entry with no description in any source carries a
`<!-- to-do -->` placeholder, so the gap shows in the file and not only in the
report; the placeholder reads back as no description. The script refuses to
touch a body containing content it cannot merge (prose beyond the description,
section headings, frontmatter).

The managed list is sorted case-insensitively by label, with the filename as
the tiebreak; below a `<!-- pinned -->` marker sits a hand-owned list copied
through verbatim, and a member pinned there is left out of the managed list.
--max-desc-len bounds description text the generator copies into an index from
somewhere else; a description that lives only where it is displayed is outside
that budget. An overrun is reported against the file that has to be shortened.

The run prints a summary line, then what it changed and what needs attention.
A description the member displaced is reported with both strings, and with no
claim about which side moved -- one run cannot tell an updated source from an
edited index. A placeholder is reported against the file that should carry the
description: a .md file's frontmatter, a directory's own index.md, or this
index for a file that can hold no text. A dropped entry is quoted whole, so the
only copy of its description survives in the report; the run infers nothing
from a drop, since a renamed directory and a deleted one look identical from
here.

An existing index.md is always regenerated. Creating a missing one depends on
mode: without -r, the named directory simply gets one. With -r, a directory
only gets one when it holds something index-worthy -- a subdirectory with an
index.md, or a .md file carrying both title and description. Bottom-up order
makes worthiness propagate: one documented file deep in the tree pulls
index.md files up its ancestor chain. -r --no-strict indexes every directory.
--refresh-only never creates: only existing index.md files are regenerated --
the mode for machinery (a created index.md needs its description authored).
--migrate converts a legacy index.md carrying frontmatter to the plain-markdown
format in the same pass that regenerates it. The body wins: the frontmatter
fills in only what the body lacks, and whatever it contributed nothing to is
discarded and reported, quoted, under `changed:`.

Usage: generate_index.py DIRECTORY [-r] [--no-strict] [--refresh-only]
                         [--include GLOB]... [--max-desc-len N] [--migrate]
"""

from __future__ import annotations

import argparse
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

FM_DELIMITER = "---"

# The two markers the format defines. Everything else between the H1 and the
# end of the file is either an entry line or the description paragraph.
TODO_MARKER = "<!-- to-do -->"
PINNED_MARKER = "<!-- pinned -->"

DEFAULT_MAX_DESC_LEN = 250

ENTRY_RE = re.compile(
    r"^[-*]\s+\[(?P<label>.+?)\]\((?P<href>.+?)\)\s*(?:[-:]\s+(?P<desc>.+?))?\s*$"
)

# A href the generator has no way to check: it addresses something outside the
# filesystem (any URI scheme) or a place inside the document itself.
UNCHECKABLE_HREF_RE = re.compile(r"^(?:[A-Za-z][A-Za-z0-9+.-]*:|#)")


@dataclass(frozen=True)
class Options:
    """The run's flags, settled once in main()."""

    include: list[str]
    create_always: bool
    refresh_only: bool
    migrate: bool
    max_desc_len: int


@dataclass
class Frontmatter:
    # None means the field is absent from the source file: it is never
    # invented, only reported.
    title: str | None
    description: str | None


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
    # The file a reader has to edit to shorten this description. None means
    # the index itself: the description was never written anywhere else.
    description_source: Path | None
    # The description this entry carried in the index until the member's own
    # description displaced it. None: nothing was displaced.
    replaced_description: str | None = None

    @property
    def member_name(self) -> str:
        """The member's filename -- the tiebreak when two labels are equal."""
        return self.href.rstrip("/")

    @property
    def labelled_by_stem(self) -> bool:
        """True for a member whose label is its filename minus a suffix."""
        return not self.href.endswith(("/", ".md"))


@dataclass
class IndexBody:
    """What an index.md says about itself and about its members."""

    title: str | None = None  # None: the file carries no H1
    # The description paragraph is kept line by line, so a hand-wrapped
    # paragraph is written back exactly as it was typed.
    description_lines: list[str] = field(default_factory=list)
    entries: dict[str, ExistingEntry] = field(default_factory=dict)
    pinned: list[str] = field(default_factory=list)  # verbatim, order and all

    @property
    def description(self) -> str | None:
        return " ".join(self.description_lines) or None


def split_frontmatter(text: str) -> tuple[Frontmatter | None, str]:
    """The leading frontmatter block of a file and the body below it."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != FM_DELIMITER:
        return None, text
    for idx in range(1, len(lines)):
        if lines[idx].strip() != FM_DELIMITER:
            continue
        fields: dict[str, str] = {}
        for line in lines[1:idx]:
            if ":" in line and not line.startswith((" ", "\t")):
                key, _, value = line.partition(":")
                fields[key.strip()] = value.strip().strip("'\"")
        title = fields.get("title") or fields.get("name") or None  # 'name' accepted leniently
        block = Frontmatter(title=title, description=fields.get("description") or None)
        return block, "\n".join(lines[idx + 1 :])
    return None, text


def parse_frontmatter(text: str) -> Frontmatter | None:
    """Return the leading frontmatter block of a file, or None if absent."""
    return split_frontmatter(text)[0]


def parse_index_body(text: str) -> IndexBody | None:
    """Read an index.md. None when it holds content the generator cannot place."""
    body = IndexBody()
    in_pinned = False
    in_paragraph = False  # inside the description paragraph's own lines
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            in_paragraph = False
            continue

        if line == PINNED_MARKER:
            if in_pinned:
                # With two markers there is no telling which block is managed.
                return None
            in_pinned = True
            in_paragraph = False
            continue

        match = ENTRY_RE.match(line)
        if match is not None:
            in_paragraph = False
            if in_pinned:
                body.pinned.append(raw_line.rstrip())
                continue
            href = match.group("href")
            description = match.group("desc")
            # Members are keyed by name so the regenerated entry finds them;
            # anything else keeps its raw href, which is what gets reported.
            body.entries[member_key(href) or href] = ExistingEntry(
                label=match.group("label"),
                href=href,
                # The placeholder marks a gap, so it must not read back as a
                # description a human wrote.
                description=None if description == TODO_MARKER else description,
            )
            continue

        started = bool(body.description_lines or body.entries or in_pinned)
        if line.startswith("#"):
            # One H1, before anything else. A deeper heading, or a second one,
            # is structure this format does not have.
            if not line.startswith("# ") or body.title is not None or started:
                return None
            body.title = line[2:].strip()
            continue

        # Anything left is prose. The first paragraph is the description; a
        # second one, prose once the list has begun, or anything at all below
        # the pinned marker, is not ours to keep.
        if in_paragraph:
            body.description_lines.append(raw_line.rstrip())
            continue
        if started:
            return None
        in_paragraph = True
        body.description_lines.append(raw_line.rstrip())
    return body


def unmergeable(index_path: Path) -> SystemExit:
    return SystemExit(
        f"error: {index_path} contains content the generator cannot merge "
        "(prose beyond the description, a section heading, a second "
        f"{PINNED_MARKER} marker); update it by hand"
    )


def migrate_body(index_path: Path, text: str) -> tuple[IndexBody, list[str]]:
    """Fold an index.md's frontmatter into its body. Returns (body, notes)."""
    block, rest = split_frontmatter(text)
    assert block is not None, index_path  # only called once frontmatter is seen
    body = parse_index_body(rest)
    if body is None:
        # Refusing here is what keeps the file whole: nothing is written, so
        # no index is left half-converted.
        raise unmergeable(index_path)

    # The body wins: the frontmatter fills a gap and is otherwise discarded.
    # Every discarded string is quoted in a note, so it stays recoverable from
    # the run's output.
    notes: list[str] = []
    if body.title is None:
        body.title = block.title
    elif block.title is not None and block.title != body.title:
        notes.append(
            f"{index_path}: frontmatter title '{block.title}' discarded; "
            f"the H1 '{body.title}' stands"
        )
    if not body.description_lines:
        if block.description is not None:
            body.description_lines = [block.description]
    elif block.description is not None:
        notes.append(
            f"{index_path}: frontmatter description '{block.description}' "
            f"discarded; the paragraph '{body.description}' stands"
        )
    notes.append(f"{index_path}: frontmatter folded into the body and removed")
    return body, notes


def first_heading(text: str) -> str | None:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def index_self_description(index_path: Path) -> tuple[str | None, str | None]:
    """The H1 and description an index.md gives for its own directory."""
    text = index_path.read_text(encoding="utf-8")
    if parse_frontmatter(text) is None:
        body = parse_index_body(text)
        if body is not None:
            return body.title, body.description
    # An unmigrated or unmergeable index still has a readable H1, but not a
    # paragraph this tool can tell apart from prose -- so it contributes none.
    return first_heading(text), None


def entry_href(line: str) -> str:
    """The href of an entry line. Only entry lines are ever passed in."""
    match = ENTRY_RE.match(line.strip())
    assert match is not None, line
    return match.group("href")


def member_key(href: str) -> str | None:
    """The member of this directory an href names, or None for anything else.

    The managed list indexes this directory's members, so above the marker an
    href is one path segment, with a trailing slash for a directory. A leading
    `./` is noise and normalised away. Anything else names something that is
    not a member -- a path into a subdirectory, a `../` path, an absolute path,
    a URL -- as does a member carrying a `#fragment` or `?query`, which
    addresses a place in a file rather than the file itself.
    """
    if UNCHECKABLE_HREF_RE.match(href):
        return None
    name = (href[2:] if href.startswith("./") else href).rstrip("/")
    if not name or name in {".", ".."} or any(char in name for char in "/#?"):
        return None
    return name


def chosen_label(self_named: str | None, prev: ExistingEntry | None, fallback: str) -> str:
    """A member that names itself wins; otherwise the index's label stands.

    The fallback is a filename, which is exactly what makes a label already in
    the index worth keeping: it is the only place the member was ever named.
    """
    if self_named is not None:
        return self_named
    if prev is not None:
        return prev.label
    return fallback


def merged_description(
    source_description: str | None, source_path: Path, prev: ExistingEntry | None
) -> tuple[str | None, Path | None, str | None]:
    """The member's own description wins; otherwise keep what the index says.

    Returns (description, the file it came from, the index text it displaced).
    Displacing is only what it says: a description the index carried is gone
    from the list now, so the run has to say what it was. Filling a gap -- a
    bare entry, a placeholder -- displaces nothing, because nothing was there.
    """
    if source_description is not None:
        replaced = prev.description if prev is not None else None
        if replaced == source_description:
            replaced = None  # the two sides agree; nothing moved
        return source_description, source_path, replaced
    if prev is not None:
        return prev.description, None, None
    return None, None, None


def entry_for_subdir(subdir: Path, prev: ExistingEntry | None) -> Entry:
    child_index = subdir / "index.md"
    title: str | None = None
    source_description: str | None = None
    if child_index.is_file():
        title, source_description = index_self_description(child_index)
    description, source, replaced = merged_description(source_description, child_index, prev)
    return Entry(
        label=chosen_label(title, prev, subdir.name),
        href=f"{subdir.name}/",
        description=description,
        description_source=source,
        replaced_description=replaced,
    )


def entry_for_md_file(path: Path, prev: ExistingEntry | None) -> Entry:
    text = path.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if fm is not None and fm.title is not None:
        self_named = fm.title
    else:
        self_named = first_heading(text)
    # Only an index.md's first paragraph is a description; prose in an ordinary
    # document was not written to be lifted into someone else's list.
    source_description = fm.description if fm is not None else None
    description, source, replaced = merged_description(source_description, path, prev)
    return Entry(
        label=chosen_label(self_named, prev, path.name),
        href=path.name,
        description=description,
        description_source=source,
        replaced_description=replaced,
    )


def entry_for_other_file(path: Path, prev: ExistingEntry | None) -> Entry:
    # Such a file carries nothing that could name or describe it, so both come
    # from the index or from nowhere.
    description = prev.description if prev is not None else None
    return Entry(
        label=chosen_label(None, prev, path.stem),
        href=path.name,
        description=description,
        description_source=None,
    )


def entry_text(label: str, href: str, description: str | None) -> str:
    """An entry as the index writes it, so it can be pasted back whole.

    An entry with no description gets no description position: quoting exists
    to make text recoverable, and there is none to recover.
    """
    written = f"[{label}]({href})"
    return written if description is None else f"{written}: {description}"


def placeholder_note(directory: Path, entry: Entry) -> str:
    """Where the description this entry is still missing belongs.

    A description is written where its subject lives -- a .md file's in its own
    frontmatter, a directory's in its own index.md, whether or not that file
    exists yet -- so that is what the note names. A file that can hold no text
    of its own is the exception: this index is the only place it can be
    described, so the note names the index and the member.
    """
    if entry.href.endswith("/"):
        home = directory / entry.member_name / "index.md"
        return f"{home}: no description -- write one as the paragraph below its H1"
    if entry.href.endswith(".md"):
        home = directory / entry.href
        return f"{home}: no description -- write one into its frontmatter"
    index_path = directory / "index.md"
    return (
        f"{index_path}: no description for {entry.href} -- the file carries none "
        "of its own, so write it here"
    )


def replacement_note(index_path: Path, entry: Entry) -> str:
    """Report a description the member displaced, quoting both strings.

    Which side moved is not knowable from one run -- an updated source and an
    edited index look identical from here -- so the note reports the two
    strings and stops there.
    """
    assert entry.replaced_description is not None, entry
    return (
        f"{index_path}: [{entry.label}]({entry.href}) now reads "
        f"'{entry.description}', where the list had '{entry.replaced_description}'"
    )


def collect_entries(
    directory: Path, body: IndexBody, include: list[str]
) -> tuple[list[Entry], list[str], list[str]]:
    """Entries for the managed list (sorted), plus (changed, gaps) notes."""
    index_path = directory / "index.md"
    # A pinned member is listed by hand, so the managed list leaves it out --
    # and must not resurrect it as a stale entry either.
    pinned_members = {
        member for line in body.pinned if (member := member_key(entry_href(line)))
    }
    seen: set[str] = set(pinned_members)

    keyed: list[tuple[str, str, Entry]] = []
    for child in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if child.name.startswith(".") or child.name == "index.md":
            continue
        if child.name in pinned_members:
            continue
        prev = body.entries.get(child.name)
        if child.is_dir():
            entry = entry_for_subdir(child, prev)
        elif child.suffix == ".md":
            entry = entry_for_md_file(child, prev)
        elif any(fnmatch(child.name, pattern) for pattern in include):
            entry = entry_for_other_file(child, prev)
        else:
            continue
        seen.add(child.name)
        keyed.append((entry.label.lower(), child.name.lower(), entry))

    changed: list[str] = []
    gaps: list[str] = []
    for key, prev in body.entries.items():
        if key in seen:
            continue
        member = member_key(prev.href)
        if member is not None and (directory / member).exists():
            # The member exists but falls outside the include set: another
            # agent put it here on purpose -- keep the entry as-is.
            entry = Entry(prev.label, prev.href, prev.description, None)
            keyed.append((entry.label.lower(), member.lower(), entry))
            continue
        # Either the member is gone or the href never named one at all. The
        # line is quoted whole: the index is the only place this description
        # lived, and the run is about to delete it.
        gaps.append(
            f"{index_path}: dropped stale entry "
            f"{entry_text(prev.label, prev.href, prev.description)}"
        )

    # The list is read, so it is ordered by what a reader sees; the filename
    # only settles a tie they cannot see at all.
    keyed.sort(key=lambda triple: (triple[0], triple[1]))
    entries = [entry for _, _, entry in keyed]
    changed.extend(
        replacement_note(index_path, entry)
        for entry in entries
        if entry.replaced_description is not None
    )
    gaps.extend(collision_notes(index_path, entries))
    return entries, changed, gaps


def collision_notes(index_path: Path, entries: list[Entry]) -> list[str]:
    """Report members left sharing a label once their suffix was dropped."""
    by_label: dict[str, list[str]] = {}
    for entry in entries:
        if entry.labelled_by_stem:
            by_label.setdefault(entry.label, []).append(entry.member_name)
    return [
        f"{index_path}: {' and '.join(members)} share the label '{label}'"
        for label, members in by_label.items()
        if len(members) > 1
    ]


def pinned_target_notes(directory: Path, pinned: list[str]) -> list[str]:
    """Report a pinned repository path that does not resolve.

    The generator deletes what it wrote and reports on what you wrote, so a
    broken pin is never removed. A target it cannot check -- a URL, a fragment
    -- is passed over rather than guessed at.
    """
    index_path = directory / "index.md"
    notes: list[str] = []
    for line in pinned:
        href = entry_href(line)
        if UNCHECKABLE_HREF_RE.match(href):
            continue
        target = href.split("#", 1)[0].split("?", 1)[0]
        if target and not (directory / target).exists():
            notes.append(f"{index_path}: pinned entry points at {target}, which is not there")
    return notes


def length_note(description: str | None, source: Path, cap: int) -> str | None:
    """Report a description over the cap, naming the file to shorten.

    Naming the source rather than the index that surfaced it is the point: the
    index is regenerated, so shortening it there would not stick.
    """
    if description is None or len(description) <= cap:
        return None
    return (
        f"{source}: description is {len(description)} characters, "
        f"over the {cap}-character cap"
    )


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


def render(title: str, description_lines: list[str], entries: list[Entry], pinned: list[str]) -> str:
    # The body is a run of blocks with one blank line between them, so an
    # absent block -- no description, an empty managed list -- leaves no gap.
    blocks: list[list[str]] = [[f"# {title}"]]
    if description_lines:
        blocks.append(list(description_lines))
    if entries:
        # Every entry has a description position: an empty one would hide the
        # gap from anyone reading the file.
        blocks.append(
            [
                f"- [{entry.label}]({entry.href}): {entry.description or TODO_MARKER}"
                for entry in entries
            ]
        )
    if pinned:
        blocks.append([PINNED_MARKER, *pinned])
    return "\n\n".join("\n".join(block) for block in blocks) + "\n"


def process_directory(directory: Path, options: Options) -> tuple[bool, list[str], list[str]]:
    """Regenerate directory/index.md in place. Returns (written, changed, gaps)."""
    assert directory.is_dir(), directory
    dir_name = directory.resolve().name  # Path(".").name is "" -- resolve first
    assert dir_name, directory
    changed: list[str] = []
    gaps: list[str] = []
    index_path = directory / "index.md"
    existed = index_path.is_file()

    if not existed:
        if options.refresh_only:
            return False, [], []
        if not options.create_always and not index_worthy(directory):
            return False, [], []

    body = IndexBody()
    if existed:
        text = index_path.read_text(encoding="utf-8")
        if parse_frontmatter(text) is not None:
            if not options.migrate:
                raise SystemExit(
                    f"error: {index_path} has frontmatter, and an index.md carries "
                    "none; rerun with --migrate to convert it"
                )
            body, notes = migrate_body(index_path, text)
            changed.extend(notes)
        else:
            parsed = parse_index_body(text)
            if parsed is None:
                raise unmergeable(index_path)
            body = parsed

    if body.title is not None:
        title = body.title  # hand-written from here on, whatever the directory is called
    else:
        title = dir_name
        if existed:
            # Declining to overwrite a chosen title is not declining to supply
            # a missing one: the parent's listing reads this heading.
            changed.append(f"{index_path}: H1 restored as '{dir_name}'")

    if not existed:
        gaps.append(f"{index_path}: created -- author its description")
    elif body.description is None:
        gaps.append(f"{index_path}: no description")

    entries, entry_changed, entry_gaps = collect_entries(directory, body, options.include)
    changed.extend(entry_changed)
    cap = options.max_desc_len
    own_note = length_note(body.description, index_path, cap)
    if own_note is not None:
        gaps.append(own_note)
    for entry in entries:
        if entry.description is None:
            gaps.append(placeholder_note(directory, entry))
        if entry.description_source is not None:
            note = length_note(entry.description, entry.description_source, cap)
            if note is not None:
                gaps.append(note)
    gaps.extend(entry_gaps)
    gaps.extend(pinned_target_notes(directory, body.pinned))

    index_path.write_text(
        render(title, body.description_lines, entries, body.pinned), encoding="utf-8"
    )
    return True, changed, gaps


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
    parser.add_argument(
        "--max-desc-len",
        type=int,
        default=DEFAULT_MAX_DESC_LEN,
        metavar="N",
        help="report any copied description longer than N characters; a "
        "description that lives only in the index it is displayed in is exempt "
        f"(default: {DEFAULT_MAX_DESC_LEN})",
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="convert an index.md carrying frontmatter to plain markdown; the "
        "body wins, the frontmatter filling in only what the body lacks, and "
        "whatever it does not contribute is reported and discarded",
    )
    args = parser.parse_args()
    directory: Path = args.directory
    if not directory.is_dir():
        raise SystemExit(f"error: not a directory: {directory}")

    options = Options(
        include=args.include,
        create_always=not args.recursive or args.no_strict,
        refresh_only=args.refresh_only,
        migrate=args.migrate,
        max_desc_len=args.max_desc_len,
    )
    targets = list(iter_dirs_bottom_up(directory)) if args.recursive else [directory]
    changed: list[str] = []
    gaps: list[str] = []
    written = 0
    for target in targets:
        wrote, target_changed, target_gaps = process_directory(target, options)
        written += int(wrote)
        changed.extend(target_changed)
        gaps.extend(target_gaps)

    noun = "directory" if written == 1 else "directories"
    skipped = len(targets) - written
    summary = f"indexed {written} {noun}"
    if skipped:
        summary += f", skipped {skipped} with nothing index-worthy (--no-strict overrides)"
    print(summary)
    if changed:
        print("changed:")
        for note in changed:
            print(f"  {note}")
    if gaps:
        print("needs attention:")
        for gap in gaps:
            print(f"  {gap}")


if __name__ == "__main__":
    main()
