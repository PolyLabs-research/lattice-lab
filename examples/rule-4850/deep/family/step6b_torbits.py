"""Step 6b. Same as step 6, but merging the free classes into orbits of the 60-degree rotation T (al, be) -> (u al, be/u),
which fixes W.  Reports, per size: number of T-orbits of free classes (the number of independent conditions for the core
statement), how many are entirely C(1) / C(2), and whether C is constant on T-orbits (T-compatibility)."""
import json, sys
import numpy as np
import famlib as L
from sizes_engine import Size

ms = [int(x) for x in sys.argv[1:]] or [13, 37, 61, 97, 109, 181, 193, 241, 313, 349, 373, 111, 133, 169, 247, 259]
out = []
for m in ms:
    S = Size(m)
    if not S.A or not S.agen:
        continue
    A, Q = S.A, 3 ** S.A
    for r in S.roots:
        vW, u = S.W_table(r)
        ui = pow(u, -1, m)
        mu6 = {pow(u, i, m) for i in range(6)}
        cls = {}
        reps = []
        for al in range(1, m):
            for be in range(1, m):
                if (al, be) in cls:
                    continue
                orb = set(); st = [(al, be)]
                while st:
                    c = st.pop()
                    if c in orb:
                        continue
                    orb.add(c); x, y = c
                    for c2 in ((2 * x % m, 2 * y % m), (-x % m, y), (x, -y % m), (y, x)):
                        if c2 not in orb:
                            st.append(c2)
                k = len(reps); reps.append((al, be))
                for c in orb:
                    cls[c] = k
        info = []
        for k, (al, be) in enumerate(reps):
            ac = int(S.a[al, be])
            ratio = be * pow(al, -1, m) % m if np.gcd(al, m) == 1 else None
            if vW[al, be] < 0 or ac == 0 or (ratio is not None and ratio in mu6):
                info.append(None); continue
            Lc = (int(vW[al, be]) - int(S.vt[al]) - int(S.vt[be])) % Q
            info.append(L.v3(Lc, A) - (A - ac))
        # union-find over T
        par = list(range(len(reps)))
        def find(x):
            while par[x] != x:
                par[x] = par[par[x]]; x = par[x]
            return x
        for k, (al, be) in enumerate(reps):
            k2 = cls[(u * al % m, be * ui % m)]
            a, b = find(k), find(k2)
            if a != b:
                par[a] = b
        groups = {}
        for k in range(len(reps)):
            if info[k] is not None:
                groups.setdefault(find(k), []).append(info[k])
        n = len(groups)
        c1 = sum(all(x >= 1 for x in g) for g in groups.values())
        c2 = sum(all(x >= 2 for x in g) for g in groups.values())
        const1 = sum(len({x >= 1 for x in g}) == 1 for g in groups.values())
        rec = dict(m=m, r=r, A=A, index_of_2=S.index2, free_classes=sum(len(g) for g in groups.values()), T_orbits=n,
                   T_orbits_C1=c1, T_orbits_C2=c2, C1_constant_on_T_orbits=const1)
        out.append(rec); print(rec, flush=True)
json.dump(out, open('step6b_torbits.json', 'w'), indent=1)
