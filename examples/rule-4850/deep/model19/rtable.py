"""The mu3-exponent r = v27/9 of 10491524 (and 4850 via the diagonal frame) as a function of the
sextic classes (ind(alpha) mod 6, ind(beta) mod 6), ind = log_2 mod 37."""
import numpy as np
import ff18 as F
import vec

for n, r in [(10491524, 6), (20982139, 6), (178279803, 6), (8438150, 6)]:
    V = vec.values([n], r)[0]
    v = vec.v27(V)
    tab = {}
    ok = True
    for a in range(1, 37):
        for b in range(1, 37):
            x = v[vec.red(a), vec.red(b)]
            if x < 0:
                continue
            key = (F.ind37(a) % 6, F.ind37(b) % 6)
            tab.setdefault(key, set()).add(int(x) // 9 if x % 9 == 0 else ('x', int(x)))
    R = np.full((6, 6), -1)
    for (p, q), s in tab.items():
        if len(s) == 1:
            R[p, q] = list(s)[0]
        else:
            ok = False
    print(n, 'well defined on sextic classes:', ok)
    print(R)
# 4850 in the diagonal frame: alpha = (j+k)/2, beta = (j-k)/2
V = vec.values([4850], 4)[0]
v = vec.v27(V)
R = np.full((6, 6), -1); ok = True
inv2 = pow(2, -1, 37)
for al in range(1, 37):
    for be in range(1, 37):
        j, k = (al + be) % 37, (al - be) % 37
        x = v[vec.red(j), vec.red(k)]
        key = (F.ind37(al) % 6, F.ind37(be) % 6)
        if R[key] == -1:
            R[key] = x // 9
        elif R[key] != x // 9:
            ok = False
print('4850 in diagonal coordinates (alpha, beta), j = alpha+beta, k = alpha-beta: well defined:', ok)
print(R)
