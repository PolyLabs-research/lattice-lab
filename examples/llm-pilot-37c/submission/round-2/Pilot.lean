/-
Formal results for the seventh pilot (CARD.md, proposal.md): ninth powers at m = 37 by exponent
bookkeeping on top of the half-Frobenius identities of Cubes37.lean.

    period_r1968276_dvd : period 37 r1968276Offsets ∣ 29127     1968276 = a^2 b^2 V
    period_r985232_dvd  : period 37 r985232Offsets  ∣ 29127     985232  = a^2 b^2 (a + b) W
    period_r1431278_dvd : period 37 r1431278Offsets ∣ 29127     1431278 = Psi_5(a) Psi_5(b) V
    period_r699738_dvd  : period 37 r699738Offsets  ∣ 29127     699738  = Psi_5(a) Psi_5(b) (a + b) W

29127 = (2^18 - 1)/9: every eigenvalue of these four rules on the 37 x 37 torus is a ninth power
in F(2^18). Unconditional: the only arithmetic input, rule 90's confinement to the cubes
(t^87381 = 1 for t = z + 1/z), is Cubes37.r90_val.

The proofs: with a = t(x) = x + 1/x, b = t(y), the rules factor exactly (`r…_poly`, identities over
any commutative ring with 2 = 0 and x xi = y yi = 1, certified by `linear_combination`). At
(X^2, Y^2) the cores satisfy Cubes37's identities V(x^2, y^2) t(x) t(y) = Sh(7,7) + Sh(5,5) and
W(x^2, y^2) t(x) t(y) t(xy) t(x/y) = Sh(7,5), whose right sides are fixed by the 2^9-th power
(`sv_frob`, `sh_frob`): they lie in F(2^9), of order dividing 511 = 2^9 - 1. So the eigenvalue of
a^2 b^2 V at (X^2, Y^2) is t(X)^3 t(Y)^3 sv with sv^511 = 1, and t^(3 * 29127) = t^87381 = 1.
For the Psi_5 rules, Psi_5(t)^2 t = t(z^5) = t^(2^23) (5 = 2^23 mod 37, `t_frob23`), so the
eigenvalue is t(X)^(2^23 - 2) t(Y)^(2^23 - 2) sv, and 3 divides 2^23 - 2: again a ninth power.
On the axes (t(X) = 0, i.e. X = 1) the Psi_5 rules restrict to Psi_5(t)^2 t (t + 1)^4 with
(t + 1)^4 = t^510 from the norm identity t^513 = t^3 (t + 1)^4 (`t_norm`, from t^(2^9) = t^6 + t^2):
the exponent 2^23 + 511 is divisible by 3.
-/
import LatticeProofs
import LatticeProofs.Cubes37

namespace LatticeProofs

namespace Pilot37c

open Cubes37

/-- Family rule 1968276 (radius 5): orbits (1,1) (2,1) (3,1) (4,1) (5,2) (5,3) (5,4) (5,5). -/
def r1968276Offsets : Finset (ℤ × ℤ) := {(-5, -5), (-5, -4), (-5, -3), (-5, -2), (-5, 2), (-5, 3), (-5, 4), (-5, 5), (-4, -5), (-4, -1), (-4, 1), (-4, 5), (-3, -5), (-3, -1), (-3, 1), (-3, 5), (-2, -5), (-2, -1), (-2, 1), (-2, 5), (-1, -4), (-1, -3), (-1, -2), (-1, -1), (-1, 1), (-1, 2), (-1, 3), (-1, 4), (1, -4), (1, -3), (1, -2), (1, -1), (1, 1), (1, 2), (1, 3), (1, 4), (2, -5), (2, -1), (2, 1), (2, 5), (3, -5), (3, -1), (3, 1), (3, 5), (4, -5), (4, -1), (4, 1), (4, 5), (5, -5), (5, -4), (5, -3), (5, -2), (5, 2), (5, 3), (5, 4), (5, 5)}

/-- Family rule 985232: orbits (2,1) (3,1) (4,1) (5,1) (5,2) (5,3) (5,4). -/
def r985232Offsets : Finset (ℤ × ℤ) := {(-5, -4), (-5, -3), (-5, -2), (-5, -1), (-5, 1), (-5, 2), (-5, 3), (-5, 4), (-4, -5), (-4, -1), (-4, 1), (-4, 5), (-3, -5), (-3, -1), (-3, 1), (-3, 5), (-2, -5), (-2, -1), (-2, 1), (-2, 5), (-1, -5), (-1, -4), (-1, -3), (-1, -2), (-1, 2), (-1, 3), (-1, 4), (-1, 5), (1, -5), (1, -4), (1, -3), (1, -2), (1, 2), (1, 3), (1, 4), (1, 5), (2, -5), (2, -1), (2, 1), (2, 5), (3, -5), (3, -1), (3, 1), (3, 5), (4, -5), (4, -1), (4, 1), (4, 5), (5, -4), (5, -3), (5, -2), (5, -1), (5, 1), (5, 2), (5, 3), (5, 4)}

/-- Family rule 1431278: orbits (1,0) (1,1) (2,0) (2,2) (3,0) (3,1) (3,3) (4,0) (4,2) (4,4) (5,0)
(5,1) (5,3) (5,5). -/
def r1431278Offsets : Finset (ℤ × ℤ) := {(-5, -5), (-5, -3), (-5, -1), (-5, 0), (-5, 1), (-5, 3), (-5, 5), (-4, -4), (-4, -2), (-4, 0), (-4, 2), (-4, 4), (-3, -5), (-3, -3), (-3, -1), (-3, 0), (-3, 1), (-3, 3), (-3, 5), (-2, -4), (-2, -2), (-2, 0), (-2, 2), (-2, 4), (-1, -5), (-1, -3), (-1, -1), (-1, 0), (-1, 1), (-1, 3), (-1, 5), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, -5), (1, -3), (1, -1), (1, 0), (1, 1), (1, 3), (1, 5), (2, -4), (2, -2), (2, 0), (2, 2), (2, 4), (3, -5), (3, -3), (3, -1), (3, 0), (3, 1), (3, 3), (3, 5), (4, -4), (4, -2), (4, 0), (4, 2), (4, 4), (5, -5), (5, -3), (5, -1), (5, 0), (5, 1), (5, 3), (5, 5)}

/-- Family rule 699738: orbits (1,0) (2,0) (2,1) (3,0) (3,2) (4,0) (4,1) (4,3) (5,0) (5,2) (5,4). -/
def r699738Offsets : Finset (ℤ × ℤ) := {(-5, -4), (-5, -2), (-5, 0), (-5, 2), (-5, 4), (-4, -5), (-4, -3), (-4, -1), (-4, 0), (-4, 1), (-4, 3), (-4, 5), (-3, -4), (-3, -2), (-3, 0), (-3, 2), (-3, 4), (-2, -5), (-2, -3), (-2, -1), (-2, 0), (-2, 1), (-2, 3), (-2, 5), (-1, -4), (-1, -2), (-1, 0), (-1, 2), (-1, 4), (0, -5), (0, -4), (0, -3), (0, -2), (0, -1), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, -4), (1, -2), (1, 0), (1, 2), (1, 4), (2, -5), (2, -3), (2, -1), (2, 0), (2, 1), (2, 3), (2, 5), (3, -4), (3, -2), (3, 0), (3, 2), (3, 4), (4, -5), (4, -3), (4, -1), (4, 0), (4, 1), (4, 3), (4, 5), (5, -4), (5, -2), (5, 0), (5, 2), (5, 4)}

section Polys

variable {R : Type*} [CommRing R]

