---
name: lesson-promote
description: Use after a task, a mistake, or a postmortem to externalize newly-learned lessons as review proposals — classify each lesson by target tier (working-only / approved-lesson / policy / gate) and write a promotion note, without self-approving. Use when wrapping up a task, after something went wrong, or when the user gives a correction that should persist. Do not use to grant a lesson authority directly — the worker proposes, humans/CI approve.
license: MIT
metadata:
  version: "0.1.0"
  author: zhjai
  tags: "agent-memory, lessons, postmortem, promotion, governance-memory"
  related_skills: "resume-context"
---

# Lesson Promote

## When to use
- Task wrap-up, postmortem, or when the user gives a correction meant to last.

## Procedure
1. Extract each lesson from `state/tasks/<task_id>/candidate_lessons.md` (or the session).
2. Tag each lesson with a **target tier**:
   - `working-only` — relevant to this task only; stays in `state/`.
   - `approved-lesson-candidate` — recurring; propose into `control/approved_lessons/`.
   - `policy-candidate` — stable, cross-task; propose into `control/rules.md`.
   - `gate-candidate` — binary, machine-checkable; propose as a deterministic check (see completion-control-kit).
3. Write a **promotion note** listing each lesson, its proposed tier, and the evidence.
4. Leave the lessons in `candidate_lessons.md` (pending). **Do not move anything into `control/` yourself.**

## Outputs
- Updated `candidate_lessons.md` with tier tags.
- A promotion note for human/CI review.

## Do not
- Do not write to `control/approved_lessons/` or `control/rules.md` — those are read-only to the worker; promotion is a reviewed action.
- Do not mark a lesson "enforced" without a corresponding rule/gate actually carrying it.
