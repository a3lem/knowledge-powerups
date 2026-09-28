#!/usr/bin/env bash
# Create the fixed parts of a context wiki: the git repository, the reserved
# folders, the symlinks and the special files whose content never varies.
#
# Usage: init-wiki.sh [wiki-root]   (default: current directory)
#
# Idempotent: creates only what is missing, never overwrites an existing
# file. Safe to re-run. README.md and the root INDEX.md are not created
# here: README.md needs the wiki's scope, which only the human knows, and
# INDEX.md comes from the index-md skill. Nothing is committed.
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
make_dir sources
make_dir inbox
make_dir .agents
make_dir .claude
make_keep agent-skills
make_keep sources
make_keep inbox

make_link .agents/skills ../agent-skills
make_link .claude/skills ../agent-skills

make_file AGENTS.md "$(cat <<'EOF'
This folder is a context wiki. Load the context-wiki skill before you read
or change it. Start at the README.md next to this file.
EOF
)"
make_link CLAUDE.md AGENTS.md

make_file TAGS.md "# Tags"

# inbox/* rather than inbox/: git does not look inside an ignored folder, so
# the .gitkeep exception would have no effect.
make_file .gitignore "$(cat <<'EOF'
# Raw material waiting for ingestion. Stays on this machine.
inbox/*
!inbox/.gitkeep

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
if [ "${#conflicts[@]}" -gt 0 ]; then
  echo "Conflicts (left alone, fix by hand):"
  printf '  %s\n' "${conflicts[@]}"
  exit 1
fi