/-- 1968276 = a^2 b^2 V. -/
theorem r1968276_poly (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1) (hy : y * yi = 1) :
    ((x + xi) * (y + yi))^2 * vPoly x xi y yi = xi^5*yi^5 + xi^5*yi^4 + xi^5*yi^3 + xi^5*yi^2 + xi^5*y^2 + xi^5*y^3 + xi^5*y^4 + xi^5*y^5 + xi^4*yi^5 + xi^4*yi + xi^4*y + xi^4*y^5 + xi^3*yi^5 + xi^3*yi + xi^3*y + xi^3*y^5 + xi^2*yi^5 + xi^2*yi + xi^2*y + xi^2*y^5 + xi*yi^4 + xi*yi^3 + xi*yi^2 + xi*yi + xi*y + xi*y^2 + xi*y^3 + xi*y^4 + x*yi^4 + x*yi^3 + x*yi^2 + x*yi + x*y + x*y^2 + x*y^3 + x*y^4 + x^2*yi^5 + x^2*yi + x^2*y + x^2*y^5 + x^3*yi^5 + x^3*yi + x^3*y + x^3*y^5 + x^4*yi^5 + x^4*yi + x^4*y + x^4*y^5 + x^5*yi^5 + x^5*yi^4 + x^5*yi^3 + x^5*yi^2 + x^5*y^2 + x^5*y^3 + x^5*y^4 + x^5*y^5 := by
  unfold vPoly
  linear_combination (x^5*y^3 + x^5*y^2 + 2*x^5*y + x^5*yi^3 + x^5*yi^2 + 2*x^5*yi + 2*x^5 + x^4*y^3 + x^4*yi^3 + x^3*y^5 + x^3*y^4 + 4*x^3*y^3 + 3*x^3*y^2 + 4*x^3*y + x^3*yi^5 + x^3*yi^4 + 4*x^3*yi^3 + 3*x^3*yi^2 + 4*x^3*yi + 4*x^3 + x^2*y^5 + 3*x^2*y^3 + x^2*y + x^2*yi^5 + 3*x^2*yi^3 + x^2*yi + 2*x*y^5 + 4*x*y^3 + x*y^2 + 3*x*y + 2*x*yi^5 + 4*x*yi^3 + x*yi^2 + 3*x*yi + 2*x + xi^5*y^3 + xi^5*y^2 + 2*xi^5*y + xi^5*yi^3 + xi^5*yi^2 + 2*xi^5*yi + 2*xi^5 + xi^4*y^3 + xi^4*yi^3 + xi^3*y^5 + xi^3*y^4 + 4*xi^3*y^3 + 3*xi^3*y^2 + 4*xi^3*y + xi^3*yi^5 + xi^3*yi^4 + 4*xi^3*yi^3 + 3*xi^3*yi^2 + 4*xi^3*yi + 4*xi^3 + xi^2*y^5 + 3*xi^2*y^3 + xi^2*y + xi^2*yi^5 + 3*xi^2*yi^3 + xi^2*yi + 2*xi*y^5 + 4*xi*y^3 + xi*y^2 + 3*xi*y + 2*xi*yi^5 + 4*xi*yi^3 + xi*yi^2 + 3*xi*yi + 2*xi + 2*y^5 + 4*y^3 + 2*y + 2*yi^5 + 4*yi^3 + 2*yi) * h2 + (2*x^3*y^5 + 4*x^3*y^4*yi + 2*x^3*y^4 + 2*x^3*y^3*yi^2 + 4*x^3*y^3*yi + 2*x^3*y^3 + 2*x^3*y^2*yi^3 + 4*x^3*y^2*yi^2 + 6*x^3*y^2*yi + 2*x^3*y^2 + 4*x^3*y*yi^4 + 4*x^3*y*yi^3 + 6*x^3*y*yi^2 + 4*x^3*y*yi + 2*x^3*yi^5 + 2*x^3*yi^4 + 2*x^3*yi^3 + 2*x^3*yi^2 + x^2*xi*y^5 + 2*x^2*xi*y^4*yi + x^2*xi*y^4 + x^2*xi*y^3*yi^2 + 2*x^2*xi*y^3*yi + x^2*xi*y^3 + x^2*xi*y^2*yi^3 + 2*x^2*xi*y^2*yi^2 + 3*x^2*xi*y^2*yi + x^2*xi*y^2 + 2*x^2*xi*y*yi^4 + 2*x^2*xi*y*yi^3 + 3*x^2*xi*y*yi^2 + 2*x^2*xi*y*yi + x^2*xi*yi^5 + x^2*xi*yi^4 + x^2*xi*yi^3 + x^2*xi*yi^2 + 2*x^2*y^5 + 4*x^2*y^4*yi + 2*x^2*y^3*yi^2 + 2*x^2*y^2*yi^3 + 4*x^2*y*yi^4 + 2*x^2*yi^5 + x*xi^2*y^5 + 2*x*xi^2*y^4*yi + x*xi^2*y^4 + x*xi^2*y^3*yi^2 + 2*x*xi^2*y^3*yi + x*xi^2*y^3 + x*xi^2*y^2*yi^3 + 2*x*xi^2*y^2*yi^2 + 3*x*xi^2*y^2*yi + x*xi^2*y^2 + 2*x*xi^2*y*yi^4 + 2*x*xi^2*y*yi^3 + 3*x*xi^2*y*yi^2 + 2*x*xi^2*y*yi + x*xi^2*yi^5 + x*xi^2*yi^4 + x*xi^2*yi^3 + x*xi^2*yi^2 + 2*x*xi*y^5 + 4*x*xi*y^4*yi + 2*x*xi*y^3*yi^2 + 2*x*xi*y^2*yi^3 + 4*x*xi*y*yi^4 + 2*x*xi*yi^5 + 4*x*y^5 + 8*x*y^4*yi + x*y^4 + 4*x*y^3*yi^2 + 2*x*y^3*yi + x*y^3 + 4*x*y^2*yi^3 + 2*x*y^2*yi^2 + 3*x*y^2*yi + x*y^2 + 8*x*y*yi^4 + 2*x*y*yi^3 + 3*x*y*yi^2 + 2*x*y*yi + 4*x*yi^5 + x*yi^4 + x*yi^3 + x*yi^2 + 2*xi^3*y^5 + 4*xi^3*y^4*yi + 2*xi^3*y^4 + 2*xi^3*y^3*yi^2 + 4*xi^3*y^3*yi + 2*xi^3*y^3 + 2*xi^3*y^2*yi^3 + 4*xi^3*y^2*yi^2 + 6*xi^3*y^2*yi + 2*xi^3*y^2 + 4*xi^3*y*yi^4 + 4*xi^3*y*yi^3 + 6*xi^3*y*yi^2 + 4*xi^3*y*yi + 2*xi^3*yi^5 + 2*xi^3*yi^4 + 2*xi^3*yi^3 + 2*xi^3*yi^2 + 2*xi^2*y^5 + 4*xi^2*y^4*yi + 2*xi^2*y^3*yi^2 + 2*xi^2*y^2*yi^3 + 4*xi^2*y*yi^4 + 2*xi^2*yi^5 + 4*xi*y^5 + 8*xi*y^4*yi + xi*y^4 + 4*xi*y^3*yi^2 + 2*xi*y^3*yi + xi*y^3 + 4*xi*y^2*yi^3 + 2*xi*y^2*yi^2 + 3*xi*y^2*yi + xi*y^2 + 8*xi*y*yi^4 + 2*xi*y*yi^3 + 3*xi*y*yi^2 + 2*xi*y*yi + 4*xi*yi^5 + xi*yi^4 + xi*yi^3 + xi*yi^2 + 4*y^5 + 8*y^4*yi + 4*y^3*yi^2 + 4*y^2*yi^3 + 8*y*yi^4 + 4*yi^5) * hx + (2*x^5*y^3 + x^5*y^2*yi + 2*x^5*y^2 + x^5*y*yi^2 + 2*x^5*y*yi + 4*x^5*y + 2*x^5*yi^3 + 2*x^5*yi^2 + 4*x^5*yi + 4*x^5 + 2*x^4*y^3 + x^4*y^2*yi + x^4*y*yi^2 + x^4*y + 2*x^4*yi^3 + x^4*yi + 6*x^3*y^3 + 3*x^3*y^2*yi + 4*x^3*y^2 + 3*x^3*y*yi^2 + 4*x^3*y*yi + 9*x^3*y + 6*x^3*yi^3 + 4*x^3*yi^2 + 9*x^3*yi + 8*x^3 + 6*x^2*y^3 + 3*x^2*y^2*yi + 3*x^2*y*yi^2 + 3*x^2*y + 6*x^2*yi^3 + 3*x^2*yi + 8*x*y^3 + 4*x*y^2*yi + 2*x*y^2 + 4*x*y*yi^2 + 2*x*y*yi + 7*x*y + 8*x*yi^3 + 2*x*yi^2 + 7*x*yi + 4*x + 2*xi^5*y^3 + xi^5*y^2*yi + 2*xi^5*y^2 + xi^5*y*yi^2 + 2*xi^5*y*yi + 4*xi^5*y + 2*xi^5*yi^3 + 2*xi^5*yi^2 + 4*xi^5*yi + 4*xi^5 + 2*xi^4*y^3 + xi^4*y^2*yi + xi^4*y*yi^2 + xi^4*y + 2*xi^4*yi^3 + xi^4*yi + 6*xi^3*y^3 + 3*xi^3*y^2*yi + 4*xi^3*y^2 + 3*xi^3*y*yi^2 + 4*xi^3*y*yi + 9*xi^3*y + 6*xi^3*yi^3 + 4*xi^3*yi^2 + 9*xi^3*yi + 8*xi^3 + 6*xi^2*y^3 + 3*xi^2*y^2*yi + 3*xi^2*y*yi^2 + 3*xi^2*y + 6*xi^2*yi^3 + 3*xi^2*yi + 8*xi*y^3 + 4*xi*y^2*yi + 2*xi*y^2 + 4*xi*y*yi^2 + 2*xi*y*yi + 7*xi*y + 8*xi*yi^3 + 2*xi*yi^2 + 7*xi*yi + 4*xi + 8*y^3 + 4*y^2*yi + 4*y*yi^2 + 4*y + 8*yi^3 + 4*yi) * hy

