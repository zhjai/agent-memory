# agent-memory

> **Governance-layer memory for AI agents** — three permission-separated layers so an agent can carry rules, state, and lessons across tasks **without being able to rewrite its own authority**. Not a retrieval engine; a trust boundary. Usable standalone in **any** task.

Most agent-memory products (Mem0, Zep, Letta, LangMem) optimize **retrieval quality** — vector/graph/temporal recall — and assume the agent is cooperative. `agent-memory` solves a different, usually-ignored problem: **a goal-driven agent will quietly downgrade or rewrite "memory" that gets in the way of declaring a task done.** Its core is **who can write what**, not how to embed it.

Plain files + a permission split. Agent-agnostic, portable, zero retrieval dependency. **Use it on its own** — you do not need any completion machinery to benefit from carrying rules/state/lessons across runs.

## The three layers (by permission, not by content)

```
🔒 control/   read-only to the worker (human / CI maintains)
   rules.md                 stable rules the agent must obey, cannot edit
   approved_lessons/        reviewed, promoted lessons
     index.yaml             summary-first index

✍️ state/     worker-writable, NOT a source of truth
   tasks/<task_id>/
     run_state.yaml         task checkpoint (belief, not truth) — not cross-task knowledge
     decision_log.md        decisions / risks during the task
     candidate_lessons.md   newly observed lessons, PENDING review (no self-approve)
```

**Invariants:**
- Worker **cannot write `control/`** — mount it `read_only` (Claude Code subagent memory / Managed Agents memory stores enforce read_only vs read_write at the filesystem level; use that, don't build your own).
- `state/` is **working memory, not truth** (`run_state` = "what the agent believes it did").
- New lessons go to `candidate_lessons.md`; **promotion to `approved_lessons/` is a reviewed action — the worker proposes, never self-approves.**
- Promotion **cannot weaken enforcement** — completion truth sources (gates, manifests, verifier prompts in [`agent-completion-gate`](https://github.com/zhjai/agent-completion-gate)) are not reachable by lesson promotion.

## Standalone use (any task, not just long ones)

You don't need gates or long-task machinery:
1. `resume-context` reads `control/rules.md` (e.g. project naming conventions) at start.
2. Write decisions to `state/.../decision_log.md` as you go.
3. On wrap-up, `lesson-promote` files keepers into `candidate_lessons.md`.

**Install footprint is provably standalone:** installing `agent-memory` into a fresh project pulls in **no gate files, no gate config, no completion machinery** — just the three layers + two skills.

## Skills (process, not authority)

- [`resume-context`](skills/resume-context/SKILL.md) — load control + task state at start/resume; surface active constraints + relevant lessons.
- [`lesson-promote`](skills/lesson-promote/SKILL.md) — turn observations into promotion *proposals* (worker proposes only).

## vs mainstream memory

We deliberately ship **no vector/graph backend** (Mem0's documented weakness: multi-store complexity, schema design, paywalled graph, lock-in). Lessons use summary-first frontmatter + an index; add retrieval only if recall volume demands it. Our value is the **governance/permission boundary**, not retrieval — the thing mainstream memory libraries omit.

## Pairs with agent-completion-gate

For **long / high-stakes** tasks, add [`agent-completion-gate`](https://github.com/zhjai/agent-completion-gate) — a fail-closed completion gate + four-state machine that reads this kit's read-only `control/` to decide completion. **agent-memory is the base and stands alone; that kit is the optional enforcement layer on top.**

## Install

```bash
npx skills add zhjai/agent-memory -g -a claude-code
```

## Status

`v0.1.0` preview. MIT. Portable, agent-agnostic, file-based, standalone.
