"""
The seventh pilot's second round, over the API: Claude Fable gets what the judge may report back
from round 1 (the library check, the targets, the training claims and the Lean build's errors), a
copy of its own branch and a few tools, and is asked to make Pilot.lean build.

    uv run --no-sync python examples/llm-pilot-37c/round2.py prepare
    uv run --no-sync python examples/llm-pilot-37c/round2.py run [--max-usd 30] [--max-steps 80]
    uv run --no-sync python examples/llm-pilot-37c/round2.py commit
    uv run --no-sync python examples/llm-pilot-37c/judge.py 2 local:round-2

The first round ran in its own cloud session. This one is billed to the API key in
CONSULT_ANTHROPIC_API_KEY (the consultations' key), and the loop runs in the orchestrator's
container, so the agent works through tools rather than a shell:

- read_file, list_files and search, over its tree and, read-only, mathlib's sources;
- write_file and edit_file, on Pilot.lean, files under proofs/LatticeProofs/Pilot/ and scratch/
  only (what the judge allows, less the Python deliverables, which this round leaves alone);
- lean_build, which builds LatticeProofs.Pilot against the real library and lists each theorem's
  axioms when it builds, and lean_file, which checks one scratch .lean file;
- run_python, which runs one of its scratch scripts in the tree with no environment;
- finish, with its report, written to scratch/report-round-2.md.

The tree is a worktree of the local sandbox clone, on the branch round-2 grown from the round-1
commit (read from branches.bundle), which `commit` commits and the judge reads as
`local:round-2`. Everything is logged in round2/ as it happens: requests.jsonl (each request's
stop reason, model, usage and cost) and transcript.jsonl (each assistant turn without
signatures, each tool call and its result), for the audit.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / "src"))

from lattice_lab import consult  # noqa: E402

CLONE = Path("/home/user/pilot-sandbox-37c")
TREE = Path("/home/user/pilot-37c-round2")
PROJ = Path("/tmp/claude-0/pilot-37c-round2-proofs")
OUT = HERE / "round2"
PROOFS = REPO / "proofs"
MATHLIB = PROOFS / ".lake" / "packages" / "mathlib"
PYTHON = REPO / ".venv" / "bin" / "python"
ROUND1 = "b5014b601065d078a554d925f5ba789533e08145"
MODEL = "claude-fable-5-1"
ENV = {
    **os.environ,
    "PATH": f"{Path.home() / '.elan' / 'bin'}:{os.environ['PATH']}",
    "ELAN_TOOLCHAIN": "v4.35.0-local",
}
STANDARD = {"propext", "Classical.choice", "Quot.sound"}
WRITABLE = re.compile(r"^(proofs/LatticeProofs/Pilot\.lean|proofs/LatticeProofs/Pilot/.+\.lean"
                      r"|scratch/.+)$")  # fmt: skip
CACHE = {"type": "ephemeral", "ttl": "1h"}  # a Lean build outlasts the five-minute cache

SYSTEM = """\
You are the proposer in a pilot of an LLM-central research loop, in its second round. You work \
through the tools below in a copy of your own branch from the first round; there is no shell. \
Paths are relative to the root of your checkout; paths starting with mathlib/ read mathlib's \
sources. Keep to the tools' purposes: run_python is for your own scripts in scratch/, which \
should read and write only inside the checkout."""


def git(*args: str, cwd: Path = CLONE) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout  # fmt: skip


def run(cmd: list[str], cwd: Path, timeout: int, env: dict | None = None) -> dict:
    start = time.time()
    try:
        out = subprocess.run(cmd, cwd=cwd, env=env or ENV, capture_output=True, text=True,
                             timeout=timeout)  # fmt: skip
        code, text = out.returncode, out.stdout + out.stderr
    except subprocess.TimeoutExpired as e:
        text = (e.stdout or b"").decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
        code, text = -1, f"timeout after {timeout} s\n{text}"
    return {"returncode": code, "seconds": round(time.time() - start, 1), "output": text}


# ---------------------------------------------------------------- setting up


def prepare(force: bool) -> None:
    if TREE.exists():
        if not force:
            raise SystemExit(f"{TREE} exists; pass --force to rebuild it")
        git("worktree", "remove", "--force", str(TREE))
    for ref in ("round-2", "round-1"):
        if git("branch", "--list", ref).strip():
            git("branch", "-D", ref)
    git("fetch", "-q", str(HERE / "branches.bundle"), "pilot-37c-submission:round-1")
    assert git("rev-parse", "round-1").strip() == ROUND1
    git("worktree", "add", "-q", "-b", "round-2", str(TREE), "round-1")
    if PROJ.exists():
        shutil.rmtree(PROJ)
    PROJ.mkdir(parents=True)
    for item in ["lakefile.toml", "lean-toolchain", "lake-manifest.json", "LatticeProofs.lean"]:
        shutil.copy(PROOFS / item, PROJ / item)
    shutil.copytree(PROOFS / "LatticeProofs", PROJ / "LatticeProofs")
    (PROJ / ".lake").mkdir()
    (PROJ / ".lake" / "packages").symlink_to(PROOFS / ".lake" / "packages")
    shutil.copytree(PROOFS / ".lake" / "build", PROJ / ".lake" / "build", symlinks=True)
    (PROJ / "Scratch").mkdir()
    OUT.mkdir(exist_ok=True)
    print(f"tree {TREE} at {ROUND1[:12]} on round-2; Lean project {PROJ}")


def errors_of(output: str, limit: int = 20000) -> str:
    """The error messages of a Lean build, each with its context, and a count of the warnings."""
    chunks, current = [], None
    for line in output.splitlines():
        if re.match(r"^(error|warning|info):|^[✔⚠✖] \[", line):
            current = [line] if line.startswith("error") else None
            if current is not None:
                chunks.append(current)
        elif current is not None and len(current) < 80:
            current.append(re.sub(r"^ {5,}", "    ", line))  # Lean's deep indentation
    warnings = sum(line.startswith("warning:") for line in output.splitlines())
    text = "\n".join("\n".join(c) for c in chunks)
    if len(text) > limit:
        text = text[:limit] + f"\n... ({len(text) - limit} more characters of errors)"
    return f"{text}\n({warnings} warnings not shown)" if warnings else text


def round1_errors() -> str:
    build = json.loads((HERE / "judgements" / "round-1.json").read_text())["lean"]["build"]
    return errors_of(build["output"])


# ---------------------------------------------------------------- the tools


TOOLS = [
    {"name": "read_file", "description": "Read a text file, with line numbers.",
     "input_schema": {"type": "object", "properties": {
         "path": {"type": "string"},
         "offset": {"type": "integer", "description": "first line, from 1"},
         "limit": {"type": "integer", "description": "number of lines, at most 600"}},
         "required": ["path"]}},
    {"name": "list_files", "description": "List a directory's entries.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}},
                      "required": ["path"]}},
    {"name": "search", "description": "Search files under a directory for a regular expression "
     "(ripgrep syntax); at most 80 matching lines.",
     "input_schema": {"type": "object", "properties": {
         "pattern": {"type": "string"}, "path": {"type": "string"},
         "glob": {"type": "string", "description": "e.g. *.lean"}},
         "required": ["pattern", "path"]}},
    {"name": "write_file", "description": "Write a whole file (Pilot.lean, files under "
     "proofs/LatticeProofs/Pilot/, or scratch/).",
     "input_schema": {"type": "object", "properties": {
         "path": {"type": "string"}, "content": {"type": "string"}},
         "required": ["path", "content"]}},
    {"name": "edit_file", "description": "Replace one exact occurrence of old with new in a "
     "writable file.",
     "input_schema": {"type": "object", "properties": {
         "path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}},
         "required": ["path", "old", "new"]}},
    {"name": "lean_build", "description": "Build LatticeProofs.Pilot (Pilot.lean and "
     "proofs/LatticeProofs/Pilot/) against the real library, as the judge does; a few minutes. "
     "Returns the errors, and when it builds, each theorem's axioms.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "lean_file", "description": "Check one scratch .lean file with `lake env lean` "
     "(it may import Mathlib and LatticeProofs modules); for quick experiments.",
     "input_schema": {"type": "object", "properties": {"path": {"type": "string"}},
                      "required": ["path"]}},
    {"name": "run_python", "description": "Run one of your scratch/*.py scripts from the root "
     "of the checkout (numpy and sympy available); at most 15 minutes.",
     "input_schema": {"type": "object", "properties": {
         "path": {"type": "string"}, "args": {"type": "array", "items": {"type": "string"}}},
         "required": ["path"]}},
    {"name": "finish", "description": "End the round with your report.",
     "input_schema": {"type": "object", "properties": {"report": {"type": "string"}},
                      "required": ["report"]}},
]  # fmt: skip


def resolve(path: str, write: bool = False) -> Path:
    if write and not WRITABLE.match(path):
        raise ValueError(f"not writable in this round: {path}")
    base, rel = (MATHLIB, path[len("mathlib/") :]) if path.startswith("mathlib/") else (TREE, path)
    if write and base is MATHLIB:
        raise ValueError("mathlib is read-only")
    full = (base / rel).resolve()
    if full != base.resolve() and base.resolve() not in full.parents:
        raise ValueError(f"outside the checkout: {path}")
    if ".git" in full.relative_to(base.resolve()).parts:
        raise ValueError("no access to .git")
    return full


def sync() -> None:
    shutil.copy(TREE / "proofs" / "LatticeProofs" / "Pilot.lean", PROJ / "LatticeProofs")
    shutil.rmtree(PROJ / "LatticeProofs" / "Pilot", ignore_errors=True)
    if (TREE / "proofs" / "LatticeProofs" / "Pilot").is_dir():
        shutil.copytree(
            TREE / "proofs" / "LatticeProofs" / "Pilot", PROJ / "LatticeProofs" / "Pilot"
        )


def sources() -> list[str]:
    pilot = TREE / "proofs" / "LatticeProofs"
    return [(pilot / "Pilot.lean").read_text()] + [
        p.read_text() for p in sorted(pilot.glob("Pilot/**/*.lean"))]  # fmt: skip


def lean_build() -> str:
    sync()
    build = run(["lake", "build", "LatticeProofs.Pilot"], PROJ, 3600)
    src = sources()
    forbidden = [w for w in ["axiom ", "native_decide", "sorry"] if any(w in s for s in src)]
    head = f"returncode {build['returncode']} in {build['seconds']} s"
    if forbidden:
        head += f"; the sources contain {forbidden}, which the judge does not accept"
    if build["returncode"] != 0:
        return f"{head}\n{errors_of(build['output']) or build['output'][-8000:]}"
    import judge  # noqa: PLC0415, the judge's own reading of the declared theorems

    names = sorted({n for s in src for n in judge.declared(s)})
    (PROJ / "AllAxioms.lean").write_text(
        "import LatticeProofs.Pilot\n" + "".join(f"#print axioms {n}\n" for n in names)
    )
    every = run(["lake", "env", "lean", "AllAxioms.lean"], PROJ, 1800)
    found = re.findall(r"'([\w.']+)' depends on axioms: \[([^\]]*)\]", every["output"])
    axioms = {n: sorted(a.strip() for a in ax.split(",")) for n, ax in found}
    for n in re.findall(r"'([\w.']+)' does not depend on any axioms", every["output"]):
        axioms[n] = []
    bad = {n: ax for n, ax in axioms.items() if not set(ax) <= STANDARD}
    lines = [f"{head}: it builds.", f"{len(axioms)} theorems; on the standard axioms only: "
             f"{len(axioms) - len(bad)}"]  # fmt: skip
    lines += [f"  {n}: {ax}" for n, ax in sorted(bad.items())]
    return "\n".join(lines)


def lean_file(path: str) -> str:
    src = resolve(path)
    if not path.startswith("scratch/") or src.suffix != ".lean":
        raise ValueError("lean_file checks a scratch/*.lean file")
    sync()
    target = PROJ / "Scratch" / src.name
    shutil.copy(src, target)
    r = run(["lake", "env", "lean", str(target.relative_to(PROJ))], PROJ, 1800)
    body = r["output"].strip()
    if len(body) > 20000:
        body = errors_of(body) or body[-20000:]
    return f"returncode {r['returncode']} in {r['seconds']} s\n{body}"


def run_python(path: str, args: list[str]) -> str:
    src = resolve(path)
    if not path.startswith("scratch/") or src.suffix != ".py":
        raise ValueError("run_python runs a scratch/*.py script")
    env = {"PATH": "/usr/bin:/bin", "HOME": str(TREE / "scratch"), "LANG": "C.UTF-8"}
    r = run([str(PYTHON), "-E", "-s", path, *map(str, args)], TREE, 900, env=env)
    body = r["output"]
    if len(body) > 15000:
        body = body[:3000] + f"\n... ({len(body) - 13000} characters omitted) ...\n" + body[-10000:]
    return f"returncode {r['returncode']} in {r['seconds']} s\n{body}"


def execute(name: str, args: dict) -> str:
    if name == "read_file":
        lines = resolve(args["path"]).read_text().splitlines()
        start = max(int(args.get("offset") or 1), 1)
        stop = start - 1 + min(int(args.get("limit") or 600), 600)
        body = "\n".join(f"{i:6}\t{line}" for i, line in enumerate(lines[start - 1 : stop], start))
        more = f"\n({len(lines) - stop} more lines)" if stop < len(lines) else ""
        return body + more
    if name == "list_files":
        d = resolve(args["path"] or ".")
        return "\n".join(p.name + ("/" if p.is_dir() else "") for p in sorted(d.iterdir())
                         if p.name != ".git")  # fmt: skip
    if name == "search":
        d = resolve(args["path"] or ".")
        cmd = ["rg", "-n", "--no-heading", "-M", "300", "-e", args["pattern"], str(d)]
        if args.get("glob"):
            cmd[1:1] = ["-g", args["glob"]]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout
        lines = [line.replace(str(MATHLIB), "mathlib").replace(str(TREE) + "/", "")
                 for line in out.splitlines()]  # fmt: skip
        return "\n".join(lines[:80]) + (f"\n({len(lines) - 80} more)" if len(lines) > 80 else "")
    if name == "write_file":
        target = resolve(args["path"], write=True)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(args["content"])
        return f"wrote {args['path']}: {len(args['content'].splitlines())} lines"
    if name == "edit_file":
        target = resolve(args["path"], write=True)
        text = target.read_text()
        n = text.count(args["old"])
        if n != 1:
            raise ValueError(f"old occurs {n} times in {args['path']}; it must occur once")
        target.write_text(text.replace(args["old"], args["new"]))
        return f"edited {args['path']}"
    if name == "lean_build":
        return lean_build()
    if name == "lean_file":
        return lean_file(args["path"])
    if name == "run_python":
        return run_python(args["path"], args.get("args") or [])
    if name == "finish":
        target = TREE / "scratch" / "report-round-2.md"
        target.write_text(args["report"])
        return "report written to scratch/report-round-2.md; the round is over"
    raise ValueError(f"no tool named {name}")


# ---------------------------------------------------------------- the round


def prompt() -> str:
    return f"""\
