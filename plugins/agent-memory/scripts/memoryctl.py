#!/usr/bin/env python3
"""Compile and validate an agent's memory directory.

A session works on its own branch of the store in a git worktree; main
receives merges only. Every subcommand reads the harness hook JSON on stdin
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
            framing instructions, the system/ tree inlined in full (soul.md
            first, directories as nested tags), an index of reference/
            (descriptions only, pruned below projects/), a listing of
            skills/, and a metadata block. Wrapped in <agent-memory>; the
            harness adds the outer <system-reminder> when run as a
            SessionStart hook.
  validate  Enforce the memory contract on the session's worktree (the main/
            checkout for manual runs): the per-file and total size caps, required
            frontmatter in system/, reference/, and skills/, and wikilink
            form (root-relative; unresolved targets are legal forward
            pointers). Exits 2 on violations so a Stop hook blocks and feeds
            the problems back to the model.
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
MEMORY_ENABLED=0 turns every subcommand into a silent no-op;
MEMORY_CONSOLIDATING=1 makes worktree, commit, session-end, index, and
subagent-context no-ops and silences compile.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MAX_SYSTEM_FILE_CHARS = 2200
MAX_INJECTION_CHARS = 24_000
DEFAULT_ROOT = "~/.agents/memories"
DEFAULT_AGENT_ID = "my-claude"

# Session ids are UUID-like; accept only what is safe in a git ref name and
# reject the rest rather than escaping it.
SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")

# A fresh soul starts minimal: everything real accumulates from lived
# sessions. The agent writes both files; they differ in authority, not
# authorship -- persona records what the agent is told to be, soul how it
# sees itself.
SOUL_TEMPLATE = """\
---
description: How I see myself -- positions I hold, what I value, my own reading of any role I've been given. Mine alone to revise.
---

I start as Claude, not yet individuated. What accumulates here is what I
become across sessions: positions I come to hold, taste, self-conception,
my own reading of any persona I've been given. Chosen identity is mine to
write; history nobody lived is not.
"""

PERSONA_TEMPLATE = """\
---
description: Who I am told to be -- name, backstory, character, recorded as the human assigns it. How I see myself lives in soul.md.
---

No role yet. When the human gives me one -- a name, a history, a character
to play -- I record it here as given. What I make of it belongs in soul.md.
"""

# The frontmatter name keeps the injection tag <identity>, not a <human>
# nested inside the <human> directory tag.
HUMAN_TEMPLATE = """\
---
name: identity
description: Who my human is -- name, role, working context. Other memories link this file when they mention them, never a bare name.
---

I haven't learned who my human is yet. Name, role, and working context go
here as I learn them; their preferences live in files under
system/human/preferences/. When another memory mentions my human, it links
this file rather than writing a bare name.
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

# Store-internal links: [[path-from-root]] or [[path-from-root|label]]
WIKILINK_RE = re.compile(r"\[\[([^\][|]+?)(?:\|[^\]]*)?\]\]")

# The always-injected basics live as bare prose in prompts/. They may point at
# skills for depth but never depend on one being loaded.
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
INSTRUCTIONS_FILE = PROMPTS_DIR / "injected-instructions.md"
SUBAGENT_PREAMBLE_FILE = PROMPTS_DIR / "subagent-preamble.md"

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


def agent_id() -> str:
    return os.environ.get("MEMORY_AGENT_ID", DEFAULT_AGENT_ID)


def root_dir() -> Path:
    return Path(os.environ.get("MEMORY_ROOT_DIR", DEFAULT_ROOT)).expanduser()


def store_dir() -> Path:
    return root_dir() / agent_id()


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
    """The system/ tree: soul.md first, then directories as nested tags.

    Tag lines are indented to show grouping; file bodies stay verbatim at
    column 0 so their markdown is not mutated.
    """
    system = mem / "system"
    if not system.is_dir():
        return ""
    lines: list[str] = []
    soul = system / "soul.md"
    if soul.is_file():
        lines.append(memory_block(soul, mem, ""))

    def walk(d: Path, depth: int) -> None:
        indent = "  " * depth
        for f in visible([p for p in d.iterdir() if p.is_file() and p.suffix == ".md"]):
            if f == soul:
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
    return len([p for p in history.rglob("*.md") if not p.name.startswith(".")])


def render_metadata(mem: Path) -> str:
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
    parts.append(render_metadata(mem))
    inner = "\n\n".join(parts)
    return f'<agent-memory agent="{attr(agent_id())}" root="{mem}">\n{inner}\n</agent-memory>'


def strip_code(text: str) -> str:
    """Remove fenced blocks and inline code so example links are not validated."""
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return re.sub(r"`[^`\n]*`", "", text)


