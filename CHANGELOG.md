# Changelog

## v0.1.0

- Initial preview of `agent-memory`: **governance-layer memory** for AI agents — three permission-separated layers (`control/` read-only authority, `state/` worker-writable working memory, lessons split into approved + pending). Solves agent self-rewrite / authority erosion, **not** retrieval (no vector/graph backend, by design).
- Skills: `resume-context` (load control + task state at start/resume), `lesson-promote` (worker proposes lesson promotion, never self-approves).
- **Standalone-usable in any task** — install footprint carries no completion-gate machinery.
- Permission model maps to `read_only`/`read_write` memory mounts (Claude Code subagent memory / Managed Agents memory stores).
- Spec-compliant frontmatter. Pairs with [`agent-completion-gate`](https://github.com/zhjai/agent-completion-gate) as the optional enforcement layer.
- Designed and reviewed via agent-arena (Claude × Codex), including heterogeneous red-team passes on bypasses (self-policing, lesson laundering).
