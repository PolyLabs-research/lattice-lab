"""
Step 4d: are the ratios of the relatives "units times F(2^9)-valued"?

Line-log vectors (log mod 513 = log modulo F(2^9)*, at the 38 lines (1,k), (0,1)) of
  * targets: w2 = R2/R1, w3 = R3/R1, Z = R3 R1^7 / R2^8, and 4850 / R1 themselves;
  * units: for each of the 11 D4-classes W of directions, T_W(c) = sum_{w in W} log t_(w.c)
    (0 where w.c = 0): the log of the symmetric orbit product of Psi_e(t_w) is E * T_W with
    E = A_e / 2, and E is arbitrary mod 513 (A_5 = 2^23 - 1 is a unit mod 513).
Solve target = sum_{W in S} E_W T_W (mod 513) for all S with |S| <= 4 (mod 27 and mod 19
separately, then CRT), and record the rank of all T_W (vacuity).  Also the same restricted to
the 36 off-axis lines.  Writes ratio_units.json.
"""
import itertools
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gr  # noqa: E402

sys.path.insert(0, "/home/user/pilot-37c-round2/scratch")
import f18  # noqa: E402

M = 37
N18 = 2**18 - 1
LINES = [(1, k) for k in range(M)] + [(0, 1)]


def line_logs(f):
    return [f18.log(gr.eig(f, *jk)) for jk in LINES]


def dir_classes():
    seen, out = set(), []
    for w in [(1, k) for k in range(M)] + [(0, 1)]:
        orb = set()
        for p, q in (w, (w[1], w[0])):
            for sp in (1, -1):
                for sq in (1, -1):
                    v = ((sp * p) % M, (sq * q) % M)
                    # normalise to a projective representative
                    if v[0]:
                        inv = pow(v[0], -1, M)
                        v = (1, v[1] * inv % M)
                    else:
                        v = (0, 1)
                    orb.add(v)
        key = frozenset(orb)
        if key in seen:
            continue
        seen.add(key)
        # the orbit of actual vectors (with signs), as used in the product
        vecs = set()
        for p, q in (w, (w[1], w[0])):
            for sp in (1, -1):
                for sq in (1, -1):
                    vecs.add(((sp * p) % M, (sq * q) % M))
        out.append(sorted(vecs))
    return out


def T_vec(vecs):
    lt1 = f18.log(f18.t(1))
    out = []
    for (j, k) in LINES:
        s = 0
        for (p, q) in vecs:
            d = (p * j + q * k) % M
            if d:
                s += lt1 * pow(2, f18.log2(d), N18)
        out.append(s % N18)
    return np.array(out, dtype=np.int64)