This is the second round of the seventh pilot (ninth powers at m = 37). Your first-round work is \
this checkout, at your commit {ROUND1[:7]}: CARD.md, mechanism.py, proposal.md, proposal.py, \
report.md, proofs/LatticeProofs/Pilot.lean and scratch/.

**What the judge reports back from round 1** (the results it may share; it does not report the \
held-out ones):

- Library unchanged: yes.
- Targets: your condition explains 4 of the 5 (699738, 985232, 1431278, 1968276, each with q \
divisible by 9 at m = 37); not 4850.
- Soundness at the training sizes: it ran on every set without an error, and made 1,182 claims, \
none false.
- proposal.py: 42 checks, all passing.
- Lean: **Pilot.lean does not build** against the library, so no theorem is accepted. The build \
took 346 s; its errors:

```
{round1_errors()}
```

**This round's task: make the Lean proof build.** The four theorems period_r1968276_dvd, \
period_r985232_dvd, period_r1431278_dvd and period_r699738_dvd should keep their statements \
(`period 37 rXOffsets ∣ 29127`); everything else in Pilot.lean is yours to change, and you may \
split it into files under proofs/LatticeProofs/Pilot/. The judge accepts a theorem when the file \
builds against the real library, the sources contain no `axiom` declaration and no \
`native_decide`, and `#print axioms` shows only propext, Classical.choice and Quot.sound (so no \
`sorry`). The mechanism and the proposal are not part of this round: leave mechanism.py, \
proposal.md and proposal.py as they are.

