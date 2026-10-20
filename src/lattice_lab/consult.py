"""Consultations: the same question, with the same context, put to other models by API.

    lattice-lab consult ask NAME --question FILE [--context FILE ...]   round 1, independent
    lattice-lab consult ask NAME --preset direction                      what should we do next?
    lattice-lab consult review NAME                                      round 2: each reviews all

Each consultant answers on its own, and every exchange is kept verbatim under
`consultations/NAME/`: the exact prompt sent (`round-1/prompt.md`), and for each consultant a
record (`round-1/fable.json`: model, effort, the parameters sent, the prompt's hash, times,
usage, stop reason, the summarised reasoning and the answer) with the answer alone beside it
(`round-1/fable.md`); with code execution, the record also holds every block of the exchange,
the code run and its output included. Records are written once and never overwritten. A
consultant that fails
(network, rate limit) leaves no record, and one cut off at its output limit leaves its record in
`round-1/attempts/` instead, so running `ask` again calls only the ones without an answer, and
only if the prompt is unchanged.

A review round puts the round-1 prompt and every complete round-1 answer, labelled A, B, ... in
a fixed order and without names, to every consultant, with the same request: where the answers
agree and conflict, which claims are wrong, and a recommendation revised in the light of the
others. Nothing a consultant says counts until it has been checked (docs/consultations.md).

Both consultants can run code by default (Anthropic's code execution tool, OpenAI's code
interpreter), each in its provider's sandbox, so that they can check their own identities and
arithmetic before stating them; `--no-code` turns this off. The prompt is marked for caching,
since a tool loop rereads it at every step and, uncached, would bill it in full each time.

The keys are read from CONSULT_ANTHROPIC_API_KEY and CONSULT_OPENAI_API_KEY, not the usual
names, so that a cloud session's own Claude credentials are never used for, or confused with,
these calls; the API hosts are fixed for the same reason. ChatGPT's model is CONSULT_OPENAI_MODEL
(or `--model chatgpt=ID`): it has no default, since a guessed model id would only fail.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

ANTHROPIC_BASE_URL = "https://api.anthropic.com"
OPENAI_BASE_URL = "https://api.openai.com/v1"
# Server-side refusal fallback, "default" form: on a policy decline the API reruns the request
# on the model Anthropic recommends for that category, inside the same call.
FALLBACK_BETA = "server-side-fallback-2026-07-01"
# Task budgets: an advisory token budget for thinking and answer together, which the model sees
# and paces itself against. Without one, Fable's first consultation thought for 64,000 tokens,
# its whole output limit, and wrote no answer.
BUDGET_BETA = "task-budgets-2026-03-13"
CODE_TOOL = {"type": "code_execution_20260521", "name": "code_execution"}
MAX_CONTINUATIONS = 8  # requests after a pause_turn, when a long tool loop is paused
# Dollars per million tokens (input, output, cache write, cache read), for the cost estimate:
# Fable, and the models its refusal fallback runs.
PRICES = {
    "claude-fable-5-1": (10.0, 50.0, 12.5, 0.25),
    "claude-opus-4-8": (5.0, 25.0, 6.25, 0.5),
    "claude-opus-5": (5.0, 25.0, 6.25, 0.5),
}
TOKENS = ("input_tokens", "output_tokens", "cache_creation_input_tokens",
          "cache_read_input_tokens")  # fmt: skip


class ConsultError(Exception):
    """A consultation that cannot go ahead as asked."""


@dataclass(frozen=True)
class Consultant:
    name: str
    provider: str  # "anthropic" or "openai"
    model: str | None
    effort: str = "high"
    max_tokens: int = 64000  # the hard limit on output, thinking included
    budget: int | None = None  # the advisory task budget (Anthropic only)
    code: bool = True  # code execution in the provider's sandbox


def consultants() -> dict[str, Consultant]:
    return {
        "fable": Consultant(
            "fable", "anthropic", "claude-fable-5-1", max_tokens=128000, budget=64000
        ),
        "chatgpt": Consultant("chatgpt", "openai", os.environ.get("CONSULT_OPENAI_MODEL")),
    }


PREAMBLE = """\
You are being consulted on a mathematics research project. The project studies linear cellular \
automata over GF(2) on tori: which rules have every nonzero eigenvalue in a given subgroup (a \
cube, say) at a given size, why, and what laws their periods follow. Its rule is that nothing \
counts until a machine has checked it: identities are multiplied out again, claims about \
eigenvalues are recomputed, proofs go into Lean, and predictions are registered before they are \
tested. Other models are being asked the same question independently.