def solve_mod_prime_power(A, b, p, k):
    """Is b in the column span of A over Z/p^k?  Hermite-style elimination (small sizes)."""
    mod = p**k
    A = [list(map(int, row)) for row in A]
    b = list(map(int, b))
    rows, cols = len(A), len(A[0]) if A else 0
    # augmented, column elimination over Z/p^k: brute force for <= 4 columns
    import itertools as it
    if cols == 0:
        return all(x % mod == 0 for x in b)
    # brute force over coefficients is 513^4 too big; do mod p^k with Smith-like reduction:
    M_ = np.array(A, dtype=object) % mod
    bb = np.array(b, dtype=object) % mod
    # iterate: find pivot with minimal valuation
    used_rows = []
    Mw = M_.copy()
    bw = bb.copy()
    r = 0
    for c in range(cols):
        # pivot: entry in column c (rows >= r) with least p-adic valuation
        best, bi = None, None
        for i in range(r, rows):
            x = int(Mw[i, c]) % mod
            if x == 0:
                continue
            v = 0
            while x % p == 0:
                x //= p
                v += 1
            if best is None or v < best:
                best, bi = v, i
        if bi is None:
            continue
        Mw[[r, bi]] = Mw[[bi, r]]
        bw[[r, bi]] = bw[[bi, r]]
        piv = int(Mw[r, c]) % mod
        v = 0
        u = piv
        while u % p == 0:
            u //= p
            v += 1
        uinv = pow(u, -1, mod)
        for i in range(rows):
            if i == r:
                continue
            x = int(Mw[i, c]) % mod
            if x == 0:
                continue
            # x has valuation >= v; eliminate
            fac = (x // (p**v)) * uinv % mod
            Mw[i] = (Mw[i] - fac * Mw[r]) % mod
            bw[i] = (bw[i] - fac * bw[r]) % mod
        r += 1
    # now rows >= r of Mw are zero; consistency needs bw[i] == 0 for those, and for pivot rows
    # with valuation v, bw[i] divisible by p^v
    for i in range(r, rows):
        if int(bw[i]) % mod:
            return False
    for i in range(r):
        row = Mw[i]
        nz = [int(x) % mod for x in row if int(x) % mod]
        if not nz:
            continue
        vmin = min(_val(x, p) for x in nz)
        if _val(int(bw[i]) % mod, p, k) < vmin:
            return False
    return True


def _val(x, p, cap=99):
    if x == 0:
        return cap
    v = 0
    while x % p == 0:
        x //= p
        v += 1
    return v


def in_span(cols, b, lines_idx):
    A = np.stack([c[lines_idx] for c in cols], axis=1) if cols else np.zeros((len(lines_idx), 0), dtype=np.int64)
    bb = b[lines_idx]
    return (solve_mod_prime_power(A, bb % 27, 3, 3) and solve_mod_prime_power(A, bb % 19, 19, 1))


def rank_mod(cols, p, idx):
    A = np.stack([c[idx] % p for c in cols], axis=1).astype(np.int64)
    # rank over F_p
    A = A.copy() % p
    r = 0
    rows, ncols = A.shape
    for c in range(ncols):
        piv = next((i for i in range(r, rows) if A[i, c] % p), None)
        if piv is None:
            continue
        A[[r, piv]] = A[[piv, r]]
        inv = pow(int(A[r, c]), -1, p)
        A[r] = A[r] * inv % p
        for i in range(rows):
            if i != r and A[i, c]:
                A[i] = (A[i] - A[i, c] * A[r]) % p
        r += 1
    return r


def main():
    out = {}
    f18.full_log_table()
    L = {n: np.array(line_logs(gr.rule_array(n)), dtype=np.int64) for n in (4850, 10491524, 20982139, 178279803)}
    targets = {
        "w2=R2/R1": (L[20982139] - L[10491524]) % N18,
        "w3=R3/R1": (L[178279803] - L[10491524]) % N18,
        "Z=R3 R1^7/R2^8": (L[178279803] + 7 * L[10491524] - 8 * L[20982139]) % N18,
        "R1": L[10491524],
        "4850": L[4850],
    }
    D = dir_classes()
    T = [T_vec(v) for v in D]
    out["direction_classes"] = [v[0] for v in D]
    all_idx = np.arange(38)
    off_idx = np.array([i for i, jk in enumerate(LINES) if jk not in ((1, 0), (0, 1))])
    out["rank_T_mod19_all"] = rank_mod(T, 19, all_idx)
    out["rank_T_mod3_all"] = rank_mod(T, 3, all_idx)
    # dimension of the space of D4-symmetric mod-19 line functions: rank of the targets' ambient
    print("11 direction classes; rank of the T_W mod 19:", out["rank_T_mod19_all"], "mod 3:", out["rank_T_mod3_all"])
    for name, b in targets.items():
        for label, idx in (("all", all_idx), ("offaxis", off_idx)):
            sols = []
            for size in range(0, 5):
                for S in itertools.combinations(range(len(T)), size):
                    if in_span([T[i] for i in S], b, idx):
                        sols.append([D[i][0] for i in S])
                if sols:
                    break
            out[f"{name}|{label}"] = sols[:10]
            print(f"{name:18s} {label:8s} smallest unit sets (<= 4 direction classes):", sols[:6] if sols else "none")
            # mod 19 only and mod 27 only
            for p, k, tag in ((19, 1, "mod19"), (3, 3, "mod27")):
                found = None
                for size in range(0, 5):
                    for S in itertools.combinations(range(len(T)), size):
                        A = np.stack([T[i][idx] for i in S], axis=1) if S else np.zeros((len(idx), 0), dtype=np.int64)
                        if solve_mod_prime_power(A, b[idx] % (p**k), p, k):
                            found = (size, [D[i][0] for i in S])
                            break
                    if found:
                        break
                out[f"{name}|{label}|{tag}"] = found
                print(f"   {tag}: smallest", found)
    with open(os.path.join(gr.HERE, "ratio_units.json"), "w") as fh:
        json.dump(out, fh, indent=1, default=str)


if __name__ == "__main__":
    main()
