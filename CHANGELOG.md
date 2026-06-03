# Changelog

## v0.3.1

- **Repositioned vs built-in agent memory** (verified June 2026: Claude Code auto memory + Codex memories both auto-record engineering details — but are *recall* layers, not authority; vendors' own docs put "rules that must always apply" in CLAUDE.md/AGENTS.md). README now says it plainly — lessonbook doesn't compete on recall (it's weaker there); it's the git-reviewed gate that decides which lessons become project authority. Tagline: "built-in auto memory helps an agent remember what it *thinks* it learned; lessonbook decides which become authority for every agent on the repo."
- **Triggers** (`integrations/`) so capture isn't starved (it's a skill the agent must invoke), without becoming "auto-record everything":
  - `integrations/hooks/lessonbook_hook.py` — a thin, **trigger-only** hook for **both Claude Code and Codex**: `UserPromptSubmit` nudges on a likely correction, `PostToolUse` nudges on a failed tool/check, `PreCompact` writes an **UNREVIEWED** pending to the inbox so a correction isn't lost to compaction. It never writes a final lesson, never promotes, and exits 0 on bad input.
  - **One** shared hook script (output validated against the real host schemas — Codex `rust-v0.135.0` + Claude Code docs — both use `{"hookSpecificOutput":{"hookEventName","additionalContext"}}`); **two** host-specific config files (`integrations/claude-code/settings.hooks.json` vs `integrations/codex/hooks.json` + `config.toml.example`). Honest caveats: Codex `PostToolUse` exposes no numeric exit code (failure→drift is best-effort, and skips `0 errors`/`success`), and `PreCompact` can't inject context on either host (it only writes the inbox).
  - Security: the inbox path is forced out of `control/` and away from journals/candidate files (a mis-set `LESSONBOOK_INBOX` can't pollute authority), and `transcript_path` is sanitized so it can't forge headings/actions in the inbox.
  - Host-agnostic soft nudge `templates/lessonbook-nudge.md` (a CLAUDE.md/AGENTS.md line — the floor that works on every host).
  - `correction-capture` / `resume-context` now triage the hook-written inbox, so unreviewed placeholders don't rot.
- Discipline held: triggers only remind/flag; the model still judges the 5 types and a human still promotes. No Stop blocking, no classifier, no auto-record.

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
