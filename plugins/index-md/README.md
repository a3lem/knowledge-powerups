# index-md

Index files (`index.md`): per-directory tables of contents that make file trees discoverable to agents.

Skills: `index-md`.

Dependencies: the generator script lives in the repo's shared `cli/generate_index.py` (stdlib-only), two levels above the plugin root -- the skill and the agent-memory hooks both call it, so this plugin assumes it is used from the repo checkout.
