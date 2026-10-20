"""Step 3: the obstruction digits of cube- and ninth-power-confined rules in the Legendre basis.

For every zero-free symmetric rule of radius <= 5 at 37 (relations/L5.npy: logs mod 513 at the 11
census classes, f18 generator; any generator gives the same weights) and every radius-6 ninth-power
hit (examples/llm-pilot-37c/records.jsonl, logs mod 27):
  cube-confined  -> digit1 = L/3 mod 3, its coordinates eps1 in the basis S_O (sbasis.py), weight
  ninth-confined -> digit2 = L/9 mod 3, eps2, weight
Explained status: atlas3.predict (mechanisms 1-4) and the seventh pilot's condition (5-8), at the
cube level (3 | q) and at the ninth level (9 | q).
Writes step3_census.json and prints weight distributions against the uniform baseline
Binomial(10, 2/3).
"""
import json
import math
import sys
import time
from collections import Counter

import numpy as np

import sbasis

sys.path.insert(0, "/home/user/pilot-37c-round2")
sys.path.insert(0, "/home/user/pilot-37c-round2/tools")
import mechanism  # noqa: E402
import census37 as C  # noqa: E402

sys.path.insert(0, "/home/user/lattice-lab/examples/linear-atlas-3")
import atlas3  # noqa: E402

S = sbasis.S_matrix()
P = sbasis.inverse_map(S)
R18 = 2**18 + 1


def eps_of(d):
    d = np.asarray(d) % 3
    assert d[6] == 0
    e = (d @ P) % 3
    assert np.array_equal((e @ S) % 3, d), "inconsistent digit vector"
    return e


def weight(e):
    return int(np.count_nonzero(e))


def status(n, r):
    f = C.rule(n, r)
    q_atlas, why = atlas3.predict(frozenset(f), 37)
    try:
        q_p = mechanism.condition(f, 37)
    except Exception as ex:  # noqa: BLE001
        q_p = -1
    cube_atlas = q_atlas is not None and (2**36 - 1) // 3 % q_atlas == 0 if q_atlas else False
    nine_atlas = q_atlas is not None and (2**36 - 1) // 9 % q_atlas == 0 if q_atlas else False
    cube_p = q_p > 0 and q_p % 3 == 0
    nine_p = q_p > 0 and q_p % 9 == 0
    return dict(atlas=[q_atlas, why], pilot=q_p, cube_explained=bool(cube_atlas or cube_p),
                nine_explained=bool(nine_atlas or nine_p))


def binom_baseline(n=10, p=2 / 3):
    return [math.comb(n, k) * p**k * (1 - p) ** (n - k) for k in range(n + 1)]


if __name__ == "__main__":
    t0 = time.time()
    L = np.asarray(np.load("/home/user/lattice-lab/examples/rule-4850/deep/relations/L5.npy"))
    zf = (L >= 0).all(axis=0)
    cube = zf & np.all(L % 3 == 0, axis=0)
    nine = zf & np.all(L % 9 == 0, axis=0)
    cube[0] = nine[0] = False
    ids_cube = np.flatnonzero(cube)
    out = {"cube": [], "nine": [], "nine_r6": []}
    for n in ids_cube:
        n = int(n)
        r = 4 if n < 1 << 15 else 5
        lg = L[:, n].astype(np.int64)
        d1 = (lg // 3) % 3
        e1 = eps_of(d1)
        rec = dict(id=n, radius=r, logs513=lg.tolist(), digit1=d1.tolist(), eps1=e1.tolist(), w1=weight(e1))
        if nine[n]:
            d2 = (lg // 9) % 3
            e2 = eps_of(d2)
            rec.update(digit2=d2.tolist(), eps2=e2.tolist(), w2=weight(e2))
        rec.update(status(n, r))
        out["cube"].append(rec)
    print("radius <= 5 zero-free cube-confined:", len(out["cube"]), round(time.time() - t0, 1), "s", flush=True)
    # radius-6 ninth-power hits (logs mod 27; None = zero)
    for line in open("/home/user/lattice-lab/examples/llm-pilot-37c/records.jsonl"):
        rr = json.loads(line)
        if "logs" not in rr:
            continue
        lg = rr["logs"]
        if any(x is None or x == 255 for x in lg):
            continue
        lg = np.array(lg, dtype=np.int64)
        d2 = (lg // 9) % 3
        e2 = eps_of(d2)
        out["nine_r6"].append(dict(id=rr["id"], explained=rr["explained"], procedure=rr.get("procedure"),
                                   logs27=lg.tolist(), digit2=d2.tolist(), eps2=e2.tolist(), w2=weight(e2)))
    # summaries
    base = binom_baseline()
    summ = {}
    c = out["cube"]
    for label, sel in (("cube explained", [x for x in c if x["cube_explained"]]),
                       ("cube unexplained", [x for x in c if not x["cube_explained"]])):
        h = Counter(x["w1"] for x in sel)
        summ[label + " digit1 weight"] = {k: h[k] for k in sorted(h)}
        print(label, len(sel), "digit1 weights:", dict(sorted(h.items())))
    n9 = [x for x in c if "w2" in x]
    for label, sel in (("nine explained", [x for x in n9 if x["nine_explained"]]),
                       ("nine unexplained", [x for x in n9 if not x["nine_explained"]])):
        h = Counter(x["w2"] for x in sel)
        summ[label + " (r<=5) digit2 weight"] = {k: h[k] for k in sorted(h)}
        print(label, "(r<=5)", len(sel), "digit2 weights:", dict(sorted(h.items())),
              [(x["id"], x["w2"]) for x in sel] if label.startswith("nine unex") else "")
    for label, sel in (("r6 explained", [x for x in out["nine_r6"] if x["explained"]]),
                       ("r6 unexplained", [x for x in out["nine_r6"] if not x["explained"]])):
        h = Counter(x["w2"] for x in sel)
        summ[label + " digit2 weight"] = {k: h[k] for k in sorted(h)}
        print(label, len(sel), "digit2 weights:", dict(sorted(h.items())),
              [(x["id"], x["w2"]) for x in sel] if "unex" in label else "")
    summ["uniform baseline P(weight=k)"] = [round(b, 4) for b in base]
    print("uniform baseline Binomial(10,2/3):", [round(b, 3) for b in base])
    out["summary"] = summ
    json.dump(out, open("step3_census.json", "w"), indent=0, default=int)
    print("done", round(time.time() - t0, 1), "s")