/-- 985232 = a^2 b^2 (a + b) W. -/
theorem r985232_poly (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1) (hy : y * yi = 1) :
    ((x + xi) * (y + yi))^2 * (x + xi + y + yi) * wPoly x xi y yi = xi^5*yi^4 + xi^5*yi^3 + xi^5*yi^2 + xi^5*yi + xi^5*y + xi^5*y^2 + xi^5*y^3 + xi^5*y^4 + xi^4*yi^5 + xi^4*yi + xi^4*y + xi^4*y^5 + xi^3*yi^5 + xi^3*yi + xi^3*y + xi^3*y^5 + xi^2*yi^5 + xi^2*yi + xi^2*y + xi^2*y^5 + xi*yi^5 + xi*yi^4 + xi*yi^3 + xi*yi^2 + xi*y^2 + xi*y^3 + xi*y^4 + xi*y^5 + x*yi^5 + x*yi^4 + x*yi^3 + x*yi^2 + x*y^2 + x*y^3 + x*y^4 + x*y^5 + x^2*yi^5 + x^2*yi + x^2*y + x^2*y^5 + x^3*yi^5 + x^3*yi + x^3*y + x^3*y^5 + x^4*yi^5 + x^4*yi + x^4*y + x^4*y^5 + x^5*yi^4 + x^5*yi^3 + x^5*yi^2 + x^5*yi + x^5*y + x^5*y^2 + x^5*y^3 + x^5*y^4 := by
  unfold wPoly
  linear_combination (x^5*y^2 + x^5*y + x^5*yi^2 + x^5*yi + 2*x^5 + x^4*y^4 + 2*x^4*y^3 + 3*x^4*y^2 + 3*x^4*y + x^4*yi^4 + 2*x^4*yi^3 + 3*x^4*yi^2 + 3*x^4*yi + 4*x^4 + 2*x^3*y^4 + 3*x^3*y^3 + 6*x^3*y^2 + 6*x^3*y + 2*x^3*yi^4 + 3*x^3*yi^3 + 6*x^3*yi^2 + 6*x^3*yi + 8*x^3 + x^2*y^5 + 3*x^2*y^4 + 6*x^2*y^3 + 8*x^2*y^2 + 10*x^2*y + x^2*yi^5 + 3*x^2*yi^4 + 6*x^2*yi^3 + 8*x^2*yi^2 + 10*x^2*yi + 10*x^2 + x*y^5 + 3*x*y^4 + 6*x*y^3 + 10*x*y^2 + 12*x*y + x*yi^5 + 3*x*yi^4 + 6*x*yi^3 + 10*x*yi^2 + 12*x*yi + 14*x + xi^5*y^2 + xi^5*y + xi^5*yi^2 + xi^5*yi + 2*xi^5 + xi^4*y^4 + 2*xi^4*y^3 + 3*xi^4*y^2 + 3*xi^4*y + xi^4*yi^4 + 2*xi^4*yi^3 + 3*xi^4*yi^2 + 3*xi^4*yi + 4*xi^4 + 2*xi^3*y^4 + 3*xi^3*y^3 + 6*xi^3*y^2 + 6*xi^3*y + 2*xi^3*yi^4 + 3*xi^3*yi^3 + 6*xi^3*yi^2 + 6*xi^3*yi + 8*xi^3 + xi^2*y^5 + 3*xi^2*y^4 + 6*xi^2*y^3 + 8*xi^2*y^2 + 10*xi^2*y + xi^2*yi^5 + 3*xi^2*yi^4 + 6*xi^2*yi^3 + 8*xi^2*yi^2 + 10*xi^2*yi + 10*xi^2 + xi*y^5 + 3*xi*y^4 + 6*xi*y^3 + 10*xi*y^2 + 12*xi*y + xi*yi^5 + 3*xi*yi^4 + 6*xi*yi^3 + 10*xi*yi^2 + 12*xi*yi + 14*xi + 2*y^5 + 4*y^4 + 8*y^3 + 10*y^2 + 14*y + 2*yi^5 + 4*yi^4 + 8*yi^3 + 10*yi^2 + 14*yi + 12) * h2 + (3*x^3*y^4 + 6*x^3*y^3*yi + 3*x^3*y^3 + 6*x^3*y^2*yi^2 + 9*x^3*y^2*yi + 3*x^3*y^2 + 6*x^3*y*yi^3 + 9*x^3*y*yi^2 + 6*x^3*y*yi + 3*x^3*yi^4 + 3*x^3*yi^3 + 3*x^3*yi^2 + 4*x^2*xi*y^4 + 8*x^2*xi*y^3*yi + 4*x^2*xi*y^3 + 8*x^2*xi*y^2*yi^2 + 12*x^2*xi*y^2*yi + 4*x^2*xi*y^2 + 8*x^2*xi*y*yi^3 + 12*x^2*xi*y*yi^2 + 8*x^2*xi*y*yi + 4*x^2*xi*yi^4 + 4*x^2*xi*yi^3 + 4*x^2*xi*yi^2 + 2*x^2*y^5 + 6*x^2*y^4*yi + 6*x^2*y^4 + 8*x^2*y^3*yi^2 + 16*x^2*y^3*yi + 2*x^2*y^3 + 8*x^2*y^2*yi^3 + 20*x^2*y^2*yi^2 + 6*x^2*y^2*yi + 6*x^2*y*yi^4 + 16*x^2*y*yi^3 + 6*x^2*y*yi^2 + 2*x^2*yi^5 + 6*x^2*yi^4 + 2*x^2*yi^3 + 4*x*xi^2*y^4 + 8*x*xi^2*y^3*yi + 4*x*xi^2*y^3 + 8*x*xi^2*y^2*yi^2 + 12*x*xi^2*y^2*yi + 4*x*xi^2*y^2 + 8*x*xi^2*y*yi^3 + 12*x*xi^2*y*yi^2 + 8*x*xi^2*y*yi + 4*x*xi^2*yi^4 + 4*x*xi^2*yi^3 + 4*x*xi^2*yi^2 + 2*x*xi*y^5 + 6*x*xi*y^4*yi + 8*x*xi*y^4 + 8*x*xi*y^3*yi^2 + 20*x*xi*y^3*yi + 2*x*xi*y^3 + 8*x*xi*y^2*yi^3 + 24*x*xi*y^2*yi^2 + 6*x*xi*y^2*yi + 6*x*xi*y*yi^4 + 20*x*xi*y*yi^3 + 6*x*xi*y*yi^2 + 2*x*xi*yi^5 + 8*x*xi*yi^4 + 2*x*xi*yi^3 + 3*x*y^5 + 9*x*y^4*yi + 7*x*y^4 + 12*x*y^3*yi^2 + 14*x*y^3*yi + 4*x*y^3 + 12*x*y^2*yi^3 + 14*x*y^2*yi^2 + 12*x*y^2*yi + 7*x*y^2 + 9*x*y*yi^4 + 14*x*y*yi^3 + 12*x*y*yi^2 + 14*x*y*yi + 3*x*yi^5 + 7*x*yi^4 + 4*x*yi^3 + 7*x*yi^2 + 3*xi^3*y^4 + 6*xi^3*y^3*yi + 3*xi^3*y^3 + 6*xi^3*y^2*yi^2 + 9*xi^3*y^2*yi + 3*xi^3*y^2 + 6*xi^3*y*yi^3 + 9*xi^3*y*yi^2 + 6*xi^3*y*yi + 3*xi^3*yi^4 + 3*xi^3*yi^3 + 3*xi^3*yi^2 + 2*xi^2*y^5 + 6*xi^2*y^4*yi + 6*xi^2*y^4 + 8*xi^2*y^3*yi^2 + 16*xi^2*y^3*yi + 2*xi^2*y^3 + 8*xi^2*y^2*yi^3 + 20*xi^2*y^2*yi^2 + 6*xi^2*y^2*yi + 6*xi^2*y*yi^4 + 16*xi^2*y*yi^3 + 6*xi^2*y*yi^2 + 2*xi^2*yi^5 + 6*xi^2*yi^4 + 2*xi^2*yi^3 + 3*xi*y^5 + 9*xi*y^4*yi + 7*xi*y^4 + 12*xi*y^3*yi^2 + 14*xi*y^3*yi + 4*xi*y^3 + 12*xi*y^2*yi^3 + 14*xi*y^2*yi^2 + 12*xi*y^2*yi + 7*xi*y^2 + 9*xi*y*yi^4 + 14*xi*y*yi^3 + 12*xi*y*yi^2 + 14*xi*y*yi + 3*xi*yi^5 + 7*xi*yi^4 + 4*xi*yi^3 + 7*xi*yi^2 + 4*y^5 + 12*y^4*yi + 8*y^4 + 16*y^3*yi^2 + 20*y^3*yi + 4*y^3 + 16*y^2*yi^3 + 24*y^2*yi^2 + 12*y^2*yi + 12*y*yi^4 + 20*y*yi^3 + 12*y*yi^2 + 4*yi^5 + 8*yi^4 + 4*yi^3) * hx + (2*x^5*y^2 + 2*x^5*y*yi + 3*x^5*y + 2*x^5*yi^2 + 3*x^5*yi + 4*x^5 + 3*x^4*y^3 + 4*x^4*y^2*yi + 6*x^4*y^2 + 4*x^4*y*yi^2 + 8*x^4*y*yi + 7*x^4*y + 3*x^4*yi^3 + 6*x^4*yi^2 + 7*x^4*yi + 8*x^4 + 3*x^3*y^3 + 4*x^3*y^2*yi + 8*x^3*y^2 + 4*x^3*y*yi^2 + 8*x^3*y*yi + 13*x^3*y + 3*x^3*yi^3 + 8*x^3*yi^2 + 13*x^3*yi + 16*x^3 + 9*x^2*y^3 + 12*x^2*y^2*yi + 16*x^2*y^2 + 12*x^2*y*yi^2 + 20*x^2*y*yi + 21*x^2*y + 9*x^2*yi^3 + 16*x^2*yi^2 + 21*x^2*yi + 20*x^2 + 9*x*y^3 + 12*x*y^2*yi + 14*x*y^2 + 12*x*y*yi^2 + 14*x*y*yi + 24*x*y + 9*x*yi^3 + 14*x*yi^2 + 24*x*yi + 28*x + 2*xi^5*y^2 + 2*xi^5*y*yi + 3*xi^5*y + 2*xi^5*yi^2 + 3*xi^5*yi + 4*xi^5 + 3*xi^4*y^3 + 4*xi^4*y^2*yi + 6*xi^4*y^2 + 4*xi^4*y*yi^2 + 8*xi^4*y*yi + 7*xi^4*y + 3*xi^4*yi^3 + 6*xi^4*yi^2 + 7*xi^4*yi + 8*xi^4 + 3*xi^3*y^3 + 4*xi^3*y^2*yi + 8*xi^3*y^2 + 4*xi^3*y*yi^2 + 8*xi^3*y*yi + 13*xi^3*y + 3*xi^3*yi^3 + 8*xi^3*yi^2 + 13*xi^3*yi + 16*xi^3 + 9*xi^2*y^3 + 12*xi^2*y^2*yi + 16*xi^2*y^2 + 12*xi^2*y*yi^2 + 20*xi^2*y*yi + 21*xi^2*y + 9*xi^2*yi^3 + 16*xi^2*yi^2 + 21*xi^2*yi + 20*xi^2 + 9*xi*y^3 + 12*xi*y^2*yi + 14*xi*y^2 + 12*xi*y*yi^2 + 14*xi*y*yi + 24*xi*y + 9*xi*yi^3 + 14*xi*yi^2 + 24*xi*yi + 28*xi + 12*y^3 + 16*y^2*yi + 20*y^2 + 16*y*yi^2 + 24*y*yi + 28*y + 12*yi^3 + 20*yi^2 + 28*yi + 24) * hy

