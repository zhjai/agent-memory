# Triggers — making capture happen (without auto-recording everything)

`agent-lessonbook`'s weak spot vs built-in auto memory is that capture is a *skill the agent
invokes* — if it doesn't invoke it at a correction moment, the review queue starves. These
integrations reduce that, **without** turning the tool into "record everything". They only
**trigger / nudge**; the model still decides what's a real, capture-worthy correction (the 5
types), and a human still promotes. No trigger ever writes a final lesson.

## The ladder (use as much as your host supports)

| Rung | What it is | Works on | Catches |
|------|------------|----------|---------|
| **Skill** (floor) | the agent calls `correction-capture` | every host | whatever the agent chooses to capture |
| **+ Soft nudge** | one line in `CLAUDE.md` / `AGENTS.md` ([`templates/lessonbook-nudge.md`](../templates/lessonbook-nudge.md)) | every host that reads those files | explicit corrections ("remember this", "you were wrong") |
| **+ Hard hooks** | lifecycle hooks → [`hooks/lessonbook_hook.py`](hooks/lessonbook_hook.py) | Claude Code, Codex | **deterministic** events the model rationalizes away: a tool/check failing, compaction about to drop context |

**Soft is enough for human-led corrections** (the model has to judge them anyway). **Hooks earn
their keep only for deterministic drift / context-loss** — a non-zero tool exit, or `PreCompact`
about to discard the correction context. Don't expect hooks to "understand" corrections; that's
the model's job.

## What the hooks do (all trigger-only)

`hooks/lessonbook_hook.py` reads one event on stdin (Claude Code or Codex) and:

- **UserPromptSubmit** — coarse keyword pre-filter for a likely correction → nudges the model to consider `correction-capture` (conservative; the model still decides).
- **PostToolUse** — on a failed tool/check → nudges to record the root cause as drift.
- **PreCompact** — writes an **UNREVIEWED** pending placeholder to the inbox (`LESSONBOOK_INBOX`, default `state/lessonbook/inbox.md`) so a correction isn't lost to compaction. PreCompact **cannot inject context on either host** (the schema forbids it), so this is a pure side-effect — `resume-context` surfaces the inbox next session. The placeholder is **not** a lesson and **not** approved; the inbox path is forced out of `control/` and away from journals/candidate files so a mis-set `LESSONBOOK_INBOX` can't pollute authority, and `transcript_path` is sanitized so it can't forge headings.

It never writes a final journal entry, never promotes, and on bad/empty input it exits 0 (never breaks your session).

## Install

The hook script lives in this repo (skills install the *skill*, not `integrations/`). Point the
hook command at a checkout, or copy `integrations/hooks/lessonbook_hook.py` into your project.

- **Claude Code** — merge [`claude-code/settings.hooks.json`](claude-code/settings.hooks.json) into `.claude/settings.json`; fix the path.
- **Codex** — use [`codex/hooks.json`](codex/hooks.json) or the inline [`codex/config.toml.example`](codex/config.toml.example).
- **Soft nudge (recommended everywhere)** — paste [`templates/lessonbook-nudge.md`](../templates/lessonbook-nudge.md) into `CLAUDE.md` / `AGENTS.md`.

## Honest cross-host caveat

**One shared script, two host-specific configs.** The *injection format is the same on both* (verified against Codex `rust-v0.135.0` schemas + Claude Code docs): `{"hookSpecificOutput": {"hookEventName": "<Event>", "additionalContext": "…"}}` for `UserPromptSubmit`/`PostToolUse`. So `lessonbook_hook.py` is **one** script (no `--host` flag). What differs is only the **config file format** (Claude `settings.json` vs Codex `hooks.json`/`config.toml`) plus two real input gaps:

- **Codex `PostToolUse` exposes no numeric exit code** (only `tool_response`), so the failure→drift nudge is **best-effort** on Codex (it matches strong `traceback`/`error:`/`fatal`/non-zero-exit text, and skips `0 errors`/`success`). On Claude Code it uses the real `tool_exit_code`.
- **`PreCompact` cannot inject context on either host** — it only writes the inbox; the model sees it next session via `resume-context`.

The capture *logic* lives only in the skill; these hooks are thin triggers, so the two configs can't drift apart in behavior.

The capture *logic* lives only in the skill; these hooks are thin triggers, so the two host configs can't drift apart in behavior.
