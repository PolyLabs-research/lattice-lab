"""Step 8 (norms): the multiplicative structure of the Gauss periods of 37 inside F64 = F8* x F4* (x {0}),
which turns the closed form N(W) = (eta(al) eta(be))^n(d) into statements about periods of index 2, 3, 6.
   eta(x)   index 6 (mu6-cosets, F64),  theta(x) = eta(x) + eta(8x)  index 3 (F8),
   rho(x)   = eta(x) + eta(4x) + eta(16x) index 2 (F4).
Search for the exact monomial relations between them (exponents mod 63), and the char-0 vs mod-2 contrast:
for the d = 3 class the char-0 norm is already sigma_8-invariant (forced by symmetry), for d = +-1 it is not
(the F8-membership is a mod-2 fact)."""
import json
import nlib

p = 37
S = nlib.Setting(p)
F = S.F
lg = S.two
eta = lambda x: S.eta(x % p)
theta = lambda x: eta(x) ^ eta(8 * x)
rho = lambda x: eta(x) ^ eta(4 * x) ^ eta(16 * x)
out = {}
# exponent search: eta(x) = theta(c1 x)^i * rho(c2 x)^j ; theta(c x) = eta(x)^k ; rho(c x) = eta(x)^k
def find_power(target_fn, base_fn):
    res = []
    for c in range(6):
        for k in range(63):
            if all(target_fn(pow(2, c, p) * x) == F.pow(base_fn(x), k) for x in range(1, p)):
                res.append((2 ** c, k))
    return res
out['theta(2^c x) = eta(x)^k'] = find_power(theta, eta)
out['rho(2^c x) = eta(x)^k'] = find_power(rho, eta)
print('theta(2^c x) = eta(x)^k for (2^c, k) in', out['theta(2^c x) = eta(x)^k'])
print('rho(2^c x)   = eta(x)^k for (2^c, k) in', out['rho(2^c x) = eta(x)^k'])
dec = []
for c1 in range(3):
    for c2 in range(2):
        for i in (1, 2, 4):
            for j in (1, 2):
                if all(eta(x) == F.mul(F.pow(theta(pow(2, c1, p) * x), i), F.pow(rho(pow(2, c2, p) * x), j))
                       for x in range(1, p)):
                    dec.append(dict(theta_shift=2 ** c1, theta_exp=i, rho_shift=2 ** c2, rho_exp=j))
out['eta(x) = theta(c1 x)^i rho(c2 x)^j'] = dec
print('eta(x) = theta(c1 x)^i * rho(c2 x)^j :', dec)
# char-0 contrast (from the exact counts of step 1)
s1 = json.load(open('s1_exact_norms.json'))
for key in ('0,1', '0,3', '0,5'):
    c = s1['char0'][key]
    diffs = [c[1 + i] - c[1 + i + 3] for i in range(3)]
    print('char-0 N at (i,j) = (%s): c_i - c_{i+3} =' % key, diffs, ' -> sigma_8-invariant in char 0:', all(x == 0 for x in diffs),
          ' mod 2:', all(x % 2 == 0 for x in diffs))
    out['char0_sigma8_diffs_%s' % key] = diffs
json.dump(out, open('s8_period_relations.json', 'w'), indent=1)
