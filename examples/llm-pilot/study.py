"""
The pilot's registered test: the hexagon law at sizes nobody has computed.

    uv run python examples/llm-pilot/study.py register
    uv run python examples/llm-pilot/study.py run
    uv run lattice-lab verify --lab examples/llm-pilot

The pilot's target (card.md) is the hexagon law's 2-part for m >= 5. These predictions are
registered before the agent starts. They come from the law, with its odd part R(m) computed from
eigenvalues (eigen.odd_part), at even sizes above 400, the largest computed so far:

- m >= 5: P(n) = 2^(v+1) R(m). If the agent proves its theorem, these follow from it, given the
  torus model that the tests check against the engine;
- m = 3: P(n) = 2^v, from the hand proof, beyond the pilot's theorem;
- m = 1: the torus dies, period 1, also beyond it.

Each prediction is checked exactly by the atlas's engine (engine.Torus.check). Excluded and
declared: n = 416, 448 and 640. The engine built those tori, with their states past the
transient, while timing this study. No period was computed.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "linear-atlas-3"))

import atlas3  # noqa: E402
import eigen  # noqa: E402

from lattice_lab.study import Study, append_records, main  # noqa: E402

engine = atlas3.engine
SIZES = [412, 418, 424, 432, 480, 512, 544, 576, 608, 704, 768, 800, 832, 896, 1024]
SEEN = [416, 448, 640]


def split(n: int) -> tuple[int, int]:
    v = (n & -n).bit_length() - 1
    return v, n >> v


def predicted(n: int) -> int:
    v, m = split(n)
    if m == 1:
        return 1
    if m == 3:
        return 2**v
    return 2 ** (v + 1) * eigen.odd_part(atlas3.polynomial("hexagon", ("H1",)), m)


def question() -> dict:
    return {
        "id": "llm-pilot-hexagon",
        "title": "Does the hexagon law hold at sizes above 400?",
        "statement": "For n = 2^v m with m odd: P(n) = 2^(v+1) R(m) for m >= 5, with R(m) the odd "
        "part computed from eigenvalues; 2^v for m = 3; 1 (the torus dies) for m = 1.",
        "sizes": SIZES,
        "excluded_seen": SEEN,
        "checker": "engine.Torus('hexagon', ('H1',), n).check(predicted)",
        "hypotheses": {
            "law": "every prediction holds",
            "theorem_scope": "every prediction with m >= 5 holds (the pilot's theorem)",
        },
    }


def predictions() -> list[dict]:
    out = []
    for n in SIZES:
        v, m = split(n)
        scope = "theorem" if m >= 5 else "beyond"
        out.append({"n": n, "v": v, "m": m, "predicted": predicted(n), "scope": scope})
    return out


def execute(path: Path, workers: int) -> None:
    import json

    done = set()
    if path.exists():
        done = {json.loads(line)["n"] for line in path.read_text().splitlines() if line}
    for body in predictions():
        if body["n"] in done:
            continue
        torus = engine.Torus("hexagon", ("H1",), body["n"])
        check = torus.check(body["predicted"])
        append_records(path, [{**body, **check}])


def decide(rows: list[dict], registered: list[dict]) -> dict:
    by_n = {r["n"]: r for r in rows}
    missing = [p["n"] for p in registered if p["n"] not in by_n]
    held = [p["n"] for p in registered if by_n.get(p["n"], {}).get("is_period")]
    failed = [p["n"] for p in registered if p["n"] in by_n and not by_n[p["n"]]["is_period"]]
    scope = [p["n"] for p in registered if p["scope"] == "theorem"]
    return {
        "held": held,
        "failed": failed,
        "missing": missing,
        "law": "supported" if not failed and not missing else "refuted",
        "theorem_scope": "supported" if all(n in held for n in scope) else "refuted",
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
