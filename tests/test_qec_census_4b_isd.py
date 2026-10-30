"""Census stage 4b's ISD instrument (examples/qec-census-4b/isd.py and isd.c): the model, the
budget, a certify that must and must not pass, and the watch count on [[72,12,6]]."""

import importlib.util
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ISD_PY = ROOT / "examples" / "qec-census-4b" / "isd.py"
spec = importlib.util.spec_from_file_location("qec_census_4b_isd", ISD_PY)
ISD = importlib.util.module_from_spec(spec)
sys.modules["qec_census_4b_isd"] = ISD
spec.loader.exec_module(ISD)

A72, B72 = [(3, 0), (0, 1), (0, 2)], [(0, 3), (1, 0), (2, 0)]
W72 = [0, 5, 4, 1, 21, 23]


def test_model():
    # hypergeometric probabilities of meeting I in 1 or 2 positions; a check by direct sum
    n, K, w = 40, 20, 6
    direct = sum(math.comb(w, j) * math.comb(n - w, K - j) for j in (1, 2)) / math.comb(n, K)
    assert abs(ISD.p_seen(n, K, w) - direct) < 1e-15
    assert ISD.p_seen(300, 152, 20) > ISD.p_seen(300, 152, 24)
    assert ISD.budget(300, 152, 22, 1e-6) < ISD.budget(300, 152, 22, 1e-9)


def test_certify_on_a_known_code():
    assert ISD.certify(A72, B72, 6, 6, 6, 1e-6)["status"] == "probable"  # nothing below 6
    r = ISD.certify(A72, B72, 6, 6, 8, 1e-6)  # a false claim: d is 6, not 8
    assert r["status"] == "lighter" and r["upper"] == 6


def test_watch_counts_meetings():
    r = ISD.calibrate(A72, B72, 6, 6, W72, 4000, seed=3)
    assert r["meet1"] + r["meet2"] > 0 and 0.5 < r["ratio"] < 1.5
