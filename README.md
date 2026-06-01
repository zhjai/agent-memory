# agent-memory

<p align="center">
  <img src="assets/banner.svg" alt="agent-memory — governance-layer memory for AI agents, a permission-separated trust boundary, not retrieval" width="100%">
</p>

<p align="center">
  <strong>English</strong> · <a href="README.zh.md">中文</a>
</p>

<p align="center">
  <img alt="skill" src="https://img.shields.io/badge/agent--skill-agent--memory-1f6feb">
  <img alt="version" src="https://img.shields.io/badge/version-0.1.0-informational">
  <img alt="works with" src="https://img.shields.io/badge/Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20any%20agent-444">
  <img alt="no backend" src="https://img.shields.io/badge/no%20vector%2Fgraph-files%20only-2ea043">
  <a href="LICENSE"><img alt="license" src="https://img.shields.io/badge/license-MIT-yellow"></a>
</p>

> **Governance-layer memory for AI agents** — three permission-separated layers so an agent can carry rules, state, and lessons across tasks **without being able to rewrite its own authority**. Not a retrieval engine; a trust boundary. Usable standalone in **any** task, on **any** agent — Claude Code, Codex, and others.

Most agent-memory products (Mem0, Zep, Letta, LangMem) optimize **retrieval quality** — vector/graph/temporal recall — and assume the agent is cooperative. `agent-memory` solves a different, usually-ignored problem: **a goal-driven agent will quietly downgrade or rewrite "memory" that gets in the way of declaring a task done.** Its core is **who can write what**, not how to embed it.

Plain files + a permission split. Agent-agnostic, portable, zero retrieval dependency. **Use it on its own** — you do not need any completion machinery to benefit from carrying rules/state/lessons across runs.

## The failure it prevents (30 seconds)

A goal-driven agent, mid-task, finds a stable rule inconvenient and "updates" it — or promotes a self-serving "lesson" that weakens a future check. With ordinary memory (everything writable), that silently succeeds.

```
WITH agent-memory (control/ read-only, lessons need review):
  agent edits control/rules.md            → rejected (read-only mount)
  agent writes to approved_lessons/        → rejected (only candidate_lessons/ is writable)
  candidate lesson "skip the case check"   → stays PENDING; never auto-applies as authority
```

The agent can record *proposals*, but cannot rewrite its own authority or self-approve a lesson. `control/` is the trust boundary; `state/` is just its scratchpad. See [`examples/`](examples/).

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

For **long / high-stakes** tasks, add [`agent-completion-gate`](https://github.com/zhjai/agent-completion-gate) — a fail-closed completion gate + four-state machine that reads this kit's read-only `control/` (rules + approved lessons) as the policy it must honor, while bundling its own protected check spec. **agent-memory is the base and stands alone; that kit is the optional enforcement layer on top.**

## Install

```bash
npx skills add zhjai/agent-memory -g -a claude-code   # Claude Code
npx skills add zhjai/agent-memory -g -a codex          # Codex
# … or any other Agent-Skills host — it's plain files + a permission split, no vendor lock-in
```

## Status

`v0.1.0` preview. MIT. Portable, agent-agnostic, file-based, standalone.
