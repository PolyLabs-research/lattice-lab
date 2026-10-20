"""Step 3: twisted stabilizer Gamma of v27(lambda) for 4850, its rotation 10491524, the two radius-6
relatives, and random rules; and which classes are forced by it."""
import json, random, sys, time
import numpy as np
import nf
from symlib import *

def info(n, r):
    v = vfun(nf.vrule(n, r))
    t0 = time.time()
    st = stabilizer(v)
    k0 = [g for g, kk in st if kk == 0]
    return v, st, k0

res = {}
for n, r in [(4850, 4), (10491524, 6), (20982139, 6), (178279803, 6), (482758, 5), (8438150, 6), (43250486, 6)]:
    v, st, k0 = info(n, r)
    ks = sorted({kk for g, kk in st})
    res[n] = dict(order=len(st), mult_zero=len(k0), multipliers=ks)
    print(n, '|Gamma| =', len(st), ' #k=0:', len(k0), ' multipliers:', ks, flush=True)
    if n in (4850, 10491524):
        nontriv = [g for g in k0 if not (g[0][1] == 0 and g[1][0] == 0 or g[0][0] == 0 and g[1][1] == 0)]
        print('   non-monomial k=0 elements (first 8):', nontriv[:8])
random.seed(1)
cnt = []
for trial in range(20):
    n = random.randrange(1, 1 << 15)
    v, st, k0 = info(n, 4)
    cnt.append((n, len(st), len(k0)))
print('random radius-4 rules (n, |Gamma|, #k=0):', cnt)
json.dump(dict(res=res, random=cnt), open('step3_stab.json', 'w'), indent=1)
