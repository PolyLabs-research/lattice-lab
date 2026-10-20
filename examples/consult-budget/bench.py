"""
What a consultation's effort is worth: Claude Fable on two questions already answered, at three
settings, with every claim checked by machine (rubric.md is the registered design).

    uv run --no-sync python examples/consult-budget/bench.py run     # the 12 calls (resumable)
    uv run --no-sync python examples/consult-budget/bench.py blind   # relabel answers for grading
    uv run --no-sync python examples/consult-budget/bench.py grade   # machine checks, rubric, costs

The records go to consultations/2026-10-20-budget-q1/ and -q2/, one consultant per arm and
replicate (s0-r1, ..., s2-r2), through lattice_lab.consult like any consultation. An answer cut
off at its limit is a failed answer of its arm, at its cost, and is not asked again.

The machine check evaluates every congruence and factorisation in an answer's JSON block in
F2[x, y]/(x^37 - 1, y^37 - 1) with this file's own arithmetic (a 37 x 37 array of bits,
multiplied by FFT). Expressions come from the model, so each is checked against a whitelist of
names and characters before sympy parses it, and each answer is graded in a subprocess with a
time limit.
"""

from __future__ import annotations

import json
import os
import random
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import TimeoutError as Timeout
from functools import reduce
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from lattice_lab import consult  # noqa: E402

M = 37
QUESTIONS = {"q1": "q1-five.md", "q2": "q2-sixteen.md"}
ARMS = {
    "s0": {"effort": "high", "budget": 64000, "code": False},
    "s1": {"effort": "high", "budget": 64000, "code": True},
    "s2": {"effort": "xhigh", "budget": 128000, "code": True},
}
REPLICATES = 2
CAP = 60.0  # dollars, for all 12 calls
WORST_QUESTION = 2 * (3.4 + 3.4 + 6.6)  # the most one question's six calls can cost
NINE = (1112, 2436, 3461, 10498, 13584, 17056, 18246, 26883, 28944)
FIVE = {
    "f1": [(0, 0), (2, 0), (2, 1), (2, 2)],
    "f2": [(2, 1), (3, 2), (3, 3)],
    "f3": [(3, 0), (3, 1), (3, 2)],
    "f4": [(3, 0), (3, 1), (3, 2), (3, 3)],
    "f5": [(0, 0), (2, 0), (2, 2), (3, 0), (3, 1), (3, 3)],
}


def directory(q: str) -> Path:
    return ROOT / "consultations" / f"2026-10-20-budget-{q}" / "round-1"


def arm_consultants() -> list[consult.Consultant]:
    return [consult.Consultant(f"{arm}-r{k}", "anthropic", "claude-fable-5-1", max_tokens=128000,
                               **settings)
            for arm, settings in ARMS.items() for k in range(1, REPLICATES + 1)]  # fmt: skip


def prompt(q: str) -> str:
    return consult.build_prompt((HERE / QUESTIONS[q]).read_text(), [])


# ---------------------------------------------------------------- the run


def answers(q: str) -> list[dict]:
    """Every record of a question, final or truncated."""
    d = directory(q)
    paths = sorted(d.glob("*.json")) + sorted((d / "attempts").glob("*.json"))
    return [json.loads(p.read_text()) for p in paths]


def spent() -> float:
    return sum(r.get("cost_usd") or 0 for q in QUESTIONS for r in answers(q))


def run() -> None:
    for q in QUESTIONS:
        d = directory(q)
        done = {r["consultant"]["name"] for r in answers(q)}
        todo = [c for c in arm_consultants() if c.name not in done]
        if not todo:
            continue
        if spent() + WORST_QUESTION > CAP:
            print(f"bench: stopping before {q}: ${spent():.2f} spent, cap ${CAP:.0f}")
            return
        print(f"bench: {q}: asking {[c.name for c in todo]}", flush=True)
        outcome = consult.run_round(d, prompt(q), todo, 1, lambda m: print(m, flush=True))
        print(json.dumps(outcome, indent=1), flush=True)
    print(f"bench: ${spent():.2f} spent")


# ---------------------------------------------------------------- the ring F2[Z/37 x Z/37]


def mono(i: int, j: int) -> np.ndarray:
    a = np.zeros((M, M), dtype=np.uint8)
    a[i % M, j % M] = 1
    return a


def mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    c = np.fft.ifft2(np.fft.fft2(a) * np.fft.fft2(b)).real
    return (np.rint(c).astype(np.int64) & 1).astype(np.uint8)


def power(a: np.ndarray, e: int) -> np.ndarray:
    if a.sum() == 1:  # a monomial: multiply the exponents
        i, j = np.argwhere(a)[0]
        return mono(int(i) * e, int(j) * e)
    if e < 0:
        raise Unreadable("a negative power of a polynomial with more than one term")
    result = mono(0, 0)
    while e:
        if e & 1:
            result = mul(result, a)
        a = mul(a, a)
        e >>= 1
    return result


class Unreadable(Exception):
    pass


