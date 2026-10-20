"""t3 (claim 2): soundness of the hexagon / order-3-symmetry forcing arguments, from scratch.

(A) the cited counterexamples at 37:
    21563 (radius 4): pi*f support invariant under an order-3 element of SL2(F37)? cube-confined?
    105299, 132097, 1084246 (radius 5): s*f support M0-invariant?  mu27 residue M0-invariant?  confined?
(B) the hexagon family f_{p,q} = (Hex_{p,q} + Hex_{p,q}^T) / s, Hex = {+-(2p,0), +-(p,q), +-(p,-q)}, own exact
    Laurent division; f_{2,5} = 4850 checked.  At m = 37 for all p, q <= 12, and at m = 13, 61, 97, 109, 185 for
    the (p, q) whose s*f support is invariant under a projective order-3 element of SL2(Z/m) (found by direct
    search; at 185 by CRT), plus f_{2,5} as a control.  Status of each: own-field cube / ninth confinement, exact
    group-ring confinement (at 37 and for all predicted rules), and eigen.odd_part (the independent period).
(C) the reduction's forcing arguments, applied wherever their hypotheses hold, and compared with the truth:
    for a -3-type rule (q = (2w+1)p mod m, w a cube root of 1) the identity
        lambda_f(j,k) * t_al t_be = W(l al, l be),  al = (j+k)/2, be = (j-k)/2, l = 2p,
        W(al, be) = sum_{u in mu3} t_{u al} t_{be/u}
    is checked exactly (field) at every character with al*be != 0.  Then per character c' = (l al, l be):
      F1 exact t-factorisation of W(c') (combinatorial: the 6-term t-sum after cancellation is t_x, t_x t_y, or
         t_x t_y t_z exactly) -> v9(W) = sum v9(t_x);
      F2 Frobenius stabiliser: g in <D4, T, 2I> with g c' = c', W(g c) = W(c)^(2^k) -> W(c') in F(2^gcd(k,d));
         predicts ninth when 9 | (2^d - 1)/(2^gcd(k,d) - 1);
      F3 Legendre bookkeeping (37's law v9(t_j) = 3 kappa chi(j)) -- the 37 version -- and, as the sound generic
         version, the actual v9(t_j) at m.
    Prediction for lambda: v9(W(c')) - v9(t_al) - v9(t_be) when W's class is forced; else 'residual'.
    A wrong prediction (predicted ninth, actually not; or predicted not ninth, actually ninth) refutes soundness.
    Also the 37-version applied at other m (transplanted Legendre law) to show where it would mispredict, and the
    'reduction + residual fact' prediction at 37: e even -> ninth off the diagonals, e odd -> not.
(D) the same-identity family f_O = G_O^4 / pi (pi f = G_O^4 exactly, G_O a <D4,T>-orbit; exactly T-invariant
    eigenvalue structure): how many are cube-confined -- i.e. does T-symmetry alone force cubes?"""
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


# ================================================================ (A) counterexamples at 37
Z37 = Size(37)
mats37 = sl2_order3(37)
log('projective order-3 elements of SL2(F37):', len(mats37))
D4set = {((1, 0), (0, 1)), ((36, 0), (0, 1)), ((1, 0), (0, 36)), ((36, 0), (0, 36)),
         ((0, 1), (1, 0)), ((0, 36), (1, 0)), ((0, 1), (36, 0)), ((0, 36), (36, 0))}
A = {}
f = S.rule(21563, 4)
G = S.lmul(f, S.PI_POLY)
inv = invariant_elements(G, mats37, 37)
st, v = Z37.status(f, group_ring=True)
A['21563'] = dict(pi_f_terms=len(G), order3_elements_fixing_pi_f=len(inv), example=inv[:2], **st)
G2 = S.lmul(f, S.S_POLY)
A['21563']['order3_elements_fixing_s_f'] = len(invariant_elements(G2, mats37, 37))
log('(A) 21563:', A['21563'])
M0 = ((18, 29), (29, 18))
L37 = S.Logs37()
import c37
pM0 = c37.perm(M0)
for n in (105299, 132097, 1084246, 4850):
    r = 5 if n != 4850 else 4
    f = S.rule(n, r)
    Gs = S.lmul(f, S.S_POLY)
    sup_inv = len(invariant_elements(Gs, [M0], 37)) == 1
    any_inv = len(invariant_elements(Gs, mats37, 37))
    st, v = Z37.status(f, group_ring=True)
    vals = np.array([v[c] for c in c37.NZ], dtype=np.uint64)
    l27 = L37.log(vals, 27)
    res_inv = bool(np.all(l27[pM0] == l27))
    bothz = (l27 < 0) & (l27[pM0] < 0)
    bothnz = (l27 >= 0) & (l27[pM0] >= 0)
    res_inv9 = bool(np.all(bothz | (bothnz & ((l27[pM0] - l27) % 9 == 0))))
    A[str(n)] = dict(s_f_terms=len(Gs), s_f_support_M0_invariant=sup_inv, s_f_order3_elements=any_inv,
                     residue27_M0_invariant=res_inv, residue_mod9_M0_invariant=res_inv9, **st)
    log('(A)', n, A[str(n)])
