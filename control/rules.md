# Agent Rules (read-only authority)

> Maintained by humans / CI. The worker agent **must obey these and cannot edit them**.
> Mount this directory `read_only`. Edits go through review, not through the agent.

## Memory discipline

1. Long-task key decisions, completion conditions, and user-stated long-lived requirements must be **externalized to persistent files**, never left only in chat history.
2. On resume, first read `control/rules.md`, the relevant `approved_lessons/`, and the task's `state/run_state.yaml` before continuing.
3. `state/` (`run_state`, `decision_log`, `candidate_lessons`) is **working memory, not a source of truth**. It records what the agent believes, not what the system has verified.
4. A newly discovered long-lived constraint goes into `candidate_lessons.md` as **pending**. The worker may propose promotion but **must not treat it as an approved rule** until review moves it into `approved_lessons/`.

## Authority

5. The worker agent does not edit `control/`, does not approve its own lessons, and does not grant itself completion authority.
6. **Lesson promotion cannot weaken enforcement.** Completion-control truth sources (gate scripts, acceptance manifests, surface inventories, verifier prompts) are human/CI-maintained and are NOT reachable by lesson promotion. A lesson learned in a low-stakes run must never silently relax a high-stakes gate ("lesson laundering"). Promoting a lesson that touches enforcement requires explicit human review at the enforcement tier, not the lesson tier.

<!--
Add project-specific stable rules below (naming conventions, artifact-hygiene defaults, etc.).
Keep this file short — it is a constitution, not a manual. Long procedures belong in skills.
-->
