"""
The ratios 20982139/10491524 and 178279803/10491524 (and 178279803/20982139) modulo F(2^9)*.

R = L(g) - L(10491524) mod 513 at the 11 classes. Questions:
  1. 27-part (R mod 27) and 19-part (R/27 mod 19), to confirm the dossier.
  2. Is gamma*R (gamma = 2^k: Frobenius twists, which at 37 are all dilations) the log vector of a
     rule M of the radius <= 6 family (268M rules), (a) mod 513 on the 10 free classes,
     (b) mod 513 on the 8 off-line classes, (c) its 19-part on the 10 free classes (any 27-part),
     (d) its 19-part with gamma any unit mod 19?
  3. Is R a symmetric unit product (units.py): the orbit lattice has full rank, so it always is;
     we report the minimal number of direction orbits needed (mod 19 and mod 171).
  4. Is R = gamma^-1 (delta L(M1) + L(M2)) with M1, M2 of radius <= 5 (search.py)?

    python ratio.py   -> ratio.json
"""
from __future__ import annotations

import itertools
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ext6  # noqa: E402
import run_targets as RT  # noqa: E402
import search as S  # noqa: E402
import tables  # noqa: E402
import units  # noqa: E402

FREE = S.MODES["all"]
OFF = S.MODES["off"]
P2 = [pow(2, k, 513) for k in range(18)]


def L(n):
    return tables.logs513(RT.expset(n)).astype(np.int64)


def min_unit_support(R, p):
    """minimal number of orbits k with sum n_k g_k = R/(3u) mod p (p = 19, or 9 via 171)."""
    G = np.load(os.path.join(HERE, "unit_G.npy"))[:, FREE] % 171
    lt = units.log_t1()
    u = (lt // 3) % 171
    target = (np.array(R)[FREE] // 3 * pow(int(u), -1, 171)) % 171  # R = 3u * (n G)
    tgt = target % p
    best = None
    for k in range(0, 12):
        for S_ in itertools.combinations(range(11), k):
            A = G[list(S_)] % p
            if solvable(A, tgt, p):
                best = (k, S_)
                break
        if best:
            break
    return best


def solvable(A, t, p):
    """is there x with x A = t mod p (p prime)?"""
    if A.shape[0] == 0:
        return not (t % p).any()
    r1 = units._rank_mod(A.T.tolist(), p)
    aug = np.hstack([A.T, t.reshape(-1, 1)])
    return r1 == units._rank_mod(aug.tolist(), p)


def hkey(V, mod):
    k = np.zeros(V.shape[1], dtype=np.uint64)
    for i in range(V.shape[0]):
        k = k * np.uint64(mod) + V[i].astype(np.uint64)  # wraps mod 2^64: a hash
    return k


def scan_family(targets):
    """targets: dict name -> list of (mode, vectors, modulus, classes). Scan radius <= 6."""
    tab = tables.log_table()
    c5 = ext6.coords5()
    c6 = ext6.coords6_extra()
    found = {name: [] for name in targets}
    for j in range(128):
        lg = tab[c5 ^ c6[:, j: j + 1]].astype(np.int64)  # full logs, -1 zero
        for name, specs in targets.items():
            for mode, vecs, mod, cls in specs:
                sub = lg[cls]
                okz = (sub >= 0).all(axis=0)
                red = sub % mod
                keys = hkey(red, mod)
                V = np.array(vecs).T  # (k, t)
                tk = hkey(V, mod)
                for i in np.flatnonzero(np.isin(keys, tk) & okz):
                    for k in range(V.shape[1]):
                        if (red[:, i] == V[:, k]).all():
                            found[name].append({"mode": mode, "twist": k,
                                                "rule": int(i + (j << 21))})
    return found


def main():
    out = {}
    base = L(10491524)
    gs = {"20982139": L(20982139), "178279803": L(178279803)}
    Rs = {f"{g}/10491524": (v - base) % 513 for g, v in gs.items()}
    Rs["178279803/20982139"] = (gs["178279803"] - gs["20982139"]) % 513
    targets = {}
    for name, R in Rs.items():
        r27 = (R % 27).tolist()
        r19 = ((R // 27) % 19).tolist()
        out[name] = {"R513": R.tolist(), "R mod 27": r27, "19-part (R/27 mod 19)": r19}
        print(name, out[name])
        # twists mod 513
        tw = [((P2[k] * R) % 513) for k in range(18)]
        specs = [("513 all", [t[FREE] for t in tw], 513, FREE),
                 ("513 off", [t[OFF] for t in tw], 513, OFF)]
        # 19-part: L(M) mod 513 = 27*(19-part) + (27-part); compare L(M)//27 mod 19 is wrong as
        # the CRT coordinate; use the 19-component: x -> x * 27^-1 mod 19 of (x mod 19)?
        # log mod 513 determines log mod 19 = (log mod 513) mod 19; R's "19-part" as defined in
        # the dossier is R/27 mod 19 (R is 0 mod 27). Compare log mod 19 instead:
        r19log = R % 19
        specs.append(("19 all, any unit", [((c * r19log) % 19)[FREE] for c in range(1, 19)], 19,
                      FREE))
        targets[name] = specs
        for p in (3, 19):
            out[name][f"min unit orbits mod {p}"] = min_unit_support(R, p)
            print("  min unit orbits mod", p, out[name][f"min unit orbits mod {p}"])
    found = scan_family(targets)
    for name in Rs:
        out[name]["family matches"] = found[name][:200]
        out[name]["family match count"] = len(found[name])
        print(name, "family matches:", len(found[name]), found[name][:20])
    # two-rule relations for the ratio vectors
    for name, R in Rs.items():
        for mode in ("all", "off"):
            hits = S.index(mode).search(R)
            out[name][f"two-rule hits ({mode})"] = hits[:100]
            print(name, mode, "two-rule hits:", len(hits), hits[:10])
    json.dump(out, open(os.path.join(HERE, "ratio.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
