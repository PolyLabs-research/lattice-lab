"""The 12-term structure.  Verified identities (group ring, verify_identity.py):
   4850 * (x+1/x+y+1/y)          = orbits (4,0)+(5,2)   (12 monomials)
   10491524 * (x+1/x)(y+1/y)     = orbits (4,4)+(7,3)   = h^4,  h = sum_{u in U6, e=+-1} x^u y^(e/u)
where U6 = <27> = {u : u^6 = 1} in F37*.  Eigenvalue of h at (alpha, beta):
   W = K(alpha, beta) + K(alpha, -beta),   K(alpha, beta) = sum_{u^6=1} zeta^(alpha u + beta/u)
(a Kloosterman sum over the subgroup mu6 of F37*).  Here: compute K in F(2^36) (pilot gf2.Field(37)),
check K in F(2^18), transfer to ff18 via the t-basis, and study 3-parts."""
import sys, json, collections
sys.path.insert(0, '/home/user/pilot-37c-round2/tools')
from gf2 import Field
import ff18 as F

P = 37
Fd = Field(P)
z = Fd.zeta
zp = [1]
for i in range(P - 1):
    zp.append(Fd.mul(zp[-1], z))
tc = [zp[i] ^ zp[(-i) % P] for i in range(P)]
U6 = sorted({pow(27, i, P) for i in range(6)})
assert U6 == sorted(u for u in range(1, P) if pow(u, 6, P) == 1)

# linear map census-F(2^18) -> ff18 via coordinates in the t-basis t_1..t_18
basis_c = [tc[j] for j in range(1, 19)]
piv_c = F._elim(basis_c)


def to_ff18(v):
    tag = F._coords(piv_c, v)
    return F.from_nb37([j + 1 for j in range(18) if tag >> j & 1])


# sanity: multiplicativity of the transfer
assert to_ff18(Fd.mul(tc[1], tc[3])) == F.mul(F.tvec()[1], F.tvec()[3])
assert to_ff18(Fd.mul(tc[5], tc[5] ^ tc[2])) == F.mul(F.tvec()[5], F.tvec()[5] ^ F.tvec()[2])


def K(al, be):
    v = 0
    for u in U6:
        v ^= zp[(al * u + be * pow(u, -1, P)) % P]
    return v


T = F.tvec()
stats = collections.Counter()
rows = []
for al in range(1, 19):
    for be in range(1, 19):
        k1, k2 = K(al, be), K(al, -be)
        assert Fd.pow(k1, 2 ** 18) == k1 and Fd.pow(k2, 2 ** 18) == k2  # K lies in F(2^18)
        K1, K2 = to_ff18(k1), to_ff18(k2)
        Wv = K1 ^ K2
        lam = F.rule_value(10491524, 6, al, be)
        assert F.pw(Wv, 4) == F.mul(lam, F.mul(T[al], T[be]))  # lambda' * ab = W^4
        rec = dict(al=al, be=be, vK1=None if K1 == 0 else F.v27(K1), vK2=None if K2 == 0 else F.v27(K2),
                   vW=F.v27(Wv), vA=F.v27(T[al]), vB=F.v27(T[be]))
        rows.append(rec)
        stats[('K1 zero', K1 == 0, 'K2 zero', K2 == 0)] += 1
        if K1 and K2:
            stats[('vK1 mod 3', rec['vK1'] % 3, 'vK2 mod 3', rec['vK2'] % 3)] += 1
        stats[('vW mod 3', rec['vW'] % 3)] += 1
        stats[('4vW - vA - vB mod 9', (4 * rec['vW'] - rec['vA'] - rec['vB']) % 9)] += 1
print('identity  lambda_10491524 * t_alpha t_beta = W^4  verified on all (alpha, beta) in [1..18]^2')
for k, v in sorted(stats.items(), key=str):
    print(k, v)
json.dump(rows, open('kloosterman.json', 'w'))
