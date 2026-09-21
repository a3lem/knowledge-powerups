#!/usr/bin/env python3
"""Behaviour tests for generate_index.py.

Run from this directory so that `import generate_index` resolves:

    cd cli && python3 -m unittest test_generate_index -v

Every test method names the spec statement it encodes on its first line. The
statements live in plugins/index-md/docs/specs/directory-index.md, with the
in-flight changes in
plugins/index-md/docs/specs/directory-index.md.
These tests encode the TARGET behaviour: the reference spec with that delta
applied.
"""

from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
from collections.abc import Iterable, Iterator
from pathlib import Path
from unittest import mock

import generate_index

TODO = "<!-- to-do -->"
PINNED = "<!-- pinned -->"


@contextlib.contextmanager
def quiet_stderr() -> Iterator[None]:
    """Swallow argparse's usage message while a flag is still unimplemented."""
    with contextlib.redirect_stderr(io.StringIO()):
        yield

ENTRY_RE = re.compile(
    r"^[-*]\s+\[(?P<label>.+?)\]\((?P<href>[^()]*)\)(?:\s*:\s*(?P<desc>.*\S))?\s*$"
)


class GeneratorTestCase(unittest.TestCase):
    """A temporary tree, a way to run the generator over it, and readers."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root: Path = Path(tmp.name).resolve()

    # -- fixtures ---------------------------------------------------------

    def write_tree(self, tree: dict[str, str | None]) -> None:
        """Write a file tree. A None value (or a key ending in /) is a directory."""
        for relative, content in tree.items():
            target = self.root / relative
            if content is None or relative.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")

    def path(self, relative: str) -> Path:
        return self.root / relative

    # -- running ----------------------------------------------------------

    def run_generator(self, target: str, *flags: str) -> str:
        """Run the generator over root/target. Returns the report on stdout."""
        argv = ["generate_index.py", str(self.root / target), *flags]
        captured = io.StringIO()
        with mock.patch.object(sys, "argv", argv):
            with contextlib.redirect_stdout(captured):
                generate_index.main()
        return captured.getvalue()

    def run_generator_expecting_exit(self, target: str, *flags: str) -> str:
        """Run the generator expecting a fatal error. Returns the error message."""
        argv = ["generate_index.py", str(self.root / target), *flags]
        captured = io.StringIO()
        with mock.patch.object(sys, "argv", argv):
            with contextlib.redirect_stdout(captured):
                with self.assertRaises(SystemExit) as raised:
                    generate_index.main()
        return str(raised.exception)

    # -- reading back -----------------------------------------------------

    def read(self, relative: str) -> str:
        return (self.root / relative).read_text(encoding="utf-8")

    def entries(self, relative: str) -> dict[str, tuple[str, str | None]]:
        """href -> (label, description) for every entry line in the file."""
        found: dict[str, tuple[str, str | None]] = {}
        for line in self.read(relative).splitlines():
            match = ENTRY_RE.match(line.strip())
            if match is not None:
                found[match.group("href")] = (
                    match.group("label"),
                    match.group("desc"),
                )
        return found

    def entry(self, relative: str, href: str) -> tuple[str, str | None]:
        found = self.entries(relative)
        self.assertIn(href, found, f"no entry for {href!r} in {relative}")
        return found[href]

    def assertFileText(self, relative: str, expected: str) -> None:
        self.assertEqual(self.read(relative), expected)

    def assertHrefs(self, relative: str, expected: Iterable[str]) -> None:
        self.assertEqual(sorted(self.entries(relative)), sorted(expected))

    def entry_lines(self, relative: str) -> list[str]:
        """Every entry line in the file, in the order it is written."""
        return [
            line
            for line in self.read(relative).splitlines()
            if ENTRY_RE.match(line.strip()) is not None
        ]

    def labels_in_order(self, relative: str) -> list[str]:
        labels: list[str] = []
        for line in self.entry_lines(relative):
            match = ENTRY_RE.match(line.strip())
            assert match is not None
            labels.append(match.group("label"))
        return labels

    def hrefs_in_order(self, relative: str) -> list[str]:
        hrefs: list[str] = []
        for line in self.entry_lines(relative):
            match = ENTRY_RE.match(line.strip())
            assert match is not None
            hrefs.append(match.group("href"))
        return hrefs


def md(title: str | None = None, description: str | None = None, body: str = "") -> str:
    """An ordinary .md file, with optional frontmatter."""
    parts: list[str] = []
    if title is not None or description is not None:
        parts.append("---")
        if title is not None:
            parts.append(f"title: {title}")
        if description is not None:
            parts.append(f"description: {description}")
        parts.append("---")
        parts.append("")
    if body:
        parts.append(body.rstrip("\n"))
    return "\n".join(parts).rstrip("\n") + "\n"


# =====================================================================
# Group A -- statements the delta changes or adds
# =====================================================================


class IndexDocumentFormat(GeneratorTestCase):
    def test_a_created_index_carries_no_frontmatter(self) -> None:
        # spec: er5xx (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md("Alpha", "the alpha file")})
        self.run_generator("docs")
        text = self.read("docs/index.md")
        self.assertFalse(
            text.lstrip().startswith("---"), f"index.md opens with frontmatter:\n{text}"
        )

    def test_a_regenerated_index_carries_no_frontmatter(self) -> None:
        # spec: er5xx (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": "# docs\n\n- [Alpha](alpha.md): the alpha file\n",
            }
        )
        self.run_generator("docs")
        self.assertFalse(self.read("docs/index.md").lstrip().startswith("---"))

    def test_body_is_h1_then_list_when_there_is_no_description(self) -> None:
        # spec: r6han (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md("Alpha", "the alpha file")})
        self.run_generator("docs")
        self.assertFileText(
            "docs/index.md",
            "# docs\n\n- [Alpha](alpha.md): the alpha file\n",
        )

    def test_description_paragraph_sits_between_the_h1_and_the_list(self) -> None:
        # spec: r6han (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "Project documentation and specs.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        self.run_generator("docs")
        self.assertFileText(
            "docs/index.md",
            "# docs\n"
            "\n"
            "Project documentation and specs.\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n",
        )

    def test_a_pinned_marker_and_its_list_may_follow_the_managed_list(self) -> None:
        # spec: r6han (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Upstream](https://example.com/): the upstream project\n"
                ),
            }
        )
        self.run_generator("docs")
        text = self.read("docs/index.md")
        self.assertIn(PINNED, text)
        self.assertIn("- [Upstream](https://example.com/): the upstream project", text)
        self.assertLess(
            text.index("- [Alpha](alpha.md)"),
            text.index(PINNED),
            "the pinned marker must follow the managed list",
        )

    def test_an_entry_always_reads_label_href_colon_description(self) -> None:
        # spec: 2tsi8 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/bravo.md": md(body="# Bravo\n"),
                "docs/sub/index.md": "# Sub\n",
            }
        )
        self.run_generator("docs")
        lines = [
            line
            for line in self.read("docs/index.md").splitlines()
            if line.startswith("- ")
        ]
        self.assertEqual(len(lines), 3, lines)
        for line in lines:
            match = ENTRY_RE.match(line)
            self.assertIsNotNone(match, f"not an entry line: {line!r}")
            assert match is not None
            self.assertIsNotNone(
                match.group("desc"),
                f"entry written without a description position: {line!r}",
            )


class IndexHeading(GeneratorTestCase):
    def test_h1_is_the_directory_name_when_the_index_is_created(self) -> None:
        # spec: v2b9h (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md("Alpha", "the alpha file")})
        self.run_generator("docs")
        self.assertEqual(self.read("docs/index.md").splitlines()[0], "# docs")

    def test_a_hand_written_h1_is_never_touched_again(self) -> None:
        # spec: v2b9h (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": "# Project Documentation\n\n- [Alpha](alpha.md): the alpha file\n",
            }
        )
        self.run_generator("docs")
        self.assertEqual(
            self.read("docs/index.md").splitlines()[0], "# Project Documentation"
        )

    def test_a_missing_h1_is_restored_as_the_directory_name(self) -> None:
        # spec: iw1z3 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": "- [Alpha](alpha.md): the alpha file\n",
            }
        )
        self.run_generator("docs")
        self.assertFileText(
            "docs/index.md", "# docs\n\n- [Alpha](alpha.md): the alpha file\n"
        )

    def test_restoring_a_missing_h1_is_reported_under_changed(self) -> None:
        # spec: iw1z3 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": "- [Alpha](alpha.md): the alpha file\n",
            }
        )
        report = self.run_generator("docs")
        self.assertIn("changed:", report)
        self.assertIn(str(self.path("docs/index.md")), report)

    def test_an_h1_that_no_longer_matches_the_directory_name_is_left_alone(self) -> None:
        # spec: 054pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "wip/alpha.md": md("Alpha", "the alpha file"),
                "wip/index.md": "# Work in progress\n\n- [Alpha](alpha.md): the alpha file\n",
            }
        )
        self.run_generator("wip")
        self.assertFileText(
            "wip/index.md",
            "# Work in progress\n\n- [Alpha](alpha.md): the alpha file\n",
        )


class BodyValidation(GeneratorTestCase):
    def test_prose_after_the_list_is_a_fatal_error_naming_the_file(self) -> None:
        # spec: y5kyl (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    "And some trailing prose.\n"
                ),
            }
        )
        message = self.run_generator_expecting_exit("docs")
        self.assertIn(str(self.path("docs/index.md")), message)

    def test_a_section_heading_is_a_fatal_error_naming_the_file(self) -> None:
        # spec: y5kyl (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "## Specs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        message = self.run_generator_expecting_exit("docs")
        self.assertIn(str(self.path("docs/index.md")), message)

    def test_a_second_paragraph_is_a_fatal_error_naming_the_file(self) -> None:
        # spec: y5kyl (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "The first paragraph is the description.\n"
                    "\n"
                    "The second one is not allowed.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        message = self.run_generator_expecting_exit("docs")
        self.assertIn(str(self.path("docs/index.md")), message)

    def test_a_second_pinned_marker_is_a_fatal_error_naming_the_file(self) -> None:
        # spec: y5kyl (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Upstream](https://example.com/): the upstream project\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Mirror](https://example.org/): a mirror\n"
                ),
            }
        )
        message = self.run_generator_expecting_exit("docs")
        self.assertIn(str(self.path("docs/index.md")), message)

    def test_a_single_pinned_marker_is_accepted(self) -> None:
        # spec: y5kyl (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Upstream](https://example.com/): the upstream project\n"
                ),
            }
        )
        self.run_generator("docs")  # must not raise SystemExit

    def test_frontmatter_in_an_index_is_fatal_and_names_the_migrate_flag(self) -> None:
        # spec: s1lmg (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "---\n"
                    "title: docs\n"
                    "description: Project documentation.\n"
                    "---\n"
                    "\n"
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        message = self.run_generator_expecting_exit("docs")
        self.assertIn(str(self.path("docs/index.md")), message)
        self.assertIn("--migrate", message)


class SubdirectoryLabelAndDescription(GeneratorTestCase):
    def test_a_subdirectory_label_comes_from_the_h1_of_its_own_index(self) -> None:
        # spec: ht9j1 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/sub/index.md": "# Subsection\n"})
        self.run_generator("docs")
        label, _ = self.entry("docs/index.md", "sub/")
        self.assertEqual(label, "Subsection")

    def test_a_subdirectory_description_comes_from_its_first_paragraph(self) -> None:
        # spec: ht9j1 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {"docs/sub/index.md": "# Subsection\n\nAll about the subsection.\n"}
        )
        self.run_generator("docs")
        self.assertFileText(
            "docs/index.md",
            "# docs\n\n- [Subsection](sub/): All about the subsection.\n",
        )

    def test_a_directory_with_no_description_has_no_paragraph(self) -> None:
        # spec: ht9j1 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/sub/alpha.md": md("Alpha", "the alpha file")})
        self.run_generator("docs/sub")
        self.assertFileText(
            "docs/sub/index.md", "# sub\n\n- [Alpha](alpha.md): the alpha file\n"
        )

    def test_a_first_paragraph_is_not_a_description_outside_an_index(self) -> None:
        # spec: dmi28 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/notes.md": "# Notes\n\nProse that was never written as a description.\n"
            }
        )
        self.run_generator("docs")
        label, description = self.entry("docs/index.md", "notes.md")
        self.assertEqual(label, "Notes")
        self.assertEqual(description, TODO)


class DescriptionPlaceholder(GeneratorTestCase):
    def test_an_entry_with_no_description_gets_the_todo_placeholder(self) -> None:
        # spec: ltfx3 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md(body="# Alpha\n")})
        self.run_generator("docs")
        _, description = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(description, TODO)

    def test_a_subdirectory_with_no_description_gets_the_todo_placeholder(self) -> None:
        # spec: ltfx3 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/sub/index.md": "# Subsection\n"})
        self.run_generator("docs")
        _, description = self.entry("docs/index.md", "sub/")
        self.assertEqual(description, TODO)

    def test_nothing_beyond_the_placeholder_is_invented(self) -> None:
        # spec: 7fv84 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md(body="# Alpha\n")})
        self.run_generator("docs")
        self.assertFileText("docs/index.md", f"# docs\n\n- [Alpha](alpha.md): {TODO}\n")

    def test_the_placeholder_survives_regeneration_unchanged(self) -> None:
        # spec: yf2xo (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md(body="# Alpha\n")})
        self.run_generator("docs")
        self.run_generator("docs")
        self.assertFileText("docs/index.md", f"# docs\n\n- [Alpha](alpha.md): {TODO}\n")

    def test_the_placeholder_is_not_read_back_as_a_description(self) -> None:
        # spec: yf2xo (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md(body="# Alpha\n"),
                "docs/index.md": f"# docs\n\n- [Alpha](alpha.md): {TODO}\n",
            }
        )
        report = self.run_generator("docs")
        _, description = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(description, TODO)
        self.assertIn(
            "alpha.md",
            report,
            "an entry carrying the placeholder still has no description, "
            "so the run must report it as a gap",
        )

    def test_a_human_description_replaces_the_placeholder(self) -> None:
        # spec: yf2xo (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md(body="# Alpha\n"),
                "docs/index.md": "# docs\n\n- [Alpha](alpha.md): written by a human\n",
            }
        )
        self.run_generator("docs")
        _, description = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(description, "written by a human")


# =====================================================================
# Group B -- reference statements the delta leaves standing
# =====================================================================


class IndexFileLocation(GeneratorTestCase):
    def test_the_index_is_named_index_md_in_the_directory_it_describes(self) -> None:
        # spec: cy7d8 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md("Alpha", "the alpha file")})
        self.run_generator("docs")
        self.assertTrue(self.path("docs/index.md").is_file())
        self.assertFalse(self.path("index.md").exists())


class MembersListed(GeneratorTestCase):
    def test_a_subdirectory_is_listed_with_a_trailing_slash_href(self) -> None:
        # spec: gc28b (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/sub/index.md": "# Sub\n"})
        self.run_generator("docs")
        self.assertHrefs("docs/index.md", ["sub/"])

    def test_a_markdown_file_is_listed_under_its_filename(self) -> None:
        # spec: 0xe5b (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md("Alpha", "the alpha file")})
        self.run_generator("docs")
        self.assertHrefs("docs/index.md", ["alpha.md"])

    def test_another_file_is_not_listed_without_an_include_glob(self) -> None:
        # spec: zpon0 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {"docs/alpha.md": md("Alpha", "the alpha file"), "docs/diagram.png": "png"}
        )
        self.run_generator("docs")
        self.assertHrefs("docs/index.md", ["alpha.md"])

    def test_another_file_is_listed_when_an_include_glob_matches(self) -> None:
        # spec: zpon0 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {"docs/alpha.md": md("Alpha", "the alpha file"), "docs/diagram.png": "png"}
        )
        self.run_generator("docs", "--include", "*.png")
        self.assertHrefs("docs/index.md", ["alpha.md", "diagram.png"])

    def test_another_file_is_listed_when_it_already_appears_in_the_index(self) -> None:
        # spec: zpon0 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/run.sh": "#!/bin/sh\n",
                "docs/index.md": "# docs\n\n- [Release runner](run.sh): runs a release\n",
            }
        )
        self.run_generator("docs")
        self.assertIn("run.sh", self.entries("docs/index.md"))

    def test_dotfiles_and_the_index_itself_are_never_listed(self) -> None:
        # spec: cck6q (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/.hidden.md": md("Hidden", "should not be listed"),
                "docs/.cache/": None,
            }
        )
        self.run_generator("docs")
        self.assertHrefs("docs/index.md", ["alpha.md"])


class LabelSources(GeneratorTestCase):
    def test_a_markdown_label_prefers_the_frontmatter_title(self) -> None:
        # spec: w768b (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {"docs/alpha.md": md("From frontmatter", "d", body="# From heading\n")}
        )
        self.run_generator("docs")
        label, _ = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(label, "From frontmatter")

    def test_a_markdown_label_falls_back_to_the_first_h1(self) -> None:
        # spec: w768b (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": "# From heading\n"})
        self.run_generator("docs")
        label, _ = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(label, "From heading")

    def test_a_markdown_label_falls_back_to_the_filename(self) -> None:
        # spec: w768b (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": "just some text, no heading\n"})
        self.run_generator("docs")
        label, _ = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(label, "alpha.md")

    def test_name_is_a_lenient_alias_for_title(self) -> None:
        # spec: em1ax (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {"docs/alpha.md": "---\nname: Aliased\ndescription: the alpha file\n---\n"}
        )
        self.run_generator("docs")
        label, _ = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(label, "Aliased")


class DescriptionSources(GeneratorTestCase):
    def test_a_markdown_description_comes_from_its_frontmatter(self) -> None:
        # spec: 87rk6 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md("Alpha", "the alpha file")})
        self.run_generator("docs")
        _, description = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(description, "the alpha file")

    def test_a_members_own_description_wins_over_the_index(self) -> None:
        # spec: 2kbkz (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the authoritative description"),
                "docs/index.md": "# docs\n\n- [Alpha](alpha.md): the stale description\n",
            }
        )
        self.run_generator("docs")
        _, description = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(description, "the authoritative description")

    def test_a_description_that_exists_only_in_the_index_is_kept(self) -> None:
        # spec: irr1y (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha"),
                "docs/index.md": "# docs\n\n- [Alpha](alpha.md): written into the index\n",
            }
        )
        self.run_generator("docs")
        _, description = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(description, "written into the index")


class EntryLifetime(GeneratorTestCase):
    def test_an_entry_whose_member_still_exists_is_never_dropped(self) -> None:
        # spec: 33f4e (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/run.sh": "#!/bin/sh\n",
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "- [Release runner](run.sh): runs a release\n"
                ),
            }
        )
        self.run_generator("docs")  # no --include: run.sh is outside the include set
        _, description = self.entry("docs/index.md", "run.sh")
        self.assertEqual(description, "runs a release")

    def test_an_existing_index_is_always_regenerated(self) -> None:
        # spec: 1t1n1 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/bravo.md": md("Bravo", "the bravo file"),
                "docs/index.md": "# docs\n\n- [Alpha](alpha.md): the alpha file\n",
            }
        )
        self.run_generator("docs")
        self.assertHrefs("docs/index.md", ["alpha.md", "bravo.md"])


class CreationModes(GeneratorTestCase):
    def test_without_r_the_named_directory_gets_an_index(self) -> None:
        # spec: 6a8xt (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/notes.txt": "nothing index-worthy here\n"})
        self.run_generator("docs")
        self.assertTrue(self.path("docs/index.md").is_file())

    def test_with_r_every_subdirectory_is_processed(self) -> None:
        # spec: 6f4vl (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/one/alpha.md": md("Alpha", "the alpha file"),
                "docs/two/bravo.md": md("Bravo", "the bravo file"),
            }
        )
        self.run_generator("docs", "-r")
        self.assertTrue(self.path("docs/one/index.md").is_file())
        self.assertTrue(self.path("docs/two/index.md").is_file())
        self.assertTrue(self.path("docs/index.md").is_file())

    def test_with_r_an_unworthy_directory_gets_no_index(self) -> None:
        # spec: 6w3gg (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/sub/notes.txt": "nothing index-worthy here\n"})
        self.run_generator("docs", "-r")
        self.assertFalse(self.path("docs/sub/index.md").exists())
        self.assertFalse(self.path("docs/index.md").exists())

    def test_with_r_a_documented_markdown_file_makes_a_directory_worthy(self) -> None:
        # spec: 6w3gg (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/sub/alpha.md": md("Alpha", "the alpha file")})
        self.run_generator("docs", "-r")
        self.assertTrue(self.path("docs/sub/index.md").is_file())

    def test_with_r_a_title_without_a_description_is_not_worthy(self) -> None:
        # spec: 6w3gg (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/sub/alpha.md": md("Alpha")})
        self.run_generator("docs", "-r")
        self.assertFalse(self.path("docs/sub/index.md").exists())

    def test_worthiness_propagates_up_the_ancestor_chain(self) -> None:
        # spec: ijy2l (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/deep/deeper/alpha.md": md("Alpha", "the alpha file"),
                "docs/unrelated/notes.txt": "nothing index-worthy here\n",
            }
        )
        self.run_generator("docs", "-r")
        self.assertTrue(self.path("docs/deep/deeper/index.md").is_file())
        self.assertTrue(self.path("docs/deep/index.md").is_file())
        self.assertTrue(self.path("docs/index.md").is_file())
        self.assertFalse(self.path("docs/unrelated/index.md").exists())

    def test_no_strict_creates_an_index_in_every_directory(self) -> None:
        # spec: vcv98 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/sub/notes.txt": "nothing index-worthy here\n",
                "docs/empty/": None,
            }
        )
        self.run_generator("docs", "-r", "--no-strict")
        self.assertTrue(self.path("docs/index.md").is_file())
        self.assertTrue(self.path("docs/sub/index.md").is_file())
        self.assertTrue(self.path("docs/empty/index.md").is_file())

    def test_refresh_only_regenerates_but_never_creates(self) -> None:
        # spec: u417b (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": "# docs\n",
                "docs/sub/bravo.md": md("Bravo", "the bravo file"),
            }
        )
        self.run_generator("docs", "-r", "--refresh-only")
        self.assertFalse(self.path("docs/sub/index.md").exists())
        self.assertIn("alpha.md", self.entries("docs/index.md"))


class Reporting(GeneratorTestCase):
    def test_the_run_reports_how_many_directories_it_indexed(self) -> None:
        # spec: 871yq (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md("Alpha", "the alpha file")})
        report = self.run_generator("docs")
        self.assertRegex(report, r"indexed 1 director")

    def test_the_run_reports_how_many_directories_it_skipped_as_unworthy(self) -> None:
        # spec: 871yq (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/unrelated/notes.txt": "nothing index-worthy here\n",
            }
        )
        report = self.run_generator("docs", "-r")
        self.assertRegex(report, r"indexed 1 director")
        self.assertRegex(report, r"skipped 1")


# =====================================================================
# Group C -- round 2: labels, ordering, the length cap, the pinned
# block's semantics, and --migrate
# =====================================================================


def blob(length: int) -> str:
    """A description exactly `length` characters long."""
    return "x" * length


def cap_notes(report: str) -> list[str]:
    """Every over-the-cap note in a run's report."""
    return [
        note
        for note in report_sections(report)["needs attention"]
        if "character cap" in note
    ]