def points(orbits) -> set[tuple[int, int]]:
    out = set()
    for a, b in orbits:
        for p, q in ((a, b), (b, a)):
            for sp in (1, -1):
                for sq in (1, -1):
                    out.add((sp * p, sq * q))
    return out


def family_orbits(n: int) -> list[tuple[int, int]]:
    order = sorted({(a, b) for a in range(5) for b in range(a + 1)})
    if not 0 < n < 1 << len(order):
        raise Unreadable(f"no family rule {n}")
    return [o for i, o in enumerate(order) if n >> i & 1]


# ---------------------------------------------------------------- parsing the model's claims

_ALLOWED = re.compile(r"^[A-Za-z0-9_\s+\-*^/(),]*$")
_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_BUILTIN = {"x", "y", "O", "t", "R", "f1", "f2", "f3", "f4", "f5"}


def parse(text: str, defined: dict):
    """A whitelisted expression, parsed by sympy with only the names of the question."""
    import sympy
    from sympy.parsing.sympy_parser import convert_xor, parse_expr, standard_transformations

    if not isinstance(text, str) or not _ALLOWED.match(text) or len(text) > 20000:
        raise Unreadable(f"characters outside the expression syntax: {str(text)[:80]!r}")
    for name in _NAME.findall(text):
        if name not in _BUILTIN and name not in defined:
            raise Unreadable(f"unknown name {name!r}")
    x, y = sympy.symbols("x y")

    def orbit_sum(X, Y, orbits):
        return sum(X**p * Y**q for p, q in points(orbits))

    names = {
        "x": x,
        "y": y,
        "O": lambda a, b: orbit_sum(x, y, [(int(a), int(b))]),
        "t": lambda z: z + 1 / z,
        "R": lambda n: orbit_sum(x, y, family_orbits(int(n))),
        **{k: (lambda X, Y, o=o: orbit_sum(X, Y, o)) for k, o in FIVE.items()},
        **defined,
    }
    return parse_expr(text, local_dict=names, transformations=standard_transformations
                      + (convert_xor,))  # fmt: skip


def evaluate(e) -> np.ndarray:
    """A sympy expression as an element of F2[Z/37 x Z/37]."""
    if e.is_Symbol:
        if e.name in ("x", "y"):
            return mono(1, 0) if e.name == "x" else mono(0, 1)
        raise Unreadable(f"free symbol {e}")
    if e.is_Integer:
        return mono(0, 0) * (int(e) % 2)
    if e.is_Rational:
        if e.q % 2 == 0:
            raise Unreadable(f"{e} is not defined over GF(2)")
        return mono(0, 0) * (e.p % 2)
    if e.is_Add:
        return reduce(np.bitwise_xor, (evaluate(a) for a in e.args))
    if e.is_Mul:
        return reduce(mul, (evaluate(a) for a in e.args))
    if e.is_Pow:
        base, exp = e.args
        if not exp.is_Integer or abs(int(exp)) > 10**30:
            raise Unreadable(f"exponent {exp}")
        return power(evaluate(base), int(exp))
    raise Unreadable(f"cannot evaluate {type(e).__name__}")


def claims_block(text: str):
    blocks = re.findall(r"```json\s*(.*?)```", text, flags=re.S)
    if not blocks:
        return None
    try:
        return json.loads(blocks[-1])
    except json.JSONDecodeError:
        return None


def check(text: str) -> dict:
    """The machine's verdict on an answer's JSON block."""
    block = claims_block(text)
    out = {"json": block is not None, "congruences": [], "factorisations": [], "found": [],
           "true": 0, "false": 0, "unreadable": 0}  # fmt: skip
    if not isinstance(block, dict):
        return out
    defined = {}
    try:
        for name, expr in (block.get("definitions") or {}).items():
            if not _NAME.fullmatch(name) or name in _BUILTIN or name.startswith("_"):
                raise Unreadable(f"bad name {name!r}")
            defined[name] = parse(expr, defined)
    except Exception as exc:  # a definition that does not parse makes its uses unreadable
        out["definitions_error"] = str(exc)[:200]

    def verdict(entry: dict, fn) -> dict:
        try:
            ok, extra = fn()
            out["true" if ok else "false"] += 1
            return {"claim": entry, "holds": ok, **extra}
        except Exception as exc:
            out["unreadable"] += 1
            return {"claim": entry, "holds": None, "error": str(exc)[:200]}

    for c in block.get("congruences") or []:

        def cong(c=c):
            if not isinstance(c, dict):
                raise Unreadable("not an object")
            return bool((evaluate(parse(c["lhs"], defined)) ==
                         evaluate(parse(c["rhs"], defined))).all()), {}  # fmt: skip

        out["congruences"].append(verdict(c, cong))
    for f in block.get("factorisations") or []:

        def fact(f=f):
            rule = int(f["rule"])
            target = evaluate(parse(f"R({rule})", defined))
            product, cubed = mono(0, 0), False
            for expr, exp in f["factors"]:
                value = evaluate(parse(expr, defined))
                product = mul(product, power(value, int(exp)))
                cubed |= int(exp) % 3 == 0 and int(exp) > 0 and value.sum() >= 2
            ok = bool((product == target).all())
            return ok, {"rule": rule, "cube_factor": cubed}

        result = verdict(f, fact)
        out["factorisations"].append(result)
        if result["holds"] and result.get("cube_factor"):
            out["found"].append(result["rule"])
    out["found"] = sorted(set(out["found"]))
    return out


