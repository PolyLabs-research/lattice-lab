"""Is z = Y/W (step 9's ninth-level pair at 37) a value of rule 90 (z = t_n) or a known ninth-power unit argument?
Then 1 + z = 1 + t_n is a ninth power (rule 150 at 37) and X = W(1 + z) inherits W's class."""
from collections import Counter
import famlib as L
from sizes_engine import Size
from step4_lambda import W_values
m = 37
S = Size(m); F = S.F
Wv, u = W_values(S, 16)
tset = {F.t[n]: n for n in range(1, m)}
tpow = {}
for n in range(1, m):
    for k in range(36):
        tpow.setdefault(F.pow(F.t[n], 2 ** k), (n, k))
hits = Counter(); lin = {}
for a in range(1, m):
    for b in range(1, m):
        W = Wv[a, b]
        Y = Wv[7 * a % m, 21 * b % m] ^ Wv[21 * a % m, 7 * b % m]
        z = F.mul(Y, F.inv(W))
        hits['z = t_n'] += z in tset
        hits['z+1 = t_n'] += (z ^ 1) in tset
        hits['z in {t_n^2^k}'] += z in tpow
        if z in tset:
            lin[(a, b)] = tset[z]
print(hits, 'of', (m - 1) ** 2)
# is n a linear form +-(x a + y b)?
forms = Counter()
for (a, b), n in lin.items():
    for x in range(m):
        for y in range(m):
            if (x * a + y * b - n) % m == 0 or (x * a + y * b + n) % m == 0:
                forms[(x, y)] += 1
print('best linear forms n = +-(x al + y be):', forms.most_common(6), 'of', len(lin))