class LabelMerging(GeneratorTestCase):
    def test_a_hand_written_label_survives_when_the_member_does_not_name_itself(
        self,
    ) -> None:
        # spec: 24inj (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/notes.md": "just some text, no frontmatter and no heading\n",
                "docs/index.md": "# docs\n\n- [Field notes](notes.md): notes from the field\n",
            }
        )
        self.run_generator("docs")
        label, _ = self.entry("docs/index.md", "notes.md")
        self.assertEqual(label, "Field notes")

    def test_a_hand_written_label_survives_repeated_runs(self) -> None:
        # spec: 24inj (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/notes.md": "just some text, no frontmatter and no heading\n",
                "docs/index.md": "# docs\n\n- [Field notes](notes.md): notes from the field\n",
            }
        )
        self.run_generator("docs")
        self.run_generator("docs")
        self.assertFileText(
            "docs/index.md",
            "# docs\n\n- [Field notes](notes.md): notes from the field\n",
        )

    def test_a_frontmatter_title_wins_over_the_label_in_the_index(self) -> None:
        # spec: 24inj (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("From frontmatter", "the alpha file"),
                "docs/index.md": "# docs\n\n- [Stale label](alpha.md): the alpha file\n",
            }
        )
        self.run_generator("docs")
        label, _ = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(label, "From frontmatter")

    def test_a_first_h1_wins_over_the_label_in_the_index(self) -> None:
        # spec: 24inj (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": "# From heading\n",
                "docs/index.md": "# docs\n\n- [Stale label](alpha.md): the alpha file\n",
            }
        )
        self.run_generator("docs")
        label, _ = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(label, "From heading")

    def test_a_hand_written_label_survives_an_include_glob(self) -> None:
        # spec: 24inj (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/diagram.png": "png",
                "docs/index.md": "# docs\n\n- [Architecture diagram](diagram.png): how the pieces fit\n",
            }
        )
        self.run_generator("docs", "--include", "*.png")
        label, _ = self.entry("docs/index.md", "diagram.png")
        self.assertEqual(label, "Architecture diagram")

    def test_the_release_runner_label_is_not_reset_to_its_filename(self) -> None:
        # spec: 24inj (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/run.sh": "#!/bin/sh\n",
                "docs/index.md": "# docs\n\n- [Release runner](run.sh): runs a release\n",
            }
        )
        self.run_generator("docs", "--include", "*.sh")
        self.assertFileText(
            "docs/index.md",
            "# docs\n\n- [Release runner](run.sh): runs a release\n",
        )

    def test_a_subdirectory_h1_wins_over_the_label_in_the_index(self) -> None:
        # spec: 24inj (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/sub/index.md": "# Subsection\n",
                "docs/index.md": "# docs\n\n- [Stale label](sub/): about the sub\n",
            }
        )
        self.run_generator("docs")
        label, _ = self.entry("docs/index.md", "sub/")
        self.assertEqual(label, "Subsection")

    def test_a_subdirectory_without_an_index_keeps_the_label_in_the_index(self) -> None:
        # spec: 24inj (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/sub/notes.txt": "nothing index-worthy here\n",
                "docs/index.md": "# docs\n\n- [Loose material](sub/): odds and ends\n",
            }
        )
        self.run_generator("docs")
        label, _ = self.entry("docs/index.md", "sub/")
        self.assertEqual(label, "Loose material")


