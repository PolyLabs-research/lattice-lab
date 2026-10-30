"""The model check behind PLAN.md: for each spot-check code (known d and witness), how often its
witness meets isd.c's information set in 1 or 2 positions, against isd.p_seen. Output: one JSON
line per code (spotcheck-codes.jsonl was made with this, 4 workers, seed 1)."""

import importlib.util
import json
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
s = importlib.util.spec_from_file_location("isd", ROOT / "examples/qec-census-4b/isd.py")
ISD = importlib.util.module_from_spec(s)
sys.modules["isd"] = ISD
s.loader.exec_module(ISD)
recs = [json.loads(x) for x in open(ROOT / "examples/qec-census-3b/spotcheck/records.jsonl")]
codes = {}
for r in recs:
    c = r["code"]
    codes[(tuple(c["torus"]), str(c["A"]), str(c["B"]))] = c


def one(c):
    A = [tuple(t) for t in c["A"]]
    B = [tuple(t) for t in c["B"]]
    it = 200000 if c["n"] <= 150 else 60000
    out = ISD.calibrate(A, B, *c["torus"], c["witness"], it, seed=1)
    keys = ("iterations", "meet1", "meet2", "measured", "model", "ratio", "seconds")
    return {"torus": c["torus"], "n": c["n"], "k": c["k"], "d": c["d"], **{k: out[k] for k in keys}}


if __name__ == "__main__":
    with ProcessPoolExecutor(4) as p:
        for r in p.map(one, sorted(codes.values(), key=lambda c: c["n"])):
            print(json.dumps(r), flush=True)
