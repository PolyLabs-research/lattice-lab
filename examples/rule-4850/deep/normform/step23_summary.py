"""Step 23: the class-by-class account, in census order, for f0 = h/pi (T frame), 10491524 (T frame) and
4850 (its own frame, via (x, y) -> (xy, x/y), i.e. lambda_4850(j, k) = lambda_10491524((j+k)/2, (j-k)/2)),
plus the relatives 482758, 8438150, 43250486 as 4850 times ninth-power units, and the axis polynomials.
Types (T frame, character (al, be), d = log2(be/al) mod 6 up to sign):
   axis    : al be = 0 (f0: one-variable polynomial; the rules: cyclotomic, see below)
   d=0     : W(al, al) = t_al^2, f0 = 1 exactly (and W(al, 10al) etc. by T-symmetry)
   d=3     : fixed point of swap o (scalar 8) o (mu6 x mu6): forced 27th power
   d=+-2   : 'cancellation lines', W = t_x t_y t_z exactly (Legendre bookkeeping)
   d=+-1   : the residual condition (no structural reason found)"""
import json
import sympy as sp
import nf

m = 37
lg2 = {pow(2, k, m): k for k in range(36)}
def dtype(al, be):
    al %= m; be %= m
    if al == 0 or be == 0:
        return 'axis'
    d = (lg2[be] - lg2[al]) % 6
    return {0: 'd=0', 3: 'd=3', 1: 'd=+-1', 5: 'd=+-1', 2: 'd=+-2', 4: 'd=+-2'}[d]
inv2 = pow(2, -1, m)
rows = []
f0 = nf.vrule(24583649143032555859, 10)
r1 = nf.vrule(10491524, 6); r0 = nf.vrule(4850, 4)
V = nf.V27()
for (j, k) in nf.CLASSES:
    tT = dtype(j, k)                         # type of this class for rules in the T frame
    al, be = (j + k) * inv2 % m, (j - k) * inv2 % m
    t4850 = dtype(al, be)                    # type of 4850's class (j,k) via the rotation
    # consistency: lambda_4850(j,k) = lambda_10491524(al, be)
    assert r0[nf.cls_index(j, k)] == r1[nf.cls_index(al, be)]
    rows.append(dict(cls=(j, k), type_T_frame=tT, v27_f0=int(V[f0[nf.cls_index(j, k)]]), v27_10491524=int(V[r1[nf.cls_index(j, k)]]),
                     type_4850_frame=t4850, v27_4850=int(V[r0[nf.cls_index(j, k)]])))
print('%-8s %-8s %6s %10s   |  %-8s %6s' % ('class', 'T-type', 'f0', '10491524', '4850type', '4850'))
for r in rows:
    print('%-8s %-8s %6d %10d   |  %-8s %6d' % (r['cls'], r['type_T_frame'], r['v27_f0'], r['v27_10491524'], r['type_4850_frame'], r['v27_4850']))
# relatives of 4850 as unit multiples
J, K = nf.grid(); a = nf.vt(J); b = nf.vt(K)
units = {482758: nf.vmul(1 ^ a, 1 ^ b),                                  # (1+a)(1+b)
         8438150: nf.vmul(1 ^ nf.vt(J + K), 1 ^ nf.vt(J - K)),           # Phi3(xy)Phi3(x/y) ~ (1 + t_{j+k})(1 + t_{j-k}) up to monomials
         43250486: nf.vmul(nf.vpow(1 ^ a, 2), nf.vpow(1 ^ b, 2))}        # Phi3(x)^2 Phi3(y)^2 ~ (1+a)^2(1+b)^2
for n, u in units.items():
    r = nf.vrule(n, 5 if n == 482758 else 6)
    same = all(r[i] == nf.kmul(int(r0[i]), int(u[i])) for i in range(len(J)))
    uninth = all(V[x] % 9 == 0 for x in u if x)
    print(n, '= 4850 * unit at every character:', same, ';  unit values ninth powers:', uninth)
# axis polynomials of the three rules and of f0 (one-variable restrictions a = 0), factored
t = sp.Symbol('t')
axis = {'10491524': t ** 2 * (1 + t + t ** 2) ** 2, '20982139': 1 + t ** 2 + t ** 3, '178279803': t ** 6 + t ** 4 + t ** 3 + 1, 'f0': 1 + t + t ** 5 + t ** 9}
for name, poly in axis.items():
    print('axis', name, ':', sp.factor_list(sp.expand(poly), modulus=2))
json.dump(rows, open('step23_summary.json', 'w'), indent=1)
