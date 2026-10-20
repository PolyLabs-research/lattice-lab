"""v3 (claim 2): the partial-Frobenius lemma and its use for 4850.
Lemma: R swap-symmetric (R(j,k) = R(k,j)), Frobenius-equivariant (R(2c) = 2R(c) mod 27), and R(j, 2^g k) = R(j, k) for all
(j,k)  ==>  R(2^g j, 2^g k) = R(2^g j, k) = R(k, 2^g j) = R(k, j) = R(j, k), and R(2^g c) = 2^g R(c), so (2^g - 1) R = 0 mod 27.
(a) numerical check of the lemma on every zero-free rule of radius <= 4 (32767 rules, frames A and B, g = 1..17), using class
    residues expanded to all characters (R(u g rep) = 2^ind(u) R(rep), checked against direct evaluation on a sample);
(b) the use for 4850: hypothesis needed at the mu27 level; what the identity gives is R(Pc) = 19 R(c) (v2), i.e. P-invariance
    <=> cube.  At the level the identity does force (mod 9) the lemma's conclusion is (2^6 - 1) R = 0 mod 9: vacuous."""
import json, time
import numpy as np
import vlib as V
M = V.M
t0 = time.time()
REPS = [(0, 1), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 10), (1, 13)]
D4 = [lambda j, k: (j, k), lambda j, k: (-j, k), lambda j, k: (j, -k), lambda j, k: (-j, -k),
      lambda j, k: (k, j), lambda j, k: (-k, j), lambda j, k: (k, -j), lambda j, k: (-k, -j)]
CLS = {}
for ci, (a, b) in enumerate(REPS):
    for g in D4:
        x, y = g(a, b)
        for i in range(36):
            u = pow(2, i, M)
            CLS.setdefault((u * x % M, u * y % M), (ci, i))
assert len(CLS) == 1368
NZ = sorted(CLS)
POS = {c: n for n, c in enumerate(NZ)}
CI = np.array([CLS[c][0] for c in NZ]); EI = np.array([pow(2, CLS[c][1], 27) for c in NZ])
def mat_perm(A):
    return np.array([POS[((A[0][0] * j + A[0][1] * k) % M, (A[1][0] * j + A[1][1] * k) % M)] for j, k in NZ])
i2 = pow(2, -1, M)
ROT = ((1, 1), (1, M - 1)); ROTI = ((i2, i2), (i2, M - i2))
def mm(A, B):
    return tuple(tuple(sum(A[i][s] * B[s][j] for s in range(2)) % M for j in range(2)) for i in range(2))
PERM = {}
for g in range(1, 18):
    D = ((1, 0), (0, pow(2, g, M)))
    PERM[(g, 'A')] = mat_perm(D)
    PERM[(g, 'B')] = mat_perm(mm(ROTI, mm(D, ROT)))
# orbit values at the class reps for radius 4
orbs = V.orbits(4)
ov = np.array([[V.eig(V.d4(*o), j, k) for (j, k) in REPS] for o in orbs], dtype=object)
nrules = 1 << len(orbs)
# class values of every rule by XOR-doubling
vals = np.zeros((nrules, 11), dtype=np.int64)
for i in range(len(orbs)):
    blk = 1 << i
    vals[blk:2 * blk] = vals[:blk] ^ np.array(ov[i], dtype=np.int64)
cache = {}
def r(v):
    v = int(v)
    if v not in cache:
        cache[v] = V.res(v)
    return cache[v]
RES = np.array([[r(v) for v in row] for row in vals], dtype=np.int64)
print('class residues of 32768 rules computed, distinct values', len(cache), 'time', round(time.time() - t0, 1), flush=True)
assert list(RES[4850]) == [18, 9, 9, 18, 0, 9, 0, 9, 9, 9, 18]
# sanity: expansion matches direct evaluation for a few rules at all characters
for n in (4850, 1234, 32767):
    L = V.eig_all(V.rule(n, 4))
    full = (RES[n][CI] * EI) % 27
    assert all((V.res(L[c]) if L[c] else -1) == (full[POS[c]] if RES[n][CLS[c][0]] >= 0 else -1) for c in NZ)
print('expansion check ok')
zf = np.all(RES >= 0, axis=1); zf[0] = False
ids = np.flatnonzero(zf)
Rall = (RES[ids][:, CI] * EI[None, :]) % 27          # (rules, 1368)
hits = {}; lemma_ok = True; counter = []
for key, p in PERM.items():
    inv = np.all(Rall[:, p] == Rall, axis=1)
    g = key[0]
    concl = np.all(((2 ** g - 1) * Rall) % 27 == 0, axis=1)
    hits['g=%d,%s' % key] = int(inv.sum())
    if np.any(inv & ~concl):
        lemma_ok = False; counter.append(key)
print('(a) zero-free radius-4 rules:', len(ids), '; rules with mu27 residue fixed by P_g:', hits)
print('    lemma (P_g-invariance => (2^g-1) R = 0 mod 27) holds on every hit:', lemma_ok, counter)
# (b) for 4850 (frame B): P^B_6 invariance at mu27 vs mod 9, cube, and 19-action
R4850 = Rall[list(ids).index(4850)]
pB = PERM[(6, 'B')]
print('(b) 4850: P^B_6-invariant mu27:', bool(np.all(R4850[pB] == R4850)), '; R(Pc) == 19 R(c):', bool(np.all(R4850[pB] == 19 * R4850 % 27)),
      '; cube:', bool(np.all(R4850 % 3 == 0)), '; ninth:', bool(np.all(R4850 % 9 == 0)))
print('    the lemma at the mod-9 level: (2^6 - 1) = 63 = 0 mod 9, so its conclusion is empty:', 63 % 9 == 0)
# among radius-4 rules carrying the hidden symmetry (M0 = Rot^-1 T Rot invariance of R at mu27, off the 4850-frame diagonals),
# is P^B_6-invariance equivalent to cube confinement there?
T = ((10, 0), (0, 26)); M0 = mm(ROTI, mm(T, ROT))
print('    M0 =', M0)
off = np.array([(j + k) % M != 0 and (j - k) % M != 0 for j, k in NZ])
pM0 = mat_perm(M0)
symm = np.all((Rall[:, pM0] == Rall)[:, off], axis=1)
Pinv = np.all((Rall[:, pB] == Rall)[:, off], axis=1)
cube = np.all((Rall % 3 == 0)[:, off], axis=1)
print('    zero-free radius-4 rules with M0-invariant mu27 residue off the diagonals:', int(symm.sum()),
      '; among them P^B_6-invariant:', int((symm & Pinv).sum()), '; cube-confined off diagonals:', int((symm & cube).sum()),
      '; P-inv <=> cube on all of them:', bool(np.all(Pinv[symm] == cube[symm])))
json.dump(dict(hits=hits, lemma_ok=lemma_ok, n_zero_free=int(len(ids)), n_M0_symmetric=int(symm.sum()),
               n_M0_sym_Pinv=int((symm & Pinv).sum()), n_M0_sym_cube=int((symm & cube).sum())), open('v3_claim2.json', 'w'), indent=1)
print('time', round(time.time() - t0, 1))