class NonMarkdownLabels(GeneratorTestCase):
    def test_a_non_markdown_label_drops_the_last_suffix(self) -> None:
        # spec: 8yx76 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/diagram.png": "png"})
        self.run_generator("docs", "--include", "*.png")
        label, _ = self.entry("docs/index.md", "diagram.png")
        self.assertEqual(label, "diagram")

    def test_only_the_last_suffix_is_dropped(self) -> None:
        # spec: 8yx76 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/data.tar.gz": "archive"})
        self.run_generator("docs", "--include", "*.gz")
        label, _ = self.entry("docs/index.md", "data.tar.gz")
        self.assertEqual(label, "data.tar")

    def test_a_name_with_no_suffix_is_used_unchanged(self) -> None:
        # spec: 8yx76 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/Makefile": "all:\n"})
        self.run_generator("docs", "--include", "Makefile")
        label, _ = self.entry("docs/index.md", "Makefile")
        self.assertEqual(label, "Makefile")

    def test_labels_that_collide_once_the_suffix_is_dropped_are_reported(self) -> None:
        # spec: 8yx76 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/chart.png": "png", "docs/chart.csv": "a,b\n"})
        report = self.run_generator(
            "docs", "--include", "*.png", "--include", "*.csv"
        )
        self.assertIn("chart.png", report)
        self.assertIn("chart.csv", report)

    def test_colliding_labels_are_still_both_listed(self) -> None:
        # spec: 8yx76 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/chart.png": "png", "docs/chart.csv": "a,b\n"})
        self.run_generator("docs", "--include", "*.png", "--include", "*.csv")
        self.assertHrefs("docs/index.md", ["chart.png", "chart.csv"])

    def test_two_non_colliding_labels_are_not_reported(self) -> None:
        # spec: 8yx76 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/chart.png": "png", "docs/table.csv": "a,b\n"})
        report = self.run_generator(
            "docs", "--include", "*.png", "--include", "*.csv"
        )
        # Both members are still named by their own placeholder gaps [8rs97],
        # so silence is not the test. A collision names both at once: that is
        # the note that must not be here.
        self.assertEqual(
            [
                line
                for line in report.splitlines()
                if "chart.png" in line and "table.csv" in line
            ],
            [],
            report,
        )


