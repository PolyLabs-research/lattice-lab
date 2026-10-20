"""Step 6. Why only 13 and 37?  Class-by-class statistics of the core statement
   C(i):  W(c) / (t_al t_be)  is a 3^i-th power in its own field F(2^e_c)
over the classes of off-diagonal characters (orbits of <Frobenius, D4>; W/pi is D4-invariant and Frobenius-equivariant).
'forced' classes: beta/alpha in mu6 (there W = t_x^2 for a single x, an exact identity), and classes whose field has no
3-torsion (a_c = 0: vacuous).  For every other ('free') class we record whether C(1) and C(2) hold.  A size where the
family has a confined member needs C at every class (with the right exponent; step 3 tried W = pi^n for |n| <= 6);
the fraction satisfied at the free classes is the chance calibration: about 1/3 for C(1), 1/9 for C(2) if random."""
import json, sys
import numpy as np
import famlib as L
from sizes_engine import Size, v3arr

ms = [int(x) for x in sys.argv[1:]] or [13, 37, 61, 97, 109, 181, 193, 241, 313, 349, 373, 111, 133, 247, 259, 169]
out = []
for m in ms:
    S = Size(m)
    if not S.A or not S.agen:
        continue
    A, Q = S.A, 3 ** S.A
    for r in S.roots:
        vW, u = S.W_table(r)
        mu6 = {pow(u, i, m) for i in range(6)}
        seen = set()
        stats = dict(free=0, free_C1=0, free_C2=0, free_C2_possible=0, forced=0, forced_C1=0, vacuous=0, Wzero=0)
        free_list = []
        for al in range(1, m):
            for be in range(1, m):
                if (al, be) in seen:
                    continue
                orb = set()
                st = [(al, be)]
                while st:
                    c = st.pop()
                    if c in orb:
                        continue
                    orb.add(c)
                    x, y = c
                    for c2 in ((2 * x % m, 2 * y % m), (-x % m, y), (x, -y % m), (y, x)):
                        if c2 not in orb:
                            st.append(c2)
                seen |= orb
                ac = int(S.a[al, be])
                if vW[al, be] < 0:
                    stats['Wzero'] += 1
                    continue
                Lc = (int(vW[al, be]) - int(S.vt[al]) - int(S.vt[be])) % Q
                rel = L.v3(Lc, A) - (A - ac)       # relative level: 0 = not a cube in its field, ...
                if ac == 0:
                    stats['vacuous'] += 1
                    continue
                ratio = be * pow(al, -1, m) % m if np.gcd(al, m) == 1 else None
                if ratio is not None and ratio in mu6:
                    stats['forced'] += 1
                    stats['forced_C1'] += rel >= 1
                    continue
                stats['free'] += 1
                stats['free_C1'] += rel >= 1
                if ac >= 2:
                    stats['free_C2_possible'] += 1
                    stats['free_C2'] += rel >= 2
                free_list.append(((al, be), ac, rel))
        rec = dict(m=m, r=r, A=A, agen=S.agen, index_of_2=S.index2, t_level=S.agen - int(max(A - L.v3(int(S.vt[j]), A) for j in range(1, m))), **stats)
        rec['free_examples'] = free_list[:12]
        out.append(rec)
        print({k: v for k, v in rec.items() if k != 'free_examples'}, flush=True)
json.dump(out, open('step6_classes.json', 'w'), indent=1)
