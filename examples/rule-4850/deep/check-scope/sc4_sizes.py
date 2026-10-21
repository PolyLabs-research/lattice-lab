"""sc4 (check-scope): which sizes m satisfy the hypotheses of the 37 argument?

Setting S(m): m odd, 3 does not divide m, -1 in <2> mod m (ord = 2e), 3 | e, and w := -2^(e/3) mod m is a
primitive cube root of 1 in every prime component (w^2 + w + 1 = 0 mod m)  [sigma = Frob^(e/3) acts on the
hexagon index set by w, which is what the resolvent derivation of (*) uses];
  f := e/3, k = F(2^f).  Ninth powers decidable by N_{K/k} iff 9 | 2^f - 1 iff 6 | f.
  k = F64 (ninth powers of k* = F8*, a subfield) iff f = 6 iff ord_m(2) = 36.
  single orbit (all mu6-cosets Frobenius conjugate, so (*) collapses to one variable eta_0) iff <2> = (Z/m)*.
We enumerate (1) every m <= LIM in S(m), (2) every m with ord_m(2) = 36 (all divisors of 2^36 - 1), and
(3) the claim 'k = F64 only when ord_m(2) = 36, i.e. m | 4033'."""
import json
import math
import sympy

LIM = 200000
out = {}


def setting(m):
    if m % 2 == 0 or m % 3 == 0 or m < 5:
        return None
    d = sympy.n_order(2, m)
    if d % 2 or pow(2, d // 2, m) != m - 1:
        return None
    e = d // 2
    if e % 3:
        return None
    f = e // 3
    w = (-pow(2, f, m)) % m
    if (w * w + w + 1) % m:
        return dict(m=m, ord=d, f=f, sigma_is_primitive_cube_root=False)
    phi = sympy.totient(m)
    return dict(m=m, ord=d, f=f, sigma_is_primitive_cube_root=True, single_orbit=(d == phi),
                ninth_decidable=(f % 6 == 0), prime=sympy.isprime(m))


rows = [r for r in (setting(m) for m in range(5, LIM + 1, 2)) if r and r['sigma_is_primitive_cube_root']]
f6 = [r['m'] for r in rows if r['f'] == 6]
single = [r['m'] for r in rows if r['single_orbit']]
single_ninth = [r['m'] for r in rows if r['single_orbit'] and r['ninth_decidable']]
out['setting sizes <= LIM: count'] = len(rows)
out['setting & f = 6 (k = F64)'] = f6
out['setting & single orbit (first 40)'] = single[:40]
out['setting & single orbit & 6 | f (ninth decidable by N)'] = single_ninth
print('sizes <= %d in the setting: %d' % (LIM, len(rows)))
print('  with f = 6 (k = F64):', f6)
print('  single orbit (first 25):', single[:25])
print('  single orbit and 6 | f:', single_ninth)
# (2) all m with ord_m(2) = 36
N36 = 2 ** 36 - 1
divs = sorted(sympy.divisors(N36))
o36 = []
for m in divs:
    if m > 1 and m % 2 and sympy.n_order(2, m) == 36:
        e18 = pow(2, 18, m) == m - 1
        w = (-pow(2, 6, m)) % m
        o36.append(dict(m=m, factors=sympy.factorint(m), minus1_in_2=e18, w_primitive=(w * w + w + 1) % m == 0
                        and m % 3 != 0, divides_4033=4033 % m == 0, minus3_square=all(
                            p == 3 and False or (p % 3 == 1) for p in sympy.factorint(m))))
out['#m with ord_m(2) = 36'] = len(o36)
cnt = dict(total=len(o36), minus1=sum(r['minus1_in_2'] for r in o36),
           minus1_and_minus3square=sum(r['minus1_in_2'] and r['minus3_square'] for r in o36),
           w_primitive=sum(r['w_primitive'] for r in o36))
out['ord36 counts'] = cnt
ex = [r['m'] for r in o36 if r['minus1_in_2'] and r['minus3_square'] and not r['divides_4033']][:12]
out['ord 36, -1 in <2>, -3 a square mod m, but m does not divide 4033 (examples)'] = ex
out['ord 36 with w primitive'] = [r['m'] for r in o36 if r['w_primitive']]
out['Phi_36(2)'] = 2 ** 12 - 2 ** 6 + 1
out['primes with ord 36'] = [r['m'] for r in o36 if sympy.isprime(r['m'])]
print('m with ord_m(2) = 36:', cnt)
print('  primes:', out['primes with ord 36'], '; Phi_36(2) =', out['Phi_36(2)'], '=', sympy.factorint(4033))
print('  w = -2^6 a primitive cube root mod m exactly for m in', out['ord 36 with w primitive'])
print('  ord 36, -1 in <2>, (-3/m) = 1 but m not | 4033 (first few):', ex)
# for those composites, how does sigma = Frob^6 act on each prime component?
detail = {}
for m in ex[:6]:
    detail[m] = {p: ((-pow(2, 6, p)) % p, ((-pow(2, 6, p)) ** 2 + (-pow(2, 6, p)) + 1) % p == 0)
                 for p in sympy.factorint(m)}
out['component action of -2^6 (value, is primitive cube root)'] = detail
print('  component action of w = -2^6:', detail)
# (3) 2^6 - 3^3 and the m for which 2^6 = 3^3
out['2^6 - 3^3'] = 64 - 27
print('2^6 - 3^3 =', 64 - 27, ' -> 2^6 = 3^3 (mod m) only for m | 37')
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/check-scope/sc4_sizes.json', 'w'), indent=1,
          default=str)
