"""
Step 2b: how often do two rules of a family share their class logs mod 27 (the relatives' event)?

From code27.npy (sweep.py): for every rule, its 11 class logs mod 27 in base 28 (27 = zero).
  full : all 11 classes equal mod 27 (the triple 10491524, 20982139, 178279803 is such a cluster)
  gen  : the eight generic classes equal mod 27
Counts the colliding pairs inside each family (r4, r5n, r6n) and compares with independence:
  full: E = C(N, 2) prod_c q_c,  q_c = sum_s P_c(s)^2 (class marginals of the family)
  gen : split by the mod-9 cell of the cluster; E = sum_cells C(O_cell, 2) prod_d q_d(gamma_d) with
        q_d(g) = sum_{s = g mod 9} P_d(s)^2 / P_d(g)^2 (the chance that two rules already in the same
        index-9 coset also agree mod 27), O_cell from h9_hist.npz [h9all_<fam>].
Writes pairs.json and clusters.npz (every full-pattern cluster: code and ids). Deletes nothing.
"""
from __future__ import annotations

import json
import math
import time

import numpy as np

HERE = "/home/user/lattice-lab/examples/rule-4850/deep/calibration"
GEN = [2, 3, 4, 5, 7, 8, 9, 10]
FAMS = {"r4": (1, 1 << 15), "r5n": (1 << 15, 1 << 21), "r6n": (1 << 21, 1 << 28)}
NBUCK = 8
MULT = np.uint64(0x9E3779B97F4A7C15)