class EntryOrdering(GeneratorTestCase):
    def test_entries_are_sorted_by_label_not_by_filename(self) -> None:
        # spec: 1ny6c (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Zebra", "the last one alphabetically"),
                "docs/zulu.md": md("Apple", "the first one alphabetically"),
            }
        )
        self.run_generator("docs")
        self.assertEqual(self.labels_in_order("docs/index.md"), ["Apple", "Zebra"])

    def test_label_sorting_ignores_case(self) -> None:
        # spec: 1ny6c (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/b.md": md("apple", "lowercase a"),
                "docs/a.md": md("Banana", "uppercase b"),
                "docs/c.md": md("cherry", "lowercase c"),
            }
        )
        self.run_generator("docs")
        self.assertEqual(
            self.labels_in_order("docs/index.md"), ["apple", "Banana", "cherry"]
        )

    def test_the_filename_breaks_a_tie_between_equal_labels(self) -> None:
        # spec: 1ny6c (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/zulu.md": md("Same name", "the zulu one"),
                "docs/alpha.md": md("Same name", "the alpha one"),
            }
        )
        self.run_generator("docs")
        self.assertEqual(
            self.hrefs_in_order("docs/index.md"), ["alpha.md", "zulu.md"]
        )

    def test_subdirectories_are_not_grouped_separately(self) -> None:
        # spec: 1ny6c (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/beta.md": md("Zebra", "the zebra file"),
                "docs/zzz/index.md": "# Beta\n\nthe beta directory\n",
            }
        )
        self.run_generator("docs")
        self.assertEqual(
            self.hrefs_in_order("docs/index.md"), ["alpha.md", "zzz/", "beta.md"]
        )

    def test_the_pinned_block_keeps_the_order_it_was_written_in(self) -> None:
        # spec: 1ny6c (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Zulu](https://example.com/zulu): the last one\n"
                    "- [Mike](https://example.com/mike): the middle one\n"
                    "- [Alfa](https://example.com/alfa): the first one\n"
                ),
            }
        )
        self.run_generator("docs")
        self.assertEqual(
            self.labels_in_order("docs/index.md"),
            ["Alpha", "Zulu", "Mike", "Alfa"],
        )


class DescriptionLengthCap(GeneratorTestCase):
    def test_a_long_member_description_is_reported_naming_the_member(self) -> None:
        # spec: y6yp7 (plugins/index-md/docs/specs/directory-index.md)
        long = blob(260)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", long),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {long}\n",
            }
        )
        report = self.run_generator("docs")
        self.assertIn(str(self.path("docs/alpha.md")), report)

    def test_a_long_member_description_is_still_written_into_the_index(self) -> None:
        # spec: y6yp7 (plugins/index-md/docs/specs/directory-index.md)
        long = blob(260)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", long),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {long}\n",
            }
        )
        self.run_generator("docs")
        self.assertFileText(
            "docs/index.md", f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {long}\n"
        )

    def test_a_long_description_is_never_fatal(self) -> None:
        # spec: y6yp7 (plugins/index-md/docs/specs/directory-index.md)
        long = blob(2000)
        self.write_tree({"docs/alpha.md": md("Alpha", long)})
        self.run_generator("docs")  # must not raise SystemExit
        self.assertTrue(self.path("docs/index.md").is_file())

    def test_a_long_paragraph_in_this_directorys_own_index_is_reported(self) -> None:
        # spec: y6yp7 (plugins/index-md/docs/specs/directory-index.md)
        long = blob(260)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": f"# docs\n\n{long}\n\n- [Alpha](alpha.md): the alpha file\n",
            }
        )
        report = self.run_generator("docs")
        self.assertIn(str(self.path("docs/index.md")), report)

    def test_a_long_subdirectory_paragraph_names_that_directorys_index(self) -> None:
        # spec: y6yp7 (plugins/index-md/docs/specs/directory-index.md)
        long = blob(260)
        self.write_tree(
            {
                "docs/sub/index.md": f"# Sub\n\n{long}\n",
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Sub](sub/): {long}\n",
            }
        )
        # Not recursive: docs/sub/index.md is never processed, so it can only be
        # named because its paragraph is the description that overran.
        report = self.run_generator("docs")
        self.assertIn(str(self.path("docs/sub/index.md")), report)

    def test_a_description_at_the_default_cap_is_not_reported(self) -> None:
        # spec: qp54q (plugins/index-md/docs/specs/directory-index.md)
        exact = blob(250)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", exact),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {exact}\n",
            }
        )
        report = self.run_generator("docs")
        self.assertNotIn(str(self.path("docs/alpha.md")), report)

    def test_a_description_one_over_the_default_cap_is_reported(self) -> None:
        # spec: qp54q (plugins/index-md/docs/specs/directory-index.md)
        over = blob(251)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", over),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {over}\n",
            }
        )
        report = self.run_generator("docs")
        self.assertIn(str(self.path("docs/alpha.md")), report)

    def test_max_desc_len_lowers_the_cap(self) -> None:
        # spec: qp54q (plugins/index-md/docs/specs/directory-index.md)
        short = blob(30)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", short),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {short}\n",
            }
        )
        with quiet_stderr():
            report = self.run_generator("docs", "--max-desc-len", "20")
        self.assertIn(str(self.path("docs/alpha.md")), report)

    def test_max_desc_len_raises_the_cap(self) -> None:
        # spec: qp54q (plugins/index-md/docs/specs/directory-index.md)
        long = blob(300)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", long),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {long}\n",
            }
        )
        with quiet_stderr():
            report = self.run_generator("docs", "--max-desc-len", "500")
        self.assertNotIn(str(self.path("docs/alpha.md")), report)

    def test_a_description_that_exists_only_in_the_index_is_exempt(self) -> None:
        # spec: kp37v (plugins/index-md/docs/specs/directory-index.md)
        # The member names itself but describes itself nowhere, so the only
        # possible author of this description is whoever typed it here.
        long = blob(260)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha"),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {long}\n",
            }
        )
        report = self.run_generator("docs")
        self.assertEqual(cap_notes(report), [])

    def test_an_exempt_description_is_still_written_back_in_full(self) -> None:
        # spec: kp37v (plugins/index-md/docs/specs/directory-index.md)
        # Exempting a description from the cap is not licence to rewrite it:
        # the text survives the first run whole and the second unchanged.
        long = blob(260)
        written = f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {long}\n"
        self.write_tree({"docs/alpha.md": md("Alpha"), "docs/index.md": written})
        self.run_generator("docs")
        self.assertFileText("docs/index.md", written)
        self.run_generator("docs")
        self.assertFileText("docs/index.md", written)

    def test_the_exemption_follows_provenance_not_length(self) -> None:
        # spec: kp37v (plugins/index-md/docs/specs/directory-index.md)
        # Same run, same directory, same length: the copied one is reported,
        # the index-only one is not.
        long = blob(260)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha"),
                "docs/beta.md": md("Beta", long),
                "docs/index.md": (
                    f"# docs\n"
                    f"\n"
                    f"The docs.\n"
                    f"\n"
                    f"- [Alpha](alpha.md): {long}\n"
                    f"- [Beta](beta.md): {long}\n"
                ),
            }
        )
        notes = cap_notes(self.run_generator("docs"))
        self.assertEqual(len(notes), 1, notes)
        self.assertIn(str(self.path("docs/beta.md")), notes[0])

    def test_a_low_max_desc_len_does_not_end_the_exemption(self) -> None:
        # spec: kp37v (plugins/index-md/docs/specs/directory-index.md)
        # The cap is a budget for copied text; an index-only description is
        # outside that budget at any setting.
        short = blob(60)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha"),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {short}\n",
            }
        )
        with quiet_stderr():
            report = self.run_generator("docs", "--max-desc-len", "20")
        self.assertEqual(cap_notes(report), [])


