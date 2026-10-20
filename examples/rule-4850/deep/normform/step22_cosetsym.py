"""Step 22: affine symmetries of the coset function n(i, j) = N_{K/F64}(W(2^i, 2^j)) on (Z/6)^2 (and of
N(f0)), i.e. g(i, j) = (a i + b j + c, a' i + b' j + c') with n(g(i,j)) = n(i,j)^(2^k) for all i, j.
Known: Frobenius (i+1, j+1; k = 1), swap.  Any others (which could transport the forced class d = 3 or the
explained classes d = 0, +-2 to the remaining class d = +-1)?"""
import itertools, json
import nf
m = 37
T = nf.tvec()
mu3 = [1, 10, 26]
def W(al, be):
    v = 0
    for u in mu3:
        v ^= nf.kmul(T[u * al % m], T[be * pow(u, -1, m) % m])
    return v
def NW(al, be):
    v = 1
    for c in mu3:
        v = nf.kmul(v, W(al, c * be % m))
    return v
n = {(i, j): NW(pow(2, i, m), pow(2, j, m)) for i in range(6) for j in range(6)}
eta = lambda x: nf.kmul(1, 1)
def Nf0(i, j):
    ea = 0; eb = 0
    for u in mu3:
        ea ^= T[pow(2, i, m) * u % m]; eb ^= T[pow(2, j, m) * u % m]
    return nf.kmul(n[(i, j)], nf.kinv(nf.kpow(nf.kmul(ea, eb), 2)))
nf0 = {(i, j): Nf0(i, j) for i in range(6) for j in range(6)}
for name, fn in (('N(W)', n), ('N(f0)', nf0)):
    syms = []
    for a, b, a2, b2 in itertools.product(range(6), repeat=4):
        if (a * b2 - b * a2) % 2 == 0 or (a * b2 - b * a2) % 3 == 0:
            continue  # not invertible mod 6
        for c, c2 in itertools.product(range(6), repeat=2):
            for k in range(6):
                if all(fn[((a * i + b * j + c) % 6, (a2 * i + b2 * j + c2) % 6)] == nf.kpow(fn[(i, j)], 1 << k)
                       for i in range(6) for j in range(6)):
                    syms.append(((a, b, c), (a2, b2, c2), k))
    print(name, ': affine symmetries found:', len(syms))
    lin = sorted({(s[0][:2], s[1][:2]) for s in syms})
    print('   linear parts:', lin)
    json.dump({'n_sym': len(syms), 'examples': syms[:40]}, open('step22_cosetsym_%s.json' % name.replace('(', '').replace(')', ''), 'w'), indent=1)
