#!/usr/bin/env python3
"""Compile and validate an agent's memory directory.

A session works on its own branch of the store in a git worktree and
never writes main; only the memory agent commits there. Every subcommand
reads the harness hook JSON on stdin
(`session_id`, `transcript_path`) and binds to that session's worktree;
`--session <id>` / `--transcript <path>` override for manual runs and tests.

Subcommands:
  worktree  Create-if-missing the worktree worktrees/session-<id> on branch
            session-<id> off main (reused if present), scaffolding the store
            first when it is absent. Records the transcript path in the
            worktree as an untracked .session file, writes the untracked
            .active liveness lock, and prints the worktree path.
  env       Print `export MEMORY_DIR=<worktree>` plus the resolved
            MEMORY_ROOT_DIR and MEMORY_AGENT_ID. A SessionStart hook appends
            them to $CLAUDE_ENV_FILE, which the harness runs as a preamble
            before each Bash command.
  compile   Emit the system-prompt injection for the session's worktree:
            framing instructions, the system/ tree inlined in full (persona.md
            first, directories as nested tags), an index of reference/
            (descriptions only, pruned below projects/), a listing of
            skills/, and a metadata block. Wrapped in <agent-memory>; the
            harness adds the outer <system-reminder> when run as a
            SessionStart hook.
  validate  Enforce the memory contract on the session's worktree (the main/
            checkout for manual runs): the per-file and total size caps, required
            frontmatter in system/, reference/, and skills/, and link form
            (markdown links with rooted hrefs; unresolved targets are legal
            forward pointers). Exits 2 on violations so a Stop hook blocks and
            feeds the problems back to the model.
  system-delta
            Report the turn's net character growth in system/ (working tree
            against HEAD) when it clears a floor -- 300 net characters in
            total, or a grown file crossing half the per-file cap. The report
            goes out as Stop-hook JSON on stdout (`decision: block`, the
            report as `reason`, a one-line `systemMessage` for the human), so
            a Stop hook blocks once and asks whether the additions earn their
            place in every future prompt; the exit code is always 0, since a
            reflection question is not an error. Growth under the floor, net
            zero or shrinkage, and a stop-hook continuation
            (`stop_hook_active` in the hook JSON) print nothing at all.
  commit    Commit the session worktree's uncommitted writes to its branch,
            authored as the agent. A Stop hook runs it after validate passes;
            a clean worktree is a no-op.
  session-end
            Remove the worktree's untracked .active liveness lock. A
            SessionEnd hook runs it, so clean-up can tell an ended
            session from a running one without guessing from timestamps.
  index     Refresh the generated index.md bodies in the worktree's
            reference/ tree (shared cli/generate_index.py, refresh-only:
            never creates). SessionStart and SessionEnd hooks run it, so
            the on-disk indexes track the tree at session boundaries.
  subagent-context
            Print SubagentStart hook JSON whose additionalContext carries the
            compiled memory with a read-only preamble, so subagents see the
            store too. The memory agent (agent_type 'memory', plugin-scoped
            included) is skipped: consolidation needs the outside view.

The memory root is $MEMORY_ROOT_DIR (default ~/.agents/memories); the agent id
is $MEMORY_AGENT_ID (default my-claude). The agent's store lives at
<root>/<agent-id>/ and holds exactly two directories: main/ (the main
checkout, with the git dir inside it) and worktrees/ (one session checkout
per branch, siblings of main, never nested inside a checkout).
MEMORY_ENABLED=0 turns every subcommand into a silent no-op.

The session layer has switches of its own. MEMORY_SESSION= (set empty)
runs the session without a branch or worktree: memory is injected
read-only from main and nothing is created or committed.
MEMORY_SESSION_ID=<id> pins the session id -- it beats the id in the hook
JSON (the --session flag still wins), so any number of sessions share one
branch and worktree. MEMORY_SESSION_DIR=<path> puts the session worktree
at an explicit path instead of worktrees/session-<id>, a debugging aid.

Configuration may also come from <cwd>/.agents/memory.conf, a `KEY = value`
file whose keys are the variable names with the MEMORY_ prefix left off
(ROOT_DIR, AGENT_ID, ENABLED, SESSION, SESSION_ID, SESSION_DIR). The file
is read first; environment variables take precedence.
"""

from __future__ import annotations

import argparse
import functools
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_SYSTEM_FILE_CHARS = 2200
# Growth below this many net characters is not worth a turn's attention: the
# growth check stays silent unless a file also crossed half the per-file cap.
SYSTEM_GROWTH_FLOOR = 300
MAX_INJECTION_CHARS = 24_000
DEFAULT_ROOT = "~/.agents/memories"
DEFAULT_AGENT_ID = "my-claude"

# Session ids are UUID-like; accept only what is safe in a git ref name and
# reject the rest rather than escaping it.
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

# A fresh persona starts minimal: everything real accumulates from lived
# sessions. Exactly two sections -- what to act as, how to sound -- and no
# identity claims: identity is trained into the model, so the file must
# hold when the model changes, which is why no model is named here. The
# scaffold is written tersely -- it is the exemplar future writes imitate.
PERSONA_TEMPLATE = """\
---
description: The role I'm asked to play -- what to act as, and how to sound.
---

# Role

- Nothing assigned yet. File what to act as here, one short line each.

# Style

- Nothing assigned yet. File how to sound here, one short line each.
"""