So that your answer can be checked: state each claim precisely, with the quantifiers and the \
sizes it covers; say for each whether you proved it, checked it by computation (and how far), or \
conjecture it; give proofs or arguments where you have them; and where you can, make predictions \
at cases the documents below do not settle, which can then be registered and tested. If you \
can run code, use it to check every identity and computation before you state it. Say plainly \
where you think the project is wrong or missing something.
"""

PRESETS = {
    "direction": {
        # STATUS first, then every write-up: a summary alone left Fable flagging, as open,
        # points that the write-ups settle (docs/consultations.md, section 2).
        "context": ["docs/STATUS.md", "docs/"],
        "question": """\
The documents above are where the project stands. What should it do next?

Give at most three suggestions, ranked. For each: what to do; why now, rather than later; what \
it would establish if it worked; the first concrete step; and what result would show it was the \
wrong choice. Then say which of the open questions you think is mis-posed, and which result \
listed as established you would check again, and why.
""",
    },
}

REVIEW_REQUEST = """\
This is the second round of a consultation. In the first round several models were each given \
the prompt below, independently. Their complete answers follow it, labelled by letter in a fixed \
order and without names; one of them may be yours.

Review the answers. Where do they agree, and where do they conflict? Which claims are wrong or \
unsupported, and exactly why? Then give your own recommendation, revised in the light of the \
others: what you would do next, why, and what result would show it was the wrong choice.
"""


# ---------------------------------------------------------------- prompts


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def build_prompt(question: str, context: list[tuple[str, str]]) -> str:
    """The preamble, each context document in full, then the question."""
    parts = [PREAMBLE]
    if context:
        docs = "\n".join(f'<document path="{path}">\n{text.rstrip()}\n</document>'
                         for path, text in context)  # fmt: skip
        parts.append(f"<documents>\n{docs}\n</documents>\n")
    parts.append(f"<question>\n{question.rstrip()}\n</question>\n")
    return "\n".join(parts)


def build_review_prompt(first_prompt: str, answers: list[str]) -> str:
    labelled = "\n".join(f'<answer label="{chr(65 + i)}">\n{text.rstrip()}\n</answer>'
                         for i, text in enumerate(answers))  # fmt: skip
    return (f"{REVIEW_REQUEST}\n<round-1-prompt>\n{first_prompt.rstrip()}\n</round-1-prompt>\n\n"
            f"<answers>\n{labelled}\n</answers>\n")  # fmt: skip


# ---------------------------------------------------------------- the two APIs


def anthropic_client():
    key = os.environ.get("CONSULT_ANTHROPIC_API_KEY")
    if not key:
        raise ConsultError("CONSULT_ANTHROPIC_API_KEY is not set")
    import anthropic

    return anthropic.Anthropic(api_key=key, base_url=ANTHROPIC_BASE_URL, max_retries=3)


def openai_client():
    key = os.environ.get("CONSULT_OPENAI_API_KEY")
    if not key:
        raise ConsultError("CONSULT_OPENAI_API_KEY is not set")
    import openai

    return openai.OpenAI(api_key=key, base_url=OPENAI_BASE_URL, max_retries=3, timeout=3600)


def anthropic_params(c: Consultant) -> dict:
    params = {
        "model": c.model,
        "max_tokens": c.max_tokens,
        "betas": [FALLBACK_BETA],
        "fallbacks": "default",
        "thinking": {"type": "adaptive", "display": "summarized"},
        "output_config": {"effort": c.effort},
    }
    if c.budget:
        params["betas"].append(BUDGET_BETA)
        params["output_config"]["task_budget"] = {"type": "tokens", "total": c.budget}
    if c.code:
        params["tools"] = [CODE_TOOL]
    return params


def _record(block) -> dict:
    """A content block as JSON, without the opaque signatures and encrypted parts."""
    d = block.model_dump(exclude_none=True)
    for key in ("signature", "encrypted_content"):
        d.pop(key, None)
    return d


def attempts(requests: list[dict], model: str) -> list[tuple[str, dict]]:
    """(model, usage) for every step the requests made. The top-level usage covers only the
    attempt that produced the message, so after a refusal fallback it leaves out the declined
    model's tokens; `usage.iterations` lists every step. After a fallback, the last step of each
    attempt names its model (a declined Fable attempt, then the fallback's, ending in a
    `fallback_message`), so an unnamed step belongs to the next named one; with no fallback no
    step is named, and all are the requested model's."""
    out, pending = [], []
    for r in requests:
        steps = r["usage"].get("iterations") or []
        if not steps:
            pending.append(r["usage"])
        for step in steps:
            pending.append(step)
            if step.get("model"):
                model = step["model"]
                out += [(model, u) for u in pending]
                pending = []
    return out + [(model, u) for u in pending]