/-- 1431278 = Psi_5(a) Psi_5(b) V, Psi_5(t) = t^2 + t + 1. -/
theorem r1431278_poly (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1) (hy : y * yi = 1) :
    ((x + xi)^2 + (x + xi) + 1) * ((y + yi)^2 + (y + yi) + 1) * vPoly x xi y yi = xi^5*yi^5 + xi^5*yi^3 + xi^5*yi + xi^5 + xi^5*y + xi^5*y^3 + xi^5*y^5 + xi^4*yi^4 + xi^4*yi^2 + xi^4 + xi^4*y^2 + xi^4*y^4 + xi^3*yi^5 + xi^3*yi^3 + xi^3*yi + xi^3 + xi^3*y + xi^3*y^3 + xi^3*y^5 + xi^2*yi^4 + xi^2*yi^2 + xi^2 + xi^2*y^2 + xi^2*y^4 + xi*yi^5 + xi*yi^3 + xi*yi + xi + xi*y + xi*y^3 + xi*y^5 + yi^5 + yi^4 + yi^3 + yi^2 + yi + y + y^2 + y^3 + y^4 + y^5 + x*yi^5 + x*yi^3 + x*yi + x + x*y + x*y^3 + x*y^5 + x^2*yi^4 + x^2*yi^2 + x^2 + x^2*y^2 + x^2*y^4 + x^3*yi^5 + x^3*yi^3 + x^3*yi + x^3 + x^3*y + x^3*y^3 + x^3*y^5 + x^4*yi^4 + x^4*yi^2 + x^4 + x^4*y^2 + x^4*y^4 + x^5*yi^5 + x^5*yi^3 + x^5*yi + x^5 + x^5*y + x^5*y^3 + x^5*y^5 := by
  unfold vPoly
  linear_combination (x^5*y^4 + 2*x^5*y^3 + 3*x^5*y^2 + 3*x^5*y + x^5*yi^4 + 2*x^5*yi^3 + 3*x^5*yi^2 + 3*x^5*yi + 3*x^5 + x^4*y^5 + x^4*y^4 + 4*x^4*y^3 + 3*x^4*y^2 + 4*x^4*y + x^4*yi^5 + x^4*yi^4 + 4*x^4*yi^3 + 3*x^4*yi^2 + 4*x^4*yi + 3*x^4 + 2*x^3*y^5 + 4*x^3*y^4 + 10*x^3*y^3 + 10*x^3*y^2 + 11*x^3*y + 2*x^3*yi^5 + 4*x^3*yi^4 + 10*x^3*yi^3 + 10*x^3*yi^2 + 11*x^3*yi + 10*x^3 + 3*x^2*y^5 + 3*x^2*y^4 + 10*x^2*y^3 + 5*x^2*y^2 + 6*x^2*y + 3*x^2*yi^5 + 3*x^2*yi^4 + 10*x^2*yi^3 + 5*x^2*yi^2 + 6*x^2*yi + 3*x^2 + 3*x*y^5 + 4*x*y^4 + 11*x*y^3 + 6*x*y^2 + 6*x*y + 3*x*yi^5 + 4*x*yi^4 + 11*x*yi^3 + 6*x*yi^2 + 6*x*yi + 3*x + xi^5*y^4 + 2*xi^5*y^3 + 3*xi^5*y^2 + 3*xi^5*y + xi^5*yi^4 + 2*xi^5*yi^3 + 3*xi^5*yi^2 + 3*xi^5*yi + 3*xi^5 + xi^4*y^5 + xi^4*y^4 + 4*xi^4*y^3 + 3*xi^4*y^2 + 4*xi^4*y + xi^4*yi^5 + xi^4*yi^4 + 4*xi^4*yi^3 + 3*xi^4*yi^2 + 4*xi^4*yi + 3*xi^4 + 2*xi^3*y^5 + 4*xi^3*y^4 + 10*xi^3*y^3 + 10*xi^3*y^2 + 11*xi^3*y + 2*xi^3*yi^5 + 4*xi^3*yi^4 + 10*xi^3*yi^3 + 10*xi^3*yi^2 + 11*xi^3*yi + 10*xi^3 + 3*xi^2*y^5 + 3*xi^2*y^4 + 10*xi^2*y^3 + 5*xi^2*y^2 + 6*xi^2*y + 3*xi^2*yi^5 + 3*xi^2*yi^4 + 10*xi^2*yi^3 + 5*xi^2*yi^2 + 6*xi^2*yi + 3*xi^2 + 3*xi*y^5 + 4*xi*y^4 + 11*xi*y^3 + 6*xi*y^2 + 6*xi*y + 3*xi*yi^5 + 4*xi*yi^4 + 11*xi*yi^3 + 6*xi*yi^2 + 6*xi*yi + 3*xi + 3*y^5 + 3*y^4 + 10*y^3 + 3*y^2 + 3*y + 3*yi^5 + 3*yi^4 + 10*yi^3 + 3*yi^2 + 3*yi) * h2 + (2*x^3*y^5 + 4*x^3*y^4*yi + 4*x^3*y^4 + 2*x^3*y^3*yi^2 + 6*x^3*y^3*yi + 6*x^3*y^3 + 2*x^3*y^2*yi^3 + 4*x^3*y^2*yi^2 + 8*x^3*y^2*yi + 6*x^3*y^2 + 4*x^3*y*yi^4 + 6*x^3*y*yi^3 + 8*x^3*y*yi^2 + 8*x^3*y*yi + 4*x^3*y + 2*x^3*yi^5 + 4*x^3*yi^4 + 6*x^3*yi^3 + 6*x^3*yi^2 + 4*x^3*yi + 2*x^3 + x^2*xi*y^5 + 2*x^2*xi*y^4*yi + 2*x^2*xi*y^4 + x^2*xi*y^3*yi^2 + 3*x^2*xi*y^3*yi + 3*x^2*xi*y^3 + x^2*xi*y^2*yi^3 + 2*x^2*xi*y^2*yi^2 + 4*x^2*xi*y^2*yi + 3*x^2*xi*y^2 + 2*x^2*xi*y*yi^4 + 3*x^2*xi*y*yi^3 + 4*x^2*xi*y*yi^2 + 4*x^2*xi*y*yi + 2*x^2*xi*y + x^2*xi*yi^5 + 2*x^2*xi*yi^4 + 3*x^2*xi*yi^3 + 3*x^2*xi*yi^2 + 2*x^2*xi*yi + x^2*xi + 3*x^2*y^5 + 6*x^2*y^4*yi + 4*x^2*y^4 + 3*x^2*y^3*yi^2 + 5*x^2*y^3*yi + 5*x^2*y^3 + 3*x^2*y^2*yi^3 + 2*x^2*y^2*yi^2 + 4*x^2*y^2*yi + 3*x^2*y^2 + 6*x^2*y*yi^4 + 5*x^2*y*yi^3 + 4*x^2*y*yi^2 + 4*x^2*y*yi + 2*x^2*y + 3*x^2*yi^5 + 4*x^2*yi^4 + 5*x^2*yi^3 + 3*x^2*yi^2 + 2*x^2*yi + x^2 + x*xi^2*y^5 + 2*x*xi^2*y^4*yi + 2*x*xi^2*y^4 + x*xi^2*y^3*yi^2 + 3*x*xi^2*y^3*yi + 3*x*xi^2*y^3 + x*xi^2*y^2*yi^3 + 2*x*xi^2*y^2*yi^2 + 4*x*xi^2*y^2*yi + 3*x*xi^2*y^2 + 2*x*xi^2*y*yi^4 + 3*x*xi^2*y*yi^3 + 4*x*xi^2*y*yi^2 + 4*x*xi^2*y*yi + 2*x*xi^2*y + x*xi^2*yi^5 + 2*x*xi^2*yi^4 + 3*x*xi^2*yi^3 + 3*x*xi^2*yi^2 + 2*x*xi^2*yi + x*xi^2 + 2*x*xi*y^5 + 4*x*xi*y^4*yi + 2*x*xi*y^4 + 2*x*xi*y^3*yi^2 + 2*x*xi*y^3*yi + 2*x*xi*y^3 + 2*x*xi*y^2*yi^3 + 4*x*xi*y*yi^4 + 2*x*xi*y*yi^3 + 2*x*xi*yi^5 + 2*x*xi*yi^4 + 2*x*xi*yi^3 + 5*x*y^5 + 10*x*y^4*yi + 6*x*y^4 + 5*x*y^3*yi^2 + 7*x*y^3*yi + 7*x*y^3 + 5*x*y^2*yi^3 + 2*x*y^2*yi^2 + 4*x*y^2*yi + 3*x*y^2 + 10*x*y*yi^4 + 7*x*y*yi^3 + 4*x*y*yi^2 + 4*x*y*yi + 2*x*y + 5*x*yi^5 + 6*x*yi^4 + 7*x*yi^3 + 3*x*yi^2 + 2*x*yi + x + 2*xi^3*y^5 + 4*xi^3*y^4*yi + 4*xi^3*y^4 + 2*xi^3*y^3*yi^2 + 6*xi^3*y^3*yi + 6*xi^3*y^3 + 2*xi^3*y^2*yi^3 + 4*xi^3*y^2*yi^2 + 8*xi^3*y^2*yi + 6*xi^3*y^2 + 4*xi^3*y*yi^4 + 6*xi^3*y*yi^3 + 8*xi^3*y*yi^2 + 8*xi^3*y*yi + 4*xi^3*y + 2*xi^3*yi^5 + 4*xi^3*yi^4 + 6*xi^3*yi^3 + 6*xi^3*yi^2 + 4*xi^3*yi + 2*xi^3 + 3*xi^2*y^5 + 6*xi^2*y^4*yi + 4*xi^2*y^4 + 3*xi^2*y^3*yi^2 + 5*xi^2*y^3*yi + 5*xi^2*y^3 + 3*xi^2*y^2*yi^3 + 2*xi^2*y^2*yi^2 + 4*xi^2*y^2*yi + 3*xi^2*y^2 + 6*xi^2*y*yi^4 + 5*xi^2*y*yi^3 + 4*xi^2*y*yi^2 + 4*xi^2*y*yi + 2*xi^2*y + 3*xi^2*yi^5 + 4*xi^2*yi^4 + 5*xi^2*yi^3 + 3*xi^2*yi^2 + 2*xi^2*yi + xi^2 + 5*xi*y^5 + 10*xi*y^4*yi + 6*xi*y^4 + 5*xi*y^3*yi^2 + 7*xi*y^3*yi + 7*xi*y^3 + 5*xi*y^2*yi^3 + 2*xi*y^2*yi^2 + 4*xi*y^2*yi + 3*xi*y^2 + 10*xi*y*yi^4 + 7*xi*y*yi^3 + 4*xi*y*yi^2 + 4*xi*y*yi + 2*xi*y + 5*xi*yi^5 + 6*xi*yi^4 + 7*xi*yi^3 + 3*xi*yi^2 + 2*xi*yi + xi + 6*y^5 + 12*y^4*yi + 6*y^4 + 6*y^3*yi^2 + 6*y^3*yi + 6*y^3 + 6*y^2*yi^3 + 12*y*yi^4 + 6*y*yi^3 + 6*yi^5 + 6*yi^4 + 6*yi^3) * hx + (2*x^5*y^3 + x^5*y^2*yi + 3*x^5*y^2 + x^5*y*yi^2 + 2*x^5*y*yi + 5*x^5*y + 2*x^5*yi^3 + 3*x^5*yi^2 + 5*x^5*yi + 6*x^5 + 4*x^4*y^3 + 2*x^4*y^2*yi + 4*x^4*y^2 + 2*x^4*y*yi^2 + 2*x^4*y*yi + 6*x^4*y + 4*x^4*yi^3 + 4*x^4*yi^2 + 6*x^4*yi + 6*x^4 + 10*x^3*y^3 + 5*x^3*y^2*yi + 11*x^3*y^2 + 5*x^3*y*yi^2 + 6*x^3*y*yi + 17*x^3*y + 10*x^3*yi^3 + 11*x^3*yi^2 + 17*x^3*yi + 18*x^3 + 12*x^2*y^3 + 6*x^2*y^2*yi + 8*x^2*y^2 + 6*x^2*y*yi^2 + 2*x^2*y*yi + 10*x^2*y + 12*x^2*yi^3 + 8*x^2*yi^2 + 10*x^2*yi + 6*x^2 + 14*x*y^3 + 7*x*y^2*yi + 9*x*y^2 + 7*x*y*yi^2 + 2*x*y*yi + 11*x*y + 14*x*yi^3 + 9*x*yi^2 + 11*x*yi + 6*x + 2*xi^5*y^3 + xi^5*y^2*yi + 3*xi^5*y^2 + xi^5*y*yi^2 + 2*xi^5*y*yi + 5*xi^5*y + 2*xi^5*yi^3 + 3*xi^5*yi^2 + 5*xi^5*yi + 6*xi^5 + 4*xi^4*y^3 + 2*xi^4*y^2*yi + 4*xi^4*y^2 + 2*xi^4*y*yi^2 + 2*xi^4*y*yi + 6*xi^4*y + 4*xi^4*yi^3 + 4*xi^4*yi^2 + 6*xi^4*yi + 6*xi^4 + 10*xi^3*y^3 + 5*xi^3*y^2*yi + 11*xi^3*y^2 + 5*xi^3*y*yi^2 + 6*xi^3*y*yi + 17*xi^3*y + 10*xi^3*yi^3 + 11*xi^3*yi^2 + 17*xi^3*yi + 18*xi^3 + 12*xi^2*y^3 + 6*xi^2*y^2*yi + 8*xi^2*y^2 + 6*xi^2*y*yi^2 + 2*xi^2*y*yi + 10*xi^2*y + 12*xi^2*yi^3 + 8*xi^2*yi^2 + 10*xi^2*yi + 6*xi^2 + 14*xi*y^3 + 7*xi*y^2*yi + 9*xi*y^2 + 7*xi*y*yi^2 + 2*xi*y*yi + 11*xi*y + 14*xi*yi^3 + 9*xi*yi^2 + 11*xi*yi + 6*xi + 14*y^3 + 7*y^2*yi + 7*y^2 + 7*y*yi^2 + 7*y + 14*yi^3 + 7*yi^2 + 7*yi) * hy

