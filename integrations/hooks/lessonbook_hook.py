#!/usr/bin/env python3
"""lessonbook_hook.py — a THIN, trigger-only hook for agent-lessonbook capture.

Reads one lifecycle event on stdin (Claude Code OR Codex — verified compatible) and either:
  - UserPromptSubmit / PostToolUse: emits a context NUDGE so the model considers correction-capture, or
  - PreCompact: writes an UNREVIEWED pending placeholder to the inbox so a correction isn't lost to
    compaction (PreCompact cannot inject context on either host — schema forbids it — so this is a
    pure side-effect; resume-context surfaces the inbox next session).

It NEVER writes a final lesson, never promotes, never blocks a prompt/tool, and exits 0 on bad input.
Capturing the right thing stays the model's job (the 5 types); promotion stays the human's.

Output format (valid on Claude Code AND Codex v0.135.0):
  {"hookSpecificOutput": {"hookEventName": "<Event>", "additionalContext": "<text>"}}

Env: LESSONBOOK_INBOX (default state/lessonbook/inbox.md). It is force-kept out of control/ and
away from journals/candidate files, so a mis-set value can't pollute authority.
"""
import datetime, json, os, pathlib, re, sys

# Coarse pre-filter for a likely correction. The model still decides if it's real and which of the
# 5 types it is — keep this to fairly unambiguous correction phrases to avoid alert fatigue.
CORRECTION_SIGNALS = (
    "not like that", "that's not", "thats not", "no, that", "you missed", "you skipped",
    "you forgot", "you broke", "don't do", "stop doing", "from now on",
    "i told you", "i said ", "i asked you",
    "不是这样", "别再", "跑偏", "我说过", "以后不要", "以后都", "你漏", "你跳过", "你忘了", "你搞错",
)
# Strong failure signals (used when no numeric exit code is available, e.g. Codex PostToolUse),
# with a guard so "0 errors" / "success" don't false-trigger.
_FAIL = re.compile(r"\btraceback\b|\berror:|\bfatal\b|command failed|exit (?:code |status )?[1-9]|non-zero exit", re.I)
_OK = re.compile(r"\b0 errors?\b|\bno errors?\b|\bsuccess\b|\bpassed\b", re.I)


def tool_failed(d):
    code = d.get("tool_exit_code")
    if isinstance(code, int):
        return code != 0  # Claude: reliable
    resp = str(d.get("tool_response", "") or d.get("tool_output", ""))  # Codex: best-effort
    return bool(_FAIL.search(resp)) and not _OK.search(resp)


def _sanitize(s):
    # collapse newlines/tabs/backticks so an attacker-controlled path can't forge headings/fences
    return (re.sub(r"[\r\n\t`]", " ", str(s)).strip()[:200]) or "?"


def safe_inbox():
    p = pathlib.Path(os.environ.get("LESSONBOOK_INBOX", "state/lessonbook/inbox.md"))
    bad = ("control" in {x.lower() for x in p.parts}
           or p.name in {"rules.md", "candidate_lessons.md"}
           or p.name.endswith("_journal.md"))
    return pathlib.Path("state/lessonbook/inbox.md") if bad else p  # never pollute authority/journals


def nudge(event, d):
    if event == "UserPromptSubmit":
        p = str(d.get("prompt", "")).lower()
        if any(s in p for s in CORRECTION_SIGNALS):
            return ("Possible user correction. Consider agent-lessonbook correction-capture: record it "
                    "as one of the 5 evidence-backed types and nominate it as a candidate — never auto-promote.")
    elif event == "PostToolUse":
        if tool_failed(d):
            return ("A tool/check failed. If it exposed drift, use correction-capture to record the root "
                    "cause (one of the 5 types) — don't move on silently.")
    return None


def write_pending(d):
    p = safe_inbox()
    p.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    entry = (f"\n## {ts} — auto-precompact-snapshot · status: UNREVIEWED\n"
             f"- trigger: {_sanitize(d.get('trigger', '?'))}\n"
             f"- transcript: {_sanitize(d.get('transcript_path', '?'))}\n"
             f"- action: review the transcript for unrecorded corrections/drift and capture real ones "
             f"via correction-capture. NOT a lesson, NOT approved.\n")
    with p.open("a") as f:
        f.write(entry)


def main():
    try:
        d = json.load(sys.stdin)
    except Exception:
        return 0  # never break the host on bad/empty input
    event = d.get("hook_event_name") or d.get("event") or ""

    if event == "PreCompact":
        try:
            write_pending(d)
        except Exception:
            pass  # a failed inbox write must never break the session (and we claim nothing was saved)
        return 0  # PreCompact can't inject context on either host — side-effect only

    text = nudge(event, d)
    if not text:
        return 0
    print(json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": text}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
