"""The spot-check's SAT encoding (examples/qec-census-3b/spotcheck/sat.py) against exhaustive
enumeration on small stage-1 codes: UNSAT with a drat-trim-verified proof below d, SAT at d with
the model a verified logical. Skipped when CaDiCaL and drat-trim are not built."""

import importlib.util
import random
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "examples" / "qec-bb"))
sys.path.insert(0, str(ROOT / "examples" / "qec-distance"))

import bb  # noqa: E402
import distance as D  # noqa: E402

SAT_PY = ROOT / "examples" / "qec-census-3b" / "spotcheck" / "sat.py"
spec = importlib.util.spec_from_file_location("spotcheck_sat", SAT_PY)
SAT = importlib.util.module_from_spec(spec)
spec.loader.exec_module(SAT)

pytestmark = pytest.mark.skipif(not (SAT.CADICAL.exists() and SAT.DRAT_TRIM.exists()),
                                reason="CaDiCaL and drat-trim not built")  # fmt: skip


def _codes(count, seed):
    rng, out = random.Random(seed), []
    while len(out) < count:
        ell, m = rng.choice([(3, 4), (3, 6), (3, 7), (4, 6), (2, 9), (3, 8)])
        A = sorted({(rng.randrange(ell), rng.randrange(m)) for _ in range(3)})
        B = sorted({(rng.randrange(ell), rng.randrange(m)) for _ in range(3)})
        if len(A) < 3 or len(B) < 3:
            continue
        k = bb.k_linalg(A, B, ell, m)
        if k and ell * m + k // 2 <= D.BRUTE_CAP:
            out.append((A, B, ell, m))
    return out


@pytest.mark.parametrize("A,B,ell,m", _codes(12, 41))
def test_encoding_against_enumeration(A, B, ell, m):
    n = 2 * ell * m
    hx, hz = D._bit_rows(A, B, ell, m)
    logicals = D._logicals_bits(hz, hx, n)  # X-logicals
    d = D.distance_brute(A, B, ell, m, "Z")["d"]
    for anchors in (None, (0, ell * m)):
        below = SAT.certify(hx, logicals, n, d - 1, anchors, limit=300)
        assert below["status"] == "verified"
        at = SAT.certify(hx, logicals, n, d, anchors, limit=300)
        assert at["status"] == "sat" and len(at["support"]) <= d
        assert D.verify_witness(A, B, ell, m, "Z", at["support"])["logical"]
        assert len(at["support"]) == d


def test_a_wrong_claim_is_not_certified():
    # weight d is satisfiable, so the solver must not return UNSAT there
    A, B = [(3, 0), (0, 1), (0, 2)], [(0, 3), (1, 0), (2, 0)]  # gross code, d = 12
    n = 144
    hx, hz = D._bit_rows(A, B, 12, 6)
    logicals = D._logicals_bits(hz, hx, n)
    r = SAT.certify(hx, logicals, n, 12, (0, 72), limit=600)
    assert r["status"] == "sat"
    assert D.verify_witness(A, B, 12, 6, "Z", r["support"])["logical"]