class PinnedBlockSemantics(GeneratorTestCase):
    def test_a_pinned_entry_is_copied_through_verbatim(self) -> None:
        # spec: e8wxq (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/bravo.md": md("Real Bravo", "the description the file claims"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Frozen Bravo](bravo.md): frozen wording\n"
                ),
            }
        )
        self.run_generator("docs")
        self.assertIn(
            "- [Frozen Bravo](bravo.md): frozen wording",
            self.read("docs/index.md").splitlines(),
        )

    def test_a_pinned_entry_is_never_relabelled_or_re_described(self) -> None:
        # spec: e8wxq (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/bravo.md": md("Real Bravo", "the description the file claims"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Frozen Bravo](bravo.md): frozen wording\n"
                ),
            }
        )
        self.run_generator("docs")
        text = self.read("docs/index.md")
        self.assertNotIn("Real Bravo", text)
        self.assertNotIn("the description the file claims", text)

    def test_a_pinned_entry_is_never_reordered_or_dropped(self) -> None:
        # spec: e8wxq (plugins/index-md/docs/specs/directory-index.md)
        pinned_lines = [
            "- [Zulu](https://example.com/zulu): the last one",
            "- [Mike](https://example.com/mike): the middle one",
            "- [Alfa](https://example.com/alfa): the first one",
        ]
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n" + "\n".join(pinned_lines) + "\n"
                ),
            }
        )
        self.run_generator("docs")
        text = self.read("docs/index.md")
        marker_at = text.splitlines().index(PINNED)
        self.assertEqual(text.splitlines()[marker_at + 1 :], pinned_lines)

    def test_a_pinned_member_is_left_out_of_the_managed_list(self) -> None:
        # spec: caa4b (plugins/index-md/docs/specs/directory-index.md)
        original = (
            "# docs\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n"
            "\n"
            f"{PINNED}\n"
            "- [Frozen Bravo](bravo.md): frozen wording\n"
        )
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/bravo.md": md("Real Bravo", "the description the file claims"),
                "docs/index.md": original,
            }
        )
        self.run_generator("docs")
        self.assertFileText("docs/index.md", original)

    def test_a_pinned_member_is_never_listed_twice(self) -> None:
        # spec: caa4b (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/bravo.md": md("Real Bravo", "the description the file claims"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Frozen Bravo](bravo.md): frozen wording\n"
                ),
            }
        )
        self.run_generator("docs")
        hrefs = self.hrefs_in_order("docs/index.md")
        self.assertEqual(hrefs.count("bravo.md"), 1, hrefs)

    def test_a_pinned_subdirectory_is_left_out_of_the_managed_list(self) -> None:
        # spec: caa4b (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/sub/index.md": "# Subsection\n\nAll about the subsection.\n",
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Frozen sub](sub/): frozen wording\n"
                ),
            }
        )
        self.run_generator("docs")
        hrefs = self.hrefs_in_order("docs/index.md")
        self.assertEqual(hrefs.count("sub/"), 1, hrefs)

    def test_a_pinned_entry_may_point_anywhere_and_is_not_rewritten(self) -> None:
        # spec: z9bzy (plugins/index-md/docs/specs/directory-index.md)
        original = (
            "# docs\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n"
            "\n"
            f"{PINNED}\n"
            "- [Frozen Bravo](bravo.md): frozen wording\n"
            "- [Outside](../outside/notes.md): a note elsewhere in the repo\n"
            "- [Upstream](https://example.com/): the upstream project\n"
        )
        self.write_tree(
            {
                "outside/notes.md": md("Notes", "a note elsewhere in the repo"),
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/bravo.md": md("Real Bravo", "the description the file claims"),
                "docs/index.md": original,
            }
        )
        self.run_generator("docs")
        self.assertFileText("docs/index.md", original)

    def test_a_pinned_entry_is_not_validated_against_the_include_set(self) -> None:
        # spec: z9bzy (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/diagram.png": "png",
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [The diagram](diagram.png): how the pieces fit\n"
                ),
            }
        )
        report = self.run_generator("docs")  # no --include for *.png
        self.assertIn(
            "- [The diagram](diagram.png): how the pieces fit",
            self.read("docs/index.md").splitlines(),
        )
        self.assertNotIn("diagram", report)

    def test_a_pinned_target_that_does_not_resolve_is_reported(self) -> None:
        # spec: 2fxrs (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Gone](missing.md): a file that is not there\n"
                ),
            }
        )
        report = self.run_generator("docs")
        self.assertIn("missing.md", report)

    def test_a_pinned_target_that_does_not_resolve_is_not_removed(self) -> None:
        # spec: 2fxrs (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Gone](missing.md): a file that is not there\n"
                ),
            }
        )
        self.run_generator("docs")
        self.assertIn(
            "- [Gone](missing.md): a file that is not there",
            self.read("docs/index.md").splitlines(),
        )

    def test_a_pinned_url_is_passed_over_in_silence(self) -> None:
        # spec: 2fxrs (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "The docs.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Upstream](https://example.com/nowhere): the upstream project\n"
                ),
            }
        )
        report = self.run_generator("docs")
        self.assertNotIn("example.com", report)

    def test_a_pinned_target_that_resolves_is_not_reported(self) -> None:
        # spec: 2fxrs (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "outside/notes.md": md("Notes", "a note elsewhere in the repo"),
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "The docs.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Outside](../outside/notes.md): a note elsewhere in the repo\n"
                ),
            }
        )
        report = self.run_generator("docs")
        self.assertNotIn("outside/notes.md", report)

    def test_prose_below_the_pinned_marker_is_fatal_naming_the_file(self) -> None:
        # spec: 3ibxv (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "\n"
                    "These links are kept by hand.\n"
                    "\n"
                    "- [Upstream](https://example.com/): the upstream project\n"
                ),
            }
        )
        message = self.run_generator_expecting_exit("docs")
        self.assertIn(str(self.path("docs/index.md")), message)

    def test_a_section_heading_below_the_pinned_marker_is_fatal(self) -> None:
        # spec: 3ibxv (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    f"{PINNED}\n"
                    "\n"
                    "## Elsewhere\n"
                    "\n"
                    "- [Upstream](https://example.com/): the upstream project\n"
                ),
            }
        )
        message = self.run_generator_expecting_exit("docs")
        self.assertIn(str(self.path("docs/index.md")), message)


class PinnedBlockWhitespace(GeneratorTestCase):
    """One blank line before the marker, none after it."""

    def test_one_blank_line_separates_the_managed_list_from_the_marker(self) -> None:
        # spec: r6han (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "\n"
                    "\n"
                    f"{PINNED}\n"
                    "\n"
                    "- [Upstream](https://example.com/): the upstream project\n"
                ),
            }
        )
        self.run_generator("docs")
        self.assertFileText(
            "docs/index.md",
            "# docs\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n"
            "\n"
            f"{PINNED}\n"
            "- [Upstream](https://example.com/): the upstream project\n",
        )

    def test_an_empty_managed_list_still_leaves_one_blank_line(self) -> None:
        # spec: r6han (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    f"{PINNED}\n"
                    "- [Frozen Alpha](alpha.md): frozen wording\n"
                ),
            }
        )
        self.run_generator("docs")
        self.assertFileText(
            "docs/index.md",
            f"# docs\n\n{PINNED}\n- [Frozen Alpha](alpha.md): frozen wording\n",
        )

    def test_the_pinned_block_round_trips_without_reflowing(self) -> None:
        # spec: r6han (plugins/index-md/docs/specs/directory-index.md)
        original = (
            "# docs\n"
            "\n"
            "Project documentation and specs.\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n"
            "\n"
            f"{PINNED}\n"
            "- [Upstream](https://example.com/): the upstream project\n"
        )
        self.write_tree(
            {"docs/alpha.md": md("Alpha", "the alpha file"), "docs/index.md": original}
        )
        self.run_generator("docs")
        self.run_generator("docs")
        self.assertFileText("docs/index.md", original)


