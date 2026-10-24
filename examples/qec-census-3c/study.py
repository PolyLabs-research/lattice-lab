"""
Census stage 3c: the registered continuation of stage 3b (examples/qec-census-3b) on the tori its
run could not reach, with stage 3b's predictions copied verbatim.

    uv run --no-sync python examples/qec-census-3c/study.py register
    uv run --no-sync python examples/qec-census-3c/study.py run --workers 4
    uv run --no-sync python examples/qec-census-3c/study.py resume --workers 4  (after a stop)
    uv run --no-sync lattice-lab verify --lab examples/qec-census-3c

**Why.** Stage 3b's registered run recorded 73 tori (every random torus and 51 extrapolation
tori), then stopped making progress at 2 x 67. Its characters live in GF(2^66), and
bb._irreducible finds the field's polynomial by trial division against every polynomial of
degree <= d/2: about 2^34 divisions per candidate at d = 66. A stack sample showed the run inside
bb._irreducible, called from stage 3b's criterion_e. It was stopped then. Nothing had been
computed on 2 x 67 (criterion_e runs first), and its ledger ends at run_started: no
observations, no verdict. Stage 3b neither edits that ledger nor these records.

**Two in-process changes.** Inside this study's run process, and only there:
- **bb._irreducible** is replaced by `irreducible_fast`. It scans the same candidates in the
  same order, (1 << d) | 1, then each odd polynomial after it, and tests each by Ben-Or's
  criterion: f of degree d is irreducible exactly when gcd(f, x^(2^i) - x mod f) = 1 for
  i = 1, ..., d // 2. That is the property trial division tests (no factor of degree <= d / 2),
  so both return the smallest irreducible of degree d, and so the same Field. The tests check
  that the two agree for every d from 2 to 26, and that the fast one's output is irreducible by
  trial division for several d up to 40.
- **census3.zero_masks** is replaced by `zero_masks_wide`, which holds each field element in two
  64-bit words. census3 packs them into int64, which overflows once d >= 64 (2 x 67 is
  GF(2^66)); stage 3b never got that far, so it never met this. The adversarial review before
  registration found it. The tests check that the masks are identical to census3's on stage-1
  tori, and the two-word comparison on synthetic 66-bit values.

bb.py, census3.py and every other file are unchanged; their hashes are recorded as stage 3b
recorded them.

**Everything else is stage 3b's:** the tori (its registered list, minus those with a record
there), the instruments (fast.py, census3.py), the guard (stage 3b's `opened`), the job (stage
3b's `execute` body, through `job`), the predictions (stage 3b's ledger entries, copied verbatim)
and the rules (stage 3b's `decide`, on stage 3b's records and these together).

**The verdict.** Stage 3b's decide on the union of both studies' records. Every stage 3b record
is cited by offset and sha256 in the question, and `consistency` checks that they, stage 3b's
ledger head, the tori and this study's code are still as registered, before the run and again
in decide. The combined verdict is this study's, and stage 3b's own ledger keeps no verdict.
Stage 3b's records alone already fail P1 and P2 (the question's `known_at_registration`), so
the combined verdict is fail; this run settles P0 and P3 and the per-torus results.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import sys
from contextlib import contextmanager
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
S3B_DIR = HERE.parent / "qec-census-3b"


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


s3b = _load("qec_census_stage3b_study", S3B_DIR / "study.py")
bb, c3 = s3b.bb, s3b.c3

from lattice_lab.ledger import Ledger, record_lines  # noqa: E402
from lattice_lab.study import Study, append_records, main  # noqa: E402

ID = "qec-census-stage3c"
S3B_RECORDS = S3B_DIR / "records.jsonl"
S3B_LEDGER = S3B_DIR / "ledger.jsonl"


def _pmul_mod(a: int, b: int, f: int) -> int:
    df, r = f.bit_length() - 1, 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> df & 1:
            a ^= f
    return r


def _pgcd(a: int, b: int) -> int:
    while b:
        a, b = b, bb._pmod(a, b)
    return a


def irreducible_fast(d: int) -> int:
    """The smallest irreducible polynomial of degree d over GF(2), as bb._irreducible defines
    it (the same candidates in the same order), by Ben-Or's test."""
    for p in range((1 << d) | 1, 1 << (d + 1), 2):
        x, ok = 0b10, True
        for _ in range(d // 2):
            x = _pmul_mod(x, x, p)  # x^(2^i) mod p
            if _pgcd(p, x ^ 0b10) != 1:
                ok = False
                break
        if ok:
            return p
    raise ValueError(d)


MASK64 = (1 << 64) - 1


def zero_masks_wide(ell: int, m: int):
    """census3.zero_masks, with the field elements held in two 64-bit words instead of one int64,
    so fields GF(2^d) with 64 <= d <= 128 fit. Everything else is census3's: the guard, the
    characters, the pairs, the comparison (A(chi) = 0 exactly when 1 ^ u(chi) ^ v(chi) = 0) and
    the masks. For d < 64 the high word is zero and the result is census3's."""
    c3.guard(ell, m)
    (_, lo), (_, mo) = bb.two_part(ell), bb.two_part(m)
    N = math.lcm(lo, mo)
    F = bb._field(N)
    roots = [F.pow(F.zeta, e) for e in range(N)]
    chars = [(j, k) for j in range(lo) for k in range(mo)]
    value = [[roots[(j * (N // lo) * p + k * (N // mo) * q) % N] for j, k in chars]
             for p in range(ell) for q in range(m)]  # fmt: skip
    pairs = np.array(list(itertools.combinations(range(1, ell * m), 2)), dtype=np.int64)
    zero = _zeros(value, pairs)
    words = (len(chars) + 63) // 64
    masks = np.zeros((len(pairs), words), dtype=np.uint64)
    for c in range(len(chars)):
        masks[:, c // 64] |= zero[:, c].astype(np.uint64) << np.uint64(c % 64)
    return pairs, masks


def _zeros(value: list[list[int]], pairs) -> np.ndarray:
    """zero[i, c]: value[0][c] ^ value[u_i][c] ^ value[v_i][c] == 0, on 128-bit values."""
    if any(x >> 128 for row in value for x in row):
        raise ValueError("a field element wider than 128 bits")
    lo = np.array([[x & MASK64 for x in row] for row in value], dtype=np.uint64)
    hi = np.array([[x >> 64 for x in row] for row in value], dtype=np.uint64)
    a, b = pairs[:, 0], pairs[:, 1]
    return ((lo[0][None, :] ^ lo[a] ^ lo[b]) == 0) & ((hi[0][None, :] ^ hi[a] ^ hi[b]) == 0)


@contextmanager
def patched():
    """The two in-process changes: bb._irreducible and census3.zero_masks."""
    original, masks = bb._irreducible, c3.zero_masks
    bb._irreducible, c3.zero_masks = irreducible_fast, zero_masks_wide
    bb._field.cache_clear()
    try:
        yield
    finally:
        bb._irreducible, c3.zero_masks = original, masks
        bb._field.cache_clear()


def _s3b_rows() -> list[tuple[int, str, dict]]:
    return [(off, sha, json.loads(line)) for off, sha, line in record_lines(S3B_RECORDS)]


def _s3b_ledger() -> list[dict]:
    return [json.loads(x) for x in S3B_LEDGER.read_text().splitlines() if x.strip()]


def tori() -> list[tuple[int, int]]:
    done = {(r["l"], r["m"]) for _, _, r in _s3b_rows()}
    t = s3b.tori()
    return [x for g in ("random", "extrapolation", "exposed") for x in t[g] if x not in done]


HASHED = {"study_py": HERE / "study.py", "tests_py": ROOT / "tests" / "test_qec_census_3c.py",
          **{f"s3b_{k}": v for k, v in s3b.HASHED.items()}}  # fmt: skip


def code_hashes() -> dict[str, str]:
    return {k: hashlib.sha256(Path(p).read_bytes()).hexdigest() for k, p in HASHED.items()}


def question() -> dict:
    led = _s3b_ledger()
    return {"id": ID, "continues": "examples/qec-census-3b",
            "s3b_question": led[0]["hash"], "s3b_run_started": led[-1]["hash"],
            "s3b_last_entry": led[-1]["kind"],
            "s3b_records": [{"offset": o, "sha256": s, "torus": f"{r['l']}x{r['m']}"}
                            for o, s, r in _s3b_rows()],
            "tori": [list(t) for t in tori()],
            "change": ["bb._irreducible replaced in-process by irreducible_fast (Ben-Or): the same "
                       "smallest irreducible polynomial, so the same fields",
                       "census3.zero_masks replaced in-process by zero_masks_wide: field elements "
                       "in two 64-bit words, so GF(2^d) with d >= 64 does not overflow int64; the "
                       "same masks wherever census3's fit"],
            "known_at_registration": "stage 3b's 73 records were read to list the remaining "
                                     "tori; on them stage 3b's decide already gives P1 = fail "
                                     "(3x35, 5x21) and P2 = fail (2x51, 3x34, 3x40, 5x24, 8x15, "
                                     "3x41), so the combined verdict is fail whatever the "
                                     "remaining tori show; this run settles P0 and P3 and the "
                                     "per-torus results",
            "stopped_at": "2x67: bb._irreducible(66) by trial division, stack sampled",
            "seen_before": "while timing irreducible_fast before registration, criterion_e(2, 67) "
                           "was evaluated once (False); no code on any remaining torus was built",
            "sha256": code_hashes()}  # fmt: skip


def predictions() -> list[dict]:
    """Stage 3b's prediction bodies, verbatim, with a note of where they come from. Their
    "question" link is left out: register links each to this study's question."""
    return [{"copied_from": e["hash"], **_unlinked(e["body"])} for e in _s3b_ledger()
            if e["kind"] == "prediction"]  # fmt: skip


def _unlinked(body: dict) -> dict:
    return {k: v for k, v in body.items() if k not in ("question", "copied_from")}


def _rows(path: Path) -> list[dict]:
    return [json.loads(x) for _, _, x in record_lines(Path(path))]


def _registered_question() -> dict | None:
    entries = Ledger(HERE / "ledger.jsonl").entries
    return entries[0]["body"] if entries else None


def consistency() -> list[str]:
    """What must still be as registered: this study's code, stage 3b's cited records and ledger
    head, and the list of tori."""
    q = _registered_question()
    if q is None:
        return ["stage 3c is not registered"]
    problems = []
    if q["sha256"] != code_hashes():
        problems.append("the code differs from stage 3c's registration")
    now = question()
    for key in ("s3b_records", "s3b_run_started", "s3b_last_entry", "tori"):
        if q.get(key) != now[key]:
            problems.append(f"{key} differs from stage 3c's registration")
    return problems


def execute(path: Path, workers: int) -> None:
    problems = consistency()
    if problems:
        raise RuntimeError("; ".join(problems))
    done = {(r["l"], r["m"]) for r in _rows(path)}
    with patched():
        # stage 3b's job, one torus at a time, into this study's records
        for ell, m in tori():
            if (ell, m) in done:
                continue
            s3b_execute_one(path, ell, m, workers)


def s3b_execute_one(path: Path, ell: int, m: int, workers: int) -> None:
    """Stage 3b's execute, restricted to one torus (it skips every torus with a record in
    `path`, so a records file holding all but this one makes it run exactly this torus)."""
    tmp = Path(path).with_suffix(".one")
    others = [{"l": a, "m": b} for a, b in
              [x for g in s3b.tori().values() for x in g] if (a, b) != (ell, m)]  # fmt: skip
    tmp.write_text("".join(json.dumps(o) + "\n" for o in others))
    try:
        s3b.execute(tmp, workers)
        new = [r for r in _rows(tmp) if r.get("job") == "torus"]
        stamp = {k: v for k, v in code_hashes().items() if k in ("study_py", "tests_py")}
        append_records(path, [r | {"study": ID, "s3c_sha256": stamp} for r in new])
    finally:
        tmp.unlink(missing_ok=True)


def decide(rows: list[dict], registered: list[dict]) -> dict:
    combined = [r for _, _, r in _s3b_rows()] + [r for r in rows if r.get("job") == "torus"]
    s3b_preds = [e["body"] for e in _s3b_ledger() if e["kind"] == "prediction"]
    out = s3b.decide(combined, s3b_preds)
    problems = consistency()
    if registered and [_unlinked(p) for p in registered] != [_unlinked(p) for p in s3b_preds]:
        problems.append("the predictions differ from stage 3b's")
    seen = [(r["l"], r["m"]) for r in combined]
    if len(seen) != len(set(seen)):
        problems.append("a torus has two records")
    mine = {k: v for k, v in code_hashes().items() if k in ("study_py", "tests_py")}
    for r in rows:
        if r.get("job") == "torus" and r.get("s3c_sha256") != mine:
            problems.append(f"{r['l']}x{r['m']}: another stage 3c code")
    if problems:
        out["problems"] += problems
        out["H"] = out["verdict"] = "fail"
    return out | {"records": {"stage3b": len(combined) - len(rows), "stage3c": len(rows)}}


STUDY = Study(
    directory=HERE, question=question, predictions=predictions, execute=execute, decide=decide
)

if __name__ == "__main__":
    main(STUDY)
