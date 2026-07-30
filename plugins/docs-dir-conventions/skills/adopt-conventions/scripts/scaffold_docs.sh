#!/usr/bin/env bash
# Create the docs-dir-conventions baseline in a repository's docs/ directory.
#
# Usage: scaffold_docs.sh [repo-root]   (default: current directory)
#
# Idempotent: creates only what is missing, never overwrites or truncates
# an existing file. Safe to re-run. Optional reference dirs (explanation/,
# how-to-guides/, specs/, adrs/) are deliberately not created here; they
# are created on demand when the first file needs one. No index.md either:
# whether the project keeps one, and how, is the user's call. Seed files
# carry the frontmatter keys but no prefilled wording.
set -euo pipefail

root="${1:-.}"
if [ ! -d "$root" ]; then
  echo "error: not a directory: $root" >&2
  exit 1
fi
docs="$root/docs"

created=()
skipped=()

make_dir() {
  if [ -d "$1" ]; then
    skipped+=("$1/")
  else
    mkdir -p "$1"
    created+=("$1/")
  fi
}

# make_file <path> <content>  -- writes content only if <path> does not exist
make_file() {
  if [ -e "$1" ]; then
    skipped+=("$1")
  else
    printf '%s\n' "$2" >"$1"
    created+=("$1")
  fi
}

# make_keep <dir> -- empty .gitkeep so git tracks the directory
make_keep() {
  if [ -e "$1/.gitkeep" ]; then
    skipped+=("$1/.gitkeep")
  else
    : >"$1/.gitkeep"
    created+=("$1/.gitkeep")
  fi
}

make_dir "$docs"
make_dir "$docs/dev/work/active"
make_dir "$docs/dev/work/completed"
make_dir "$docs/dev/work/abandoned"
make_dir "$docs/dev/references/generated"

make_file "$docs/glossary.md" "$(cat <<'EOF'
---
title: Glossary
description:
---

# Glossary

<!-- Define project-specific jargon here. -->
EOF
)"

make_file "$docs/architecture.md" "$(cat <<'EOF'
---
title: Architecture
description:
---

# Architecture

<!-- Describe the high-level architecture of the project. -->
EOF
)"

make_keep "$docs/dev/work/active"
make_keep "$docs/dev/work/completed"
make_keep "$docs/dev/work/abandoned"
make_keep "$docs/dev/references/generated"

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
