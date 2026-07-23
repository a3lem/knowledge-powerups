A collection of AI agent plugins for storing and organizing new information, so that
knowledge compounds over consecutive agent sessions.

# Knowledge Management Plugins

## A Principled Approach

The brains of an AI agent, the LLM, is a static artifact, unchanging through use.
All an LLM 'knows' is what was trained into its weights and what is available
in the token context window.

This intrinsic weakness of LLMs is addressed by the 'harness' of the agent,
i.e. the software wrapping the model and turning it into a functional agent.
This is an active area of work, with nearly all agent harnesses offering one or
more kinds of simulated memory, and with a whole cottage industry of memory SaaS
products offering to do even better.

The dream is to never have to onboard an agent onto the same thing twice, to
never have to explain a particularity of your context before starting, to never
have to kindly request that the agent burns more tokens on re-exploring the
files in a project.

All users of AI agents want more or less the same thing: to feel that their agent
is getting smarter across sessions by reusing knowledge it gained previously.

[...]

### Goals

1. For any piece of knowledge, there is exactly *one* obvious place to store it.
2. Following from (1), information shall not be duplicated.
3. Distinguish between stable, authoritative information and [...]
4. ...


## Three pillars

### 1. Conventional Code Docs

AI agents make great assistants for software engineers. When working in a
code base, these 'coding agents' are happy to write files to the documentation
folder, usually abbreviated to `docs/`.

### 2. Context Wikis


### 3. Auto-memory


## 
