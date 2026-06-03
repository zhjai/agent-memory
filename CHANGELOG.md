# Changelog

## v0.3.0

- **Defined the capture scope deliberately (a tight top-5), and held the line against scope creep.** `agent-lessonbook` records only evidence-backed observations that should carry forward *and* that the worker shouldn't self-canonize: (1) user corrections / acceptance prefs, (2) drift root-causes, (3) correction-backed negative constraints, (4) repo pitfalls proven by failure, (5) authority-relevant architecture constraints. Everything else is explicitly **delegated** elsewhere (test/verify recipes → README/Makefile/CI; conventions/env → CLAUDE.md/AGENTS.md/lockfiles; task status/open questions → `run_state.yaml`; personal output style → built-in memory). The edge is *review-before-authority on high-signal evidence*, not "remember everything".
- `correction-capture` broadened from corrections/drift to the 5 typed entries (`correction` / `drift` / `negative_constraint` / `pitfall` / `architecture_constraint`), with a "what NOT to capture" guardrail and a required-evidence rule for pitfalls/constraints. No new journal files, no new skill — types collapse into `correction_journal.md`.
- README: added the "What it captures (and what it doesn't)" section and the tagline "*reviewed corrections, constraints, and lessons the project carries forward — not tutorials*". (Name `agent-lessonbook` kept — a second rename in days wasn't justified; the slight under-claim is handled by copy.)

## v0.2.0

- **Renamed `agent-memory` → `agent-lessonbook`** and repositioned. The differentiator is **review-before-authority** + **correction/drift capture**, not retrieval — it doesn't compete with Mem0/Zep/Letta/LangMem or built-in agent memory; it sits on top as the review boundary. README is problem-first ("you correct the agent mid-task and it forgets / silently self-authorizes"), with the honest caveat that it captures drift when something *exposes* it and does not make the agent reliably notice its own drift.
- **Skills (now 3, all worker-side process, none can grant authority):**
  - `resume-context` — narrowed to: load `control/` + task state, surface this run's active constraints.
  - `correction-capture` — **new.** Record a mid-task clarification or an exposed drift to `correction_journal.md` and add it to active constraints so it isn't forgotten/repeated.
  - `lesson-propose` — **renamed from `lesson-promote`** (the worker proposes, never promotes; the old name implied it could grant authority). Classifies candidates by tier for human review.
  - Promotion (candidate → `control/`) is deliberately **not a skill** — a human git action, so the worker can never reach authority through tool use.
- **Fully decoupled from `agent-completion-gate`.** No dependency either way; the gate never reads this lessonbook at runtime. The only link is human-mediated. Removed gate-specific fields from `templates/run_state.yaml`.
- Dropped the "vs Mem0 documented weakness" comparison in favor of a neutral "Where this fits".

## v0.1.0

> Historical snapshot, under the old name `agent-memory` and the old "governance-layer memory" framing. Superseded by v0.2.0 (renamed to `agent-lessonbook`, repositioned around correction/drift capture + review-before-authority, decoupled from the gate). Kept for provenance.

- Initial preview of `agent-memory`: **governance-layer memory** for AI agents — three permission-separated layers (`control/` read-only authority, `state/` worker-writable working memory, lessons split into approved + pending). Solves agent self-rewrite / authority erosion, **not** retrieval (no vector/graph backend, by design).
- Skills: `resume-context` (load control + task state at start/resume), `lesson-promote` (worker proposes lesson promotion, never self-approves).
- **Standalone-usable in any task** — install footprint carries no completion-gate machinery.
- Permission model maps to `read_only`/`read_write` memory mounts (Claude Code subagent memory / Managed Agents memory stores).
- Spec-compliant frontmatter. Pairs with [`agent-completion-gate`](https://github.com/zhjai/agent-completion-gate) as the optional enforcement layer.
- Designed and reviewed via agent-arena (Claude × Codex), including heterogeneous red-team passes on bypasses (self-policing, lesson laundering).
