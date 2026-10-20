"""
Step 6: is 4850 (or its rotation R1) a GL2(Z/37)-transport of a rule whose confinement is known,
times rule-90 units, times something F(2^9)-valued?

    target = (g E)^c * t(x)^e1 * t(y)^e2 * B     (B F(2^9)-valued, c, e1, e2 any; off the axis lines)

for E in every recorded ninth-confined rule (radius 4-6) that has no zero eigenvalue off the axes,
g in PGL2(Z/37) (the scalar part is a Frobenius power and is absorbed in c), targets R1 = 10491524
(frame of the relatives' identities) and 4850 (its own frame).  The log of gE at the line rep c is
2^(log n) L_E(c') with g^T c = n c'.  Test mod 19 (rank of {gE, t(x), t(y)} + target) and, for the
hits, mod 27, then verify in the group ring.  The 4850 family itself (4850, 10491524, 20982139,
178279803, 482758, 8438150, 43250486) is reported separately (expected hits).
Writes transport_search.json.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

sys.path.insert(0, "/home/user/pilot-37c-round2/scratch")
import f18  # noqa: E402

M = 37
N18 = 2**18 - 1
LINES = [(1, k) for k in range(M)] + [(0, 1)]
AXIS = {(1, 0), (0, 1)}
FAMILY = {4850, 10491524, 20982139, 178279803, 482758, 8438150, 43250486}


def log2(n):
    x = 1
    for e in range(36):
        if x == n % M:
            return e
        x = 2 * x % M
    raise ValueError


def line_idx(v):
    a, b = v[0] % M, v[1] % M
    if a == 0:
        return 37, b
    return (b * pow(a, -1, M)) % M, a


def pgl2():
    reps = []
    seen = set()
    for g in gr.gl2():
        p, q, r, s = (int(x) for x in g)
        inv = pow(next(v for v in (p, q, r, s) if v), -1, M)
        key = tuple(v * inv % M for v in (p, q, r, s))
        if key not in seen:
            seen.add(key)
            reps.append(key)
    return np.array(reps, dtype=np.int64)


def perm_tables(G):
    """for each g: (index array (38,), frob exponent array (38,)): (gE)(c_i) = 2^f * E(c_idx)."""
    idx = np.zeros((len(G), 38), dtype=np.int64)
    fro = np.zeros((len(G), 38), dtype=np.int64)
    for li, (j, k) in enumerate(LINES):
        # g^T c
        x = (G[:, 0] * j + G[:, 2] * k) % M
        y = (G[:, 1] * j + G[:, 3] * k) % M
        for t in range(len(G)):
            pass
        # vectorised line index and scalar
        a0 = x == 0
        inv = np.array([pow(int(v), -1, M) if v else 0 for v in range(M)])
        kk = np.where(a0, 37, (y * inv[x]) % M)
        n = np.where(a0, y, x)
        lg = np.array([log2(v) if v else 0 for v in range(M)])
        idx[:, li] = kk
        fro[:, li] = lg[n]
    return idx, fro


def nullspace_mod(A, p):
    """rows spanning the left nullspace complement: H with H @ A = 0 (mod p), A (n, k)."""
    n, k = A.shape
    # solve for vectors h with h A = 0: nullspace of A^T
    At = (A.T % p).copy()
    # row reduce At (k x n)
    R = At.copy()
    piv = []
    r = 0
    for c in range(n):
        pr = next((i for i in range(r, k) if R[i, c] % p), None)
        if pr is None:
            continue
        R[[r, pr]] = R[[pr, r]]
        R[r] = R[r] * pow(int(R[r, c]), -1, p) % p
        for i in range(k):
            if i != r and R[i, c]:
                R[i] = (R[i] - R[i, c] * R[r]) % p
        piv.append(c)
        r += 1
    free = [c for c in range(n) if c not in piv]
    H = []
    for f in free:
        h = np.zeros(n, dtype=np.int64)
        h[f] = 1
        for i, c in enumerate(piv):
            h[c] = (-R[i, f]) % p
        H.append(h)
    return np.array(H, dtype=np.int64)


def main():
    t0 = time.time()
    f18.full_log_table()
    out = {}
    G = pgl2()
    print("PGL2:", len(G))
    idx, fro = perm_tables(G)
    pow2_19 = np.array([pow(2, e, 19) for e in range(36)])
    tx = gr.from_points([(1, 0), (-1, 0)])
    ty = gr.from_points([(0, 1), (0, -1)])

    def L(f):
        v = []
        for jk in LINES:
            e = gr.eig(f, *jk)
            v.append(f18.log(e) if e else -1)
        return np.array(v, dtype=np.int64)

    Lx, Ly = L(tx), L(ty)
    rec = json.load(open(os.path.join(gr.HERE, "baselines.json")))["recorded"]
    cands = sorted({r["rule"] for r in rec if r["ninth_confined"]} | FAMILY)
    targets = {"R1": L(gr.rule_array(10491524)), "4850": L(gr.rule_array(4850))}
    off = np.array([i for i, jk in enumerate(LINES) if jk not in AXIS])
    results = {k: [] for k in targets}
    for tname, Lt in targets.items():
        # units t(x), t(y) in this frame vanish on the axis lines: off-axis only
        U = np.stack([Lx[off], Ly[off]], axis=1) % 19
        H = nullspace_mod(U, 19)  # (34, 36)
        Ht = H @ (Lt[off] % 19) % 19
        for n in cands:
            LE = L(gr.rule_array(n))
            # gE at off-axis lines: E at idx (must not be zero)
            gi = idx[:, off]
            vals = LE[gi]  # (|G|, 36)
            bad = (vals < 0).any(axis=1)
            v19 = (vals % 19) * pow2_19[fro[:, off]] % 19
            Hv = v19 @ H.T % 19  # (|G|, 34)
            # target in span{gE, units} mod 19 <=> Ht = c Hv for some c (or Ht = 0)
            ok = np.zeros(len(G), dtype=bool)
            nz = Hv.any(axis=1)
            # pick a coordinate where Hv != 0 to solve c, then check
            first = np.argmax(Hv != 0, axis=1)
            hv0 = Hv[np.arange(len(G)), first]
            inv19 = np.array([pow(int(v), -1, 19) if v else 0 for v in range(19)])
            c = Ht[first] * inv19[hv0] % 19
            ok = nz & ((c[:, None] * Hv - Ht[None, :]) % 19 == 0).all(axis=1) & ~bad
            hits = np.flatnonzero(ok)
            if len(hits):
                results[tname].append({"rule": n, "family": n in FAMILY, "hits": int(len(hits)),
                                       "first_g": G[hits[0]].tolist(), "c19": int(c[hits[0]])})
        fam = [r for r in results[tname] if r["family"]]
        nonfam = [r for r in results[tname] if not r["family"]]
        print(f"target {tname}: family hits {[(r['rule'], r['hits']) for r in fam]}")
        print(f"   NON-family rules E with target = (gE)^c t(x)^e1 t(y)^e2 B (mod 19, off-axis): {[(r['rule'], r['hits'], r['first_g']) for r in nonfam]}")
    out["results"] = results
    out["candidates"] = len(cands)
    print("candidates", len(cands), "time %.0fs" % (time.time() - t0))
    with open(os.path.join(gr.HERE, "transport_search.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