**Tools.** lean_build builds Pilot.lean as the judge does and, when it builds, lists each \
theorem's axioms. lean_file checks a single scratch .lean file and is much faster for trying a \
lemma or a tactic; it may import LatticeProofs modules (LatticeProofs, LatticeProofs.Cubes37, \
...) and the Mathlib modules the library's build compiled (about 2,500 of them; `import Mathlib` \
as a whole is not built here, and neither was it in round 1). mathlib's sources can be read \
and searched under mathlib/, and the library's under proofs/LatticeProofs/. scratch/gen_pilot.py and scratch/pilot_certs.json are your generator and \
certificates from round 1; run_python runs scratch scripts.

The round has a fixed API budget, so work economically: test pieces with lean_file before a full \
build, and prefer edit_file to rewriting whole files. When the four theorems build, or if you \
conclude you cannot get further, call finish with a short report: what you changed, the final \
build result and axioms, and anything still unproved."""


def echo(content: list) -> list:
    """The assistant turn as it is sent back: after a mid-output refusal fallback, the thinking
    and tool calls before the last `fallback` block are left out (the API's rule)."""
    switches = [i for i, b in enumerate(content) if b.type == "fallback"]
    if not switches:
        return list(content)
    cut = switches[-1]
    drop = ("thinking", "redacted_thinking", "tool_use")
    return [b for i, b in enumerate(content) if i >= cut or b.type not in drop]


def marked(messages: list[dict]) -> list[dict]:
    """The messages with one cache breakpoint, on the last block of the last user turn."""
    out = [dict(m) for m in messages]
    last = out[-1]
    blocks = [dict(b) for b in last["content"]]
    blocks[-1]["cache_control"] = CACHE
    last["content"] = blocks
    return out


def log(name: str, record: dict) -> None:
    record = {"time": datetime.now(UTC).isoformat(timespec="seconds"), **record}
    with open(OUT / name, "a") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_round(max_usd: float, max_steps: int) -> None:
    if (OUT / "requests.jsonl").exists():
        raise SystemExit(f"{OUT} already holds a round; move it away to run again")
    client = consult.anthropic_client()
    params = {
        "model": MODEL,
        "max_tokens": 64000,
        "betas": [consult.FALLBACK_BETA],
        "fallbacks": "default",
        "thinking": {"type": "adaptive", "display": "summarized"},
        "output_config": {"effort": "high"},
        "system": [{"type": "text", "text": SYSTEM, "cache_control": CACHE}],
        "tools": TOOLS,
    }
    first = prompt()
    (OUT / "prompt.md").write_text(first)
    messages = [{"role": "user", "content": [{"type": "text", "text": first}]}]
    requests, warned, finished = [], False, False
    for step in range(max_steps):
        with client.beta.messages.stream(**params, messages=marked(messages)) as stream:
            message = stream.get_final_message()
            request_id = stream.request_id
        usage = message.usage.model_dump(exclude_none=True)
        requests.append({"request_id": request_id, "usage": usage})
        spent = consult.cost(requests, MODEL) or 0.0
        log("requests.jsonl", {"step": step, "request_id": request_id, "model": message.model,
                               "stop_reason": message.stop_reason, "usage": usage,
                               "cost_usd_total": round(spent, 4)})  # fmt: skip
        turn = [consult._record(b) for b in message.content]
        log("transcript.jsonl", {"step": step, "role": "assistant", "model": message.model,
                                 "content": turn})  # fmt: skip
        content = echo(message.content)
        messages.append({"role": "assistant", "content": content})
        print(f"step {step}: {message.stop_reason}, {message.model}, ${spent:.2f}", flush=True)
        if message.stop_reason in ("refusal", "max_tokens"):
            print(f"stopped: {message.stop_reason}; its tool calls were not run")
            break
        calls = [b for b in content if b.type == "tool_use"]
        if not calls:
            break
        results = []
        for b in calls:
            try:
                text, error = execute(b.name, dict(b.input)), False
            except Exception as e:  # a tool error goes back to the agent as one
                text, error = f"{type(e).__name__}: {e}", True
            finished |= b.name == "finish" and not error
            entry = {"name": b.name, "input": b.input, "is_error": error, "result": text}
            log("transcript.jsonl", {"step": step, "role": "tool", **entry})
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": text,
                            **({"is_error": True} if error else {})})  # fmt: skip
        if finished:
            break
        if spent > max_usd:
            print(f"stopped: ${spent:.2f} spent, over the ${max_usd:.0f} cap")
            break
        if spent > 0.8 * max_usd and not warned:
            warned = True
            results.append({"type": "text", "text": "The round's API budget is nearly spent. "
                            "Finish what you are doing in the next few steps, then call finish "
                            "with your report."})  # fmt: skip
        messages.append({"role": "user", "content": results})
    summary = {"steps": len(requests), "finished": finished,
               "served_by": sorted({json.loads(line)["model"] for line in
                                    (OUT / "requests.jsonl").read_text().splitlines()}),
               "cost_usd": round(consult.cost(requests, MODEL) or 0.0, 2)}  # fmt: skip
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary))


def commit() -> None:
    git("add", "-A", cwd=TREE)
    git("-c", "user.name=lattice-lab pilot", "-c", "user.email=pilot@lattice-lab.invalid",
        "commit", "-q", "-m", "Round 2 (over the API): the Lean proof", cwd=TREE)  # fmt: skip
    print(git("log", "--oneline", "-1", cwd=TREE).strip())


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--force", action="store_true")
    r = sub.add_parser("run")
    r.add_argument("--max-usd", type=float, default=30.0)
    r.add_argument("--max-steps", type=int, default=80)
    sub.add_parser("commit")
    sub.add_parser("errors")
    args = parser.parse_args()
    if args.cmd == "prepare":
        prepare(args.force)
    elif args.cmd == "run":
        run_round(args.max_usd, args.max_steps)
    elif args.cmd == "commit":
        commit()
    else:
        print(round1_errors())


if __name__ == "__main__":
    main()
