"""check-algebra a2: numerical check of (*) and of every ingredient of its proof, in the verifier's own field model
(flib: F2[x]/(factor of Phi_p), zeta = x), at EVERY character (al, be) in (F_p*)^2.

Primes: 37 and all four of {13, 61, 97, 109}; also 19, 67, 139 (family members with e/3 odd, so F4 is NOT in k and
the resolvent argument needs the scalar extension -- covered by the F2 polynomial identity of a1).
Per prime:
  [K]  t_j in K (t^(2^e) = t), and sigma = Frob^(e/3) acts on t-indices by w = -2^(e/3) (t_j^q = t_{w j}).
  [W]  W via sum_{u in mu3} t_{u al} t_{be/u}  ==  W via the 12-term sum over mu6 x {+-1}.
  [N]  N = W^(1+q+q^2) (definition), N in k;  (*) with w and with w^2 vs N.
  [E]  per al: e1 = X, e2 = X + Xa, e3 = X^2, P = X^3 + X Xa, S1 = Xa + Xb, S2 = Xa + Xb', eta((2+w)al) = Xa,
       aux X Xa = Xb + Xb'.
  [PR] product rule eta(x) eta(y) = sum_{v in mu6} eta(x + y v) for ALL x, y in Z/p (incl. 0 and y/x in mu6).
  [C0] char-0 product rule in Z[Z/p] with eta(0) = 6 [0], then reduction mod 2 (p = 13, 19, 37).
  [NEG] sensitivity: three mutilated versions of (*) and how often they still match.
"""
import json
import sys
import time
import numpy as np
from flib import Field

PRIMES = [int(a) for a in sys.argv[1:]] or [13, 19, 37, 61, 97, 109, 67, 139]
OUT = '/home/user/lattice-lab/examples/rule-4850/deep/check-algebra/a2_star_numeric%s.json' % (
    '' if not sys.argv[1:] else '_' + '_'.join(sys.argv[1:]))