class Migration(GeneratorTestCase):
    def test_migrate_turns_frontmatter_into_the_h1_and_paragraph(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "---\n"
                    "title: Project Documentation\n"
                    "description: Project documentation and specs.\n"
                    "---\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        with quiet_stderr():
            self.run_generator("docs", "--migrate")
        self.assertFileText(
            "docs/index.md",
            "# Project Documentation\n"
            "\n"
            "Project documentation and specs.\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n",
        )

    def test_migrate_reports_the_conversion_under_changed(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "---\n"
                    "title: Project Documentation\n"
                    "description: Project documentation and specs.\n"
                    "---\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        with quiet_stderr():
            report = self.run_generator("docs", "--migrate")
        self.assertIn("changed:", report)
        self.assertIn(str(self.path("docs/index.md")), report)

    def test_migrate_keeps_a_body_h1_that_repeats_the_frontmatter_title(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "---\n"
                    "title: Project Documentation\n"
                    "description: Project documentation and specs.\n"
                    "---\n"
                    "\n"
                    "# Project Documentation\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        with quiet_stderr():
            self.run_generator("docs", "--migrate")
        self.assertFileText(
            "docs/index.md",
            "# Project Documentation\n"
            "\n"
            "Project documentation and specs.\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n",
        )

    def test_migrate_with_only_a_title_leaves_no_paragraph(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "---\n"
                    "title: Project Documentation\n"
                    "---\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        with quiet_stderr():
            self.run_generator("docs", "--migrate")
        self.assertFileText(
            "docs/index.md",
            "# Project Documentation\n\n- [Alpha](alpha.md): the alpha file\n",
        )

    def test_migrate_with_only_a_description_restores_the_directory_name(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "---\n"
                    "description: Project documentation and specs.\n"
                    "---\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        with quiet_stderr():
            self.run_generator("docs", "--migrate")
        self.assertFileText(
            "docs/index.md",
            "# docs\n"
            "\n"
            "Project documentation and specs.\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n",
        )

    def test_migrating_and_refreshing_are_one_pass(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/bravo.md": md("Bravo", "the bravo file"),
                "docs/index.md": (
                    "---\n"
                    "title: Project Documentation\n"
                    "description: Project documentation and specs.\n"
                    "---\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        with quiet_stderr():
            self.run_generator("docs", "--migrate")
        self.assertFileText(
            "docs/index.md",
            "# Project Documentation\n"
            "\n"
            "Project documentation and specs.\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n"
            "- [Bravo](bravo.md): the bravo file\n",
        )

    def test_migrate_converts_every_index_it_processes(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        frontmatter_index = (
            "---\n"
            "title: Subsection\n"
            "description: All about the subsection.\n"
            "---\n"
        )
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": frontmatter_index,
                "docs/sub/bravo.md": md("Bravo", "the bravo file"),
                "docs/sub/index.md": frontmatter_index,
            }
        )
        with quiet_stderr():
            self.run_generator("docs", "-r", "--migrate")
        for relative in ("docs/index.md", "docs/sub/index.md"):
            self.assertFalse(
                self.read(relative).lstrip().startswith("---"),
                f"{relative} still carries frontmatter",
            )

    def test_migrate_leaves_a_file_without_frontmatter_alone(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        original = (
            "# Project Documentation\n"
            "\n"
            "Project documentation and specs.\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n"
        )
        self.write_tree(
            {"docs/alpha.md": md("Alpha", "the alpha file"), "docs/index.md": original}
        )
        with quiet_stderr():
            self.run_generator("docs", "--migrate")
        self.assertFileText("docs/index.md", original)

    def test_migrate_refuses_frontmatter_over_an_unmergeable_body(self) -> None:
        # spec: vew0l (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "---\n"
                    "title: Project Documentation\n"
                    "description: Project documentation and specs.\n"
                    "---\n"
                    "\n"
                    "## Specs\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        with quiet_stderr():
            message = self.run_generator_expecting_exit("docs", "--migrate")
        self.assertIn(str(self.path("docs/index.md")), message)

    def test_a_refused_migration_leaves_the_file_untouched(self) -> None:
        # spec: vew0l (plugins/index-md/docs/specs/directory-index.md)
        original = (
            "---\n"
            "title: Project Documentation\n"
            "description: Project documentation and specs.\n"
            "---\n"
            "\n"
            "## Specs\n"
            "\n"
            "- [Alpha](alpha.md): the alpha file\n"
        )
        self.write_tree(
            {"docs/alpha.md": md("Alpha", "the alpha file"), "docs/index.md": original}
        )
        with quiet_stderr():
            self.run_generator_expecting_exit("docs", "--migrate")
        self.assertFileText("docs/index.md", original)


# =====================================================================
# Group D -- round 3: the report's two sections
# =====================================================================


def report_sections(report: str) -> dict[str, list[str]]:
    """Split a run's report into its two sections, one note per line.

    The summary line sits above both sections and belongs to neither; every
    note is indented under the header that owns it.
    """
    sections: dict[str, list[str]] = {"changed": [], "needs attention": []}
    current: list[str] | None = None
    for line in report.splitlines():
        if not line.strip():
            continue
        stripped = line.rstrip()
        if stripped in ("changed:", "needs attention:"):
            current = sections[stripped[:-1]]
        elif line[0].isspace():
            assert current is not None, f"note outside any section: {line!r}"
            current.append(line.strip())
        else:
            current = None  # the summary line, which sits in neither section
    return sections


class ReportTestCase(GeneratorTestCase):
    """Assertions about which section a note lands in and what it says."""

    def changed(self, report: str) -> list[str]:
        return report_sections(report)["changed"]

    def gaps(self, report: str) -> list[str]:
        return report_sections(report)["needs attention"]

    def notes_mentioning(self, notes: list[str], *needles: str) -> list[str]:
        return [note for note in notes if all(needle in note for needle in needles)]

    def assertOneNote(self, notes: list[str], *needles: str) -> str:
        """The single note mentioning every needle. Returns it for further checks."""
        found = self.notes_mentioning(notes, *needles)
        self.assertEqual(
            len(found), 1, f"expected exactly one note mentioning {needles}, got {notes}"
        )
        return found[0]

    def assertNoNote(self, notes: list[str], *needles: str) -> None:
        self.assertEqual(
            self.notes_mentioning(notes, *needles),
            [],
            f"no note should mention {needles}",
        )

    def assertQuotes(self, note: str, text: str) -> None:
        """The note carries `text` in quotes, so where it starts and ends is visible."""
        self.assertTrue(
            f"'{text}'" in note or f'"{text}"' in note,
            f"{text!r} is not quoted in {note!r}",
        )


class ReportStructure(ReportTestCase):
    def test_a_run_with_nothing_to_say_prints_neither_section(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n\nProject documentation.\n\n- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        report = self.run_generator("docs")
        self.assertNotIn("changed:", report)
        self.assertNotIn("needs attention:", report)

    def test_changed_is_printed_before_needs_attention(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": "- [Alpha](alpha.md): the alpha file\n",
            }
        )
        report = self.run_generator("docs")
        self.assertIn("changed:", report)
        self.assertIn("needs attention:", report)
        self.assertLess(report.index("changed:"), report.index("needs attention:"))

    def test_no_note_appears_in_both_sections(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md(body="# Alpha\n"),
                "docs/index.md": (
                    f"- [Alpha](alpha.md): {TODO}\n- [Gone](gone.md): the gone file\n"
                ),
            }
        )
        report = self.run_generator("docs")
        both = set(self.changed(report)) & set(self.gaps(report))
        self.assertEqual(both, set(), f"notes in both sections: {sorted(both)}")

    def test_an_index_without_a_description_is_a_gap(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": "# docs\n\n- [Alpha](alpha.md): the alpha file\n",
            }
        )
        report = self.run_generator("docs")
        index = str(self.path("docs/index.md"))
        self.assertOneNote(self.gaps(report), index)
        self.assertNoNote(self.changed(report), index)

    def test_a_created_index_has_no_description_and_is_a_gap(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/alpha.md": md("Alpha", "the alpha file")})
        report = self.run_generator("docs")
        index = str(self.path("docs/index.md"))
        self.assertOneNote(self.gaps(report), index)
        self.assertNoNote(self.changed(report), index)

    def test_an_entry_still_carrying_the_placeholder_is_a_gap(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md(body="# Alpha\n"),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {TODO}\n",
            }
        )
        report = self.run_generator("docs")
        alpha = str(self.path("docs/alpha.md"))
        self.assertOneNote(self.gaps(report), alpha)
        self.assertNoNote(self.changed(report), alpha)

    def test_a_dropped_stale_entry_is_a_gap(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "The docs.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "- [Gone](gone.md): the gone file\n"
                ),
            }
        )
        report = self.run_generator("docs")
        self.assertOneNote(self.gaps(report), "gone.md")
        self.assertNoNote(self.changed(report), "gone.md")

    def test_a_description_over_the_cap_is_a_gap(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        long = blob(260)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", long),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {long}\n",
            }
        )
        report = self.run_generator("docs")
        alpha = str(self.path("docs/alpha.md"))
        self.assertOneNote(self.gaps(report), alpha)
        self.assertNoNote(self.changed(report), alpha)

    def test_a_colliding_label_is_a_gap(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/chart.png": "png", "docs/chart.csv": "a,b\n"})
        report = self.run_generator("docs", "--include", "*.png", "--include", "*.csv")
        self.assertOneNote(self.gaps(report), "chart.png", "chart.csv")
        self.assertNoNote(self.changed(report), "chart.png", "chart.csv")

    def test_a_collision_is_one_note_naming_both_members(self) -> None:
        # spec: 8yx76 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree({"docs/chart.png": "png", "docs/chart.csv": "a,b\n"})
        report = self.run_generator("docs", "--include", "*.png", "--include", "*.csv")
        note = self.assertOneNote(self.gaps(report), "chart.png", "chart.csv")
        self.assertIn("chart", note)

    def test_a_restored_h1_is_a_change_not_a_gap(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": "The docs.\n\n- [Alpha](alpha.md): the alpha file\n",
            }
        )
        report = self.run_generator("docs")
        self.assertOneNote(self.changed(report), "docs")
        self.assertNoNote(self.gaps(report), "H1")

    def test_a_migration_is_a_change_not_a_gap(self) -> None:
        # spec: wk9pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "---\n"
                    "title: Project documentation\n"
                    "description: Project documentation and specs.\n"
                    "---\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        report = self.run_generator("docs", "--migrate")
        self.assertOneNote(self.changed(report), str(self.path("docs/index.md")))
        self.assertNoNote(self.gaps(report), "frontmatter")


class ReplacedDescriptionReport(ReportTestCase):
    """A member's description replacing what the index carried. [w1j5d]"""

    def replaced(self) -> dict[str, str]:
        return {
            "docs/alpha.md": md("Alpha", "the new description"),
            "docs/index.md": (
                "# docs\n\nThe docs.\n\n- [Alpha](alpha.md): the old description\n"
            ),
        }

    def test_both_the_old_and_the_new_string_are_reported(self) -> None:
        # spec: w1j5d (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.replaced())
        report = self.run_generator("docs")
        note = self.assertOneNote(self.changed(report), "the old description")
        self.assertIn("the new description", note)

    def test_the_old_and_the_new_string_are_quoted(self) -> None:
        # spec: w1j5d (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.replaced())
        report = self.run_generator("docs")
        note = self.assertOneNote(self.changed(report), "the old description")
        self.assertQuotes(note, "the old description")
        self.assertQuotes(note, "the new description")

    def test_the_note_names_the_entry_it_is_about(self) -> None:
        # spec: w1j5d (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.replaced())
        report = self.run_generator("docs")
        note = self.assertOneNote(self.changed(report), "the old description")
        self.assertIn("alpha.md", note)

    def test_the_replacement_lands_under_changed_not_needs_attention(self) -> None:
        # spec: w1j5d (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.replaced())
        report = self.run_generator("docs")
        self.assertOneNote(self.changed(report), "the old description")
        self.assertNoNote(self.gaps(report), "the old description")

    def test_the_note_draws_no_conclusion_about_which_side_was_edited(self) -> None:
        # spec: w1j5d (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.replaced())
        report = self.run_generator("docs")
        note = self.assertOneNote(self.changed(report), "the old description").lower()
        # An updated source and a hand-edited index look the same from here, so
        # the note may not say that either one happened.
        for claim in (
            "hand-edited",
            "hand edited",
            "by hand",
            "hand-written",
            "you ",
            "outdated",
            "out of date",
            "stale",
            "wrong",
        ):
            self.assertNotIn(claim, note, f"the note claims too much: {note!r}")

    def test_a_subdirectory_paragraph_replacing_the_index_is_reported_the_same_way(
        self,
    ) -> None:
        # spec: w1j5d (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/sub/index.md": "# Sub\n\nthe new description\n",
                "docs/index.md": (
                    "# docs\n\nThe docs.\n\n- [Sub](sub/): the old description\n"
                ),
            }
        )
        report = self.run_generator("docs")
        note = self.assertOneNote(self.changed(report), "the old description")
        self.assertQuotes(note, "the new description")
        self.assertIn("sub/", note)

    def test_an_unchanged_description_is_not_reported(self) -> None:
        # spec: w1j5d (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n\nThe docs.\n\n- [Alpha](alpha.md): the alpha file\n"
                ),
            }
        )
        report = self.run_generator("docs")
        self.assertEqual(self.changed(report), [])

    def test_filling_an_entry_that_had_no_description_is_not_a_replacement(self) -> None:
        # spec: w1j5d (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": "# docs\n\nThe docs.\n\n- [Alpha](alpha.md)\n",
            }
        )
        report = self.run_generator("docs")
        self.assertEqual(self.changed(report), [])

    def test_filling_a_placeholder_is_not_a_replacement(self) -> None:
        # spec: w1j5d (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": f"# docs\n\nThe docs.\n\n- [Alpha](alpha.md): {TODO}\n",
            }
        )
        report = self.run_generator("docs")
        self.assertEqual(self.changed(report), [])