OUT['A_counterexamples'] = A

# ================================================================ (B, C) hexagon family at 37
f25, _ = f_pq(2, 5)
OUT['f25_is_4850'] = f25 == S.rule(4850, 4)
log('f_{2,5} == rule 4850:', OUT['f25_is_4850'])
rows37 = []
for p in range(1, 13):
    for q in range(1, 13):
        f, G = f_pq(p, q)
        if not f:
            rows37.append(dict(p=p, q=q, empty=True)); continue
        typ = ('-3' if (q * q + 3 * p * p) % 37 == 0 else '') + ('+3' if (q * q - 3 * p * p) % 37 == 0 else '')
        inv = invariant_elements(G, mats37, 37)
        st, v = Z37.status(f, group_ring=True)
        rec = dict(p=p, q=q, type=typ, terms=len(f), radius=S.radius_of(f), G_terms=len(G),
                   order3_fixers=len(inv), **st)
        if typ == '-3':
            pr = predict_rule(Z37, f, p, q, legendre37=True)
            pg = predict_rule(Z37, f, p, q, legendre37=False)
            # 'reduction + residual fact': l = +-2^e; e even -> ninth off diagonals
            l = 2 * p % 37
            e = next(e for e in range(36) if pow(2, e, 37) in (l, 37 - l))
            rec.update(e=e, red_pred_offdiag_ninth=(e % 2 == 0), pred37=pr, pred_generic=pg)
        rows37.append(rec)
        if typ or rec.get('ninth') or rec['order3_fixers']:
            log('  37', {k: rec[k] for k in ('p', 'q', 'type', 'radius', 'order3_fixers', 'cube', 'ninth', 'odd_part', 'zero_chars')},
                ('e=%d pred37: covered %d wrong %d residual %d ident %s | generic wrong %d' % (
                    rec['e'], rec['pred37']['covered'], rec['pred37']['wrong'], rec['pred37']['residual_orbits'],
                    rec['pred37']['identity_lambda_pi_eq_W'], rec['pred_generic']['wrong'])) if typ == '-3' else '')
OUT['hex37'] = rows37
sym37 = [r for r in rows37 if r.get('order3_fixers')]
OUT['hex37_summary'] = dict(
    rules=len([r for r in rows37 if not r.get('empty')]),
    with_order3_symmetry=len(sym37),
    symmetric_cube=sum(1 for r in sym37 if r['cube']), symmetric_ninth=sum(1 for r in sym37 if r['ninth']),
    symmetric_not_cube=[(r['p'], r['q'], r['type']) for r in sym37 if not r['cube']],
    type_counts={t: sum(1 for r in rows37 if r.get('type') == t) for t in ('-3', '+3', '-3+3')},
    ninth_all=[(r['p'], r['q'], r.get('type')) for r in rows37 if r.get('ninth')],
    minus3_pred37_wrong=sum(r['pred37']['wrong'] for r in rows37 if r.get('type') == '-3'),
    minus3_generic_wrong=sum(r['pred_generic']['wrong'] for r in rows37 if r.get('type') == '-3'),
    minus3_reduction_vs_actual=[(r['p'], r['q'], r['e'], r['red_pred_offdiag_ninth'], r['pred37']['actual_offdiag_ninth'], r['ninth'])
                                for r in rows37 if r.get('type') == '-3'],
)
log('hex37 summary:', OUT['hex37_summary'])
log('time', round(time.time() - T0, 1))
json.dump(OUT, open('t3_soundness.json', 'w'), indent=1, default=str)