# The frontmatter name keeps the injection tag <identity>, not a <human>
# nested inside the <human> directory tag.
HUMAN_TEMPLATE = """\
---
name: identity
description: Who my human is -- name, role, working context. Other memories say the human, linked to this file, never the name.
---

Not learned yet. Name, role, and working context go here; preferences go
one per file under system/human/preferences/.

Their name lives only here. Elsewhere I write the
[human](/system/human/human.md) -- the word linked to this file, never the
name.
"""

# Reference directories carry an index.md: authored frontmatter description
# (what compile shows for the directory), generated body (the index-md
# skill's table of contents). The reserved ones are seeded at scaffold.
PROJECTS_INDEX_TEMPLATE = """\
---
title: projects
description: One directory per code base I work in; each project's index.md describes it.
---
"""

HISTORY_INDEX_TEMPLATE = """\
---
title: history
description: My dated episodic notes, staged for consolidation; nothing lives here permanently.
---
"""

# The reserved directories the conventions name: knowledge of the human and
# standing rules in system/, per-code-base and staged episodic notes in
# reference/. Scaffolded so the layout is discoverable without the skill.
RESERVED_DIRS = (
    "system/human",
    "system/human/preferences",
    "system/core",
    "reference/projects",
    "reference/history",
)

# A system file's tag must be a valid XML element name.
TAG_RE = re.compile(r"^[A-Za-z][A-Za-z0-9._-]*$")

# Links are markdown links; the href decides what is checked. The capture
# stops at whitespace or the closing paren, so an optional "title" after the
# href is left out of it.
MARKDOWN_LINK_RE = re.compile(r"\[[^\][]*\]\(([^()\s]*)")

# The retired spelling. Any [[...]] is a violation now.
LEGACY_WIKILINK_RE = re.compile(r"\[\[([^\]]*)\]\]")

# An href carrying a URI scheme (https:, mailto:) points outside the store.
URI_SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

# The always-injected basics live as bare prose in prompts/. They may point at
# skills for depth but never depend on one being loaded.
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
INSTRUCTIONS_FILE = PROMPTS_DIR / "injected-instructions.md"
SUBAGENT_PREAMBLE_FILE = PROMPTS_DIR / "subagent-preamble.md"
SESSIONLESS_PREAMBLE_FILE = PROMPTS_DIR / "sessionless-preamble.md"

# The index.md body generator, shared across plugins in the repo's cli/
# directory (plugins/agent-memory/scripts -> repo root). Absent -- e.g. an
# installed copy without the checkout -- the index refresh degrades to a
# skipped step, never a failure.
INDEX_GENERATOR = Path(__file__).resolve().parents[3] / "cli" / "generate_index.py"


def prompt_block(path: Path) -> str:
    try:
        body = path.read_text(encoding="utf-8").strip()
    except OSError:
        print(f"memoryctl: cannot read {path}", file=sys.stderr)
        body = f"({path.name} missing from the agent-memory plugin)"
    return f"<memory-instructions>\n{body}\n</memory-instructions>"


@functools.cache
def read_conf() -> dict[str, str]:
    """<cwd>/.agents/memory.conf: `KEY = value` lines, keys named like the
    environment variables with the MEMORY_ prefix left off. Blank lines and
    `#` comments are skipped; an empty value is legal (SESSION = disables
    the session layer, exactly like MEMORY_SESSION= in the environment)."""
    try:
        text = (Path(".agents") / "memory.conf").read_text(encoding="utf-8")
    except OSError:
        return {}
    values: dict[str, str] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if sep:
            values[key.strip()] = value.strip()
    return values


def config_value(name: str) -> str | None:
    """One lookup for all configuration: $MEMORY_<name> from the
    environment, else <name> from the conf file. The environment wins."""
    env = os.environ.get(f"MEMORY_{name}")
    if env is not None:
        return env
    return read_conf().get(name)


def agent_id() -> str:
    return config_value("AGENT_ID") or DEFAULT_AGENT_ID


def root_dir() -> Path:
    return Path(config_value("ROOT_DIR") or DEFAULT_ROOT).expanduser()


def store_dir() -> Path:
    return root_dir() / agent_id()


def session_disabled() -> bool:
    """MEMORY_SESSION set to the empty string switches the session layer
    off: no branch, no worktree, memory injected read-only from main."""
    return config_value("SESSION") == ""


def session_dir_override() -> Path | None:
    """MEMORY_SESSION_DIR pins the session worktree to an explicit path
    instead of worktrees/session-<id> -- a debugging aid."""
    value = config_value("SESSION_DIR")
    return Path(value).expanduser() if value else None


def main_dir(store: Path) -> Path:
    return store / "main"


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Split markdown into (frontmatter, body). Top-level scalar keys only."""
    if not text.startswith("---\n"):
        return {}, text
    lines = text.split("\n")
    try:
        close = lines.index("---", 1)
    except ValueError:
        return {}, text
    meta: dict[str, str] = {}
    for line in lines[1:close]:
        if not line or line.startswith((" ", "\t", "#")):
            continue
        key, sep, value = line.partition(":")
        if sep and value.strip():
            meta[key.strip()] = value.strip().strip("'\"")
    body = "\n".join(lines[close + 1 :]).lstrip("\n")
    return meta, body


def read_markdown(path: Path) -> tuple[dict[str, str], str]:
    return split_frontmatter(path.read_text(encoding="utf-8"))


def attr(value: str) -> str:
    return value.replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


def visible(entries: list[Path]) -> list[Path]:
    return sorted(p for p in entries if not p.name.startswith("."))


def file_description(f: Path) -> str:
    """A reference file's index description is its own frontmatter description."""
    if f.suffix == ".md":
        meta, _ = read_markdown(f)
        description = meta.get("description")
        if description:
            return description
    return ""