class PlaceholderReport(ReportTestCase):
    """Every entry still carrying the placeholder, and where to write it. [8rs97]"""

    def mixed_tree(self) -> dict[str, str]:
        return {
            "docs/alpha.md": md(body="# Alpha\n"),
            "docs/chart.png": "png",
            "docs/sub/index.md": "# Sub\n",
            "docs/index.md": "# docs\n\nThe docs.\n",
        }

    def test_a_markdown_files_placeholder_points_at_its_frontmatter(self) -> None:
        # spec: 8rs97 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.mixed_tree())
        report = self.run_generator("docs", "--include", "*.png")
        note = self.assertOneNote(self.gaps(report), str(self.path("docs/alpha.md")))
        self.assertIn("frontmatter", note.lower())

    def test_a_subdirectorys_placeholder_points_at_its_own_index(self) -> None:
        # spec: 8rs97 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.mixed_tree())
        report = self.run_generator("docs", "--include", "*.png")
        self.assertOneNote(self.gaps(report), str(self.path("docs/sub/index.md")))

    def test_a_subdirectory_without_an_index_still_points_at_one(self) -> None:
        # spec: 8rs97 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/sub/notes.txt": "loose notes\n",
                "docs/index.md": "# docs\n\nThe docs.\n",
            }
        )
        report = self.run_generator("docs")
        self.assertOneNote(self.gaps(report), str(self.path("docs/sub/index.md")))

    def test_another_files_placeholder_points_at_this_index(self) -> None:
        # spec: 8rs97 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.mixed_tree())
        report = self.run_generator("docs", "--include", "*.png")
        # The file cannot carry a description, so the index is where it belongs.
        self.assertOneNote(
            self.gaps(report), str(self.path("docs/index.md")), "chart.png"
        )

    def test_every_placeholder_is_reported_whatever_the_file_type(self) -> None:
        # spec: 8rs97 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.mixed_tree())
        report = self.run_generator("docs", "--include", "*.png")
        gaps = self.gaps(report)
        self.assertOneNote(gaps, str(self.path("docs/alpha.md")))
        self.assertOneNote(gaps, str(self.path("docs/sub/index.md")))
        self.assertOneNote(gaps, "chart.png")

    def test_the_placeholder_itself_stays_uniform(self) -> None:
        # spec: 8rs97 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.mixed_tree())
        self.run_generator("docs", "--include", "*.png")
        self.assertEqual(
            self.entry_lines("docs/index.md"),
            [
                f"- [Alpha](alpha.md): {TODO}",
                f"- [chart](chart.png): {TODO}",
                f"- [Sub](sub/): {TODO}",
            ],
        )

    def test_a_described_entry_is_not_reported_as_a_placeholder(self) -> None:
        # spec: 8rs97 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/chart.png": "png",
                "docs/index.md": (
                    "# docs\n\nThe docs.\n\n- [chart](chart.png): the quarterly chart\n"
                ),
            }
        )
        report = self.run_generator("docs", "--include", "*.png")
        self.assertNoNote(self.gaps(report), "chart.png")


class StaleEntryReport(ReportTestCase):
    """A dropped entry is quoted in full, so its description survives. [f0lcv]"""

    def test_a_dropped_entry_is_reported_with_its_full_text(self) -> None:
        # spec: f0lcv (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "The docs.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "- [Gone](gone.md): what the gone file used to say\n"
                ),
            }
        )
        report = self.run_generator("docs")
        note = self.assertOneNote(self.gaps(report), "gone.md")
        self.assertIn("[Gone](gone.md): what the gone file used to say", note)

    def test_a_dropped_subdirectory_entry_is_reported_with_its_full_text(self) -> None:
        # spec: f0lcv (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "The docs.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "- [Old Section](old/): everything the old section held\n"
                ),
            }
        )
        report = self.run_generator("docs")
        note = self.assertOneNote(self.gaps(report), "old/")
        self.assertIn("[Old Section](old/): everything the old section held", note)

    def test_each_dropped_entry_is_reported_with_its_own_text(self) -> None:
        # spec: f0lcv (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "The docs.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "- [One](one.md): the first gone file\n"
                    "- [Two](two.md): the second gone file\n"
                ),
            }
        )
        report = self.run_generator("docs")
        gaps = self.gaps(report)
        self.assertIn("[One](one.md): the first gone file", self.assertOneNote(gaps, "one.md"))
        self.assertIn("[Two](two.md): the second gone file", self.assertOneNote(gaps, "two.md"))

    def test_a_description_written_only_in_the_index_does_not_save_the_entry(self) -> None:
        # spec: f0lcv (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "The docs.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "- [Gone](gone.md): a description nobody else holds\n"
                ),
            }
        )
        report = self.run_generator("docs")
        self.assertNotIn("gone.md", self.read("docs/index.md"))
        note = self.assertOneNote(self.gaps(report), "gone.md")
        self.assertIn("a description nobody else holds", note)

    def test_a_dropped_entry_names_the_index_it_was_dropped_from(self) -> None:
        # spec: f0lcv (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "The docs.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "- [Gone](gone.md): what the gone file used to say\n"
                ),
            }
        )
        report = self.run_generator("docs")
        note = self.assertOneNote(self.gaps(report), "gone.md")
        self.assertIn(str(self.path("docs/index.md")), note)