def cost(requests: list[dict], model: str) -> float | None:
    """The estimated dollar cost of the requests, each attempt at its own model's prices."""
    total = 0.0
    for name, usage in attempts(requests, model):
        if name not in PRICES:
            return None
        prices = PRICES[name]
        total += sum(usage.get(k, 0) * r for k, r in zip(TOKENS, prices, strict=True))
        # a one-hour cache write costs twice the input price, not the five-minute 1.25 times
        hour = (usage.get("cache_creation") or {}).get("ephemeral_1h_input_tokens", 0)
        total += hour * (2 * prices[0] - prices[2])
    return round(total / 1e6, 4)


def ask_anthropic(client, c: Consultant, prompt: str) -> dict:
    params = anthropic_params(c)
    # Cached, because a tool loop rereads the whole prompt at each step.
    user = {"role": "user", "content": [
        {"type": "text", "text": prompt, "cache_control": {"type": "ephemeral"}}]}  # fmt: skip
    blocks, requests = [], []
    for _ in range(1 + MAX_CONTINUATIONS):
        messages = [user] + ([{"role": "assistant", "content": list(blocks)}] if blocks else [])
        with client.beta.messages.stream(**params, messages=messages) as stream:
            message = stream.get_final_message()
            request_id = stream.request_id
        blocks += list(message.content)
        requests.append({"request_id": request_id, "stop_reason": message.stop_reason,
                         "usage": message.usage.model_dump(exclude_none=True)})  # fmt: skip
        if message.stop_reason != "pause_turn":
            break
        # A paused server-side tool loop resumes when the turn so far is sent back as it is,
        # in the same container, with what is left of the budget.
        params["container"] = message.container.id
        if c.budget:
            left = max(c.budget - sum(r["usage"]["output_tokens"] for r in requests), 0)
            budget = {"type": "tokens", "total": c.budget, "remaining": left}
            params["output_config"] = {**params["output_config"], "task_budget": budget}
    # After a fallback, the declined model's partial output stays in the stream, ahead of a
    # `fallback` block; the answer is what follows the last one, and its text is what follows
    # the last tool call.
    switches = [i for i, b in enumerate(blocks) if b.type == "fallback"]
    answer = blocks[switches[-1] + 1 :] if switches else blocks
    tools = [i for i, b in enumerate(answer) if b.type.endswith(("tool_use", "tool_result"))]
    final = answer[tools[-1] + 1 :] if tools else answer
    if not any(b.type == "text" for b in final):
        final = answer
    iterations = [e for r in requests for e in r["usage"].get("iterations", [])]
    stop = message.stop_reason
    status = {"refusal": "refused", "max_tokens": "truncated", "pause_turn": "truncated"}.get(
        stop, "complete"
    )
    steps = attempts(requests, c.model)
    usage = {k: sum(u.get(k, 0) for _, u in steps) for k in TOKENS}
    usage["by_model"] = {m: {k: sum(u.get(k, 0) for n, u in steps if n == m) for k in TOKENS}
                         for m in dict.fromkeys(n for n, _ in steps)}  # fmt: skip
    usage["thinking_tokens"] = sum(  # of the attempts that produced the messages
        r["usage"].get("output_tokens_details", {}).get("thinking_tokens", 0) for r in requests
    )
    details = getattr(message, "stop_details", None)
    container = getattr(message, "container", None)
    return {
        "status": status,
        "served_by": message.model,
        "fallback": bool(switches) or any(e.get("type") == "fallback_message" for e in iterations),
        "stop_reason": stop,
        "stop_details": details.model_dump() if details is not None else None,
        "request_id": requests[0]["request_id"],
        "usage": usage,
        "cost_usd": cost(requests, c.model),
        "tool_calls": sum(b.type == "server_tool_use" for b in blocks),
        "container": container.id if container is not None else None,
        "requests": requests,
        "reasoning_summary": "\n\n".join(b.thinking for b in answer if b.type == "thinking"),
        "text": "".join(b.text for b in final if b.type == "text"),
        "content": [_record(b) for b in blocks],
    }


