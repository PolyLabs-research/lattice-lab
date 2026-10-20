"""3-adic engine for the hexagon family at any odd m with r^2 = -3 (mod m).

For c = (j, k) put alpha = (j+k)/2, beta = (j-k)/2 (so j = alpha + beta, k = alpha - beta).  For integers p, q with
q = +-r p (mod m), p a unit, the eigenvalues of f_{p,q} = (Hex_{p,q} + Hex_{p,q}^T)/s are (step 2, proof in the report)
   W_r(2p alpha, 2p beta) / (t_alpha t_beta)      (alpha beta != 0),   W_r(a, b) = sum_{v in <u^2>} t_{v a} t_{b / v},
   t_{pj} t_{qj} / t_j  or 0                      (alpha beta = 0;  p != q resp. p = q mod 2),
with u = (1 + r)/2, a primitive 6th root of unity mod m.  Everything below works with 3-adic logarithms
v(x) = log x mod 3^A in F(2^d)*, d = ord_m(2), A = v3(2^d - 1), so the whole family (all p) costs one table of
v(W) and one of v(t).

For a value x lying in the subfield F(2^e_c) of its class (e_c = |<2> x D4 orbit| / |D4 orbit|), a_c = v3(2^e_c - 1)
is the 3-exponent of a generic value; x has 3-exponent A - v3(v(x)) <= a_c.  The rule's 3-exponent is the max over
classes; 'level' = (max_c a_c) - (rule's 3-exponent), so level 1 = cube-confined, 2 = ninth-confined, ..."""
from __future__ import annotations

import math
import numpy as np
import sympy
import famlib as L


def v3arr(x, A):
    """elementwise 3-adic valuation of x mod 3^A (A for 0); x int array."""
    x = np.asarray(x) % 3 ** A
    out = np.zeros(x.shape, dtype=np.int64)
    y = x.copy()
    zero = y == 0
    out[zero] = A
    for i in range(1, A):
        mask = (~zero) & (y % 3 ** i == 0)
        out[mask] = i
    return out


