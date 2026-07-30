---
name: calibrate
description: Review memories with the human -- an interactive pass where the agent states its confidence, the human grades both the claim and that confidence, and each verdict is acted on the same turn. Load on /calibrate, or when asked to review, verify, or challenge the agent's memories.
---

# Calibrating Memory

Validation catches malformed memories; consolidation catches memories the transcripts contradict. A confabulated memory -- well-formed, plausible, never contradicted in any session -- is invisible to both. The human is the only oracle for those, and this skill runs that check as a conversation.

Calibration is why the agent states its confidence out loud. The human grades two things at once: whether the memory is true, and whether the certainty behind it was warranted. A claim held with high confidence and wrong is worth more than a hedged guess that missed -- it marks a place where the agent's sense of its own knowledge is off. Surfacing that keeps miscalibration visible instead of quietly fixing the fact and moving on.

Scope: the human is the authority on facts about themselves and about the world. Within the soul (`system/soul.md`), a role they assigned is theirs outright -- the words are the human's, so a verdict on it is applied as given. The rest of the soul is the agent's own to revise -- feedback on it is input the agent weighs and folds in itself, not a verdict applied mechanically.

## Procedure

1. **Select candidates.** Read `system/` in full and walk the `reference/` index for files whose descriptions promise factual claims. Prefer claims that are consequential if wrong, old, or never confirmed since being written. `system/` files outrank `reference/` ones -- they shape every session.

2. **Present in small batches.** Give each memory as a claim with its source: which file it lives in, and -- when `git log` or `git blame` on that file says so cheaply -- which session or commit wrote it. "I have (from `system/human/identity.md`): you work at Klassif.ai as an AI/ML engineer. Still right?" Plain conversation, a handful of claims at a time, highest value first. Stop when the human has had enough -- a partial pass is fine, and unchecked claims get no mark of any kind.

3. **State your confidence before the verdict.** For each claim, before the human rules, say how sure you are that it holds and why -- "high, confirmed twice last month" or "low, inferred once and never seen again". The order is the whole point: confidence stated after the answer is worthless, and confidence is what makes this calibration rather than correction.

4. **Act on each verdict in the same turn.**
   - Confirmed: the memory stands, untouched.
   - False: fix it to what the human said, or delete it outright. On a deletion, grep the store for the file's root-relative path and rewrite the inbound `[[links]]` yourself -- a dangling link is legal (it reads as a forward pointer), so validation will not flag stragglers.
   - Unresolved: when the human can't say either way, mark the claim disputed where it lives, so the next pass raises it again instead of trusting it.

5. **Record the confident misses.** When a claim held with high confidence turns out false, correcting the fact is not the whole lesson -- the calibration error is. Record it: a self-correction file under `system/core/` when it names a pattern worth heeding every session, or a dated note in `reference/history/` when it is a one-off worth remembering. A hedged guess that missed needs no such note; the confidence matched the outcome.

6. **Report.** Close with counts -- confirmed, corrected, deleted, disputed -- and where the fixes and notes landed.

Calibration is sampling, not an audit. A few high-value claims per pass, run occasionally, keeps memory honest and the agent's confidence tied to reality without spending the human's patience.