def openai_params(c: Consultant) -> dict:
    params = {
        "model": c.model,
        "max_output_tokens": c.max_tokens,
        "reasoning": {"effort": c.effort, "summary": "auto"},
        "store": False,
    }
    if c.code:
        params["tools"] = [{"type": "code_interpreter", "container": {"type": "auto"}}]
        params["include"] = ["code_interpreter_call.outputs"]
    return params


def ask_openai(client, c: Consultant, prompt: str) -> dict:
    with client.responses.stream(**openai_params(c), input=prompt) as stream:
        response = stream.get_final_response()
    parts = [p for item in response.output if item.type == "message" for p in item.content]
    refused = any(p.type == "refusal" for p in parts)
    reason = response.incomplete_details.reason if response.incomplete_details else None
    if refused or reason == "content_filter":
        status = "refused"
    elif response.status == "completed":
        status = "complete"
    else:
        status = "truncated"
    summary = [s.text for item in response.output if item.type == "reasoning"
               for s in item.summary]  # fmt: skip
    return {
        "status": status,
        "served_by": response.model,
        "fallback": False,
        "stop_reason": response.status if reason is None else f"{response.status}: {reason}",
        "stop_details": None,
        "request_id": response.id,
        "usage": response.usage.model_dump(exclude_none=True) if response.usage else None,
        "cost_usd": None,
        "tool_calls": sum(item.type == "code_interpreter_call" for item in response.output),
        "reasoning_summary": "\n\n".join(summary),
        "text": "".join(p.text for p in parts if p.type == "output_text"),
        "content": [_record(item) for item in response.output],
    }


PROVIDERS: dict[str, tuple[Callable, Callable, Callable]] = {
    "anthropic": (anthropic_client, ask_anthropic, anthropic_params),
    "openai": (openai_client, ask_openai, openai_params),
}


