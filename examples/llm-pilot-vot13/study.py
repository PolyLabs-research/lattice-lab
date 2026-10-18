"""
The VO + T13 pilot's registered test: the orchestrator's law at sizes nobody has computed, and
the observed periods there, against which the agent's own law is judged afterwards.

    uv run python examples/llm-pilot-vot13/study.py register
    uv run python examples/llm-pilot-vot13/study.py run
    uv run lattice-lab verify --lab examples/llm-pilot-vot13

In this pilot the agent has to find the law itself, so it is not registered here: the agent
fixes it in its own submission, and the judge compares it with these records, which the agent
never sees. What is registered, before the agent starts, is the orchestrator's own law, read off
the sizes up to 128 (all computed before) and the eigenvalue argument of TriTwoPart.lean:

- m >= 3: P(n) = 2^(v+1) L(m), with L(m) the odd part computed from eigenvalues;
- m = 1, v >= 2: P(n) = 2^(v-1).

Each record holds the exact period, found by exact.Torus, so any law can be checked against it.
VO + T13 has been computed at n <= 282 in round 3 and at n <= 128 while planning this pilot;
these 20 sizes are all above 398. Nothing is excluded.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import exact  # noqa: E402
from exact import atlas3  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

sys.path.insert(0, str(HERE.parent / "linear-atlas-3"))
import eigen  # noqa: E402

SHELLS = ("VO", "T13")
SIZES = [408, 410, 416, 420, 434, 448, 480, 496, 504, 508, 512, 544, 560, 576, 584, 640, 672, 704,
         768, 1024]  # fmt: skip


def split(n: int) -> tuple[int, int]:
    v = (n & -n).bit_length() - 1
    return v, n >> v


def predicted(n: int) -> int:
    v, m = split(n)
    if m == 1:
        return 2 ** (v - 1)
    return 2 ** (v + 1) * eigen.odd_part(atlas3.polynomial("triangle", SHELLS), m)


def question() -> dict:
    return {
        "id": "llm-pilot-vot13",
        "title": "VO + T13's period on the atlas's triangular torus above 398",
        "statement": "For n = 2^v m with m odd: P(n) = 2^(v+1) L(m) for m >= 3, with L(m) the odd "
        "part computed from eigenvalues, and P(n) = 2^(v-1) for m = 1 (the orchestrator's law). "
        "The exact period is recorded at each size, so that the agent's own law, fixed in its "
        "submission, can be judged against it.",
        "rule": "triangle VO+T13",
        "sizes": SIZES,
        "excluded_seen": [],
        "checker": "exact.check(('VO', 'T13'), n, predicted)",
        "hypotheses": {
            "law": "every prediction holds",
            "m1": "the m = 1 predictions hold (P = 2^(v-1))",
        },
    }


def predictions() -> list[dict]:
    out = []
    for n in SIZES:
        v, m = split(n)
        out.append({"n": n, "v": v, "m": m, "predicted": predicted(n)})
    return out


def execute(path: Path, workers: int) -> None:
    import json

    done = set()
    if path.exists():
        done = {json.loads(line)["n"] for line in path.read_text().splitlines() if line}
    for body in sorted(predictions(), key=lambda b: b["n"]):
        if body["n"] in done:
            continue
        append_records(path, [{**body, **exact.check(SHELLS, body["n"], body["predicted"])}])


def decide(rows: list[dict], registered: list[dict]) -> dict:
    by_n = {r["n"]: r for r in rows}
    missing = [p["n"] for p in registered if p["n"] not in by_n]
    held = [p["n"] for p in registered if by_n.get(p["n"], {}).get("is_period")]
    failed = [p["n"] for p in registered if p["n"] in by_n and not by_n[p["n"]]["is_period"]]
    m1 = [p["n"] for p in registered if p["m"] == 1]
    return {
        "held": held,
        "failed": failed,
        "missing": missing,
        "law": "supported" if not failed and not missing else "refuted",
        "m1": "supported" if all(n in held for n in m1) else "refuted",
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