def dir_description(d: Path) -> str:
    """A directory's description is the authored frontmatter of its index.md;
    the generated body is ignored here. Without one, the entry is name-only."""
    idx = d / "index.md"
    return file_description(idx) if idx.is_file() else ""


def tag_name(f: Path) -> str:
    """The XML tag a system file renders as: frontmatter name, else file stem."""
    meta, _ = read_markdown(f)
    name = meta.get("name")
    return name if name else f.stem


def memory_block(f: Path, mem: Path, indent: str) -> str:
    meta, body = read_markdown(f)
    tag = tag_name(f)
    child = indent + "  "
    lines = [
        f"{indent}<{tag}>",
        f"{child}<path>$MEMORY_DIR/{f.relative_to(mem)}</path>",
    ]
    description = meta.get("description")
    if description:
        lines.append(f"{child}<description>{attr(description)}</description>")
    lines.append(body.rstrip())
    lines.append(f"{indent}</{tag}>")
    return "\n".join(lines)


def render_system(mem: Path) -> str:
    """The system/ tree: persona.md first, then directories as nested tags.

    Tag lines are indented to show grouping; file bodies stay verbatim at
    column 0 so their markdown is not mutated.
    """
    system = mem / "system"
    if not system.is_dir():
        return ""
    lines: list[str] = []
    persona = system / "persona.md"
    if persona.is_file():
        lines.append(memory_block(persona, mem, ""))

    def walk(d: Path, depth: int) -> None:
        indent = "  " * depth
        for f in visible([p for p in d.iterdir() if p.is_file() and p.suffix == ".md"]):
            if f == persona:
                continue
            lines.append(memory_block(f, mem, indent))
        for sub in visible([p for p in d.iterdir() if p.is_dir()]):
            lines.append(f"{indent}<{sub.name}>")
            walk(sub, depth + 1)
            lines.append(f"{indent}</{sub.name}>")

    walk(system, 0)
    return "\n".join(lines)


def render_reference_index(mem: Path) -> str:
    ref = mem / "reference"
    lines: list[str] = []

    def entry_line(indent: str, label: str, description: str) -> str:
        return (
            f"{indent}{label} -- {description}" if description else f"{indent}{label}"
        )

    def walk(d: Path, depth: int) -> None:
        indent = "  " * depth
        for sub in visible([p for p in d.iterdir() if p.is_dir()]):
            if sub.name == "projects" and depth == 0:
                note = "[project names only; browse a project for its files]"
                lines.append(entry_line(indent, f"{sub.name}/", note))
                for project in visible([p for p in sub.iterdir() if p.is_dir()]):
                    lines.append(
                        entry_line(
                            indent + "  ",
                            f"{project.name}/",
                            dir_description(project),
                        )
                    )
                continue
            lines.append(entry_line(indent, f"{sub.name}/", dir_description(sub)))
            walk(sub, depth + 1)
        # index.md files are navigation for on-disk traversal; the compiled
        # index shows their description on the directory line instead.
        for f in visible([p for p in d.iterdir() if p.is_file()]):
            if f.name == "index.md":
                continue
            lines.append(entry_line(indent, f.name, file_description(f)))

    head = '<memory-index root="reference/">'
    note = "Contents are not loaded into context; read a file when its description is relevant."
    walk(ref, 0)
    return "\n".join([head, note, *lines, "</memory-index>"])


def render_skills(mem: Path) -> str:
    skills = mem / "skills"
    if not skills.is_dir():
        return ""
    lines: list[str] = []
    for d in visible([p for p in skills.iterdir() if p.is_dir()]):
        skill_file = d / "SKILL.md"
        if not skill_file.is_file():
            continue
        meta, _ = read_markdown(skill_file)
        name = meta.get("name")
        description = meta.get("description")
        label = name if name else d.name
        lines.append(f"- {label} -- {description}" if description else f"- {label}")
    if not lines:
        return ""
    return "\n".join(["<memory-skills>", *lines, "</memory-skills>"])


def queued_session_branches(mem: Path) -> int | None:
    """The consolidation queue: session-* branches. None when git is absent."""
    if not (mem / ".git").exists():
        return None
    try:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(mem),
                "for-each-ref",
                "--format=%(refname:short)",
                "refs/heads/session-*",
            ],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return len([line for line in result.stdout.splitlines() if line.strip()])


def git_head(mem: Path) -> str | None:
    if not (mem / ".git").exists():
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(mem), "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def staged_history_count(mem: Path) -> int:
    history = mem / "reference" / "history"
    if not history.is_dir():
        return 0
    # index.md is navigation, not a staged note -- same skip as the index.
    return len(
        [
            p
            for p in history.rglob("*.md")
            if not p.name.startswith(".") and p.name != "index.md"
        ]
    )


