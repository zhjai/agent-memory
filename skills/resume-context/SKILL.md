---
name: resume-context
description: Use at the start or resume of any task (especially long or multi-session tasks) to load the lessonbook before acting — read the read-only control rules and approved lessons plus the task's working state, and surface the active constraints for this run. Use when starting/resuming work, picking up a long task, or when continuity across sessions matters. Do not use for one-shot factual lookups with no prior state.
license: MIT
metadata:
  version: "0.3.0"
  author: zhjai
  tags: "lessonbook, resume, context, active-constraints, long-task, continuity"
  related_skills: "correction-capture, lesson-propose"
---

# Resume Context

## When to use
- Starting or resuming a task that has prior state, rules, or lessons.
- Long / multi-session / multi-stage work where chat context is unreliable.

## Procedure
1. Read `control/rules.md` (read-only authority — you must obey, cannot edit).
2. Read `control/approved_lessons/index.yaml`; pull the lessons relevant to this task by their summaries (load full lesson files only as needed — progressive disclosure).
3. Read the task's `state/tasks/<task_id>/run_state.yaml` (working memory — what was believed/done so far; **not** ground truth) and its `correction_journal.md` if present.
4. Produce an **active_constraints** list (from rules + relevant approved lessons + any journal entries from earlier in this task) and a short **relevant_lessons** summary.
5. Any unmet precondition or open question → record it in `state/tasks/<task_id>/run_state.yaml` (do not silently proceed past it).

## Outputs
- Updated `run_state.yaml` (resume marker, active_constraints).
- A short "active constraints + relevant lessons" summary for this session.

## Do not
- Do not treat `run_state.yaml` as proof a condition is met — it records belief, not verified state.
- Do not edit `control/`. If a rule seems wrong, file a `candidate_lessons` proposal; do not change authority yourself.
