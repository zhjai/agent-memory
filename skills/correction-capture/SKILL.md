---
name: correction-capture
description: Use the moment evidence appears that should influence FUTURE execution and would be wrong for the worker to treat as authority on its own — a user correction/clarification ("actually…", "you skipped X again"), exposed drift (a check fails, a miss is pointed out), a proven repo pitfall, a "never do X" constraint, or an authority-relevant architecture constraint. Record it to the task's correction journal with a type, and add active ones to run_state constraints. Do not use for routine progress, or for things that belong in the repo (test commands, conventions, env) or built-in memory. Captures evidence when something exposes it; it does not make the agent notice drift on its own.
license: MIT
metadata:
  version: "0.3.1"
  author: zhjai
  tags: "lessonbook, corrections, drift, constraints, pitfalls, journal"
  related_skills: "resume-context, lesson-propose"
---

# Correction Capture

Capture **evidence-backed** observations that should carry forward AND that need human review
before becoming authority. A clarified requirement and an exposed drift are often the same moment
("you skipped the baseline again" is both). One journal, one skill. The worker records; it never
gains authority.

## What to capture (the only 5 types)

| type | example | why it needs the review gate |
|------|---------|------------------------------|
| `correction` | user: "actually, chart titles must include the run name" | the worker shouldn't self-canonize "what the user wants" |
| `drift` | a check failed because a constraint wasn't loaded | root cause, so the next run doesn't repeat it |
| `negative_constraint` | "never auto-promote a lesson" | a "don't do X" that must not be silently relaxed |
| `pitfall` | "running test A without env B gives false confidence" | a repo trap **proven by a failure**, not a guess |
| `architecture_constraint` | "approved lessons live in control/; workers can't write there" | a design rule that, if wrongly rewritten, breaks the trust model |

> Captures evidence when something **exposes** it (a user, a check, a concrete self-observed error). It does **not** guarantee the agent notices its own drift unprompted.

## What NOT to capture here (belongs elsewhere — keeps the journal high-signal)
- How to run tests / validate the repo → the repo's README / Makefile / CI.
- Project conventions, env/dependency setup → `CLAUDE.md` / `AGENTS.md` / lockfiles.
- Current task status, open questions → `run_state.yaml` (no review needed — it's scratch).
- Your personal output preferences (language, patch-vs-prose) → built-in agent memory, not this repo.

## Procedure
0. **Triage the inbox first** (if you use the optional hooks). A `PreCompact` hook may have left
   `status: UNREVIEWED` placeholders in `state/lessonbook/inbox.md` (`$LESSONBOOK_INBOX`). Review
   each: if it points at a real correction/drift, turn it into a typed journal entry below and
   clear it; if it's noise, drop it. The inbox is a machine-written pointer, never authority —
   don't let it rot.
1. Append an entry to `state/tasks/<task_id>/correction_journal.md`:
   ```md
   ## <date> — <type>            # correction | drift | negative_constraint | pitfall | architecture_constraint
   Trigger:  <what surfaced it: user said X / check Y failed / self-observed>
   Expected: <what should have happened>      # (correction/drift)
   Actual:   <what happened>                  # (correction/drift)
   Evidence: <the failure / quote that backs this — required for pitfall/constraint>
   Prevention: <concrete check or step to avoid repeating it>
   Scope: task-only | candidate for future tasks
   ```
2. If it's an active requirement for the rest of this task, add it to `run_state.yaml`'s `active_constraints` immediately — so it's honored three steps later, not forgotten.
3. If `Scope` is "candidate for future tasks", flag it so `lesson-propose` picks it up at wrap-up. **Do not** promote it yourself.

## Outputs
- Appended `correction_journal.md` entry (typed).
- Updated `run_state.yaml` `active_constraints` (when it applies to the rest of the task).

## Do not
- Do not write to `control/` — these are worker observations, not authority, until a human reviews them.
- Do not silently "absorb" a correction without recording it — recording is the point (so it survives compaction and the next session).
- Do not over-capture: routine progress is not an entry, and a `pitfall`/constraint needs real **evidence** (a failure), not a hunch. Fewer, higher-trust entries beat a noisy journal.