res = {}
for p in PRIMES:
    t0 = time.time()
    F = Field(p)
    d = F.d
    assert d % 2 == 0 and (d // 2) % 3 == 0, p
    e = d // 2
    q = 1 << (e // 3)
    s = pow(2, e // 3, p)
    w = (-s) % p
    w2 = w * w % p
    mu3, mu6 = F.mu(3), F.mu(6)
    m, inv = F.mul, (lambda a: pow(a, -1, p))
    eta = [F.eta(x, mu6) for x in range(p)]  # eta[0] = 6*1 = 0 automatically
    r = dict(p=p, d=d, e=e, k_degree=e // 3, w=w, n_Phi_factors=F.nfactors, modulus_bits=bin(F.M))
    # [K]
    r['K_t_in_K'] = all(F.frob(F.t(j), e) == F.t(j) for j in range(p))
    r['K_sigma_acts_by_w'] = all(F.pow(F.t(j), q) == F.t(w * j) for j in range(p))
    r['K_eta_in_k'] = all(F.pow(eta[x], q) == eta[x] for x in range(p))
    r['eta0_is_zero_in_char2'] = eta[0] == 0

    # [E]
    def parts(al, ww):
        X, Xa = eta[al % p], eta[(1 - ww) * al % p]
        Xb, Xbp = eta[(2 - ww) * al % p], eta[(2 - ww * ww) * al % p]
        return X, Xa, Xb, Xbp
    bad_E = {k: 0 for k in ('e1', 'e2', 'e3', 'P', 'S1', 'S2', 'eta(2+w)=Xa', 'aux')}
    for al in range(1, p):
        A = [F.t(pow(w, i, p) * al) for i in range(3)]
        e1 = A[0] ^ A[1] ^ A[2]
        e2 = m(A[0], A[1]) ^ m(A[1], A[2]) ^ m(A[2], A[0])
        e3 = m(m(A[0], A[1]), A[2])
        P = F.pow(A[0], 3) ^ F.pow(A[1], 3) ^ F.pow(A[2], 3)
        S1 = m(m(A[0], A[0]), A[1]) ^ m(m(A[1], A[1]), A[2]) ^ m(m(A[2], A[2]), A[0])
        S2 = m(A[0], m(A[1], A[1])) ^ m(A[1], m(A[2], A[2])) ^ m(A[2], m(A[0], A[0]))
        X, Xa, Xb, Xbp = parts(al, w)
        chk = {'e1': e1 == X, 'e2': e2 == X ^ Xa, 'e3': e3 == m(X, X), 'P': P == F.pow(X, 3) ^ m(X, Xa),
               'S1': S1 == Xa ^ Xb, 'S2': S2 == Xa ^ Xbp, 'eta(2+w)=Xa': eta[(2 + w) * al % p] == Xa,
               'aux': m(X, Xa) == Xb ^ Xbp}
        for k, v in chk.items():
            bad_E[k] += (not v)
    r['E_failures_over_al'] = bad_E

    # [W], [N]
    def star(al, be, ww, mode=0):
        X, Xa, Xb, Xbp = parts(al, ww)
        Y, Ya, Yb, Ybp = parts(be, ww)
        XY = m(X, Y)
        v = m(m(XY, XY), 1 ^ X ^ Y)
        v ^= m(XY, m(X, Ya) ^ m(Xa, Y))
        if mode != 1:
            v ^= m(XY, m(Xa, Ya))
        v ^= m(m(Xa, Ya), X ^ Y)
        if mode == 2:
            v ^= m(Xb, Ybp) ^ m(Xbp, Yb)        # wrong pairing
        elif mode == 3:
            v ^= m(Xb, Yb)                       # drop Xb' Yb'
        else:
            v ^= m(Xb, Yb) ^ m(Xbp, Ybp)
        return v
    badW = badNk = badS = badS2 = badWK = 0
    neg = {1: 0, 2: 0, 3: 0}
    tot = 0
    expo = 1 + q + q * q
    for al in range(1, p):
        for be in range(1, p):
            Wp = 0
            for u in mu3:
                Wp ^= m(F.t(u * al), F.t(be * inv(u)))
            W12 = 0
            for u in mu6:
                for sg in (1, -1):
                    W12 ^= F.z(u * al + sg * be * inv(u))
            badW += Wp != W12
            badWK += F.frob(Wp, e) != Wp
            N = F.pow(Wp, expo)
            badNk += F.pow(N, q) != N
            badS += star(al, be, w) != N
            badS2 += star(al, be, w2) != N
            for k in neg:
                neg[k] += star(al, be, w, k) == N
            tot += 1
    r.update(characters=tot, W_productform_vs_12term_fail=badW, W_not_in_K=badWK, N_not_in_k=badNk,
             star_fail_w=badS, star_fail_w2=badS2,
             NEG_still_match={'drop XY XaYa': neg[1], 'pair Xb Yb\' + Xb\' Yb': neg[2], 'drop Xb\' Yb\'': neg[3]})

    # [PR] product rule, all x, y in Z/p
    badPR = edge = 0
    for x in range(p):
        for y in range(p):
            rhs = 0
            hit0 = False
            for v in mu6:
                z = (x + y * v) % p
                hit0 |= z == 0
                rhs ^= eta[z]
            edge += hit0
            badPR += m(eta[x], eta[y]) != rhs
    r.update(PR_pairs=p * p, PR_fail=badPR, PR_pairs_hitting_eta0=edge)

    # [C0] char-0 group ring
    if p in (13, 19, 37):
        def etaZ(x):
            v = np.zeros(p, dtype=np.int64)
            for u in mu6:
                v[x * u % p] += 1
            return v

        def conv(a, b):
            o = np.zeros(p, dtype=np.int64)
            for i in np.nonzero(a)[0]:
                o += a[i] * np.roll(b, i)
            return o
        badC0 = badC0mod2 = 0
        for x in range(p):
            for y in range(p):
                lhs = conv(etaZ(x), etaZ(y))
                rhs = sum(etaZ((x + y * v) % p) for v in mu6)
                badC0 += not np.array_equal(lhs, rhs)
        # eta(0) in Z[Z/p] is 6*[0]: reduction mod 2 is 0, and [0] = 1 in the field (J -> 0 is irrelevant here)
        r.update(C0_fail=badC0, C0_eta0_vector_is_6_at_0=etaZ(0).tolist()[:1] + [int(etaZ(0)[1:].sum())])
    r['seconds'] = round(time.time() - t0, 1)
    res[p] = r
    print(json.dumps(r), flush=True)
json.dump(res, open(OUT, 'w'), indent=1)
