"""Step 10. Rule 90 (t_j = zeta^j + zeta^-j) at the 2-primitive primes m = 13 mod 24 up to 2000: its 3-adic level in
F(2^e)*, e = (m-1)/2 (one Frobenius orbit, so one logarithm decides).  Level 1 = every t_j a cube (the 37 situation)."""
import json, sympy
import famlib as L
out = []
for m in sympy.primerange(13, 2001):
    if m % 24 != 13 or sympy.n_order(2, m) != m - 1:
        continue
    F = L.GF(m)
    e = (m - 1) // 2
    a = sympy.multiplicity(3, 2 ** e - 1)
    v = F.log3(F.t[1])                      # log mod 3^A in F(2^(m-1))*, A = v3(2^(m-1) - 1) = a (2^e + 1 prime to 3)
    lev = L.v3(v, F.A) - (F.A - a)
    out.append(dict(m=m, e=e, v3_2e_minus_1=a, t_level=lev))
    print(out[-1], flush=True)
json.dump(out, open('step10_rule90.json', 'w'), indent=1)
print('rule 90 cube-confined at:', [r['m'] for r in out if r['t_level'] >= 1])
