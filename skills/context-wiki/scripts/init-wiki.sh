#!/usr/bin/env bash
# Create the parts every context wiki starts with: the git repository,
# AGENTS.md with its CLAUDE.md symlink, and agent-skills/ with the symlinks
# that let agent harnesses find its skills.
#
# Usage: init-wiki.sh [wiki-root]   (default: current directory)
#
# Idempotent: creates only what is missing, never overwrites an existing
# file. Safe to re-run. README.md and the root INDEX.md are not created
# here: README.md needs the wiki's scope, which only the human knows, and
# INDEX.md comes from the index-md skill. Nothing is committed, and nothing
# already in the folder is moved.
set -euo pipefail

root="${1:-.}"
mkdir -p "$root"
root="$(cd "$root" && pwd -P)"

created=()
skipped=()
conflicts=()

# The wiki root must be the root of its git repository.
if toplevel="$(git -C "$root" rev-parse --show-toplevel 2>/dev/null)"; then
  toplevel="$(cd "$toplevel" && pwd -P)"
  if [ "$toplevel" != "$root" ]; then
    echo "error: $root is inside the git repository at $toplevel." >&2
    echo "A context wiki must be the root of its own repository." >&2
    exit 1
  fi
  skipped+=(".git/")
else
  git init --quiet "$root"
  created+=(".git/")
fi

make_dir() {
  if [ -d "$root/$1" ]; then
    skipped+=("$1/")
  else
    mkdir -p "$root/$1"
    created+=("$1/")
  fi
}

# make_file <path> <content>  -- writes content only if <path> does not exist
make_file() {
  if [ -e "$root/$1" ] || [ -L "$root/$1" ]; then
    skipped+=("$1")
  else
    printf '%s\n' "$2" >"$root/$1"
    created+=("$1")
  fi
}

# make_keep <dir> -- empty .gitkeep so git tracks the folder. Without it a
# fresh clone of a wiki with no skills has no agent-skills/, and the
# symlinks to it point at nothing.
make_keep() {
  if [ -e "$root/$1/.gitkeep" ]; then
    skipped+=("$1/.gitkeep")
  else
    : >"$root/$1/.gitkeep"
    created+=("$1/.gitkeep")
  fi
}

# make_link <path> <target>  -- relative symlink, so it works in every clone
make_link() {
  if [ -L "$root/$1" ] && [ "$(readlink "$root/$1")" = "$2" ]; then
    skipped+=("$1 -> $2")
  elif [ -e "$root/$1" ] || [ -L "$root/$1" ]; then
    conflicts+=("$1 exists but is not a symlink to $2")
  else
    ln -s "$2" "$root/$1"
    created+=("$1 -> $2")
  fi
}

make_dir agent-skills
make_dir .agents
make_dir .claude
make_keep agent-skills

make_link .agents/skills ../agent-skills
make_link .claude/skills ../agent-skills

make_file AGENTS.md "$(cat <<'EOF'
This folder is a context wiki. Load the context-wiki skill before you read
or change it. Start at the README.md next to this file.

## Conventions

- Agent skills live in agent-skills/. .claude/skills and .agents/skills are
  relative symlinks to it.
EOF
)"
make_link CLAUDE.md AGENTS.md

make_file .gitignore "$(cat <<'EOF'
# Personal Claude Code settings and instructions
CLAUDE.local.md
.claude/settings.local.json

.DS_Store
EOF
)"

echo "Created:"
if [ "${#created[@]}" -eq 0 ]; then
  echo "  (nothing -- everything already existed)"
else
  printf '  %s\n' "${created[@]}"
fi
echo "Skipped (already existed):"
if [ "${#skipped[@]}" -eq 0 ]; then
  echo "  (nothing)"
else
  printf '  %s\n' "${skipped[@]}"
fi
# has_note_frontmatter <file> -- the file opens with frontmatter that carries
# both name and description
has_note_frontmatter() {
  awk 'NR == 1 && $0 != "---" { exit 1 }
       NR > 1 && $0 == "---" { exit !(n && d) }
       /^name:/ { n = 1 }
       /^description:/ { d = 1 }
       END { if (NR < 2) exit 1 }' "$1"
}

# Markdown that was here before is a note, and needs name and description
# frontmatter. Reported, never moved or changed.
missing=()
while IFS= read -r -d '' f; do
  rel="${f#"$root"/}"
  case "$rel" in
    README.md | AGENTS.md | CLAUDE.md | INDEX.md | */INDEX.md | agent-skills/*) continue ;;
  esac
  has_note_frontmatter "$f" || missing+=("$rel")
done < <(find "$root" -name .git -prune -o -type f -name '*.md' -print0)
if [ "${#missing[@]}" -gt 0 ]; then
  echo "Notes without name and description frontmatter:"
  printf '  %s\n' "${missing[@]}"
fi
if [ "${#conflicts[@]}" -gt 0 ]; then
  echo "Conflicts (left alone, fix by hand):"
  printf '  %s\n' "${conflicts[@]}"
  exit 1
fi
