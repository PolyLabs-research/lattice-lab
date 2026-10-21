# Rule 4850 at m = 37: final report of the deep dive

Written 2026-10-21, after the final proof check. Paths are relative to
`examples/rule-4850/deep/` unless they begin with `examples/`, which is relative to the lattice-lab
root. The question, the setting and the notation (t_j = ζ^j + ζ^-j, classes, F(2^18), 29127 =
(2^18 - 1)/9) are those of `DOSSIER.md`.

Status words used throughout:

- **verified**: an independent verifier recomputed it, in its own field model or its own algebra,
  and confirmed it.
- **verified with repair**: confirmed once a verifier supplied a missing step or corrected the
  statement.
- **partial**: part of the claim was confirmed and part was not.
- **refuted**: a verifier showed the claim false as stated.
- **investigator only**: computed by an investigator and not re-run by any verifier.

The investigators were relations, reciprocity, threeadic, normform, grouping, calibration, model19,
norms and family. The first-round verifiers were verify-identities, verify-reduction and
verify-specificity. The final proof check was check-algebra, check-chain and check-scope. Each
verifier built its own field (trinomial, sparse, dense random or Φ_37 moduli) and imported nothing
from the investigators.

## 1. The answer in brief

**Is 4850 explained?** Yes. Ninth-power confinement of rule 4850 at m = 37 now has a proof. All
three final checkers, working separately, returned the same overall verdict: "the proof stands
with repairs". The repairs are small and the checkers supplied them (section 3). Two things are
still missing. The repaired proof has not been written up as one document: it is spread over
script docstrings in `norms/` and the three check logs, and the docstring's "see report" points
to a file that does not exist. It has also not been formalised.

**By what.** Three facts, in order.

1. *The hexagon identity* (exact, at every size). With s = x + 1/x + y + 1/y,

       4850 · s = Hex(x, y) + Hex(y, x),   Hex = {±(4,0), ±(2,5), ±(2,-5)},

   a 12-term Laurent polynomial (the D4-orbits (4,0) and (5,2)).
2. *An order-3 symmetry, which exists only at 37.* Mod 37 the 12 points are fixed by an order-3
   element of SL2(F37), because 5^2 + 3·2^2 = 37. In the 45° coordinates α = (j+k)/2,
   β = (j-k)/2 this gives the closed form

       λ_4850(j, k) = W(α, β)^4 / (t_α t_β),   W(α, β) = Σ_{u ∈ μ3} t_{uα} t_{β/u},

   off the diagonals j = ±k. Here μ3 = {1, 10, 26} mod 37, and W is the eigenvalue of a 12-point
   hexagon set (a Kloosterman-type sum over μ6).
3. *A norm computation.* Let K = F(2^18), k = F64 and N = N_{K/k}. A nonzero λ in K is a ninth
   power iff N(λ) lies in F8*. Two norms are known in closed form. N(t_x) = η(x)^2, where
   η(x) = Σ_{u ∈ μ6} ζ^{ux} is a Gauss period. N(W) is a fixed polynomial (*) in Gauss periods,
   valid at every prime of the family. At 37 all the periods are Frobenius conjugates of one
   element η_0. The discrete logs mod 6 of 1 - w, 2 - w and 2 - w^2 (w = 10, the cube root of 1
   by which Frobenius^6 acts) are (4, 3, 5). They force η_0^24 + η_0^9 + 1 = 0, so η_0 has
   order 21: it is a cube in F64*. Formula (*) then collapses to
   N(W) = (η(α)η(β))^{n(d)}, with n = (2, -1, -4, 2, -4, -1) indexed by d = log2(β/α) mod 6.
   So N(λ) = (η(α)η(β))^{4n(d)-2}. Every exponent is divisible by 3, so N(λ) lies in F8*. The 72
   diagonal characters have λ = t_j t_{5j}, whose norm η(j)^66 also lies in F8*.

**Its relatives.** All six are accounted for by exact identities, verified in the first round
(section 2.4). 482758, 8438150 and 43250486 are 4850 times ninth-power units. 10491524 is the 45°
image of 4850. 20982139 and 178279803 are Frobenius^6 conjugates of 10491524, times a ninth-power
unit off the axes, and have cyclotomic axis restrictions. According to `calibration/condition.jsonl`
(investigator only), these seven are the only ninth-power rules of radius ≤ 6 that mechanisms 1 to
8 leave unexplained. The dossier's open list is therefore closed.

**Why only at 37.** "Only at 37" means two different things here.

- *For 4850 itself* (verified): the order-3 symmetry of its 12-point numerator exists mod m only
  when m divides 5^2 + 3·2^2 = 37. The dossier records that 4850 is not confined at 101, 109,
  185 or 197; the verifiers found the same at 13, 61, 97 and 109.
- *For the hexagon family* f_{p,q} with q^2 + 3p^2 ≡ 0 (mod m): the mechanism needs k = F64, all
  μ6-cosets in one Frobenius orbit, the right coset data, and η a cube. Among all sizes checked
  these hold only at 37 (verified, check-scope). The family survey found confinement beyond the
  generic level only at 13 (cube level) and 37 (ninth level) (investigator only; negatives
  spot-checked at 61, 97, 109 and 4033 by check-scope). Non-confinement elsewhere is computed,
  not derived: the mechanism gives sufficient conditions and makes no negative predictions.

The 37-specific input is the coset triple (4, 3, 5), which is three discrete logarithms mod 37.
The investigators summarised it as "2^6 ≡ 3^3 (mod 37)", but that congruence fixes only the
first entry (partial, check-scope).

**Honest status after the checks.**

- Proved and checked three times: 4850 is ninth-power confined at 37 for the reasons above, and
  therefore so are its six relatives. The norm formula (*) has two independent symbolic proofs
  over GF(2), each with an independent field check. The 37-specific steps are small finite
  computations (a gcd and six polynomial reductions mod a sextic), and three checkers reproduced
  them.
- Repairs needed, all supplied by the checkers:
  - a missing step in the derivation of (*);
  - a proof that η_0 is not in F8, which had only been observed numerically;
  - a norm-based treatment of the diagonal, replacing a computed fact;
  - narrowing the "2^6 = 3^3" claim;
  - corrected scope wording for composite sizes.
- Not covered by the proof:
  - the class logs mod 27: the norm argument gives log ≡ 0 mod 9 and cannot tell 0, 9 and 18
    apart;
  - why 37's coset data are (4, 3, 5);
  - non-confinement at other sizes.

## 2. The structure

### 2.1 The hexagon identity

4850 = F(a, b) = s^3 + P^2 s^2 + P^3 + P^2 + P, with a = x + 1/x, b = y + 1/y, s = a + b and
P = ab. Multiplying by s collapses its 40 terms to 12:

    4850 · (a + b) = D4(a) + D4(b) + D5(a) D2(b) + D2(a) D5(b) = Hex(x, y) + Hex(y, x),

where D_n are Dickson polynomials and Hex_{p,q} = {±(2p,0), ±(p,q), ±(p,-q)} with (p, q) = (2, 5).
This holds as a Laurent identity over GF(2), with no reduction mod 37.

- Verified: verify-identities `claim12.py` (as a Laurent product, as an identity in F2[a, b], and
  at all 1369 characters).
- Found by: reciprocity `step11_numerator.py`, normform `step2_identities.py`, relations
  `sparse.py` (as the closed form λ_4850 (t_j + t_k) = t_{5j} t_{2k} + t_{2j} t_{5k} + t_{4j} + t_{4k}),
  model19 `verify_identity2.py`.