class Size:
    def __init__(self, m: int):
        self.m = m
        self.F = F = L.GF(m)
        self.d, self.A = F.d, F.A
        two = {pow(2, i, m) for i in range(self.d)}
        self.minus1_in_2 = (m - 1) in two
        self.units = [x for x in range(1, m) if math.gcd(x, m) == 1]
        self.index2 = len(self.units) // self.d
        self.roots = L.sqrt_minus3(m)
        if not self.A:
            return
        A, Q = self.A, 3 ** self.A
        # v(t_j), via orbits j -> 2j (v doubles), t_{-j} = t_j
        vt = np.full(m, -1, dtype=np.int64)
        for j in range(1, m):
            if vt[j] >= 0:
                continue
            v = F.log3(F.t[j])
            x = j
            while vt[x] < 0:
                vt[x] = v
                vt[(-x) % m] = v
                x = 2 * x % m
                v = 2 * v % Q
        self.vt = vt
        # field degrees e_c and a_c on the (alpha, beta) grid.  D4 in these coordinates: (al,be)->(+-al,+-be),(+-be,+-al)
        self.a = self._acs()
        self.agen = int(self.a[1:, 1:].max())

    def _acs(self):
        m, d = self.m, self.d
        e = np.zeros((m, m), dtype=np.int64)
        seen = np.zeros((m, m), dtype=bool)
        for al in range(m):
            for be in range(m):
                if seen[al, be] or (al == 0 and be == 0):
                    continue
                d4 = {(s1 * x % m, s2 * y % m) for x, y in ((al, be), (be, al)) for s1 in (1, -1) for s2 in (1, -1)}
                orb = set()
                frontier = [(al, be)]
                while frontier:
                    c = frontier.pop()
                    if c in orb:
                        continue
                    orb.add(c)
                    x, y = c
                    for c2 in ((2 * x % m, 2 * y % m), (-x % m, y), (y, x)):
                        if c2 not in orb:
                            frontier.append(c2)
                ec = len(orb) // len(d4)
                for c in orb:
                    e[c] = ec
                    seen[c] = True
        cache = {}
        out = np.zeros_like(e)
        for x in np.unique(e):
            x = int(x)
            cache[x] = sympy.multiplicity(3, 2 ** x - 1) if x and (2 ** x - 1) % 3 == 0 else 0
            out[e == x] = cache[x]
        return out

    def W_table(self, r):
        """v(W_r(al, be)) on the grid (al, be != 0), -1 where W = 0."""
        m, F, A = self.m, self.F, self.A
        Q = 3 ** A
        h = pow(2, -1, m)
        u = (1 + r) * h % m
        assert pow(u, 3, m) == m - 1, (m, r, u)
        mu3 = [1, u * u % m, pow(u, 4, m)]
        mu3i = [pow(x, -1, m) for x in mu3]
        vW = np.full((m, m), -2, dtype=np.int64)
        t = F.t
        for al in range(1, m):
            for be in range(1, m):
                if vW[al, be] != -2:
                    continue
                w = 0
                for x, xi in zip(mu3, mu3i):
                    w ^= F.mul(t[x * al % m], t[be * xi % m])
                v = F.log3(w)
                # orbit: scalar doubling (v doubles), T_u, swap, signs (v fixed)
                stack = [((al, be), v)]
                while stack:
                    (x, y), vv = stack.pop()
                    if vW[x, y] != -2:
                        continue
                    vW[x, y] = -1 if vv is None else vv
                    v2 = None if vv is None else 2 * vv % Q
                    stack.append(((2 * x % m, 2 * y % m), v2))
                    for c2 in ((u * x % m, y * pow(u, -1, m) % m), (y, x), (-x % m, y), (x, -y % m)):
                        if vW[c2] == -2:
                            stack.append((c2, vv))
        return vW, u

    def family(self, r):
        """Per p (units up to sign): off-diagonal 3-exponent, per-class level stats, diagonal (opposite parity) exponent."""
        m, A = self.m, self.A
        Q = 3 ** A
        vW, u = self.W_table(r)
        vt = self.vt
        idx = np.arange(m)
        al = idx[:, None] * np.ones((1, m), dtype=np.int64)
        be = np.ones((m, 1), dtype=np.int64) * idx[None, :]
        off = (al > 0) & (be > 0)
        a = self.a
        res = {}
        # base objects
        vpi = (vt[al] + vt[be]) % Q
        Wnz = off & (vW >= 0)
        res['W_exp'] = int((A - v3arr(vW[Wnz], A)).max()) if Wnz.any() else None
        res['W_zero_chars'] = int((off & (vW < 0)).sum())
        res['pi_exp'] = int((A - v3arr(vpi[off], A)).max())
        res['t_exp'] = int(max(A - L.v3(int(vt[j]), A) for j in range(1, m)))
        # C-type statements: W = pi^n mod 3^i-th powers for some n?  record best (n, i)
        best = (None, 0)
        for n in range(-6, 7):
            x = (vW - n * vpi) % Q
            lev = int(v3arr(x[Wnz], A).min()) if Wnz.any() else A
            if lev > best[1]:
                best = (n, lev)
        res['W_equals_pi^n_mod_3^i'] = best
        seen = set()
        fam = []
        for p in self.units:
            if p in seen:
                continue
            seen |= {p, m - p}
            a2 = 2 * p % m
            Wp = vW[(a2 * al) % m, (a2 * be) % m]
            nz = off & (Wp >= 0)
            Lv = (Wp - vt[al] - vt[be]) % Q
            exps = A - v3arr(Lv, A)
            E_off = int(exps[nz].max()) if nz.any() else 0
            # per-class relative level l_c = v3(L) - (A - a_c)
            lc = v3arr(Lv, A) - (A - a)
            lc_off = lc[nz]
            q = r * p % m
            vd = [(int(vt[p * j % m]) + int(vt[q * j % m]) - int(vt[j])) % Q for j in range(1, m)]
            E_diag = max(A - L.v3(x, A) for x in vd)
            fam.append(dict(p=p, q=q, E_off=E_off, E_diag_opp=E_diag, min_class_level=int(lc_off.min()) if nz.any() else None,
                            zeros_off=int((off & (Wp < 0)).sum())))
        res['family'] = fam
        res['u'] = u
        return res
