# Creating a context wiki

Most of a new wiki is the same every time. A script creates that part. The
human decides the rest: where the wiki lives, what belongs in it, and who
shares it.

1. Ask the human three things:
   - the folder for the wiki,
   - its scope: who reads it, and what belongs in it,
   - whether other people share it.

2. Run the script, `scripts/init-wiki.sh` in this skill's base directory:

   ```sh
   <skill-base-dir>/scripts/init-wiki.sh <wiki-folder>
   ```

   The script:

   - creates the wiki folder if it is missing, and runs `git init`,
   - creates `agent-skills/`, `sources/` and `inbox/`, each with an empty
     `.gitkeep` file so that git tracks the folder until it holds
     something,
   - creates the symlinks `.agents/skills`, `.claude/skills` and
     `CLAUDE.md`. They are relative, so they work in every clone.
   - creates the files `AGENTS.md` and `TAGS.md`, and a `.gitignore` so that
     the contents of `inbox/` and personal Claude Code settings are not
     tracked by git.

   The script never overwrites a file, so you can run it again safely. It
   stops if the folder is inside another git repository, because the wiki
   must be the root of its own repository. If that happens, tell the human.
   Do not move anything.

3. Write `README.md` with the human. The Scope section matters most.
   Contributors read it to decide whether an entry belongs in this wiki.
   Suggested format (all sections except Scope are optional):

   ```markdown
   # <Wiki Name>

   <Intro sentence>

   ## Scope

   <What belongs here, what doesn't>

   ## Tips for Readers

   <Help your audience>

   ## Rules for Contributors

   <Guard against noise>
   ```

4. Generate the root `INDEX.md` with the index-md skill. `README.md`,
   `AGENTS.md`, `CLAUDE.md` and `TAGS.md` have no frontmatter, so the
   generator gives them a `<!-- to-do -->` placeholder. Replace each
   placeholder with a short description in `INDEX.md` itself. The generator
   keeps descriptions written there.

5. Commit everything.

6. If the wiki is shared, add the remote with `git remote add origin <url>`.
   Push only when the human says so.

7. Add the folder to `CONTEXT_WIKI_DIRS` on this machine. See
   [context-wiki-dirs.md](context-wiki-dirs.md).

If the folder already holds markdown files, the script leaves them alone.
Each of them becomes an entry and needs a `title` and a `description` in its
frontmatter.
