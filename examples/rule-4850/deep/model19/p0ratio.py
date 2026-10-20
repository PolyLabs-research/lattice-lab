"""P0 for 10491524 & co: R(j,k) = lambda(27j, k) / lambda(j, k).  Components."""
import numpy as np
import ff18 as F
import vec

for n, r in [(10491524, 6), (20982139, 6), (178279803, 6), (7, 4), (41, 4), (4850, 4)]:
    V = vec.values([n], r)[0]
    L = vec.logs(V)
    i27, i19 = vec._consts()
    J = list(range(1, 19))
    Rlog = (L[[vec.IDX27[j] for j in J], :][:, 1:] - L[J, :][:, 1:]) % F.N
    v = (Rlog % 27) * i27 % 27
    s = (Rlog % 19) * i19 % 19
    inF512 = (Rlog % 513 == 0)
    print(n, 'R v27 values', sorted(set(v.ravel().tolist())), ' R in F(2^9) everywhere:', bool(inF512.all()), ' frac', inF512.mean())
    print('   s19(R)(j, k) for j=1..6 (rows), k=1..8:', s[:6, :8].tolist())
