<!-- Paste this into your project's CLAUDE.md (Claude Code) and/or AGENTS.md (Codex).
     It's the host-agnostic SOFT trigger — read every session, no code, no maintenance.
     It's the floor that works on every host (Cursor, Gemini CLI, etc.); hooks add a hard
     trigger on top where the host supports them. -->

## agent-lessonbook

When the user corrects or clarifies you mid-task ("actually…", "not like that", "from now on…"),
or a tool/check exposes drift, or compaction may lose that context: call **correction-capture**.
Record only the 5 evidence-backed types (correction / drift / negative_constraint / pitfall /
architecture_constraint) and **nominate** them as candidates — never auto-promote. Promotion to
`control/` is a human git action.
