"""The consultation module: prompts, the two API calls as the real SDKs send them, records."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from lattice_lab import consult
from lattice_lab.cli import main

FABLE = consult.Consultant("fable", "anthropic", "claude-fable-5-1")
GPT = consult.Consultant("chatgpt", "openai", "test-model")


def _sse(events: list[dict]) -> bytes:
    return "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events).encode()


def _mock(body: bytes, headers: dict, seen: list):
    httpx2 = pytest.importorskip("httpx2")

    def handler(request):
        seen.append(request)
        return httpx2.Response(200, headers={"content-type": "text/event-stream", **headers},
                               content=body)  # fmt: skip

    return httpx2.Client(transport=httpx2.MockTransport(handler))


def test_prompts():
    prompt = consult.build_prompt("Why 37?", [("docs/a.md", "alpha\n"), ("b.md", "beta")])
    assert prompt.startswith(consult.PREAMBLE)
    assert prompt.index('<document path="docs/a.md">\nalpha\n</document>') < prompt.index("beta")
    assert prompt.rstrip().endswith("<question>\nWhy 37?\n</question>")
    review = consult.build_review_prompt(prompt, ["first", "second"])
    assert review.startswith(consult.REVIEW_REQUEST)
    assert '<answer label="A">\nfirst\n</answer>' in review
    assert '<answer label="B">\nsecond\n</answer>' in review
    assert prompt in review


def test_anthropic_request_and_answer():
    anthropic = pytest.importorskip("anthropic")
    events = [
        {"type": "message_start", "message": {
            "id": "msg_1", "type": "message", "role": "assistant", "model": "claude-fable-5-1",
            "content": [], "stop_reason": None, "stop_sequence": None,
            "usage": {"input_tokens": 12, "output_tokens": 1}}},
        {"type": "content_block_start", "index": 0,
         "content_block": {"type": "thinking", "thinking": "", "signature": ""}},
        {"type": "content_block_delta", "index": 0,
         "delta": {"type": "thinking_delta", "thinking": "Tried the dilation."}},
        {"type": "content_block_delta", "index": 0,
         "delta": {"type": "signature_delta", "signature": "sig"}},
        {"type": "content_block_stop", "index": 0},
        {"type": "content_block_start", "index": 1, "content_block": {"type": "text", "text": ""}},
        {"type": "content_block_delta", "index": 1,
         "delta": {"type": "text_delta", "text": "Because 2^9 = -6."}},
        {"type": "content_block_stop", "index": 1},
        {"type": "message_delta", "delta": {"stop_reason": "end_turn", "stop_sequence": None},
         "usage": {"output_tokens": 40}},
        {"type": "message_stop"},
    ]  # fmt: skip
    seen = []
    http = _mock(_sse(events), {"request-id": "req_1"}, seen)
    client = anthropic.Anthropic(api_key="t", base_url=consult.ANTHROPIC_BASE_URL, http_client=http)
    result = consult.ask_anthropic(client, consult.consultants()["fable"], "Why 37?")

    (request,) = seen
    assert str(request.url) == "https://api.anthropic.com/v1/messages?beta=true"
    assert consult.FALLBACK_BETA in request.headers["anthropic-beta"]
    assert consult.BUDGET_BETA in request.headers["anthropic-beta"]
    body = json.loads(request.content)
    assert body["model"] == "claude-fable-5-1" and body["stream"] is True
    assert body["fallbacks"] == "default"
    assert body["thinking"] == {"type": "adaptive", "display": "summarized"}
    assert body["max_tokens"] == 128000
    assert body["output_config"] == {
        "effort": "high", "task_budget": {"type": "tokens", "total": 64000}
    }  # fmt: skip
    assert body["messages"] == [{"role": "user", "content": [
        {"type": "text", "text": "Why 37?", "cache_control": {"type": "ephemeral"}}]}]  # fmt: skip
    assert body["tools"] == [consult.CODE_TOOL]
    assert "budget_tokens" not in json.dumps(body)

    assert result["status"] == "complete" and result["fallback"] is False
    assert result["text"] == "Because 2^9 = -6."
    assert result["reasoning_summary"] == "Tried the dilation."
    assert result["request_id"] == "req_1" and result["served_by"] == "claude-fable-5-1"
    assert result["usage"]["output_tokens"] == 40


class _Block(SimpleNamespace):
    def model_dump(self, **_):
        return dict(vars(self))


def _fake_anthropic(*turns, model="claude-opus-4-8"):
    """A client whose streams return `turns` in order: (content, stop_reason, iterations)."""
    sent = []

    def stream(**params):
        content, stop_reason, iterations = turns[len(sent)]
        sent.append(params)
        usage = {"input_tokens": 10, "output_tokens": 100,
                 "iterations": [{"type": t} for t in iterations or []]}  # fmt: skip
        message = SimpleNamespace(
            content=content, stop_reason=stop_reason, model=model, stop_details=None,
            container=SimpleNamespace(id="container_1"),
            usage=SimpleNamespace(model_dump=lambda **_: usage))  # fmt: skip
        live = SimpleNamespace(get_final_message=lambda: message, request_id=f"req_{len(sent)}")

        class Manager:
            def __enter__(self):
                return live

            def __exit__(self, *exc):
                return False

        return Manager()

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(stream=stream)))
    return client, sent


def _text(t):
    return _Block(type="text", text=t)


def test_anthropic_fallback_and_refusal():
    """After a fallback, only the output that follows the last switch is the answer; a refusal is
    recorded as one."""
    switch = _Block(type="fallback")
    client, _ = _fake_anthropic(([_text("partial"), switch, _text("whole")], "end_turn", None))
    result = consult.ask_anthropic(client, FABLE, "q")
    assert result["text"] == "whole" and result["fallback"] and result["status"] == "complete"
    client, _ = _fake_anthropic(([_text("whole")], "end_turn", ["fallback_message"]))
    sticky = consult.ask_anthropic(client, FABLE, "q")
    assert sticky["fallback"] and sticky["text"] == "whole"
    client, _ = _fake_anthropic(([], "refusal", None))
    assert consult.ask_anthropic(client, FABLE, "q")["status"] == "refused"
    client, _ = _fake_anthropic(([_text("x")], "max_tokens", None))
    assert consult.ask_anthropic(client, FABLE, "q")["status"] == "truncated"


def test_anthropic_tool_loop_resumes_after_pause():
    """A paused tool loop is resumed with the turn so far, in the same container and with what is
    left of the budget; the answer is the text after the last tool call, and the record keeps
    every block."""
    fable = consult.consultants()["fable"]
    call = _Block(type="server_tool_use", id="t1", name="bash_code_execution", input={"cmd": "x"})
    result_block = _Block(type="bash_code_execution_tool_result", tool_use_id="t1")
    first = [_text("Let me check."), call, result_block]
    second = [_Block(type="thinking", thinking="It holds.", signature="s"), _text("Holds.")]
    client, sent = _fake_anthropic((first, "pause_turn", None), (second, "end_turn", None),
                                   model="claude-fable-5-1")  # fmt: skip
    result = consult.ask_anthropic(client, fable, "q")

    assert len(sent) == 2 and "container" not in sent[0]
    assert sent[1]["container"] == "container_1"
    assert sent[1]["messages"][1] == {"role": "assistant", "content": first}
    assert sent[1]["output_config"]["task_budget"]["remaining"] == 64000 - 100
    assert sent[0]["output_config"]["task_budget"] == {"type": "tokens", "total": 64000}
    assert result["text"] == "Holds." and result["status"] == "complete"
    assert result["tool_calls"] == 1 and len(result["requests"]) == 2
    assert result["usage"]["output_tokens"] == 200
    assert result["cost_usd"] == round((20 * 10 + 200 * 50) / 1e6, 4)
    assert [b["type"] for b in result["content"]] == [
        "text", "server_tool_use", "bash_code_execution_tool_result", "thinking", "text"
    ]  # fmt: skip
    assert "signature" not in result["content"][3]

    client, sent = _fake_anthropic(*[(first, "pause_turn", None)] * (1 + consult.MAX_CONTINUATIONS))
    assert consult.ask_anthropic(client, fable, "q")["status"] == "truncated"
    assert len(sent) == 1 + consult.MAX_CONTINUATIONS


def test_context_directories(tmp_path: Path):
    (tmp_path / "b.md").write_text("b")
    (tmp_path / "a.md").write_text("a")
    (tmp_path / "skip.txt").write_text("no")
    status = tmp_path / "b.md"
    assert consult.expand([status, tmp_path]) == [status, tmp_path / "a.md"]


def test_openai_request_and_answer():
    openai = pytest.importorskip("openai")
    response = {
        "id": "resp_1", "object": "response", "created_at": 0, "model": "test-model",
        "status": "completed", "parallel_tool_calls": True, "tool_choice": "auto", "tools": [],
        "output": [
            {"type": "reasoning", "id": "rs_1",
             "summary": [{"type": "summary_text", "text": "Tried the dilation."}]},
            {"type": "message", "id": "msg_1", "role": "assistant", "status": "completed",
             "content": [{"type": "output_text", "text": "Because 2^9 = -6.",
                          "annotations": []}]},
        ],
        "usage": {"input_tokens": 12, "output_tokens": 40, "total_tokens": 52,
                  "input_tokens_details": {"cached_tokens": 0},
                  "output_tokens_details": {"reasoning_tokens": 30}},
    }  # fmt: skip
    created = {**response, "status": "in_progress", "output": [], "usage": None}
    events = [
        {"type": "response.created", "sequence_number": 0, "response": created},
        {"type": "response.completed", "sequence_number": 1, "response": response},
    ]
    seen = []
    client = openai.OpenAI(api_key="test", base_url=consult.OPENAI_BASE_URL,
                           http_client=_mock(_sse(events), {}, seen))  # fmt: skip
    result = consult.ask_openai(client, GPT, "Why 37?")

    (request,) = seen
    assert str(request.url) == "https://api.openai.com/v1/responses"
    body = json.loads(request.content)
    assert body["model"] == "test-model" and body["input"] == "Why 37?" and body["stream"]
    assert body["reasoning"] == {"effort": "high", "summary": "auto"}
    assert body["store"] is False and body["max_output_tokens"] == 64000
    assert body["tools"] == [{"type": "code_interpreter", "container": {"type": "auto"}}]
    assert body["include"] == ["code_interpreter_call.outputs"]

    assert result["status"] == "complete"
    assert result["text"] == "Because 2^9 = -6."
    assert result["reasoning_summary"] == "Tried the dilation."
    assert result["request_id"] == "resp_1" and result["usage"]["output_tokens"] == 40


def _fake_providers(monkeypatch, answers: dict, calls: list):
    def fake(name):
        def ask(client, c, prompt):
            calls.append(c.name)
            if isinstance(answers[name], Exception):
                raise answers[name]
            answer = answers[name]
            status, text = answer if isinstance(answer, tuple) else ("complete", answer)
            return {"status": status, "served_by": c.model, "fallback": False,
                    "stop_reason": "end_turn", "stop_details": None, "request_id": "r",
                    "usage": {}, "reasoning_summary": "thought", "text": text}  # fmt: skip

        return ask

    for provider, name in (("anthropic", "fable"), ("openai", "chatgpt")):
        params = consult.PROVIDERS[provider][2]
        monkeypatch.setitem(consult.PROVIDERS, provider, (lambda: None, fake(name), params))


def test_records_are_written_once_and_resume(tmp_path: Path, monkeypatch):
    calls = []
    answers = {"fable": "F says.", "chatgpt": ConnectionError("down")}
    _fake_providers(monkeypatch, answers, calls)
    directory = tmp_path / "c" / "round-1"
    outcome = consult.run_round(directory, "the prompt", [FABLE, GPT], 1, lambda m: None)
    assert outcome["fable"] == "written" and outcome["chatgpt"].startswith("ConnectionError")
    record = json.loads((directory / "fable.json").read_text())
    assert record["prompt_sha256"] == consult.sha256("the prompt")
    assert record["params"]["fallbacks"] == "default" and record["consultation"] == "c"
    assert (directory / "fable.md").read_text() == "F says.\n"
    assert not (directory / "chatgpt.json").exists()  # a failure leaves no record

    answers["chatgpt"] = "G says."
    outcome = consult.run_round(directory, "the prompt", [FABLE, GPT], 1, lambda m: None)
    assert outcome == {"fable": "exists", "chatgpt": "written"}
    assert calls == ["fable", "chatgpt", "chatgpt"]
    with pytest.raises(consult.ConsultError):
        consult.run_round(directory, "another prompt", [FABLE, GPT], 1, lambda m: None)
    nameless = consult.Consultant("chatgpt2", "openai", None)
    outcome = consult.run_round(directory, "the prompt", [nameless], 1, lambda m: None)
    assert "no model" in outcome["chatgpt2"]


def test_truncated_answer_is_kept_and_asked_again(tmp_path: Path, monkeypatch):
    calls = []
    answers = {"fable": ("truncated", "")}
    _fake_providers(monkeypatch, answers, calls)
    directory = tmp_path / "c" / "round-1"
    for attempt in (1, 2):
        outcome = consult.run_round(directory, "the prompt", [FABLE], 1, lambda m: None)
        assert (
            outcome["fable"].startswith("truncated") and f"fable-{attempt}.json" in outcome["fable"]
        )
        kept = json.loads((directory / "attempts" / f"fable-{attempt}.json").read_text())
        assert kept["status"] == "truncated" and kept["reasoning_summary"] == "thought"
        assert not (directory / "fable.json").exists()
    answers["fable"] = "F says."
    assert consult.run_round(directory, "the prompt", [FABLE], 1, lambda m: None) == {
        "fable": "written"
    }
    assert calls == ["fable"] * 3
    assert consult.round_answers(directory) == [("fable", "F says.")]


def test_overrides(monkeypatch):
    args = SimpleNamespace(with_=["fable"], model=[], effort=["fable=xhigh"], no_code=True,
                           budget=["fable=0"], max_tokens=["fable=90000"])  # fmt: skip
    (fable,) = consult._chosen(args)
    assert (fable.effort, fable.budget, fable.max_tokens) == ("xhigh", 0, 90000)
    assert "task_budget" not in consult.anthropic_params(fable)["output_config"]
    assert consult.anthropic_params(fable)["betas"] == [consult.FALLBACK_BETA]
    assert "tools" not in consult.anthropic_params(fable)
    with pytest.raises(consult.ConsultError):
        consult._chosen(SimpleNamespace(**{**vars(args), "budget": ["fable=lots"]}))


def test_missing_key_leaves_no_record(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("CONSULT_ANTHROPIC_API_KEY", raising=False)
    outcome = consult.run_round(tmp_path / "round-1", "p", [FABLE], 1, lambda m: None)
    assert "CONSULT_ANTHROPIC_API_KEY" in outcome["fable"]
    assert not (tmp_path / "round-1" / "fable.json").exists()


def test_command_ask_then_review(tmp_path: Path, monkeypatch, capsys):
    calls = []
    _fake_providers(monkeypatch, {"fable": "F says.", "chatgpt": "G says."}, calls)
    monkeypatch.setenv("CONSULT_OPENAI_MODEL", "test-model")
    question = tmp_path / "q.md"
    question.write_text("Why 37?\n")
    context = tmp_path / "status.md"
    context.write_text("Where we are.\n")
    base = ["consult", "ask", "why-37", "--dir", str(tmp_path / "consultations"),
            "--question", str(question), "--context", str(context)]  # fmt: skip

    assert main([*base, "--dry-run"]) == 0
    assert "Where we are." in capsys.readouterr().out and calls == []
    assert not (tmp_path / "consultations").exists()

    assert main(base) == 0
    first = tmp_path / "consultations" / "why-37" / "round-1"
    assert "Where we are." in (first / "prompt.md").read_text()
    assert sorted(p.name for p in first.iterdir()) == [
        "chatgpt.json", "chatgpt.md", "fable.json", "fable.md", "prompt.md"
    ]  # fmt: skip

    review = ["consult", "review", "why-37", "--dir", str(tmp_path / "consultations")]
    assert main(review) == 0
    second = tmp_path / "consultations" / "why-37" / "round-2"
    labels = json.loads((second / "labels.json").read_text())
    assert labels == {"A": "chatgpt", "B": "fable"}  # name order, so the same prompt for all
    prompt = (second / "prompt.md").read_text()
    assert prompt.index("G says.") < prompt.index("F says.")
    assert json.loads((second / "fable.json").read_text())["round"] == 2

    assert main(["consult", "ask", "Bad Name", "--preset", "direction"]) == 2
    assert main(["consult", "ask", "x", "--with", "nobody", "--preset", "direction"]) == 2


def test_cost_counts_every_attempt_at_its_own_prices():
    """The shape of a real record (2026-10-20-budget-q1, s1-r2): Fable declined after one step,
    and Opus 4.8 ran the whole tool loop. Each attempt's last step names its model; the top-level
    usage holds only Opus's attempt."""
    steps = [
        {"type": "message", "model": "claude-fable-5-1", "input_tokens": 26,
         "output_tokens": 5000},
        {"type": "message", "input_tokens": 10, "cache_creation_input_tokens": 2000,
         "output_tokens": 100},
        {"type": "message", "input_tokens": 5, "cache_read_input_tokens": 3000,
         "output_tokens": 200},
        {"type": "fallback_message", "model": "claude-opus-4-8", "input_tokens": 24,
         "cache_read_input_tokens": 1000, "output_tokens": 8000},
    ]  # fmt: skip
    requests = [{"usage": {"input_tokens": 39, "output_tokens": 8300, "iterations": steps}}]
    fable = (26 * 10 + 5000 * 50) / 1e6
    opus = (39 * 5 + 8300 * 25 + 2000 * 6.25 + 4000 * 0.5) / 1e6
    assert consult.cost(requests, "claude-fable-5-1") == round(fable + opus, 4)
    assert [m for m, _ in consult.attempts(requests, "claude-fable-5-1")] == [
        "claude-fable-5-1", "claude-opus-4-8", "claude-opus-4-8", "claude-opus-4-8"
    ]  # fmt: skip
    # no fallback: no step is named, and every step is the requested model's
    plain = [{"usage": {"iterations": [{"type": "message", "output_tokens": 10}] * 3}}]
    assert {m for m, _ in consult.attempts(plain, "claude-fable-5-1")} == {"claude-fable-5-1"}
    assert consult.cost([{"usage": {"output_tokens": 1}}], "some-other-model") is None