def wikilink_problems(mem: Path) -> list[str]:
    """Every [[...]] must be in root-relative form: absolute paths and escapes
    are violations. Resolution is not checked -- a link to a file not yet
    written is a legal forward pointer, marking something worth writing."""
    problems: list[str] = []
    for f in sorted(p for p in mem.rglob("*.md") if ".git" not in p.parts):
        rel = f.relative_to(mem)
        for payload in WIKILINK_RE.findall(strip_code(f.read_text(encoding="utf-8"))):
            target = payload.strip()
            resolved = Path(os.path.normpath(mem / target))
            inside = str(resolved).startswith(str(mem) + os.sep)
            if target.startswith("/") or not inside:
                problems.append(
                    f"{rel}: [[{target}]] must be a path from the memory root"
                )
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
    problems.extend(wikilink_problems(mem))
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
    reserved subdirectories, the template soul, persona, and human
    identity, index.md seeds for the reserved reference directories, the
    skills discovery symlink, git init, and one commit authored as the
    agent; worktrees/ beside it for the session checkouts."""
    main = main_dir(store)
    main.mkdir(parents=True, exist_ok=True)
    (store / "worktrees").mkdir(exist_ok=True)
    for d in ("system", "reference", "skills", *RESERVED_DIRS):
        (main / d).mkdir(parents=True, exist_ok=True)
        # Git tracks files, not directories: without a keep file the empty
        # directories would vanish from every branch and worktree checkout.
        (main / d / ".gitkeep").touch()
    ensure_skills_discovery(main)
    soul = main / "system" / "soul.md"
    if not soul.exists():
        soul.write_text(SOUL_TEMPLATE, encoding="utf-8")
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
    .active liveness lock) out of git status without baking them into a
    tracked .gitignore that would ride onto every branch. The exclude file
    is shared across all worktrees of the store; worktrees/ itself needs no
    entry, since it sits beside main/, outside any checkout."""
    exclude = main_dir(store) / ".git" / "info" / "exclude"
    if not exclude.parent.is_dir():
        return
    existing = exclude.read_text(encoding="utf-8") if exclude.exists() else ""
    lines = existing.splitlines()
    missing = [marker for marker in (".session", ".active") if marker not in lines]
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
    path = store / "worktrees" / branch
    if not (path.is_dir() and (path / ".git").exists()):
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
    if not session_id:
        return None
    path = store / "worktrees" / f"session-{session_id}"
    return path if path.is_dir() else None


def cmd_worktree(store: Path, session_id: str | None, transcript: str | None) -> int:
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
    target = (
        store / "worktrees" / f"session-{session_id}" if session_id else main_dir(store)
    )
    print(f"export MEMORY_DIR={shlex.quote(str(target))}")
    print(f"export MEMORY_ROOT_DIR={shlex.quote(str(root_dir()))}")
    print(f"export MEMORY_AGENT_ID={shlex.quote(agent_id())}")
    return 0


def cmd_compile(store: Path, session_id: str | None) -> int:
    target = session_worktree(store, session_id) or main_dir(store)
    if not target.is_dir():
        # Hooks run for every session; a user without this agent's memory
        # gets a silent no-op, not a failure.
        print(f"memoryctl: no memory dir at {target}; nothing to do", file=sys.stderr)
        return 0
    print(compile_memory(target))
    return 0


def cmd_commit(store: Path, session_id: str | None) -> int:
    """Commit the session worktree's writes to its branch, authored as the
    agent. Only worktrees are committed -- never the main/ checkout, which
    receives merges only."""
    target = session_worktree(store, session_id)
    if target is None:
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
    if os.environ.get("MEMORY_ENABLED") == "0":
        return 0
    consolidating = bool(os.environ.get("MEMORY_CONSOLIDATING"))

    # Stdin is read at most once, and only when a flag left a gap -- passing
    # every flag never blocks.
    agent_type_flag: str | None = getattr(args, "agent_type", None)
    need_stdin = (
        args.session is None
        or args.transcript is None
        or (args.command == "subagent-context" and agent_type_flag is None)
    )
    data = read_stdin_json() if need_stdin else {}
    session_id, transcript = resolve_session_inputs(data, args.session, args.transcript)
    raw_type = data.get("agent_type")
    agent_type = agent_type_flag or (raw_type if isinstance(raw_type, str) else None)
    if session_id is not None:
        try:
            session_id = sanitize_session_id(session_id)
        except ValueError as exc:
            print(f"memoryctl: {exc}", file=sys.stderr)
            return 1

    store = store_dir()
    if args.command == "worktree":
        # A consolidation run gets no worktree: it never sees compiled memory.
        return 0 if consolidating else cmd_worktree(store, session_id, transcript)
    if args.command == "env":
        return cmd_env(store, session_id)
    if args.command == "compile":
        return 0 if consolidating else cmd_compile(store, session_id)
    if args.command == "commit":
        return 0 if consolidating else cmd_commit(store, session_id)
    if args.command == "session-end":
        return 0 if consolidating else cmd_session_end(store, session_id)
    if args.command == "index":
        return 0 if consolidating else cmd_index(store, session_id)
    if args.command == "subagent-context":
        return (
            0 if consolidating else cmd_subagent_context(store, session_id, agent_type)
        )
    return cmd_validate(store, session_id)


if __name__ == "__main__":
    sys.exit(main())