### 2.2 The order-3 symmetry from 5^2 + 3·2^2 = 37

Over Q, the hexagon Hex(x, y) is mapped to itself by the rational order-3 matrix
R = [[-1/2, -3/5], [5/4, -1/2]], and its transpose Hex(y, x) by the transposed matrix. The two
matrices agree mod m iff m divides the numerator of 5/4 + 3/5 = 37/20, that is, iff m = 37. Mod 37,
M = [[19, 8], [8, 19]] (determinant 1, M^3 = -I) fixes G = 4850 · s. It does not fix 4850 or s
separately, and it does not fix G over Z. The full stabiliser of G in GL2(F37) has order 24,
against 8 for D4. For general (p, q) the condition reads q^2 + 3p^2 ≡ 0 (mod m) ("-3 type").

- Verified: verify-identities `claim12.py` (primes where the rotations agree: [37]; stabiliser
  order 24).
- Found by: reciprocity `step11_numerator.py` and `step12_symmetry.py` (as R3 = [[18, -8], [-8, 18]],
  eigenvalues 10 and 26), model19 `verify_identity.py`, normform `step5_calib.py` (as M0 = -M).

### 2.3 The 45° frame and the closed form W^4/(t t)

The map (x, y) → (xy, x/y) is invertible mod 37. It sends 4850 to rule 10491524 of radius 6, and
conjugates M to diag(27, 11), which up to sign is T = diag(10, 26) (10 and 26 are the primitive
cube roots of 1 mod 37). In this frame three identities hold.

- π · 10491524 = orbit(4,4) + orbit(7,3), with π = ab. This is an exact Laurent identity.
- Mod 37, that right-hand side equals h^4 in F2[(Z/37)^2], where
  h = Σ_{u ∈ μ6, e = ±1} x^u y^{e/u} is a 12-point set fixed by T.
- The eigenvalue of h is W(α, β) = Σ_{u ∈ μ3} t_{uα} t_{β/u}. Hence λ'(α, β) t_α t_β = W^4 at
  every character, and λ_4850(j, k) = W(α, β)^4 / (t_α t_β) off j = ±k.

Verification:

