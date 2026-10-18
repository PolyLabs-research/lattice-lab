"""
The triangle pilot's registered test: the triangle laws at sizes nobody has computed.

    uv run python examples/llm-pilot-triangle/study.py register
    uv run python examples/llm-pilot-triangle/study.py run
    uv run lattice-lab verify --lab examples/llm-pilot-triangle

The pilot's targets (card.md) are the exact 2-parts of the two triangle parity rules, edge (E) and
edge+vertex (E+VO+VS), for odd parts m >= 3. These predictions are registered before the agent
starts. They come from the law, with its odd part L(m) computed from eigenvalues
(eigen.odd_part), at 20 even sizes above 398, the largest computed for these rules so far:

- m >= 3: P(n) = 2^(v+1) L(m). If the agent proves its theorems, these follow from them, given
  the torus model that the tests check against the engine;
- m = 1, beyond the theorems, from the hand proof: the edge rule has period 2^v = n, and the
  edge+vertex rule dies (period 1).

Each prediction is checked exactly by the atlas's engine (engine.Torus.check). Nothing is
excluded: no period of either rule has been computed above 398, and no torus of these sizes was
built while preparing the study.
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
RULES = {"E": ("E",), "E+VO+VS": ("E", "VO", "VS")}
SIZES = [408, 410, 416, 420, 434, 448, 480, 496, 504, 508, 512, 544, 560, 576, 584, 640, 672, 704,
         768, 1024]  # fmt: skip


def split(n: int) -> tuple[int, int]:
    v = (n & -n).bit_length() - 1
    return v, n >> v


def predicted(rule: str, n: int) -> int:
    v, m = split(n)
    if m == 1:
        return 2**v if rule == "E" else 1
    return 2 ** (v + 1) * eigen.odd_part(atlas3.polynomial("triangle", RULES[rule]), m)


def question() -> dict:
    return {
        "id": "llm-pilot-triangle",
        "title": "Do the triangle laws hold at sizes above 398?",
        "statement": "For n = 2^v m with m odd, on the atlas's triangular torus: both parity rules "
        "have P(n) = 2^(v+1) L(m) for m >= 3, with L(m) the odd part computed from eigenvalues; "
        "for m = 1 the edge rule has period 2^v and the edge+vertex rule dies.",
        "rules": RULES,
        "sizes": SIZES,
        "excluded_seen": [],
        "checker": "engine.Torus('triangle', shells, n).check(predicted)",
        "hypotheses": {
            "law": "every prediction holds",
            "theorem_scope": "every prediction with m >= 3 holds (the pilot's theorems)",
        },
    }


def predictions() -> list[dict]:
    out = []
    for rule in RULES:
        for n in SIZES:
            v, m = split(n)
            scope = "theorem" if m >= 3 else "beyond"
            out.append(
                {
                    "rule": rule,
                    "n": n,
                    "v": v,
                    "m": m,
                    "predicted": predicted(rule, n),
                    "scope": scope,
                }
            )
    return out


def execute(path: Path, workers: int) -> None:
    import json

    done = set()
    if path.exists():
        rows = [json.loads(line) for line in path.read_text().splitlines() if line]
        done = {(r["rule"], r["n"]) for r in rows}
    # The small sizes first, so an interrupted run has the most finished.
    for body in sorted(predictions(), key=lambda b: b["n"]):
        if (body["rule"], body["n"]) in done:
            continue
        torus = engine.Torus("triangle", RULES[body["rule"]], body["n"])
        check = torus.check(body["predicted"])
        append_records(path, [{**body, **check}])


def decide(rows: list[dict], registered: list[dict]) -> dict:
    key = lambda r: (r["rule"], r["n"])  # noqa: E731
    by_key = {key(r): r for r in rows}
    missing = [key(p) for p in registered if key(p) not in by_key]
    held = [key(p) for p in registered if by_key.get(key(p), {}).get("is_period")]
    failed = [key(p) for p in registered if key(p) in by_key and not by_key[key(p)]["is_period"]]
    scope = [key(p) for p in registered if p["scope"] == "theorem"]
    return {
        "held": held,
        "failed": failed,
        "missing": missing,
        "law": "supported" if not failed and not missing else "refuted",
        "theorem_scope": "supported" if all(k in held for k in scope) else "refuted",
    }


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