class NonMemberEntry(ReportTestCase):
    """Above the marker an entry names a direct member of this directory.

    One path segment, with a trailing slash for a directory. A path into a
    subdirectory, a `../` path and a URL are all links to something that is not
    a member, and resolving on disk does not make one a member: the managed
    list is an index of this directory's files, and anything else belongs in
    the pinned block. [k5zgu]
    """

    def index_with(self, *extra_lines: str) -> dict[str, str]:
        """A docs/ index listing alpha.md plus whatever else is passed in."""
        lines = ["- [Alpha](alpha.md): the alpha file", *extra_lines]
        return {
            "docs/alpha.md": md("Alpha", "the alpha file"),
            "docs/index.md": "# docs\n\nThe docs.\n\n" + "".join(f"{line}\n" for line in lines),
        }

    # -- a ../ path -------------------------------------------------------

    def test_a_parent_relative_path_is_dropped(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        tree = self.index_with("- [Other](../other/notes.md): lives elsewhere")
        tree["other/notes.md"] = md("Other", "lives elsewhere")
        self.write_tree(tree)
        self.run_generator("docs")
        self.assertHrefs("docs/index.md", ["alpha.md"])

    def test_a_parent_relative_path_is_dropped_though_it_resolves_on_disk(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        tree = self.index_with("- [Other](../other/notes.md): lives elsewhere")
        tree["other/notes.md"] = md("Other", "lives elsewhere")
        self.write_tree(tree)
        self.run_generator("docs")
        self.assertTrue(self.path("other/notes.md").exists(), "the target is still there")
        self.assertNotIn("../other/notes.md", self.read("docs/index.md"))

    def test_a_dropped_parent_relative_path_is_reported_with_its_full_text(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        tree = self.index_with("- [Other](../other/notes.md): lives elsewhere")
        tree["other/notes.md"] = md("Other", "lives elsewhere")
        self.write_tree(tree)
        report = self.run_generator("docs")
        note = self.assertOneNote(self.gaps(report), "../other/notes.md")
        self.assertIn("[Other](../other/notes.md): lives elsewhere", note)
        self.assertIn(str(self.path("docs/index.md")), note)

    # -- a path into a subdirectory ---------------------------------------

    def subdirectory_tree(self) -> dict[str, str]:
        tree = self.index_with("- [Deep](sub/deep.md): two segments down")
        tree["docs/sub/deep.md"] = md("Deep", "the deep file")
        tree["docs/sub/index.md"] = "# sub\n\nthe sub directory\n"
        return tree

    def test_a_path_into_a_subdirectory_is_dropped(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.subdirectory_tree())
        self.run_generator("docs")
        self.assertHrefs("docs/index.md", ["alpha.md", "sub/"])

    def test_the_subdirectory_itself_is_still_listed_as_a_member(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.subdirectory_tree())
        self.run_generator("docs")
        label, description = self.entry("docs/index.md", "sub/")
        self.assertEqual(label, "sub")
        self.assertEqual(description, "the sub directory")

    def test_a_dropped_subdirectory_path_is_reported_with_its_full_text(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.subdirectory_tree())
        report = self.run_generator("docs")
        note = self.assertOneNote(self.gaps(report), "sub/deep.md")
        self.assertIn("[Deep](sub/deep.md): two segments down", note)
        self.assertIn(str(self.path("docs/index.md")), note)

    # -- a URL ------------------------------------------------------------

    def test_a_url_above_the_marker_is_dropped(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.index_with("- [Upstream](https://example.com/): a url"))
        self.run_generator("docs")
        self.assertHrefs("docs/index.md", ["alpha.md"])

    def test_a_dropped_url_is_reported_with_its_full_text(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.index_with("- [Upstream](https://example.com/): a url"))
        report = self.run_generator("docs")
        note = self.assertOneNote(self.gaps(report), "https://example.com/")
        self.assertIn("[Upstream](https://example.com/): a url", note)

    # -- a member, which is what the list is for --------------------------

    def test_a_bare_member_that_exists_is_kept(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.index_with())
        report = self.run_generator("docs")
        _, description = self.entry("docs/index.md", "alpha.md")
        self.assertEqual(description, "the alpha file")
        self.assertNoNote(self.gaps(report), "alpha.md")

    def test_a_directory_member_with_its_trailing_slash_is_kept(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        tree = self.index_with("- [sub](sub/): the sub directory")
        tree["docs/sub/index.md"] = "# sub\n\nthe sub directory\n"
        self.write_tree(tree)
        report = self.run_generator("docs")
        _, description = self.entry("docs/index.md", "sub/")
        self.assertEqual(description, "the sub directory")
        self.assertNoNote(self.gaps(report), "sub/")

    def test_a_member_outside_the_include_set_survives_beside_a_dropped_non_member(
        self,
    ) -> None:
        # spec: 33f4e (plugins/index-md/docs/specs/directory-index.md)
        tree = self.index_with(
            "- [Release runner](run.sh): runs a release",
            "- [Other](../other/notes.md): lives elsewhere",
        )
        tree["docs/run.sh"] = "#!/bin/sh\n"
        tree["other/notes.md"] = md("Other", "lives elsewhere")
        self.write_tree(tree)
        report = self.run_generator("docs")  # no --include: run.sh is outside the set
        _, description = self.entry("docs/index.md", "run.sh")
        self.assertEqual(description, "runs a release")
        self.assertNoNote(self.gaps(report), "run.sh")
        self.assertOneNote(self.gaps(report), "../other/notes.md")

    # -- the pinned block is the place for everything else ----------------

    def test_a_pinned_non_member_is_kept_while_a_managed_one_is_dropped(self) -> None:
        # spec: k5zgu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "other/notes.md": md("Other", "lives elsewhere"),
                "other/legacy.md": md("Legacy", "also lives elsewhere"),
                "docs/index.md": (
                    "# docs\n"
                    "\n"
                    "The docs.\n"
                    "\n"
                    "- [Alpha](alpha.md): the alpha file\n"
                    "- [Legacy](../other/legacy.md): above the marker\n"
                    "\n"
                    f"{PINNED}\n"
                    "\n"
                    "- [Other](../other/notes.md): below the marker\n"
                ),
            }
        )
        report = self.run_generator("docs")
        text = self.read("docs/index.md")
        self.assertIn("- [Other](../other/notes.md): below the marker", text)
        self.assertNotIn("../other/legacy.md", text)
        self.assertOneNote(self.gaps(report), "../other/legacy.md")
        self.assertNoNote(self.gaps(report), "../other/notes.md")


class RenamedDirectoryReport(ReportTestCase):
    """A rename is a drop and an arrival, and the run says nothing more.

    A single run holds only the current parent index, so a renamed directory
    looks exactly like a stale entry beside a new one. The generator does not
    try to detect the rename: it reports the drop with its full text, which
    leaves the description recoverable, and ties nothing together. [054pu]
    """

    def renamed(self) -> dict[str, str]:
        return {
            "docs/howtos/index.md": "# Guides\n\nhow to do things\n",
            "docs/index.md": (
                "# docs\n\nThe docs.\n\n- [Guides](guides/): how to do things\n"
            ),
        }

    def test_a_renamed_directory_is_reported_as_a_plain_drop(self) -> None:
        # spec: f0lcv (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.renamed())
        report = self.run_generator("docs")
        note = self.assertOneNote(self.gaps(report), "guides/")
        self.assertIn("[Guides](guides/): how to do things", note)

    def test_no_note_ties_the_dropped_href_to_the_new_one(self) -> None:
        # spec: 054pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.renamed())
        report = self.run_generator("docs")
        # The shared title is exactly what a rename hint would have keyed on.
        # Nothing may claim the two hrefs are the same thing, in either section.
        self.assertNoNote(self.gaps(report), "guides/", "howtos")
        self.assertNoNote(self.changed(report), "guides/", "howtos")

    def test_no_rename_is_claimed_when_the_titles_differ(self) -> None:
        # spec: 054pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(
            {
                "docs/howtos/index.md": "# How-tos\n\nhow to do things\n",
                "docs/index.md": (
                    "# docs\n\nThe docs.\n\n- [Guides](guides/): how to do things\n"
                ),
            }
        )
        report = self.run_generator("docs")
        # The drop is still reported; what must not appear is a note tying the
        # two hrefs together, since nothing here says they are the same thing.
        self.assertOneNote(self.gaps(report), "guides/")
        self.assertNoNote(self.gaps(report), "guides/", "howtos")

    def test_a_rename_leaves_both_titles_alone(self) -> None:
        # spec: 054pu (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.renamed())
        self.run_generator("docs")
        self.assertEqual(self.read("docs/howtos/index.md").splitlines()[0], "# Guides")
        label, _ = self.entry("docs/index.md", "howtos/")
        self.assertEqual(label, "Guides")


# =====================================================================
# Group E -- round 6: --migrate, where the body wins
# =====================================================================


class MigrationBodyWins(ReportTestCase):
    """The body wins; frontmatter fills in only what the body lacks. [6g8s7]

    A `title` becomes the H1 only when there is no H1, and a `description`
    becomes the paragraph only when there is no paragraph. Whatever the
    frontmatter contributed nothing to is discarded and reported under
    `changed:`, so no text disappears without a record.
    """

    FM_TITLE = "Frontmatter Title"
    FM_DESCRIPTION = "The frontmatter description."
    BODY_TITLE = "Body Title"
    BODY_PARAGRAPH = "The body paragraph."
    ENTRY = "- [Alpha](alpha.md): the alpha file"

    def legacy(self, body: str) -> dict[str, str]:
        """A tree whose index.md carries both frontmatter fields over `body`."""
        return {
            "docs/alpha.md": md("Alpha", "the alpha file"),
            "docs/index.md": (
                "---\n"
                f"title: {self.FM_TITLE}\n"
                f"description: {self.FM_DESCRIPTION}\n"
                "---\n"
                "\n"
                f"{body}"
            ),
        }

    def index_notes(self, notes: list[str]) -> list[str]:
        return self.notes_mentioning(notes, str(self.path("docs/index.md")))

    # -- a disagreeing title -------------------------------------------------

    def test_an_h1_that_disagrees_with_the_frontmatter_title_survives(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.legacy(f"# {self.BODY_TITLE}\n\n{self.ENTRY}\n"))
        self.run_generator("docs", "--migrate")
        self.assertFileText(
            "docs/index.md",
            f"# {self.BODY_TITLE}\n"
            "\n"
            f"{self.FM_DESCRIPTION}\n"
            "\n"
            f"{self.ENTRY}\n",
        )

    def test_the_discarded_frontmatter_title_is_reported_under_changed(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.legacy(f"# {self.BODY_TITLE}\n\n{self.ENTRY}\n"))
        report = self.run_generator("docs", "--migrate")
        self.assertOneNote(
            self.changed(report), str(self.path("docs/index.md")), self.FM_TITLE
        )
        self.assertNoNote(self.gaps(report), self.FM_TITLE)

    # -- a body paragraph ----------------------------------------------------

    def test_a_body_paragraph_survives_the_migration(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.legacy(f"{self.BODY_PARAGRAPH}\n\n{self.ENTRY}\n"))
        self.run_generator("docs", "--migrate")
        self.assertFileText(
            "docs/index.md",
            f"# {self.FM_TITLE}\n"
            "\n"
            f"{self.BODY_PARAGRAPH}\n"
            "\n"
            f"{self.ENTRY}\n",
        )

    def test_a_frontmatter_description_beside_a_paragraph_is_not_fatal(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.legacy(f"{self.BODY_PARAGRAPH}\n\n{self.ENTRY}\n"))
        # The run completes and writes the file; carrying both is an ordinary
        # conversion, not an error.
        self.run_generator("docs", "--migrate")
        self.assertNotIn(self.FM_DESCRIPTION, self.read("docs/index.md"))

    def test_the_discarded_frontmatter_description_is_reported_under_changed(
        self,
    ) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.legacy(f"{self.BODY_PARAGRAPH}\n\n{self.ENTRY}\n"))
        report = self.run_generator("docs", "--migrate")
        self.assertOneNote(
            self.changed(report), str(self.path("docs/index.md")), self.FM_DESCRIPTION
        )
        self.assertNoNote(self.gaps(report), self.FM_DESCRIPTION)

    # -- both at once --------------------------------------------------------

    def both(self) -> dict[str, str]:
        return self.legacy(
            f"# {self.BODY_TITLE}\n\n{self.BODY_PARAGRAPH}\n\n{self.ENTRY}\n"
        )

    def test_the_body_wins_on_the_title_and_the_paragraph_together(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.both())
        self.run_generator("docs", "--migrate")
        self.assertFileText(
            "docs/index.md",
            f"# {self.BODY_TITLE}\n"
            "\n"
            f"{self.BODY_PARAGRAPH}\n"
            "\n"
            f"{self.ENTRY}\n",
        )

    def test_both_discarded_strings_are_reported_under_changed(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.both())
        report = self.run_generator("docs", "--migrate")
        changed = self.changed(report)
        self.assertOneNote(changed, str(self.path("docs/index.md")), self.FM_TITLE)
        self.assertOneNote(changed, str(self.path("docs/index.md")), self.FM_DESCRIPTION)

    def test_the_conversion_is_reported_alongside_the_discards(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.both())
        report = self.run_generator("docs", "--migrate")
        # A note about the file that is neither discard note: the conversion
        # itself is still recorded when the frontmatter contributed nothing.
        conversion = [
            note
            for note in self.index_notes(self.changed(report))
            if self.FM_TITLE not in note and self.FM_DESCRIPTION not in note
        ]
        self.assertEqual(
            len(conversion),
            1,
            f"expected one conversion note beside the discards, got {conversion}",
        )

    # -- what the report leaves recoverable ----------------------------------

    def test_the_discarded_text_appears_in_the_report_verbatim(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        title = "Docs: specs, decisions & how-tos"
        description = "Everything written down -- specs, decisions, how-tos."
        self.write_tree(
            {
                "docs/alpha.md": md("Alpha", "the alpha file"),
                "docs/index.md": (
                    "---\n"
                    f"title: '{title}'\n"
                    f"description: {description}\n"
                    "---\n"
                    "\n"
                    f"# {self.BODY_TITLE}\n"
                    "\n"
                    f"{self.BODY_PARAGRAPH}\n"
                    "\n"
                    f"{self.ENTRY}\n"
                ),
            }
        )
        report = self.run_generator("docs", "--migrate")
        # Discarded text is only recoverable if it is reproduced exactly.
        self.assertIn(title, report)
        self.assertIn(description, report)

    # -- stability -----------------------------------------------------------

    def test_a_migrated_file_is_byte_stable_on_a_second_run(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.both())
        self.run_generator("docs", "--migrate")
        migrated = self.read("docs/index.md")
        self.run_generator("docs")
        self.assertEqual(self.read("docs/index.md"), migrated)

    def test_a_second_run_without_migrate_reports_no_conversion(self) -> None:
        # spec: 6g8s7 (plugins/index-md/docs/specs/directory-index.md)
        self.write_tree(self.both())
        self.run_generator("docs", "--migrate")
        report = self.run_generator("docs")
        # Nothing about the frontmatter is left to say, and nothing it held
        # can be discarded twice.
        self.assertNoNote(self.changed(report), self.FM_TITLE)
        self.assertNoNote(self.changed(report), self.FM_DESCRIPTION)

if __name__ == "__main__":
    unittest.main()
