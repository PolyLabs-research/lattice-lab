"""check-chain c4: end to end on rule 4850 at 37, own field / own generator.

* rule 4850 = union of the D4-orbits selected by its bits, orbits (a,b), 0 <= b <= a <= 4, in sorted order
  (rebuilt here from the dossier's description, compared with the dossier's orbit list).
* every nonzero character: lambda != 0 and lambda^29127 = 1 (ninth power).
* class logs at the census representatives (0,1), (1,k), k in 1,2,3,4,5,6,7,8,10,13:
  log mod 27 (via lambda^9709 against g^9709) and log mod 63 (via N(lambda) = lambda^4161 against N(g)),
  with g a generator of F(2^18)* in OUR model.  The generator and zeta are ours, so the dossier's logs mod 27 can
  only agree up to a global unit u mod 27; on values in {0, 9, 18} that is identity or the swap 9 <-> 18.
* the chain's prediction at each class: N(lambda) = (eta(al) eta(be))^(4n(d)-2) off the diagonal, eta(j)^66 on it,
  hence log mod 63 predicted (so log mod 9 = 0); log mod 27 itself is NOT determined by the norm to F64.
"""
import json
import functools
import clib
from clib import p

F = clib.GF36()
z = [F.pow(F.zeta, i) for i in range(p)]
t = [z[i] ^ z[(-i) % p] for i in range(p)]
mu6 = clib.mu(6)
L2 = clib.LOG2
eta = lambda x: functools.reduce(lambda a, b: a ^ b, (z[x * u % p] for u in mu6), 0)
n_claim = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
out = {}

orbs = sorted((a, b) for a in range(5) for b in range(a + 1))
sel = [orbs[i] for i in range(len(orbs)) if 4850 >> i & 1]
out['orbits selected by the bits of 4850'] = sel
out['matches dossier orbit list'] = sel == clib.RULE4850_ORBITS
pts = clib.rule_points(sel)
def lam(j, k):
    v = 0
    for a, b in pts:
        v ^= z[(a * j + b * k) % p]
    return v

allc = [(j, k) for j in range(p) for k in range(p) if (j, k) != (0, 0)]
vals = {c: lam(*c) for c in allc}
out['nonzero characters'] = len(allc)
out['zero eigenvalues'] = sum(1 for v in vals.values() if v == 0)
out['all in F(2^18)'] = all(F.in_sub(v, 18) for v in vals.values())
out['all ninth powers (lambda^29127 = 1)'] = all(F.pow(v, 29127) == 1 for v in vals.values() if v)
out['number that are 27th powers'] = sum(1 for v in vals.values() if v and F.pow(v, 9709) == 1)

g = F.g18
g27 = F.pow(g, 9709)
tab27 = {}
x = 1
for i in range(27):
    tab27[x] = i
    x = F.mul(x, g27)
Ng = F.norm_K_k(g)
tab63 = {}
x = 1
for i in range(63):
    tab63[x] = i
    x = F.mul(x, Ng)
assert len(tab27) == 27 and len(tab63) == 63
log27 = lambda v: tab27[F.pow(v, 9709)]
log63 = lambda v: tab63[F.norm_K_k(v)]

reps = [(0, 1)] + [(1, k) for k in (1, 2, 3, 4, 5, 6, 7, 8, 10, 13)]
dossier27 = [18, 9, 9, 18, 0, 9, 0, 9, 9, 9, 18]
h = pow(2, -1, p)
rows = []
for (j, k), dl in zip(reps, dossier27):
    v = vals[j, k]
    al, be = (j + k) * h % p, (j - k) * h % p
    if al and be:
        d = (L2[be] - L2[al]) % 6
        pred = F.pow(F.mul(eta(al), eta(be)), 4 * n_claim[d] - 2)
        kind = 'off-diagonal d=%d' % d
    else:
        d = None
        pred = F.pow(eta(j), 66)
        kind = 'diagonal (be=0 or al=0)'
    rows.append(dict(rep=(j, k), frame=kind, al=al, be=be, log27=log27(v), log63=log63(v),
                     pred_log63=tab63[pred], log9=log27(v) % 9, dossier27=dl))
for r in rows:
    print(r)
mine = [r['log27'] for r in rows]
swap = {0: 0, 9: 18, 18: 9}
out['class rows'] = rows
out['all class logs mod 27 in {0,9,18}'] = all(v in (0, 9, 18) for v in mine)
out['predicted log mod 63 == actual at every class'] = all(r['log63'] == r['pred_log63'] for r in rows)
out['ours == dossier (mod 27) exactly'] = mine == dossier27
out['ours == dossier (mod 27) after global swap 9<->18'] = [swap[v] for v in mine] == dossier27
# the global unit relating our (zeta, g) to theirs must be the same at every class: check via all units mod 27
units = [u for u in range(27) if u % 3]
out['units u mod 27 with u*ours == dossier at all 11 classes'] = [u for u in units if [u * v % 27 for v in mine] == dossier27]
# constancy of ninth-power-ness and of log mod 27 up to the Frobenius doubling on each line
def cls_of(j, k):
    if j == 0 or k == 0:
        return (0, 1)
    r = k * pow(j, -1, p) % p
    orb = {r, -r % p, pow(r, -1, p), -pow(r, -1, p) % p}
    return (1, min(orb))
by = {}
for c, v in vals.items():
    by.setdefault(cls_of(*c), set()).add(log27(v) % 9)
out['log mod 9 over all characters of each class'] = {str(k): sorted(s) for k, s in by.items()}
json.dump(out, open('c4_endtoend.json', 'w'), indent=1, default=str)
for k_, v_ in out.items():
    if k_ != 'class rows':
        print(k_, ':', v_)
