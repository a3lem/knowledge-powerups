---
name: using-specs
description: Load this skill when creating, using, or managing specs for spec-driven development, or when encountering spec files, .delta.md files, statement codes like [2b342], or "spec:" reference comments in a repo.
---

**Prerequisite skills**:

-  /docs-conventions:using-docs

# Using Incremental Specs

## What Is A 'Spec'?

A software spec (short for 'specification') describes the behavior of a system or of one of its capabilities. It describes *what* is (to be) built, not how. It is closely related to 'requirements' in the acceptance criteria/requirements engineering sense. The difference is that a spec may serve as long-term documentation, whereas requirements belong to the time before and during the build, not after. Additionally, the audience is different. Requirements describe the system's behavior from the perspective of its users, whereas specifications describe from the perspective of the technical team.

A spec describes a capability, not a single feature. A capability is a domain concept named with a noun: 'user-registration', 'billing', 'notifications'. A feature-shaped name like 'user-creates-account' reads like a user story, and a spec named after one story has no room for the behavior around it -- verification, expiry, rate limits -- which then scatters over sibling files.

## What Is *Not* A Spec?

Some engineers include the 'how' in their definition of a specification. These are also known as 'design specs'. Design specs are a legitimate part of planning a change; we just don't count them as specs, because 'what' specs serve as long-term documentation whereas 'how' specs become stale.

## Incremental Specs With Spec Deltas

Once the software is built, specs serve as a reference. If the spec was adhered to, the code and the spec should match. Of course, the code will always be more expressive and unambiguous, for that is the whole reason why we use formal programming languages instead of natural language to write programs.

Spec-driven development hearkens back to the days of waterfall. Today, the lifecycle is entirely iterative. Software is never truly 'done'. Inevitably, features are added to a capability, or its described behavior changes. If specs are description and code is implementation, the two must evolve together. A spec that no longer matches the code is worse than no spec.

To do this, distinguish between 'reference specs' on the one hand and **'spec deltas'** on the other. In a spec-driven code base, spec deltas are an ingredient of any non-trivial planned code change. They describe how one or more reference specs are to be updated once the planned code change is implemented and verified. At that point, the reference spec is updated accordingly and the spec deltas are archived along with other parts of the finalized plan.

A spec delta is just a markdown file with sections matching different update operations:

1. `## ADD` -- Append to the reference spec;
2. `## REPLACE` -- Reads like a diff; replace the content of `### OLD` by `### NEW`;
3. `## DELETE` -- Remove the matched string from the spec. Include a one-line reason, since the updated spec won't say why the behavior is gone;
4. `## RENAME` -- Rename the spec and any titles, file names, etc.

Write deltas so that applying them is mechanical: quote enough of the reference spec that each operation matches without judgment. A delta that says 'clarify the expiry wording' forces whoever applies it to improvise; a delta that quotes the old line and gives the new one does not.

## Statement Codes

A behavior statement in a reference spec ends with a code in square brackets: a random 5-character lowercase alphanumeric tag with at least one letter and one digit, so it reads as a code rather than a word or a number.

Codes are a linking tool, not ceremony. Give new statements a code as you write them; it costs seven characters and keeps the statement referenceable the moment a test, an implementation site, or a delta needs to name it. But don't backfill: in an existing spec written without codes, add a code to a statement when something first references it, and leave the unreferenced statements alone.

```markdown
- Verification links expire after 24 hours; using an expired link offers a
  resend. [2b342]
```

The code gives the statement a stable, greppable identity, so code can point at the requirement it implements. Tests reference the statement they verify with a fixed `spec:` marker, the code, and the spec's path:

```python
def test_expired_link_offers_resend() -> None:
    # spec: 2b342 (docs/specs/user-registration.md)
    ...
```

The marker makes every reference findable with one grep, the code pins the statement, and the path leads back to the spec. Add references in implementation code only where it enforces one specific rule (a limit, a duration, a threshold); elsewhere a module-level pointer to the spec file is enough.

Codes are random, so there is no registry to maintain. Generate them with the bundled generator, which prints one code per line:

```
${CLAUDE_PLUGIN_ROOT}/skills/using-specs/scripts/gen-spec-codes.py -k 3
```

Collisions are unlikely, but grep a fresh code before using it.

Codes and deltas interact through quoting: delta operations quote statements verbatim, codes included, so a delta names exactly which codes it touches.

- `## ADD` statements get fresh codes, generated when the delta is written. Tests for the new behavior can then reference the code during implementation, before the reference spec is updated.
- `## REPLACE` keeps the old statement's code in `### NEW` -- same requirement, changed content.
- `## DELETE` retires the code with the statement.
- `## RENAME` leaves codes untouched, but references carry the spec's path, so the rename edits update them.

