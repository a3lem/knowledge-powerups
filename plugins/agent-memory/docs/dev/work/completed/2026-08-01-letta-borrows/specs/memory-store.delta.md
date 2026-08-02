## ADD

- Memory never stores secrets -- credentials, API keys, tokens: the store
  is a git repository that may leave the machine. A secret stays in the
  environment or a secrets store and is referenced by name. Convention,
  not validated.

Reason: borrowed from the letta-code prompt. Nothing in the conventions or
the contract stopped a session from filing a key it learned; the injected
instructions and keeping-memories now carry the rule, and the spec records
it beside the other unvalidated conventions (first person, atomic files).
A machine check is a separate decision (akps-cb20).
