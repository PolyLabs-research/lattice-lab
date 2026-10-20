"""Step 2a: the n-th power reciprocity law in F_64[T] (q = 64, n | 63), verified numerically.

Statement (char 2, so (-1) = 1): for coprime nonzero A, B in F_q[T] with leading coefficients
a, b (and (A/B)_n defined through the monic irreducible factors of B, ignoring b):
    (A/B)_n = a^{((q-1)/n) deg B} * b^{-((q-1)/n) deg A} * (B/A)_n .
For A, B monic: (A/B)_n = (B/A)_n.  For n = 9, q = 64: (q-1)/n = 7.
Proof: for monic B, (A/B)_n = prod_R N(A(beta_R))^{(q-1)/n} = Res(B, A)^{(q-1)/n}; and
Res(B, A) = (-1)^{deg A deg B} Res(A, B), Res(cA0, B0) = c^{deg B0} Res(A0, B0).
The test: random A, B of degrees 1..12, symbols from the factorisations (Euler's criterion),
compared with the formula; also Res-based symbols."""
import random
from rlib import *

rng = random.Random(2026)
n = 9
e = 63 // n
count = 0
for trial in range(400):
    da, db = rng.randrange(1, 13), rng.randrange(1, 13)
    A = [rng.randrange(64) for _ in range(da)] + [rng.randrange(1, 64)]
    B = [rng.randrange(64) for _ in range(db)] + [rng.randrange(1, 64)]
    if q_deg(q_gcd(A, B)) > 0:
        continue
    a, b = A[-1], B[-1]
    lhs = jacobi9(A, B, n)
    rhs = m64(m64(pow64(a, e * db), pow64(inv64(b), e * da)), jacobi9(B, A, n))
    assert lhs == rhs, (A, B, lhs, rhs)
    # also: (A/B)_n = Res(B_monic, A)^e
    Bm = q_monic(B)
    assert lhs == pow64(resultant64(Bm, A), e)
    count += 1
# other n dividing 63 (3, 7, 21, 63) on a smaller sample
for n2 in (3, 7, 21, 63):
    e2 = 63 // n2
    for trial in range(60):
        da, db = rng.randrange(1, 9), rng.randrange(1, 9)
        A = [rng.randrange(64) for _ in range(da)] + [rng.randrange(1, 64)]
        B = [rng.randrange(64) for _ in range(db)] + [rng.randrange(1, 64)]
        if q_deg(q_gcd(A, B)) > 0:
            continue
        lhs = jacobi9(A, B, n2)
        rhs = m64(m64(pow64(A[-1], e2 * db), pow64(inv64(B[-1]), e2 * da)), jacobi9(B, A, n2))
        assert lhs == rhs
print(f'reciprocity law verified on {count} random coprime pairs (n = 9) and samples for n = 3, 7, 21, 63')

# The six cubic factors pi_a of m37 over F_64 and the check (Q/pi)_9 == Q(t_1)^29127
P = pis()
prod = [1]
for p in P:
    prod = q_mul(prod, p)
assert prod == q_from2(m37()), 'pis multiply to m37'
for a, p in enumerate(P):
    print(f'pi_{a} = T^3 + w^{LOG64[p[2]] if p[2] else "-"} T^2 + w^{LOG64[p[1]] if p[1] else "-"} T + w^{LOG64[p[0]] if p[0] else "-"}')
# frobenius relation pi_{a+1} = pi_a^sigma
for a in range(6):
    assert q_frob(P[a]) == P[(a + 1) % 6]
print('pi_{a+1} = sigma(pi_a) (coefficientwise squaring)')
rng = random.Random(5)
for trial in range(200):
    Q = rng.getrandbits(rng.randrange(2, 60)) | 1
    if pgcd(Q, m37()) != 1:
        continue
    v = val_t1(Q)
    s_direct = to64_from18(f18_pow(v, NINTH))
    s_symbol = jacobi9(q_from2(Q), P[0])
    s_recip = jacobi9(P[0], q_from2(Q))
    assert s_direct == s_symbol == s_recip, (Q, s_direct, s_symbol, s_recip)
print('(Q/pi_0)_9 = Q(t_1)^29127 = (pi_0/Q)_9 for 200 random Q in GF(2)[T]')
