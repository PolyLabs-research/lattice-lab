"""Explore: at 37, X = W(c) + Y(c), Y(c) = W(7al, 21be) + W(21al, 7be) is ninth-confined relative to pi (step 9).
Look for the relation: is Y in F(2^9)?  Y/W?  X in F(2^9)*W?  X^? """
import numpy as np
import famlib as L
from sizes_engine import Size
from step4_lambda import W_values
m = 37
S = Size(m)
F = S.F
Wv, u = W_values(S, 16)
def inF9(x): return F.pow(x, 512) == x if x else True
def frob9(x): return F.pow(x, 512)
cnt = dict(Y_in_F9=0, X_in_F9=0, YoverW_in_F9=0, XoverW_in_F9=0, total=0, X_eq_Wbar=0, Y_eq_Wbar=0, X_eq_W2k=0)
res = []
for a in range(1, m):
    for b in range(1, m):
        W = Wv[a, b]
        Y = Wv[7 * a % m, 21 * b % m] ^ Wv[21 * a % m, 7 * b % m]
        X = W ^ Y
        cnt['total'] += 1
        cnt['Y_in_F9'] += inF9(Y)
        cnt['X_in_F9'] += inF9(X)
        cnt['YoverW_in_F9'] += inF9(F.mul(Y, F.inv(W)))
        cnt['XoverW_in_F9'] += inF9(F.mul(X, F.inv(W)))
        cnt['X_eq_Wbar'] += X == frob9(W)
        cnt['Y_eq_Wbar'] += Y == frob9(W)
        cnt['X_eq_W2k'] += any(X == F.pow(W, 2 ** k) for k in range(36))
print(cnt)
# which Frobenius power / dilation of W is X?  test X(c) == W(lam al, mu be) for lam, mu
hits = []
for lam in range(1, m):
    for mu in range(1, m):
        ok = True
        for a, b in ((1, 2), (1, 3), (2, 5), (1, 1), (3, 7)):
            W = Wv[a, b]; Y = Wv[7 * a % m, 21 * b % m] ^ Wv[21 * a % m, 7 * b % m]
            if (W ^ Y) != Wv[lam * a % m, mu * b % m]:
                ok = False; break
        if ok:
            hits.append((lam, mu))
print('X(c) = W(lam al, mu be) for (lam, mu) in', hits[:20])
