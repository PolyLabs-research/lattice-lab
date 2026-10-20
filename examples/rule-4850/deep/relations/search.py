"""
Two-rule multiplicative relations modulo F(2^9)* at m = 37.

For a target f (log vector F mod 513 over the 11 classes) find every
    gamma * F = delta * L(M1) + L(M2)   (mod 513, at every class of a chosen set)
with gamma = 2^gp, delta = 2^dp (gp, dp in 0..17: every power of 2 mod 513, -1 = 2^9 included)
and M1, M2 rules of radius <= 5 that are nonzero on the chosen classes (the identity, rule 1,
has L = 0). Equivalently
    f^(2^gp) = M1^(2^dp) * M2 * (F(2^9)-valued)    at every character of those classes,
which covers alpha*L(f) + beta*L(M1) = L(M2) for all alpha, beta in <2> (divide by alpha).

Class sets ("modes"):
    all   the 10 classes other than (1,6) (which is F(2^9)-valued for every rule); M1, M2 zero-free.
    off   the 8 classes i = 1..8 of the dossier, (1,2),(1,3),(1,4),(1,5),(1,7),(1,8),(1,10),(1,13):
          the axis and the diagonal are explained for 4850 separately, and rule-90 orbit units
          such as t(x)t(y)t(xy)t(x/y) vanish there (the half-Frobenius certificates are of
          this kind). M1, M2 need only be nonzero on these 8 classes.

Hashing: the vectors are keyed on 7 of their coordinates (uint64), with a packed bitmap on the
first 3 coordinates as a prefilter, then searchsorted, then exact comparison. Every hit is then
verified exactly in the group ring F2[x,y]/(x^37-1, y^37-1) by
    P(x^512) Q M2 == P Q(x^512) M2(x^512),   P = f(x^(2^gp)), Q = M1(x^(2^dp)),
i.e. (lambda_P / (lambda_Q lambda_M2))^511 = 1 at every character where M1, M2 are nonzero
(no discrete logs involved).
"""
from __future__ import annotations

import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tables  # noqa: E402

C = tables.C
M = 37
MODES = {"all": [0, 1, 2, 3, 4, 5, 7, 8, 9, 10], "off": [2, 3, 4, 5, 7, 8, 9, 10]}
KEYC = 7
POW = np.array([pow(513, i) for i in range(KEYC)], dtype=np.uint64)
P2 = [pow(2, k, 513) for k in range(18)]


class Index:
    def __init__(self, mode="all", L=None, ids=None):
        if L is None:
            L = tables.L5()
            ids = np.arange(L.shape[1])
        self.mode = mode
        self.cls = MODES[mode]
        ok = (L[self.cls] >= 0).all(axis=0)
        self.ids = np.asarray(ids)[ok]  # rule numbers
        self.V = L[self.cls][:, ok].astype(np.int32)  # (k, n)
        key = self.key(self.V)
        order = np.argsort(key, kind="stable")
        self.skey = key[order]
        self.sidx = order
        k3 = self.V[0].astype(np.int64) + 513 * self.V[1] + 263169 * self.V[2].astype(np.int64)
        bm = np.zeros(513**3, dtype=bool)
        bm[k3] = True
        self.bits = np.packbits(bm, bitorder="little")
        self.n3 = len(np.unique(k3))

    @staticmethod
    def key(V) -> np.ndarray:
        k = np.zeros(V.shape[1], dtype=np.uint64)
        for i in range(KEYC):
            k += V[i].astype(np.uint64) * POW[i]
        return k

    def lookup(self, Q, cols):
        key = self.key(Q)
        lo = np.searchsorted(self.skey, key, "left")
        hi = np.searchsorted(self.skey, key, "right")
        out = []
        for c in np.flatnonzero(hi > lo):
            for p in range(lo[c], hi[c]):
                j = self.sidx[p]
                if (self.V[:, j] == Q[:, c]).all():
                    out.append((int(cols[c]), int(self.ids[j])))
        return out

    def search(self, F, verbose=False, dps=range(18), gps=range(18), m1max=None,
               fmults=None, m1mults=None, max_hits=None):
        """All (gp, dp, M1, M2) with 2^gp F = 2^dp L(M1) + L(M2) mod 513 on the mode's classes.
        m1max: restrict M1 to rule numbers < m1max (e.g. 2^15 = radius <= 4)."""
        F = np.asarray(F, dtype=np.int64)[self.cls]
        assert (F >= 0).all()
        fm = P2 if fmults is None else list(fmults)  # multipliers of F (default: 2^gp)
        mm = P2 if m1mults is None else list(m1mults)  # multipliers of L(M1) (default: 2^dp)
        if fmults is not None:
            gps = range(len(fm))
        if m1mults is not None:
            dps = range(len(mm))
        hits = []
        t0 = time.time()
        sel = np.arange(self.V.shape[1]) if m1max is None else np.flatnonzero(self.ids < m1max)
        V1 = self.V[:, sel]
        for dp in dps:
            D3 = ((mm[dp] * V1[:3]) % 513).astype(np.int32)
            for gp in gps:
                G = (fm[gp] * F) % 513
                q0 = G[0] - D3[0]; q0 += 513 * (q0 < 0)  # noqa: E702
                q1 = G[1] - D3[1]; q1 += 513 * (q1 < 0)  # noqa: E702
                q2 = G[2] - D3[2]; q2 += 513 * (q2 < 0)  # noqa: E702
                k3 = q0.astype(np.int64) + 513 * q1 + 263169 * q2.astype(np.int64)
                ok = (self.bits[k3 >> 3] >> (k3 & 7).astype(np.uint8)) & 1
                cols = sel[np.flatnonzero(ok)]
                if cols.size == 0:
                    continue
                Q = (G[:, None] - (mm[dp] * self.V[:, cols]) % 513) % 513
                for c, m2 in self.lookup(Q.astype(np.int32), cols):
                    hits.append((gp, dp, int(self.ids[c]), m2))
                if max_hits is not None and len(hits) >= max_hits:
                    return hits
            if verbose:
                print(f"  dp={dp} {time.time() - t0:.0f}s hits so far {len(hits)}", flush=True)
        return hits


# ---------------------------------------------------------------- exact group-ring checks
def dense(f, m=M) -> np.ndarray:
    a = np.zeros((m, m), dtype=np.int64)
    for p, q in f:
        a[p % m, q % m] ^= 1
    return a


def gmul(a, b) -> np.ndarray:
    r = np.fft.ifft2(np.fft.fft2(a) * np.fft.fft2(b)).real
    return np.rint(r).astype(np.int64) & 1


def dilate(a, d, m=M) -> np.ndarray:
    out = np.zeros_like(a)
    idx = (np.arange(m) * d) % m
    out[np.ix_(idx, idx)] = a
    return out


def exact_relation(f, gp, dp, m1, m2) -> bool:
    """(lambda_f^(2^gp) / (lambda_M1^(2^dp) lambda_M2))^511 = 1 wherever M1, M2 are nonzero."""
    P = dilate(dense(f), pow(2, gp, M))
    Q = dilate(dense(C.rule(m1, 5)), pow(2, dp, M))
    R = dense(C.rule(m2, 5))
    s = 512 % M
    lhs = gmul(gmul(dilate(P, s), Q), R)
    rhs = gmul(gmul(P, dilate(Q, s)), dilate(R, s))
    return bool((lhs == rhs).all())


_INDEX = {}


def index(mode="all") -> Index:
    if mode not in _INDEX:
        _INDEX[mode] = Index(mode)
    return _INDEX[mode]