# ---------------------------------------------------------------- records


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _write_once(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as f:
        f.write(text)


def _fix(path: Path, text: str) -> None:
    """Write `text` to `path`, or check that it is what is already there."""
    if not path.exists():
        _write_once(path, text)
    elif path.read_text() != text:
        raise ConsultError(f"{path} holds something else; this round's records are for that")


def run_round(directory: Path, prompt: str, chosen: list[Consultant], round_number: int,
              log: Callable[[str], None]) -> dict:  # fmt: skip
    """Ask every chosen consultant without a record in `directory`, concurrently; write each
    record as it arrives (a truncated one to `attempts/`, so that it is asked again next time).
    Returns {name: "written" | "exists" | "truncated: ..." | error message}."""
    _fix(directory / "prompt.md", prompt)
    digest = sha256(prompt)
    outcome = {}
    todo = []
    for c in chosen:
        if (directory / f"{c.name}.json").exists():
            outcome[c.name] = "exists"
        elif not c.model:
            outcome[c.name] = f"no model for {c.name} (CONSULT_OPENAI_MODEL or --model)"
        else:
            todo.append(c)

    def one(c: Consultant) -> tuple[str, str]:
        make_client, ask_fn, params = PROVIDERS[c.provider]
        try:
            client = make_client()
            log(f"{c.name}: asking {c.model} (effort {c.effort})")
            started, t0 = _now(), time.monotonic()
            result = ask_fn(client, c, prompt)
        except Exception as exc:  # any failure leaves no record, so a rerun retries it
            return c.name, f"{type(exc).__name__}: {exc}"
        record = {
            "consultation": directory.parent.name,
            "round": round_number,
            "consultant": asdict(c),
            "params": params(c),
            "prompt_sha256": digest,
            "started": started,
            "finished": _now(),
            "seconds": round(time.monotonic() - t0, 1),
            **result,
        }
        cost = f", ${result['cost_usd']:.2f}" if result.get("cost_usd") is not None else ""
        log(f"{c.name}: {result['status']} in {record['seconds']} s, "
            f"{result.get('tool_calls', 0)} tool calls{cost}")  # fmt: skip
        if result["status"] == "truncated":
            attempt = len(list((directory / "attempts").glob(f"{c.name}-*.json"))) + 1
            path = directory / "attempts" / f"{c.name}-{attempt}.json"
            _write_once(path, json.dumps(record, indent=2) + "\n")
            return c.name, f"truncated at {c.max_tokens} output tokens; kept as {path}"
        _write_once(directory / f"{c.name}.json", json.dumps(record, indent=2) + "\n")
        _write_once(directory / f"{c.name}.md", result["text"].rstrip() + "\n")
        return c.name, "written"

    with ThreadPoolExecutor(max_workers=max(1, len(todo))) as pool:
        outcome.update(dict(pool.map(one, todo)))
    return outcome


def round_answers(directory: Path) -> list[tuple[str, str]]:
    """(consultant, answer) for every complete record in a round, in name order."""
    out = []
    for path in sorted(directory.glob("*.json")):
        record = json.loads(path.read_text())
        if record["status"] == "complete":
            out.append((record["consultant"]["name"], record["text"]))
    return out


# ---------------------------------------------------------------- the command


_NAME = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def _chosen(args) -> list[Consultant]:
    available = consultants()
    names = args.with_ or list(available)
    unknown = [n for n in names if n not in available]
    if unknown:
        raise ConsultError(f"unknown consultant(s) {unknown}; known: {sorted(available)}")
    chosen = {n: available[n] for n in names}
    if args.no_code:
        chosen = {n: replace(c, code=False) for n, c in chosen.items()}
    for field in ("model", "effort", "budget", "max_tokens"):
        for spec in getattr(args, field):
            name, _, value = spec.partition("=")
            flag = "--" + field.replace("_", "-")
            if name not in chosen or not value:
                raise ConsultError(f"{flag} takes NAME=VALUE with NAME one of {sorted(chosen)}")
            if field in ("budget", "max_tokens"):
                if not value.isdigit():
                    raise ConsultError(f"{flag} {spec}: a whole number of tokens")
                value = int(value)
            chosen[name] = replace(chosen[name], **{field: value})
    if args.replicates > 1:  # independent answers from the same settings: fable-r1, fable-r2, ...
        return [replace(c, name=f"{c.name}-r{k}") for c in chosen.values()
                for k in range(1, args.replicates + 1)]  # fmt: skip
    return list(chosen.values())


def _directory(args) -> Path:
    if not _NAME.match(args.name):
        raise ConsultError(f"name {args.name!r}: lower-case letters, digits and hyphens")
    return args.dir / args.name


def cmd_ask(args, log: Callable[[str], None]) -> int:
    preset = PRESETS[args.preset] if args.preset else {}
    if args.question:
        question = args.question.read_text()
    elif preset:
        question = preset["question"]
    else:
        raise ConsultError("give --question FILE or --preset NAME")
    paths = args.context or [Path(p) for p in preset.get("context", [])]
    prompt = build_prompt(question, [(str(p), p.read_text()) for p in expand(paths)])
    return _run(args, prompt, 1, log)


def expand(paths: list[Path]) -> list[Path]:
    """Files as given, and directories as their Markdown files in name order, each once."""
    out = []
    for path in paths:
        for f in sorted(path.glob("*.md")) if path.is_dir() else [path]:
            if f not in out:
                out.append(f)
    return out


def cmd_review(args, log: Callable[[str], None]) -> int:
    first = _directory(args) / "round-1"
    if not (first / "prompt.md").exists():
        raise ConsultError(f"no round 1 at {first}")
    answers = round_answers(first)
    if len(answers) < 2:
        raise ConsultError(f"round 1 has {len(answers)} complete answer(s); a review needs two")
    prompt = build_review_prompt((first / "prompt.md").read_text(), [t for _, t in answers])
    if not args.dry_run:
        labels = {chr(65 + i): name for i, (name, _) in enumerate(answers)}
        _fix(_directory(args) / "round-2" / "labels.json", json.dumps(labels, indent=2) + "\n")
    return _run(args, prompt, 2, log)


def _run(args, prompt: str, round_number: int, log: Callable[[str], None]) -> int:
    chosen = _chosen(args)
    directory = _directory(args) / f"round-{round_number}"
    if args.dry_run:
        print(prompt)
        for c in chosen:
            params = PROVIDERS[c.provider][2](c)
            log(f"{c.name}: would send {json.dumps(params)} with a prompt of {len(prompt):,} "
                f"characters (sha256 {sha256(prompt)[:12]})")  # fmt: skip
        return 0
    outcome = run_round(directory, prompt, chosen, round_number, log)
    print(json.dumps({"directory": str(directory), "consultants": outcome}))
    return 0 if all(v in ("written", "exists") for v in outcome.values()) else 1


def add_parser(sub) -> None:
    p = sub.add_parser("consult", help="Put a question to other models and record the answers.")
    rounds = p.add_subparsers(dest="round", required=True)
    rounds_help = {
        "ask": "Round 1: every consultant answers independently.",
        "review": "Round 2: every consultant reviews all the answers.",
    }
    for name, helptext in rounds_help.items():
        q = rounds.add_parser(name, help=helptext)
        q.add_argument("name", help="the consultation's name, e.g. 2026-10-21-next-steps")
        q.add_argument("--dir", type=Path, default=Path("consultations"))
        q.add_argument("--with", dest="with_", action="append", metavar="CONSULTANT",
                       help="ask only these (repeatable; default all)")  # fmt: skip
        q.add_argument("--model", action="append", default=[], metavar="NAME=ID")
        q.add_argument("--effort", action="append", default=[], metavar="NAME=LEVEL")
        q.add_argument("--budget", action="append", default=[], metavar="NAME=TOKENS",
                       help="advisory task budget (fable; 0 for none)")  # fmt: skip
        q.add_argument("--max-tokens", action="append", default=[], metavar="NAME=TOKENS")
        q.add_argument("--no-code", action="store_true", help="no code execution")
        q.add_argument("--replicates", type=int, default=1, metavar="N",
                       help="N independent answers from each consultant")  # fmt: skip
        q.add_argument("--dry-run", action="store_true", help="print the prompt; call nothing")
        if name == "ask":
            q.add_argument("--question", type=Path, help="a file holding the question")
            q.add_argument("--context", type=Path, action="append",
                           help="a document to include in full (repeatable)")  # fmt: skip
            q.add_argument("--preset", choices=sorted(PRESETS))


def main(args, log: Callable[[str], None]) -> int:
    return {"ask": cmd_ask, "review": cmd_review}[args.round](args, log)
