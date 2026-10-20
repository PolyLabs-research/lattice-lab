"""Exact group-ring verification (no eigenvalues, no field arithmetic) in F2[Z_37^2]:

 (I)  G^[M] * G^[6] = G * G^[6M]        G = f * mult,  [A]: exponent (p,q) -> A^T (p,q) mod 37
      4850:     mult = x + 1/x + y + 1/y,      M = [[19, 8], [8, 19]]
      10491524, 20982139, 178279803:  mult = (x + 1/x)(y + 1/y),  M = diag(27, 11)
 (N)  partial norms  f(x,y) f(x^27,y) f(x^26,y)  of 20982139 and 178279803 equal that of 10491524
      modulo Phi37(x) (i.e. at every character with j != 0).
Also: the same identities for random rules (controls)."""
import json, random, sys
import numpy as np
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import census

P = 37


def arr(expset):
    a = np.zeros((P, P), dtype=np.uint8)
    for p, q in expset:
        a[p % P, q % P] ^= 1
    return a


def mul(a, b):
    out = np.zeros((P, P), dtype=np.uint8)
    for p, q in zip(*np.nonzero(a)):
        out ^= np.roll(np.roll(b, p, axis=0), q, axis=1)
    return out


def dil(a, A):
    out = np.zeros((P, P), dtype=np.uint8)
    (a11, a12), (a21, a22) = A
    for p, q in zip(*np.nonzero(a)):
        # exponent (p,q) -> A^T (p,q)
        out[(a11 * p + a21 * q) % P, (a12 * p + a22 * q) % P] ^= 1
    return out


def identity_I(f, mult, M):
    G = mul(f, mult)
    six = ((6, 0), (0, 6))
    sixM = tuple(tuple((6 * x) % P for x in row) for row in M)
    lhs = mul(dil(G, M), dil(G, six))
    rhs = mul(G, dil(G, sixM))
    return bool(np.array_equal(lhs, rhs)), int(G.sum()), int(lhs.sum())


def mod_phi_x(a):
    """reduce modulo Phi37(x): subtract (row-wise) the all-ones x-vector; canonical form: make row x^36 zero."""
    b = a.copy()
    top = b[36, :].copy()
    b ^= top[None, :]  # Phi37(x) = 1 + x + ... + x^36 times top
    return b


S = arr({(1, 0), (-1, 0), (0, 1), (0, -1)})
AB = mul(arr({(1, 0), (-1, 0)}), arr({(0, 1), (0, -1)}))
M4850 = ((19, 8), (8, 19))
Mstd = ((27, 0), (0, 11))
out = {}
for n, r, mult, M, name in [(4850, 4, S, M4850, 's'), (10491524, 6, AB, Mstd, 'ab'), (20982139, 6, AB, Mstd, 'ab'),
                            (178279803, 6, AB, Mstd, 'ab')]:
    ok, wG, wl = identity_I(arr(census.rule(n, r)), mult, M)
    out['I_%d' % n] = dict(holds=ok, mult=name, M=M, weight_G=wG, weight_side=wl)
    print('(I)', n, 'mult', name, 'M', M, '->', ok, ' |G| =', wG, ' |each side| =', wl)
random.seed(2)
ctrl = []
for _ in range(20):
    n = random.randrange(1, 1 << 15)
    ctrl.append((n, identity_I(arr(census.rule(n, 4)), S, M4850)[0], identity_I(arr(census.rule(n, 4)), AB, Mstd)[0]))
out['I_controls_random_r4'] = ctrl
print('controls (random radius-4, both versions):', [c for c in ctrl if c[1] or c[2]], 'of', len(ctrl))


def pnorm(n, r):
    f = arr(census.rule(n, r))
    return mod_phi_x(mul(mul(f, dil(f, ((27, 0), (0, 1)))), dil(f, ((26, 0), (0, 1)))))


N0 = pnorm(10491524, 6)
for n in (20982139, 178279803):
    eq = bool(np.array_equal(pnorm(n, 6), N0))
    out['N_%d' % n] = eq
    print('(N) partial norm of', n, '== that of 10491524 mod Phi37(x):', eq)
# control: a random radius-6 rule
n = random.randrange(1, 1 << 28)
print('(N) control', n, bool(np.array_equal(pnorm(n, 6), N0)))
json.dump(out, open('verify_identity.json', 'w'), indent=1)
