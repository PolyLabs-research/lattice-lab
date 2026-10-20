"""t6: the residue-level forcing lemmas, tested for false predictions.
 L1 (threeadic / grouping): R mu27-invariant under P_g (frame A or B)  =>  (2^g - 1) R = 0 mod 27.
 L2 (normform step 6): R mu27-invariant under M in {M0 (4850 frame), T (rotated frame)}  =>  at every class whose
    stabiliser in <D4, (2I,1), (M,0)> has Frobenius multiplier k:  R = 0 mod 27/gcd(2^k - 1, 27).
Test set: the hexagon family f_{p,q}, p, q <= 12 (144 rules) and every radius-4 rule (32767), own field, residues at
all 1368 characters (class bookkeeping c37, checked in t2 against direct evaluation)."""
import sys, json, math, time
import numpy as np
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850/deep/verify-specificity')
import slib as S
import c37
from t3_soundness_lib import f_pq
T0 = time.time()
L = S.Logs37(); E = L.E; F = E.F
M = 37
KEYS = [(g, fr) for g in range(1, 18) for fr in 'AB']
PERMS = {k: c37.perm(c37.partial(*k)) for k in KEYS}
M0 = ((18, 29), (29, 18)); Tg = ((10, 0), (0, 26))
def closure(extra):
    I = ((1, 0), (0, 1))
    gens = [(g, 0) for g in c37.D4] + [(((2, 0), (0, 2)), 1), (extra, 0)]
    seen = {(I, 0)}; fr = [(I, 0)]
    while fr:
        nf = []
        for g, k in fr:
            for h, kh in gens:
                e = (c37.mm(h, g), (k + kh) % 36)
                if e not in seen:
                    seen.add(e); nf.append(e)
        fr = nf
    return seen
FORCED = {}
for name, Mx in (('M0', M0), ('T', Tg)):
    G = closure(Mx)
    lv = []
    for c in c37.NZ:
        lvl = 1
        for g, k in G:
            if c37.act(g, c) == c:
                lvl = max(lvl, 27 // math.gcd(2 ** k - 1, 27))
        lv.append(lvl)
    FORCED[name] = (c37.perm(Mx), np.array(lv))
def residues_all(pts):
    v = E.values(pts)
    vals = np.array([v[c] for c in c37.NZ], dtype=np.uint64)
    return L.log(vals, 27)
def check(R):
    """returns list of (lemma, hypothesis held, conclusion held)"""
    out = []
    nz = R >= 0
    for k, p in PERMS.items():
        if np.all(R[p] == R):  # zeros map to zeros, values equal
            g = k[0]
            need = 27 // math.gcd(2 ** g - 1, 27)
            out.append(('L1 P_g=%d,%s' % k, bool(np.all(R[nz] % need == 0))))
    for name, (p, lv) in FORCED.items():
        if np.all(R[p] == R):
            out.append(('L2 ' + name, bool(np.all((R[nz] % lv[nz]) == 0))))
    return out
stats = {}
def record(tag, R):
    for lemma, ok in check(R):
        s = stats.setdefault(lemma, dict(hyp=0, fail=0, examples=[]))
        s['hyp'] += 1
        if not ok:
            s['fail'] += 1
            if len(s['examples']) < 5:
                s['examples'].append(tag)
for p in range(1, 13):
    for q in range(1, 13):
        f, G = f_pq(p, q)
        if f:
            record(('hex', p, q), residues_all(f))
hexstats = json.loads(json.dumps(stats)); stats.clear()
print('hexagon family: lemma hypotheses held / failures:', {k: (v['hyp'], v['fail']) for k, v in hexstats.items()}, flush=True)
# radius 4: class residues via orbit values, expanded
def class_vals(r, ids):
    ov = []
    for o in S.orbits(r):
        pts = S.orbit_points(*o)
        row = []
        for j, k in c37.REPS:
            x = 0
            for a, b in pts:
                x ^= int(E.zp[(a * j + b * k) % M])
            row.append(x)
        ov.append(row)
    ov = np.array(ov, dtype=np.uint64)
    out = np.zeros((c37.NCL, len(ids)), dtype=np.uint64)
    ids = np.asarray(ids)
    for i in range(ov.shape[0]):
        sel = ((ids >> i) & 1).astype(bool)
        out[:, sel] ^= ov[i][:, None]
    return out
ids = np.arange(1, 1 << 15)
V = class_vals(4, ids)
Lc = L.log(V, 27)  # (11, n), -1 for zero
# expand: zero stays -1
EI = np.array([pow(2, int(i), 27) for i in c37.EI])
for col in range(Lc.shape[1]):
    cl = Lc[:, col]
    R = np.where(cl[c37.CI] < 0, -1, (cl[c37.CI] * EI) % 27)
    record(('r4', int(ids[col])), R)
print('radius-4 family: lemma hypotheses held / failures:', {k: (v['hyp'], v['fail']) for k, v in stats.items()}, flush=True)
json.dump(dict(hexagon=hexstats, radius4=stats, time=round(time.time() - T0, 1)), open('t6_lemmas.json', 'w'), indent=1, default=str)
print('time', round(time.time() - T0, 1))
