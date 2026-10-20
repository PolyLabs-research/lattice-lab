"""
Which confined rules do the known mechanisms explain?  For every ninth-power rule of r4, r5n, r6n
(all 125) and for every cube rule of r4 and r5n plus a random sample of r6n cube rules, run
  - atlas3.predict (mechanisms 1-4): explained if it splits or predicts an odd part dividing the target
  - pilot 7's condition (/home/user/pilot-37c-round2/mechanism.py, mechanisms 5-8): q divisible by 9
    (ninth) or 3 (cube); q includes the factor 2^18 + 1, which is prime to 3.
Writes condition.jsonl (one row per rule).   python run_condition.py [sample_size]
"""
from __future__ import annotations

import json
import signal
import sys
import time

import numpy as np

sys.path[:0] = ["/home/user/pilot-37c-round2", "/home/user/lattice-lab/examples/rule-4850",
                "/home/user/lattice-lab/examples/linear-atlas-3"]
import atlas3  # noqa: E402
import census  # noqa: E402
import mechanism  # noqa: E402

HERE = "/home/user/lattice-lab/examples/rule-4850/deep/calibration"
N18 = 2**18 - 1


class Timeout(Exception):
    pass


def _alarm(*_):
    raise Timeout


def fam(i):
    return "r4" if i < 1 << 15 else ("r5n" if i < 1 << 21 else "r6n")


def main():
    sample = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    C = np.load(f"{HERE}/cubes.npz")
    ids, logs = C["ids"], C["logs"]
    z = logs == census.ZERO
    nine = np.all(z | (logs % 9 == 0), axis=1)
    rng = np.random.default_rng(4850)
    r6cube = np.flatnonzero((ids >= 1 << 21) & ~nine)
    pick = set(np.flatnonzero(nine)) | set(np.flatnonzero(ids < 1 << 21)) | set(rng.choice(r6cube, sample, replace=False))
    signal.signal(signal.SIGALRM, _alarm)
    out = open(f"{HERE}/condition.jsonl", "w")
    t0 = time.time()
    for n, k in enumerate(sorted(pick, key=lambda k: (not nine[k], ids[k]))):
        rid = int(ids[k])
        f = census.rule(rid, 6)
        q9 = bool(nine[k])
        target = N18 // 9 if q9 else N18 // 3
        row = {"id": rid, "family": fam(rid), "ninth": q9, "logs": [int(v) for v in logs[k]]}
        signal.alarm(60)
        try:
            odd, why = atlas3.predict(f, 37)
            row["atlas"] = why
            row["atlas_explains"] = bool("splits" in why or (odd is not None and target % odd == 0))
        except Timeout:
            row["atlas"] = "timeout"
            row["atlas_explains"] = False
        signal.alarm(0)
        signal.alarm(60)
        try:
            q = mechanism.condition(f, 37)
            row["q"] = int(q)
            row["cond_explains"] = bool(q % (9 if q9 else 3) == 0)
        except Timeout:
            row["q"] = None
            row["cond_explains"] = False
        signal.alarm(0)
        row["explained"] = row["atlas_explains"] or row["cond_explains"]
        out.write(json.dumps(row) + "\n")
        out.flush()
        if n % 200 == 0:
            print(n, len(pick), round(time.time() - t0, 1), flush=True)
    print("done", len(pick), round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