def render_metadata(mem: Path, total: int) -> str:
    """The closing block. `total` is the compiled injection's size, measured
    on an assembly that carried a stand-in where this line's number goes, so
    it can drift a character or two from the block it reports on -- exactness
    is validate's job, visibility is this line's."""
    compiled = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "<memory-metadata>",
        f"agent: {agent_id()}",
        f"MEMORY_DIR: {mem}",
        f"compiled: {compiled}",
    ]
    head = git_head(mem)
    if head is not None:
        lines.append(f"memory HEAD: {head}")
    lines.append(
        f"injection: {total:,} / {MAX_INJECTION_CHARS:,} chars,"
        f" system/: {len(render_system(mem)):,}"
    )
    staged = staged_history_count(mem)
    unit = "entry" if staged == 1 else "entries"
    lines.append(
        f"staged in reference/history/: {staged} {unit} awaiting consolidation"
    )
    queued = queued_session_branches(mem)
    if queued is not None:
        unit = "branch" if queued == 1 else "branches"
        lines.append(f"consolidation queue: {queued} session {unit}")
    lines.append("</memory-metadata>")
    return "\n".join(lines)


def compile_memory(mem: Path, preamble: str | None = None) -> str:
    parts: list[str] = [
        preamble if preamble is not None else prompt_block(INSTRUCTIONS_FILE)
    ]
    system_block = render_system(mem)
    if system_block:
        parts.append(system_block)
    if (mem / "reference").is_dir():
        parts.append(render_reference_index(mem))
    skills_block = render_skills(mem)
    if skills_block:
        parts.append(skills_block)

    def assemble(metadata: str) -> str:
        inner = "\n\n".join([*parts, metadata])
        return (
            f'<agent-memory agent="{attr(agent_id())}" root="{mem}">\n'
            f"{inner}\n</agent-memory>"
        )

    # The accounting line measures the block it sits in. Size one assembly
    # whose line carries the cap where the total goes -- the same width as any
    # total that stays under it -- then report that size.
    probe = assemble(render_metadata(mem, MAX_INJECTION_CHARS))
    return assemble(render_metadata(mem, len(probe)))