/-- 699738 = Psi_5(a) Psi_5(b) (a + b) W. -/
theorem r699738_poly (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1) (hy : y * yi = 1) :
    ((x + xi)^2 + (x + xi) + 1) * ((y + yi)^2 + (y + yi) + 1) * (x + xi + y + yi) * wPoly x xi y yi = xi^5*yi^4 + xi^5*yi^2 + xi^5 + xi^5*y^2 + xi^5*y^4 + xi^4*yi^5 + xi^4*yi^3 + xi^4*yi + xi^4 + xi^4*y + xi^4*y^3 + xi^4*y^5 + xi^3*yi^4 + xi^3*yi^2 + xi^3 + xi^3*y^2 + xi^3*y^4 + xi^2*yi^5 + xi^2*yi^3 + xi^2*yi + xi^2 + xi^2*y + xi^2*y^3 + xi^2*y^5 + xi*yi^4 + xi*yi^2 + xi + xi*y^2 + xi*y^4 + yi^5 + yi^4 + yi^3 + yi^2 + yi + y + y^2 + y^3 + y^4 + y^5 + x*yi^4 + x*yi^2 + x + x*y^2 + x*y^4 + x^2*yi^5 + x^2*yi^3 + x^2*yi + x^2 + x^2*y + x^2*y^3 + x^2*y^5 + x^3*yi^4 + x^3*yi^2 + x^3 + x^3*y^2 + x^3*y^4 + x^4*yi^5 + x^4*yi^3 + x^4*yi + x^4 + x^4*y + x^4*y^3 + x^4*y^5 + x^5*yi^4 + x^5*yi^2 + x^5 + x^5*y^2 + x^5*y^4 := by
  unfold wPoly
  linear_combination (x^5*y^3 + 2*x^5*y^2 + 3*x^5*y + x^5*yi^3 + 2*x^5*yi^2 + 3*x^5*yi + 3*x^5 + 2*x^4*y^4 + 4*x^4*y^3 + 8*x^4*y^2 + 9*x^4*y + 2*x^4*yi^4 + 4*x^4*yi^3 + 8*x^4*yi^2 + 9*x^4*yi + 10*x^4 + x^3*y^5 + 4*x^3*y^4 + 10*x^3*y^3 + 18*x^3*y^2 + 22*x^3*y + x^3*yi^5 + 4*x^3*yi^4 + 10*x^3*yi^3 + 18*x^3*yi^2 + 22*x^3*yi + 24*x^3 + 2*x^2*y^5 + 8*x^2*y^4 + 18*x^2*y^3 + 29*x^2*y^2 + 34*x^2*y + 2*x^2*yi^5 + 8*x^2*yi^4 + 18*x^2*yi^3 + 29*x^2*yi^2 + 34*x^2*yi + 35*x^2 + 3*x*y^5 + 9*x*y^4 + 22*x*y^3 + 34*x*y^2 + 41*x*y + 3*x*yi^5 + 9*x*yi^4 + 22*x*yi^3 + 34*x*yi^2 + 41*x*yi + 42*x + xi^5*y^3 + 2*xi^5*y^2 + 3*xi^5*y + xi^5*yi^3 + 2*xi^5*yi^2 + 3*xi^5*yi + 3*xi^5 + 2*xi^4*y^4 + 4*xi^4*y^3 + 8*xi^4*y^2 + 9*xi^4*y + 2*xi^4*yi^4 + 4*xi^4*yi^3 + 8*xi^4*yi^2 + 9*xi^4*yi + 10*xi^4 + xi^3*y^5 + 4*xi^3*y^4 + 10*xi^3*y^3 + 18*xi^3*y^2 + 22*xi^3*y + xi^3*yi^5 + 4*xi^3*yi^4 + 10*xi^3*yi^3 + 18*xi^3*yi^2 + 22*xi^3*yi + 24*xi^3 + 2*xi^2*y^5 + 8*xi^2*y^4 + 18*xi^2*y^3 + 29*xi^2*y^2 + 34*xi^2*y + 2*xi^2*yi^5 + 8*xi^2*yi^4 + 18*xi^2*yi^3 + 29*xi^2*yi^2 + 34*xi^2*yi + 35*xi^2 + 3*xi*y^5 + 9*xi*y^4 + 22*xi*y^3 + 34*xi*y^2 + 41*xi*y + 3*xi*yi^5 + 9*xi*yi^4 + 22*xi*yi^3 + 34*xi*yi^2 + 41*xi*yi + 42*xi + 3*y^5 + 10*y^4 + 24*y^3 + 35*y^2 + 42*y + 3*yi^5 + 10*yi^4 + 24*yi^3 + 35*yi^2 + 42*yi + 40) * h2 + (3*x^3*y^4 + 6*x^3*y^3*yi + 6*x^3*y^3 + 6*x^3*y^2*yi^2 + 12*x^3*y^2*yi + 9*x^3*y^2 + 6*x^3*y*yi^3 + 12*x^3*y*yi^2 + 12*x^3*y*yi + 6*x^3*y + 3*x^3*yi^4 + 6*x^3*yi^3 + 9*x^3*yi^2 + 6*x^3*yi + 3*x^3 + 4*x^2*xi*y^4 + 8*x^2*xi*y^3*yi + 8*x^2*xi*y^3 + 8*x^2*xi*y^2*yi^2 + 16*x^2*xi*y^2*yi + 12*x^2*xi*y^2 + 8*x^2*xi*y*yi^3 + 16*x^2*xi*y*yi^2 + 16*x^2*xi*y*yi + 8*x^2*xi*y + 4*x^2*xi*yi^4 + 8*x^2*xi*yi^3 + 12*x^2*xi*yi^2 + 8*x^2*xi*yi + 4*x^2*xi + 2*x^2*y^5 + 6*x^2*y^4*yi + 10*x^2*y^4 + 8*x^2*y^3*yi^2 + 24*x^2*y^3*yi + 14*x^2*y^3 + 8*x^2*y^2*yi^3 + 28*x^2*y^2*yi^2 + 26*x^2*y^2*yi + 14*x^2*y^2 + 6*x^2*y*yi^4 + 24*x^2*y*yi^3 + 26*x^2*y*yi^2 + 16*x^2*y*yi + 6*x^2*y + 2*x^2*yi^5 + 10*x^2*yi^4 + 14*x^2*yi^3 + 14*x^2*yi^2 + 6*x^2*yi + 2*x^2 + 4*x*xi^2*y^4 + 8*x*xi^2*y^3*yi + 8*x*xi^2*y^3 + 8*x*xi^2*y^2*yi^2 + 16*x*xi^2*y^2*yi + 12*x*xi^2*y^2 + 8*x*xi^2*y*yi^3 + 16*x*xi^2*y*yi^2 + 16*x*xi^2*y*yi + 8*x*xi^2*y + 4*x*xi^2*yi^4 + 8*x*xi^2*yi^3 + 12*x*xi^2*yi^2 + 8*x*xi^2*yi + 4*x*xi^2 + 2*x*xi*y^5 + 6*x*xi*y^4*yi + 12*x*xi*y^4 + 8*x*xi*y^3*yi^2 + 28*x*xi*y^3*yi + 16*x*xi*y^3 + 8*x*xi*y^2*yi^3 + 32*x*xi*y^2*yi^2 + 28*x*xi*y^2*yi + 16*x*xi*y^2 + 6*x*xi*y*yi^4 + 28*x*xi*y*yi^3 + 28*x*xi*y*yi^2 + 16*x*xi*y*yi + 6*x*xi*y + 2*x*xi*yi^5 + 12*x*xi*yi^4 + 16*x*xi*yi^3 + 16*x*xi*yi^2 + 6*x*xi*yi + 2*x*xi + 4*x*y^5 + 12*x*y^4*yi + 16*x*y^4 + 16*x*y^3*yi^2 + 34*x*y^3*yi + 22*x*y^3 + 16*x*y^2*yi^3 + 36*x*y^2*yi^2 + 36*x*y^2*yi + 26*x*y^2 + 12*x*y*yi^4 + 34*x*y*yi^3 + 36*x*y*yi^2 + 30*x*y*yi + 14*x*y + 4*x*yi^5 + 16*x*yi^4 + 22*x*yi^3 + 26*x*yi^2 + 14*x*yi + 8*x + 3*xi^3*y^4 + 6*xi^3*y^3*yi + 6*xi^3*y^3 + 6*xi^3*y^2*yi^2 + 12*xi^3*y^2*yi + 9*xi^3*y^2 + 6*xi^3*y*yi^3 + 12*xi^3*y*yi^2 + 12*xi^3*y*yi + 6*xi^3*y + 3*xi^3*yi^4 + 6*xi^3*yi^3 + 9*xi^3*yi^2 + 6*xi^3*yi + 3*xi^3 + 2*xi^2*y^5 + 6*xi^2*y^4*yi + 10*xi^2*y^4 + 8*xi^2*y^3*yi^2 + 24*xi^2*y^3*yi + 14*xi^2*y^3 + 8*xi^2*y^2*yi^3 + 28*xi^2*y^2*yi^2 + 26*xi^2*y^2*yi + 14*xi^2*y^2 + 6*xi^2*y*yi^4 + 24*xi^2*y*yi^3 + 26*xi^2*y*yi^2 + 16*xi^2*y*yi + 6*xi^2*y + 2*xi^2*yi^5 + 10*xi^2*yi^4 + 14*xi^2*yi^3 + 14*xi^2*yi^2 + 6*xi^2*yi + 2*xi^2 + 4*xi*y^5 + 12*xi*y^4*yi + 16*xi*y^4 + 16*xi*y^3*yi^2 + 34*xi*y^3*yi + 22*xi*y^3 + 16*xi*y^2*yi^3 + 36*xi*y^2*yi^2 + 36*xi*y^2*yi + 26*xi*y^2 + 12*xi*y*yi^4 + 34*xi*y*yi^3 + 36*xi*y*yi^2 + 30*xi*y*yi + 14*xi*y + 4*xi*yi^5 + 16*xi*yi^4 + 22*xi*yi^3 + 26*xi*yi^2 + 14*xi*yi + 8*xi + 6*y^5 + 18*y^4*yi + 20*y^4 + 24*y^3*yi^2 + 44*y^3*yi + 26*y^3 + 24*y^2*yi^3 + 48*y^2*yi^2 + 42*y^2*yi + 24*y^2 + 18*y*yi^4 + 44*y*yi^3 + 42*y*yi^2 + 24*y*yi + 10*y + 6*yi^5 + 20*yi^4 + 26*yi^3 + 24*yi^2 + 10*yi + 4) * hx + (2*x^5*y^2 + 2*x^5*y*yi + 4*x^5*y + 2*x^5*yi^2 + 4*x^5*yi + 6*x^5 + 3*x^4*y^3 + 4*x^4*y^2*yi + 10*x^4*y^2 + 4*x^4*y*yi^2 + 12*x^4*y*yi + 16*x^4*y + 3*x^4*yi^3 + 10*x^4*yi^2 + 16*x^4*yi + 20*x^4 + 6*x^3*y^3 + 8*x^3*y^2*yi + 20*x^3*y^2 + 8*x^3*y*yi^2 + 22*x^3*y*yi + 34*x^3*y + 6*x^3*yi^3 + 20*x^3*yi^2 + 34*x^3*yi + 44*x^3 + 15*x^2*y^3 + 20*x^2*y^2*yi + 38*x^2*y^2 + 20*x^2*y*yi^2 + 44*x^2*y*yi + 60*x^2*y + 15*x^2*yi^3 + 38*x^2*yi^2 + 60*x^2*yi + 68*x^2 + 18*x*y^3 + 24*x*y^2*yi + 40*x*y^2 + 24*x*y*yi^2 + 42*x*y*yi + 66*x*y + 18*x*yi^3 + 40*x*yi^2 + 66*x*yi + 76*x + 2*xi^5*y^2 + 2*xi^5*y*yi + 4*xi^5*y + 2*xi^5*yi^2 + 4*xi^5*yi + 6*xi^5 + 3*xi^4*y^3 + 4*xi^4*y^2*yi + 10*xi^4*y^2 + 4*xi^4*y*yi^2 + 12*xi^4*y*yi + 16*xi^4*y + 3*xi^4*yi^3 + 10*xi^4*yi^2 + 16*xi^4*yi + 20*xi^4 + 6*xi^3*y^3 + 8*xi^3*y^2*yi + 20*xi^3*y^2 + 8*xi^3*y*yi^2 + 22*xi^3*y*yi + 34*xi^3*y + 6*xi^3*yi^3 + 20*xi^3*yi^2 + 34*xi^3*yi + 44*xi^3 + 15*xi^2*y^3 + 20*xi^2*y^2*yi + 38*xi^2*y^2 + 20*xi^2*y*yi^2 + 44*xi^2*y*yi + 60*xi^2*y + 15*xi^2*yi^3 + 38*xi^2*yi^2 + 60*xi^2*yi + 68*xi^2 + 18*xi*y^3 + 24*xi*y^2*yi + 40*xi*y^2 + 24*xi*y*yi^2 + 42*xi*y*yi + 66*xi*y + 18*xi*yi^3 + 40*xi*yi^2 + 66*xi*yi + 76*xi + 21*y^3 + 28*y^2*yi + 46*y^2 + 28*y*yi^2 + 50*y*yi + 74*y + 21*yi^3 + 46*yi^2 + 74*yi + 76) * hy

