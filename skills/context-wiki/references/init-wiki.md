# Creating a context wiki

A script creates what every new wiki starts with. The human decides the
rest: where the wiki lives, what belongs in it, and who shares it.

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
   - creates `AGENTS.md`, and `CLAUDE.md` as a symlink to it,
   - creates `agent-skills/` with an empty `.gitkeep` file, so that git
     tracks the folder before it holds a skill,
   - creates `.agents/skills` and `.claude/skills` as symlinks to
     `agent-skills/`. They are relative, so they work in every clone.
   - writes into `AGENTS.md` the command that generates the wiki's
     `INDEX.md` files.
   - creates a `.gitignore` so that personal Claude Code settings are not
     tracked by git.

   The script never overwrites or moves a file, so you can run it again
   safely. It stops if the folder is inside another git repository, because
   the wiki must be the root of its own repository. If that happens, tell
   the human. Do not move anything.

   If the folder already holds markdown files, the script lists those
   without `name` and `description` frontmatter. Each of them is a note and
   needs both fields. Add them with the human's agreement.

3. Write `README.md` with the human. The Scope section matters most.
   Contributors read it to decide whether a note belongs in this wiki.
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

4. Ask the human which of the skill's other defaults the wiki adopts, such
   as `sources/`, `inbox/`, rooted links, a glossary or tags. Set up each
   one, list it under Conventions in `AGENTS.md`, and add any folder that
   should not be indexed to the index command there.

5. Create the `INDEX.md` files by running the index command in
   `AGENTS.md`. It creates one in every folder it indexes, including empty
   ones such as a new `sources/`. In the root `INDEX.md`, replace the H1
   with the wiki's name and write a one-line description below it. In each
   other new `INDEX.md`, write a description that says what belongs in that
   folder. `README.md` and `AGENTS.md` have no frontmatter, so the
   generator gives them a `<!-- to-do -->` placeholder and suggests adding
   frontmatter. Instead, replace each placeholder with a short description
   in the root `INDEX.md` itself. The generator keeps descriptions written
   there. Run the command again, so that the root index picks up the
   descriptions of the folders below it.

6. Commit everything.

7. If the wiki is shared, add the remote with `git remote add origin <url>`.
   Push only when the human says so.

8. Add the folder to `CONTEXT_WIKI_DIRS` on this machine. See
   [context-wiki-dirs.md](context-wiki-dirs.md).