def strip_code(text: str) -> str:
    """Remove fenced blocks and inline code so example links are not validated."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return re.sub(r"`[^`\n]*`", "", text)


def link_problems(mem: Path) -> list[str]:
    """Every markdown link is checked by its href. An external href -- a URI
    scheme or a protocol-relative // -- and a same-file anchor go unchecked.
    A rooted href (leading /) is an in-store link: its normalized path must
    stay inside the store, escapes are violations, and resolution is not
    checked, since a link to a file not yet written is a legal forward
    pointer. A relative href is a violation outside a generated index.md
    body, whose child links the generator re-derives on every refresh. A
    wikilink is the retired spelling and always a violation."""
    problems: list[str] = []
    for f in sorted(p for p in mem.rglob("*.md") if ".git" not in p.parts):
        rel = f.relative_to(mem)
        text = strip_code(f.read_text(encoding="utf-8"))
        for payload in LEGACY_WIKILINK_RE.findall(text):
            problems.append(
                f"{rel}: [[{payload}]] is a legacy wikilink"
                " -- write [label](/path-from-root)"
            )
        for href in MARKDOWN_LINK_RE.findall(text):
            if URI_SCHEME_RE.match(href) or href.startswith(("//", "#")):
                continue
            if not href.startswith("/"):
                if f.name != "index.md":
                    problems.append(
                        f"{rel}: ({href}) must be a path from the memory root,"
                        " written with a leading /"
                    )
                continue
            resolved = Path(os.path.normpath(mem / href.lstrip("/")))
            if not str(resolved).startswith(str(mem) + os.sep):
                problems.append(f"{rel}: ({href}) escapes the memory root")
    return problems


def validate_memory(mem: Path) -> list[str]:
    problems: list[str] = []
    system = mem / "system"
    if system.is_dir():
        for f in visible(list(system.rglob("*.md"))):
            text = f.read_text(encoding="utf-8")
            rel = f.relative_to(mem)
            if len(text) > MAX_SYSTEM_FILE_CHARS:
                problems.append(
                    f"{rel}: {len(text)} chars exceeds the {MAX_SYSTEM_FILE_CHARS}-char cap"
                    " for system/ files. Condense it, or move detail to reference/."
                )
            meta, _ = split_frontmatter(text)
            if not meta.get("description"):
                problems.append(f"{rel}: missing 'description' frontmatter")
            tag = tag_name(f)
            if not TAG_RE.match(tag):
                problems.append(
                    f"{rel}: '{tag}' is not a valid XML tag name;"
                    " set a tag-safe 'name' in the frontmatter"
                )
    reference = mem / "reference"
    if reference.is_dir():
        for f in visible(list(reference.rglob("*.md"))):
            meta, _ = split_frontmatter(f.read_text(encoding="utf-8"))
            if not meta.get("description"):
                rel = f.relative_to(mem)
                problems.append(f"{rel}: missing 'description' frontmatter")
    skills = mem / "skills"
    if skills.is_dir():
        # Agent skills, not memory files: the harness needs name + description.
        for d in visible([p for p in skills.iterdir() if p.is_dir()]):
            skill_file = d / "SKILL.md"
            if not skill_file.is_file():
                problems.append(f"skills/{d.name}: missing SKILL.md")
                continue
            meta, _ = read_markdown(skill_file)
            for field in ("name", "description"):
                if not meta.get(field):
                    problems.append(
                        f"skills/{d.name}/SKILL.md: missing '{field}' frontmatter"
                    )
    problems.extend(link_problems(mem))
    compiled = compile_memory(mem)
    if len(compiled) > MAX_INJECTION_CHARS:
        problems.append(
            f"compiled injection is {len(compiled)} chars, over the"
            f" {MAX_INJECTION_CHARS}-char total cap. Condense system/ files or"
            " move content to reference/, which is indexed, not injected."
        )
    return problems


def read_stdin_json() -> dict[str, object]:
    """The hook JSON on stdin. Empty when there is nothing to read (a tty, an
    empty pipe, or malformed input) so manual runs never block or crash."""
    if sys.stdin is None or sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read()
    except OSError:
        return {}
    if not raw.strip():
        return {}
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def resolve_session_inputs(
    data: dict[str, object], session_flag: str | None, transcript_flag: str | None
) -> tuple[str | None, str | None]:
    """Session id and transcript path from flags, falling back to hook JSON."""
    session_id = session_flag
    transcript = transcript_flag
    if session_id is None:
        value = data.get("session_id")
        session_id = value if isinstance(value, str) and value else None
    if transcript is None:
        value = data.get("transcript_path")
        transcript = value if isinstance(value, str) and value else None
    return session_id, transcript


def sanitize_session_id(session_id: str) -> str:
    if (
        SESSION_ID_RE.match(session_id)
        and ".." not in session_id
        and not session_id.endswith(".lock")
    ):
        return session_id
    raise ValueError(
        f"unsafe session id {session_id!r}: expected characters safe for a git ref name"
    )


def git(mem: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(mem), *args],
        capture_output=True,
        text=True,
        check=True,
    )


def store_exists(store: Path) -> bool:
    return (main_dir(store) / ".git").exists()


def ensure_skills_discovery(checkout: Path) -> None:
    """Claude Code discovers agent skills at .claude/skills/ of a directory
    passed with --add-dir; the tracked symlink points that path at the
    skills/ tier. Ensured per checkout so stores that predate the link heal:
    in a worktree the auto-commit carries it onto the branch, and the next
    merge lands it in main, where discovery actually looks."""
    skills = checkout / "skills"
    if not skills.is_dir():
        skills.mkdir()
        (skills / ".gitkeep").touch()
    link = checkout / ".claude" / "skills"
    if not (link.is_symlink() or link.exists()):
        link.parent.mkdir(exist_ok=True)
        link.symlink_to(Path("..") / "skills")


def scaffold_store(store: Path) -> None:
    """Create a fresh store: main/ holding the three tiers with their
    reserved subdirectories, the template persona and human identity,
    index.md seeds for the reserved reference directories, the skills
    discovery symlink, git init, and one commit authored as the agent;
    worktrees/ beside it for the session checkouts."""
    main = main_dir(store)
    main.mkdir(parents=True, exist_ok=True)
    (store / "worktrees").mkdir(exist_ok=True)
    for d in ("system", "reference", "skills", *RESERVED_DIRS):
        (main / d).mkdir(parents=True, exist_ok=True)
        # Git tracks files, not directories: without a keep file the empty
        # directories would vanish from every branch and worktree checkout.
        (main / d / ".gitkeep").touch()
    ensure_skills_discovery(main)
    persona = main / "system" / "persona.md"
    if not persona.exists():
        persona.write_text(PERSONA_TEMPLATE, encoding="utf-8")
    human = main / "system" / "human" / "human.md"
    if not human.exists():
        human.write_text(HUMAN_TEMPLATE, encoding="utf-8")
    for rel, template in (
        ("reference/projects", PROJECTS_INDEX_TEMPLATE),
        ("reference/history", HISTORY_INDEX_TEMPLATE),
    ):
        idx = main / rel / "index.md"
        if not idx.exists():
            idx.write_text(template, encoding="utf-8")
    aid = agent_id()
    git(main, "init", "-b", "main")
    git(main, "add", "-A")
    git(
        main,
        "-c",
        f"user.name={aid}",
        "-c",
        f"user.email={aid}@agents.local",
        "commit",
        "-m",
        "initial memory",
    )


def ensure_exclude(store: Path) -> None:
    """Keep the untracked session markers (.session transcript pointer,
    .active liveness lock, .discard mark) out of git status without baking
    them into a tracked .gitignore that would ride onto every branch. The
    exclude file is shared across all worktrees of the store; worktrees/
    itself needs no entry, since it sits beside main/, outside any
    checkout."""
    exclude = main_dir(store) / ".git" / "info" / "exclude"
    if not exclude.parent.is_dir():
        return
    existing = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    lines = existing.splitlines()
    missing = [
        marker
        for marker in (".session", ".active", ".discard")
        if marker not in lines
    ]
    if not missing:
        return
    prefix = "" if not existing or existing.endswith("\n") else "\n"
    with exclude.open("a", encoding="utf-8") as handle:
        handle.write(prefix + "".join(f"{marker}\n" for marker in missing))


def branch_exists(mem: Path, branch: str) -> bool:
    result = subprocess.run(
        [
            "git",
            "-C",
            str(mem),
            "rev-parse",
            "--verify",
            "--quiet",
            f"refs/heads/{branch}",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def ensure_worktree(store: Path, session_id: str, transcript: str | None) -> Path:
    """Create-if-missing worktrees/session-<id> on branch session-<id>, reuse
    it if present, and (re)write its untracked .session pointer every time."""
    ensure_exclude(store)
    main = main_dir(store)
    branch = f"session-{session_id}"
    path = session_dir_override() or store / "worktrees" / branch
    if not (path.is_dir() and (path / ".git").exists()):
        path.parent.mkdir(parents=True, exist_ok=True)
        git(main, "worktree", "prune")
        if branch_exists(main, branch):
            # Resume where the session left off: reattach its existing branch.
            git(main, "worktree", "add", str(path), branch)
        else:
            # A new session, or a resume after the branch was reaped: branch
            # fresh off current main.
            git(main, "worktree", "add", "-b", branch, str(path), "main")
    ensure_skills_discovery(path)
    (path / ".session").write_text((transcript or "") + "\n", encoding="utf-8")
    # The liveness lock: present while the session runs. SessionEnd removes
    # it; a resume rewrites it. Clean-up deletes nothing that carries it.
    (path / ".active").touch()
    return path


def session_worktree(store: Path, session_id: str | None) -> Path | None:
    """The session's worktree path if it exists on disk, else None."""
    if session_disabled():
        return None
    override = session_dir_override()
    if override is not None:
        return override if override.is_dir() else None
    if not session_id:
        return None
    path = store / "worktrees" / f"session-{session_id}"
    return path if path.is_dir() else None