/-- Psi_5(t)^2 t = t(x^5) for t = x + 1/x: D_5(t) = t^5 + t^3 + t. -/
theorem d5_identity (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    ((x + xi)^2 + (x + xi) + 1)^2 * (x + xi) = x^5 + xi^5 := by
  linear_combination (x^4 + 4*x^3 + 5*x^2 + 10*x + xi^4 + 4*xi^3 + 5*xi^2 + 10*xi + 8) * h2 + (5*x^3 + 10*x^2*xi + 8*x^2 + 10*x*xi^2 + 12*x*xi + 19*x + 5*xi^3 + 8*xi^2 + 19*xi + 16) * hx

/-- D_6(t) = t^6 + t^2 for t = x + 1/x. -/
theorem d6_identity (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    (x + xi)^6 + (x + xi)^2 = x^6 + xi^6 := by
  linear_combination (3*x^4 + 8*x^2 + 3*xi^4 + 8*xi^2 + 11) * h2 + (6*x^4 + 15*x^3*xi + 20*x^2*xi^2 + 15*x^2 + 15*x*xi^3 + 20*x*xi + 6*xi^4 + 15*xi^2 + 22) * hx

end Polys

section Field

variable {K : Type*} [Field K] [CharP K 2]

theorem ev_r1968276 {x y : K} (hx : x ≠ 0) (hy : y ≠ 0) :
    ev r1968276Offsets x y = ((x + x⁻¹) * (y + y⁻¹))^2 * ev vOffsets x y := by
  rw [ev_v, r1968276_poly two_eq_zero_of_charTwo x x⁻¹ y y⁻¹ (mul_inv_cancel₀ hx)
    (mul_inv_cancel₀ hy)]
  simp [ev, r1968276Offsets]
  ring

theorem ev_r985232 {x y : K} (hx : x ≠ 0) (hy : y ≠ 0) :
    ev r985232Offsets x y = ((x + x⁻¹) * (y + y⁻¹))^2 * (x + x⁻¹ + y + y⁻¹) * ev wOffsets x y := by
  rw [ev_w, r985232_poly two_eq_zero_of_charTwo x x⁻¹ y y⁻¹ (mul_inv_cancel₀ hx)
    (mul_inv_cancel₀ hy)]
  simp [ev, r985232Offsets]
  ring

theorem ev_r1431278 {x y : K} (hx : x ≠ 0) (hy : y ≠ 0) :
    ev r1431278Offsets x y =
      ((x + x⁻¹)^2 + (x + x⁻¹) + 1) * ((y + y⁻¹)^2 + (y + y⁻¹) + 1) * ev vOffsets x y := by
  rw [ev_v, r1431278_poly two_eq_zero_of_charTwo x x⁻¹ y y⁻¹ (mul_inv_cancel₀ hx)
    (mul_inv_cancel₀ hy)]
  simp [ev, r1431278Offsets]
  ring

theorem ev_r699738 {x y : K} (hx : x ≠ 0) (hy : y ≠ 0) :
    ev r699738Offsets x y =
      ((x + x⁻¹)^2 + (x + x⁻¹) + 1) * ((y + y⁻¹)^2 + (y + y⁻¹) + 1) * (x + x⁻¹ + y + y⁻¹) *
        ev wOffsets x y := by
  rw [ev_w, r699738_poly two_eq_zero_of_charTwo x x⁻¹ y y⁻¹ (mul_inv_cancel₀ hx)
    (mul_inv_cancel₀ hy)]
  simp [ev, r699738Offsets]
  ring

/-- t(X^2) = t(X)^2. -/
theorem t_sq (h2 : (2 : K) = 0) (Z : K) (hZ : Z ≠ 0) : Z ^ 2 + (Z ^ 2)⁻¹ = (Z + Z⁻¹) ^ 2 := by
  rw [← inv_pow]
  linear_combination (-(Z * Z⁻¹)) * h2

/-- t(X^2) + t(Y^2) = t(XY) t(X/Y). -/
theorem t_sum (X Y : K) (hX : X ≠ 0) (hY : Y ≠ 0) :
    X ^ 2 + (X ^ 2)⁻¹ + Y ^ 2 + (Y ^ 2)⁻¹ = (X * Y + X⁻¹ * Y⁻¹) * (X * Y⁻¹ + X⁻¹ * Y) := by
  rw [← inv_pow, ← inv_pow]
  linear_combination (-(Y ^ 2 + Y⁻¹ ^ 2)) * mul_inv_cancel₀ hX + (-(X ^ 2 + X⁻¹ ^ 2)) *
    mul_inv_cancel₀ hY

/-- Psi_5(t^2) = Psi_5(t)^2. -/
theorem psi5_sq (h2 : (2 : K) = 0) (a : K) : (a ^ 2) ^ 2 + a ^ 2 + 1 = (a ^ 2 + a + 1) ^ 2 := by
  linear_combination (-(a ^ 3 + a ^ 2 + a)) * h2

/-- 5 = 2^23 mod 37: t(z^5) = t(z)^(2^23). -/
theorem t_frob23 {X : K} (hX : X ^ 37 = 1) : (X + X⁻¹) ^ 2 ^ 23 = X ^ 5 + X⁻¹ ^ 5 := by
  rw [inv_eq_pow36 hX, add_pow_char_pow, ← pow_mul, ← pow_mul, pow_mod37 hX (2 ^ 23),
    pow_mod37 hX (36 * 2 ^ 23), pow_mod37 hX (36 * 5), show 2 ^ 23 % 37 = 5 by norm_num,
    show 36 * 2 ^ 23 % 37 = 32 by norm_num, show 36 * 5 % 37 = 32 by norm_num]

/-- 2^9 = -6 mod 37: t(z)^(2^9) = t(z^6). -/
theorem t_frob9 {X : K} (hX : X ^ 37 = 1) : (X + X⁻¹) ^ 2 ^ 9 = X ^ 6 + X⁻¹ ^ 6 := by
  rw [inv_eq_pow36 hX, add_pow_char_pow, ← pow_mul, ← pow_mul, pow_mod37 hX (2 ^ 9),
    pow_mod37 hX (36 * 2 ^ 9), pow_mod37 hX (36 * 6), show 2 ^ 9 % 37 = 31 by norm_num,
    show 36 * 2 ^ 9 % 37 = 6 by norm_num, show 36 * 6 % 37 = 31 by norm_num, add_comm]

/-- The norm identity: t^513 = t^3 (t + 1)^4, i.e. t^510 = (t + 1)^4 for t = t(z) ≠ 0. -/
theorem t_norm (h2 : (2 : K) = 0) {X : K} (hX : X ^ 37 = 1) (ht : X + X⁻¹ ≠ 0) :
    (X + X⁻¹ + 1) ^ 4 = (X + X⁻¹) ^ 510 := by
  have hX0 : X ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hX
  have h6 := d6_identity h2 X X⁻¹ (mul_inv_cancel₀ hX0)
  rw [← t_frob9 hX] at h6
  apply mul_left_cancel₀ (pow_ne_zero 2 ht)
  have e : (X + X⁻¹) ^ 2 * (X + X⁻¹) ^ 510 = (X + X⁻¹) ^ 2 ^ 9 := by
    rw [← pow_add]
    norm_num
  rw [e, ← h6]
  linear_combination (2 * (X + X⁻¹) ^ 5 + 3 * (X + X⁻¹) ^ 4 + 2 * (X + X⁻¹) ^ 3) * h2

/-- The period divides L when the eigenvalues at (X^2, Y^2) are 0 or L-th roots of unity. -/
theorem period_dvd_of_val' (D : Finset (ℤ × ℤ)) (L : ℕ)
    (hv : ∀ X Y : AlgebraicClosure (ZMod 2), X ^ 37 = 1 → Y ^ 37 = 1 →
        ev D (X ^ 2) (Y ^ 2) = 0 ∨ ev D (X ^ 2) (Y ^ 2) ^ L = 1) :
    period 37 D ∣ L := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot (m := 37) ⟨18, rfl⟩
  rw [← isPeriod_iff_period_dvd, isPeriod_iff hζ]
  intro j _ k _
  rw [lam_eq_ev hζ.pow_eq_one]
  have hp : ∀ i : ℕ, ((ζ ^ i)⁻¹) ^ 37 = 1 := fun i => by
    rw [inv_pow, ← pow_mul, mul_comm, pow_mul, hζ.pow_eq_one, one_pow, inv_one]
  have sq : ∀ z : AlgebraicClosure (ZMod 2), z ^ 37 = 1 → (z ^ 19) ^ 2 = z ∧ (z ^ 19) ^ 37 = 1 :=
    fun z hz => ⟨by rw [← pow_mul, show 19 * 2 = 37 + 1 by norm_num, pow_succ, hz, one_mul],
      by rw [← pow_mul, mul_comm, pow_mul, hz, one_pow]⟩
  have hx := sq _ (hp j)
  have hy := sq _ (hp k)
  have := hv _ _ hx.2 hy.2
  rwa [hx.1, hy.1] at this

/-- A cube of a rule-90 value is a 29127-th root of unity. -/
theorem t3_val {X : K} (hX : X ^ 37 = 1) (ht : X + X⁻¹ ≠ 0) : ((X + X⁻¹) ^ 3) ^ 29127 = 1 := by
  rw [← pow_mul, show 3 * 29127 = 87381 by norm_num]
  exact (r90_val hX).resolve_left ht

/-- t^(2^23 - 2) is a 29127-th root of unity: 3 divides 2^23 - 2. -/
theorem tpsi_val {X : K} (hX : X ^ 37 = 1) (ht : X + X⁻¹ ≠ 0) :
    ((X + X⁻¹) ^ (2 ^ 23 - 2)) ^ 29127 = 1 := by
  rw [← pow_mul, show (2 ^ 23 - 2) * 29127 = 87381 * 2796202 by norm_num, pow_mul,
    (r90_val hX).resolve_left ht, one_pow]

theorem sv_val {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    svNat X Y = 0 ∨ svNat X Y ^ 29127 = 1 := by
  rcases eq_zero_or_pow_eq_one (by norm_num) (sv_frob hX hY) with h0 | h1
  · exact Or.inl h0
  · right
    rw [show (29127 : ℕ) = (2 ^ 9 - 1) * 57 by norm_num, pow_mul, h1, one_pow]

theorem sh_val {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    shNat X Y = 0 ∨ shNat X Y ^ 29127 = 1 := by
  rcases eq_zero_or_pow_eq_one (by norm_num) (sh_frob hX hY) with h0 | h1
  · exact Or.inl h0
  · right
    rw [show (29127 : ℕ) = (2 ^ 9 - 1) * 57 by norm_num, pow_mul, h1, one_pow]

theorem prod_val' {u w : K} {L : ℕ} (hu : u = 0 ∨ u ^ L = 1) (hw : w = 0 ∨ w ^ L = 1) :
    u * w = 0 ∨ (u * w) ^ L = 1 := by
  rcases hu with hu | hu
  · left; rw [hu, zero_mul]
  rcases hw with hw | hw
  · left; rw [hw, mul_zero]
  · right; rw [mul_pow, hu, hw, one_mul]

/-- **1968276 = a^2 b^2 V at (X^2, Y^2)**: t(X)^3 t(Y)^3 sv. -/
theorem r1968276_val_sq {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    ev r1968276Offsets (X ^ 2) (Y ^ 2) = 0 ∨ ev r1968276Offsets (X ^ 2) (Y ^ 2) ^ 29127 = 1 := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  have hX0 : X ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hX
  have hY0 : Y ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hY
  have hid := v_identity h2 X X⁻¹ Y Y⁻¹ (mul_inv_cancel₀ hX0) (mul_inv_cancel₀ hY0)
  rw [inv_pow, inv_pow, svPoly_eq hX hY] at hid
  have key : ev r1968276Offsets (X ^ 2) (Y ^ 2) =
      (X + X⁻¹) ^ 3 * (Y + Y⁻¹) ^ 3 * svNat X Y := by
    rw [ev_r1968276 (pow_ne_zero 2 hX0) (pow_ne_zero 2 hY0), ev_v, t_sq h2 X hX0, t_sq h2 Y hY0,
      ← hid]
    ring
  rw [key]
  by_cases n1 : X + X⁻¹ = 0
  · left; rw [n1]; ring
  by_cases n2 : Y + Y⁻¹ = 0
  · left; rw [n2]; ring
  exact prod_val' (prod_val' (Or.inr (t3_val hX n1)) (Or.inr (t3_val hY n2))) (sv_val hX hY)

/-- **985232 = a^2 b^2 (a + b) W at (X^2, Y^2)**: t(X)^3 t(Y)^3 sh. -/
theorem r985232_val_sq {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    ev r985232Offsets (X ^ 2) (Y ^ 2) = 0 ∨ ev r985232Offsets (X ^ 2) (Y ^ 2) ^ 29127 = 1 := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  have hX0 : X ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hX
  have hY0 : Y ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hY
  have hid := w_identity h2 X X⁻¹ Y Y⁻¹ (mul_inv_cancel₀ hX0) (mul_inv_cancel₀ hY0)
  rw [inv_pow, inv_pow, shPoly_eq hX hY] at hid
  have key : ev r985232Offsets (X ^ 2) (Y ^ 2) =
      (X + X⁻¹) ^ 3 * (Y + Y⁻¹) ^ 3 * shNat X Y := by
    rw [ev_r985232 (pow_ne_zero 2 hX0) (pow_ne_zero 2 hY0), ev_w, t_sum X Y hX0 hY0,
      t_sq h2 X hX0, t_sq h2 Y hY0, ← hid]
    ring
  rw [key]
  by_cases n1 : X + X⁻¹ = 0
  · left; rw [n1]; ring
  by_cases n2 : Y + Y⁻¹ = 0
  · left; rw [n2]; ring
  exact prod_val' (prod_val' (Or.inr (t3_val hX n1)) (Or.inr (t3_val hY n2))) (sh_val hX hY)

/-- The value of a Psi_5 rule on an axis: Psi_5(t)^2 t^2 (t + 1)^4 = t^(2^23 + 511) is a
29127-th root of unity (3 divides 2^23 + 511). -/
theorem axis_val (h2 : (2 : K) = 0) {Y : K} (hY : Y ^ 37 = 1) (nt : Y + Y⁻¹ ≠ 0) :
    ((((Y + Y⁻¹) ^ 2 + (Y + Y⁻¹) + 1) ^ 2 * (Y + Y⁻¹)) * (Y + Y⁻¹) * (Y + Y⁻¹ + 1) ^ 4) ^ 29127 =
      1 := by
  have hY0 : Y ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hY
  rw [d5_identity h2 Y Y⁻¹ (mul_inv_cancel₀ hY0), ← t_frob23 hY, t_norm h2 hY nt, ← pow_succ,
    ← pow_add, ← pow_mul, show (2 ^ 23 + 1 + 510) * 29127 = 87381 * 2796373 by norm_num, pow_mul,
    (r90_val hY).resolve_left nt, one_pow]

/-- t^(2^23 - 2) t^2 = Psi_5(t)^2 t for t = t(Z), Z^37 = 1. -/
theorem psi_pow_identity (h2 : (2 : K) = 0) {Z : K} (hZ : Z ^ 37 = 1) (hZ0 : Z ≠ 0) :
    (Z + Z⁻¹) ^ (2 ^ 23 - 2) * (Z + Z⁻¹) ^ 2 =
      ((Z + Z⁻¹) ^ 2 + (Z + Z⁻¹) + 1) ^ 2 * (Z + Z⁻¹) := by
  rw [← pow_add, show 2 ^ 23 - 2 + 2 = 2 ^ 23 by norm_num, t_frob23 hZ,
    d5_identity h2 Z Z⁻¹ (mul_inv_cancel₀ hZ0)]

/-- **1431278 = Psi_5(a) Psi_5(b) V at (X^2, Y^2)**. -/
theorem r1431278_val_sq {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    ev r1431278Offsets (X ^ 2) (Y ^ 2) = 0 ∨ ev r1431278Offsets (X ^ 2) (Y ^ 2) ^ 29127 = 1 := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  have hX0 : X ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hX
  have hY0 : Y ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hY
  have hid := v_identity h2 X X⁻¹ Y Y⁻¹ (mul_inv_cancel₀ hX0) (mul_inv_cancel₀ hY0)
  rw [inv_pow, inv_pow, svPoly_eq hX hY] at hid
  rw [ev_r1431278 (pow_ne_zero 2 hX0) (pow_ne_zero 2 hY0), ev_v, t_sq h2 X hX0, t_sq h2 Y hY0,
    psi5_sq h2, psi5_sq h2]
  by_cases n1 : X + X⁻¹ = 0
  · -- X = 1: the axis; the value is Psi_5(t(Y))^2 t(Y)^2 (t(Y)^2 + 1)^2
    rw [n1]
    have hX1 := eq_one_of_add_inv hX n1
    subst hX1
    rw [one_pow, inv_one, vPoly_axisx h2 _ _ (mul_inv_cancel₀ (pow_ne_zero 2 hY0)), t_sq h2 Y hY0]
    by_cases n2 : Y + Y⁻¹ = 0
    · left; rw [n2]; ring
    right
    have av := axis_val h2 hY n2
    generalize Y + Y⁻¹ = t at av ⊢
    convert av using 2
    linear_combination (-((t ^ 2 + t + 1) ^ 2 * t ^ 2 * (2 * t ^ 3 + 2 * t ^ 2 + 2 * t))) * h2
  by_cases n2 : Y + Y⁻¹ = 0
  · rw [n2]
    have hY1 := eq_one_of_add_inv hY n2
    subst hY1
    rw [one_pow, inv_one, vPoly_axisy h2 _ _ (mul_inv_cancel₀ (pow_ne_zero 2 hX0)), t_sq h2 X hX0]
    right
    have av := axis_val h2 hX n1
    generalize X + X⁻¹ = t at av ⊢
    convert av using 2
    linear_combination (-((t ^ 2 + t + 1) ^ 2 * t ^ 2 * (2 * t ^ 3 + 2 * t ^ 2 + 2 * t))) * h2
  -- generic: multiply by t(X)^2 t(Y)^2
  have hu : (X + X⁻¹) ^ 2 * (Y + Y⁻¹) ^ 2 ≠ 0 := mul_ne_zero (pow_ne_zero 2 n1) (pow_ne_zero 2 n2)
  have eX := psi_pow_identity h2 hX hX0
  have eY := psi_pow_identity h2 hY hY0
  have key : ((X + X⁻¹) ^ 2 + (X + X⁻¹) + 1) ^ 2 * ((Y + Y⁻¹) ^ 2 + (Y + Y⁻¹) + 1) ^ 2 *
      vPoly (X ^ 2) (X ^ 2)⁻¹ (Y ^ 2) (Y ^ 2)⁻¹ =
      (X + X⁻¹) ^ (2 ^ 23 - 2) * (Y + Y⁻¹) ^ (2 ^ 23 - 2) * svNat X Y := by
    apply mul_right_cancel₀ hu
    rw [← hid]
    generalize (X + X⁻¹) ^ (2 ^ 23 - 2) = pX at eX ⊢
    generalize (Y + Y⁻¹) ^ (2 ^ 23 - 2) = pY at eY ⊢
    generalize vPoly (X ^ 2) (X ^ 2)⁻¹ (Y ^ 2) (Y ^ 2)⁻¹ = v
    generalize X + X⁻¹ = t at eX ⊢
    generalize Y + Y⁻¹ = s at eY ⊢
    linear_combination (-(v * t * s * (s ^ 2 + s + 1) ^ 2 * s)) * eX +
      (-(v * t * s * pX * t ^ 2)) * eY
  rw [key]
  exact prod_val' (prod_val' (Or.inr (tpsi_val hX n1)) (Or.inr (tpsi_val hY n2))) (sv_val hX hY)

/-- **699738 = Psi_5(a) Psi_5(b) (a + b) W at (X^2, Y^2)**. -/
theorem r699738_val_sq {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    ev r699738Offsets (X ^ 2) (Y ^ 2) = 0 ∨ ev r699738Offsets (X ^ 2) (Y ^ 2) ^ 29127 = 1 := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  have hX0 : X ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hX
  have hY0 : Y ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hY
  have hid := w_identity h2 X X⁻¹ Y Y⁻¹ (mul_inv_cancel₀ hX0) (mul_inv_cancel₀ hY0)
  rw [inv_pow, inv_pow, shPoly_eq hX hY] at hid
  rw [ev_r699738 (pow_ne_zero 2 hX0) (pow_ne_zero 2 hY0), ev_w, t_sum X Y hX0 hY0,
    t_sq h2 X hX0, t_sq h2 Y hY0, psi5_sq h2, psi5_sq h2]
  by_cases n1 : X + X⁻¹ = 0
  · -- X = 1: the value is Psi_5(t(Y))^2 (t(Y) t(Y)) (t(Y)^2 + 1)^2
    rw [n1]
    have hX1 := eq_one_of_add_inv hX n1
    subst hX1
    simp only [one_pow, inv_one, one_mul]
    rw [wPoly_axisx h2 _ _ (mul_inv_cancel₀ (pow_ne_zero 2 hY0)), t_sq h2 Y hY0, add_comm Y⁻¹ Y]
    by_cases n2 : Y + Y⁻¹ = 0
    · left; rw [n2]; ring
    right
    have av := axis_val h2 hY n2
    generalize Y + Y⁻¹ = t at av ⊢
    convert av using 2
    linear_combination (-((t ^ 2 + t + 1) ^ 2 * t ^ 2 * (2 * t ^ 3 + 2 * t ^ 2 + 2 * t))) * h2
  by_cases n2 : Y + Y⁻¹ = 0
  · rw [n2]
    have hY1 := eq_one_of_add_inv hY n2
    subst hY1
    simp only [one_pow, inv_one, mul_one]
    rw [wPoly_axisy h2 _ _ (mul_inv_cancel₀ (pow_ne_zero 2 hX0)), t_sq h2 X hX0]
    right
    have av := axis_val h2 hX n1
    generalize X + X⁻¹ = t at av ⊢
    convert av using 2
    linear_combination (-((t ^ 2 + t + 1) ^ 2 * t ^ 2 * (2 * t ^ 3 + 2 * t ^ 2 + 2 * t))) * h2
  have hu : (X + X⁻¹) ^ 2 * (Y + Y⁻¹) ^ 2 ≠ 0 := mul_ne_zero (pow_ne_zero 2 n1) (pow_ne_zero 2 n2)
  have eX := psi_pow_identity h2 hX hX0
  have eY := psi_pow_identity h2 hY hY0
  have key : ((X + X⁻¹) ^ 2 + (X + X⁻¹) + 1) ^ 2 * ((Y + Y⁻¹) ^ 2 + (Y + Y⁻¹) + 1) ^ 2 *
      ((X * Y + X⁻¹ * Y⁻¹) * (X * Y⁻¹ + X⁻¹ * Y)) * wPoly (X ^ 2) (X ^ 2)⁻¹ (Y ^ 2) (Y ^ 2)⁻¹ =
      (X + X⁻¹) ^ (2 ^ 23 - 2) * (Y + Y⁻¹) ^ (2 ^ 23 - 2) * shNat X Y := by
    apply mul_right_cancel₀ hu
    rw [← hid]
    generalize (X + X⁻¹) ^ (2 ^ 23 - 2) = pX at eX ⊢
    generalize (Y + Y⁻¹) ^ (2 ^ 23 - 2) = pY at eY ⊢
    generalize wPoly (X ^ 2) (X ^ 2)⁻¹ (Y ^ 2) (Y ^ 2)⁻¹ = w
    generalize X * Y + X⁻¹ * Y⁻¹ = p
    generalize X * Y⁻¹ + X⁻¹ * Y = q
    generalize X + X⁻¹ = t at eX ⊢
    generalize Y + Y⁻¹ = s at eY ⊢
    linear_combination (-(w * p * q * t * s * (s ^ 2 + s + 1) ^ 2 * s)) * eX +
      (-(w * p * q * t * s * pX * t ^ 2)) * eY
  rw [key]
  exact prod_val' (prod_val' (Or.inr (tpsi_val hX n1)) (Or.inr (tpsi_val hY n2))) (sh_val hX hY)

end Field

/-- **Theorem.** On the 37 x 37 torus the period of family rule 1968276 = a^2 b^2 V divides
29127 = (2^18 - 1)/9: every eigenvalue is a ninth power in F(2^18). -/
theorem period_r1968276_dvd : period 37 r1968276Offsets ∣ 29127 :=
  period_dvd_of_val' _ _ fun _ _ hX hY => r1968276_val_sq hX hY

/-- The same for 985232 = a^2 b^2 (a + b) W. -/
theorem period_r985232_dvd : period 37 r985232Offsets ∣ 29127 :=
  period_dvd_of_val' _ _ fun _ _ hX hY => r985232_val_sq hX hY

/-- The same for 1431278 = Psi_5(a) Psi_5(b) V. -/
theorem period_r1431278_dvd : period 37 r1431278Offsets ∣ 29127 :=
  period_dvd_of_val' _ _ fun _ _ hX hY => r1431278_val_sq hX hY

/-- The same for 699738 = Psi_5(a) Psi_5(b) (a + b) W. -/
theorem period_r699738_dvd : period 37 r699738Offsets ∣ 29127 :=
  period_dvd_of_val' _ _ fun _ _ hX hY => r699738_val_sq hX hY

end Pilot37c

end LatticeProofs
