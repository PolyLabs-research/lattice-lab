"""
Turn the agent's server-side transcript into the audit's inputs.

    uv run python examples/llm-pilot-vot13/transcript.py <page> [<page> ...]

Each page is a saved `list_events` result for the agent's session (kinds assistant and user),
as the orchestrator read it. The script writes, in transcript/:

- tool_calls.jsonl: every tool call, in order, as {"i", "time", "tool", "input"}, for audit.py;
- messages.md: every text block the agent wrote, verbatim;
- inputs.json: every input the session received other than tool results (the prompt, task
  notifications, hook feedback, any message), with its origin where the transcript records one.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def events(pages: list[str]) -> list[tuple[str, str, dict]]:
    seen = {}
    for page in pages:
        text = Path(page).read_text()
        data = json.loads(text[text.index('{"ccr"') : text.rindex("}") + 1])["ccr"]["data"]
        for e in data:
            kind = next(k for k in e if k != "created_at")
            inner = e[kind]
            seen[inner.get("uuid") or json.dumps(e)[:120]] = (e["created_at"], kind, inner)
    return sorted(seen.values(), key=lambda x: x[0])


def main() -> None:
    calls, texts, inputs, sidechains = [], [], [], set()
    for t, kind, inner in events(sys.argv[1:]):
        body = inner.get("internal_anthropic_catchall", inner)
        # tool_progress events also carry a parent tool id (a long-running Bash call), so only
        # assistant and user events can mark a subagent's sidechain
        if kind in ("assistant", "user") and body.get("parent_tool_use_id"):
            sidechains.add(body["parent_tool_use_id"])
        message = body.get("message", {})
        content = message.get("content") if isinstance(message, dict) else None
        if kind == "assistant" and isinstance(content, list):
            for c in content:
                if c.get("type") == "tool_use":
                    calls.append(
                        {"i": len(calls), "time": t, "tool": c["name"], "input": c["input"]}
                    )
                elif c.get("type") == "text":
                    texts.append((t, c["text"]))
        elif kind == "user":
            origin = body.get("origin")
            if isinstance(content, str):
                inputs.append({"time": t, "origin": origin, "text": content})
            elif isinstance(content, list):
                for c in content:
                    if c.get("type") == "text":
                        inputs.append({"time": t, "origin": origin, "text": c["text"]})
    out = HERE / "transcript"
    out.mkdir(exist_ok=True)
    with open(out / "tool_calls.jsonl", "w") as f:
        for c in calls:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    with open(out / "messages.md", "w") as f:
        f.write("# The agent's messages, verbatim\n\nEvery text block of the agent's session, in ")
        f.write("order, read from its server-side transcript.\n\n")
        for t, x in texts:
            f.write(f"## {t}\n\n{x}\n\n")
    (out / "inputs.json").write_text(json.dumps(inputs, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({"tool_calls": len(calls), "texts": len(texts), "inputs": len(inputs),
                      "subagent_calls": len(sidechains)}))  # fmt: skip


if __name__ == "__main__":
    main()