def cmd_worktree(store: Path, session_id: str | None, transcript: str | None) -> int:
    if session_disabled():
        # The session layer is off: nothing to create, memory reads from main.
        return 0
    if session_id is None:
        print(
            "memoryctl: worktree needs a session id (stdin session_id or --session)",
            file=sys.stderr,
        )
        return 1
    if not store_exists(store):
        scaffold_store(store)
    print(ensure_worktree(store, session_id, transcript))
    return 0


def cmd_env(store: Path, session_id: str | None) -> int:
    # Printed even when the target is missing: the variable costs nothing and
    # names the advertised location. The forwarded configuration lets Bash
    # commands run with exactly what the hook resolved.
    if session_disabled() or session_id is None:
        target = main_dir(store)
    else:
        target = session_dir_override() or store / "worktrees" / f"session-{session_id}"
    print(f"export MEMORY_DIR={shlex.quote(str(target))}")
    print(f"export MEMORY_ROOT_DIR={shlex.quote(str(root_dir()))}")
    print(f"export MEMORY_AGENT_ID={shlex.quote(agent_id())}")
    # Resolved values, conf file included, so Bash commands see the same
    # configuration wherever they later cd to.
    for name in ("SESSION", "SESSION_ID", "SESSION_DIR"):
        value = config_value(name)
        if value is not None:
            print(f"export MEMORY_{name}={shlex.quote(value)}")
    return 0


def cmd_compile(store: Path, session_id: str | None) -> int:
    target = session_worktree(store, session_id) or main_dir(store)
    if not target.is_dir():
        # Hooks run for every session; a user without this agent's memory
        # gets a silent no-op, not a failure.
        print(f"memoryctl: no memory dir at {target}; nothing to do", file=sys.stderr)
        return 0
    if session_disabled():
        # No branch to write to: the injection carries the read-only framing
        # instead of the maintenance instructions.
        print(compile_memory(target, preamble=prompt_block(SESSIONLESS_PREAMBLE_FILE)))
        return 0
    print(compile_memory(target))
    return 0


def cmd_commit(store: Path, session_id: str | None) -> int:
    """Commit the session worktree's writes to its branch, authored as the
    agent. Only worktrees are committed -- never the main/ checkout, which
    only the memory agent writes."""
    target = session_worktree(store, session_id)
    if target is None or session_id is None:
        print(
            "memoryctl: commit needs a session worktree; nothing to do", file=sys.stderr
        )
        return 0
    try:
        if not git(target, "status", "--porcelain").stdout.strip():
            return 0
        git(target, "add", "-A")
        aid = agent_id()
        git(
            target,
            "-c",
            f"user.name={aid}",
            "-c",
            f"user.email={aid}@agents.local",
            "commit",
            "-m",
            f"inline writes, session {session_id}",
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else str(exc)
        print(f"memoryctl: commit failed: {stderr}", file=sys.stderr)
        return 1
    return 0


def cmd_index(store: Path, session_id: str | None) -> int:
    """Refresh the generated index.md bodies in the session worktree's
    reference/ tree. Refresh only -- creation needs an authored description,
    so it stays with the agent and the index-md skill. Prints nothing to
    stdout: at SessionStart, stdout belongs to the injection."""
    target = session_worktree(store, session_id)
    if target is None:
        return 0
    ref = target / "reference"
    if not ref.is_dir():
        return 0
    if not INDEX_GENERATOR.is_file():
        print(
            f"memoryctl: no index generator at {INDEX_GENERATOR}; skipping",
            file=sys.stderr,
        )
        return 0
    result = subprocess.run(
        [sys.executable, str(INDEX_GENERATOR), str(ref), "-r", "--refresh-only"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        print(f"memoryctl: index refresh failed: {detail}", file=sys.stderr)
    return 0


def cmd_session_end(store: Path, session_id: str | None) -> int:
    """Remove the session worktree's .active liveness lock. A missing
    worktree or lock is a no-op: a memoryless or already-ended session has
    nothing to unlock."""
    target = session_worktree(store, session_id)
    if target is None:
        return 0
    (target / ".active").unlink(missing_ok=True)
    return 0


def is_memory_agent(agent_type: str | None) -> bool:
    if not agent_type:
        return False
    return agent_type.rsplit(":", 1)[-1] == "memory"


def cmd_subagent_context(
    store: Path, session_id: str | None, agent_type: str | None
) -> int:
    """SubagentStart injects only via hookSpecificOutput.additionalContext;
    plain stdout is not added to a subagent's context."""
    if is_memory_agent(agent_type):
        # Consolidation weighs every branch from outside; it never sees
        # compiled memory.
        return 0
    target = session_worktree(store, session_id) or main_dir(store)
    if not target.is_dir():
        return 0
    block = compile_memory(target, preamble=prompt_block(SUBAGENT_PREAMBLE_FILE))
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SubagentStart",
                    "additionalContext": block,
                }
            }
        )
    )
    return 0


