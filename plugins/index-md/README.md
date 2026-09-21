# index-md

Index files (`index.md`): per-directory tables of contents that make file trees discoverable to agents.

Skills: `index-md`.

An `index.md` is plain markdown: an H1 and a description paragraph written by hand, a generated list of the directory's members, and an optional `<!-- pinned -->` block the generator copies through verbatim.

Dependencies: the generator script lives in the repo's shared `cli/generate_index.py` (stdlib-only), two levels above the plugin root, so this plugin assumes it is used from the repo checkout. Its behaviour is specified in `docs/specs/directory-index.md` and tested by `cli/test_generate_index.py`.