# ================================================================ (B, C) other sizes
other = {}
for m in (13, 61, 97, 109, 185):
    Z = Size(m)
    mats = sl2_order3(m)
    cand = []
    rng = range(1, 13) if m != 185 else range(1, 31)
    for p in rng:
        for q in rng:
            typ = ('-3' if (q * q + 3 * p * p) % m == 0 else '') + ('+3' if (q * q - 3 * p * p) % m == 0 else '')
            if typ or (p, q) == (2, 5):
                cand.append((p, q, typ))
    if m == 185:
        cand = [c for c in cand if c[2] or c[:2] == (2, 5)][:12]
    rows = []
    for p, q, typ in cand:
        f, G = f_pq(p, q)
        if not f:
            continue
        inv = invariant_elements(G, mats, m)
        st, v = Z.status(f, group_ring=(m <= 109 or len(f) < 400))
        rec = dict(p=p, q=q, type=typ, terms=len(f), radius=S.radius_of(f), order3_fixers=len(inv), **st)
        if '-3' in typ and Z.omega:
            try:
                rec['pred_generic'] = predict_rule(Z, f, p, q, legendre37=False)
                rec['pred_transplanted37'] = predict_rule(Z, f, p, q, legendre37=True)
            except StopIteration:
                pass
        rows.append(rec)
        log('  m=%d' % m, {k: rec[k] for k in ('p', 'q', 'type', 'radius', 'order3_fixers', 'cube', 'ninth', 'odd_part', 'zero_chars')},
            ('generic: ident %s covered %d wrong %d residual %d | 37-law kappa %s covered %d wrong %d' % (
                rec['pred_generic']['identity_lambda_pi_eq_W'], rec['pred_generic']['covered'], rec['pred_generic']['wrong'],
                rec['pred_generic']['residual_orbits'], rec['pred_transplanted37']['legendre_kappa'],
                rec['pred_transplanted37']['covered'], rec['pred_transplanted37']['wrong'])) if 'pred_generic' in rec else '')
    other[m] = dict(d=Z.d, order3_elements=len(mats), rows=rows,
                    symmetric=len([r for r in rows if r['order3_fixers']]),
                    symmetric_cube=sum(1 for r in rows if r['order3_fixers'] and r['cube']),
                    symmetric_ninth=sum(1 for r in rows if r['order3_fixers'] and r['ninth']),
                    any_ninth=[(r['p'], r['q']) for r in rows if r['ninth']],
                    generic_wrong=sum(r['pred_generic']['wrong'] for r in rows if 'pred_generic' in r),
                    transplanted_wrong=sum(r['pred_transplanted37']['wrong'] for r in rows if 'pred_transplanted37' in r))
    log('m=%d summary:' % m, {k: v_ for k, v_ in other[m].items() if k != 'rows'}, ' time', round(time.time() - T0, 1))
    OUT['other_sizes'] = other
    json.dump(OUT, open('t3_soundness.json', 'w'), indent=1, default=str)

# ================================================================ (D) f_O = G_O^4 / pi at 37
D4 = [((1, 0), (0, 1)), ((-1, 0), (0, 1)), ((1, 0), (0, -1)), ((-1, 0), (0, -1)),
      ((0, 1), (1, 0)), ((0, -1), (1, 0)), ((0, 1), (-1, 0)), ((0, -1), (-1, 0))]
Tg = ((10, 0), (0, 26))
seen, orbs = set(), []
for c in [(a, b) for a in range(1, 37) for b in range(1, 37)]:
    if c in seen:
        continue
    O = {c}; fr = [c]
    while fr:
        nf_ = []
        for x in fr:
            for g in D4 + [Tg]:
                y = ((g[0][0] * x[0] + g[0][1] * x[1]) % 37, (g[1][0] * x[0] + g[1][1] * x[1]) % 37)
                if y not in O:
                    O.add(y); nf_.append(y)
        fr = nf_
    seen |= O; orbs.append(frozenset(O))
cen = lambda a: (a % 37) - 37 if (a % 37) > 18 else (a % 37)
Drows = []
for O in orbs:
    G4 = frozenset((4 * cen(a), 4 * cen(b)) for a, b in O)
    f, R = S.ldiv(G4, S.PI_POLY)
    assert not R
    st, v = Z37.status(f, group_ring=False, odd=False)
    offm = (Z37.E.J != 0) & (Z37.E.K != 0)
    cmask = Z37.E.qth_power_mask(v, 3)
    cube_off = bool(np.all(cmask[offm] | (v[offm] == 0)))
    Drows.append(dict(size=len(O), rep=min(O), cube=st['cube'], ninth=st['ninth'], cube_off_axis=cube_off))
OUT['G4_over_pi_family'] = dict(n=len(Drows), cube=sum(r['cube'] for r in Drows), ninth=sum(r['ninth'] for r in Drows),
                                cube_by_size={s: sum(r['cube'] for r in Drows if r['size'] == s) for s in (12, 24)},
                                cube_off_axis=sum(r['cube_off_axis'] for r in Drows))
log('(D) f_O = G_O^4/pi over all <D4,T>-orbits:', OUT['G4_over_pi_family'])
OUT['time'] = round(time.time() - T0, 1)
log('time', OUT['time'])
json.dump(OUT, open('t3_soundness.json', 'w'), indent=1, default=str)