## Where Everything Goes

Specs (short for 'reference spec') usually live in a dedicated folder. Spec deltas are usually part of a transient code change. Thus, the two live separately. Spec deltas are ultimately archived. Specs either exist or are deleted.

Several **conventions** exist for naming spec and spec delta files. 

### Openspec's `SPEC.md`s

Name of the containing folder represents the name of the spec.

```
openspec/  # top-level folder in repo
  reference/
    <capability>/  # e.g. user-registration
      SPEC.md
  changes/  # planned changes
    <name-of-change>  # e.g. change-user-email-address
      specs/
        <capability>/  # same name as reference spec
          SPEC.md  # spec delta
```

### Adriaan's conventional docs

Specs belong in `docs/`. Name of the spec is in the file name, not folder name. Specs are identified by their context. Reference specs belong in `docs/specs/`. Spec deltas are found in `docs/dev/work/<work-item>/specs/`. Deltas are marked with a `.delta.` infix in the name.

```
./docs/
  specs/
    <capability>.md  # just a markdown file. e.g. user-registration.md
  dev/
    work/
      active/
        <work-item>/
          specs/
            <capability>.delta.md  # e.g. user-registration.delta.md
```

Always check with the user if the preferred convention cannot be inferred from the code base or other instructions.

## Examples

### Spec

`docs/specs/user-registration.md`:

```markdown
# User Registration

A visitor registers with an email address and a password and ends up with an
account they can log in to.

- Registration requires an email address and a password. [k4v2n]
- The email address must not already belong to an account. [8xq1d]
- The registration form tells the visitor when an address is already taken. [w3jp5]
- The password must be at least 12 characters. [e9m4t]
- On success, the system sends a verification email with a one-time link. [p6c8r]
- An account stays unverified until its link is opened; unverified accounts
  cannot log in. [a5hz3]
- Verification links expire after 24 hours; using an expired link offers a
  resend. [2b342]
```

That is the whole template: a title, a sentence of context, and testable behavior statements, each ending in a statement code. Add sections only when a capability has too many statements for a flat list.

Two rules keep the statements testable. Use concrete values ('12 characters', '24 hours'), not vague ones ('sufficiently long', 'promptly'). And don't over-specify: pin down required behavior, not implementation detail, and leave out features nobody has asked for yet.

### Spec Delta

A delta for a planned change (work item `harden-signup`) to the spec above, at `docs/dev/work/harden-signup/specs/user-registration.delta.md`. The file name identifies the target spec, so the delta contains only the operations:

```markdown
## ADD

- At most three verification emails may be sent per address per hour. [f7s0q]

## REPLACE

### OLD

- Verification links expire after 24 hours; using an expired link offers a
  resend. [2b342]

### NEW

- Verification links expire after 1 hour; using an expired link offers a
  resend. [2b342]

## DELETE

- The registration form tells the visitor when an address is already taken. [w3jp5]

Reason: the message leaks which addresses have an account.

## RENAME

user-registration -> signup
```

The `ADD` statement carries a fresh code (`f7s0q`), generated when the delta was written. The `REPLACE` keeps `2b342`: the requirement changed, but it is the same requirement.

Once `harden-signup` is implemented and verified, these edits are applied to `docs/specs/user-registration.md` -- which the rename turns into `docs/specs/signup.md` -- and the delta is archived with the rest of the work item.

## Finishing Up: Apply The Deltas

When the work item's change is implemented and verified -- not before -- apply each delta to its reference spec. Applying early would make the spec describe behavior that doesn't exist yet.

Application is mechanical: perform the operations as written. If an `### OLD` or `## DELETE` string doesn't match the reference spec, the reference has drifted since the delta was written (perhaps another work item touched it first); stop and resolve with the user instead of improvising. `## RENAME` covers the file name, the title, and any references to either.

Applying a delta also syncs `spec:` references in code. Collect the codes the delta touched and grep each one across the repo:

- For `## REPLACE`, check that each referencing test or implementation site still matches the new statement; update the ones that don't.
- For `## DELETE`, remove the references along with the behavior.
- For `## RENAME`, update the spec path inside every `spec:` reference.

A reference that can't be resolved mechanically is flagged to the user, like a delta that no longer matches.

Then archive the delta along with the rest of the work item. A delta under an active work item is pending; an archived one has been applied. Don't leave an applied delta in the active tree -- the next reader can't tell it's already in the spec.
