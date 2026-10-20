"""Step 7: the rules of radius <= 5 whose v27 function is exactly M0- or T-invariant (step 5):
their class logs, zeros, ninth-confinement, and whether a known mechanism explains them
(atlas3.predict = mechanisms 1-4; pilot 7's condition = 5-8)."""
import sys, os, json, time
import numpy as np
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
sys.path.insert(0, '/home/user/lattice-lab/examples/linear-atlas-3')
from calib_lib import sym_mask, M0, T, census, ZERO
import atlas3
here = os.getcwd()
os.chdir('/home/user/pilot-37c-round2'); sys.path.insert(0, '/home/user/pilot-37c-round2')
import mechanism
os.chdir(here)
out = []
for radius in (4, 5):
    logs = census.class_logs(radius)
    nine = census.confined(logs, 9)
    for name, M in (('M0', M0), ('T', T)):
        s = sym_mask(logs, M); s[0] = False
        for n in np.flatnonzero(s):
            n = int(n)
            if radius == 5 and n < (1 << 15):
                continue  # already listed at radius 4
            f = census.rule(n, radius)
            cl = [int(x) for x in logs[:, n]]
            pv, why = atlas3.predict(f, 37)
            try:
                q = mechanism.condition(f, 37)
            except Exception as ex:
                q = 'err:' + str(ex)[:40]
            row = dict(rule=n, radius=radius, sym=name, logs27=cl, zeros=sum(x == ZERO for x in cl),
                       ninth=bool(nine[n]), atlas=[pv, why], atlas_ninth=(pv is not None and 29127 % pv == 0),
                       pilot_q=q, terms=len(f))
            out.append(row)
            print(row, flush=True)
    del logs
json.dump(out, open('step7_symrules.json', 'w'), indent=1)