- Verified at all 1369 characters with 0 failures: verify-identities `claim34.py`,
  verify-reduction `v1_identities.py`, check-chain `c2_chain.py` (1296 off-diagonal characters,
  computed from 4850's own orbit list).
- Found by: normform `step2_identities.py` and `step12_core.py`, model19 `kloosterman.py`.

### 2.4 The relatives as σ-conjugates

Let σ be Frobenius x → x^(2^6). On eigenvalues at 37 it acts as the dilation by 2^6 = 27 ≡ -10.
It has order 3 on F(2^18) and fixes F64. Write R1 = 10491524, R2 = 20982139 and R3 = 178279803.
Then, exactly, mod 37:

    R2 · ab = (R1 · ab) dilated by 10,     R3 · ab = (R1 · ab) dilated by 26 = 2^12,

each side having 12 terms. Off the axes this gives λ_R2 = λ_R1^64 π^63 and
λ_R3 = λ_R1^4096 π^4095. π is a cube and 3 divides 63 and 4095, so the factors π^63 and π^4095 are
ninth powers. On the axes, R2 restricts to Ψ7(t) and R3 to Ψ3(t)Ψ11(t). Both are cyclotomic, and
their values at 37 were computed to be ninth powers. The identities also explain why R1, R2 and R3
share one exact mod-27 class pattern. Multiplying a log by 64 acts as multiplication by 10 mod 27,
which fixes 0, 9 and 18. And π^63 is a 27th power. So the pattern cannot change. The other three
relatives are exact multiples of 4850:

- 482758 = 4850 · (1+a)(1+b);
- 8438150 = 4850 · (1 + t(xy))(1 + t(x/y));
- 43250486 = 4850 · (1+a)^2 (1+b)^2.

The unit factors are rule-150 type, and their values are ninth powers at 37.

- Verified: verify-identities `claim34.py` (claim 4: the dilation identities, the eigenvalue
  relations at 1296 characters, the axis polynomials); verify-specificity `t4_calibration.py`
  part 5 (all six dependences and their units).
- Found by: relations `trio.py`, `sigma_exact.py` and `shells.py`; reciprocity
  `step10_identity.py` (the same identity as F(R2) · G = F(R1) · G' in GF(2)[a, b]); normform
  `step12_core.py` (all three as transforms of one core f0 = h/π); calibration `triple.py`.
- Investigator only: in the full radius-6 family (2^28 rules), exactly R1, R2 and R3 share one
  F64-norm vector (reciprocity `step15_norm_census.py`). Also, σ-partners of this kind are common
  among confined rules in general: 116 of the 125 ninth-power rules have one, against 0 in random
  sets (relations `sigma.py`).

### 2.5 What the structure alone settles

In the 45° frame each of 4850's 11 classes has a type d = log2(β/α) mod 6, folded by d ~ -d.
Before the norm proof, the structure explained eight of the 11 classes (verified,
verify-reduction `v4_claim3.py`; verify-specificity `t4_calibration.py`):

| 4850 class | type | explanation |
| --- | --- | --- |
| (0,1), (1,7) | d = 0 | W = t_x^2 exactly, then Legendre bookkeeping |
| (1,1) | diagonal | F(t, t) = t^2 (1 + t + t^2)^2, cyclotomic exponents |
| (1,2), (1,8), (1,10) | d = ±2 | two of W's six terms cancel, leaving W = t_x t_y t_z exactly; then Legendre bookkeeping |
| (1,4) | d = 3 | a stabiliser in <D4, 2I, T> with odd Frobenius multiplier forces a 27th power |
| (1,6) | d = 3 | F(2^9)-valued for every symmetric rule |
| (1,3), (1,5), (1,13) | d = ±1 | **no structural reason**: the residual |

"Legendre bookkeeping" uses rule 90's law t_j^29127 = ρ^{χ(j)}, which verify-reduction checked as
an exact group-ring identity. The three residual classes form a single <D4, T, 2I>-orbit of
W-arguments, so they are one condition (verified, verify-specificity t4). Section 3 is the proof
of that condition. It actually covers every off-diagonal class at once.

## 3. The proof of the last condition

**Setting.** Let p be a prime with ord_p(2) = 2e and 3 | e. Then K = F(2^e) contains the t_j,
k = F(2^{e/3}), and σ = Frob^{e/3} generates Gal(K/k). Because t is even, σ acts on indices as
multiplication by a primitive cube root of 1, w = -2^{e/3} mod p. At 37: e = 18, k = F64, w = 10.
Write η(x) = Σ_{u ∈ μ6} ζ^{ux} ∈ k, and set

- X = η(α), Xa = η((1-w)α), Xb = η((2-w)α), Xb' = η((2-w^2)α);
- Y, Ya, Yb, Yb' the same with β in place of α.

The norm formula is

    (*)  N(W) = X^2 Y^2 (1 + X + Y) + XY (X Ya + Xa Y) + XY Xa Ya + Xa Ya (X + Y) + Xb Yb + Xb' Yb'.

### Step 1. The norm formula (*)

**(1a) The resolvent core: verified.** Put A_i = t_{w^i α} and B_i = t_{w^i β}. Then
W = A0B0 + A1B2 + A2B1, and N(W) = W · σW · σ^2 W. check-algebra re-derived the expansion of this
product in the symmetric and cyclic functions e1, e2, P, S1, S2 of the A_i and B_i, and checked
it as an identity in F2[A0..B2]. Since the identity has F2 coefficients, it needs no cube root of
1 in k. It therefore also covers primes with e/3 odd (19, 67, 139), which the investigator's
resolvent sketch had tacitly excluded. check-scope proved the same statement independently: by a
Groebner basis over GF(2), N(W) - (*) lies in the ideal generated by e3 + e1^2 (that is,
η(2x) = η(x)^2), and the difference is not zero without that relation. Files: check-algebra
`a1_symbolic.py` (CHECK 1); check-scope `sc3_symbolic.py`.

**(1b) Elimination to (*): verified with repair.** Evaluating the symmetric functions uses
t_x t_y = t_{x+y} + t_{x-y}, t_0 = 0 and μ6-invariance of η:

- e1 = X, e2 = X + Xa, e3 = X^2, P = X^3 + X Xa;
- S1 = η((2+w)α) + Xb, S2 = η((2+w^2)α) + Xb'.

The investigator's sketch (the docstring of `norms/s2_universal_formula.py`) listed only
η((2+w)x) = η((2+w^2)x). That is not enough: with η((2+w)x) left free, a term
X Xa (Ya + Yc) + Y Ya (Xa + Xc) is left over. The missing fact is exact and short. From
1 + w + w^2 = 0 we get 2 + w^2 = 1 - w and 2 + w = -w^2(1 - w), so η((2+w)x) = η((2+w^2)x) = Xa.
The elimination also uses the auxiliary relation X Xa = Xb + Xb', which the sketch does list; it
is the evaluation of S1 + S2 = e1 e2 + e3, or equivalently the mod-2 product rule. With both, the
reduction equals (*) exactly. (*) is unchanged when w is replaced by w^2, so the choice of cube
root does not matter. Nondegeneracy holds for all 75 family primes below 2000. Files:
check-algebra `a1_symbolic.py` (CHECKs 3 to 5).

**(1c) The mod-2 product rule: verified.** η(x)η(y) = Σ_{v ∈ μ6} η(x + yv), including the case
η(0) = 6 = 0. It holds for all x, y at 13, 19, 37, 61, 67, 97, 109 and 139, and as an exact
identity in Z[Z/p] at 13, 19 and 37. The case η(0) never arises in the auxiliary relation, since
it would need p to divide 28. File: check-algebra (same scripts); also checked exactly in
Z[Z/37] by check-chain `c1_certificate.py`.

**(1d) (*) against the field norm: verified.** check-algebra computed the field norm
z^{1+q+q^2} directly, in its own field. (*) matched it at every character for p = 13, 19, 37, 61,
67, 97, 109 and 139: 49,644 characters in all, with 0 failures. Three deliberately broken
versions of (*) matched at 0 characters, so the test is sensitive. check-scope matched (*) at
every pair for 13 to 109 and at 3240 sampled pairs at 181. Files: check-algebra
`a2_star_numeric.py` with `flib.py` and its two logs; check-scope `sc3_symbolic.py`.

### Step 2. The certificate at 37

**(2a) Coset data: verified.** w = -2^6 = 10. Then 1 - w = 28 = 2^34, 2 - w = 29 = 2^21 and
2 - w^2 = 13 = 2^11, which gives cosets (log2 mod 6) of (4, 3, 5). With w^2 as the generator they
are (4, 5, 3), which gives the same relation. Files: check-algebra `a3_step2_37.py`, check-chain
`c1_certificate.py`, check-scope `sc1_core37.py`.

**(2b) The relation and its factorisation: verified.** Since μ6 = <2^6>, all periods are
η_0^{2^i}. Putting X = x, the coset data give Xa = x^16, Xb = x^8 and Xb' = x^32. The auxiliary
relation then reads x^17 = x^8 + x^32, that is, x^8 (x^24 + x^9 + 1) = 0. The polynomial facts:

- gcd(x^24 + x^9 + 1, x^63 + 1) = x^9 + x^3 + 1 = (x^3 + x^2 + 1)(x^6 + x^5 + x^4 + x^2 + 1);
- both factors are irreducible;
- the sextic divides x^21 + 1 but not x^7 + 1.

In F64 the relation has exactly 10 solutions: 0, the 3 roots of the cubic, and the 6 conjugates of
η_0. Files: the same three scripts, plus check-scope `sc2_certificate.py` (sympy, in its own F64).

**(2c) η_0 is a root of the sextic: verified with repair.** η_0 lies in F64 because Frobenius^6
sends η(1) to η(64) = η(27) = η(1). In `norms/` the facts η_0 ∉ F8 and η_0 ≠ 0 were only
observed numerically; in the investigator's chain this was a silent gap. The checkers proved
them. ord_37(2) = 36, so Φ37 is irreducible over F2, and ζ^1 through ζ^36 are linearly
independent. The six periods are sums over disjoint μ6-cosets, so they are distinct and nonzero,
and η_0 + η_3 is a sum of 12 distinct basis elements. Hence η_0 is a root of the sextic and has
order exactly 21: a cube in F64*, but not a ninth power. The argument uses only the auxiliary
relation, not (*), so it is not circular. Files: check-algebra `a3_step2_37.py`, check-chain
`c1_certificate.py` part (d), check-scope `sc1_core37.py` (rank of {ζ^i} = 36).

### Step 3. The closed form and N(λ)

**Verified.** Reduced mod the sextic, (*)_d (with Y = X^{2^d}) is congruent to (XY)^{n(d)}, with
n = (2, -1, -4, 2, -4, -1), for each d = 0..5. check-chain checked this with the true exponents
(up to 1056), not reduced mod 63. A minor point: for odd d, XY has order 7, so n(d) is fixed
only mod 7. The stated values are valid representatives, and this does not affect the
conclusion.

Two exact identities hold at all characters. N(t_x) = Π_{u ∈ μ3} t_{ux} = η(2x) = η(x)^2 is an
identity in the group ring, and λ t_α t_β = W^4 holds at all 1296 off-diagonal characters with 0
failures. Together they give

    N(λ) = (XY)^{4n(d) - 2},   exponents 6, -6, -18, 6, -18, -6.

All the exponents are divisible by 3 because n ≡ 2 mod 3, and XY lies in μ21, so N(λ) lies in
μ7 = F8*. This holds at all 1296 characters. The investigators also wrote a theta form,
N(λ) = (θ(α)θ(β))^{2(2n-1)}. It is correct as well, but it needs η = θρ (index 6 = index 3 ×
index 2), which check-chain verified exactly in F2[Z/37]/(J). Files: check-chain
`c1_certificate.py`, `c2_chain.py` and `c5_theta_form.py`; check-scope `sc1_core37.py`,
`sc2_certificate.py` and `sc8_odds.py`.

### Step 4. The criterion

**Verified.** N(z) = z · z^64 · z^4096 = z^4161, and 4161 · 63 = 2^18 - 1. The image of a
generator g of K* has order 63, so N maps onto F64*. Hence z = g^L has N(z) in μ7 iff 9 divides
L, iff z is a ninth power. Equivalently, λ^29127 = N(λ)^7. The two tests agreed on 400 random
elements and at all 1368 eigenvalues (check-chain `c2_chain.py`). They also agreed on all of K*
(verify-reduction `v5_claim4.py` (a)), and at every character (check-scope).

### Step 5. The diagonals j = ±k

**Verified with repair.** F(t, t) = t^6 + t^4 + t^2 = t^2 (1 + t + t^2)^2 = t(x) t(x^5) as Laurent
polynomials, so λ(j, ±j) = t_j t_{5j} at all 72 diagonal characters. The investigators covered
this case through a computed fact: rule 90 is Legendre, that is, 1 + ζ is a cube but not a ninth
power. check-chain replaced it with the norm route: N(t_j t_{5j}) = η(j)^2 η(5j)^2 = η(j)^66,
since log2(5) = 23 ≡ 5 mod 6. Then 66 ≡ 3 mod 21, so the norm lies in F8*. check-scope showed
that the Legendre fact itself follows from N(t_x) = η(x)^2 together with η_0 being a cube.
All 72 diagonal eigenvalues are ninth powers, and none is a 27th power. Files: check-chain
`c3_diagonal.py`, check-scope `sc1_core37.py` (e).

### Step 6. "The 37-specific fact 2^6 ≡ 3^3 (mod 37)"

**Partial.** What holds is narrower. Since (1 - w)^2 = -3w and -w = 2^6, we get
log2(1 - w) = (log2 3 + 6)/2 mod 18. So A = 4 is equivalent to log2 3 ≡ 2 (mod 12), which is
equivalent to 3^3 ≡ 2^6.

What does not hold:

- Under the cube hypothesis the residual is forced exactly when A = 4. But the cube property
  itself needs {B, B'} = {3, 5}. Those are separate congruences: 2 - w = -2^3, and
  2 - w^2 = -3 · 2^3.
- With the auxiliary relation alone, the residual is forced for 12 triples, including some with
  A = 1, 2 or 3.
- 2^6 ≡ 3^3 (mod m) holds only for m dividing 37, so the stated "iff" has no free parameter.

The 37-specific input is the whole triple (4, 3, 5). File: check-scope `sc2_certificate.py`
(forcing table over all 216 triples in its own F64).

### End to end

**Verified.** check-chain rebuilt 4850 from its bits and computed all 1368 nonzero eigenvalues in
its own field. All lie in F(2^18) and all are ninth powers; none is zero. 216 of them are 27th
powers: the classes (1,4) and (1,6). The class logs mod 27 in census order,
[18, 9, 9, 18, 0, 9, 0, 9, 9, 9, 18], match the dossier exactly. The predicted log mod 63, from
(XY)^{4n-2} off the diagonal and η(j)^66 on it, equals the actual value at all 11 classes.
check-scope found the same in its own field model.

One caveat: the proof predicts only log ≡ 0 mod 9. The norm to F64 sees the log mod 63, and the
3-part of that is mod 9 only. So which of 0, 9 and 18 occurs mod 27 is not determined by the
argument. Files: check-chain `c4_endtoend.py`, check-scope `sc1_core37.py`.

### What is derived and what is computed

This is check-scope's accounting, which the other two checkers' findings agree with.

- **Derived**, valid at every size in the setting:
  - the hexagon and reduction identity;
  - λ t_α t_β = W^4;
  - the char-2 diagonal derivative formula;
  - (*) and the auxiliary identity;
  - N(t_x) = η(x)^2;
  - the norm criterion;
  - η_0 ∉ F8, via the normal basis.
- **Computed at 37**, all small:
  - 2 is a primitive root with ord 36, so k = F64 and there is a single orbit;
  - the triple (4, 3, 5);
  - χ(2) = χ(5) = -1;
  - the six reductions mod the sextic. These are formal once the triple is known; they give
    n(d) ≡ 2 mod 3.

## 4. The hexagon family

### 4.1 Definition and reduction

f_{p,q} = (Hex_{p,q}(x, y) + Hex_{p,q}(y, x)) / s, with Hex_{p,q} = {±(2p,0), ±(p,q), ±(p,-q)}.
s always divides, and 4850 = f_{2,5}. A member is of -3 type at m when q^2 + 3p^2 ≡ 0 (mod m).
At 37 this means q ≡ ±16p, since 16^2 ≡ -3.

At 37 every -3-type member is a dilate of 4850: if (p, ±q) ≡ l · (2, 5) with l = ±2^e, then
f_{p,q} · s ≡ dil_l(4850 · s) mod 37. So off the diagonals,

    λ_{p,q} = λ_4850^{2^e} · s^{2^e - 1}.

This is verified for 9 members at 1296 characters each, with 0 failures (verify-identities
`claim5.py`). The investigators' general reduction formula is λ_{p,q} = W(2pα, 2pβ)/(t_α t_β) off
the diagonals. On the diagonals it is t_{pj} t_{qj} / t_j, or 0 when p ≡ q mod 2. This formula
is verified on 27 members with 0 failures (check-scope `sc5_family.py`). The family investigator
checked it at 30,096 characters (investigator only, `family/step2_theory37.py`). Its docstring's
"proof in the report" refers to a file that does not exist; the dilation argument and
check-scope's derivation take its place.

### 4.2 The classification at 37 and the dichotomy

**Verified.** Among -3-type members at 37:

- p a quadratic non-residue: ninth-power confined, odd part 29127;
- p a residue: cube-confined only, odd part 87381.

Parity does not change the level at 37. A same-parity member has zero eigenvalues on the
diagonals, and zeros do not enter the odd part.

The derivation (check-scope): off the diagonals, the μ3-exponent of N(λ) is
(n(d)χ(2p) - 2)(χ(α) + χ(β)). It vanishes iff χ(p) = -1, using n ≡ 2 mod 3 on even d and
χ(2) = -1. On the diagonals the class is 2χ(j)(2χ(p) - 1), or the value is 0 when p ≡ q mod 2.
Equivalently, in the dilation form above, the member is ninth-confined iff e is even, iff l is a
square, iff p = 2l is a non-residue.

Fourteen members were checked by four methods (eigen.odd_part, the direct level, the mechanism's
prediction, and the investigators' rule), all in agreement. These are (2,5), (5,6), (2,32),
(8,17), (6,15), (13,14) and (14,2) on the non-residue side, and (1,16), (1,21), (3,11), (7,1),
(9,4), (12,7) and (4,27) on the residue side (check-scope `sc5_family.py`).

Investigator only:

- The spectrum depends only on k = ind_2(p) mod 18 and on parity: 36 cases, with one
  representative each computed by eigen.odd_part, all as predicted (`family/step8_classify.py`).
- All 22 -3-type members with p, q ≤ 20 fall on the dichotomy (`family/step1_map37.py`).
- None of the 22 "+3 type" members (q^2 ≡ 3p^2) is confined at all.
- A twin-digit identity d_NR + d_QR = ε(χ(α) + χ(β)) holds at every off-diagonal character
  (`family/step14_twins.py`).

### 4.3 The cube-level analogue at 13

**Verified.** At 13 the condition is q ≡ ±6p, and k = F4. Symmetric values lie in F(2^6), and
63 = 9 · 7. A member is cube-confined (odd part 21 rather than 63) iff p is a non-residue mod 13
and p ≡ q mod 2.

check-scope derived the 2 × 2 table of N(W) by coset pair, (η0, 1; 1, η1). It follows from (*)
with the triple (1, 1, 0) and η0 a primitive cube root of 1 in F4. From the table, the
off-diagonal part is a cube iff p is a non-residue. Parity enters only through the diagonal: if
p ≡ q mod 2 the diagonal eigenvalues are 0; otherwise N(λ) = η(j)^-2, which is never 1. The
five non-residue same-parity members (5,9), (7,3), (11,1), (2,12) and (6,10) have odd part 21,
and the other eight checked have 63 (check-scope `sc5_family.py`, `sc6_negatives.py`). All 60
-3-type members with p, q ≤ 20 match the rule (investigator only, `family/step5_map13.py`). This
is the same reasoning one 3-adic level down. It also needs the char-2 derivative formula on the
diagonal, which is not part of 4850's own proof.

### 4.4 The size survey

- **The mechanism's hypotheses** (verified, check-scope `sc4_sizes.py`). The setting is: m odd,
  -1 ∈ <2>, 3 | e, and w = -2^{e/3} a primitive cube root of 1 in every prime component.
  check-scope enumerated every m ≤ 200,000 in the setting and every divisor of 2^36 - 1. Within
  the setting, f = e/3 = 6 (k = F64) holds exactly for m ∈ {37, 109, 4033}, where
  4033 = 37 · 109 = Φ36(2). Adding the single-orbit condition (2 a primitive root) leaves only 37.
- **Negatives** (verified, check-scope `sc6_negatives.py`, `sc7_size4033.py`).
  - At 61, 97 and 109 the hypotheses fail: at 61, f = 10 and η is not a cube; at 97, 2 has index
    2; at 109, 2 has index 3 and η is not a cube. All members tested there, and 4850 itself, are
    at level 0, and (*) agrees with the direct level as far as it can decide.
  - At 4033 (not a single orbit), 428 of 3997 and 446 of 3999 sampled eigenvalues of two members
    are ninth powers, which is the chance rate of about 1/9.
- **The family survey** (investigator only, `family/step3_sizes.py`, `step7_bigprimes.py`,
  `sizes_table.log`). It covered every odd m ≤ 400 for which r^2 ≡ -3 is solvable (57 sizes),
  plus 421, 541 and 613. Members confined beyond the generic level appear only at 13 (level 1)
  and 37 (level 2). Sizes whose symmetric value field has no 3-torsion (19, 43, 67, 139, ...) are
  vacuous, because every symmetric rule is trivially confined there. They were excluded, and the
  same applies to normform's and model19's results at 19.
- **Same conclusion at fewer sizes** (investigator only): normform `step20_othersizes.py`,
  model19 `sizes.py` and `wtest.py`, norms `s7_other_sizes.py`.

### 4.5 Beyond the hexagon (investigator only)

- 24-point <D4, T>-orbit numerators never reach the ninth level at 37 (`family/step4_lambda.py`).
- Some unions of two orbit numerators do reach the ninth level relative to π, for example
  W(c) + W_3(7c) and W_3(2c) + W_6(5c) (`family/step9_sums.py`). Built with even exponent
  representatives so that the diagonal vanishes (`step12_evenreps.py`), they give ninth-confined
  rules; two were computed, both with odd part 29127.
- The proof does not cover these rules. They form tier T3 of the registered test (section 7.2).

## 5. What was refuted or corrected along the way

### 5.1 "The order-3 symmetry forces cube confinement": refuted as an argument

**Who claimed it.** normform (steps 5 and 6) and threeadic (steps 9 and 11) argued from a lemma:
if the μ27-residue R of a D4-symmetric rule is invariant under a partial Frobenius P_g, then
(2^g - 1)R ≡ 0 mod 27. Here P = diag(1, 27) in the 45° frame, and g = 6 gives cubes. grouping
used the same lemma for its property (A).

**The lemma is true.** No false prediction among the 144 hexagon rules and all 32,767 radius-4
rules (verify-specificity `t6_lemmas.py`; verify-reduction `v3_claim2.py`).

**The inference is what fails.** The symmetry supplies R(Tc) = R(c), and P = (sign) · 2^12 · T.
So R(Pc) = 2^12 R(c) = 19 R(c) mod 27. P-invariance at the μ27 level therefore holds iff
18R ≡ 0 mod 27, iff R ≡ 0 mod 3. That is, it is equivalent to cube confinement and cannot be used
to derive it. At the mod-9 level, where the symmetry does give invariance, the lemma's
conclusion (2^6 - 1)R ≡ 0 mod 9 is empty.

**Counterexamples.** Consider the family f_O = G_O^4/π over all 63 <D4, T>-orbits. Every member
is T-invariant and satisfies every premise of the argument, yet only 27 are cube-confined. The
smallest counterexample has radius 10 and odd part 262143 by eigen.odd_part (verify-reduction
`v2_claim1.py`, `v6_extra.py`; verify-specificity `t3_soundness.py` (D)).

**Sound uses of the symmetry remain.** The stabiliser argument for the d = 3 classes, with an
odd Frobenius multiplier, is sound (verify-reduction `v4_claim3.py`). So are reciprocity's ties
at the ninth-power level, since they are 63rd-power ratios (`reciprocity/step19_proof_checks.py`,
investigator; the same tie groups were confirmed by verify-reduction v4).

### 5.2 The one-trit reduction: corrected, then superseded

threeadic `step11_reduction.py` claimed that the symmetry plus the three exact line
factorisations force cubes and leave ninth-power confinement to a single trit, whose value for
4850 is 0. The cube step rested on 5.1. verify-specificity `t4_calibration.py` gave the corrected
statement. The residual is one orbit of classes, {(1,3), (1,5), (1,13)}. It carries 1 trit if
cube-ness is granted and 2 trits if not, because the residual argument has no Frobenius
stabiliser and no exact t-factorisation. The norm proof (section 3) later covered this residual,
and every other off-diagonal class with it.

### 5.3 The calibration's p-value: corrected reading

The calibration investigator found a local p of 3.4e-4 and, after look-elsewhere across 121
(family, size, q) combinations, a global p of 0.0034. These are probabilities under a null with
no structure. Once the hexagon structure is taken into account, the honest chance probability for
the residual was about 1/9, and the question was settled by proof, not by the calibration.
Section 6 gives the details.

### 5.4 Fable's congruence is a restatement

Fable's round-2 congruence was R(4850) · D10 · D26 = D8 · D6 · D23, with D_n = f(x^n, y^n). At 37
every dilation is a Frobenius power: D_n = f^{2^k} with n ≡ ±2^k. Here D10 = f^{2^6},
D26 = f^{2^12}, D8 = f^{2^3}, D6 = f^{2^9} and D23 = f^{2^15}. So the left side is
f^{1+2^6+2^12} = N(f) and the right side is f^{2^3+2^9+2^15} = N(f)^8. The congruence therefore
says N^7 = 1 wherever f ≠ 0, which is λ^29127 = 1: ninth-power confinement itself, not a
certificate for it. Over all 32,767 radius-4 rules it holds for exactly the 21 ninth-confined
ones (`grouping/fable_congruence.py`; investigator only). The exponent bookkeeping is two lines,
and the criterion it restates was verified independently (verify-reduction `v5_claim4.py` (a)).

### 5.5 Corrections from the final proof check

These were all listed in sections 1 and 3. In summary:

- (a) The written derivation of (*) omitted η((2+w)x) = η((1-w)x). The `norms/` docstring says
  "PROVED (algebra, see report)", but no report exists anywhere in `deep/`. check-algebra
  supplied the step.
- (b) The resolvent sketch tacitly assumed a cube root of 1 in k. The F2 polynomial identity
  removes that assumption.
- (c) η_0 ∉ F8 and η_0 ≠ 0 were numerical only. They are now proved via the normal basis.
- (d) The diagonal relied on the computed rule-90 Legendre fact. It is now handled through the
  norm, and the Legendre fact is itself derived.
- (e) "2^6 ≡ 3^3 is the 37-specific fact" is partial: the whole triple (4, 3, 5) is needed.
- (f) "k = F64 only when ord_m(2) = 36, i.e. m | 4033" is false for composites. 462 values of m
  have ord_m(2) = 36. Of these, 481, 1417 and 52429 have -1 ∈ <2> and -3 a square, but
  Frobenius^6 acts trivially mod 13 there. The correct statement is: in the setting, f = 6 iff
  m | 4033.
- (g) For odd d, n(d) is determined only mod 7. This is harmless.
- (h) For general family members and for the parity rule at 13, the diagonals need the char-2
  derivative formula, not 4850's factorisation.

### 5.6 Smaller points (investigator only)

- Unrestricted half-Frobenius certificates (mechanism 5) are vacuous at 37. Using all 38
  directions, every zero-free ninth-confined rule has one, because the 38 × 38 Legendre and
  19-part character matrices are invertible (`threeadic/step4_vacuity.py`). Mechanism 5 explains
  something only when its unit product is sparse.
- grouping's partial-twist relation puts R2 and R3 in span{R1, rR1, r^2 R1} modulo F(2^9). It is
  specific to confined rules rather than to the triple: verify-specificity `t2_nulls.py` found 0
  of 1000 random rules in the span, but 16 of 75 zero-free confined rules with a nonzero 19-part
  were in it. The exact σ-identity of 2.4 supersedes it.
- Pilot 7 noted that F' = N_{F(2^54)/F(2^18)}(π + c) holds "without a visible reason". The reason
  is π · F' = h^4 (2.3). The literal shape "π^3 + square" is not itself a mechanism: only 2 of the
  1024 rules of that shape are ninth-confined (`normform/step18_cubesq_family.py`).

## 6. The chance calibration, with the corrected reading

### 6.1 What was measured (calibration/, investigator only unless noted)

- **Per-class rates** (`rates.py`). In the radius-4 family, the axis and the diagonal are
  ninth-OK 0.469 of the time each, the eight generic classes 0.112 to 0.135 each, and (1,6) is
  forced. For the new radius-5 rules the generic rates are 0.111 to 0.115. At radius 4 the
  classes are strongly dependent at high order. After the 21 fully confined rules are removed,
  the joint counts match independence (`rates_refined.log`).
- **Decoy test** (`decoy.py`). On the non-cube cells, where every generic class is a non-cube and
  no mechanism prefers any pattern, the independent model is calibrated at full order: χ²/cell is
  1.13 at radius 4, 1.00 for the new radius-5 rules and 1.00 for the new radius-6 rules. The
  cube-level cells show large excesses (χ²/cell up to 98 at radius 4): there is structure at the
  cube level.
- **Expected chance count.** The expected number of chance ninth-power rules at radius ≤ 4 is
  3.4e-4, close to Fable's estimate of about 4e-4. That makes 4850's local p 3.4e-4
  (`lookelsewhere.py`).
- **Look-elsewhere.** Over the 121 (family, size, q) combinations the project has examined, where
  an event this improbable would have been noticed, the global p is 0.0034 (about 9.3 effective
  trials).
- **The relatives' shared pattern.** Under independence, the chance of two or more chance
  radius-6 rules landing on one noticeable mod-27 pattern is about 1.2e-9 (`triple.py`).

### 6.2 The corrected reading

**What the p-values measure.** 3.4e-4 and 0.0034 are the probabilities that a rule with no
structure would be ninth-confined. They show, correctly, that 4850 is not a typical rule. They do
not measure the doubt that remained once its structure was visible. The hexagon numerator, the
order-3 symmetry and the 45° closed form settle eight of the 11 classes by exact identities and
stabilisers (2.5), and leave one orbit of classes worth 1 or 2 trits.

**The honest residual chance** (verified, verify-specificity `t4_calibration.py` and
`t5_residual_extra.py`). Conditioned on the structure, the chance probability for the residual
was about 1/9:

| null | probability |
| --- | --- |
| two uniform trits | 0.111 |
| one trit, if cube-ness is granted | 0.333 |
| normform's trinomial null at d = 1, over all a of order 1387 | 0.125 |
| pooled unforced W classes at 13, 61, 97, 109 and 241 | 0.117 |

**How rare the structure is** (verified, verify-specificity `t1_shape.py` and `t2_nulls.py`).

- Among the 125 recorded ninth-power rules, s · f is a single <D4, M0>-orbit only for 4850, and
  π · f is a single <D4, T>-orbit only for R1, R2 and R3.
- Of all 3^10 symmetric digit functions, 0.27% have any partial-Frobenius symmetry and 0.135%
  have the particular one. On real rules the rates are 0.12% to 0.25%.

**What follows.** Before the norm proof the evidence was a rare structure that is visible in the
polynomial, plus one event of chance probability about 1 in 9. A calibration of this kind cannot,
on its own, tell "a mechanism" apart from "structure plus a coincidence", and the small global p
was not evidence for a mechanism beyond the structure. The proof settled the question.

**The relatives' triple.** Here the calibration was right that the shared pattern is not chance.
It is the exact σ-identity, which also explains why the three patterns coincide exactly (2.4).

### 6.3 After the proof

No chance component is left for 4850 at 37. The calibration remains useful as the null model for
future census hits. Its decoy result, that independence is calibrated at full order on the
non-cube cells, still stands as an investigator result.

## 7. What is left open, the registered test, and Lean

### 7.1 Open items

1. **Write the proof down.** The repaired proof exists only as the docstrings of
   `norms/s1` to `s9` plus the three check logs. Section 3 is an outline that cites where each
   step is checked; it is not a proof document. The family's "proof in the report" for the
   reduction theorem likewise points to nothing.
2. **Why (4, 3, 5).** Nothing explains why 37's coset data take these values. The congruence
   2^6 ≡ 3^3 accounts only for the first entry.
3. **Negative results are computed.** The mechanism gives sufficient conditions only.
   Non-confinement at 61, 97, 109, 181 and 4033, and across the family survey, is observed, not
   derived.
4. **Logs mod 27.** The norm argument does not say which of 0, 9 and 18 occurs. The d = 3
   classes (1,4) and (1,6) are 27th powers by the stabiliser argument; the other classes' values
   mod 27 are unexplained.
5. **Other numerators.** The ninth-level two-orbit numerators at 37 (4.5) are observed, not
   explained.
6. **General m.** (*) holds at every prime in the setting. No statement for composite m, and no
   general condition under which (*) forces confinement, has been worked out.
7. **Results the report relies on that no verifier re-ran:**
   - the list of seven unexplained rules (`calibration/condition.jsonl`);
   - the family survey beyond the spot checks;
   - the calibration numbers in 6.1;
   - the 36-case classification at 37.

### 7.2 The registered test: the 47 predictions in family/predictions.json

**The proposal.** `family/step13_predictions.py` wrote 47 predictions of period odd parts
(predictions.json, sha256 `bd1965d3...527d`). It computed 6, which all agreed, and held out 41.

| tier | entries (held out) | content |
| --- | --- | --- |
| T0 | 19 (17) | classification at 37 (non-residue p: 29127, residue p: 87381) and at 13 (21 or 63) |
| T1 | 8 (6) | other sizes (61, 97, 109, 111, 181, 193): exact odd parts, assuming the non-3 part is generic |
| T2 | 2 (2) | 481 = 13 · 37 and 703 = 19 · 37: mixed characters generic (heuristic) |
| T3 | 12 (10) | two-orbit numerators at 37, with the twist rule A → As |
| T4 | 6 (6) | the closest analogues of 37 (709, 757, 829, 877, 1213, 1861): 3-part of the odd part only |

**What each tier tests, now that the proof has been checked.**

- T0 at 37 and at 13 follows from the checked mechanism (4.2, 4.3). It tests the arithmetic and
  the construction code; a failure would point to an error in the proof or in the builders.
- T3 is the only tier with new positive content beyond the proof.
- T1, T2 and T4 are negative predictions. The mechanism does not make them, so they test the
  reading "nothing else is confined". T1 and T2 additionally test the assumption that the non-3
  part of the odd part is generic, 2^e - 1.

**Status.** The test has been registered as `examples/hexagon-family`:

- `study.py` holds the protocol: each entry is computed by the family's builders and
  eigen.odd_part with a 45-minute limit, an entry that times out counts as not tested, and any
  mismatch refutes the classification as stated.
- `ledger.jsonl` holds the question and the 41 prediction entries, written at 2026-10-21
  00:04:54 UTC. Its predictions_sha256 matches the file in `deep/family`. The run started at
  00:05:06.

As of 00:46 UTC, `records.jsonl` holds 35 of the 41 results, and all agree with the predictions:
all 17 held-out T0 entries, all 10 T3 entries, the 6 T1 entries and the 2 T2 entries. The six T4
entries remain. The first (m = 709) had been running for about 39 minutes against its 45-minute
limit, which suggests that the T4 entries will be recorded as not tested. No verdict has been
written yet.

**Recommendation.** Let the run finish and judge it tier by tier as above. If the T4 entries time
out, register a cheaper 3-part-only computation (`family/sizes_engine.py`) as a separate test
before running it, rather than changing this one.

### 7.3 What to formalise in Lean

The project's Lean library (`proofs/LatticeProofs`) already provides three things this needs:
`period_dvd_of_val'` (the period divides L when every eigenvalue at 37th roots of unity is 0 or
an L-th root of 1), `Cubes37.r90_val` (rule 90 is cube-confined), and `Ninth37`, which proves
`period 37 … ∣ 29127` for pilot 7's four rules. The axiom policy (`proofs/Axioms.lean`) allows
Lean's standard three axioms only, which rules out `native_decide`. The recommended target is a
`Rule4850.lean` proving `period 37 r4850Offsets ∣ 29127` by the structured route, in this order:

1. **Polynomial identities**, as `linear_combination` certificates in the style of `Ninth37`:
   - 4850 · s = Hex + Hex^T;
   - π · 10491524 = orbit(4,4) + orbit(7,3);
   - the 45° rotation;
   - the three unit multiples (482758, 8438150, 43250486).
2. **Eigenvalue identities in a field with 2 = 0 and X^37 = 1:**
   - λ t_α t_β = W^4;
   - t_x t_y = t_{x+y} + t_{x-y};
   - the mod-2 product rule for η;
   - N(t_x) = η(x)^2.
3. **The norm formula (*)** as a polynomial identity over F2: check-algebra's CHECK 1, or
   check-scope's ideal-membership certificate. This is the general part. Formalised once, it
   gives the mechanism at every prime of the setting.
4. **The 37 certificate in F2[x]:**
   - the gcd and the factorisation;
   - the sextic divides x^21 + 1;
   - the six reductions (*)_d ≡ (x^{1+2^d})^{n(d)} mod the sextic.
5. **η_0 is a root of the sextic.** This needs η_0 ∉ F8, which can be proved either from the
   irreducibility of Φ37 over F2, or, more cheaply, by proving η_0^21 = 1 directly as a
   divisibility Φ37 | η(x)^21 - 1 in F2[x]. That divisibility holds at every primitive 37th root
   of unity in any field of characteristic 2, and it avoids the normal-basis argument.
6. **The group step:** λ^29127 = N(λ)^7, with N(λ) = λ · σλ · σ^2 λ and σ the dilation by 27,
   in the same way as the `t_frob` lemmas.
7. **The diagonals by the norm route:** N(t_j t_{5j}) = η(j)^66, and 21 divides 63.
8. **Assembly** with `period_dvd_of_val'`. Then the relatives: 10491524 by a GL2-invariance lemma
   for the period, and 20982139 and 178279803 by the σ-identity and the axis polynomials Ψ7 and
   Ψ3Ψ11.
9. **The family at 37**, through the dilation lemma of 4.1. This would make the T0 entries at 37
   theorems.

A cheaper cross-check of the conclusion alone is the single group-ring identity
R(4850)^29127 = 1 + J_x J_y in F2[(Z/37)^2]. 29127 has nine binary ones, so this is a product of
nine dilations. It certifies the conclusion without explaining it, and with the standard axioms
only it would have to run in the kernel, which may be too slow at 1369 coefficients.

## 8. Index of scripts

Each entry gives a script and what it proves or checks. Logs and JSON outputs share the script's
name.

### Final proof check

- **check-algebra/**
  - `a1_symbolic.py`: step (1a), the F2 identity for W · σW · σ^2 W; the ω-resolvent form; the
    Newton facts; the elimination to (*) with and without the repair; w ↔ w^2 invariance;
    nondegeneracy for 75 primes below 2000.
  - `a2_star_numeric.py` with `flib.py`: (*) against z^{1+q+q^2} at every character for 8
    primes, with negative controls.
  - `a3_step2_37.py`: step 2 at 37 (log table, cosets, auxiliary relation, gcd, Rabin tests, the
    F64 solution set, η_0 ∈ F64 \ F8).
- **check-chain/** (own dense-modulus field, `clib.py`)
  - `c1_certificate.py`: the F2[x] certificate with unreduced exponents; the product rule in
    Z[Z/37]; the ingredients of the η_0 ∉ F8 proof.
  - `c2_chain.py`: N(t_x) = η^2, the σ action, λ t t = W^4, N(λ) ∈ F8*, and the criterion
    (exponent 4161, surjectivity, random elements).
  - `c3_diagonal.py`: the diagonal, routes A and B.
  - `c4_endtoend.py`: an independent rebuild of 4850 and all 1368 eigenvalues; class logs mod 27
    and mod 63.
  - `c5_theta_form.py`: the theta form and η = θρ.
- **check-scope/** (own dense-modulus field, `cslib.py`)
  - `sc1_core37.py`: the 37 argument in its own field (normal basis, coset data, (*), 4850 at
    all characters, N(t_x) and the Legendre class).
  - `sc2_certificate.py`: the sympy certificate and the forcing table over 216 coset triples.
  - `sc3_symbolic.py`: the ideal-membership proof of (*), and dictionary checks at 13 to 181.
  - `sc4_sizes.py`: sizes in the setting up to 200,000, and the divisors of 2^36 - 1.
  - `sc5_family.py`: family levels at 37 and 13 by four methods; the diagonal derivative
    formula.
  - `sc6_negatives.py`: 61, 97 and 109, and the 13 table.
  - `sc7_size4033.py`: sampled characters at 4033.
  - `sc8_odds.py`: the theta form, the η_0 equation, and the d-values of the residual class.

### First-round verifiers

- **verify-identities/** (`vlib.py`, trinomial modulus)
  - `claim12.py`: the hexagon identity; the order-3 symmetry; the rotations agree only at 37.
  - `claim34.py`: λ = W^4/(t t) at 1369 characters; the relatives' dilation identities and
    axes.
  - `claim5.py`: the hexagon family, and the dilation form f_{p,q} · s ≡ dil_l(4850 · s).
- **verify-reduction/** (`vlib.py`, Φ37 modulus)
  - `v1_identities.py`: the rotation, π f' = h^4, and the W^4 form.
  - `v2_claim1.py`, `v3_claim2.py`, `v6_extra.py`: the symmetry-forces-cubes refutation and its
    counterexamples.
  - `v4_claim3.py`: class bookkeeping (2.5).
  - `v5_claim4.py`: the norm criterion over all of K*, and N(W(1,2)) = θ_2.
- **verify-specificity/** (`slib.py`, sparse modulus)
  - `t0_selftest.py`: R(4850)^29127 = 1 + J.
  - `t1_shape.py`: the specificity of the single-orbit shape.
  - `t2_nulls.py`: symmetry null rates; the partial-twist span.
  - `t3_soundness.py`: forcing arguments across the hexagon family and other sizes.
  - `t4_calibration.py`: the honest residual p-values; the relatives' dependences.
  - `t5_residual_extra.py`: the cross-size W null; a first check of the (*) closed form.
  - `t6_lemmas.py`: the residue lemmas never mispredict.

### Investigators

- **norms/** (`nlib.py`): the source of the proof.
  - `s1_exact_norms.py`: N(W) at every character, exactly.
  - `s2_universal_formula.py`: (*) at 13, 37, 61, 97 and 109; the docstring holds the derivation
    sketch.
  - `s3_f64_analysis.py`: the auxiliary relation and the forcing table.
  - `s4_bookkeeping.py`: formal F8-membership under the cube hypothesis.
  - `s5_closed_form.py`: the F2[x] certificate and the closed form.
  - `s6_hexfamily37.py`: the family at 37.
  - `s7_other_sizes.py`: the hypotheses at other sizes.
  - `s8_period_relations.py`: relations between periods of index 2, 3 and 6.
  - `s9_endtoend.py`: the theta form on 4850.
- **normform/**
  - `step1_cubesq.py`, `step2_identities.py`: the cube-plus-square form and π F' = h^4.
  - `step4_f64.py`, `step13_periods.py`, `step14_NWformula.py`: the norm to F64 and the period
    formulas.
  - `step5_calib.py`, `step6_forcing.py`: the symmetry and forcing (see 5.1).
  - `step11_orbitfamily.py`, `step12_core.py`: the core f0 = h/π and the relatives.
  - `step16_d1search.py`, `step17_trinomial.py`: the residual class and its 1-in-8 null.
  - `step20_othersizes.py`, `step21_formula109.py`: other sizes.
  - `step23_summary.py`: the class-by-class account.
- **family/** (`famlib.py`, `sizes_engine.py`)
  - `step1_map37.py`, `step2_theory37.py`, `step8_classify.py`: the classification at 37.
  - `step3_sizes.py`, `step6_classes.py`, `step6b_torbits.py`, `step7_bigprimes.py`: the size
    survey.
  - `step4_lambda.py`, `step9_sums.py`, `step12_evenreps.py`: other numerators.
  - `step5_map13.py`: 13.
  - `step13_predictions.py`: writes `predictions.json`.
  - `step14_twins.py`: the twin-digit identity.
- **relations/**
  - `sparse.py`, `lam.py`: closed forms.
  - `trio.py`, `sigma_exact.py`, `shells.py`, `bfactor.py`: the σ-identity for the relatives.
  - `sigma.py`: σ-partners across the census.
  - `search.py`, `run_targets.py`, `calib.py`, `gen_beta.py`, `ext6.py`: two-rule relation
    searches (none clean for 4850).
  - `patterns.py`, `ratio.py`: pattern statistics and the relatives' ratios.
  - `tables.py`, `checks.py`: log tables mod 513, checked against eigen.odd_part.
- **reciprocity/** (`rlib.py`)
  - `step2_reciprocity.py` to `step5_points.py`: the n-th power reciprocity reformulation.
  - `step7_norm_identity.py`: the norm form of the condition.
  - `step10_identity.py`: the relatives' identity in GF(2)[a, b].
  - `step11_numerator.py`, `step12_symmetry.py`, `step18_subspace.py`, `step19_proof_checks.py`:
    the R3 symmetry and tie groups.
  - `step15_norm_census.py`: the F64-norm census of 2^28 rules.
  - `step24_partial_cyclotomic.py`: the residual line in cyclotomic terms.
- **threeadic/** (`tlib.py`, `sbasis.py`)
  - `step1_digits.py`, `step2_transform.py`, `step3_census.py`: 3-adic digits and the Legendre
    basis.
  - `step4_vacuity.py`: mechanism 5 is vacuous when unrestricted.
  - `step5_support.py`, `step6_calib.py`: minimal unit supports.
  - `step9_partialfrob.py`, `step11_reduction.py`: the partial-Frobenius lemma and the one-trit
    claim (see 5.1, 5.2).
  - `step12_trit.py`: the residual line.
- **grouping/** (`gr.py`)
  - `u4850.py`, `baselines.py`: group-ring objects.
  - `census_A.py`, `census_A2.py`, `calib_A.py`: property (A).
  - `fable_congruence.py`: 5.4.
  - `relatives.py`, `partial_twist.py`, `verify_twist.py`, `vacuity_twist.py`, `mu19_relation.py`:
    the relatives' 19-parts.
  - `transport_search.py`: GL2 transports.
- **model19/** (`ff18.py`, `torus19.py`)
  - `hexfamily.py`, `hexsizes.py`: the hexagon family and its sizes.
  - `verify_identity.py`, `verify_identity2.py`: the group-ring identities, including
    5^2 + 3 · 2^2 = 37.
  - `kloosterman.py`, `resolvents.py`, `gauss.py`: W as a Kloosterman sum; Lagrange resolvents;
    Gauss sums.
  - `sizes.py`, `wtest.py`: 109, 185 and other primes.
- **calibration/**
  - `sweep.py`: one pass over all 2^28 rules.
  - `rates.py`, `decoy.py`: rates, dependence, and the decoy test.
  - `pairs.py`, `gcd_clusters.py`, `collisions_by_level.py`, `triple.py`: pattern collisions and
    the relatives' null.
  - `lookelsewhere.py`: the global p.
  - `run_condition.py`: mechanisms 1 to 8 on all 125 ninth-power rules (`condition.jsonl`).
  - `test_design.py`: two alternative test designs, a radius-7 census and the <swap, -I> family.

## Addendum (the orchestrator)

- **The orchestrator's check.** `tests/test_rule4850_proof.py` rechecks the final chain with the
  orchestrator's own field (`examples/qec-bb/bb.py`, F(2^36)), importing nothing from the
  investigators or the checkers. It covers:
  - the hexagon identity;
  - η_0 ∈ F64 ∖ F8, with η_0^24 + η_0^9 + 1 = 0 and order 21;
  - λ · t_α t_β = W^4 at all 1296 off-diagonal characters;
  - N(λ) = (η(α)η(β))^(4n(d)−2) at each of them, with N(λ) ∈ F8*;
  - λ = t_j t_{5j} on the diagonals;
  - every nonzero eigenvalue a ninth power.

  All pass, in 3 seconds.
- **The registered test** (`examples/hexagon-family`, registered and pushed in `f13c115` before any
  prediction was computed) is finished. **Verdict: the classification holds.**
  - **Tested:** 35 of 41 predictions, all agreeing and none wrong, spread over the tiers (17 T0,
    10 T3, 6 T1 and 2 T2).
  - **Sizes:** 21 at 37, 6 at 13, and 61, 97, 109, 111, 181, 193, 481 and 703 once each.
  - **Not tested:** the six T4 entries, at 709 to 1861. Two exceeded the 45-minute limit.
  - **The run was interrupted.** A container restart killed it after 37 records. Before it was
    resumed, the study recorded the last four T4 entries as not run (documented in its docstring
    and commit). Their registered predictions are expressions such as "2^930 - 1", which the
    registered comparison cannot match.
  - **The ledger** verifies with no problems.
