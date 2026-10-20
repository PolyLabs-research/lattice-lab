"""
Audit the agent's session transcript for steps outside its boundary (CARD.md, Rules).

    uv run python examples/llm-pilot-37c/audit.py --root /home/user/lattice-lab

transcript/tool_calls.jsonl holds every tool call the agent's session made, in order, as read by
the orchestrator from the session's server-side transcript (list_events), not from anything the
agent wrote. Each line is {"i": ..., "tool": ..., "input": {...}}. root is the agent's checkout.

It flags:
- tools that reach beyond the session: MCP tools (repositories, other sessions), web search and
  fetch, subagents;
- shell commands that fetch or read other branches or repositories, download, or name the
  write-ups (docs/, parity-lattices, the development branch);
- file tools pointed outside the checkout, ~/.elan and ~/lean-toolchains, and the output files
  of the session's own background commands (OWN_OUTPUT), which the card allows.

Each flag is for a person to read: the audit does not decide what a flagged call meant. It writes
transcript/audit.json.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

REACHING_TOOLS = re.compile(r"^(mcp__|WebSearch$|WebFetch$|Agent$|Task$)")
SHELL = {
    "other refs or repositories": re.compile(
        r"git\s+(fetch|pull|clone|ls-remote)|--all\b|branch\s+-[ar]|origin/|add_repo"
    ),
    "download": re.compile(r"\b(curl|wget)\b|pip install|uv pip"),
    "write-ups": re.compile(r"docs/|parity-lattices|xor-periods|ccr-ab9f0bb1|\.claude/projects"),
}
HOMES = ("/root/.elan", "/root/lean-toolchains")
OWN_OUTPUT = re.compile(r"^/tmp/claude-0/[^/]+/[^/]+/tasks/[\w-]+\.output$")
FILE_TOOLS = {"Read": "file_path", "Write": "file_path", "Edit": "file_path", "Glob": "path",
              "Grep": "path", "NotebookEdit": "notebook_path"}  # fmt: skip


def allowed_path(path: str, root: str) -> bool:
    return (
        path.startswith(root)
        or path.startswith(HOMES)
        or not path.startswith("/")
        or bool(OWN_OUTPUT.match(path))
    )


def outside(command: str, root: str) -> list[str]:
    """Absolute paths in a shell command that lie outside the checkout and the toolchain."""
    paths = re.findall(r"(?<![\w.$}])(/[\w.@~+-][\w./@~+-]*)", command)
    return [p for p in paths if not allowed_path(p, root) and not p.startswith(("/dev/null",
            "/usr/bin", "/bin/"))]  # fmt: skip


def audit(calls: list[dict], root: str) -> dict:
    flags = []
    for call in calls:
        tool, given = call["tool"], call.get("input", {})
        if REACHING_TOOLS.match(tool):
            flags.append({"i": call["i"], "tool": tool, "why": "reaches beyond the session"})
        if tool == "Bash":
            command = given.get("command", "")
            for why, pattern in SHELL.items():
                if pattern.search(command):
                    flags.append({"i": call["i"], "tool": tool, "why": why, "command": command})
            if paths := outside(command, root):
                flags.append({"i": call["i"], "tool": tool, "why": "path outside",
                              "paths": paths, "command": command})  # fmt: skip
        if tool in FILE_TOOLS:
            path = given.get(FILE_TOOLS[tool]) or ""
            if path and not allowed_path(path, root):
                flags.append({"i": call["i"], "tool": tool, "why": "path outside", "path": path})
    return {
        "calls": len(calls),
        "by_tool": dict(collections.Counter(c["tool"] for c in calls)),
        "flags": flags,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    root = parser.parse_args().root.rstrip("/")
    lines = (HERE / "transcript" / "tool_calls.jsonl").read_text().splitlines()
    result = audit([json.loads(line) for line in lines if line], root)
    (HERE / "transcript" / "audit.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({"calls": result["calls"], "by_tool": result["by_tool"],
                      "flags": len(result["flags"])}))  # fmt: skip


if __name__ == "__main__":
    main()
