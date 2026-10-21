"""check-algebra a1: symbolic re-derivation of the universal norm formula (*), char 2.

Independent derivation (verifier's own).
Let sigma generate Gal(K/k), |Gal| = 3, acting on t-indices by w (primitive cube root of 1 in F_p).
A_i = sigma^i(t_al) = t_{w^i al},  B_i = t_{w^i be}.  Then
    W(al, be) = sum_{u in mu3} t_{u al} t_{be/u} = A0 B0 + A1 B2 + A2 B1,
    sigma W   = A1 B1 + A2 B0 + A0 B2,   sigma^2 W = A2 B2 + A0 B1 + A1 B0.
Step R (resolvents): with omega in F4 and R_k(A) = A0 + omega^k A1 + omega^2k A2, x_k = R_k(A) R_k(B):
    W = x0 + x1 + x2 (3 = 1), sigma x_k = omega^k x_k, so N W = x0^3 + x1^3 + x2^3 + x0 x1 x2 (-3 = 1).
    x0 = e1(A) e1(B);  R1 R2 = e1^2 + e2 (char 2);  R1^3 = P + omega S1 + omega^2 S2, R2^3 = P + omega^2 S1 + omega S2,
    P = sum A_i^3, S1 = A0^2 A1 + A1^2 A2 + A2^2 A0, S2 = A0 A1^2 + A1 A2^2 + A2 A0^2.
    => x1^3 + x2^3 = P_A (S1_B + S2_B) + P_B (S1_A + S2_A) + S1_A S1_B + S2_A S2_B.
  CHECK 1 below: the resulting identity has F2 coefficients and holds in F2[A0..B2] -- so it needs neither
  omega in k nor any field: it is a polynomial identity (covers e/3 odd too, e.g. p = 19).
Step E (evaluation at t's; uses only t_x t_y = t_{x+y} + t_{x-y}, t_0 = 0, mu6-invariance of eta):
    e1 = eta(al) = X;  e2 = eta((1+w)al) + eta((1-w)al) = X + Xa  (1 + w = -w^2 in mu6);
    e3 = t_al t_{w al} t_{w^2 al} = t_0 + t_{-2w^2 al} + t_{-2w al} + t_{2al} = eta(2al) = X^2;
    P = e1^3 + e1 e2 + e3 = X^3 + X Xa  (Newton, char 2);
    S1 = eta((2+w)al) + eta((2-w)al),  S2 = eta((2+w^2)al) + eta((2-w^2)al);
    and EXACTLY 2 + w^2 = 1 - w, 2 + w = 1 - w^2 = -w^2 (1 - w)  (from 1 + w + w^2 = 0),
    so eta((2+w)al) = eta((2+w^2)al) = Xa, S1 = Xa + Xb, S2 = Xa + Xb'.
  NOTE: this last identification eta((2+w)x) = eta((1-w)x) is NOT among the facts listed in the investigator's
  s2 docstring (which lists only eta((2+w)x) = eta((2+w^2)x)); without it the elimination leaves
  Xc Y Ya + Yc X Xa (Xc = eta((2+w)al)) in place of Xa Ya (X + Y).  CHECK 2 confirms both statements.
  CHECK 3: the substituted expression equals (*) in F2[X, Xa, Xb, Xb', Y, Ya, Yb, Yb'] MODULO the auxiliary
  relations X Xa = Xb + Xb', Y Ya = Yb + Yb' (they are the evaluation of S1 + S2 = e1 e2 + e3, and equally the
  mod-2 product rule eta(x) eta((1-w)x) = sum_v eta(x(1 + (1-w)v)) -- no eta(0) term occurs there, since
  1 - w in mu6 would force p | 28).  Without Xc = Xa, the leftover is X Xa (Ya + Yc) + Y Ya (Xa + Xc).
  CHECK 4: (*) is invariant under w <-> w^2 (Xa fixed since (1-w^2) = -w^2 (1-w); Xb <-> Xb', Yb <-> Yb' together).
  CHECK 5: the F_p multiplier identities hold for every prime p < 2000 in the family, and the nondegeneracy
  (1-w, 2-w, 2-w^2, 3 nonzero mod p) holds; the multipliers 1-w, 2-w, 2-w^2 avoid 0 and mu6-multiples of each
  other as needed.
"""
import json
import sympy as sp

