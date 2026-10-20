"""Does P0 (and ninth-power-ness) of F'(A, B) = (AB)^3 + s^2 (1 + s e)^2 survive when B is an
arbitrary element of F(2^18) instead of a t_beta?  A runs over the t_alpha."""
import random, collections
import ff18 as F
T = F.tvec()

def Fp(A, B):
    s = A ^ B; p = F.mul(A, B); e = F.mul(1 ^ A, 1 ^ B)
    Y = F.mul(s, 1 ^ F.mul(s, e))
    return F.pw(p, 3) ^ F.mul(Y, Y)

random.seed(5)
stats = collections.Counter()
for trial in range(400):
    B = random.randrange(2, 1 << 18)
    p0 = True; ninth = True
    for al in range(1, 19):
        vs = []
        for h in (1, 27, 26):
            v = Fp(T[h * al % 37], B)
            vs.append(None if v == 0 else F.v27(v))
        if None in vs:
            continue
        if len(set(vs)) > 1:
            p0 = False
        if any(x % 9 for x in vs):
            ninth = False
    stats[(p0, ninth)] += 1
print('random B in F(2^18): (P0 holds for all alpha, all values ninth powers) ->', dict(stats))
# B in F64 / F(2^9) / F(2^6): special subfields
for name, deg in (('F64', 6), ('F512', 9)):
    st = collections.Counter()
    for B in range(1, 1 << 18):
        if F.pw(B, 2 ** deg) != B:
            continue
        p0 = True
        for al in range(1, 19):
            vs = [F.v27(Fp(T[h * al % 37], B)) if Fp(T[h * al % 37], B) else None for h in (1, 27, 26)]
            if None not in vs and len(set(vs)) > 1:
                p0 = False
        st[p0] += 1
    print('B in', name, ': P0 holds for', dict(st))
# B = t_beta (the actual case)
st = collections.Counter()
for be in range(1, 19):
    for al in range(1, 19):
        vs = [F.v27(Fp(T[h * al % 37], T[be])) if Fp(T[h * al % 37], T[be]) else None for h in (1, 27, 26)]
        st[None in vs or len(set(vs)) == 1] += 1
print('B = t_beta: P0 per (alpha, beta):', dict(st))