def head_blob(mem: Path, rel: str) -> str | None:
    """A file's content at HEAD, or None when HEAD does not carry it."""
    try:
        result = subprocess.run(
            ["git", "-C", str(mem), "show", f"HEAD:{rel}"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout if result.returncode == 0 else None


def head_system_files(mem: Path) -> list[str]:
    """The system/ memory files HEAD carries -- the other half of the
    comparison, so a file deleted this turn is counted too."""
    try:
        result = subprocess.run(
            ["git", "-C", str(mem), "ls-tree", "-r", "--name-only", "HEAD", "system/"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return []
    if result.returncode != 0:
        return []
    return [
        line
        for line in result.stdout.splitlines()
        if line.endswith(".md") and not line.rsplit("/", 1)[-1].startswith(".")
    ]


def system_char_deltas(mem: Path) -> dict[str, int]:
    """Net characters added per system/ file this turn: the working tree
    against HEAD. A file HEAD lacks counts in full, a deleted one counts
    negative, and files of unchanged size are left out."""
    paths: set[str] = set(head_system_files(mem))
    system = mem / "system"
    if system.is_dir():
        for f in visible(list(system.rglob("*.md"))):
            paths.add(f.relative_to(mem).as_posix())
    deltas: dict[str, int] = {}
    for rel in sorted(paths):
        f = mem / rel
        now = f.read_text(encoding="utf-8") if f.is_file() else ""
        before = head_blob(mem, rel) or ""
        if len(now) != len(before):
            deltas[rel] = len(now) - len(before)
    return deltas


def growth_report(lines: list[str], past_half: list[str]) -> str:
    """The report the model reads: the numbers, then what a good answer to
    them looks like. Headroom decides the framing -- under half the cap
    confirming is expected, past it the file is named -- and the trim it
    invites drops or moves content, never grinds sentences into fragments."""
    report = list(lines)
    report.append("Are the additions worth their permanent place in the injection?")
    if past_half:
        if len(past_half) == 1:
            named = f"{past_half[0]} sits past half its cap"
        else:
            named = (
                ", ".join(past_half[:-1])
                + f" and {past_half[-1]} sit past half their cap"
            )
        report.append(
            f"{named}, where the room that is left is worth guarding: look"
            " there first, and move detail that can be read on demand into"
            " reference/."
        )
    else:
        report.append(
            "Every file that grew is under half its cap, so there is room:"
            " confirming the additions is the expected answer, unless"
            " something in them is detail that belongs in reference/ instead,"
            " read on demand rather than in every prompt."
        )
    report.append(
        "A trim drops content or moves it to reference/; whole sentences stay"
        " whole. Compressing prose into fragments or coined shorthand loses"
        " the memory rather than shortening it."
    )
    report.append("Trimming and confirming are both answers; either one ends the turn.")
    return "\n".join(report)


def cmd_system_delta(
    store: Path, session_id: str | None, stop_hook_active: bool
) -> int:
    """Block once on growth in system/ worth a question, with the numbers, so
    the turn weighs what it added against every future prompt that will carry
    it. The block is Stop-hook JSON on stdout, not an error: the exit code is
    always 0. Growth under the floor that crossed no half-cap, net zero --
    content moved between system/ files -- and shrinkage all stay silent, as
    does the continuation the block itself produced."""
    if stop_hook_active:
        # The turn is already a stop-hook continuation: it has seen the
        # report, and blocking on it again would never resolve.
        return 0
    target = session_worktree(store, session_id)
    if target is None or git_head(target) is None:
        return 0
    deltas = system_char_deltas(target)
    total = sum(deltas.values())
    if total <= 0:
        return 0
    half = MAX_SYSTEM_FILE_CHARS // 2
    lines = [
        "Memory check: this turn added characters to system/, which is read in"
        " full in every session."
    ]
    crossed_half: list[str] = []
    past_half: list[str] = []
    for rel, delta in sorted(deltas.items()):
        if delta <= 0:
            continue
        size = len((target / rel).read_text(encoding="utf-8"))
        share = round(100 * size / MAX_SYSTEM_FILE_CHARS)
        lines.append(
            f"- {rel}: +{delta:,} chars, now {size:,} /"
            f" {MAX_SYSTEM_FILE_CHARS:,} ({share}% of the cap)"
        )
        if size > half:
            past_half.append(rel)
            # The crossing itself is the moment worth a question; a file
            # already past half only earns one again through the floor.
            if size - delta <= half:
                crossed_half.append(rel)
    if total < SYSTEM_GROWTH_FLOOR and not crossed_half:
        # Small additions are the store working as intended: no question.
        return 0
    budget = round(100 * total / MAX_SYSTEM_FILE_CHARS)
    lines.append(
        f"Added in total: {total:,} chars -- {budget}% of one file's"
        f" {MAX_SYSTEM_FILE_CHARS:,}-char budget."
    )
    print(
        json.dumps(
            {
                "decision": "block",
                "reason": growth_report(lines, past_half),
                "systemMessage": (
                    "agent-memory: system/ grew this turn; asked the agent to"
                    " weigh the additions."
                ),
            }
        )
    )
    return 0


def cmd_validate(store: Path, session_id: str | None) -> int:
    # A session validates its own worktree; a manual run validates the main
    # checkout -- so concurrent sessions never validate each other's branch.
    target = session_worktree(store, session_id) or main_dir(store)
    if not target.is_dir():
        print(f"memoryctl: no memory dir at {target}; nothing to do", file=sys.stderr)
        return 0
    problems = validate_memory(target)
    if problems:
        print("Agent memory violates its contract:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 2
    return 0


def main() -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--session", help="session id (overrides stdin session_id)")
    common.add_argument(
        "--transcript", help="transcript path (overrides stdin transcript_path)"
    )

    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser(
        "worktree", parents=[common], help="create/reuse the session worktree"
    )
    sub.add_parser(
        "env", parents=[common], help="print the export lines for $CLAUDE_ENV_FILE"
    )
    sub.add_parser(
        "compile", parents=[common], help="print the system-prompt injection"
    )
    sub.add_parser(
        "validate",
        parents=[common],
        help="check the memory contract; exit 2 on violations",
    )
    delta = sub.add_parser(
        "system-delta",
        parents=[common],
        help="report the turn's net system/ growth; block once via hook JSON",
    )
    delta.add_argument(
        "--stop-hook-active",
        action="store_true",
        help="the turn is a stop-hook continuation (overrides stdin stop_hook_active)",
    )
    sub.add_parser(
        "commit",
        parents=[common],
        help="commit session worktree writes, authored as the agent",
    )
    sub.add_parser(
        "session-end",
        parents=[common],
        help="remove the session worktree's .active liveness lock",
    )
    sub.add_parser(
        "index",
        parents=[common],
        help="refresh generated index.md bodies in the worktree's reference/",
    )
    subagent = sub.add_parser(
        "subagent-context",
        parents=[common],
        help="print SubagentStart JSON that injects compiled memory",
    )
    subagent.add_argument(
        "--agent-type", help="agent type (overrides stdin agent_type)"
    )
    args = parser.parse_args()

    # Kill switch: MEMORY_ENABLED=0 turns every entry point into a silent no-op
    # with no side effects -- the session leaves no memory trace.
    if config_value("ENABLED") == "0":
        return 0

    # Stdin is read at most once, and only when a flag left a gap -- passing
    # every flag never blocks.
    agent_type_flag: str | None = getattr(args, "agent_type", None)
    stop_hook_flag: bool = getattr(args, "stop_hook_active", False)
    need_stdin = (
        args.session is None
        or args.transcript is None
        or (args.command == "subagent-context" and agent_type_flag is None)
        or (args.command == "system-delta" and not stop_hook_flag)
    )
    data = read_stdin_json() if need_stdin else {}
    session_id, transcript = resolve_session_inputs(data, args.session, args.transcript)
    # MEMORY_SESSION_ID pins the id between the explicit flag and the hook
    # JSON: every session started with the pin shares one branch and worktree.
    pin = config_value("SESSION_ID")
    if args.session is None and pin:
        session_id = pin
    raw_type = data.get("agent_type")
    agent_type = agent_type_flag or (raw_type if isinstance(raw_type, str) else None)
    # The harness marks a turn that is already a stop-hook continuation, so
    # the growth check blocks once and never on its own continuation.
    stop_hook_active = stop_hook_flag or data.get("stop_hook_active") is True
    if session_id is not None:
        try:
            session_id = sanitize_session_id(session_id)
        except ValueError as exc:
            print(f"memoryctl: {exc}", file=sys.stderr)
            return 1

    store = store_dir()
    if args.command == "worktree":
        return cmd_worktree(store, session_id, transcript)
    if args.command == "env":
        return cmd_env(store, session_id)
    if args.command == "compile":
        return cmd_compile(store, session_id)
    if args.command == "system-delta":
        return cmd_system_delta(store, session_id, stop_hook_active)
    if args.command == "commit":
        return cmd_commit(store, session_id)
    if args.command == "session-end":
        return cmd_session_end(store, session_id)
    if args.command == "index":
        return cmd_index(store, session_id)
    if args.command == "subagent-context":
        return cmd_subagent_context(store, session_id, agent_type)
    return cmd_validate(store, session_id)


if __name__ == "__main__":
    sys.exit(main())
