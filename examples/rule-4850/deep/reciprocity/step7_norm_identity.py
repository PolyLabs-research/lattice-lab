"""Step 7: the norm form of the ninth-power condition, and an exact group-ring identity.

At 37, lambda in F(2^18)* is a ninth power iff N_{F(2^18)/F_64}(lambda) = lambda^(1+64+4096) lies in
F_8 (mu_7), because the ninth-power symbol is lambda^29127 = N(lambda)^7.  On the group ring
F_2[Z_37^2], lambda^64 is the dilation by 64 = 27 = -10, so the norm is the group-ring element
n(f) = f * f(x^10, y^10) * f(x^26, y^26)   (10 has order 3 mod 37; f symmetric so -1 is harmless)
and f is ninth-power confined at 37 iff n(f) is invariant under the dilation by 8 (n(f)^8 = n(f))
on the nonzero characters.  Here: compute n(f) for the targets; test n(f)(x^8,y^8) == n(f);
test the identities n(20982139) == n(10491524) == n(178279803) in F_2[Z_37^2]."""
import numpy as np
from rlib import rule_points
from gring import *

def rp(n):
    r = 4 if n < 2**15 else (5 if n < 2**21 else 6)
    return rule_points(n, r)

R = {n: elem(rp(n)) for n in (4850, 10491524, 20982139, 178279803, 482758, 8438150, 43250486)}
N = {n: norm10(a) for n, a in R.items()}
for n, a in N.items():
    inv8 = np.array_equal(dil(a, 8), a)
    # the trivial character: value of n(f) at (1,1) is the parity of its support
    print(f'rule {n}: |f| = {int(R[n].sum())}, |n(f)| = {int(a.sum())}, n(f) invariant under [8]: {inv8}')
print('n(20982139) == n(10491524):', np.array_equal(N[20982139], N[10491524]))
print('n(178279803) == n(10491524):', np.array_equal(N[178279803], N[10491524]))
d = N[20982139] ^ N[10491524]
print('|n(20982139) - n(10491524)| =', int(d.sum()))
