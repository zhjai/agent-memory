---
name: lesson-propose
description: Use at task wrap-up, after a mistake, or on a postmortem to turn the correction journal and observations into review PROPOSALS — classify each candidate lesson by target tier (working-only / approved-lesson / policy / gate-candidate) and write a proposal note, without self-approving. Use when wrapping up, after something went wrong, or when a correction should persist. Do not grant a lesson authority — the worker proposes, a human promotes.
license: MIT
metadata:
  version: "0.3.0"
  author: zhjai
  tags: "lessonbook, lessons, postmortem, proposal, review"
  related_skills: "correction-capture, resume-context"
---

# Lesson Propose

The worker **proposes** lessons; it never promotes them. Promotion (candidate →
`control/approved_lessons/` or `rules.md`) is a human git action, not a tool the worker can call.

## When to use
- Task wrap-up, postmortem, or when a correction/drift note should outlive this task.

## Procedure
1. Read `state/tasks/<task_id>/correction_journal.md` and any session observations.
2. For each keeper, write a candidate into `state/tasks/<task_id>/candidate_lessons.md`, tagged with a **target tier**:
   - `working-only` — relevant to this task only; stays in `state/`.
   - `approved-lesson-candidate` — recurring; propose into `control/approved_lessons/`.
   - `policy-candidate` — stable, cross-task; propose into `control/rules.md`.
   - `gate-candidate` — binary, machine-checkable; a human may translate it into an `agent-completion-gate` check (this skill does NOT touch the gate).
3. Each candidate carries: the lesson, evidence (cite the journal entry), `applies_when`, and `not_authoritative_until_reviewed: true`.
4. Leave everything in `candidate_lessons.md` (pending). **Do not move anything into `control/` yourself.**

## Outputs
- `candidate_lessons.md` with tier-tagged proposals + evidence.
- A short summary the human can review and promote in git.

## Do not
- Do not write to `control/approved_lessons/` or `control/rules.md` — read-only to the worker; promotion is a reviewed action.
- Do not edit any `agent-completion-gate` manifest. Surfacing a `gate-candidate` is a suggestion to a human, not an action.
- Do not mark a lesson "enforced" without a corresponding rule/gate actually carrying it.
