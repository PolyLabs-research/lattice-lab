"""Step 9 (norms): end-to-end check on rule 4850 itself, in the final 'index-3 period' form.

Claims (m = 37; al = (j+k)/2, be = (j-k)/2, d = log2(be/al) mod 6, theta = index-3 period):
  (1) core f0:  N_{K/F64}( W/(t_al t_be) ) = (theta(al) theta(be))^(3 m(d)),  m = 0,-1,-2,0,-2,-1
  (2) 4850:     N_{K/F64}( lambda_4850(j, k) ) = (theta(al) theta(be))^(2 (2 n(d) - 1)),  n = 2,-1,-4,2,-4,-1
      at every character with j != +-k  (both are in F8*, i.e. ninth powers);
  (3) on j = +-k (the 4850 class (1,1)) lambda is a ninth power (direct; known cyclotomic explanation);
  (4) corollary 'rule 90 is Legendre': t_x^29127 = rho(2x) (= sum over the coset 2x QR of zeta^u) for all x != 0;
  (5) eta(x) = theta(x) rho(x)  (index 6 = index 3 x index 2), all x != 0.
lambda_4850 is computed from the rule's orbits (census.rule), independently of W."""
import sys, json
sys.path.insert(0, '/home/user/lattice-lab/examples/rule-4850')
import census
import nlib

p = 37
S = nlib.Setting(p)
F = S.F
mul = F.mul
lg = S.two
eta = lambda x: S.eta(x % p)
theta = lambda x: eta(x) ^ eta(8 * x)
rho = lambda x: eta(x) ^ eta(4 * x) ^ eta(16 * x)
n = {0: 2, 1: -1, 2: -4, 3: 2, 4: -4, 5: -1}
mm = {d: (n[d] - 2) // 3 for d in n}
inF8 = lambda z: F.frob(z, 3) == z
h = pow(2, -1, p)
rule = census.rule(4850, 4)
ok1 = ok2 = ok3 = True
cnt_off = cnt_diag = 0
for j in range(p):
    for k in range(p):
        if (j, k) == (0, 0):
            continue
        lam = 0
        for a, b in rule:
            lam ^= S.zp[(a * j + b * k) % p]
        assert lam != 0
        N = S.norm_Kk(lam)
        al, be = (j + k) * h % p, (j - k) * h % p
        if al == 0 or be == 0:
            cnt_diag += 1
            ok3 &= inF8(N)
            continue
        cnt_off += 1
        d = (lg[be] - lg[al]) % 6
        TT = mul(theta(al), theta(be))
        ok2 &= N == F.pow(TT, (2 * (2 * n[d] - 1)) % F.order)
        lam0 = mul(S.W(al, be), F.inv(mul(S.t[al], S.t[be])))
        ok1 &= S.norm_Kk(lam0) == F.pow(TT, (3 * mm[d]) % F.order)
ok4 = all(F.pow(S.t[x], 29127) == rho(2 * x) for x in range(1, p))   # t_x in K: t^((2^18-1)/9) = t^29127
ok5 = all(eta(x) == mul(theta(x), rho(x)) for x in range(1, p))
out = {'(1) core f0 norm = (theta theta)^(3m(d))': ok1,
       '(2) 4850 norm = (theta theta)^(2(2n(d)-1)) off j=+-k (%d chars)' % cnt_off: ok2,
       '(3) 4850 ninth powers on j=+-k (%d chars)' % cnt_diag: ok3,
       '(4) t_x^29127 = rho(2x)': ok4,
       '(5) eta = theta rho': ok5}
for k_, v in out.items():
    print(k_, v)
json.dump(out, open('s9_endtoend.json', 'w'), indent=1)
