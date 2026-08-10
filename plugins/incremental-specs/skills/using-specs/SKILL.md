---
name: using-specs
description: Load this skill when creating, using, or managing specs for spec-driven development, or when encountering spec files or .delta.md files in a repo.
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

- Registration requires an email address and a password.
- The email address must not already belong to an account.
- The registration form tells the visitor when an address is already taken.
- The password must be at least 12 characters.
- On success, the system sends a verification email with a one-time link.
- An account stays unverified until its link is opened; unverified accounts
  cannot log in.
- Verification links expire after 24 hours; using an expired link offers a
  resend.
```

That is the whole template: a title, a sentence of context, and testable behavior statements. Add sections only when a capability has too many statements for a flat list.

Two rules keep the statements testable. Use concrete values ('12 characters', '24 hours'), not vague ones ('sufficiently long', 'promptly'). And don't over-specify: pin down required behavior, not implementation detail, and leave out features nobody has asked for yet.

### Spec Delta

A delta for a planned change (work item `harden-signup`) to the spec above, at `docs/dev/work/harden-signup/specs/user-registration.delta.md`. The file name identifies the target spec, so the delta contains only the operations:

```markdown
## ADD

- At most three verification emails may be sent per address per hour.

## REPLACE

### OLD

- Verification links expire after 24 hours; using an expired link offers a
  resend.

### NEW

- Verification links expire after 1 hour; using an expired link offers a
  resend.

## DELETE

- The registration form tells the visitor when an address is already taken.

Reason: the message leaks which addresses have an account.

## RENAME

user-registration -> signup
```

Once `harden-signup` is implemented and verified, these edits are applied to `docs/specs/user-registration.md` -- which the rename turns into `docs/specs/signup.md` -- and the delta is archived with the rest of the work item.

## Finishing Up: Apply The Deltas

When the work item's change is implemented and verified -- not before -- apply each delta to its reference spec. Applying early would make the spec describe behavior that doesn't exist yet.

Application is mechanical: perform the operations as written. If an `### OLD` or `## DELETE` string doesn't match the reference spec, the reference has drifted since the delta was written (perhaps another work item touched it first); stop and resolve with the user instead of improvising. `## RENAME` covers the file name, the title, and any references to either.

Then archive the delta along with the rest of the work item. A delta under an active work item is pending; an archived one has been applied. Don't leave an applied delta in the active tree -- the next reader can't tell it's already in the spec.
