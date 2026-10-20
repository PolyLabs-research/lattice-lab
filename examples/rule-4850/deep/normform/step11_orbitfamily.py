"""Step 11: the shape family.  For every <D4, T>-orbit O of off-axis points of (Z/37)^2
(T = diag(10, 26), the anti-diagonal mu3 / mu6 dilation), G_O = sum_{c in O} x^c (lifted to centred
representatives; divisible by pi = (x+1/x)(y+1/y) as a Laurent polynomial since O avoids the axes).
Test, off the axes, whether G_O * pi^j is ninth-confined for j in {-1, 0, 1, 2}; j = -1 is the rule
f_O = G_O / pi (the shape of 10491524, 20982139, 178279803).  Prediction from the core statement
C: W pi^2 ninth-confined, where W = eigenvalue of the 12-point orbit of (1, 1):
   12-point orbits are dilations: W_O = W^(2^k) (up to Frobenius^6 conjugation), and
   W_O pi^j is ninth-confined  <=>  j = 2^(k+1) (mod 3).
24-point orbits: no prediction (chance: ~3 free classes)."""
import json, collections
import numpy as np
import nf

m = 37
V = nf.V27()
J, K = nf.grid()
offax = (J != 0) & (K != 0)
mu6 = [u for u in range(1, m) if pow(u, 6, m) == 1]
def Torbit(p, q):
    out = set()
    for c in mu6:
        ci = pow(c, -1, m)
        for e in (1, -1):
            x, y = c * p % m, e * ci * q % m
            out.add((x, y)); out.add((y, x))
    return frozenset(out)
orbs = sorted({Torbit(p, q) for p in range(1, m) for q in range(1, m)}, key=lambda o: (len(o), min(o)))
print('number of <D4,T>-orbits off the axes:', len(orbs), ' sizes:', collections.Counter(len(o) for o in orbs))
pi = nf.vmul(nf.vt(J), nf.vt(K))
pinv = nf.vinv(np.where(pi == 0, 1, pi))
def eig(O):
    # D4-orbits (p, q) with 0 < q <= p contained in O (O is D4-invariant): use orbit values
    seen = set(); v = np.zeros(J.shape, dtype=np.int64)
    for (x, y) in O:
        c = (min(x, m - x), min(y, m - y))
        o = (max(c), min(c))
        if o in seen:
            continue
        seen.add(o)
        v ^= nf.vorbit(o)
    return v
lg2 = {pow(2, k, m): k for k in range(36)}
# W itself
W = eig(Torbit(1, 1))
assert np.all(W[~offax] == 0)
vW = V[W[offax]]; vpi = V[pi[offax]]
core = np.all((vW + 2 * vpi) % 9 == 0)
print('core statement C (W pi^2 ninth at every off-axis character):', bool(core))
rows = []
for O in orbs:
    G = eig(O)
    rec = {'orbit_rep': min(O), 'size': len(O)}
    if len(O) == 12:
        p, q = min(O)
        # q = p c with c in mu6; W_O(al,be) = W(p al, p c be); write p c' with c'^2 = c (c' in mu6) -> 2^k
        c = q * pow(p, -1, m) % m
        if pow(c, 3, m) != 1:
            c = m - c   # W(al, -be) = W(al, be)
        cp = next(x for x in (1, 10, 26) if x * x % m == c)
        # W(p al, p c be) = W(p c' al', ...) ; k = log2(p c') mod 36 (sign irrelevant)
        k = lg2[p * cp % m] if p * cp % m in lg2 else None
        rec['k'] = k
    for j in (-1, 0, 1, 2):
        u = pinv if j == -1 else nf.vpow(pi, j) if j > 0 else np.ones_like(pi)
        val = nf.vmul(G, u)[offax]
        vv = V[val]
        nz = vv >= 0
        rec[f'ninth_j{j}'] = bool(np.all(vv[nz] % 9 == 0))
        rec[f'zeros_j{j}'] = int((~nz).sum())
        if len(O) == 12:
            rec[f'pred_j{j}'] = (j - pow(2, rec['k'] + 1)) % 3 == 0
    rows.append(rec)
# summaries
for size in (12, 24):
    sub = [r for r in rows if r['size'] == size]
    for j in (-1, 0, 1, 2):
        conf = sum(r[f'ninth_j{j}'] for r in sub)
        line = f'size {size}: j = {j:2d}: ninth-confined {conf} / {len(sub)}'
        if size == 12:
            agree = sum(r[f'ninth_j{j}'] == r[f'pred_j{j}'] for r in sub)
            line += f'   prediction agrees on {agree} / {len(sub)}'
        print(line)
print('size-12 orbits (rep, k, confined for j=-1..2):', [(r['orbit_rep'], r['k'], [int(r[f"ninth_j{j}"]) for j in (-1, 0, 1, 2)]) for r in rows if r['size'] == 12])
print('size-24 orbits confined for some j:', [(r['orbit_rep'], [int(r[f"ninth_j{j}"]) for j in (-1, 0, 1, 2)]) for r in rows if r['size'] == 24 and any(r[f"ninth_j{j}"] for j in (-1, 0, 1, 2))])
json.dump(rows, open('step11_orbitfamily.json', 'w'), indent=1)