def digits_of(code: np.ndarray, classes) -> np.ndarray:
    return np.stack([(code // 28**c) % 28 for c in classes])


def clusters_in(codes: np.ndarray, ids: np.ndarray):
    """(codes, list of id arrays) for every value occurring at least twice."""
    order = np.argsort(codes, kind="stable")
    c = codes[order]
    i = ids[order]
    starts = np.flatnonzero(np.r_[True, c[1:] != c[:-1]])
    lens = np.diff(np.r_[starts, len(c)])
    big = np.flatnonzero(lens >= 2)
    return c[starts[big]], [i[starts[b]: starts[b] + lens[b]] for b in big], lens


def scan(path, label, keep_clusters):
    mm = np.load(path, mmap_mode="r")
    out = {}
    allc = {f: [] for f in FAMS}
    for f, (lo, hi) in FAMS.items():
        pairs = 0
        sizes = {}
        for b in range(NBUCK):
            codes_b, ids_b = [], []
            step = 1 << 24
            for s in range(lo, hi, step):
                e = min(hi, s + step)
                c = np.asarray(mm[s:e])
                h = (c.astype(np.uint64) * MULT) >> np.uint64(61)
                sel = np.flatnonzero(h == b)
                codes_b.append(c[sel])
                ids_b.append(sel.astype(np.int64) + s)
            codes_b = np.concatenate(codes_b)
            ids_b = np.concatenate(ids_b)
            cc, groups, lens = clusters_in(codes_b, ids_b)
            for L in lens[lens >= 2]:
                sizes[int(L)] = sizes.get(int(L), 0) + 1
                pairs += int(L) * (int(L) - 1) // 2
            if keep_clusters:
                allc[f] += list(zip(cc.tolist(), groups))
        out[f] = {"pairs": pairs, "cluster_sizes": dict(sorted(sizes.items()))}
        print(label, f, out[f], flush=True)
    return out, allc


def main():
    t0 = time.time()
    S = np.load(f"{HERE}/sweep_stats.npz")
    res = {}
    # gen27.npy: the eight generic classes' symbols, base 28
    gpath = f"{HERE}/gen27.npy"
    mm = np.load(f"{HERE}/code27.npy", mmap_mode="r")
    g = np.lib.format.open_memmap(gpath, mode="w+", dtype=np.int64, shape=mm.shape)
    pw = (28 ** np.arange(8)).astype(np.int64)
    for s in range(0, len(mm), 1 << 24):
        c = np.asarray(mm[s: s + (1 << 24)])
        g[s: s + (1 << 24)] = pw @ digits_of(c, GEN)
    g.flush()
    del g
    print("gen codes", round(time.time() - t0, 1), flush=True)
    full, fullc = scan(f"{HERE}/code27.npy", "full", True)
    gen, genc = scan(gpath, "gen", True)
    # expectations
    for f, (lo, hi) in FAMS.items():
        N = hi - lo
        marg = S[f"marg_{f}"].astype(np.float64)
        P = marg / marg.sum(axis=1, keepdims=True)
        q = (P**2).sum(axis=1)
        Efull = N * (N - 1) / 2 * np.prod(q)
        # gen collisions by the cluster's mod-9 cell type
        h = np.load(f"{HERE}/h9_hist.npz")[f"h9all_{f}"].astype(np.float64)
        Pg = P[GEN]  # (8, 28)
        res9 = np.zeros((8, 9))
        qq = np.zeros((8, 9))
        for d in range(8):
            for r in range(9):
                syms = [s for s in range(27) if s % 9 == r] + ([27] if r == 0 else [])
                pr = Pg[d, syms]
                res9[d, r] = pr.sum()
                qq[d, r] = (pr**2).sum() / pr.sum() ** 2 if pr.sum() else 0
        # expected gen collisions per cell = C(O,2) prod_d qq[d, r_d]
        idx = np.arange(9**8)
        logq = np.zeros(9**8)
        allzero = np.ones(9**8, dtype=bool)
        allcube = np.ones(9**8, dtype=bool)
        noncube = np.ones(9**8, dtype=bool)
        for d in range(8):
            dd = (idx // 9**d) % 9
            logq += np.log(qq[d][dd])
            allzero &= dd == 0
            allcube &= dd % 3 == 0
            noncube &= dd % 3 != 0
            del dd
        del idx
        pairs_cell = h * (h - 1) / 2
        types = {"zero": allzero, "cube_nonzero": allcube & ~allzero, "noncube": noncube}
        types["mixed"] = ~(allzero | allcube | noncube)
        Egen = {k: float((pairs_cell[v] * np.exp(logq[v])).sum()) for k, v in types.items()}
        Pairs_in_cells = {k: float(pairs_cell[v].sum()) for k, v in types.items()}
        # observed gen collisions by type
        obs_gen = {k: 0 for k in types}
        for code, ids in genc[f]:
            ds = [(code // 28**d) % 28 for d in range(8)]
            r = [0 if s == 27 else s % 9 for s in ds]
            key = (sum(r[d] * 9**d for d in range(8)))
            for k, v in types.items():
                if v[key]:
                    obs_gen[k] += len(ids) * (len(ids) - 1) // 2
        res[f] = {"N": N, "full_pairs_obs": full[f]["pairs"], "full_pairs_exp": float(Efull),
                  "full_cluster_sizes": full[f]["cluster_sizes"], "gen_pairs_obs_by_cell": obs_gen,
                  "gen_pairs_exp_by_cell": Egen, "pairs_sharing_a_mod9_cell": Pairs_in_cells,
                  "gen_cluster_sizes": gen[f]["cluster_sizes"]}
        print(f, json.dumps(res[f]), flush=True)
    # store the full-pattern clusters
    flat = []
    for f in FAMS:
        for code, ids in fullc[f]:
            flat.append((f, code, ids))
    np.savez_compressed(f"{HERE}/clusters.npz",
                        fam=np.array([x[0] for x in flat]), code=np.array([x[1] for x in flat], dtype=np.int64),
                        ids=np.array([",".join(map(str, x[2].tolist())) for x in flat]))
    json.dump(res, open(f"{HERE}/pairs.json", "w"), indent=1)
    print("done", round(time.time() - t0, 1))


if __name__ == "__main__":
    main()