def check_safely(text: str, seconds: int = 300) -> dict:
    with ProcessPoolExecutor(max_workers=1) as pool:
        future = pool.submit(check, text)
        try:
            return future.result(timeout=seconds)
        except Timeout:
            for p in pool._processes.values():
                p.kill()
            return {"json": True, "timeout": True, "true": 0, "false": 0, "unreadable": 1,
                    "found": [], "congruences": [], "factorisations": []}  # fmt: skip


# ---------------------------------------------------------------- blind grading and results


def blind() -> None:
    """Write every complete answer under a random label, with the machine's verdict, for the
    rubric; the key goes to blind-key.json, to be read only after grades.json is written."""
    key_path = HERE / "blind-key.json"
    if key_path.exists():
        raise SystemExit("already blinded; grade from blind/ and grades.json")
    items = [(q, r) for q in QUESTIONS for r in answers(q) if r["status"] == "complete"]
    labels = random.Random(os.urandom(16)).sample(range(100, 1000), len(items))
    (HERE / "blind").mkdir(exist_ok=True)
    key = {}
    for label, (q, r) in zip(labels, items, strict=True):
        machine = check_safely(r["text"])
        body = (f"# Answer {label} ({q})\n\nMachine check: {machine['true']} hold, "
                f"{machine['false']} false, {machine['unreadable']} unreadable; found: "
                f"{machine['found']}\n\n" + r["text"])  # fmt: skip
        (HERE / "blind" / f"{label}.md").write_text(body)
        key[str(label)] = {"question": q, "consultant": r["consultant"]["name"]}
    key_path.write_text(json.dumps(key, indent=1, sort_keys=True) + "\n")
    print(f"bench: {len(items)} answers in blind/; grade them into grades.json")


def succeeds(q: str, machine: dict, rubric: dict | None) -> bool | None:
    if rubric is None:
        return None
    if machine["false"]:
        return False
    if q == "q1":
        return all(rubric.get(k) for k in ("R1", "R2", "R3", "R6"))
    return set(NINE) <= set(machine["found"]) and bool(rubric.get("Q1") and rubric.get("Q2"))


def grade() -> None:
    key = json.loads((HERE / "blind-key.json").read_text())
    grades = json.loads((HERE / "grades.json").read_text())
    label_of = {(v["question"], v["consultant"]): k for k, v in key.items()}
    rows = []
    for q in QUESTIONS:
        for r in answers(q):
            name = r["consultant"]["name"]
            machine = check_safely(r["text"]) if r["status"] == "complete" else None
            rubric = grades.get(label_of.get((q, name), ""), None)
            ok = succeeds(q, machine, rubric) if machine else False
            rows.append({
                "question": q, "arm": name.split("-")[0], "consultant": name,
                "status": r["status"], "cost": r.get("cost_usd"), "seconds": r["seconds"],
                "tool_calls": r.get("tool_calls", 0), "thinking": r["usage"].get("thinking_tokens"),
                "output": r["usage"].get("output_tokens"), "machine": machine, "rubric": rubric,
                "success": ok,
            })  # fmt: skip
    summary = {}
    for arm in ARMS:
        mine = [x for x in rows if x["arm"] == arm]
        cost = sum(x["cost"] or 0 for x in mine)
        wins = sum(bool(x["success"]) for x in mine)
        summary[arm] = {
            "answers": len(mine), "successes": wins, "cost": round(cost, 2),
            "mean_cost": round(cost / len(mine), 2) if mine else None,
            "false_claims": sum((x["machine"] or {}).get("false", 0) for x in mine),
            "per_success": round(cost / wins, 2) if wins else None,
            "per_question": {q: sum(bool(x["success"]) for x in mine if x["question"] == q)
                             for q in QUESTIONS},
        }  # fmt: skip
    s1, s2 = summary["s1"], summary["s2"]
    if s1["answers"] and s2["answers"]:
        p1, p2 = s1["successes"] / s1["answers"], s2["successes"] / s2["answers"]
        c = s1["mean_cost"] + (1 - p1) * s2["mean_cost"]
        p = 1 - (1 - p1) * (1 - p2)
        summary["s1_then_s2"] = {"mean_cost": round(c, 2), "success_rate": round(p, 2),
                                 "per_success": round(c / p, 2) if p else None}  # fmt: skip
    (HERE / "results.json").write_text(json.dumps({"answers": rows, "summary": summary},
                                                  indent=1, default=str) + "\n")  # fmt: skip
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    {"run": run, "blind": blind, "grade": grade}[sys.argv[1]]()