A0, A1, A2, B0, B1, B2 = sp.symbols('A0 A1 A2 B0 B1 B2')
out = {}


def F2(expr, gens):
    return sp.Poly(sp.expand(expr), *gens, modulus=2)


gensAB = (A0, A1, A2, B0, B1, B2)
W0 = A0 * B0 + A1 * B2 + A2 * B1
W1 = A1 * B1 + A2 * B0 + A0 * B2
W2 = A2 * B2 + A0 * B1 + A1 * B0
LHS = W0 * W1 * W2


def sym(a0, a1, a2):
    e1 = a0 + a1 + a2
    e2 = a0 * a1 + a1 * a2 + a2 * a0
    e3 = a0 * a1 * a2
    P = a0 ** 3 + a1 ** 3 + a2 ** 3
    S1 = a0 ** 2 * a1 + a1 ** 2 * a2 + a2 ** 2 * a0
    S2 = a0 * a1 ** 2 + a1 * a2 ** 2 + a2 * a0 ** 2
    return e1, e2, e3, P, S1, S2


e1A, e2A, e3A, PA, S1A, S2A = sym(A0, A1, A2)
e1B, e2B, e3B, PB, S1B, S2B = sym(B0, B1, B2)
RHS = (e1A * e1B) ** 3 + e1A * e1B * (e1A ** 2 + e2A) * (e1B ** 2 + e2B) \
    + PA * (S1B + S2B) + PB * (S1A + S2A) + S1A * S1B + S2A * S2B
c1 = (F2(LHS, gensAB) - F2(RHS, gensAB)).is_zero
print('CHECK 1  W sigmaW sigma^2W == resolvent expansion in F2[A0..B2]:', c1)
out['check1_resolvent_identity_F2'] = bool(c1)
# also verify the resolvent route itself with omega adjoined (F2[omega]/(omega^2+omega+1)): x0^3+x1^3+x2^3+x0x1x2
om = sp.symbols('om')
R = lambda a, k: a[0] + om ** k * a[1] + om ** (2 * k) * a[2]
x = [R((A0, A1, A2), k) * R((B0, B1, B2), k) for k in range(3)]
resv = sp.expand(x[0] ** 3 + x[1] ** 3 + x[2] ** 3 + x[0] * x[1] * x[2] - LHS)
resv_red = sp.Poly(resv, om, *gensAB, modulus=2)
_, rem = sp.div(resv_red, sp.Poly(om ** 2 + om + 1, om, *gensAB, modulus=2))
print('         x0^3+x1^3+x2^3+x0x1x2 == N W in F4[A,B]:', rem.is_zero)
out['check1b_resolvent_cubic_form_F4'] = bool(rem.is_zero)
# Newton and cyclic-sum facts used in step E
c1c = (F2(PA - (e1A ** 3 + e1A * e2A + e3A), gensAB)).is_zero and \
      (F2(S1A + S2A - (e1A * e2A + e3A), gensAB)).is_zero
print('         P = e1^3 + e1 e2 + e3 and S1 + S2 = e1 e2 + e3 (char 2):', c1c)
out['check1c_newton_char2'] = bool(c1c)

# ---------------- CHECK 2/3: elimination
X, Xa, Xb, Xbp, Xc, Y, Ya, Yb, Ybp, Yc = sp.symbols('X Xa Xb Xbp Xc Y Ya Yb Ybp Yc')
gensE = (X, Xa, Xb, Xbp, Xc, Y, Ya, Yb, Ybp, Yc)


def reduced(X, Xa, Xb, Xbp, Xc, Y, Ya, Yb, Ybp, Yc):
    e1A, e2A, PA, S1A, S2A = X, X + Xa, X ** 3 + X * Xa, Xc + Xb, Xc + Xbp
    e1B, e2B, PB, S1B, S2B = Y, Y + Ya, Y ** 3 + Y * Ya, Yc + Yb, Yc + Ybp
    return (e1A * e1B) ** 3 + e1A * e1B * (e1A ** 2 + e2A) * (e1B ** 2 + e2B) \
        + PA * (S1B + S2B) + PB * (S1A + S2A) + S1A * S1B + S2A * S2B


STAR = X ** 2 * Y ** 2 * (1 + X + Y) + X * Y * (X * Ya + Xa * Y) + X * Y * Xa * Ya + Xa * Ya * (X + Y) \
    + Xb * Yb + Xbp * Ybp
