"""helpers of t3_soundness.py (identical code, importable without running the tests)."""
import sys, json, time, math, itertools
import numpy as np
import sympy
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/verify-specificity')
import slib as S
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
import eigen

T0 = time.time()
OUT = {}


def log(*a):
    print(*a, flush=True)


# ---------------------------------------------------------------- generic helpers at size m
class Size:
    def __init__(self, m):
        self.m = m
        self.E = S.Eig(m)
        self.F = self.E.F
        self.d = self.F.d
        self.N = self.F.N
        self.GR = S.GroupRing(m)
        F = self.F
        # h of order 9 (when 9 | N) for logs mod 9
        self.has9 = self.N % 9 == 0
        if self.has9:
            x = next(x for x in range(2, 10000) if F.pow(x, self.N // 3) != 1)
            h = F.pow(x, self.N // 9)
            pw = [1]
            for _ in range(8):
                pw.append(F.mul(pw[-1], h))
            assert F.mul(pw[-1], h) == 1 and len(set(pw)) == 9
            self.lut9 = {v: i for i, v in enumerate(pw)}
        zp = self.E.zp
        self.t = np.array([int(zp[i]) ^ int(zp[(-i) % m]) for i in range(m)], dtype=np.uint64)
        self.mu3 = [u for u in range(1, m) if pow(u, 3, m) == 1]
        self.omega = [u for u in self.mu3 if u != 1]

    def v9(self, x):
        x = np.asarray(x, dtype=np.uint64)
        w = self.F.vpow(x, self.N // 9)
        out = np.array([self.lut9.get(int(y), -2) for y in w.ravel()], dtype=np.int64).reshape(x.shape)
        out[x == 0] = -1
        return out

    def status(self, pts, group_ring=False, odd=True):
        v = self.E.values(pts)
        rec = dict(zero_chars=int((v == 0).sum()))
        rec['cube'] = self.E.confined(v, 3) if self.N % 3 == 0 else None
        rec['ninth'] = self.E.confined(v, 9) if self.has9 else None
        if group_ring:
            a = self.GR.elem(pts)
            rec['gr_cube'] = self.GR.confined(a, 3)
            rec['gr_ninth'] = self.GR.confined(a, 9)
            assert rec['gr_cube'] == rec['cube'] and rec['gr_ninth'] == rec['ninth']
        if odd:
            op = eigen.odd_part(frozenset(pts), self.m)
            rec['odd_part'] = op
            rec['odd_ninth'] = (self.N // 9) % op == 0 if self.has9 else None
            rec['odd_cube'] = (self.N // 3) % op == 0
            if self.has9:
                assert rec['odd_ninth'] == rec['ninth'], (pts, self.m)
        return rec, v


def hexagon(p, q):
    return frozenset({(2 * p, 0), (-2 * p, 0), (p, q), (-p, -q), (p, -q), (-p, q)})


def f_pq(p, q):
    H = hexagon(p, q)
    HT = frozenset((b, a) for a, b in H)
    G = S.ladd(H, HT)
    f, R = S.ldiv(G, S.S_POLY)
    assert not R and S.lmul(f, S.S_POLY) == G
    return f, G


def sl2_order3(m):
    """projective order-3 elements of SL2(Z/m): M^3 = +-I, M != +-I (m prime, or 185 = 5 * 37 by CRT)."""
    def prime_list(pr, include_pm_identity):
        # parametrise by trace: tr = -1 (M^3 = I) or tr = +1 (M^3 = -I); plus +-I if asked
        out = []
        for tr, sgn in ((pr - 1, 1), (1, -1)):
            for a in range(pr):
                d_ = (tr - a) % pr
                for b in range(pr):
                    if b == 0:
                        if a * d_ % pr != 1:
                            continue
                        for c in range(pr):
                            out.append(((a, 0), (c, d_), sgn))
                    else:
                        c = (a * d_ - 1) * pow(b, -1, pr) % pr
                        out.append(((a, b), (c, d_), sgn))
        if include_pm_identity:
            out.append(((1, 0), (0, 1), 1))
            out.append(((pr - 1, 0), (0, pr - 1), -1))
        return out
    fac = sympy.factorint(m)
    assert all(e == 1 for e in fac.values())
    ps = sorted(fac)
    if len(ps) == 1:
        return [((a, b), (c, d_)) for (a, b), (c, d_), s in prime_list(m, False)]
    assert len(ps) == 2
    p1, p2 = ps
    L1, L2 = prime_list(p1, True), prime_list(p2, True)
    out = []
    for (A1, B1, s1) in L1:
        for (A2, B2, s2) in L2:
            if s1 != s2:
                continue
            if A1 == (1, 0) and B1 == (0, 1) and A2 == (1, 0) and B2 == (0, 1):
                continue
            if A1 == (p1 - 1, 0) and B1 == (0, p1 - 1) and A2 == (p2 - 1, 0) and B2 == (0, p2 - 1):
                continue
            ent = []
            for x1, x2 in zip(A1 + B1, A2 + B2):
                ent.append(int(sympy.ntheory.modular.crt([p1, p2], [x1, x2])[0]))
            out.append(((ent[0], ent[1]), (ent[2], ent[3])))
    return out


def invariant_elements(G, mats, m):
    pts = np.array(sorted({(p % m, q % m) for p, q in G}), dtype=np.int64)
    key = set(map(tuple, pts))
    A = np.array([[M[0][0], M[0][1], M[1][0], M[1][1]] for M in mats], dtype=np.int64)
    X = (A[:, 0:1] * pts[None, :, 0] + A[:, 1:2] * pts[None, :, 1]) % m
    Y = (A[:, 2:3] * pts[None, :, 0] + A[:, 3:4] * pts[None, :, 1]) % m
    codes = np.sort(X * m + Y, axis=1)
    kc = np.array(sorted(p * m + q for p, q in key))
    ok = np.all(codes == kc[None, :], axis=1)
    return [mats[i] for i in np.flatnonzero(ok)]


def t_sum_indices(al, be, m, mu3):
    """W(al, be) = sum_{u in mu3} (t_{u al + be/u} + t_{u al - be/u}) as a set of indices mod +- after cancellation."""
    cnt = {}
    for u in mu3:
        ui = pow(u, -1, m)
        for e in (1, -1):
            i = (u * al + e * be * ui) % m
            i = min(i, m - i)
            if i == 0:
                continue  # t_0 = 0
            cnt[i] = cnt.get(i, 0) ^ 1
    return frozenset(i for i, c in cnt.items() if c)


def t_product_expansion(xs, m):
    """indices of prod t_x as a sum of t's (mod +-, cancelling)."""
    terms = {0: 1}  # exponent -> parity, as Laurent in zeta
    for x in xs:
        new = {}
        for e, c in terms.items():
            for s in (x, -x):
                k = (e + s) % m
                new[k] = new.get(k, 0) ^ c
        terms = {k: c for k, c in new.items() if c}
    # sum_k zeta^k must be symmetric: pair k with -k into t_k
    out = set()
    for k in terms:
        if k == 0:
            raise ValueError('constant term')
        kk = min(k, m - k)
        out.add(kk)
    return frozenset(out)


def factor_W(Sidx, m, cache={}):
    """exact factorisation of the t-sum with index set Sidx as t_x, t_x t_y or t_x t_y t_z (None if not)."""
    key = (Sidx, m)
    if key in cache:
        return cache[key]
    res = None
    s = sorted(Sidx)
    h = pow(2, -1, m)
    if len(s) == 1:
        res = (s[0],)
    elif len(s) == 2:
        a, b = s
        res = ((a + b) * h % m, (a - b) * h % m)
        res = tuple(min(x, m - x) for x in res)
        assert t_product_expansion(res, m) == Sidx
    elif len(s) == 4:
        # t_x t_y t_z = t_{x+y+z} + t_{x+y-z} + t_{x-y+z} + t_{-x+y+z}; with s1 = x+y+z etc. up to signs:
        # x = (s_a + s_b)/2 for suitable signed pairs; brute force over sign patterns of the four indices
        for signs in itertools.product((1, -1), repeat=3):
            A = s[0]
            B, C, D = (sg * v for sg, v in zip(signs, s[1:]))
            # try A = x+y+z, B = x+y-z, C = x-y+z, D = -x+y+z (as residues)
            # solve linear system exactly: x = (B + C)/2, y = (B + D)/2, z = (C + D)/2
            x = (B + C) * h % m; y = (B + D) * h % m; z = (C + D) * h % m
            xs = tuple(sorted(min(v, m - v) for v in (x, y, z)))
            if 0 in xs:
                continue
            try:
                if t_product_expansion(xs, m) == Sidx:
                    res = xs
                    break
            except ValueError:
                continue
    cache[key] = res
    return res


def frob_stabiliser(c, m, d, Tm):
    """Frobenius exponents k (mod d) such that some g in <D4, T> satisfies 2^k g c = c."""
    D4 = [((1, 0), (0, 1)), ((-1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, -1)),
          ((0, 1), (1, 0)), ((0, -1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (-1, 0))]
    ks = set()
    imgs = set()
    for g in D4:
        for Ti in Tm:
            x = (Ti[0] * c[0]) % m, (Ti[1] * c[1]) % m
            y = ((g[0][0] * x[0] + g[0][1] * x[1]) % m, (g[1][0] * x[0] + g[1][1] * x[1]) % m)
            imgs.add(y)
    for k in range(d):
        u = pow(2, k, m)
        for y in imgs:
            if (u * y[0] % m, u * y[1] % m) == c:
                ks.add(k)
    return sorted(ks)


def predict_rule(Z, f, p, q, legendre37=False):
    """Apply F1-F3 to a -3-type rule f_{p,q} at size Z.m.  Returns per-Frobenius-orbit predictions vs truth."""
    m, F = Z.m, Z.F
    w = next(u for u in Z.omega if (q - (2 * u + 1) * p) % m == 0 or (q + (2 * u + 1) * p) % m == 0)
    l = 2 * p % m
    lam = Z.E.values(f)
    t = Z.t
    h = pow(2, -1, m)
    J, K = Z.E.J, Z.E.K
    AL = ((J + K) * h) % m
    BE = ((J - K) * h) % m
    # W(l al, l be) at every character
    Wv = np.zeros((m, m), dtype=np.uint64)
    for u in Z.mu3:
        ui = pow(u, -1, m)
        Wv ^= F.vmul(t[(u * l * AL) % m], t[(ui * l * BE) % m])
    pi = F.vmul(t[AL], t[BE])
    off = (AL != 0) & (BE != 0)
    ident = bool(np.array_equal(F.vmul(lam, pi)[off], Wv[off]))
    # 37's Legendre law check (v9(t_j) = 3 kappa chi(j))
    vt = Z.v9(t[1:])
    chi = np.array([1 if pow(j, (m - 1) // 2, m) == 1 else -1 for j in range(1, m)]) if sympy.isprime(m) else None
    leg = None
    if chi is not None and np.all(vt >= 0):
        for kappa in (1, 2):
            if np.all((vt - 3 * kappa * chi) % 9 == 0):
                leg = kappa
    vt_full = np.concatenate([[-1], vt])
    Tm = [(1, 1), (w, pow(w, -1, m)), (w * w % m, pow(w * w, -1, m))]
    seen = set()
    rows = []
    vlam = Z.v9(lam)
    for j in range(m):
        for k in range(m):
            if not off[j, k] or (j, k) in seen:
                continue
            c = (j, k)
            while c not in seen:
                seen.add(c); c = (2 * c[0] % m, 2 * c[1] % m)
            al, be = int(AL[j, k]), int(BE[j, k])
            cp = (l * al % m, l * be % m)
            Sidx = t_sum_indices(cp[0], cp[1], m, Z.mu3)
            fac = factor_W(Sidx, m)
            src, vW = None, None
            if fac is not None:
                src = 'F1:t-product' + str(len(fac))
                if legendre37:
                    vW = sum(3 * leg * (1 if pow(x, (m - 1) // 2, m) == 1 else -1) for x in fac) if leg else None
                else:
                    vv = [int(vt_full[x]) for x in fac]
                    vW = None if min(vv) < 0 else sum(vv)
            else:
                ks = frob_stabiliser(cp, m, Z.d, Tm)
                gs = [math.gcd(k, Z.d) for k in ks if k % Z.d]
                forced = [g_ for g_ in gs if (Z.N // (2 ** g_ - 1)) % 9 == 0]
                if forced:
                    src, vW = 'F2:frobenius-stabiliser', 0
            if vW is None:
                pred = None
            else:
                if legendre37:
                    if leg is None:
                        pred = None
                    else:
                        va = 3 * leg * (1 if pow(al, (m - 1) // 2, m) == 1 else -1)
                        vb = 3 * leg * (1 if pow(be, (m - 1) // 2, m) == 1 else -1)
                        pred = (vW - va - vb) % 9 == 0
                else:
                    va, vb = int(vt_full[al]), int(vt_full[be])
                    pred = None if min(va, vb) < 0 else (vW - va - vb) % 9 == 0
            actual = None if lam[j, k] == 0 else bool(vlam[j, k] % 9 == 0)
            rows.append(dict(c=(j, k), ratio_class=(al, be), source=src, predicted_ninth=pred, actual_ninth=actual))
    covered = [r for r in rows if r['predicted_ninth'] is not None]
    wrong = [r for r in covered if r['actual_ninth'] is not None and r['predicted_ninth'] != r['actual_ninth']]
    return dict(identity_lambda_pi_eq_W=ident, l=l, omega=w, legendre_kappa=leg, orbits=len(rows),
                covered=len(covered), wrong=len(wrong), wrong_examples=wrong[:5],
                residual_orbits=len(rows) - len(covered),
                residual_actual_ninth=sum(1 for r in rows if r['predicted_ninth'] is None and r['actual_ninth']),
                predicted_all_covered_ninth=all(r['predicted_ninth'] for r in covered) if covered else None,
                actual_offdiag_ninth=all(r['actual_ninth'] for r in rows if r['actual_ninth'] is not None))


