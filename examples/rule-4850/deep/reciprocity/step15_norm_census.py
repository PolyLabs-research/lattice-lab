"""Step 15: the F_64-norm census.  For every symmetric rule of radius <= 6 (2^28 rules), the vector of
N_{F(2^18)/F_64}(lambda) at the 11 classes, encoded as log mod 63 (255 for a zero eigenvalue).
Two rules with equal vectors have eigenvalue ratios in mu_4161 = (F*)^63 everywhere: ninth powers
(and seventh powers), so one is ninth-power confined iff the other is.  We list every rule whose
vector equals that of 4850, of 10491524, or of any other target, and count how many vector-classes
of size > 1 contain a ninth-power-confined rule."""
import sys, time, json
import numpy as np
from rlib import *
from fulllog import log_table, CLASS_K, class_value, family_values

RAD = 6
LOG = log_table()
LOG63 = np.full(1 << 18, 255, dtype=np.uint8)
LOG63[1:] = (LOG[1:] % 63).astype(np.uint8)

def vec(n, r):
    F = rule_F(n, r)
    return np.array([LOG63[class_value(F, k)] for k in CLASS_K], dtype=np.uint8)

targets = {n: vec(n, r) for n, r in [(4850, 4), (10491524, 6), (482758, 5), (8438150, 6), (43250486, 6)]}
for n, v in targets.items():
    print('target', n, list(v))

orbs = orbits(RAD)
nlow = 20
t0 = time.time()
lowF = family_values(5)  # radius 5 = first 21 orbits; we need exactly nlow orbits for the low table
# build low table over the first nlow orbits and high values over the rest
vals_orb = []
for o in orbs:
    F = orbit_F(o)
    vals_orb.append([class_value(F, k) for k in CLASS_K])
vals_orb = np.array(vals_orb, dtype=np.uint32)  # (28, 11)
low = np.zeros((11, 1 << nlow), dtype=np.uint32)
for i in range(nlow):
    low[:, 1 << i: 2 << i] = low[:, : 1 << i] ^ vals_orb[i][:, None]
nhigh = len(orbs) - nlow
high = np.zeros((11, 1 << nhigh), dtype=np.uint32)
for i in range(nhigh):
    high[:, 1 << i: 2 << i] = high[:, : 1 << i] ^ vals_orb[nlow + i][:, None]
print('tables built', round(time.time() - t0, 1), 's')

matches = {n: [] for n in targets}
ninth_count = 0
for h in range(1 << nhigh):
    masks = {n: np.ones(1 << nlow, dtype=bool) for n in targets}
    ninth = np.ones(1 << nlow, dtype=bool)
    for c in range(11):
        l = LOG63[low[c] ^ high[c, h]]
        ninth &= (l == 255) | (l % 9 == 0)
        for n, v in targets.items():
            masks[n] &= (l == v[c])
    ninth_count += int(ninth.sum())
    for n in targets:
        idx = np.flatnonzero(masks[n])
        matches[n] += [int((h << nlow) | i) for i in idx]
print('scan done', round(time.time() - t0, 1), 's; ninth-power-confined rules (incl. 0):', ninth_count)
for n in targets:
    print(f'rules with the same F_64-norm vector as {n}:', matches[n])
json.dump({str(n): matches[n] for n in targets}, open('step15_norm_census.json', 'w'))