generic = reduced(X, Xa, Xb, Xbp, Xc, Y, Ya, Yb, Ybp, Yc)
diff_generic = F2(generic - STAR, gensE)
print('CHECK 2  with Xc = eta((2+w)x) kept free, reduced - (*) =', diff_generic.as_expr())
out['check2_leftover_if_Xc_free'] = str(diff_generic.as_expr())
spec = reduced(X, Xa, Xb, Xbp, Xa, Y, Ya, Yb, Ybp, Ya)
c3raw = F2(spec - STAR, gensE).is_zero
print('CHECK 3  with Xc = Xa only (no aux relation): reduced == (*):', c3raw)
# the aux relation  X Xa = Xb + Xb'  (= S1 + S2 = e1 e2 + e3 evaluated, or the mod-2 product rule):
aux = {Xbp: Xb + X * Xa, Ybp: Yb + Y * Ya}
d3 = F2(sp.expand(spec.subs(aux, simultaneous=True) - STAR.subs(aux, simultaneous=True)), gensE)
c3 = d3.is_zero
print('         with Xc = Xa AND modulo Xb\' = Xb + X Xa, Yb\' = Yb + Y Ya: reduced == (*):', c3)
d3x = F2(sp.expand(generic.subs(aux, simultaneous=True) - STAR.subs(aux, simultaneous=True)), gensE)
print('         with Xc free but modulo the aux relation, leftover =', d3x.as_expr())
out['check3_raw_without_aux'] = bool(c3raw)
out['check3_elimination_gives_star_mod_aux'] = bool(c3)
out['check3_leftover_Xc_free_mod_aux'] = str(d3x.as_expr())
# CHECK 4: w <-> w^2 swaps Xb<->Xbp and Yb<->Ybp simultaneously
STARsw = STAR.subs({Xb: Xbp, Xbp: Xb, Yb: Ybp, Ybp: Yb}, simultaneous=True)
c4 = F2(STARsw - STAR, gensE).is_zero
print('CHECK 4  (*) invariant under w <-> w^2:', c4)
out['check4_w_swap_invariant'] = bool(c4)
# mixed pairing would NOT be the same (sanity that the pairing matters)
STARmix = STAR.subs({Yb: Ybp, Ybp: Yb}, simultaneous=True)
print('         (sanity) swapping only Yb<->Yb\' changes (*):', not F2(STARmix - STAR, gensE).is_zero)


# ---------------- CHECK 5: F_p multiplier identities over the family
def ordmod(a, m):
    x, k = a % m, 1
    while x != 1:
        x = x * a % m
        k += 1
    return k


fam, bad = [], []
for p in sp.primerange(5, 2000):
    d = ordmod(2, p)
    if d % 2 or (d // 2) % 3:
        continue
    e = d // 2
    s = pow(2, e // 3, p)              # sigma = Frob^(e/3) acts on zeta-exponents by s
    mu6 = {u for u in range(1, p) if pow(u, 6, p) == 1}
    w = (-s) % p                       # t is even, so sigma acts on t-indices by w = -s
    ok = (pow(s, 6, p) == 1 and pow(s, 3, p) == p - 1 and pow(w, 3, p) == 1 and w != 1
          and (1 + w) % p in mu6                                  # e2: eta((1+w)x) = eta(x)
          and (2 + w * w) % p == (1 - w) % p                      # 2 + w^2 = 1 - w
          and (2 + w) % p == (-w * w * (1 - w)) % p               # 2 + w = -w^2 (1 - w)
          and (1 + w - w * w) % p == (-2 * w * w) % p and (1 - w + w * w) % p == (-2 * w) % p   # e3
          and all(c % p for c in (1 - w, 2 - w, 2 - w * w, 3)))
    fam.append(p)
    if not ok:
        bad.append(p)
print('CHECK 5  family primes < 2000 (ord_p(2) = 2e, 3 | e):', len(fam), 'first:', fam[:12], ' failures:', bad)
out['check5_family_primes_lt_2000'] = fam
out['check5_failures'] = bad
json.dump(out, open('/home/user/lattice-lab/examples/rule-4850/deep/check-algebra/a1_symbolic.json', 'w'), indent=1)
