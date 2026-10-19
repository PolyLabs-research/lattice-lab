/-
Formal results for the m = 37 pilot (CARD.md, proposal.md): the half-Frobenius mechanism.

For each of the six rules D, on the 37 x 37 torus,

    period 37 D ∣ lcm(511, period 37 r90)            (r90 = x + 1/x, rule 90)

* `period_w_dvd`               A4 + K8 + B4 + self (W)
* `period_k8m8e4_dvd`          K8 + M8 + E4          = ab W
* `period_c4l8m8_dvd`          C4 + L8 + M8          = (a + b) W
* `period_a4b4c4l8e4self_dvd`  A4 + B4 + C4 + L8 + E4 + self = (a + 1)(b + 1) W
* `period_v_dvd`               C4 + L8 + M8 + E4 (V)
* `period_tri_dvd`             the triangle rule VS + T9 + T13 + self, through its plane rule s

and `period_r90_dvd` proves that rule 90's period at 37 divides 87381 = (2^18 - 1)/3 (an explicit
cube root of t = z + 1/z modulo Psi_37). Since 511 divides 87381, each of the six has
`period 37 D ∣ 87381` unconditionally (`period_w_dvd_87381`, ..., `period_tri_dvd_87381`): every
eigenvalue is a cube in F(2^18).

The proofs: an identity over GF(2) (`w_identity`, `v_identity`, `tri_identity`), e.g.

    W(x^2, y^2) * t(x) t(y) t(xy) t(x/y) = Sh(7, 5),     t(z) = z + 1/z,

whose right side is permuted by 2^9 = -6 (mod 37), so its eigenvalues are fixed by the 2^9-th
power (`sh_frob`, `sv_frob`, `tb_frob`) and lie in F(2^9), of order dividing 511; the t-factors are
rule-90 eigenvalues, of order dividing P; on the lines where a t-factor vanishes the rule reduces
to (t + 1)^2 = t(z^3)/t(z) or t(z^9)/t(z) (`line_val`, `ratio_val`).
-/
import LatticeProofs

namespace LatticeProofs

namespace Pilot

/-- Rule 90 along the first axis, x + 1/x. -/
def r90Offsets : Finset (ℤ × ℤ) := {(-1, 0), (1, 0)}

/-- The square rule A4 + K8 + B4 + self (atlas rule 189). -/
def wOffsets : Finset (ℤ × ℤ) :=
  {(-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-1, -2), (-1, 2), (0, -2), (0, 0), (0, 2),
    (1, -2), (1, 2), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2)}

section Polys

variable {R : Type*} [CommRing R]

/-- W's Laurent polynomial, with xi = 1/x and yi = 1/y. -/
def wPoly (x xi y yi : R) : R :=
  x^2*y^2 + x^2*y + x^2*yi^2 + x^2*yi + x^2 + x*y^2 + x*yi^2 + xi^2*y^2 + xi^2*y + xi^2*yi^2 +
    xi^2*yi + xi^2 + xi*y^2 + xi*yi^2 + y^2 + yi^2 + 1

/-- The shell (+-7, +-5), (+-5, +-7). -/
def shPoly (x xi y yi : R) : R :=
  x^7*y^5 + x^7*yi^5 + x^5*y^7 + x^5*yi^7 + xi^7*y^5 + xi^7*yi^5 + xi^5*y^7 + xi^5*yi^7

/-- **The identity.** W(x^2, y^2) t(x) t(y) t(xy) t(x/y) = Sh(7, 5) in characteristic 2. -/
theorem w_identity (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1) (hy : y * yi = 1) :
    wPoly (x^2) (xi^2) (y^2) (yi^2) * ((x + xi) * (y + yi) * (x*y + xi*yi) * (x*yi + xi*y)) =
      shPoly x xi y yi := by
  unfold wPoly shPoly
  linear_combination (x^7*y^3 + x^7*y + x^7*yi^3 + x^7*yi + 2*x^5*y^5 + 3*x^5*y^3 + 3*x^5*y + 2*x^5*yi^5 + 3*x^5*yi^3 + 3*x^5*yi + x^3*y^7 + 3*x^3*y^5 + 4*x^3*y^3 + 4*x^3*y + x^3*yi^7 + 3*x^3*yi^5 + 4*x^3*yi^3 + 4*x^3*yi + x*y^7 + 3*x*y^5 + 4*x*y^3 + 3*x*y + x*yi^7 + 3*x*yi^5 + 4*x*yi^3 + 3*x*yi + xi^7*y^3 + xi^7*y + xi^7*yi^3 + xi^7*yi + 2*xi^5*y^5 + 3*xi^5*y^3 + 3*xi^5*y + 2*xi^5*yi^5 + 3*xi^5*yi^3 + 3*xi^5*yi + xi^3*y^7 + 3*xi^3*y^5 + 4*xi^3*y^3 + 4*xi^3*y + xi^3*yi^7 + 3*xi^3*yi^5 + 4*xi^3*yi^3 + 4*xi^3*yi + xi*y^7 + 3*xi*y^5 + 4*xi*y^3 + 3*xi*y + xi*yi^7 + 3*xi*yi^5 + 4*xi*yi^3 + 3*xi*yi) * h2 + (x^5*y^7 + 2*x^5*y^6*yi + 2*x^5*y^5*yi^2 + x^5*y^5 + x^5*y^4*yi^3 + 2*x^5*y^4*yi + x^5*y^3*yi^4 + 3*x^5*y^3*yi^2 + x^5*y^3 + 2*x^5*y^2*yi^5 + 3*x^5*y^2*yi^3 + 2*x^5*y^2*yi + 2*x^5*y*yi^6 + 2*x^5*y*yi^4 + 2*x^5*y*yi^2 + x^5*yi^7 + x^5*yi^5 + x^5*yi^3 + x^4*xi*y^7 + 2*x^4*xi*y^6*yi + 2*x^4*xi*y^5*yi^2 + x^4*xi*y^5 + x^4*xi*y^4*yi^3 + 2*x^4*xi*y^4*yi + x^4*xi*y^3*yi^4 + 3*x^4*xi*y^3*yi^2 + x^4*xi*y^3 + 2*x^4*xi*y^2*yi^5 + 3*x^4*xi*y^2*yi^3 + 2*x^4*xi*y^2*yi + 2*x^4*xi*y*yi^6 + 2*x^4*xi*y*yi^4 + 2*x^4*xi*y*yi^2 + x^4*xi*yi^7 + x^4*xi*yi^5 + x^4*xi*yi^3 + x^3*xi^2*y^6*yi + x^3*xi^2*y^5*yi^2 + x^3*xi^2*y^4*yi + x^3*xi^2*y^3*yi^2 + x^3*xi^2*y^2*yi^5 + x^3*xi^2*y^2*yi^3 + x^3*xi^2*y^2*yi + x^3*xi^2*y*yi^6 + x^3*xi^2*y*yi^4 + x^3*xi^2*y*yi^2 + 2*x^3*y^7 + 4*x^3*y^6*yi + 4*x^3*y^5*yi^2 + x^3*y^5 + 2*x^3*y^4*yi^3 + 2*x^3*y^4*yi + 2*x^3*y^3*yi^4 + 3*x^3*y^3*yi^2 + x^3*y^3 + 4*x^3*y^2*yi^5 + 3*x^3*y^2*yi^3 + 2*x^3*y^2*yi + 4*x^3*y*yi^6 + 2*x^3*y*yi^4 + 2*x^3*y*yi^2 + 2*x^3*yi^7 + x^3*yi^5 + x^3*yi^3 + x^2*xi^3*y^6*yi + x^2*xi^3*y^5*yi^2 + x^2*xi^3*y^4*yi + x^2*xi^3*y^3*yi^2 + x^2*xi^3*y^2*yi^5 + x^2*xi^3*y^2*yi^3 + x^2*xi^3*y^2*yi + x^2*xi^3*y*yi^6 + x^2*xi^3*y*yi^4 + x^2*xi^3*y*yi^2 + x^2*xi*y^7 + 4*x^2*xi*y^6*yi + 4*x^2*xi*y^5*yi^2 + x^2*xi*y^4*yi^3 + x^2*xi*y^4*yi + x^2*xi*y^3*yi^4 + x^2*xi*y^3*yi^2 + 4*x^2*xi*y^2*yi^5 + x^2*xi*y^2*yi^3 + x^2*xi*y^2*yi + 4*x^2*xi*y*yi^6 + x^2*xi*y*yi^4 + x^2*xi*y*yi^2 + x^2*xi*yi^7 + x*xi^4*y^7 + 2*x*xi^4*y^6*yi + 2*x*xi^4*y^5*yi^2 + x*xi^4*y^5 + x*xi^4*y^4*yi^3 + 2*x*xi^4*y^4*yi + x*xi^4*y^3*yi^4 + 3*x*xi^4*y^3*yi^2 + x*xi^4*y^3 + 2*x*xi^4*y^2*yi^5 + 3*x*xi^4*y^2*yi^3 + 2*x*xi^4*y^2*yi + 2*x*xi^4*y*yi^6 + 2*x*xi^4*y*yi^4 + 2*x*xi^4*y*yi^2 + x*xi^4*yi^7 + x*xi^4*yi^5 + x*xi^4*yi^3 + x*xi^2*y^7 + 4*x*xi^2*y^6*yi + 4*x*xi^2*y^5*yi^2 + x*xi^2*y^4*yi^3 + x*xi^2*y^4*yi + x*xi^2*y^3*yi^4 + x*xi^2*y^3*yi^2 + 4*x*xi^2*y^2*yi^5 + x*xi^2*y^2*yi^3 + x*xi^2*y^2*yi + 4*x*xi^2*y*yi^6 + x*xi^2*y*yi^4 + x*xi^2*y*yi^2 + x*xi^2*yi^7 + 2*x*y^7 + 6*x*y^6*yi + 6*x*y^5*yi^2 + 2*x*y^4*yi^3 + x*y^4*yi + 2*x*y^3*yi^4 + x*y^3*yi^2 + x*y^3 + 6*x*y^2*yi^5 + x*y^2*yi^3 + 3*x*y^2*yi + 6*x*y*yi^6 + x*y*yi^4 + 3*x*y*yi^2 + 2*x*yi^7 + x*yi^3 + xi^5*y^7 + 2*xi^5*y^6*yi + 2*xi^5*y^5*yi^2 + xi^5*y^5 + xi^5*y^4*yi^3 + 2*xi^5*y^4*yi + xi^5*y^3*yi^4 + 3*xi^5*y^3*yi^2 + xi^5*y^3 + 2*xi^5*y^2*yi^5 + 3*xi^5*y^2*yi^3 + 2*xi^5*y^2*yi + 2*xi^5*y*yi^6 + 2*xi^5*y*yi^4 + 2*xi^5*y*yi^2 + xi^5*yi^7 + xi^5*yi^5 + xi^5*yi^3 + 2*xi^3*y^7 + 4*xi^3*y^6*yi + 4*xi^3*y^5*yi^2 + xi^3*y^5 + 2*xi^3*y^4*yi^3 + 2*xi^3*y^4*yi + 2*xi^3*y^3*yi^4 + 3*xi^3*y^3*yi^2 + xi^3*y^3 + 4*xi^3*y^2*yi^5 + 3*xi^3*y^2*yi^3 + 2*xi^3*y^2*yi + 4*xi^3*y*yi^6 + 2*xi^3*y*yi^4 + 2*xi^3*y*yi^2 + 2*xi^3*yi^7 + xi^3*yi^5 + xi^3*yi^3 + 2*xi*y^7 + 6*xi*y^6*yi + 6*xi*y^5*yi^2 + 2*xi*y^4*yi^3 + xi*y^4*yi + 2*xi*y^3*yi^4 + xi*y^3*yi^2 + xi*y^3 + 6*xi*y^2*yi^5 + xi*y^2*yi^3 + 3*xi*y^2*yi + 6*xi*y*yi^6 + xi*y*yi^4 + 3*xi*y*yi^2 + 2*xi*yi^7 + xi*yi^3) * hx + (x^7*y^5 + x^7*y^4*yi + 2*x^7*y^3 + x^7*y^2*yi + x^7*y*yi^4 + x^7*y*yi^2 + 2*x^7*y + x^7*yi^5 + 2*x^7*yi^3 + 2*x^7*yi + 3*x^5*y^5 + 3*x^5*y^4*yi + x^5*y^3*yi^2 + 5*x^5*y^3 + x^5*y^2*yi^3 + 4*x^5*y^2*yi + 3*x^5*y*yi^4 + 4*x^5*y*yi^2 + 6*x^5*y + 3*x^5*yi^5 + 5*x^5*yi^3 + 6*x^5*yi + 5*x^3*y^5 + 5*x^3*y^4*yi + 2*x^3*y^3*yi^2 + 7*x^3*y^3 + 2*x^3*y^2*yi^3 + 5*x^3*y^2*yi + 5*x^3*y*yi^4 + 5*x^3*y*yi^2 + 8*x^3*y + 5*x^3*yi^5 + 7*x^3*yi^3 + 8*x^3*yi + 6*x*y^5 + 6*x*y^4*yi + 2*x*y^3*yi^2 + 7*x*y^3 + 2*x*y^2*yi^3 + 3*x*y^2*yi + 6*x*y*yi^4 + 3*x*y*yi^2 + 6*x*y + 6*x*yi^5 + 7*x*yi^3 + 6*x*yi + xi^7*y^5 + xi^7*y^4*yi + 2*xi^7*y^3 + xi^7*y^2*yi + xi^7*y*yi^4 + xi^7*y*yi^2 + 2*xi^7*y + xi^7*yi^5 + 2*xi^7*yi^3 + 2*xi^7*yi + 3*xi^5*y^5 + 3*xi^5*y^4*yi + xi^5*y^3*yi^2 + 5*xi^5*y^3 + xi^5*y^2*yi^3 + 4*xi^5*y^2*yi + 3*xi^5*y*yi^4 + 4*xi^5*y*yi^2 + 6*xi^5*y + 3*xi^5*yi^5 + 5*xi^5*yi^3 + 6*xi^5*yi + 5*xi^3*y^5 + 5*xi^3*y^4*yi + 2*xi^3*y^3*yi^2 + 7*xi^3*y^3 + 2*xi^3*y^2*yi^3 + 5*xi^3*y^2*yi + 5*xi^3*y*yi^4 + 5*xi^3*y*yi^2 + 8*xi^3*y + 5*xi^3*yi^5 + 7*xi^3*yi^3 + 8*xi^3*yi + 6*xi*y^5 + 6*xi*y^4*yi + 2*xi*y^3*yi^2 + 7*xi*y^3 + 2*xi*y^2*yi^3 + 3*xi*y^2*yi + 6*xi*y*yi^4 + 3*xi*y*yi^2 + 6*xi*y + 6*xi*yi^5 + 7*xi*yi^3 + 6*xi*yi) * hy

/-- (t + 1)^2 t = t(x^3) for t = x + 1/x, in characteristic 2. -/
theorem line_identity (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    (x + xi + 1)^2 * (x + xi) = x^3 + xi^3 := by
  linear_combination (x^2 + 2*x + xi^2 + 2*xi + 2) * h2 + (3*x + 3*xi + 4) * hx

/-- W on the lines x = 1, y = 1, y = x and y = 1/x. -/
theorem wPoly_axisx (h2 : (2 : R) = 0) (y yi : R) (hy : y * yi = 1) :
    wPoly 1 1 y yi = (y + yi + 1)^2 := by
  unfold wPoly
  linear_combination (2*y^2 + 2*yi^2) * h2 + (-2) * hy

theorem wPoly_axisy (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    wPoly x xi 1 1 = (x + xi + 1)^2 := by
  unfold wPoly
  linear_combination (2*x^2 + 2*xi^2) * h2 + (-2) * hx

theorem wPoly_diag (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    wPoly x xi x xi = ((x + xi + 1)^2)^2 := by
  unfold wPoly
  linear_combination (-x^3 - 4*x^2 - 7*x - xi^3 - 4*xi^2 - 7*xi - 8) * h2 +
    (-4*x^2 - 4*x*xi - 10*x - 4*xi^2 - 10*xi - 16) * hx

theorem wPoly_anti (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    wPoly x xi xi x = ((x + xi + 1)^2)^2 := by
  unfold wPoly
  linear_combination (-x^3 - 4*x^2 - 7*x - xi^3 - 4*xi^2 - 7*xi - 8) * h2 +
    (-4*x^2 - 4*x*xi - 10*x - 4*xi^2 - 10*xi - 16) * hx

/-- The square rule K8+M8+E4. -/
def k8m8e4Offsets : Finset (ℤ × ℤ) :=
  {(-3, -3), (-3, -2), (-3, 2), (-3, 3), (-2, -3), (-2, -1), (-2, 1), (-2, 3), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -3), (2, -1), (2, 1), (2, 3), (3, -3), (3, -2), (3, 2), (3, 3)}

/-- K8+M8+E4 is W times rule-90 factors. -/
theorem k8m8e4_poly {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1)
    (hy : y * yi = 1) :
    x^3*y^3 + x^3*y^2 + x^3*yi^3 + x^3*yi^2 + x^2*y^3 + x^2*y + x^2*yi^3 + x^2*yi + x*y^2 + x*yi^2 + xi^3*y^3 + xi^3*y^2 + xi^3*yi^3 + xi^3*yi^2 + xi^2*y^3 + xi^2*y + xi^2*yi^3 + xi^2*yi + xi*y^2 + xi*yi^2 = (x + xi) * (y + yi) * wPoly x xi y yi := by
  unfold wPoly
  linear_combination (-x^3*y - x^3*yi - x^3 - x*y^3 - 2*x*y - x*yi^3 - 2*x*yi - x - xi^3*y - xi^3*yi - xi^3 - xi*y^3 - 2*xi*y - xi*yi^3 - 2*xi*yi - xi - y^3 - y - yi^3 - yi) * h2 + (-x*y^3 - x*y^2*yi - x*y^2 - x*y*yi^2 - 2*x*y*yi - x*y - x*yi^3 - x*yi^2 - x*yi - xi*y^3 - xi*y^2*yi - xi*y^2 - xi*y*yi^2 - 2*xi*y*yi - xi*y - xi*yi^3 - xi*yi^2 - xi*yi - 2*y^3 - 2*y^2*yi - 2*y*yi^2 - 2*yi^3) * hx + (-x^3*y - x^3*yi - 2*x^3 - x^2*y - x^2*yi - 2*x*y - 2*x*yi - 2*x - xi^3*y - xi^3*yi - 2*xi^3 - xi^2*y - xi^2*yi - 2*xi*y - 2*xi*yi - 2*xi - 2*y - 2*yi) * hy

/-- The square rule C4+L8+M8. -/
def c4l8m8Offsets : Finset (ℤ × ℤ) :=
  {(-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-2, -3), (-2, 3), (-1, -3), (-1, 3), (0, -3), (0, 3), (1, -3), (1, 3), (2, -3), (2, 3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2)}

/-- C4+L8+M8 is W times rule-90 factors. -/
theorem c4l8m8_poly {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1)
    (hy : y * yi = 1) :
    x^3*y^2 + x^3*y + x^3*yi^2 + x^3*yi + x^3 + x^2*y^3 + x^2*yi^3 + x*y^3 + x*yi^3 + xi^3*y^2 + xi^3*y + xi^3*yi^2 + xi^3*yi + xi^3 + xi^2*y^3 + xi^2*yi^3 + xi*y^3 + xi*yi^3 + y^3 + yi^3 = (x + xi + y + yi) * wPoly x xi y yi := by
  unfold wPoly
  linear_combination (-x^2*y^2 - x^2*y - x^2*yi^2 - x^2*yi - x^2 - x*y^2 - x*y - x*yi^2 - x*yi - x - xi^2*y^2 - xi^2*y - xi^2*yi^2 - xi^2*yi - xi^2 - xi*y^2 - xi*y - xi*yi^2 - xi*yi - xi - y^2 - y - yi^2 - yi) * h2 + (-x*y^2 - x*y - x*yi^2 - x*yi - x - xi*y^2 - xi*y - xi*yi^2 - xi*yi - xi - 2*y^2 - 2*yi^2) * hx + (-x^2*y - x^2*yi - 2*x^2 - x*y - x*yi - xi^2*y - xi^2*yi - 2*xi^2 - xi*y - xi*yi - y - yi) * hy

/-- The square rule A4+B4+C4+L8+E4+self. -/
def a4b4c4l8e4selfOffsets : Finset (ℤ × ℤ) :=
  {(-3, -3), (-3, -1), (-3, 0), (-3, 1), (-3, 3), (-2, -2), (-2, 0), (-2, 2), (-1, -3), (-1, 3), (0, -3), (0, -2), (0, 0), (0, 2), (0, 3), (1, -3), (1, 3), (2, -2), (2, 0), (2, 2), (3, -3), (3, -1), (3, 0), (3, 1), (3, 3)}

/-- A4+B4+C4+L8+E4+self is W times rule-90 factors. -/
theorem a4b4c4l8e4self_poly {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1)
    (hy : y * yi = 1) :
    x^3*y^3 + x^3*y + x^3*yi^3 + x^3*yi + x^3 + x^2*y^2 + x^2*yi^2 + x^2 + x*y^3 + x*yi^3 + xi^3*y^3 + xi^3*y + xi^3*yi^3 + xi^3*yi + xi^3 + xi^2*y^2 + xi^2*yi^2 + xi^2 + xi*y^3 + xi*yi^3 + y^3 + y^2 + yi^3 + yi^2 + 1 = (x + xi + 1) * (y + yi + 1) * wPoly x xi y yi := by
  unfold wPoly
  linear_combination (-x^3*y^2 - x^3*y - x^3*yi^2 - x^3*yi - x^3 - x^2*y^3 - x^2*y^2 - 2*x^2*y - x^2*yi^3 - x^2*yi^2 - 2*x^2*yi - x^2 - x*y^3 - 2*x*y^2 - 3*x*y - x*yi^3 - 2*x*yi^2 - 3*x*yi - 2*x - xi^3*y^2 - xi^3*y - xi^3*yi^2 - xi^3*yi - xi^3 - xi^2*y^3 - xi^2*y^2 - 2*xi^2*y - xi^2*yi^3 - xi^2*yi^2 - 2*xi^2*yi - xi^2 - xi*y^3 - 2*xi*y^2 - 3*xi*y - xi*yi^3 - 2*xi*yi^2 - 3*xi*yi - 2*xi - y^3 - y^2 - 2*y - yi^3 - yi^2 - 2*yi) * h2 + (-x*y^3 - x*y^2*yi - 2*x*y^2 - x*y*yi^2 - 2*x*y*yi - 2*x*y - x*yi^3 - 2*x*yi^2 - 2*x*yi - x - xi*y^3 - xi*y^2*yi - 2*xi*y^2 - xi*y*yi^2 - 2*xi*y*yi - 2*xi*y - xi*yi^3 - 2*xi*yi^2 - 2*xi*yi - xi - 2*y^3 - 2*y^2*yi - 2*y^2 - 2*y*yi^2 - 2*yi^3 - 2*yi^2) * hx + (-x^3*y - x^3*yi - 2*x^3 - 2*x^2*y - 2*x^2*yi - 2*x^2 - 3*x*y - 3*x*yi - 2*x - xi^3*y - xi^3*yi - 2*xi^3 - 2*xi^2*y - 2*xi^2*yi - 2*xi^2 - 3*xi*y - 3*xi*yi - 2*xi - 3*y - 3*yi) * hy

/-- The square rule C4 + L8 + M8 + E4 (V, the boundary of the 7 x 7 square). -/
def vOffsets : Finset (ℤ × ℤ) :=
  {(-3, -3), (-3, -2), (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-2, -3), (-2, 3), (-1, -3), (-1, 3), (0, -3), (0, 3), (1, -3), (1, 3), (2, -3), (2, 3), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), (3, 2), (3, 3)}

/-- V's Laurent polynomial. -/
def vPoly {R : Type*} [CommRing R] (x xi y yi : R) : R :=
  x^3*y^3 + x^3*y^2 + x^3*y + x^3*yi^3 + x^3*yi^2 + x^3*yi + x^3 + x^2*y^3 + x^2*yi^3 + x*y^3 + x*yi^3 + xi^3*y^3 + xi^3*y^2 + xi^3*y + xi^3*yi^3 + xi^3*yi^2 + xi^3*yi + xi^3 + xi^2*y^3 + xi^2*yi^3 + xi*y^3 + xi*yi^3 + y^3 + yi^3

/-- The shells (+-7, +-7) and (+-5, +-5). -/
def svPoly {R : Type*} [CommRing R] (x xi y yi : R) : R :=
  x^7*y^7 + x^7*yi^7 + x^5*y^5 + x^5*yi^5 + xi^7*y^7 + xi^7*yi^7 + xi^5*y^5 + xi^5*yi^5

/-- **The identity for V.** V(x^2, y^2) t(x) t(y) = Sh(7,7) + Sh(5,5). -/
theorem v_identity {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1)
    (hy : y * yi = 1) :
    vPoly (x^2) (xi^2) (y^2) (yi^2) * ((x + xi) * (y + yi)) = svPoly x xi y yi := by
  unfold vPoly svPoly
  linear_combination (x^7*y^5 + x^7*y^3 + x^7*y + x^7*yi^5 + x^7*yi^3 + x^7*yi + x^5*y^7 + x^5*y^5 + x^5*y^3 + x^5*y + x^5*yi^7 + x^5*yi^5 + x^5*yi^3 + x^5*yi + x^3*y^7 + x^3*y^5 + x^3*yi^7 + x^3*yi^5 + x*y^7 + x*y^5 + x*yi^7 + x*yi^5 + xi^7*y^5 + xi^7*y^3 + xi^7*y + xi^7*yi^5 + xi^7*yi^3 + xi^7*yi + xi^5*y^7 + xi^5*y^5 + xi^5*y^3 + xi^5*y + xi^5*yi^7 + xi^5*yi^5 + xi^5*yi^3 + xi^5*yi + xi^3*y^7 + xi^3*y^5 + xi^3*yi^7 + xi^3*yi^5 + xi*y^7 + xi*y^5 + xi*yi^7 + xi*yi^5) * h2 + (x^5*y^7 + x^5*y^6*yi + x^5*y^5 + x^5*y^4*yi + x^5*y^3 + x^5*y^2*yi + x^5*y*yi^6 + x^5*y*yi^4 + x^5*y*yi^2 + x^5*y + x^5*yi^7 + x^5*yi^5 + x^5*yi^3 + x^5*yi + x^3*y^7 + x^3*y^6*yi + x^3*y*yi^6 + x^3*yi^7 + x*y^7 + x*y^6*yi + x*y*yi^6 + x*yi^7 + xi^5*y^7 + xi^5*y^6*yi + xi^5*y^5 + xi^5*y^4*yi + xi^5*y^3 + xi^5*y^2*yi + xi^5*y*yi^6 + xi^5*y*yi^4 + xi^5*y*yi^2 + xi^5*y + xi^5*yi^7 + xi^5*yi^5 + xi^5*yi^3 + xi^5*yi + xi^3*y^7 + xi^3*y^6*yi + xi^3*y*yi^6 + xi^3*yi^7 + xi*y^7 + xi*y^6*yi + xi*y*yi^6 + xi*yi^7) * hx + (x^7*y^5 + x^7*y^3 + x^7*y + x^7*yi^5 + x^7*yi^3 + x^7*yi + 2*x^5*y^5 + x^5*y^3 + x^5*y + 2*x^5*yi^5 + x^5*yi^3 + x^5*yi + 2*x^3*y^5 + 2*x^3*yi^5 + 2*x*y^5 + 2*x*yi^5 + xi^7*y^5 + xi^7*y^3 + xi^7*y + xi^7*yi^5 + xi^7*yi^3 + xi^7*yi + 2*xi^5*y^5 + xi^5*y^3 + xi^5*y + 2*xi^5*yi^5 + xi^5*yi^3 + xi^5*yi + 2*xi^3*y^5 + 2*xi^3*yi^5 + 2*xi*y^5 + 2*xi*yi^5) * hy

theorem vPoly_axisx {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (y yi : R) (hy : y * yi = 1) :
    vPoly 1 1 y yi = (y + yi) * (y + yi + 1)^2 := by
  unfold vPoly
  linear_combination (3*y^3 - y + 3*yi^3 - yi - 1) * h2 +  (-3*y - 3*yi - 4) * hy

theorem vPoly_axisy {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    vPoly x xi 1 1 = (x + xi) * (x + xi + 1)^2 := by
  unfold vPoly
  linear_combination (3*x^3 - x + 3*xi^3 - xi - 1) * h2 + (-3*x - 3*xi - 4) * hx 

/-- The triangle rule VS + T9 + T13 + self: its plane rule s (atlas rule 1101). -/
def triOffsets : Finset (ℤ × ℤ) :=
  {(-4, -4), (-4, -3), (-4, -2), (-4, -1), (-4, 0), (-3, -4), (-3, -3), (-3, 0), (-3, 1), (-2, -4), (-2, -2), (-2, 0), (-2, 2), (-1, -4), (-1, -1), (-1, 0), (-1, 3), (0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, -3), (1, 0), (1, 1), (1, 4), (2, -2), (2, 0), (2, 2), (2, 4), (3, -1), (3, 0), (3, 3), (3, 4), (4, 0), (4, 1), (4, 2), (4, 3), (4, 4)}

/-- s's Laurent polynomial. -/
def triPoly {R : Type*} [CommRing R] (x xi y yi : R) : R :=
  x^4*y^4 + x^4*y^3 + x^4*y^2 + x^4*y + x^4 + x^3*y^4 + x^3*y^3 + x^3*yi + x^3 + x^2*y^4 + x^2*y^2 + x^2*yi^2 + x^2 + x*y^4 + x*y + x*yi^3 + x + xi^4*yi^4 + xi^4*yi^3 + xi^4*yi^2 + xi^4*yi + xi^4 + xi^3*y + xi^3*yi^4 + xi^3*yi^3 + xi^3 + xi^2*y^2 + xi^2*yi^4 + xi^2*yi^2 + xi^2 + xi*y^3 + xi*yi^4 + xi*yi + xi + y^4 + y^3 + y^2 + y + yi^4 + yi^3 + yi^2 + yi + 1

/-- The two hexagonal orbits of (14, 12) and (12, 10). -/
def tbPoly {R : Type*} [CommRing R] (x xi y yi : R) : R :=
  x^14*y^12 + x^14*y^2 + x^12*y^14 + x^12*y^10 + x^12*y^2 + x^12*yi^2 + x^10*y^12 + x^10*yi^2 + x^2*y^14 + x^2*y^12 + x^2*yi^12 + x^2*yi^10 + xi^14*yi^12 + xi^14*yi^2 + xi^12*y^2 + xi^12*yi^14 + xi^12*yi^10 + xi^12*yi^2 + xi^10*y^2 + xi^10*yi^12 + xi^2*y^12 + xi^2*y^10 + xi^2*yi^14 + xi^2*yi^12

set_option maxRecDepth 200000 in
set_option maxHeartbeats 8000000 in
/-- **The identity for the triangle.** s(x^2, y^2) O(1,0) O(2,1) = Hex(14,12) + Hex(12,10). -/
theorem tri_identity {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi y yi : R) (hx : x * xi = 1)
    (hy : y * yi = 1) :
    triPoly (x^2) (xi^2) (y^2) (yi^2) * ((x + xi) * (y + yi) * (x*y + xi*yi) * (x^2*y + xi^2*yi) *
      (x*y^2 + xi*yi^2) * (x*yi + xi*y)) = tbPoly x xi y yi := by
  unfold triPoly tbPoly
  linear_combination (x^14*y^10 + x^14*y^8 + x^14*y^6 + x^14*y^4 + 2*x^12*y^12 + 3*x^12*y^10 + 4*x^12*y^8 + 4*x^12*y^6 + 4*x^12*y^4 + 3*x^12*y^2 + 2*x^12 + x^10*y^14 + 3*x^10*y^12 + 6*x^10*y^10 + 8*x^10*y^8 + 9*x^10*y^6 + 9*x^10*y^4 + 8*x^10*y^2 + x^10*yi^4 + 3*x^10*yi^2 + 6*x^10 + x^8*y^14 + 4*x^8*y^12 + 8*x^8*y^10 + 11*x^8*y^8 + 13*x^8*y^6 + 14*x^8*y^4 + 13*x^8*y^2 + x^8*yi^6 + 4*x^8*yi^4 + 8*x^8*yi^2 + 11*x^8 + x^6*y^14 + 4*x^6*y^12 + 9*x^6*y^10 + 13*x^6*y^8 + 16*x^6*y^6 + 17*x^6*y^4 + 17*x^6*y^2 + x^6*yi^8 + 4*x^6*yi^6 + 9*x^6*yi^4 + 13*x^6*yi^2 + 16*x^6 + x^4*y^14 + 4*x^4*y^12 + 9*x^4*y^10 + 14*x^4*y^8 + 17*x^4*y^6 + 19*x^4*y^4 + 20*x^4*y^2 + x^4*yi^10 + 4*x^4*yi^8 + 9*x^4*yi^6 + 14*x^4*yi^4 + 17*x^4*yi^2 + 19*x^4 + 3*x^2*y^12 + 8*x^2*y^10 + 13*x^2*y^8 + 17*x^2*y^6 + 20*x^2*y^4 + 20*x^2*y^2 + 3*x^2*yi^10 + 8*x^2*yi^8 + 13*x^2*yi^6 + 17*x^2*yi^4 + 20*x^2*yi^2 + 20*x^2 + xi^14*yi^10 + xi^14*yi^8 + xi^14*yi^6 + xi^14*yi^4 + 2*xi^12*yi^12 + 3*xi^12*yi^10 + 4*xi^12*yi^8 + 4*xi^12*yi^6 + 4*xi^12*yi^4 + 3*xi^12*yi^2 + 2*xi^12 + xi^10*y^4 + 3*xi^10*y^2 + xi^10*yi^14 + 3*xi^10*yi^12 + 6*xi^10*yi^10 + 8*xi^10*yi^8 + 9*xi^10*yi^6 + 9*xi^10*yi^4 + 8*xi^10*yi^2 + 6*xi^10 + xi^8*y^6 + 4*xi^8*y^4 + 8*xi^8*y^2 + xi^8*yi^14 + 4*xi^8*yi^12 + 8*xi^8*yi^10 + 11*xi^8*yi^8 + 13*xi^8*yi^6 + 14*xi^8*yi^4 + 13*xi^8*yi^2 + 11*xi^8 + xi^6*y^8 + 4*xi^6*y^6 + 9*xi^6*y^4 + 13*xi^6*y^2 + xi^6*yi^14 + 4*xi^6*yi^12 + 9*xi^6*yi^10 + 13*xi^6*yi^8 + 16*xi^6*yi^6 + 17*xi^6*yi^4 + 17*xi^6*yi^2 + 16*xi^6 + xi^4*y^10 + 4*xi^4*y^8 + 9*xi^4*y^6 + 14*xi^4*y^4 + 17*xi^4*y^2 + xi^4*yi^14 + 4*xi^4*yi^12 + 9*xi^4*yi^10 + 14*xi^4*yi^8 + 17*xi^4*yi^6 + 19*xi^4*yi^4 + 20*xi^4*yi^2 + 19*xi^4 + 3*xi^2*y^10 + 8*xi^2*y^8 + 13*xi^2*y^6 + 17*xi^2*y^4 + 20*xi^2*y^2 + 3*xi^2*yi^12 + 8*xi^2*yi^10 + 13*xi^2*yi^8 + 17*xi^2*yi^6 + 20*xi^2*yi^4 + 20*xi^2*yi^2 + 20*xi^2 + 2*y^12 + 6*y^10 + 11*y^8 + 16*y^6 + 19*y^4 + 20*y^2 + 2*yi^12 + 6*yi^10 + 11*yi^8 + 16*yi^6 + 19*yi^4 + 20*yi^2 + 20) * h2 + (x^12*y^14 + 2*x^12*y^13*yi + 2*x^12*y^12*yi^2 + x^12*y^12 + 2*x^12*y^11*yi^3 + 2*x^12*y^11*yi + x^12*y^10*yi^4 + 2*x^12*y^10*yi^2 + x^12*y^10 + 2*x^12*y^9*yi^3 + 2*x^12*y^9*yi + x^12*y^8*yi^4 + 2*x^12*y^8*yi^2 + x^12*y^8 + 2*x^12*y^7*yi^3 + 2*x^12*y^7*yi + x^12*y^6*yi^4 + 2*x^12*y^6*yi^2 + x^12*y^6 + 2*x^12*y^5*yi^3 + 2*x^12*y^5*yi + x^12*y^4*yi^4 + 2*x^12*y^4*yi^2 + 2*x^12*y^3*yi^3 + x^12*y^2*yi^4 + x^11*xi*y^14 + 2*x^11*xi*y^13*yi + 4*x^11*xi*y^12*yi^2 + x^11*xi*y^12 + 4*x^11*xi*y^11*yi^3 + 2*x^11*xi*y^11*yi + 2*x^11*xi*y^10*yi^4 + 4*x^11*xi*y^10*yi^2 + x^11*xi*y^10 + x^11*xi*y^9*yi^5 + 4*x^11*xi*y^9*yi^3 + 2*x^11*xi*y^9*yi + 2*x^11*xi*y^8*yi^4 + 4*x^11*xi*y^8*yi^2 + x^11*xi*y^8 + x^11*xi*y^7*yi^5 + 4*x^11*xi*y^7*yi^3 + 2*x^11*xi*y^7*yi + 2*x^11*xi*y^6*yi^4 + 4*x^11*xi*y^6*yi^2 + x^11*xi*y^6 + x^11*xi*y^5*yi^5 + 4*x^11*xi*y^5*yi^3 + 2*x^11*xi*y^5*yi + 2*x^11*xi*y^4*yi^4 + 4*x^11*xi*y^4*yi^2 + x^11*xi*y^3*yi^5 + 4*x^11*xi*y^3*yi^3 + 2*x^11*xi*y^2*yi^4 + x^11*xi*y*yi^5 + 2*x^10*xi^2*y^13*yi + 4*x^10*xi^2*y^12*yi^2 + 4*x^10*xi^2*y^11*yi^3 + 2*x^10*xi^2*y^11*yi + 4*x^10*xi^2*y^10*yi^4 + 4*x^10*xi^2*y^10*yi^2 + 2*x^10*xi^2*y^9*yi^5 + 4*x^10*xi^2*y^9*yi^3 + 2*x^10*xi^2*y^9*yi + 4*x^10*xi^2*y^8*yi^4 + 4*x^10*xi^2*y^8*yi^2 + 2*x^10*xi^2*y^7*yi^5 + 4*x^10*xi^2*y^7*yi^3 + 2*x^10*xi^2*y^7*yi + 4*x^10*xi^2*y^6*yi^4 + 4*x^10*xi^2*y^6*yi^2 + 2*x^10*xi^2*y^5*yi^5 + 4*x^10*xi^2*y^5*yi^3 + 2*x^10*xi^2*y^5*yi + 4*x^10*xi^2*y^4*yi^4 + 4*x^10*xi^2*y^4*yi^2 + 2*x^10*xi^2*y^3*yi^5 + 4*x^10*xi^2*y^3*yi^3 + 4*x^10*xi^2*y^2*yi^4 + 2*x^10*xi^2*y*yi^5 + 2*x^10*y^14 + 4*x^10*y^13*yi + 6*x^10*y^12*yi^2 + 2*x^10*y^12 + 6*x^10*y^11*yi^3 + 4*x^10*y^11*yi + 3*x^10*y^10*yi^4 + 6*x^10*y^10*yi^2 + x^10*y^10 + x^10*y^9*yi^5 + 6*x^10*y^9*yi^3 + 2*x^10*y^9*yi + 3*x^10*y^8*yi^4 + 4*x^10*y^8*yi^2 + x^10*y^8 + x^10*y^7*yi^5 + 4*x^10*y^7*yi^3 + 2*x^10*y^7*yi + 2*x^10*y^6*yi^4 + 5*x^10*y^6*yi^2 + 2*x^10*y^6 + x^10*y^5*yi^5 + 6*x^10*y^5*yi^3 + 4*x^10*y^5*yi + 4*x^10*y^4*yi^4 + 6*x^10*y^4*yi^2 + 3*x^10*y^3*yi^5 + 6*x^10*y^3*yi^3 + x^10*y^2*yi^6 + 3*x^10*y^2*yi^4 + x^10*y*yi^5 + x^9*xi^3*y^13*yi + 2*x^9*xi^3*y^12*yi^2 + 4*x^9*xi^3*y^11*yi^3 + x^9*xi^3*y^11*yi + 4*x^9*xi^3*y^10*yi^4 + 2*x^9*xi^3*y^10*yi^2 + 2*x^9*xi^3*y^9*yi^5 + 4*x^9*xi^3*y^9*yi^3 + x^9*xi^3*y^9*yi + x^9*xi^3*y^8*yi^6 + 4*x^9*xi^3*y^8*yi^4 + 2*x^9*xi^3*y^8*yi^2 + 2*x^9*xi^3*y^7*yi^5 + 4*x^9*xi^3*y^7*yi^3 + x^9*xi^3*y^7*yi + x^9*xi^3*y^6*yi^6 + 4*x^9*xi^3*y^6*yi^4 + 2*x^9*xi^3*y^6*yi^2 + 2*x^9*xi^3*y^5*yi^5 + 4*x^9*xi^3*y^5*yi^3 + x^9*xi^3*y^5*yi + x^9*xi^3*y^4*yi^6 + 4*x^9*xi^3*y^4*yi^4 + 2*x^9*xi^3*y^4*yi^2 + 2*x^9*xi^3*y^3*yi^5 + 4*x^9*xi^3*y^3*yi^3 + x^9*xi^3*y^2*yi^6 + 4*x^9*xi^3*y^2*yi^4 + 2*x^9*xi^3*y*yi^5 + x^9*xi^3*yi^6 + x^9*xi*y^14 + 4*x^9*xi*y^13*yi + 8*x^9*xi*y^12*yi^2 + x^9*xi*y^12 + 8*x^9*xi*y^11*yi^3 + 4*x^9*xi*y^11*yi + 6*x^9*xi*y^10*yi^4 + 8*x^9*xi*y^10*yi^2 + 3*x^9*xi*y^9*yi^5 + 8*x^9*xi*y^9*yi^3 + 2*x^9*xi*y^9*yi + 6*x^9*xi*y^8*yi^4 + 4*x^9*xi*y^8*yi^2 + 3*x^9*xi*y^7*yi^5 + 4*x^9*xi*y^7*yi^3 + 2*x^9*xi*y^7*yi + 4*x^9*xi*y^6*yi^4 + 5*x^9*xi*y^6*yi^2 + x^9*xi*y^6 + 2*x^9*xi*y^5*yi^5 + 6*x^9*xi*y^5*yi^3 + 4*x^9*xi*y^5*yi + 8*x^9*xi*y^4*yi^4 + 8*x^9*xi*y^4*yi^2 + 6*x^9*xi*y^3*yi^5 + 8*x^9*xi*y^3*yi^3 + 2*x^9*xi*y^2*yi^6 + 6*x^9*xi*y^2*yi^4 + x^9*xi*y*yi^7 + 3*x^9*xi*y*yi^5 + x^8*xi^4*y^12*yi^2 + 2*x^8*xi^4*y^11*yi^3 + 2*x^8*xi^4*y^10*yi^4 + x^8*xi^4*y^10*yi^2 + 2*x^8*xi^4*y^9*yi^5 + 2*x^8*xi^4*y^9*yi^3 + x^8*xi^4*y^8*yi^6 + 2*x^8*xi^4*y^8*yi^4 + x^8*xi^4*y^8*yi^2 + 2*x^8*xi^4*y^7*yi^5 + 2*x^8*xi^4*y^7*yi^3 + x^8*xi^4*y^6*yi^6 + 2*x^8*xi^4*y^6*yi^4 + x^8*xi^4*y^6*yi^2 + 2*x^8*xi^4*y^5*yi^5 + 2*x^8*xi^4*y^5*yi^3 + x^8*xi^4*y^4*yi^6 + 2*x^8*xi^4*y^4*yi^4 + x^8*xi^4*y^4*yi^2 + 2*x^8*xi^4*y^3*yi^5 + 2*x^8*xi^4*y^3*yi^3 + x^8*xi^4*y^2*yi^6 + 2*x^8*xi^4*y^2*yi^4 + 2*x^8*xi^4*y*yi^5 + x^8*xi^4*yi^6 + 3*x^8*xi^2*y^13*yi + 6*x^8*xi^2*y^12*yi^2 + 8*x^8*xi^2*y^11*yi^3 + 3*x^8*xi^2*y^11*yi + 8*x^8*xi^2*y^10*yi^4 + 6*x^8*xi^2*y^10*yi^2 + 4*x^8*xi^2*y^9*yi^5 + 8*x^8*xi^2*y^9*yi^3 + x^8*xi^2*y^9*yi + x^8*xi^2*y^8*yi^6 + 8*x^8*xi^2*y^8*yi^4 + 2*x^8*xi^2*y^8*yi^2 + 4*x^8*xi^2*y^7*yi^5 + 4*x^8*xi^2*y^7*yi^3 + x^8*xi^2*y^7*yi + x^8*xi^2*y^6*yi^6 + 4*x^8*xi^2*y^6*yi^4 + 2*x^8*xi^2*y^6*yi^2 + 2*x^8*xi^2*y^5*yi^5 + 6*x^8*xi^2*y^5*yi^3 + 3*x^8*xi^2*y^5*yi + x^8*xi^2*y^4*yi^6 + 8*x^8*xi^2*y^4*yi^4 + 6*x^8*xi^2*y^4*yi^2 + 6*x^8*xi^2*y^3*yi^5 + 8*x^8*xi^2*y^3*yi^3 + 5*x^8*xi^2*y^2*yi^6 + 8*x^8*xi^2*y^2*yi^4 + 2*x^8*xi^2*y*yi^7 + 4*x^8*xi^2*y*yi^5 + x^8*xi^2*yi^6 + 2*x^8*y^14 + 6*x^8*y^13*yi + 10*x^8*y^12*yi^2 + x^8*y^12 + 10*x^8*y^11*yi^3 + 4*x^8*y^11*yi + 7*x^8*y^10*yi^4 + 8*x^8*y^10*yi^2 + x^8*y^10 + 3*x^8*y^9*yi^5 + 8*x^8*y^9*yi^3 + 4*x^8*y^9*yi + 6*x^8*y^8*yi^4 + 6*x^8*y^8*yi^2 + 3*x^8*y^7*yi^5 + 6*x^8*y^7*yi^3 + 2*x^8*y^7*yi + 6*x^8*y^6*yi^4 + 5*x^8*y^6*yi^2 + 2*x^8*y^6 + 4*x^8*y^5*yi^5 + 6*x^8*y^5*yi^3 + 6*x^8*y^5*yi + 2*x^8*y^4*yi^6 + 8*x^8*y^4*yi^4 + 10*x^8*y^4*yi^2 + 2*x^8*y^3*yi^7 + 6*x^8*y^3*yi^5 + 10*x^8*y^3*yi^3 + x^8*y^2*yi^8 + 2*x^8*y^2*yi^6 + 7*x^8*y^2*yi^4 + x^8*y*yi^7 + 3*x^8*y*yi^5 + x^7*xi^5*y^10*yi^4 + x^7*xi^5*y^9*yi^5 + x^7*xi^5*y^8*yi^4 + x^7*xi^5*y^7*yi^5 + x^7*xi^5*y^6*yi^4 + x^7*xi^5*y^5*yi^5 + x^7*xi^5*y^4*yi^4 + x^7*xi^5*y^3*yi^5 + x^7*xi^5*y^2*yi^4 + x^7*xi^5*y*yi^5 + x^7*xi^3*y^13*yi + 3*x^7*xi^3*y^12*yi^2 + 6*x^7*xi^3*y^11*yi^3 + x^7*xi^3*y^11*yi + 6*x^7*xi^3*y^10*yi^4 + 3*x^7*xi^3*y^10*yi^2 + 4*x^7*xi^3*y^9*yi^5 + 6*x^7*xi^3*y^9*yi^3 + 2*x^7*xi^3*y^8*yi^6 + 6*x^7*xi^3*y^8*yi^4 + x^7*xi^3*y^8*yi^2 + 4*x^7*xi^3*y^7*yi^5 + 2*x^7*xi^3*y^7*yi^3 + 2*x^7*xi^3*y^6*yi^6 + 2*x^7*xi^3*y^6*yi^4 + x^7*xi^3*y^6*yi^2 + 2*x^7*xi^3*y^5*yi^5 + 3*x^7*xi^3*y^5*yi^3 + x^7*xi^3*y^5*yi + x^7*xi^3*y^4*yi^6 + 4*x^7*xi^3*y^4*yi^4 + 3*x^7*xi^3*y^4*yi^2 + 6*x^7*xi^3*y^3*yi^5 + 6*x^7*xi^3*y^3*yi^3 + 5*x^7*xi^3*y^2*yi^6 + 6*x^7*xi^3*y^2*yi^4 + 2*x^7*xi^3*y*yi^7 + 4*x^7*xi^3*y*yi^5 + x^7*xi^3*yi^8 + 2*x^7*xi^3*yi^6 + x^7*xi*y^14 + 5*x^7*xi*y^13*yi + 10*x^7*xi*y^12*yi^2 + 12*x^7*xi*y^11*yi^3 + 3*x^7*xi*y^11*yi + 10*x^7*xi*y^10*yi^4 + 6*x^7*xi*y^10*yi^2 + x^7*xi*y^10 + 5*x^7*xi*y^9*yi^5 + 8*x^7*xi*y^9*yi^3 + 3*x^7*xi*y^9*yi + x^7*xi*y^8*yi^6 + 8*x^7*xi*y^8*yi^4 + 6*x^7*xi*y^8*yi^2 + 4*x^7*xi*y^7*yi^5 + 8*x^7*xi*y^7*yi^3 + x^7*xi*y^7*yi + x^7*xi*y^6*yi^6 + 7*x^7*xi*y^6*yi^4 + 2*x^7*xi*y^6*yi^2 + x^7*xi*y^6 + 5*x^7*xi*y^5*yi^5 + 6*x^7*xi*y^5*yi^3 + 5*x^7*xi*y^5*yi + 5*x^7*xi*y^4*yi^6 + 8*x^7*xi*y^4*yi^4 + 10*x^7*xi*y^4*yi^2 + 4*x^7*xi*y^3*yi^7 + 6*x^7*xi*y^3*yi^5 + 12*x^7*xi*y^3*yi^3 + 2*x^7*xi*y^2*yi^8 + 5*x^7*xi*y^2*yi^6 + 10*x^7*xi*y^2*yi^4 + x^7*xi*y*yi^9 + 2*x^7*xi*y*yi^7 + 5*x^7*xi*y*yi^5 + x^7*xi*yi^6 + x^6*xi^4*y^12*yi^2 + 2*x^6*xi^4*y^11*yi^3 + 3*x^6*xi^4*y^10*yi^4 + x^6*xi^4*y^10*yi^2 + 3*x^6*xi^4*y^9*yi^5 + 2*x^6*xi^4*y^9*yi^3 + x^6*xi^4*y^8*yi^6 + 3*x^6*xi^4*y^8*yi^4 + 3*x^6*xi^4*y^7*yi^5 + x^6*xi^4*y^6*yi^6 + x^6*xi^4*y^6*yi^4 + x^6*xi^4*y^5*yi^5 + 2*x^6*xi^4*y^4*yi^4 + x^6*xi^4*y^4*yi^2 + 3*x^6*xi^4*y^3*yi^5 + 2*x^6*xi^4*y^3*yi^3 + 2*x^6*xi^4*y^2*yi^6 + 3*x^6*xi^4*y^2*yi^4 + 2*x^6*xi^4*y*yi^7 + 3*x^6*xi^4*y*yi^5 + x^6*xi^4*yi^8 + x^6*xi^4*yi^6 + 3*x^6*xi^2*y^13*yi + 7*x^6*xi^2*y^12*yi^2 + 10*x^6*xi^2*y^11*yi^3 + x^6*xi^2*y^11*yi + 10*x^6*xi^2*y^10*yi^4 + 3*x^6*xi^2*y^10*yi^2 + 6*x^6*xi^2*y^9*yi^5 + 6*x^6*xi^2*y^9*yi^3 + 2*x^6*xi^2*y^9*yi + 2*x^6*xi^2*y^8*yi^6 + 6*x^6*xi^2*y^8*yi^4 + 5*x^6*xi^2*y^8*yi^2 + 4*x^6*xi^2*y^7*yi^5 + 6*x^6*xi^2*y^7*yi^3 + 2*x^6*xi^2*y^6*yi^6 + 6*x^6*xi^2*y^6*yi^4 + x^6*xi^2*y^6*yi^2 + 6*x^6*xi^2*y^5*yi^5 + 3*x^6*xi^2*y^5*yi^3 + 3*x^6*xi^2*y^5*yi + 5*x^6*xi^2*y^4*yi^6 + 4*x^6*xi^2*y^4*yi^4 + 7*x^6*xi^2*y^4*yi^2 + 4*x^6*xi^2*y^3*yi^7 + 6*x^6*xi^2*y^3*yi^5 + 10*x^6*xi^2*y^3*yi^3 + 4*x^6*xi^2*y^2*yi^8 + 5*x^6*xi^2*y^2*yi^6 + 10*x^6*xi^2*y^2*yi^4 + 2*x^6*xi^2*y*yi^9 + 2*x^6*xi^2*y*yi^7 + 6*x^6*xi^2*y*yi^5 + x^6*xi^2*yi^8 + 2*x^6*xi^2*yi^6 + 2*x^6*y^14 + 7*x^6*y^13*yi + 12*x^6*y^12*yi^2 + 14*x^6*y^11*yi^3 + 3*x^6*y^11*yi + 11*x^6*y^10*yi^4 + 6*x^6*y^10*yi^2 + x^6*y^10 + 5*x^6*y^9*yi^5 + 8*x^6*y^9*yi^3 + 3*x^6*y^9*yi + x^6*y^8*yi^6 + 8*x^6*y^8*yi^4 + 6*x^6*y^8*yi^2 + x^6*y^8 + 4*x^6*y^7*yi^5 + 8*x^6*y^7*yi^3 + 3*x^6*y^7*yi + 2*x^6*y^6*yi^6 + 7*x^6*y^6*yi^4 + 4*x^6*y^6*yi^2 + 2*x^6*y^6 + 2*x^6*y^5*yi^7 + 5*x^6*y^5*yi^5 + 8*x^6*y^5*yi^3 + 7*x^6*y^5*yi + 2*x^6*y^4*yi^8 + 5*x^6*y^4*yi^6 + 9*x^6*y^4*yi^4 + 12*x^6*y^4*yi^2 + 2*x^6*y^3*yi^9 + 4*x^6*y^3*yi^7 + 6*x^6*y^3*yi^5 + 14*x^6*y^3*yi^3 + x^6*y^2*yi^10 + 2*x^6*y^2*yi^8 + 5*x^6*y^2*yi^6 + 11*x^6*y^2*yi^4 + x^6*y*yi^9 + 2*x^6*y*yi^7 + 5*x^6*y*yi^5 + x^6*yi^6 + x^5*xi^7*y^5*yi^9 + x^5*xi^7*y^5*yi^7 + x^5*xi^7*y^5*yi^5 + x^5*xi^7*y^5*yi^3 + x^5*xi^7*y^5*yi + x^5*xi^7*y^4*yi^10 + x^5*xi^7*y^4*yi^8 + x^5*xi^7*y^4*yi^6 + x^5*xi^7*y^4*yi^4 + x^5*xi^7*y^4*yi^2 + x^5*xi^5*y^10*yi^4 + x^5*xi^5*y^9*yi^5 + x^5*xi^5*y^8*yi^4 + x^5*xi^5*y^7*yi^5 + x^5*xi^5*y^7*yi + x^5*xi^5*y^6*yi^2 + x^5*xi^5*y^5*yi^9 + x^5*xi^5*y^5*yi^7 + x^5*xi^5*y^5*yi + x^5*xi^5*y^4*yi^10 + x^5*xi^5*y^4*yi^8 + x^5*xi^5*y^4*yi^2 + x^5*xi^5*y^2*yi^6 + x^5*xi^5*y^2*yi^4 + x^5*xi^5*y*yi^7 + x^5*xi^5*y*yi^5 + x^5*xi^3*y^13*yi + 3*x^5*xi^3*y^12*yi^2 + 6*x^5*xi^3*y^11*yi^3 + 7*x^5*xi^3*y^10*yi^4 + x^5*xi^3*y^10*yi^2 + 5*x^5*xi^3*y^9*yi^5 + 2*x^5*xi^3*y^9*yi^3 + 2*x^5*xi^3*y^9*yi + 2*x^5*xi^3*y^8*yi^6 + 3*x^5*xi^3*y^8*yi^4 + 3*x^5*xi^3*y^8*yi^2 + 3*x^5*xi^3*y^7*yi^5 + 4*x^5*xi^3*y^7*yi^3 + x^5*xi^3*y^6*yi^6 + 5*x^5*xi^3*y^6*yi^4 + x^5*xi^3*y^5*yi^9 + 5*x^5*xi^3*y^5*yi^5 + 2*x^5*xi^3*y^5*yi + x^5*xi^3*y^4*yi^10 + 4*x^5*xi^3*y^4*yi^6 + 2*x^5*xi^3*y^4*yi^4 + 4*x^5*xi^3*y^4*yi^2 + 4*x^5*xi^3*y^3*yi^7 + 3*x^5*xi^3*y^3*yi^5 + 6*x^5*xi^3*y^3*yi^3 + 4*x^5*xi^3*y^2*yi^8 + 2*x^5*xi^3*y^2*yi^6 + 7*x^5*xi^3*y^2*yi^4 + 2*x^5*xi^3*y*yi^9 + 2*x^5*xi^3*y*yi^7 + 5*x^5*xi^3*y*yi^5 + x^5*xi^3*yi^10 + x^5*xi^3*yi^8 + 2*x^5*xi^3*yi^6 + x^5*xi*y^14 + 5*x^5*xi*y^13*yi + 11*x^5*xi*y^12*yi^2 + 14*x^5*xi*y^11*yi^3 + 2*x^5*xi*y^11*yi + 12*x^5*xi*y^10*yi^4 + 4*x^5*xi*y^10*yi^2 + 7*x^5*xi*y^9*yi^5 + 6*x^5*xi*y^9*yi^3 + 2*x^5*xi*y^9*yi + 2*x^5*xi*y^8*yi^6 + 6*x^5*xi*y^8*yi^4 + 5*x^5*xi*y^8*yi^2 + x^5*xi*y^8 + 4*x^5*xi*y^7*yi^5 + 6*x^5*xi*y^7*yi^3 + 2*x^5*xi*y^7*yi + 3*x^5*xi*y^6*yi^6 + 6*x^5*xi*y^6*yi^4 + 5*x^5*xi*y^6*yi^2 + x^5*xi*y^6 + x^5*xi*y^5*yi^9 + 2*x^5*xi*y^5*yi^7 + 6*x^5*xi*y^5*yi^5 + 8*x^5*xi*y^5*yi^3 + 6*x^5*xi*y^5*yi + x^5*xi*y^4*yi^10 + 4*x^5*xi*y^4*yi^8 + 5*x^5*xi*y^4*yi^6 + 7*x^5*xi*y^4*yi^4 + 12*x^5*xi*y^4*yi^2 + 4*x^5*xi*y^3*yi^9 + 4*x^5*xi*y^3*yi^7 + 7*x^5*xi*y^3*yi^5 + 14*x^5*xi*y^3*yi^3 + 2*x^5*xi*y^2*yi^10 + 4*x^5*xi*y^2*yi^8 + 5*x^5*xi*y^2*yi^6 + 12*x^5*xi*y^2*yi^4 + x^5*xi*y*yi^11 + 2*x^5*xi*y*yi^9 + 2*x^5*xi*y*yi^7 + 7*x^5*xi*y*yi^5 + x^5*xi*yi^8 + 2*x^5*xi*yi^6 + x^4*xi^8*y^6*yi^8 + x^4*xi^8*y^6*yi^6 + x^4*xi^8*y^6*yi^4 + x^4*xi^8*y^6*yi^2 + x^4*xi^8*y^6 + 2*x^4*xi^8*y^5*yi^9 + 2*x^4*xi^8*y^5*yi^7 + 2*x^4*xi^8*y^5*yi^5 + 2*x^4*xi^8*y^5*yi^3 + 2*x^4*xi^8*y^5*yi + 2*x^4*xi^8*y^4*yi^10 + 2*x^4*xi^8*y^4*yi^8 + 2*x^4*xi^8*y^4*yi^6 + 2*x^4*xi^8*y^4*yi^4 + 2*x^4*xi^8*y^4*yi^2 + 2*x^4*xi^8*y^3*yi^11 + 2*x^4*xi^8*y^3*yi^9 + 2*x^4*xi^8*y^3*yi^7 + 2*x^4*xi^8*y^3*yi^5 + 2*x^4*xi^8*y^3*yi^3 + x^4*xi^8*y^2*yi^12 + x^4*xi^8*y^2*yi^10 + x^4*xi^8*y^2*yi^8 + x^4*xi^8*y^2*yi^6 + x^4*xi^8*y^2*yi^4 + x^4*xi^6*y^8 + 2*x^4*xi^6*y^7*yi + x^4*xi^6*y^6*yi^8 + x^4*xi^6*y^6*yi^6 + 2*x^4*xi^6*y^6*yi^2 + x^4*xi^6*y^6 + 3*x^4*xi^6*y^5*yi^9 + 3*x^4*xi^6*y^5*yi^7 + x^4*xi^6*y^5*yi^5 + 3*x^4*xi^6*y^5*yi^3 + 3*x^4*xi^6*y^5*yi + 3*x^4*xi^6*y^4*yi^10 + 3*x^4*xi^6*y^4*yi^8 + x^4*xi^6*y^4*yi^6 + 2*x^4*xi^6*y^4*yi^4 + 3*x^4*xi^6*y^4*yi^2 + 2*x^4*xi^6*y^3*yi^11 + 2*x^4*xi^6*y^3*yi^9 + 2*x^4*xi^6*y^3*yi^3 + x^4*xi^6*y^2*yi^12 + x^4*xi^6*y^2*yi^10 + x^4*xi^6*y^2*yi^4 + x^4*xi^4*y^12*yi^2 + 2*x^4*xi^4*y^11*yi^3 + 3*x^4*xi^4*y^10*yi^4 + x^4*xi^4*y^10 + 3*x^4*xi^4*y^9*yi^5 + 2*x^4*xi^4*y^9*yi + x^4*xi^4*y^8*yi^6 + x^4*xi^4*y^8*yi^4 + 3*x^4*xi^4*y^8*yi^2 + x^4*xi^4*y^7*yi^5 + 4*x^4*xi^4*y^7*yi^3 + x^4*xi^4*y^7*yi + x^4*xi^4*y^6*yi^8 + 4*x^4*xi^4*y^6*yi^4 + x^4*xi^4*y^6*yi^2 + x^4*xi^4*y^6 + 3*x^4*xi^4*y^5*yi^9 + x^4*xi^4*y^5*yi^7 + 4*x^4*xi^4*y^5*yi^5 + 3*x^4*xi^4*y^5*yi + 3*x^4*xi^4*y^4*yi^10 + x^4*xi^4*y^4*yi^8 + 4*x^4*xi^4*y^4*yi^6 + 4*x^4*xi^4*y^4*yi^2 + 2*x^4*xi^4*y^3*yi^11 + 4*x^4*xi^4*y^3*yi^7 + 4*x^4*xi^4*y^3*yi^3 + x^4*xi^4*y^2*yi^12 + 3*x^4*xi^4*y^2*yi^8 + x^4*xi^4*y^2*yi^6 + 4*x^4*xi^4*y^2*yi^4 + 2*x^4*xi^4*y*yi^9 + x^4*xi^4*y*yi^7 + 3*x^4*xi^4*y*yi^5 + x^4*xi^4*yi^10 + x^4*xi^4*yi^6 + 3*x^4*xi^2*y^13*yi + 7*x^4*xi^2*y^12*yi^2 + x^4*xi^2*y^12 + 10*x^4*xi^2*y^11*yi^3 + 2*x^4*xi^2*y^11*yi + 11*x^4*xi^2*y^10*yi^4 + 3*x^4*xi^2*y^10*yi^2 + 7*x^4*xi^2*y^9*yi^5 + 4*x^4*xi^2*y^9*yi^3 + 2*x^4*xi^2*y^9*yi + 2*x^4*xi^2*y^8*yi^6 + 4*x^4*xi^2*y^8*yi^4 + 3*x^4*xi^2*y^8*yi^2 + 3*x^4*xi^2*y^7*yi^5 + 4*x^4*xi^2*y^7*yi^3 + 2*x^4*xi^2*y^7*yi + x^4*xi^2*y^6*yi^8 + x^4*xi^2*y^6*yi^6 + 5*x^4*xi^2*y^6*yi^4 + 5*x^4*xi^2*y^6*yi^2 + x^4*xi^2*y^6 + 3*x^4*xi^2*y^5*yi^9 + 2*x^4*xi^2*y^5*yi^7 + 5*x^4*xi^2*y^5*yi^5 + 6*x^4*xi^2*y^5*yi^3 + 6*x^4*xi^2*y^5*yi + 3*x^4*xi^2*y^4*yi^10 + 4*x^4*xi^2*y^4*yi^8 + 4*x^4*xi^2*y^4*yi^6 + 8*x^4*xi^2*y^4*yi^4 + 10*x^4*xi^2*y^4*yi^2 + 2*x^4*xi^2*y^3*yi^11 + 4*x^4*xi^2*y^3*yi^9 + 4*x^4*xi^2*y^3*yi^7 + 7*x^4*xi^2*y^3*yi^5 + 12*x^4*xi^2*y^3*yi^3 + x^4*xi^2*y^2*yi^12 + 4*x^4*xi^2*y^2*yi^10 + 4*x^4*xi^2*y^2*yi^8 + 3*x^4*xi^2*y^2*yi^6 + 12*x^4*xi^2*y^2*yi^4 + 2*x^4*xi^2*y*yi^11 + 2*x^4*xi^2*y*yi^9 + 2*x^4*xi^2*y*yi^7 + 7*x^4*xi^2*y*yi^5 + x^4*xi^2*yi^10 + x^4*xi^2*yi^8 + 2*x^4*xi^2*yi^6 + 2*x^4*y^14 + 7*x^4*y^13*yi + 13*x^4*y^12*yi^2 + x^4*y^12 + 16*x^4*y^11*yi^3 + 4*x^4*y^11*yi + 13*x^4*y^10*yi^4 + 6*x^4*y^10*yi^2 + x^4*y^10 + 7*x^4*y^9*yi^5 + 8*x^4*y^9*yi^3 + 4*x^4*y^9*yi + 2*x^4*y^8*yi^6 + 7*x^4*y^8*yi^4 + 7*x^4*y^8*yi^2 + 2*x^4*y^8 + 4*x^4*y^7*yi^5 + 8*x^4*y^7*yi^3 + 4*x^4*y^7*yi + x^4*y^6*yi^8 + 4*x^4*y^6*yi^6 + 8*x^4*y^6*yi^4 + 8*x^4*y^6*yi^2 + 2*x^4*y^6 + 3*x^4*y^5*yi^9 + 4*x^4*y^5*yi^7 + 8*x^4*y^5*yi^5 + 12*x^4*y^5*yi^3 + 8*x^4*y^5*yi + 3*x^4*y^4*yi^10 + 6*x^4*y^4*yi^8 + 7*x^4*y^4*yi^6 + 10*x^4*y^4*yi^4 + 14*x^4*y^4*yi^2 + 2*x^4*y^3*yi^11 + 6*x^4*y^3*yi^9 + 6*x^4*y^3*yi^7 + 9*x^4*y^3*yi^5 + 16*x^4*y^3*yi^3 + x^4*y^2*yi^12 + 3*x^4*y^2*yi^10 + 5*x^4*y^2*yi^8 + 6*x^4*y^2*yi^6 + 13*x^4*y^2*yi^4 + x^4*y*yi^11 + 2*x^4*y*yi^9 + 2*x^4*y*yi^7 + 7*x^4*y*yi^5 + x^4*yi^8 + 2*x^4*yi^6 + x^3*xi^9*y^6*yi^8 + x^3*xi^9*y^6*yi^6 + x^3*xi^9*y^6*yi^4 + x^3*xi^9*y^6*yi^2 + x^3*xi^9*y^6 + 2*x^3*xi^9*y^5*yi^9 + 2*x^3*xi^9*y^5*yi^7 + 2*x^3*xi^9*y^5*yi^5 + 2*x^3*xi^9*y^5*yi^3 + 2*x^3*xi^9*y^5*yi + 4*x^3*xi^9*y^4*yi^10 + 4*x^3*xi^9*y^4*yi^8 + 4*x^3*xi^9*y^4*yi^6 + 4*x^3*xi^9*y^4*yi^4 + 4*x^3*xi^9*y^4*yi^2 + 4*x^3*xi^9*y^3*yi^11 + 4*x^3*xi^9*y^3*yi^9 + 4*x^3*xi^9*y^3*yi^7 + 4*x^3*xi^9*y^3*yi^5 + 4*x^3*xi^9*y^3*yi^3 + 2*x^3*xi^9*y^2*yi^12 + 2*x^3*xi^9*y^2*yi^10 + 2*x^3*xi^9*y^2*yi^8 + 2*x^3*xi^9*y^2*yi^6 + 2*x^3*xi^9*y^2*yi^4 + x^3*xi^9*y*yi^13 + x^3*xi^9*y*yi^11 + x^3*xi^9*y*yi^9 + x^3*xi^9*y*yi^7 + x^3*xi^9*y*yi^5 + x^3*xi^7*y^8 + 2*x^3*xi^7*y^7*yi + 2*x^3*xi^7*y^6*yi^8 + 2*x^3*xi^7*y^6*yi^6 + x^3*xi^7*y^6*yi^4 + 5*x^3*xi^7*y^6*yi^2 + 2*x^3*xi^7*y^6 + 4*x^3*xi^7*y^5*yi^9 + 4*x^3*xi^7*y^5*yi^7 + 2*x^3*xi^7*y^5*yi^5 + 6*x^3*xi^7*y^5*yi^3 + 4*x^3*xi^7*y^5*yi + 6*x^3*xi^7*y^4*yi^10 + 6*x^3*xi^7*y^4*yi^8 + 2*x^3*xi^7*y^4*yi^6 + 4*x^3*xi^7*y^4*yi^4 + 6*x^3*xi^7*y^4*yi^2 + 6*x^3*xi^7*y^3*yi^11 + 6*x^3*xi^7*y^3*yi^9 + 2*x^3*xi^7*y^3*yi^7 + 3*x^3*xi^7*y^3*yi^5 + 6*x^3*xi^7*y^3*yi^3 + 3*x^3*xi^7*y^2*yi^12 + 3*x^3*xi^7*y^2*yi^10 + x^3*xi^7*y^2*yi^8 + x^3*xi^7*y^2*yi^6 + 3*x^3*xi^7*y^2*yi^4 + x^3*xi^7*y*yi^13 + x^3*xi^7*y*yi^11 + x^3*xi^7*y*yi^5 + x^3*xi^5*y^10*yi^4 + x^3*xi^5*y^10 + x^3*xi^5*y^9*yi^5 + 2*x^3*xi^5*y^9*yi + 4*x^3*xi^5*y^8*yi^2 + x^3*xi^5*y^8 + 4*x^3*xi^5*y^7*yi^3 + 2*x^3*xi^5*y^7*yi + 2*x^3*xi^5*y^6*yi^8 + x^3*xi^5*y^6*yi^6 + 4*x^3*xi^5*y^6*yi^4 + 2*x^3*xi^5*y^6*yi^2 + 2*x^3*xi^5*y^6 + 5*x^3*xi^5*y^5*yi^9 + 3*x^3*xi^5*y^5*yi^7 + 5*x^3*xi^5*y^5*yi^5 + 3*x^3*xi^5*y^5*yi^3 + 5*x^3*xi^5*y^5*yi + 7*x^3*xi^5*y^4*yi^10 + 3*x^3*xi^5*y^4*yi^8 + 5*x^3*xi^5*y^4*yi^6 + 2*x^3*xi^5*y^4*yi^4 + 7*x^3*xi^5*y^4*yi^2 + 6*x^3*xi^5*y^3*yi^11 + 2*x^3*xi^5*y^3*yi^9 + 4*x^3*xi^5*y^3*yi^7 + 6*x^3*xi^5*y^3*yi^3 + 3*x^3*xi^5*y^2*yi^12 + x^3*xi^5*y^2*yi^10 + 3*x^3*xi^5*y^2*yi^8 + 4*x^3*xi^5*y^2*yi^4 + x^3*xi^5*y*yi^13 + 2*x^3*xi^5*y*yi^9 + 2*x^3*xi^5*y*yi^5 + x^3*xi^3*y^13*yi + 3*x^3*xi^3*y^12*yi^2 + x^3*xi^3*y^12 + 6*x^3*xi^3*y^11*yi^3 + 2*x^3*xi^3*y^11*yi + 7*x^3*xi^3*y^10*yi^4 + 4*x^3*xi^3*y^10*yi^2 + x^3*xi^3*y^10 + 5*x^3*xi^3*y^9*yi^5 + 4*x^3*xi^3*y^9*yi^3 + 2*x^3*xi^3*y^9*yi + 2*x^3*xi^3*y^8*yi^6 + 3*x^3*xi^3*y^8*yi^4 + 3*x^3*xi^3*y^8*yi^2 + 2*x^3*xi^3*y^7*yi^5 + 4*x^3*xi^3*y^7*yi^3 + 2*x^3*xi^3*y^7*yi + 2*x^3*xi^3*y^6*yi^8 + 4*x^3*xi^3*y^6*yi^4 + 4*x^3*xi^3*y^6*yi^2 + 2*x^3*xi^3*y^6 + 5*x^3*xi^3*y^5*yi^9 + 2*x^3*xi^3*y^5*yi^7 + 4*x^3*xi^3*y^5*yi^5 + 6*x^3*xi^3*y^5*yi^3 + 6*x^3*xi^3*y^5*yi + 7*x^3*xi^3*y^4*yi^10 + 3*x^3*xi^3*y^4*yi^8 + 4*x^3*xi^3*y^4*yi^6 + 8*x^3*xi^3*y^4*yi^4 + 10*x^3*xi^3*y^4*yi^2 + 6*x^3*xi^3*y^3*yi^11 + 4*x^3*xi^3*y^3*yi^9 + 4*x^3*xi^3*y^3*yi^7 + 6*x^3*xi^3*y^3*yi^5 + 12*x^3*xi^3*y^3*yi^3 + 3*x^3*xi^3*y^2*yi^12 + 4*x^3*xi^3*y^2*yi^10 + 3*x^3*xi^3*y^2*yi^8 + 4*x^3*xi^3*y^2*yi^6 + 10*x^3*xi^3*y^2*yi^4 + x^3*xi^3*y*yi^13 + 2*x^3*xi^3*y*yi^11 + 2*x^3*xi^3*y*yi^9 + 2*x^3*xi^3*y*yi^7 + 6*x^3*xi^3*y*yi^5 + x^3*xi^3*yi^12 + x^3*xi^3*yi^10 + 2*x^3*xi^3*yi^6 + x^3*xi*y^14 + 5*x^3*xi*y^13*yi + 11*x^3*xi*y^12*yi^2 + 2*x^3*xi*y^12 + 14*x^3*xi*y^11*yi^3 + 4*x^3*xi*y^11*yi + 13*x^3*xi*y^10*yi^4 + 7*x^3*xi*y^10*yi^2 + x^3*xi*y^10 + 8*x^3*xi*y^9*yi^5 + 8*x^3*xi*y^9*yi^3 + 4*x^3*xi*y^9*yi + 2*x^3*xi*y^8*yi^6 + 6*x^3*xi*y^8*yi^4 + 7*x^3*xi*y^8*yi^2 + x^3*xi*y^8 + 4*x^3*xi*y^7*yi^5 + 8*x^3*xi*y^7*yi^3 + 4*x^3*xi*y^7*yi + 2*x^3*xi*y^6*yi^8 + 2*x^3*xi*y^6*yi^6 + 8*x^3*xi*y^6*yi^4 + 10*x^3*xi*y^6*yi^2 + 2*x^3*xi*y^6 + 5*x^3*xi*y^5*yi^9 + 4*x^3*xi*y^5*yi^7 + 8*x^3*xi*y^5*yi^5 + 12*x^3*xi*y^5*yi^3 + 8*x^3*xi*y^5*yi + 7*x^3*xi*y^4*yi^10 + 8*x^3*xi*y^4*yi^8 + 8*x^3*xi*y^4*yi^6 + 14*x^3*xi*y^4*yi^4 + 14*x^3*xi*y^4*yi^2 + 6*x^3*xi*y^3*yi^11 + 8*x^3*xi*y^3*yi^9 + 8*x^3*xi*y^3*yi^7 + 12*x^3*xi*y^3*yi^5 + 16*x^3*xi*y^3*yi^3 + 3*x^3*xi*y^2*yi^12 + 6*x^3*xi*y^2*yi^10 + 6*x^3*xi*y^2*yi^8 + 5*x^3*xi*y^2*yi^6 + 14*x^3*xi*y^2*yi^4 + x^3*xi*y*yi^13 + 3*x^3*xi*y*yi^11 + 3*x^3*xi*y*yi^9 + 3*x^3*xi*y*yi^7 + 8*x^3*xi*y*yi^5 + x^3*xi*yi^10 + x^3*xi*yi^8 + 2*x^3*xi*yi^6 + 2*x^2*xi^10*y^5*yi^9 + 2*x^2*xi^10*y^5*yi^7 + 2*x^2*xi^10*y^5*yi^5 + 2*x^2*xi^10*y^5*yi^3 + 2*x^2*xi^10*y^5*yi + 4*x^2*xi^10*y^4*yi^10 + 4*x^2*xi^10*y^4*yi^8 + 4*x^2*xi^10*y^4*yi^6 + 4*x^2*xi^10*y^4*yi^4 + 4*x^2*xi^10*y^4*yi^2 + 4*x^2*xi^10*y^3*yi^11 + 4*x^2*xi^10*y^3*yi^9 + 4*x^2*xi^10*y^3*yi^7 + 4*x^2*xi^10*y^3*yi^5 + 4*x^2*xi^10*y^3*yi^3 + 4*x^2*xi^10*y^2*yi^12 + 4*x^2*xi^10*y^2*yi^10 + 4*x^2*xi^10*y^2*yi^8 + 4*x^2*xi^10*y^2*yi^6 + 4*x^2*xi^10*y^2*yi^4 + 2*x^2*xi^10*y*yi^13 + 2*x^2*xi^10*y*yi^11 + 2*x^2*xi^10*y*yi^9 + 2*x^2*xi^10*y*yi^7 + 2*x^2*xi^10*y*yi^5 + 2*x^2*xi^8*y^7*yi + x^2*xi^8*y^6*yi^8 + x^2*xi^8*y^6*yi^6 + x^2*xi^8*y^6*yi^4 + 5*x^2*xi^8*y^6*yi^2 + x^2*xi^8*y^6 + 4*x^2*xi^8*y^5*yi^9 + 4*x^2*xi^8*y^5*yi^7 + 2*x^2*xi^8*y^5*yi^5 + 6*x^2*xi^8*y^5*yi^3 + 4*x^2*xi^8*y^5*yi + 8*x^2*xi^8*y^4*yi^10 + 8*x^2*xi^8*y^4*yi^8 + 4*x^2*xi^8*y^4*yi^6 + 8*x^2*xi^8*y^4*yi^4 + 8*x^2*xi^8*y^4*yi^2 + 8*x^2*xi^8*y^3*yi^11 + 8*x^2*xi^8*y^3*yi^9 + 4*x^2*xi^8*y^3*yi^7 + 6*x^2*xi^8*y^3*yi^5 + 8*x^2*xi^8*y^3*yi^3 + 6*x^2*xi^8*y^2*yi^12 + 6*x^2*xi^8*y^2*yi^10 + 2*x^2*xi^8*y^2*yi^8 + 2*x^2*xi^8*y^2*yi^6 + 6*x^2*xi^8*y^2*yi^4 + 3*x^2*xi^8*y*yi^13 + 3*x^2*xi^8*y*yi^11 + x^2*xi^8*y*yi^9 + x^2*xi^8*y*yi^7 + 3*x^2*xi^8*y*yi^5 + 2*x^2*xi^6*y^9*yi + 4*x^2*xi^6*y^8*yi^2 + x^2*xi^6*y^8 + 4*x^2*xi^6*y^7*yi^3 + 2*x^2*xi^6*y^7*yi + 2*x^2*xi^6*y^6*yi^8 + 2*x^2*xi^6*y^6*yi^6 + 5*x^2*xi^6*y^6*yi^4 + 5*x^2*xi^6*y^6*yi^2 + 2*x^2*xi^6*y^6 + 6*x^2*xi^6*y^5*yi^9 + 4*x^2*xi^6*y^5*yi^7 + 6*x^2*xi^6*y^5*yi^5 + 6*x^2*xi^6*y^5*yi^3 + 6*x^2*xi^6*y^5*yi + 10*x^2*xi^6*y^4*yi^10 + 6*x^2*xi^6*y^4*yi^8 + 6*x^2*xi^6*y^4*yi^6 + 4*x^2*xi^6*y^4*yi^4 + 10*x^2*xi^6*y^4*yi^2 + 10*x^2*xi^6*y^3*yi^11 + 6*x^2*xi^6*y^3*yi^9 + 6*x^2*xi^6*y^3*yi^7 + 3*x^2*xi^6*y^3*yi^5 + 10*x^2*xi^6*y^3*yi^3 + 7*x^2*xi^6*y^2*yi^12 + 3*x^2*xi^6*y^2*yi^10 + 5*x^2*xi^6*y^2*yi^8 + x^2*xi^6*y^2*yi^6 + 7*x^2*xi^6*y^2*yi^4 + 3*x^2*xi^6*y*yi^13 + x^2*xi^6*y*yi^11 + 2*x^2*xi^6*y*yi^9 + 3*x^2*xi^6*y*yi^5 + x^2*xi^4*y^12*yi^2 + 2*x^2*xi^4*y^11*yi^3 + 2*x^2*xi^4*y^11*yi + 3*x^2*xi^4*y^10*yi^4 + 4*x^2*xi^4*y^10*yi^2 + x^2*xi^4*y^10 + 3*x^2*xi^4*y^9*yi^5 + 4*x^2*xi^4*y^9*yi^3 + 2*x^2*xi^4*y^9*yi + x^2*xi^4*y^8*yi^6 + 4*x^2*xi^4*y^8*yi^4 + 4*x^2*xi^4*y^8*yi^2 + x^2*xi^4*y^8 + 2*x^2*xi^4*y^7*yi^5 + 4*x^2*xi^4*y^7*yi^3 + 2*x^2*xi^4*y^7*yi + 2*x^2*xi^4*y^6*yi^8 + x^2*xi^4*y^6*yi^6 + 4*x^2*xi^4*y^6*yi^4 + 3*x^2*xi^4*y^6*yi^2 + 2*x^2*xi^4*y^6 + 7*x^2*xi^4*y^5*yi^9 + 3*x^2*xi^4*y^5*yi^7 + 5*x^2*xi^4*y^5*yi^5 + 7*x^2*xi^4*y^5*yi^3 + 7*x^2*xi^4*y^5*yi + 11*x^2*xi^4*y^4*yi^10 + 4*x^2*xi^4*y^4*yi^8 + 5*x^2*xi^4*y^4*yi^6 + 8*x^2*xi^4*y^4*yi^4 + 12*x^2*xi^4*y^4*yi^2 + 10*x^2*xi^4*y^3*yi^11 + 4*x^2*xi^4*y^3*yi^9 + 4*x^2*xi^4*y^3*yi^7 + 6*x^2*xi^4*y^3*yi^5 + 12*x^2*xi^4*y^3*yi^3 + 7*x^2*xi^4*y^2*yi^12 + 3*x^2*xi^4*y^2*yi^10 + 3*x^2*xi^4*y^2*yi^8 + 5*x^2*xi^4*y^2*yi^6 + 10*x^2*xi^4*y^2*yi^4 + 3*x^2*xi^4*y*yi^13 + 2*x^2*xi^4*y*yi^11 + 2*x^2*xi^4*y*yi^9 + 2*x^2*xi^4*y*yi^7 + 6*x^2*xi^4*y*yi^5 + x^2*xi^4*yi^12 + x^2*xi^4*yi^6 + 3*x^2*xi^2*y^13*yi + 7*x^2*xi^2*y^12*yi^2 + x^2*xi^2*y^12 + 10*x^2*xi^2*y^11*yi^3 + 4*x^2*xi^2*y^11*yi + 11*x^2*xi^2*y^10*yi^4 + 8*x^2*xi^2*y^10*yi^2 + x^2*xi^2*y^10 + 7*x^2*xi^2*y^9*yi^5 + 8*x^2*xi^2*y^9*yi^3 + 4*x^2*xi^2*y^9*yi + 2*x^2*xi^2*y^8*yi^6 + 7*x^2*xi^2*y^8*yi^4 + 7*x^2*xi^2*y^8*yi^2 + 4*x^2*xi^2*y^7*yi^5 + 8*x^2*xi^2*y^7*yi^3 + 4*x^2*xi^2*y^7*yi + 2*x^2*xi^2*y^6*yi^8 + 8*x^2*xi^2*y^6*yi^4 + 8*x^2*xi^2*y^6*yi^2 + 2*x^2*xi^2*y^6 + 7*x^2*xi^2*y^5*yi^9 + 4*x^2*xi^2*y^5*yi^7 + 8*x^2*xi^2*y^5*yi^5 + 12*x^2*xi^2*y^5*yi^3 + 8*x^2*xi^2*y^5*yi + 11*x^2*xi^2*y^4*yi^10 + 7*x^2*xi^2*y^4*yi^8 + 8*x^2*xi^2*y^4*yi^6 + 16*x^2*xi^2*y^4*yi^4 + 14*x^2*xi^2*y^4*yi^2 + 10*x^2*xi^2*y^3*yi^11 + 8*x^2*xi^2*y^3*yi^9 + 8*x^2*xi^2*y^3*yi^7 + 12*x^2*xi^2*y^3*yi^5 + 16*x^2*xi^2*y^3*yi^3 + 7*x^2*xi^2*y^2*yi^12 + 8*x^2*xi^2*y^2*yi^10 + 7*x^2*xi^2*y^2*yi^8 + 8*x^2*xi^2*y^2*yi^6 + 14*x^2*xi^2*y^2*yi^4 + 3*x^2*xi^2*y*yi^13 + 4*x^2*xi^2*y*yi^11 + 4*x^2*xi^2*y*yi^9 + 4*x^2*xi^2*y*yi^7 + 8*x^2*xi^2*y*yi^5 + x^2*xi^2*yi^12 + x^2*xi^2*yi^10 + 2*x^2*xi^2*yi^6 + x^2*y^14 + 5*x^2*y^13*yi + 11*x^2*y^12*yi^2 + 2*x^2*y^12 + 14*x^2*y^11*yi^3 + 4*x^2*y^11*yi + 13*x^2*y^10*yi^4 + 7*x^2*y^10*yi^2 + x^2*y^10 + 8*x^2*y^9*yi^5 + 8*x^2*y^9*yi^3 + 4*x^2*y^9*yi + 2*x^2*y^8*yi^6 + 6*x^2*y^8*yi^4 + 7*x^2*y^8*yi^2 + x^2*y^8 + 4*x^2*y^7*yi^5 + 8*x^2*y^7*yi^3 + 4*x^2*y^7*yi + 2*x^2*y^6*yi^8 + 2*x^2*y^6*yi^6 + 8*x^2*y^6*yi^4 + 10*x^2*y^6*yi^2 + 2*x^2*y^6 + 5*x^2*y^5*yi^9 + 4*x^2*y^5*yi^7 + 8*x^2*y^5*yi^5 + 12*x^2*y^5*yi^3 + 8*x^2*y^5*yi + 7*x^2*y^4*yi^10 + 8*x^2*y^4*yi^8 + 8*x^2*y^4*yi^6 + 14*x^2*y^4*yi^4 + 14*x^2*y^4*yi^2 + 6*x^2*y^3*yi^11 + 8*x^2*y^3*yi^9 + 8*x^2*y^3*yi^7 + 12*x^2*y^3*yi^5 + 16*x^2*y^3*yi^3 + 3*x^2*y^2*yi^12 + 6*x^2*y^2*yi^10 + 6*x^2*y^2*yi^8 + 5*x^2*y^2*yi^6 + 14*x^2*y^2*yi^4 + x^2*y*yi^13 + 3*x^2*y*yi^11 + 3*x^2*y*yi^9 + 3*x^2*y*yi^7 + 8*x^2*y*yi^5 + x^2*yi^10 + x^2*yi^8 + 2*x^2*yi^6 + x*xi^11*y^5*yi^9 + x*xi^11*y^5*yi^7 + x*xi^11*y^5*yi^5 + x*xi^11*y^5*yi^3 + x*xi^11*y^5*yi + 2*x*xi^11*y^4*yi^10 + 2*x*xi^11*y^4*yi^8 + 2*x*xi^11*y^4*yi^6 + 2*x*xi^11*y^4*yi^4 + 2*x*xi^11*y^4*yi^2 + 4*x*xi^11*y^3*yi^11 + 4*x*xi^11*y^3*yi^9 + 4*x*xi^11*y^3*yi^7 + 4*x*xi^11*y^3*yi^5 + 4*x*xi^11*y^3*yi^3 + 4*x*xi^11*y^2*yi^12 + 4*x*xi^11*y^2*yi^10 + 4*x*xi^11*y^2*yi^8 + 4*x*xi^11*y^2*yi^6 + 4*x*xi^11*y^2*yi^4 + 2*x*xi^11*y*yi^13 + 2*x*xi^11*y*yi^11 + 2*x*xi^11*y*yi^9 + 2*x*xi^11*y*yi^7 + 2*x*xi^11*y*yi^5 + x*xi^11*yi^14 + x*xi^11*yi^12 + x*xi^11*yi^10 + x*xi^11*yi^8 + x*xi^11*yi^6 + x*xi^9*y^7*yi + 2*x*xi^9*y^6*yi^2 + 3*x*xi^9*y^5*yi^9 + 3*x*xi^9*y^5*yi^7 + 2*x*xi^9*y^5*yi^5 + 6*x*xi^9*y^5*yi^3 + 3*x*xi^9*y^5*yi + 6*x*xi^9*y^4*yi^10 + 6*x*xi^9*y^4*yi^8 + 4*x*xi^9*y^4*yi^6 + 8*x*xi^9*y^4*yi^4 + 6*x*xi^9*y^4*yi^2 + 8*x*xi^9*y^3*yi^11 + 8*x*xi^9*y^3*yi^9 + 4*x*xi^9*y^3*yi^7 + 6*x*xi^9*y^3*yi^5 + 8*x*xi^9*y^3*yi^3 + 8*x*xi^9*y^2*yi^12 + 8*x*xi^9*y^2*yi^10 + 4*x*xi^9*y^2*yi^8 + 5*x*xi^9*y^2*yi^6 + 8*x*xi^9*y^2*yi^4 + 4*x*xi^9*y*yi^13 + 4*x*xi^9*y*yi^11 + 2*x*xi^9*y*yi^9 + 2*x*xi^9*y*yi^7 + 4*x*xi^9*y*yi^5 + x*xi^9*yi^14 + x*xi^9*yi^12 + x*xi^9*yi^6 + x*xi^7*y^9*yi + 2*x*xi^7*y^8*yi^2 + 4*x*xi^7*y^7*yi^3 + 2*x*xi^7*y^7*yi + x*xi^7*y^6*yi^8 + x*xi^7*y^6*yi^6 + 5*x*xi^7*y^6*yi^4 + 5*x*xi^7*y^6*yi^2 + x*xi^7*y^6 + 5*x*xi^7*y^5*yi^9 + 4*x*xi^7*y^5*yi^7 + 5*x*xi^7*y^5*yi^5 + 6*x*xi^7*y^5*yi^3 + 5*x*xi^7*y^5*yi + 10*x*xi^7*y^4*yi^10 + 8*x*xi^7*y^4*yi^8 + 7*x*xi^7*y^4*yi^6 + 8*x*xi^7*y^4*yi^4 + 10*x*xi^7*y^4*yi^2 + 12*x*xi^7*y^3*yi^11 + 8*x*xi^7*y^3*yi^9 + 8*x*xi^7*y^3*yi^7 + 6*x*xi^7*y^3*yi^5 + 12*x*xi^7*y^3*yi^3 + 10*x*xi^7*y^2*yi^12 + 6*x*xi^7*y^2*yi^10 + 6*x*xi^7*y^2*yi^8 + 2*x*xi^7*y^2*yi^6 + 10*x*xi^7*y^2*yi^4 + 5*x*xi^7*y*yi^13 + 3*x*xi^7*y*yi^11 + 3*x*xi^7*y*yi^9 + x*xi^7*y*yi^7 + 5*x*xi^7*y*yi^5 + x*xi^7*yi^14 + x*xi^7*yi^10 + x*xi^7*yi^6 + x*xi^5*y^11*yi + x*xi^5*y^10*yi^4 + 2*x*xi^5*y^10*yi^2 + x*xi^5*y^9*yi^5 + 4*x*xi^5*y^9*yi^3 + 2*x*xi^5*y^9*yi + 4*x*xi^5*y^8*yi^4 + 4*x*xi^5*y^8*yi^2 + x*xi^5*y^8 + 2*x*xi^5*y^7*yi^5 + 4*x*xi^5*y^7*yi^3 + 2*x*xi^5*y^7*yi + 2*x*xi^5*y^6*yi^8 + 3*x*xi^5*y^6*yi^6 + 5*x*xi^5*y^6*yi^4 + 5*x*xi^5*y^6*yi^2 + 2*x*xi^5*y^6 + 7*x*xi^5*y^5*yi^9 + 4*x*xi^5*y^5*yi^7 + 6*x*xi^5*y^5*yi^5 + 7*x*xi^5*y^5*yi^3 + 7*x*xi^5*y^5*yi + 12*x*xi^5*y^4*yi^10 + 6*x*xi^5*y^4*yi^8 + 6*x*xi^5*y^4*yi^6 + 7*x*xi^5*y^4*yi^4 + 12*x*xi^5*y^4*yi^2 + 14*x*xi^5*y^3*yi^11 + 6*x*xi^5*y^3*yi^9 + 6*x*xi^5*y^3*yi^7 + 8*x*xi^5*y^3*yi^5 + 14*x*xi^5*y^3*yi^3 + 11*x*xi^5*y^2*yi^12 + 4*x*xi^5*y^2*yi^10 + 5*x*xi^5*y^2*yi^8 + 5*x*xi^5*y^2*yi^6 + 12*x*xi^5*y^2*yi^4 + 5*x*xi^5*y*yi^13 + 2*x*xi^5*y*yi^11 + 2*x*xi^5*y*yi^9 + 2*x*xi^5*y*yi^7 + 6*x*xi^5*y*yi^5 + x*xi^5*yi^14 + x*xi^5*yi^8 + x*xi^5*yi^6 + x*xi^3*y^13*yi + 3*x*xi^3*y^12*yi^2 + 6*x*xi^3*y^11*yi^3 + 3*x*xi^3*y^11*yi + 7*x*xi^3*y^10*yi^4 + 6*x*xi^3*y^10*yi^2 + x*xi^3*y^10 + 5*x*xi^3*y^9*yi^5 + 8*x*xi^3*y^9*yi^3 + 3*x*xi^3*y^9*yi + 2*x*xi^3*y^8*yi^6 + 8*x*xi^3*y^8*yi^4 + 6*x*xi^3*y^8*yi^2 + x*xi^3*y^8 + 4*x*xi^3*y^7*yi^5 + 8*x*xi^3*y^7*yi^3 + 3*x*xi^3*y^7*yi + 2*x*xi^3*y^6*yi^8 + 2*x*xi^3*y^6*yi^6 + 8*x*xi^3*y^6*yi^4 + 5*x*xi^3*y^6*yi^2 + 2*x*xi^3*y^6 + 8*x*xi^3*y^5*yi^9 + 4*x*xi^3*y^5*yi^7 + 8*x*xi^3*y^5*yi^5 + 12*x*xi^3*y^5*yi^3 + 8*x*xi^3*y^5*yi + 13*x*xi^3*y^4*yi^10 + 6*x*xi^3*y^4*yi^8 + 8*x*xi^3*y^4*yi^6 + 14*x*xi^3*y^4*yi^4 + 14*x*xi^3*y^4*yi^2 + 14*x*xi^3*y^3*yi^11 + 8*x*xi^3*y^3*yi^9 + 8*x*xi^3*y^3*yi^7 + 12*x*xi^3*y^3*yi^5 + 16*x*xi^3*y^3*yi^3 + 11*x*xi^3*y^2*yi^12 + 7*x*xi^3*y^2*yi^10 + 7*x*xi^3*y^2*yi^8 + 10*x*xi^3*y^2*yi^6 + 14*x*xi^3*y^2*yi^4 + 5*x*xi^3*y*yi^13 + 4*x*xi^3*y*yi^11 + 4*x*xi^3*y*yi^9 + 4*x*xi^3*y*yi^7 + 8*x*xi^3*y*yi^5 + x*xi^3*yi^14 + 2*x*xi^3*yi^12 + x*xi^3*yi^10 + x*xi^3*yi^8 + 2*x*xi^3*yi^6 + 3*x*xi*y^13*yi + 7*x*xi*y^12*yi^2 + x*xi*y^12 + 10*x*xi*y^11*yi^3 + 4*x*xi*y^11*yi + 11*x*xi*y^10*yi^4 + 8*x*xi*y^10*yi^2 + x*xi*y^10 + 7*x*xi*y^9*yi^5 + 8*x*xi*y^9*yi^3 + 4*x*xi*y^9*yi + 2*x*xi*y^8*yi^6 + 7*x*xi*y^8*yi^4 + 7*x*xi*y^8*yi^2 + 4*x*xi*y^7*yi^5 + 8*x*xi*y^7*yi^3 + 4*x*xi*y^7*yi + 2*x*xi*y^6*yi^8 + 8*x*xi*y^6*yi^4 + 8*x*xi*y^6*yi^2 + 2*x*xi*y^6 + 7*x*xi*y^5*yi^9 + 4*x*xi*y^5*yi^7 + 8*x*xi*y^5*yi^5 + 12*x*xi*y^5*yi^3 + 8*x*xi*y^5*yi + 11*x*xi*y^4*yi^10 + 7*x*xi*y^4*yi^8 + 8*x*xi*y^4*yi^6 + 16*x*xi*y^4*yi^4 + 14*x*xi*y^4*yi^2 + 10*x*xi*y^3*yi^11 + 8*x*xi*y^3*yi^9 + 8*x*xi*y^3*yi^7 + 12*x*xi*y^3*yi^5 + 16*x*xi*y^3*yi^3 + 7*x*xi*y^2*yi^12 + 8*x*xi*y^2*yi^10 + 7*x*xi*y^2*yi^8 + 8*x*xi*y^2*yi^6 + 14*x*xi*y^2*yi^4 + 3*x*xi*y*yi^13 + 4*x*xi*y*yi^11 + 4*x*xi*y*yi^9 + 4*x*xi*y*yi^7 + 8*x*xi*y*yi^5 + x*xi*yi^12 + x*xi*yi^10 + 2*x*xi*yi^6 + xi^12*y^4*yi^10 + xi^12*y^4*yi^8 + xi^12*y^4*yi^6 + xi^12*y^4*yi^4 + xi^12*y^4*yi^2 + 2*xi^12*y^3*yi^11 + 2*xi^12*y^3*yi^9 + 2*xi^12*y^3*yi^7 + 2*xi^12*y^3*yi^5 + 2*xi^12*y^3*yi^3 + 2*xi^12*y^2*yi^12 + 2*xi^12*y^2*yi^10 + 2*xi^12*y^2*yi^8 + 2*xi^12*y^2*yi^6 + 2*xi^12*y^2*yi^4 + 2*xi^12*y*yi^13 + 2*xi^12*y*yi^11 + 2*xi^12*y*yi^9 + 2*xi^12*y*yi^7 + 2*xi^12*y*yi^5 + xi^12*yi^14 + xi^12*yi^12 + xi^12*yi^10 + xi^12*yi^8 + xi^12*yi^6 + xi^10*y^6*yi^2 + xi^10*y^5*yi^9 + xi^10*y^5*yi^7 + xi^10*y^5*yi^5 + 3*xi^10*y^5*yi^3 + xi^10*y^5*yi + 3*xi^10*y^4*yi^10 + 3*xi^10*y^4*yi^8 + 2*xi^10*y^4*yi^6 + 4*xi^10*y^4*yi^4 + 3*xi^10*y^4*yi^2 + 6*xi^10*y^3*yi^11 + 6*xi^10*y^3*yi^9 + 4*xi^10*y^3*yi^7 + 6*xi^10*y^3*yi^5 + 6*xi^10*y^3*yi^3 + 6*xi^10*y^2*yi^12 + 6*xi^10*y^2*yi^10 + 4*xi^10*y^2*yi^8 + 5*xi^10*y^2*yi^6 + 6*xi^10*y^2*yi^4 + 4*xi^10*y*yi^13 + 4*xi^10*y*yi^11 + 2*xi^10*y*yi^9 + 2*xi^10*y*yi^7 + 4*xi^10*y*yi^5 + 2*xi^10*yi^14 + 2*xi^10*yi^12 + xi^10*yi^10 + xi^10*yi^8 + 2*xi^10*yi^6 + xi^8*y^8*yi^2 + 2*xi^8*y^7*yi^3 + xi^8*y^7*yi + 2*xi^8*y^6*yi^4 + 2*xi^8*y^6*yi^2 + 3*xi^8*y^5*yi^9 + 3*xi^8*y^5*yi^7 + 4*xi^8*y^5*yi^5 + 6*xi^8*y^5*yi^3 + 3*xi^8*y^5*yi + 7*xi^8*y^4*yi^10 + 6*xi^8*y^4*yi^8 + 6*xi^8*y^4*yi^6 + 8*xi^8*y^4*yi^4 + 7*xi^8*y^4*yi^2 + 10*xi^8*y^3*yi^11 + 8*xi^8*y^3*yi^9 + 6*xi^8*y^3*yi^7 + 6*xi^8*y^3*yi^5 + 10*xi^8*y^3*yi^3 + 10*xi^8*y^2*yi^12 + 8*xi^8*y^2*yi^10 + 6*xi^8*y^2*yi^8 + 5*xi^8*y^2*yi^6 + 10*xi^8*y^2*yi^4 + 6*xi^8*y*yi^13 + 4*xi^8*y*yi^11 + 4*xi^8*y*yi^9 + 2*xi^8*y*yi^7 + 6*xi^8*y*yi^5 + 2*xi^8*yi^14 + xi^8*yi^12 + xi^8*yi^10 + 2*xi^8*yi^6 + xi^6*y^10*yi^2 + 2*xi^6*y^9*yi^3 + xi^6*y^9*yi + 2*xi^6*y^8*yi^4 + 2*xi^6*y^8*yi^2 + 2*xi^6*y^7*yi^5 + 4*xi^6*y^7*yi^3 + 2*xi^6*y^7*yi + xi^6*y^6*yi^8 + 2*xi^6*y^6*yi^6 + 5*xi^6*y^6*yi^4 + 5*xi^6*y^6*yi^2 + xi^6*y^6 + 5*xi^6*y^5*yi^9 + 4*xi^6*y^5*yi^7 + 5*xi^6*y^5*yi^5 + 6*xi^6*y^5*yi^3 + 5*xi^6*y^5*yi + 11*xi^6*y^4*yi^10 + 8*xi^6*y^4*yi^8 + 7*xi^6*y^4*yi^6 + 9*xi^6*y^4*yi^4 + 11*xi^6*y^4*yi^2 + 14*xi^6*y^3*yi^11 + 8*xi^6*y^3*yi^9 + 8*xi^6*y^3*yi^7 + 8*xi^6*y^3*yi^5 + 14*xi^6*y^3*yi^3 + 12*xi^6*y^2*yi^12 + 6*xi^6*y^2*yi^10 + 6*xi^6*y^2*yi^8 + 4*xi^6*y^2*yi^6 + 12*xi^6*y^2*yi^4 + 7*xi^6*y*yi^13 + 3*xi^6*y*yi^11 + 3*xi^6*y*yi^9 + 3*xi^6*y*yi^7 + 7*xi^6*y*yi^5 + 2*xi^6*yi^14 + xi^6*yi^10 + xi^6*yi^8 + 2*xi^6*yi^6 + xi^4*y^12*yi^2 + 2*xi^4*y^11*yi^3 + xi^4*y^11*yi + 3*xi^4*y^10*yi^4 + 3*xi^4*y^10*yi^2 + 3*xi^4*y^9*yi^5 + 6*xi^4*y^9*yi^3 + 2*xi^4*y^9*yi + xi^4*y^8*yi^6 + 6*xi^4*y^8*yi^4 + 5*xi^4*y^8*yi^2 + xi^4*y^8 + 4*xi^4*y^7*yi^5 + 6*xi^4*y^7*yi^3 + 2*xi^4*y^7*yi + 2*xi^4*y^6*yi^8 + 4*xi^4*y^6*yi^6 + 7*xi^4*y^6*yi^4 + 6*xi^4*y^6*yi^2 + 2*xi^4*y^6 + 7*xi^4*y^5*yi^9 + 4*xi^4*y^5*yi^7 + 8*xi^4*y^5*yi^5 + 9*xi^4*y^5*yi^3 + 7*xi^4*y^5*yi + 13*xi^4*y^4*yi^10 + 7*xi^4*y^4*yi^8 + 8*xi^4*y^4*yi^6 + 10*xi^4*y^4*yi^4 + 13*xi^4*y^4*yi^2 + 16*xi^4*y^3*yi^11 + 8*xi^4*y^3*yi^9 + 8*xi^4*y^3*yi^7 + 12*xi^4*y^3*yi^5 + 16*xi^4*y^3*yi^3 + 13*xi^4*y^2*yi^12 + 6*xi^4*y^2*yi^10 + 7*xi^4*y^2*yi^8 + 8*xi^4*y^2*yi^6 + 14*xi^4*y^2*yi^4 + 7*xi^4*y*yi^13 + 4*xi^4*y*yi^11 + 4*xi^4*y*yi^9 + 4*xi^4*y*yi^7 + 8*xi^4*y*yi^5 + 2*xi^4*yi^14 + xi^4*yi^12 + xi^4*yi^10 + 2*xi^4*yi^8 + 2*xi^4*yi^6 + xi^2*y^13*yi + 3*xi^2*y^12*yi^2 + 6*xi^2*y^11*yi^3 + 3*xi^2*y^11*yi + 7*xi^2*y^10*yi^4 + 6*xi^2*y^10*yi^2 + xi^2*y^10 + 5*xi^2*y^9*yi^5 + 8*xi^2*y^9*yi^3 + 3*xi^2*y^9*yi + 2*xi^2*y^8*yi^6 + 8*xi^2*y^8*yi^4 + 6*xi^2*y^8*yi^2 + xi^2*y^8 + 4*xi^2*y^7*yi^5 + 8*xi^2*y^7*yi^3 + 3*xi^2*y^7*yi + 2*xi^2*y^6*yi^8 + 2*xi^2*y^6*yi^6 + 8*xi^2*y^6*yi^4 + 5*xi^2*y^6*yi^2 + 2*xi^2*y^6 + 8*xi^2*y^5*yi^9 + 4*xi^2*y^5*yi^7 + 8*xi^2*y^5*yi^5 + 12*xi^2*y^5*yi^3 + 8*xi^2*y^5*yi + 13*xi^2*y^4*yi^10 + 6*xi^2*y^4*yi^8 + 8*xi^2*y^4*yi^6 + 14*xi^2*y^4*yi^4 + 14*xi^2*y^4*yi^2 + 14*xi^2*y^3*yi^11 + 8*xi^2*y^3*yi^9 + 8*xi^2*y^3*yi^7 + 12*xi^2*y^3*yi^5 + 16*xi^2*y^3*yi^3 + 11*xi^2*y^2*yi^12 + 7*xi^2*y^2*yi^10 + 7*xi^2*y^2*yi^8 + 10*xi^2*y^2*yi^6 + 14*xi^2*y^2*yi^4 + 5*xi^2*y*yi^13 + 4*xi^2*y*yi^11 + 4*xi^2*y*yi^9 + 4*xi^2*y*yi^7 + 8*xi^2*y*yi^5 + xi^2*yi^14 + 2*xi^2*yi^12 + xi^2*yi^10 + xi^2*yi^8 + 2*xi^2*yi^6 + 3*y^13*yi + 7*y^12*yi^2 + y^12 + 10*y^11*yi^3 + 4*y^11*yi + 11*y^10*yi^4 + 8*y^10*yi^2 + y^10 + 7*y^9*yi^5 + 8*y^9*yi^3 + 4*y^9*yi + 2*y^8*yi^6 + 7*y^8*yi^4 + 7*y^8*yi^2 + 4*y^7*yi^5 + 8*y^7*yi^3 + 4*y^7*yi + 2*y^6*yi^8 + 8*y^6*yi^4 + 8*y^6*yi^2 + 2*y^6 + 7*y^5*yi^9 + 4*y^5*yi^7 + 8*y^5*yi^5 + 12*y^5*yi^3 + 8*y^5*yi + 11*y^4*yi^10 + 7*y^4*yi^8 + 8*y^4*yi^6 + 16*y^4*yi^4 + 14*y^4*yi^2 + 10*y^3*yi^11 + 8*y^3*yi^9 + 8*y^3*yi^7 + 12*y^3*yi^5 + 16*y^3*yi^3 + 7*y^2*yi^12 + 8*y^2*yi^10 + 7*y^2*yi^8 + 8*y^2*yi^6 + 14*y^2*yi^4 + 3*y*yi^13 + 4*y*yi^11 + 4*y*yi^9 + 4*y*yi^7 + 8*y*yi^5 + yi^12 + yi^10 + 2*yi^6) * hx + (x^14*y^12 + x^14*y^11*yi + 2*x^14*y^10 + x^14*y^9*yi + 2*x^14*y^8 + x^14*y^7*yi + 2*x^14*y^6 + x^14*y^5*yi + 2*x^14*y^4 + x^14*y^3*yi + x^14*y^2 + 3*x^12*y^12 + 3*x^12*y^11*yi + 2*x^12*y^10*yi^2 + 6*x^12*y^10 + x^12*y^9*yi^3 + 5*x^12*y^9*yi + 3*x^12*y^8*yi^2 + 7*x^12*y^8 + x^12*y^7*yi^3 + 5*x^12*y^7*yi + 3*x^12*y^6*yi^2 + 7*x^12*y^6 + x^12*y^5*yi^3 + 5*x^12*y^5*yi + 4*x^12*y^4*yi^2 + 8*x^12*y^4 + 2*x^12*y^3*yi^3 + 7*x^12*y^3*yi + 4*x^12*y^2*yi^2 + 7*x^12*y^2 + x^12*y*yi^3 + 4*x^12*y*yi + x^12*yi^2 + 4*x^12 + 5*x^10*y^12 + 7*x^10*y^11*yi + 6*x^10*y^10*yi^2 + 11*x^10*y^10 + 3*x^10*y^9*yi^3 + 12*x^10*y^9*yi + x^10*y^8*yi^4 + 9*x^10*y^8*yi^2 + 15*x^10*y^8 + 4*x^10*y^7*yi^3 + 14*x^10*y^7*yi + x^10*y^6*yi^4 + 8*x^10*y^6*yi^2 + 16*x^10*y^6 + 3*x^10*y^5*yi^3 + 13*x^10*y^5*yi + 2*x^10*y^4*yi^4 + 9*x^10*y^4*yi^2 + 18*x^10*y^4 + x^10*y^3*yi^5 + 6*x^10*y^3*yi^3 + 16*x^10*y^3*yi + 4*x^10*y^2*yi^4 + 12*x^10*y^2*yi^2 + 16*x^10*y^2 + x^10*y*yi^5 + 7*x^10*y*yi^3 + 12*x^10*y*yi + 2*x^10*yi^4 + 7*x^10*yi^2 + 12*x^10 + 7*x^8*y^12 + 11*x^8*y^11*yi + 10*x^8*y^10*yi^2 + 15*x^8*y^10 + 7*x^8*y^9*yi^3 + 18*x^8*y^9*yi + 3*x^8*y^8*yi^4 + 15*x^8*y^8*yi^2 + 22*x^8*y^8 + 9*x^8*y^7*yi^3 + 21*x^8*y^7*yi + 3*x^8*y^6*yi^4 + 15*x^8*y^6*yi^2 + 24*x^8*y^6 + 9*x^8*y^5*yi^3 + 21*x^8*y^5*yi + x^8*y^4*yi^6 + 4*x^8*y^4*yi^4 + 15*x^8*y^4*yi^2 + 28*x^8*y^4 + x^8*y^3*yi^7 + 3*x^8*y^3*yi^5 + 12*x^8*y^3*yi^3 + 26*x^8*y^3*yi + 3*x^8*y^2*yi^6 + 9*x^8*y^2*yi^4 + 22*x^8*y^2*yi^2 + 26*x^8*y^2 + x^8*y*yi^7 + 5*x^8*y*yi^5 + 16*x^8*y*yi^3 + 22*x^8*y*yi + 2*x^8*yi^6 + 8*x^8*yi^4 + 16*x^8*yi^2 + 22*x^8 + 8*x^6*y^12 + 13*x^6*y^11*yi + 14*x^6*y^10*yi^2 + 17*x^6*y^10 + 11*x^6*y^9*yi^3 + 21*x^6*y^9*yi + 5*x^6*y^8*yi^4 + 19*x^6*y^8*yi^2 + 25*x^6*y^8 + x^6*y^7*yi^5 + 13*x^6*y^7*yi^3 + 26*x^6*y^7*yi + 5*x^6*y^6*yi^4 + 21*x^6*y^6*yi^2 + 30*x^6*y^6 + 2*x^6*y^5*yi^5 + 12*x^6*y^5*yi^3 + 26*x^6*y^5*yi + x^6*y^4*yi^8 + 3*x^6*y^4*yi^6 + 8*x^6*y^4*yi^4 + 21*x^6*y^4*yi^2 + 34*x^6*y^4 + x^6*y^3*yi^9 + 4*x^6*y^3*yi^7 + 9*x^6*y^3*yi^5 + 18*x^6*y^3*yi^3 + 34*x^6*y^3*yi + 3*x^6*y^2*yi^8 + 8*x^6*y^2*yi^6 + 15*x^6*y^2*yi^4 + 32*x^6*y^2*yi^2 + 34*x^6*y^2 + x^6*y*yi^9 + 5*x^6*y*yi^7 + 13*x^6*y*yi^5 + 26*x^6*y*yi^3 + 32*x^6*y*yi + 2*x^6*yi^8 + 7*x^6*yi^6 + 18*x^6*yi^4 + 26*x^6*yi^2 + 32*x^6 + 7*x^4*y^12 + 13*x^4*y^11*yi + 16*x^4*y^10*yi^2 + 17*x^4*y^10 + 13*x^4*y^9*yi^3 + 22*x^4*y^9*yi + 7*x^4*y^8*yi^4 + 21*x^4*y^8*yi^2 + 26*x^4*y^8 + 2*x^4*y^7*yi^5 + 14*x^4*y^7*yi^3 + 28*x^4*y^7*yi + 6*x^4*y^6*yi^4 + 22*x^4*y^6*yi^2 + 32*x^4*y^6 + x^4*y^5*yi^7 + 4*x^4*y^5*yi^5 + 14*x^4*y^5*yi^3 + 30*x^4*y^5*yi + 3*x^4*y^4*yi^8 + 5*x^4*y^4*yi^6 + 12*x^4*y^4*yi^4 + 26*x^4*y^4*yi^2 + 38*x^4*y^4 + 3*x^4*y^3*yi^9 + 9*x^4*y^3*yi^7 + 12*x^4*y^3*yi^5 + 22*x^4*y^3*yi^3 + 40*x^4*y^3*yi + 2*x^4*y^2*yi^10 + 9*x^4*y^2*yi^8 + 15*x^4*y^2*yi^6 + 21*x^4*y^2*yi^4 + 38*x^4*y^2*yi^2 + 40*x^4*y^2 + x^4*y*yi^11 + 5*x^4*y*yi^9 + 14*x^4*y*yi^7 + 21*x^4*y*yi^5 + 34*x^4*y*yi^3 + 38*x^4*y*yi + 2*x^4*yi^10 + 7*x^4*yi^8 + 16*x^4*yi^6 + 28*x^4*yi^4 + 34*x^4*yi^2 + 38*x^4 + 5*x^2*y^12 + 11*x^2*y^11*yi + 14*x^2*y^10*yi^2 + 15*x^2*y^10 + 13*x^2*y^9*yi^3 + 21*x^2*y^9*yi + 8*x^2*y^8*yi^4 + 21*x^2*y^8*yi^2 + 25*x^2*y^8 + 2*x^2*y^7*yi^5 + 14*x^2*y^7*yi^3 + 28*x^2*y^7*yi + 6*x^2*y^6*yi^4 + 22*x^2*y^6*yi^2 + 32*x^2*y^6 + 2*x^2*y^5*yi^7 + 2*x^2*y^5*yi^5 + 14*x^2*y^5*yi^3 + 32*x^2*y^5*yi + 5*x^2*y^4*yi^8 + 6*x^2*y^4*yi^6 + 10*x^2*y^4*yi^4 + 26*x^2*y^4*yi^2 + 40*x^2*y^4 + 7*x^2*y^3*yi^9 + 13*x^2*y^3*yi^7 + 14*x^2*y^3*yi^5 + 24*x^2*y^3*yi^3 + 40*x^2*y^3*yi + 6*x^2*y^2*yi^10 + 15*x^2*y^2*yi^8 + 21*x^2*y^2*yi^6 + 26*x^2*y^2*yi^4 + 40*x^2*y^2*yi^2 + 40*x^2*y^2 + 3*x^2*y*yi^11 + 12*x^2*y*yi^9 + 21*x^2*y*yi^7 + 26*x^2*y*yi^5 + 40*x^2*y*yi^3 + 40*x^2*y*yi + x^2*yi^12 + 6*x^2*yi^10 + 15*x^2*yi^8 + 24*x^2*yi^6 + 34*x^2*yi^4 + 40*x^2*yi^2 + 40*x^2 + xi^14*y*yi^11 + xi^14*y*yi^9 + xi^14*y*yi^7 + xi^14*y*yi^5 + xi^14*y*yi^3 + xi^14*yi^12 + 2*xi^14*yi^10 + 2*xi^14*yi^8 + 2*xi^14*yi^6 + 2*xi^14*yi^4 + xi^14*yi^2 + xi^12*y^3*yi^9 + xi^12*y^3*yi^7 + xi^12*y^3*yi^5 + 2*xi^12*y^3*yi^3 + xi^12*y^3*yi + 2*xi^12*y^2*yi^10 + 3*xi^12*y^2*yi^8 + 3*xi^12*y^2*yi^6 + 4*xi^12*y^2*yi^4 + 4*xi^12*y^2*yi^2 + xi^12*y^2 + 3*xi^12*y*yi^11 + 5*xi^12*y*yi^9 + 5*xi^12*y*yi^7 + 5*xi^12*y*yi^5 + 7*xi^12*y*yi^3 + 4*xi^12*y*yi + 3*xi^12*yi^12 + 6*xi^12*yi^10 + 7*xi^12*yi^8 + 7*xi^12*yi^6 + 8*xi^12*yi^4 + 7*xi^12*yi^2 + 4*xi^12 + xi^10*y^5*yi^3 + xi^10*y^5*yi + xi^10*y^4*yi^8 + xi^10*y^4*yi^6 + 2*xi^10*y^4*yi^4 + 4*xi^10*y^4*yi^2 + 2*xi^10*y^4 + 3*xi^10*y^3*yi^9 + 4*xi^10*y^3*yi^7 + 3*xi^10*y^3*yi^5 + 6*xi^10*y^3*yi^3 + 7*xi^10*y^3*yi + 6*xi^10*y^2*yi^10 + 9*xi^10*y^2*yi^8 + 8*xi^10*y^2*yi^6 + 9*xi^10*y^2*yi^4 + 12*xi^10*y^2*yi^2 + 7*xi^10*y^2 + 7*xi^10*y*yi^11 + 12*xi^10*y*yi^9 + 14*xi^10*y*yi^7 + 13*xi^10*y*yi^5 + 16*xi^10*y*yi^3 + 12*xi^10*y*yi + 5*xi^10*yi^12 + 11*xi^10*yi^10 + 15*xi^10*yi^8 + 16*xi^10*yi^6 + 18*xi^10*yi^4 + 16*xi^10*yi^2 + 12*xi^10 + xi^8*y^7*yi^3 + xi^8*y^7*yi + xi^8*y^6*yi^4 + 3*xi^8*y^6*yi^2 + 2*xi^8*y^6 + 3*xi^8*y^5*yi^3 + 5*xi^8*y^5*yi + 3*xi^8*y^4*yi^8 + 3*xi^8*y^4*yi^6 + 4*xi^8*y^4*yi^4 + 9*xi^8*y^4*yi^2 + 8*xi^8*y^4 + 7*xi^8*y^3*yi^9 + 9*xi^8*y^3*yi^7 + 9*xi^8*y^3*yi^5 + 12*xi^8*y^3*yi^3 + 16*xi^8*y^3*yi + 10*xi^8*y^2*yi^10 + 15*xi^8*y^2*yi^8 + 15*xi^8*y^2*yi^6 + 15*xi^8*y^2*yi^4 + 22*xi^8*y^2*yi^2 + 16*xi^8*y^2 + 11*xi^8*y*yi^11 + 18*xi^8*y*yi^9 + 21*xi^8*y*yi^7 + 21*xi^8*y*yi^5 + 26*xi^8*y*yi^3 + 22*xi^8*y*yi + 7*xi^8*yi^12 + 15*xi^8*yi^10 + 22*xi^8*yi^8 + 24*xi^8*yi^6 + 28*xi^8*yi^4 + 26*xi^8*yi^2 + 22*xi^8 + xi^6*y^9*yi^3 + xi^6*y^9*yi + xi^6*y^8*yi^4 + 3*xi^6*y^8*yi^2 + 2*xi^6*y^8 + 4*xi^6*y^7*yi^3 + 5*xi^6*y^7*yi + 3*xi^6*y^6*yi^4 + 8*xi^6*y^6*yi^2 + 7*xi^6*y^6 + xi^6*y^5*yi^7 + 2*xi^6*y^5*yi^5 + 9*xi^6*y^5*yi^3 + 13*xi^6*y^5*yi + 5*xi^6*y^4*yi^8 + 5*xi^6*y^4*yi^6 + 8*xi^6*y^4*yi^4 + 15*xi^6*y^4*yi^2 + 18*xi^6*y^4 + 11*xi^6*y^3*yi^9 + 13*xi^6*y^3*yi^7 + 12*xi^6*y^3*yi^5 + 18*xi^6*y^3*yi^3 + 26*xi^6*y^3*yi + 14*xi^6*y^2*yi^10 + 19*xi^6*y^2*yi^8 + 21*xi^6*y^2*yi^6 + 21*xi^6*y^2*yi^4 + 32*xi^6*y^2*yi^2 + 26*xi^6*y^2 + 13*xi^6*y*yi^11 + 21*xi^6*y*yi^9 + 26*xi^6*y*yi^7 + 26*xi^6*y*yi^5 + 34*xi^6*y*yi^3 + 32*xi^6*y*yi + 8*xi^6*yi^12 + 17*xi^6*yi^10 + 25*xi^6*yi^8 + 30*xi^6*yi^6 + 34*xi^6*yi^4 + 34*xi^6*yi^2 + 32*xi^6 + xi^4*y^11*yi + 2*xi^4*y^10*yi^2 + 2*xi^4*y^10 + 3*xi^4*y^9*yi^3 + 5*xi^4*y^9*yi + 3*xi^4*y^8*yi^4 + 9*xi^4*y^8*yi^2 + 7*xi^4*y^8 + xi^4*y^7*yi^5 + 9*xi^4*y^7*yi^3 + 14*xi^4*y^7*yi + 5*xi^4*y^6*yi^4 + 15*xi^4*y^6*yi^2 + 16*xi^4*y^6 + 2*xi^4*y^5*yi^7 + 4*xi^4*y^5*yi^5 + 12*xi^4*y^5*yi^3 + 21*xi^4*y^5*yi + 7*xi^4*y^4*yi^8 + 6*xi^4*y^4*yi^6 + 12*xi^4*y^4*yi^4 + 21*xi^4*y^4*yi^2 + 28*xi^4*y^4 + 13*xi^4*y^3*yi^9 + 14*xi^4*y^3*yi^7 + 14*xi^4*y^3*yi^5 + 22*xi^4*y^3*yi^3 + 34*xi^4*y^3*yi + 16*xi^4*y^2*yi^10 + 21*xi^4*y^2*yi^8 + 22*xi^4*y^2*yi^6 + 26*xi^4*y^2*yi^4 + 38*xi^4*y^2*yi^2 + 34*xi^4*y^2 + 13*xi^4*y*yi^11 + 22*xi^4*y*yi^9 + 28*xi^4*y*yi^7 + 30*xi^4*y*yi^5 + 40*xi^4*y*yi^3 + 38*xi^4*y*yi + 7*xi^4*yi^12 + 17*xi^4*yi^10 + 26*xi^4*yi^8 + 32*xi^4*yi^6 + 38*xi^4*yi^4 + 40*xi^4*yi^2 + 38*xi^4 + xi^2*y^12 + 3*xi^2*y^11*yi + 6*xi^2*y^10*yi^2 + 6*xi^2*y^10 + 7*xi^2*y^9*yi^3 + 12*xi^2*y^9*yi + 5*xi^2*y^8*yi^4 + 15*xi^2*y^8*yi^2 + 15*xi^2*y^8 + 2*xi^2*y^7*yi^5 + 13*xi^2*y^7*yi^3 + 21*xi^2*y^7*yi + 6*xi^2*y^6*yi^4 + 21*xi^2*y^6*yi^2 + 24*xi^2*y^6 + 2*xi^2*y^5*yi^7 + 2*xi^2*y^5*yi^5 + 14*xi^2*y^5*yi^3 + 26*xi^2*y^5*yi + 8*xi^2*y^4*yi^8 + 6*xi^2*y^4*yi^6 + 10*xi^2*y^4*yi^4 + 26*xi^2*y^4*yi^2 + 34*xi^2*y^4 + 13*xi^2*y^3*yi^9 + 14*xi^2*y^3*yi^7 + 14*xi^2*y^3*yi^5 + 24*xi^2*y^3*yi^3 + 40*xi^2*y^3*yi + 14*xi^2*y^2*yi^10 + 21*xi^2*y^2*yi^8 + 22*xi^2*y^2*yi^6 + 26*xi^2*y^2*yi^4 + 40*xi^2*y^2*yi^2 + 40*xi^2*y^2 + 11*xi^2*y*yi^11 + 21*xi^2*y*yi^9 + 28*xi^2*y*yi^7 + 32*xi^2*y*yi^5 + 40*xi^2*y*yi^3 + 40*xi^2*y*yi + 5*xi^2*yi^12 + 15*xi^2*yi^10 + 25*xi^2*yi^8 + 32*xi^2*yi^6 + 40*xi^2*yi^4 + 40*xi^2*yi^2 + 40*xi^2 + 3*y^12 + 7*y^11*yi + 10*y^10*yi^2 + 11*y^10 + 11*y^9*yi^3 + 18*y^9*yi + 7*y^8*yi^4 + 19*y^8*yi^2 + 22*y^8 + 2*y^7*yi^5 + 14*y^7*yi^3 + 26*y^7*yi + 6*y^6*yi^4 + 22*y^6*yi^2 + 30*y^6 + 2*y^5*yi^7 + 14*y^5*yi^3 + 30*y^5*yi + 7*y^4*yi^8 + 6*y^4*yi^6 + 8*y^4*yi^4 + 26*y^4*yi^2 + 38*y^4 + 11*y^3*yi^9 + 14*y^3*yi^7 + 14*y^3*yi^5 + 24*y^3*yi^3 + 40*y^3*yi + 10*y^2*yi^10 + 19*y^2*yi^8 + 22*y^2*yi^6 + 26*y^2*yi^4 + 40*y^2*yi^2 + 40*y^2 + 7*y*yi^11 + 18*y*yi^9 + 26*y*yi^7 + 30*y*yi^5 + 40*y*yi^3 + 40*y*yi + 3*yi^12 + 11*yi^10 + 22*yi^8 + 30*yi^6 + 38*yi^4 + 40*yi^2 + 40) * hy

theorem triPoly_x1 {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (y yi : R) (hy : y * yi = 1) :
    triPoly 1 1 y yi = ((y + yi + 1)^2)^2 := by
  unfold triPoly
  linear_combination (2*y^4 - 3*y^2 - 6*y + 2*yi^4 - 3*yi^2 - 6*yi - 5) * h2 + (-4*y^2 - 6*y*yi - 12*y - 4*yi^2 - 12*yi - 18) * hy

theorem triPoly_y1 {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    triPoly x xi 1 1 = ((x + xi + 1)^2)^2 := by
  unfold triPoly
  linear_combination (2*x^4 - 3*x^2 - 6*x + 2*xi^4 - 3*xi^2 - 6*xi - 5) * h2 + (-4*x^2 - 6*x*xi - 12*x - 4*xi^2 - 12*xi - 18) * hx

theorem triPoly_anti {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    triPoly x xi xi x = ((x + xi + 1)^2)^2 := by
  unfold triPoly
  linear_combination (2*x^4 - 3*x^2 - 6*x + 2*xi^4 - 3*xi^2 - 6*xi - 5) * h2 + (2*x^3*xi^3 + 2*x^3*xi^2 + 2*x^3*xi + 2*x^3 + 2*x^2*xi^3 + 4*x^2*xi^2 + 2*x^2*xi - 2*x^2 + 2*x*xi^3 + 2*x*xi^2 - 10*x + 2*xi^3 - 2*xi^2 - 10*xi - 10) * hx

theorem triPoly_x2y {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    triPoly x xi (xi^2) (x^2) * (x + xi) = x^9 + xi^9 := by
  unfold triPoly
  linear_combination (x^8 + 2*x^7 + 2*x^6 + 3*x^5 + 2*x^4 + 4*x^3 + 2*x^2 + 4*x + xi^8 + 2*xi^7 + 2*xi^6 + 3*xi^5 + 2*xi^4 + 4*xi^3 + 2*xi^2 + 4*xi + 2) * h2 + (x^8*xi^3 + x^8*xi^2 + x^8*xi + x^8 + x^7*xi^4 + x^7*xi^3 + 2*x^7*xi^2 + 2*x^7*xi + 2*x^7 + 2*x^6*xi^3 + 2*x^6*xi^2 + 2*x^6*xi + 3*x^6 + x^5*xi^4 + x^5*xi^3 + 2*x^5*xi^2 + 2*x^5*xi + 4*x^5 + x^4*xi^7 + x^4*xi^5 + 3*x^4*xi^3 + x^4*xi^2 + 4*x^4*xi + 3*x^4 + x^3*xi^8 + x^3*xi^7 + 2*x^3*xi^6 + x^3*xi^5 + 3*x^3*xi^4 + 5*x^3*xi^2 + x^3*xi + 6*x^3 + x^2*xi^8 + 2*x^2*xi^7 + 2*x^2*xi^6 + 2*x^2*xi^5 + x^2*xi^4 + 5*x^2*xi^3 + 5*x^2*xi + 3*x^2 + x*xi^8 + 2*x*xi^7 + 2*x*xi^6 + 2*x*xi^5 + 4*x*xi^4 + x*xi^3 + 5*x*xi^2 + 2*x*xi + 7*x + xi^8 + 2*xi^7 + 3*xi^6 + 4*xi^5 + 3*xi^4 + 6*xi^3 + 3*xi^2 + 7*xi + 4) * hx

theorem triPoly_xy2 {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (y yi : R) (hy : y * yi = 1) :
    triPoly (yi^2) (y^2) y yi * (y + yi) = y^9 + yi^9 := by
  unfold triPoly
  linear_combination (y^8 + 2*y^7 + 2*y^6 + 3*y^5 + 2*y^4 + 4*y^3 + 2*y^2 + 4*y + yi^8 + 2*yi^7 + 2*yi^6 + 3*yi^5 + 2*yi^4 + 4*yi^3 + 2*yi^2 + 4*yi + 2) * h2 + (y^8*yi^3 + y^8*yi^2 + y^8*yi + y^8 + y^7*yi^4 + y^7*yi^3 + 2*y^7*yi^2 + 2*y^7*yi + 2*y^7 + 2*y^6*yi^3 + 2*y^6*yi^2 + 2*y^6*yi + 3*y^6 + y^5*yi^4 + y^5*yi^3 + 2*y^5*yi^2 + 2*y^5*yi + 4*y^5 + y^4*yi^7 + y^4*yi^5 + 3*y^4*yi^3 + y^4*yi^2 + 4*y^4*yi + 3*y^4 + y^3*yi^8 + y^3*yi^7 + 2*y^3*yi^6 + y^3*yi^5 + 3*y^3*yi^4 + 5*y^3*yi^2 + y^3*yi + 6*y^3 + y^2*yi^8 + 2*y^2*yi^7 + 2*y^2*yi^6 + 2*y^2*yi^5 + y^2*yi^4 + 5*y^2*yi^3 + 5*y^2*yi + 3*y^2 + y*yi^8 + 2*y*yi^7 + 2*y*yi^6 + 2*y*yi^5 + 4*y*yi^4 + y*yi^3 + 5*y*yi^2 + 2*y*yi + 7*y + yi^8 + 2*yi^7 + 3*yi^6 + 4*yi^5 + 3*yi^4 + 6*yi^3 + 3*yi^2 + 7*yi + 4) * hy

theorem triPoly_diag {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    triPoly x xi x xi * (x + xi) = x^9 + xi^9 := by
  unfold triPoly
  linear_combination (x^8 + 2*x^7 + 2*x^6 + 3*x^5 + 2*x^4 + 4*x^3 + 2*x^2 + 4*x + xi^8 + 2*xi^7 + 2*xi^6 + 3*xi^5 + 2*xi^4 + 4*xi^3 + 2*xi^2 + 4*xi + 2) * h2 + (x^7 + 2*x^6 + 3*x^5 + 2*x^4 + 5*x^3 + 4*x^2*xi + 2*x^2 + 4*x*xi^2 + 7*x + xi^7 + 2*xi^6 + 3*xi^5 + 2*xi^4 + 5*xi^3 + 2*xi^2 + 7*xi + 4) * hx

end Polys

section Field

variable {K : Type*} [Field K] [CharP K 2]

theorem ev_w (x y : K) : ev wOffsets x y = wPoly x x⁻¹ y y⁻¹ := by
  simp [ev, wOffsets, wPoly]
  ring

theorem ev_r90 (x y : K) : ev r90Offsets x y = x⁻¹ + x := by
  simp [ev, r90Offsets]

theorem pow_mod37 {X : K} (hX : X ^ 37 = 1) (n : ℕ) : X ^ n = X ^ (n % 37) := by
  conv_lhs => rw [← Nat.div_add_mod n 37, pow_add, pow_mul, hX, one_pow, one_mul]

/-- The shell with exponents reduced mod 37 (1/X = X^36). -/
def shNat (X Y : K) : K :=
  X^7*Y^5 + X^7*Y^32 + X^5*Y^7 + X^5*Y^30 + X^30*Y^5 + X^30*Y^32 + X^32*Y^7 + X^32*Y^30

theorem frob_term {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) (a b a' b' : ℕ)
    (ha : a * 2 ^ 9 % 37 = a') (hb : b * 2 ^ 9 % 37 = b') :
    (X ^ a * Y ^ b) ^ 2 ^ 9 = X ^ a' * Y ^ b' := by
  rw [mul_pow, ← pow_mul, ← pow_mul, pow_mod37 hX, pow_mod37 hY, ha, hb]

/-- **Half Frobenius.** 2^9 = -6 mod 37 permutes the shell: its value is fixed by x -> x^(2^9). -/
theorem sh_frob {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    shNat X Y ^ 2 ^ 9 = shNat X Y := by
  unfold shNat
  simp only [add_pow_char_pow]
  rw [frob_term hX hY 7 5 32 7 (by norm_num) (by norm_num),
    frob_term hX hY 7 32 32 30 (by norm_num) (by norm_num),
    frob_term hX hY 5 7 7 32 (by norm_num) (by norm_num),
    frob_term hX hY 5 30 7 5 (by norm_num) (by norm_num),
    frob_term hX hY 30 5 5 7 (by norm_num) (by norm_num),
    frob_term hX hY 30 32 5 30 (by norm_num) (by norm_num),
    frob_term hX hY 32 7 30 32 (by norm_num) (by norm_num),
    frob_term hX hY 32 30 30 5 (by norm_num) (by norm_num)]
  ring

theorem inv_eq_pow36 {X : K} (hX : X ^ 37 = 1) : X⁻¹ = X ^ 36 :=
  inv_eq_of_mul_eq_one_right (by rw [← pow_succ', hX])

theorem shPoly_eq {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    shPoly X X⁻¹ Y Y⁻¹ = shNat X Y := by
  unfold shPoly shNat
  rw [inv_eq_pow36 hX, inv_eq_pow36 hY]
  simp only [← pow_mul]
  rw [pow_mod37 hX (36 * 7), pow_mod37 hX (36 * 5), pow_mod37 hY (36 * 7), pow_mod37 hY (36 * 5)]

/-- V's shells with exponents reduced mod 37. -/
def svNat (X Y : K) : K :=
  X^7*Y^7 + X^7*Y^30 + X^5*Y^5 + X^5*Y^32 + X^30*Y^7 + X^30*Y^30 + X^32*Y^5 + X^32*Y^32

theorem sv_frob {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    svNat X Y ^ 2 ^ 9 = svNat X Y := by
  unfold svNat
  simp only [add_pow_char_pow]
  rw [frob_term hX hY 7 7 32 32 (by norm_num) (by norm_num),
    frob_term hX hY 7 30 32 5 (by norm_num) (by norm_num),
    frob_term hX hY 5 5 7 7 (by norm_num) (by norm_num),
    frob_term hX hY 5 32 7 30 (by norm_num) (by norm_num),
    frob_term hX hY 30 7 5 32 (by norm_num) (by norm_num),
    frob_term hX hY 30 30 5 5 (by norm_num) (by norm_num),
    frob_term hX hY 32 5 30 7 (by norm_num) (by norm_num),
    frob_term hX hY 32 32 30 30 (by norm_num) (by norm_num)]
  ring

theorem svPoly_eq {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    svPoly X X⁻¹ Y Y⁻¹ = svNat X Y := by
  unfold svPoly svNat
  rw [inv_eq_pow36 hX, inv_eq_pow36 hY]
  simp only [← pow_mul]
  rw [pow_mod37 hX (36 * 7), pow_mod37 hX (36 * 5), pow_mod37 hY (36 * 7), pow_mod37 hY (36 * 5)]

/-- The triangle's B with exponents reduced mod 37. -/
def tbNat (X Y : K) : K :=
  X^14*Y^12 + X^14*Y^2 + X^12*Y^14 + X^12*Y^10 + X^12*Y^2 + X^12*Y^35 + X^10*Y^12 + X^10*Y^35 + X^2*Y^14 + X^2*Y^12 + X^2*Y^25 + X^2*Y^27 + X^23*Y^25 + X^23*Y^35 + X^25*Y^2 + X^25*Y^23 + X^25*Y^27 + X^25*Y^35 + X^27*Y^2 + X^27*Y^25 + X^35*Y^12 + X^35*Y^10 + X^35*Y^23 + X^35*Y^25

theorem tb_frob {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    tbNat X Y ^ 2 ^ 9 = tbNat X Y := by
  unfold tbNat
  simp only [add_pow_char_pow]
  rw [frob_term hX hY 14 12 27 2 (by norm_num) (by norm_num),
    frob_term hX hY 14 2 27 25 (by norm_num) (by norm_num),
    frob_term hX hY 12 14 2 27 (by norm_num) (by norm_num),
    frob_term hX hY 12 10 2 14 (by norm_num) (by norm_num),
    frob_term hX hY 12 2 2 25 (by norm_num) (by norm_num),
    frob_term hX hY 12 35 2 12 (by norm_num) (by norm_num),
    frob_term hX hY 10 12 14 2 (by norm_num) (by norm_num),
    frob_term hX hY 10 35 14 12 (by norm_num) (by norm_num),
    frob_term hX hY 2 14 25 27 (by norm_num) (by norm_num),
    frob_term hX hY 2 12 25 2 (by norm_num) (by norm_num),
    frob_term hX hY 2 25 25 35 (by norm_num) (by norm_num),
    frob_term hX hY 2 27 25 23 (by norm_num) (by norm_num),
    frob_term hX hY 23 25 10 35 (by norm_num) (by norm_num),
    frob_term hX hY 23 35 10 12 (by norm_num) (by norm_num),
    frob_term hX hY 25 2 35 25 (by norm_num) (by norm_num),
    frob_term hX hY 25 23 35 10 (by norm_num) (by norm_num),
    frob_term hX hY 25 27 35 23 (by norm_num) (by norm_num),
    frob_term hX hY 25 35 35 12 (by norm_num) (by norm_num),
    frob_term hX hY 27 2 23 25 (by norm_num) (by norm_num),
    frob_term hX hY 27 25 23 35 (by norm_num) (by norm_num),
    frob_term hX hY 35 12 12 2 (by norm_num) (by norm_num),
    frob_term hX hY 35 10 12 14 (by norm_num) (by norm_num),
    frob_term hX hY 35 23 12 10 (by norm_num) (by norm_num),
    frob_term hX hY 35 25 12 35 (by norm_num) (by norm_num)]
  ring

theorem tbPoly_eq {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    tbPoly X X⁻¹ Y Y⁻¹ = tbNat X Y := by
  unfold tbPoly tbNat
  rw [inv_eq_pow36 hX, inv_eq_pow36 hY]
  simp only [← pow_mul]
  rw [pow_mod37 hX (36 * 2), pow_mod37 hX (36 * 10), pow_mod37 hX (36 * 12), pow_mod37 hX (36 * 14), pow_mod37 hY (36 * 2), pow_mod37 hY (36 * 10), pow_mod37 hY (36 * 12), pow_mod37 hY (36 * 14)]
  all_goals first | rfl | ring

theorem eq_one_of_add_inv {z : K} (hz : z ^ 37 = 1) (h : z + z⁻¹ = 0) : z = 1 := by
  have hz0 : z ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hz
  have h1 : z = z⁻¹ := by
    have := congrArg (· + z⁻¹) h
    simpa [CharTwo.add_self_eq_zero, add_assoc] using this
  have h2 : z ^ 2 = 1 := by
    rw [sq]
    nth_rewrite 2 [h1]
    exact mul_inv_cancel₀ hz0
  calc z = z * (z ^ 2) ^ 18 := by rw [h2, one_pow, mul_one]
    _ = z ^ 37 := by ring
    _ = 1 := hz

variable {P : ℕ}

/-- On the lines: (t + 1)^2 = t(z^3)/t(z) is a quotient of rule-90 values. -/
theorem line_val (hP : ∀ z : K, z ^ 37 = 1 → z + z⁻¹ = 0 ∨ (z + z⁻¹) ^ P = 1) {z : K}
    (hz : z ^ 37 = 1) : (z + z⁻¹ + 1) ^ 2 = 0 ∨ ((z + z⁻¹ + 1) ^ 2) ^ P = 1 := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  have hz0 : z ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hz
  have hid := line_identity h2 z z⁻¹ (mul_inv_cancel₀ hz0)
  rw [inv_pow] at hid
  have hz3 : (z ^ 3) ^ 37 = 1 := by rw [← pow_mul, mul_comm, pow_mul, hz, one_pow]
  rcases Nat.eq_zero_or_pos P with hP0 | hPpos
  · right; rw [hP0, pow_zero]
  rcases hP z hz with h0 | h1
  · right
    rw [eq_one_of_add_inv hz h0, inv_one, show (1 + 1 + 1 : K) = 1 by linear_combination h2]
    simp
  have hne : z + z⁻¹ ≠ 0 := by
    intro h
    rw [h, zero_pow hPpos.ne'] at h1
    exact zero_ne_one h1
  rcases hP (z ^ 3) hz3 with h3 | h3
  · left
    exact (mul_eq_zero.1 (hid.trans h3)).resolve_right hne
  · right
    have := congrArg (· ^ P) hid
    simp only [mul_pow, h1, mul_one] at this
    rw [this, h3]

theorem pow_of_line {w : K} (h : w = 0 ∨ w ^ P = 1) (e L : ℕ) (he : e ≠ 0) (hL : P ∣ L) :
    w ^ e = 0 ∨ (w ^ e) ^ L = 1 := by
  rcases h with h | h
  · left; rw [h, zero_pow he]
  · right
    obtain ⟨c, rfl⟩ := hL
    rw [← pow_mul, mul_comm e, pow_mul, pow_mul, h, one_pow, one_pow]

/-- The eigenvalue of W at (X^2, Y^2), X^37 = Y^37 = 1, has order dividing lcm(511, P), where
every rule-90 value z + 1/z (z^37 = 1) has order dividing P. -/
theorem w_val_sq (hP : ∀ z : K, z ^ 37 = 1 → z + z⁻¹ = 0 ∨ (z + z⁻¹) ^ P = 1) {X Y : K}
    (hX37 : X ^ 37 = 1) (hY37 : Y ^ 37 = 1) :
    ev wOffsets (X ^ 2) (Y ^ 2) = 0 ∨ ev wOffsets (X ^ 2) (Y ^ 2) ^ Nat.lcm 511 P = 1 := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  have hPL : P ∣ Nat.lcm 511 P := Nat.dvd_lcm_right 511 P
  have hX0 : X ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hX37
  have hY0 : Y ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hY37
  have hx : (X ^ 2) ^ 37 = 1 := by rw [← pow_mul, mul_comm, pow_mul, hX37, one_pow]
  have hy : (Y ^ 2) ^ 37 = 1 := by rw [← pow_mul, mul_comm, pow_mul, hY37, one_pow]
  have hx0 : X ^ 2 ≠ 0 := pow_ne_zero 2 hX0
  have hy0 : Y ^ 2 ≠ 0 := pow_ne_zero 2 hY0
  rw [ev_w]
  -- the lines
  by_cases n1 : X + X⁻¹ = 0
  · rw [eq_one_of_add_inv hX37 n1, one_pow, inv_one,
      wPoly_axisx h2 _ _ (mul_inv_cancel₀ hy0)]
    exact pow_of_line (line_val hP hy) 1 _ one_ne_zero hPL |>.imp (by simp) (by simp)
  by_cases n2 : Y + Y⁻¹ = 0
  · rw [eq_one_of_add_inv hY37 n2, one_pow, inv_one,
      wPoly_axisy h2 _ _ (mul_inv_cancel₀ hx0)]
    exact pow_of_line (line_val hP hx) 1 _ one_ne_zero hPL |>.imp (by simp) (by simp)
  have hXY37 : (X * Y) ^ 37 = 1 := by rw [mul_pow, hX37, hY37, one_mul]
  have hXY'37 : (X * Y⁻¹) ^ 37 = 1 := by rw [mul_pow, inv_pow, hX37, hY37, inv_one, one_mul]
  by_cases n3 : X * Y + (X * Y)⁻¹ = 0
  · have hxy : X ^ 2 * Y ^ 2 = 1 := by rw [← mul_pow, eq_one_of_add_inv hXY37 n3, one_pow]
    have hyx : Y ^ 2 = (X ^ 2)⁻¹ := eq_inv_of_mul_eq_one_right hxy
    rw [hyx, inv_inv, wPoly_anti h2 _ _ (mul_inv_cancel₀ hx0)]
    exact pow_of_line (line_val hP hx) 2 _ two_ne_zero hPL
  by_cases n4 : X * Y⁻¹ + (X * Y⁻¹)⁻¹ = 0
  · have hxy : X = Y := by
      have h := eq_one_of_add_inv hXY'37 n4
      calc X = X * Y⁻¹ * Y := by rw [mul_assoc, inv_mul_cancel₀ hY0, mul_one]
        _ = Y := by rw [h, one_mul]
    rw [hxy, wPoly_diag h2 _ _ (mul_inv_cancel₀ hy0)]
    exact pow_of_line (line_val hP hy) 2 _ two_ne_zero hPL
  -- off the lines
  have v1 := (hP X hX37).resolve_left n1
  have v2 := (hP Y hY37).resolve_left n2
  have v3 := (hP _ hXY37).resolve_left n3
  have v4 := (hP _ hXY'37).resolve_left n4
  have hid := w_identity h2 X X⁻¹ Y Y⁻¹ (mul_inv_cancel₀ hX0) (mul_inv_cancel₀ hY0)
  rw [inv_pow, inv_pow, shPoly_eq hX37 hY37] at hid
  have e3 : X * Y + X⁻¹ * Y⁻¹ = X * Y + (X * Y)⁻¹ := by rw [mul_inv]
  have e4 : X * Y⁻¹ + X⁻¹ * Y = X * Y⁻¹ + (X * Y⁻¹)⁻¹ := by rw [mul_inv, inv_inv]
  rw [e3, e4] at hid
  have hNP : ((X + X⁻¹) * (Y + Y⁻¹) * (X * Y + (X * Y)⁻¹) * (X * Y⁻¹ + (X * Y⁻¹)⁻¹)) ^ P = 1 := by
    rw [mul_pow, mul_pow, mul_pow, v1, v2, v3, v4]; norm_num
  have hN0 : (X + X⁻¹) * (Y + Y⁻¹) * (X * Y + (X * Y)⁻¹) * (X * Y⁻¹ + (X * Y⁻¹)⁻¹) ≠ 0 :=
    mul_ne_zero (mul_ne_zero (mul_ne_zero n1 n2) n3) n4
  have hS := eq_zero_or_pow_eq_one (by norm_num) (sh_frob hX37 hY37)
  rcases hS with hS | hS
  · left
    rw [hS] at hid
    exact (mul_eq_zero.1 hid).resolve_right hN0
  · right
    have hSL : shNat X Y ^ Nat.lcm 511 P = 1 := by
      obtain ⟨c, hc⟩ := Nat.dvd_lcm_left 511 P
      rw [hc, pow_mul]
      norm_num at hS
      rw [hS, one_pow]
    have hNL : ((X + X⁻¹) * (Y + Y⁻¹) * (X * Y + (X * Y)⁻¹) * (X * Y⁻¹ + (X * Y⁻¹)⁻¹)) ^
        Nat.lcm 511 P = 1 := by
      obtain ⟨c, hc⟩ := hPL
      rw [hc, pow_mul, hNP, one_pow]
    have := congrArg (· ^ Nat.lcm 511 P) hid
    simp only [mul_pow] at this hNL
    rw [hNL, mul_one, hSL] at this
    exact this

/-- The same at any x, y with x^37 = y^37 = 1 (x = (x^19)^2). -/
theorem w_val (hP : ∀ z : K, z ^ 37 = 1 → z + z⁻¹ = 0 ∨ (z + z⁻¹) ^ P = 1) {x y : K}
    (hx : x ^ 37 = 1) (hy : y ^ 37 = 1) :
    ev wOffsets x y = 0 ∨ ev wOffsets x y ^ Nat.lcm 511 P = 1 := by
  have sq : ∀ z : K, z ^ 37 = 1 → (z ^ 19) ^ 2 = z ∧ (z ^ 19) ^ 37 = 1 := fun z hz =>
    ⟨by rw [← pow_mul, show 19 * 2 = 37 + 1 by norm_num, pow_succ, hz, one_mul],
      by rw [← pow_mul, mul_comm, pow_mul, hz, one_pow]⟩
  have hx' := sq x hx
  have hy' := sq y hy
  have := w_val_sq hP hx'.2 hy'.2
  rwa [hx'.1, hy'.1] at this

theorem prod_val {u w : K} {L : ℕ} (hu : u = 0 ∨ u ^ L = 1) (hw : w = 0 ∨ w ^ L = 1) :
    u * w = 0 ∨ (u * w) ^ L = 1 := by
  rcases hu with hu | hu
  · left; rw [hu, zero_mul]
  rcases hw with hw | hw
  · left; rw [hw, mul_zero]
  · right; rw [mul_pow, hu, hw, one_mul]

theorem lift_val {u : K} (h : u = 0 ∨ u ^ P = 1) : u = 0 ∨ u ^ Nat.lcm 511 P = 1 := by
  have := pow_of_line h 1 _ one_ne_zero (Nat.dvd_lcm_right 511 P)
  simpa using this

theorem sq37 {X : K} (hX : X ^ 37 = 1) : (X ^ 2) ^ 37 = 1 := by
  rw [← pow_mul, mul_comm, pow_mul, hX, one_pow]

theorem ev_k8m8e4 {x y : K} (hx : x ≠ 0) (hy : y ≠ 0) :
    ev k8m8e4Offsets x y = (x + x⁻¹) * (y + y⁻¹) * ev wOffsets x y := by
  rw [ev_w, ← k8m8e4_poly two_eq_zero_of_charTwo x x⁻¹ y y⁻¹ (mul_inv_cancel₀ hx)
    (mul_inv_cancel₀ hy)]
  simp [ev, k8m8e4Offsets]
  ring

theorem ev_c4l8m8 {x y : K} (hx : x ≠ 0) (hy : y ≠ 0) :
    ev c4l8m8Offsets x y = (x + x⁻¹ + y + y⁻¹) * ev wOffsets x y := by
  rw [ev_w, ← c4l8m8_poly two_eq_zero_of_charTwo x x⁻¹ y y⁻¹ (mul_inv_cancel₀ hx)
    (mul_inv_cancel₀ hy)]
  simp [ev, c4l8m8Offsets]
  ring

theorem ev_a4b4c4l8e4self {x y : K} (hx : x ≠ 0) (hy : y ≠ 0) :
    ev a4b4c4l8e4selfOffsets x y = (x + x⁻¹ + 1) * (y + y⁻¹ + 1) * ev wOffsets x y := by
  rw [ev_w, ← a4b4c4l8e4self_poly two_eq_zero_of_charTwo x x⁻¹ y y⁻¹ (mul_inv_cancel₀ hx)
    (mul_inv_cancel₀ hy)]
  simp [ev, a4b4c4l8e4selfOffsets]
  ring

theorem ev_tri (x y : K) : ev triOffsets x y = triPoly x x⁻¹ y y⁻¹ := by
  simp [ev, triOffsets, triPoly]
  ring

theorem ev_v (x y : K) : ev vOffsets x y = vPoly x x⁻¹ y y⁻¹ := by
  simp [ev, vOffsets, vPoly]
  ring

section Vals

variable (hP : ∀ z : K, z ^ 37 = 1 → z + z⁻¹ = 0 ∨ (z + z⁻¹) ^ P = 1)
include hP

theorem k8m8e4_val_sq {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    ev k8m8e4Offsets (X ^ 2) (Y ^ 2) = 0 ∨
      ev k8m8e4Offsets (X ^ 2) (Y ^ 2) ^ Nat.lcm 511 P = 1 := by
  rw [ev_k8m8e4 (pow_ne_zero 2 (ne_zero_of_pow_eq_one (m := 37) hX))
    (pow_ne_zero 2 (ne_zero_of_pow_eq_one (m := 37) hY))]
  exact prod_val (prod_val (lift_val (hP _ (sq37 hX))) (lift_val (hP _ (sq37 hY))))
    (w_val_sq hP hX hY)

theorem c4l8m8_val_sq {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    ev c4l8m8Offsets (X ^ 2) (Y ^ 2) = 0 ∨
      ev c4l8m8Offsets (X ^ 2) (Y ^ 2) ^ Nat.lcm 511 P = 1 := by
  have hX0 : X ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hX
  have hY0 : Y ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hY
  rw [ev_c4l8m8 (pow_ne_zero 2 hX0) (pow_ne_zero 2 hY0)]
  have e : X ^ 2 + (X ^ 2)⁻¹ + Y ^ 2 + (Y ^ 2)⁻¹ =
      (X * Y + (X * Y)⁻¹) * (X * Y⁻¹ + (X * Y⁻¹)⁻¹) := by
    field_simp
    ring
  have hXY37 : (X * Y) ^ 37 = 1 := by rw [mul_pow, hX, hY, one_mul]
  have hXY'37 : (X * Y⁻¹) ^ 37 = 1 := by rw [mul_pow, inv_pow, hX, hY, inv_one, one_mul]
  rw [e]
  exact prod_val (prod_val (lift_val (hP _ hXY37)) (lift_val (hP _ hXY'37))) (w_val_sq hP hX hY)

theorem a4b4c4l8e4self_val_sq {X Y : K} (hX : X ^ 37 = 1) (hY : Y ^ 37 = 1) :
    ev a4b4c4l8e4selfOffsets (X ^ 2) (Y ^ 2) = 0 ∨
      ev a4b4c4l8e4selfOffsets (X ^ 2) (Y ^ 2) ^ Nat.lcm 511 P = 1 := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  have hX0 : X ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hX
  have hY0 : Y ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hY
  rw [ev_a4b4c4l8e4self (pow_ne_zero 2 hX0) (pow_ne_zero 2 hY0)]
  have e : ∀ Z : K, Z ≠ 0 → Z ^ 2 + (Z ^ 2)⁻¹ + 1 = (Z + Z⁻¹ + 1) ^ 2 := fun Z hZ => by
    rw [← inv_pow]
    linear_combination (-Z * Z⁻¹ - Z - Z⁻¹) * h2
  rw [e X hX0, e Y hY0]
  exact prod_val (prod_val (lift_val (line_val hP hX)) (lift_val (line_val hP hY)))
    (w_val_sq hP hX hY)

theorem v_val_sq {X Y : K} (hX37 : X ^ 37 = 1) (hY37 : Y ^ 37 = 1) :
    ev vOffsets (X ^ 2) (Y ^ 2) = 0 ∨ ev vOffsets (X ^ 2) (Y ^ 2) ^ Nat.lcm 511 P = 1 := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  have hX0 : X ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hX37
  have hY0 : Y ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hY37
  have hx0 : X ^ 2 ≠ 0 := pow_ne_zero 2 hX0
  have hy0 : Y ^ 2 ≠ 0 := pow_ne_zero 2 hY0
  rw [ev_v]
  by_cases n1 : X + X⁻¹ = 0
  · rw [eq_one_of_add_inv hX37 n1, one_pow, inv_one, vPoly_axisx h2 _ _ (mul_inv_cancel₀ hy0)]
    exact prod_val (lift_val (hP _ (sq37 hY37))) (lift_val (line_val hP (sq37 hY37)))
  by_cases n2 : Y + Y⁻¹ = 0
  · rw [eq_one_of_add_inv hY37 n2, one_pow, inv_one, vPoly_axisy h2 _ _ (mul_inv_cancel₀ hx0)]
    exact prod_val (lift_val (hP _ (sq37 hX37))) (lift_val (line_val hP (sq37 hX37)))
  have v1 := (hP X hX37).resolve_left n1
  have v2 := (hP Y hY37).resolve_left n2
  have hid := v_identity h2 X X⁻¹ Y Y⁻¹ (mul_inv_cancel₀ hX0) (mul_inv_cancel₀ hY0)
  rw [inv_pow, inv_pow, svPoly_eq hX37 hY37] at hid
  have hN0 : (X + X⁻¹) * (Y + Y⁻¹) ≠ 0 := mul_ne_zero n1 n2
  rcases eq_zero_or_pow_eq_one (by norm_num) (sv_frob hX37 hY37) with hS | hS
  · left
    rw [hS] at hid
    exact (mul_eq_zero.1 hid).resolve_right hN0
  · right
    have hSL : svNat X Y ^ Nat.lcm 511 P = 1 := by
      obtain ⟨c, hc⟩ := Nat.dvd_lcm_left 511 P
      rw [hc, pow_mul]
      norm_num at hS
      rw [hS, one_pow]
    have hNL : ((X + X⁻¹) * (Y + Y⁻¹)) ^ Nat.lcm 511 P = 1 := by
      obtain ⟨c, hc⟩ := Nat.dvd_lcm_right 511 P
      rw [hc, pow_mul, mul_pow, v1, v2, one_mul, one_pow]
    have := congrArg (· ^ Nat.lcm 511 P) hid
    simp only [mul_pow] at this hNL
    rw [hNL, mul_one, hSL] at this
    exact this


theorem ratio_val {z w : K} (hz : z ^ 37 = 1) (ht : z + z⁻¹ ≠ 0) (n : ℕ)
    (hid : w * (z + z⁻¹) = z ^ n + (z⁻¹) ^ n) : w = 0 ∨ w ^ P = 1 := by
  have hzn : (z ^ n) ^ 37 = 1 := by rw [← pow_mul, mul_comm, pow_mul, hz, one_pow]
  have h1 := (hP z hz).resolve_left ht
  rw [inv_pow] at hid
  rcases hP (z ^ n) hzn with h3 | h3
  · left
    exact (mul_eq_zero.1 (hid.trans h3)).resolve_right ht
  · right
    have := congrArg (· ^ P) hid
    simp only [mul_pow, h1, mul_one] at this
    rw [this, h3]

theorem tri_val_sq {X Y : K} (hX37 : X ^ 37 = 1) (hY37 : Y ^ 37 = 1) :
    ev triOffsets (X ^ 2) (Y ^ 2) = 0 ∨ ev triOffsets (X ^ 2) (Y ^ 2) ^ Nat.lcm 511 P = 1 := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  have hX0 : X ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hX37
  have hY0 : Y ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hY37
  have hx0 : X ^ 2 ≠ 0 := pow_ne_zero 2 hX0
  have hy0 : Y ^ 2 ≠ 0 := pow_ne_zero 2 hY0
  have sqt : ∀ Z : K, Z ≠ 0 → Z ^ 2 + (Z ^ 2)⁻¹ = (Z + Z⁻¹) ^ 2 := fun Z hZ => by
    rw [← inv_pow]
    linear_combination (-Z * Z⁻¹) * h2 + (-2 : K) * 0 * Z
  rw [ev_tri]
  by_cases n1 : X + X⁻¹ = 0
  · rw [eq_one_of_add_inv hX37 n1, one_pow, inv_one, triPoly_x1 h2 _ _ (mul_inv_cancel₀ hy0)]
    exact pow_of_line (line_val hP (sq37 hY37)) 2 _ two_ne_zero (Nat.dvd_lcm_right 511 P)
  by_cases n2 : Y + Y⁻¹ = 0
  · rw [eq_one_of_add_inv hY37 n2, one_pow, inv_one, triPoly_y1 h2 _ _ (mul_inv_cancel₀ hx0)]
    exact pow_of_line (line_val hP (sq37 hX37)) 2 _ two_ne_zero (Nat.dvd_lcm_right 511 P)
  have tx : X ^ 2 + (X ^ 2)⁻¹ ≠ 0 := by rw [sqt X hX0]; exact pow_ne_zero 2 n1
  have ty : Y ^ 2 + (Y ^ 2)⁻¹ ≠ 0 := by rw [sqt Y hY0]; exact pow_ne_zero 2 n2
  have r37 : ∀ a b : ℕ, (X ^ a * Y ^ b) ^ 37 = 1 := fun a b => by
    rw [mul_pow, ← pow_mul, ← pow_mul, mul_comm a, mul_comm b, pow_mul, pow_mul, hX37, hY37,
      one_pow, one_pow, one_mul]
  have hXY'37 : (X * Y⁻¹) ^ 37 = 1 := by rw [mul_pow, inv_pow, hX37, hY37, inv_one, one_mul]
  by_cases n3 : X * Y + (X * Y)⁻¹ = 0
  · have h := eq_one_of_add_inv (by simpa using r37 1 1) n3
    have hyx : Y ^ 2 = (X ^ 2)⁻¹ :=
      eq_inv_of_mul_eq_one_right (by rw [← mul_pow, h, one_pow])
    rw [hyx, inv_inv, triPoly_anti h2 _ _ (mul_inv_cancel₀ hx0)]
    exact pow_of_line (line_val hP (sq37 hX37)) 2 _ two_ne_zero (Nat.dvd_lcm_right 511 P)
  by_cases n4 : X ^ 2 * Y + (X ^ 2 * Y)⁻¹ = 0
  · have h := eq_one_of_add_inv (by simpa using r37 2 1) n4
    have hY' : Y = (X ^ 2)⁻¹ := eq_inv_of_mul_eq_one_right h
    rw [hY', show (((X ^ 2)⁻¹) ^ 2)⁻¹ = (X ^ 2) ^ 2 by rw [inv_pow, inv_inv]]
    exact lift_val (ratio_val hP (sq37 hX37) tx 9
      (triPoly_x2y h2 (X ^ 2) (X ^ 2)⁻¹ (mul_inv_cancel₀ hx0)))
  by_cases n5 : X * Y ^ 2 + (X * Y ^ 2)⁻¹ = 0
  · have h := eq_one_of_add_inv (by simpa using r37 1 2) n5
    have hX' : X = (Y ^ 2)⁻¹ := eq_inv_of_mul_eq_one_left h
    rw [hX', show (((Y ^ 2)⁻¹) ^ 2)⁻¹ = (Y ^ 2) ^ 2 by rw [inv_pow, inv_inv]]
    exact lift_val (ratio_val hP (sq37 hY37) ty 9
      (triPoly_xy2 h2 (Y ^ 2) (Y ^ 2)⁻¹ (mul_inv_cancel₀ hy0)))
  by_cases n6 : X * Y⁻¹ + (X * Y⁻¹)⁻¹ = 0
  · have hxy : X = Y := by
      have h := eq_one_of_add_inv hXY'37 n6
      calc X = X * Y⁻¹ * Y := by rw [mul_assoc, inv_mul_cancel₀ hY0, mul_one]
        _ = Y := by rw [h, one_mul]
    rw [← hxy]
    exact lift_val (ratio_val hP (sq37 hX37) tx 9
      (triPoly_diag h2 (X ^ 2) (X ^ 2)⁻¹ (mul_inv_cancel₀ hx0)))
  -- off the lines
  have v1 := (hP X hX37).resolve_left n1
  have v2 := (hP Y hY37).resolve_left n2
  have v3 := (hP _ (by simpa using r37 1 1)).resolve_left n3
  have v4 := (hP _ (by simpa using r37 2 1)).resolve_left n4
  have v5 := (hP _ (by simpa using r37 1 2)).resolve_left n5
  have v6 := (hP _ hXY'37).resolve_left n6
  have hid := tri_identity h2 X X⁻¹ Y Y⁻¹ (mul_inv_cancel₀ hX0) (mul_inv_cancel₀ hY0)
  rw [inv_pow, inv_pow, tbPoly_eq hX37 hY37] at hid
  have e3 : X * Y + X⁻¹ * Y⁻¹ = X * Y + (X * Y)⁻¹ := by rw [mul_inv]
  have e4 : X ^ 2 * Y + (X ^ 2)⁻¹ * Y⁻¹ = X ^ 2 * Y + (X ^ 2 * Y)⁻¹ := by rw [mul_inv]
  have e5 : X * Y ^ 2 + X⁻¹ * (Y ^ 2)⁻¹ = X * Y ^ 2 + (X * Y ^ 2)⁻¹ := by rw [mul_inv]
  have e6 : X * Y⁻¹ + X⁻¹ * Y = X * Y⁻¹ + (X * Y⁻¹)⁻¹ := by rw [mul_inv, inv_inv]
  rw [e3, e4, e5, e6] at hid
  set N := (X + X⁻¹) * (Y + Y⁻¹) * (X * Y + (X * Y)⁻¹) * (X ^ 2 * Y + (X ^ 2 * Y)⁻¹) *
    (X * Y ^ 2 + (X * Y ^ 2)⁻¹) * (X * Y⁻¹ + (X * Y⁻¹)⁻¹) with hN
  have hN0 : N ≠ 0 := by
    rw [hN]
    exact mul_ne_zero (mul_ne_zero (mul_ne_zero (mul_ne_zero (mul_ne_zero n1 n2) n3) n4) n5) n6
  rcases eq_zero_or_pow_eq_one (by norm_num) (tb_frob hX37 hY37) with hS | hS
  · left
    rw [hS] at hid
    exact (mul_eq_zero.1 hid).resolve_right hN0
  · right
    have hSL : tbNat X Y ^ Nat.lcm 511 P = 1 := by
      obtain ⟨c, hc⟩ := Nat.dvd_lcm_left 511 P
      rw [hc, pow_mul]
      norm_num at hS
      rw [hS, one_pow]
    have hNP : N ^ P = 1 := by
      rw [hN, mul_pow, mul_pow, mul_pow, mul_pow, mul_pow, v1, v2, v3, v4, v5, v6]
      norm_num
    have hNL : N ^ Nat.lcm 511 P = 1 := by
      obtain ⟨c, hc⟩ := Nat.dvd_lcm_right 511 P
      rw [hc, pow_mul, hNP, one_pow]
    have := congrArg (· ^ Nat.lcm 511 P) hid
    simp only [mul_pow] at this
    rw [hNL, mul_one, hSL] at this
    exact this

end Vals

/-- From the eigenvalues at squares to the period: every eigenvalue of D at 37 is 0 or has order
dividing lcm(511, P), P the period of rule 90 at 37. -/
theorem period_dvd_of_val (D : Finset (ℤ × ℤ))
    (hv : ∀ P : ℕ, (∀ z : AlgebraicClosure (ZMod 2), z ^ 37 = 1 → z + z⁻¹ = 0 ∨ (z + z⁻¹) ^ P = 1) →
      ∀ X Y : AlgebraicClosure (ZMod 2), X ^ 37 = 1 → Y ^ 37 = 1 →
        ev D (X ^ 2) (Y ^ 2) = 0 ∨ ev D (X ^ 2) (Y ^ 2) ^ Nat.lcm 511 P = 1) :
    period 37 D ∣ Nat.lcm 511 (period 37 r90Offsets) := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot (m := 37) ⟨18, rfl⟩
  set P := period 37 r90Offsets
  have h90 := (isPeriod_iff hζ r90Offsets P).1 ((isPeriod_iff_period_dvd 37 r90Offsets P).2 dvd_rfl)
  have hP : ∀ z : AlgebraicClosure (ZMod 2), z ^ 37 = 1 → z + z⁻¹ = 0 ∨ (z + z⁻¹) ^ P = 1 := by
    intro z hz
    obtain ⟨i, hi, rfl⟩ := hζ.eq_pow_of_pow_eq_one hz
    have := h90 i hi 0 (by norm_num)
    rw [lam_eq_ev hζ.pow_eq_one, ev_r90, inv_inv] at this
    exact this
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
  have := hv P hP _ _ hx.2 hy.2
  rwa [hx.1, hy.1] at this

/-- **Theorem.** On the 37 x 37 torus, the period of A4 + K8 + B4 + self divides
lcm(511, period of rule 90). (The census has rule 90's period 87381 = (2^18 - 1)/3 at 37, and
511 divides 87381: so every eigenvalue of W is a cube in F(2^18).) -/
theorem period_w_dvd : period 37 wOffsets ∣ Nat.lcm 511 (period 37 r90Offsets) :=
  period_dvd_of_val _ fun _ hP _ _ hX hY => w_val_sq hP hX hY

/-- The same for K8 + M8 + E4 = ab W. -/
theorem period_k8m8e4_dvd : period 37 k8m8e4Offsets ∣ Nat.lcm 511 (period 37 r90Offsets) :=
  period_dvd_of_val _ fun _ hP _ _ hX hY => k8m8e4_val_sq hP hX hY

/-- The same for C4 + L8 + M8 = (a + b) W. -/
theorem period_c4l8m8_dvd : period 37 c4l8m8Offsets ∣ Nat.lcm 511 (period 37 r90Offsets) :=
  period_dvd_of_val _ fun _ hP _ _ hX hY => c4l8m8_val_sq hP hX hY

/-- The same for A4 + B4 + C4 + L8 + E4 + self = (a + 1)(b + 1) W. -/
theorem period_a4b4c4l8e4self_dvd :
    period 37 a4b4c4l8e4selfOffsets ∣ Nat.lcm 511 (period 37 r90Offsets) :=
  period_dvd_of_val _ fun _ hP _ _ hX hY => a4b4c4l8e4self_val_sq hP hX hY

/-- The same for the triangle rule VS + T9 + T13 + self (its plane rule s on the 37-torus). -/
theorem period_tri_dvd : period 37 triOffsets ∣ Nat.lcm 511 (period 37 r90Offsets) :=
  period_dvd_of_val _ fun _ hP _ _ hX hY => tri_val_sq hP hX hY

/-- The same for C4 + L8 + M8 + E4 (V(x^2, y^2) t(x) t(y) = Sh(7,7) + Sh(5,5)). -/
theorem period_v_dvd : period 37 vOffsets ∣ Nat.lcm 511 (period 37 r90Offsets) :=
  period_dvd_of_val _ fun _ hP _ _ hX hY => v_val_sq hP hX hY


/-! ### Rule 90 at 37: every t = z + 1/z is a cube of F(2^18)

Phi_37 is irreducible over GF(2) (2 is a primitive root mod 37), so t generates F(2^18) =
GF(2)[t]/Psi_37 with Psi_37(z + 1/z) = z^-18 Phi_37(z). The certificate: an explicit cube root
v(t) of t there; v(t) is fixed by the 2^18-th power because t is, so
t^87381 = v(t)^(2^18 - 1) = 1. -/

/-- Psi_37, the minimal polynomial of z + 1/z over GF(2). -/
def psi37 {R : Type*} [CommRing R] (t : R) : R :=
  t^18 + t^17 + t^16 + t^13 + t^12 + t^10 + t^9 + t^8 + t^2 + t + 1

/-- A cube root of t modulo Psi_37. -/
def v37 {R : Type*} [CommRing R] (t : R) : R :=
  t^15 + t^13 + t^12 + t^11 + t^9 + t^7 + t^6 + t

theorem psi37_identity {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (x xi : R) (hx : x * xi = 1) :
    psi37 (x + xi) * x ^ 18 = ∑ i ∈ Finset.range 37, x ^ i := by
  simp only [Finset.sum_range_succ, Finset.sum_range_zero, psi37]
  linear_combination (9*x^34 + 8*x^33 + 84*x^32 + 68*x^31 + 468*x^30 + 346*x^29 + 1816*x^28 + 1229*x^27 + 5232*x^26 + 3241*x^25 + 11602*x^24 + 6563*x^23 + 20237*x^22 + 10409*x^21 + 28128*x^20 + 13076*x^19 + 31369*x^18 + 13076*x^17 + 28128*x^16 + 10409*x^15 + 20237*x^14 + 6563*x^13 + 11602*x^12 + 3241*x^11 + 5232*x^10 + 1229*x^9 + 1816*x^8 + 346*x^7 + 468*x^6 + 68*x^5 + 84*x^4 + 8*x^3 + 9*x^2) * h2 + (18*x^34 + 153*x^33*xi + 17*x^33 + 816*x^32*xi^2 + 136*x^32*xi + 169*x^32 + 3060*x^31*xi^3 + 680*x^31*xi^2 + 936*x^31*xi + 136*x^31 + 8568*x^30*xi^4 + 2380*x^30*xi^3 + 3620*x^30*xi^2 + 680*x^30*xi + 936*x^30 + 18564*x^29*xi^5 + 6188*x^29*xi^4 + 10388*x^29*xi^3 + 2380*x^29*xi^2 + 3620*x^29*xi + 693*x^29 + 31824*x^28*xi^6 + 12376*x^28*xi^5 + 22932*x^28*xi^4 + 6188*x^28*xi^3 + 10388*x^28*xi^2 + 2458*x^28*xi + 3632*x^28 + 43758*x^27*xi^7 + 19448*x^27*xi^6 + 39832*x^27*xi^5 + 12376*x^27*xi^4 + 22932*x^27*xi^3 + 6474*x^27*xi^2 + 10454*x^27*xi + 2458*x^27 + 48620*x^26*xi^8 + 24310*x^26*xi^7 + 55198*x^26*xi^6 + 19448*x^26*xi^5 + 39832*x^26*xi^4 + 13091*x^26*xi^3 + 23152*x^26*xi^2 + 6474*x^26*xi + 10464*x^26 + 43758*x^25*xi^9 + 24310*x^25*xi^8 + 61490*x^25*xi^7 + 24310*x^25*xi^6 + 55198*x^25*xi^5 + 20735*x^25*xi^4 + 40327*x^25*xi^3 + 13091*x^25*xi^2 + 23197*x^25*xi + 6483*x^25 + 31824*x^24*xi^10 + 19448*x^24*xi^9 + 55198*x^24*xi^8 + 24310*x^24*xi^7 + 61490*x^24*xi^6 + 26026*x^24*xi^5 + 55990*x^24*xi^4 + 20735*x^24*xi^3 + 40447*x^24*xi^2 + 13127*x^24*xi + 23205*x^24 + 18564*x^23*xi^11 + 12376*x^23*xi^10 + 39832*x^23*xi^9 + 19448*x^23*xi^8 + 55198*x^23*xi^7 + 26026*x^23*xi^6 + 62414*x^23*xi^5 + 26026*x^23*xi^4 + 56200*x^23*xi^3 + 20819*x^23*xi^2 + 40475*x^23*xi + 13127*x^23 + 8568*x^22*xi^12 + 6188*x^22*xi^11 + 22932*x^22*xi^10 + 12376*x^22*xi^9 + 39832*x^22*xi^8 + 20735*x^22*xi^7 + 55990*x^22*xi^6 + 26026*x^22*xi^5 + 62666*x^22*xi^4 + 26152*x^22*xi^3 + 56256*x^22*xi^2 + 20819*x^22*xi + 40475*x^22 + 3060*x^21*xi^13 + 2380*x^21*xi^12 + 10388*x^21*xi^11 + 6188*x^21*xi^10 + 22932*x^21*xi^9 + 13091*x^21*xi^8 + 40327*x^21*xi^7 + 20735*x^21*xi^6 + 56200*x^21*xi^5 + 26152*x^21*xi^4 + 62736*x^21*xi^3 + 26152*x^21*xi^2 + 56256*x^21*xi + 20819*x^21 + 816*x^20*xi^14 + 680*x^20*xi^13 + 3620*x^20*xi^12 + 2380*x^20*xi^11 + 10388*x^20*xi^10 + 6474*x^20*xi^9 + 23152*x^20*xi^8 + 13091*x^20*xi^7 + 40447*x^20*xi^6 + 20819*x^20*xi^5 + 56256*x^20*xi^4 + 26152*x^20*xi^3 + 62736*x^20*xi^2 + 26152*x^20*xi + 56256*x^20 + 153*x^19*xi^15 + 136*x^19*xi^14 + 936*x^19*xi^13 + 680*x^19*xi^12 + 3620*x^19*xi^11 + 2458*x^19*xi^10 + 10454*x^19*xi^9 + 6474*x^19*xi^8 + 23197*x^19*xi^7 + 13127*x^19*xi^6 + 40475*x^19*xi^5 + 20819*x^19*xi^4 + 56256*x^19*xi^3 + 26152*x^19*xi^2 + 62736*x^19*xi + 26152*x^19 + 18*x^18*xi^16 + 17*x^18*xi^15 + 169*x^18*xi^14 + 136*x^18*xi^13 + 936*x^18*xi^12 + 693*x^18*xi^11 + 3632*x^18*xi^10 + 2458*x^18*xi^9 + 10464*x^18*xi^8 + 6483*x^18*xi^7 + 23205*x^18*xi^6 + 13127*x^18*xi^5 + 40475*x^18*xi^4 + 20819*x^18*xi^3 + 56256*x^18*xi^2 + 26152*x^18*xi + 62738*x^18 + x^17*xi^17 + x^17*xi^16 + 19*x^17*xi^15 + 17*x^17*xi^14 + 169*x^17*xi^13 + 137*x^17*xi^12 + 937*x^17*xi^11 + 693*x^17*xi^10 + 3633*x^17*xi^9 + 2459*x^17*xi^8 + 10465*x^17*xi^7 + 6483*x^17*xi^6 + 23205*x^17*xi^5 + 13127*x^17*xi^4 + 40475*x^17*xi^3 + 20819*x^17*xi^2 + 56257*x^17*xi + 26153*x^17 + x^16*xi^16 + x^16*xi^15 + 19*x^16*xi^14 + 17*x^16*xi^13 + 169*x^16*xi^12 + 137*x^16*xi^11 + 937*x^16*xi^10 + 693*x^16*xi^9 + 3633*x^16*xi^8 + 2459*x^16*xi^7 + 10465*x^16*xi^6 + 6483*x^16*xi^5 + 23205*x^16*xi^4 + 13127*x^16*xi^3 + 40475*x^16*xi^2 + 20819*x^16*xi + 56257*x^16 + x^15*xi^15 + x^15*xi^14 + 19*x^15*xi^13 + 17*x^15*xi^12 + 169*x^15*xi^11 + 137*x^15*xi^10 + 937*x^15*xi^9 + 693*x^15*xi^8 + 3633*x^15*xi^7 + 2459*x^15*xi^6 + 10465*x^15*xi^5 + 6483*x^15*xi^4 + 23205*x^15*xi^3 + 13127*x^15*xi^2 + 40475*x^15*xi + 20819*x^15 + x^14*xi^14 + x^14*xi^13 + 19*x^14*xi^12 + 17*x^14*xi^11 + 169*x^14*xi^10 + 137*x^14*xi^9 + 937*x^14*xi^8 + 693*x^14*xi^7 + 3633*x^14*xi^6 + 2459*x^14*xi^5 + 10465*x^14*xi^4 + 6483*x^14*xi^3 + 23205*x^14*xi^2 + 13127*x^14*xi + 40475*x^14 + x^13*xi^13 + x^13*xi^12 + 19*x^13*xi^11 + 17*x^13*xi^10 + 169*x^13*xi^9 + 137*x^13*xi^8 + 937*x^13*xi^7 + 693*x^13*xi^6 + 3633*x^13*xi^5 + 2459*x^13*xi^4 + 10465*x^13*xi^3 + 6483*x^13*xi^2 + 23205*x^13*xi + 13127*x^13 + x^12*xi^12 + x^12*xi^11 + 19*x^12*xi^10 + 17*x^12*xi^9 + 169*x^12*xi^8 + 137*x^12*xi^7 + 937*x^12*xi^6 + 693*x^12*xi^5 + 3633*x^12*xi^4 + 2459*x^12*xi^3 + 10465*x^12*xi^2 + 6483*x^12*xi + 23205*x^12 + x^11*xi^11 + x^11*xi^10 + 19*x^11*xi^9 + 17*x^11*xi^8 + 169*x^11*xi^7 + 137*x^11*xi^6 + 937*x^11*xi^5 + 693*x^11*xi^4 + 3633*x^11*xi^3 + 2459*x^11*xi^2 + 10465*x^11*xi + 6483*x^11 + x^10*xi^10 + x^10*xi^9 + 19*x^10*xi^8 + 17*x^10*xi^7 + 169*x^10*xi^6 + 137*x^10*xi^5 + 937*x^10*xi^4 + 693*x^10*xi^3 + 3633*x^10*xi^2 + 2459*x^10*xi + 10465*x^10 + x^9*xi^9 + x^9*xi^8 + 19*x^9*xi^7 + 17*x^9*xi^6 + 169*x^9*xi^5 + 137*x^9*xi^4 + 937*x^9*xi^3 + 693*x^9*xi^2 + 3633*x^9*xi + 2459*x^9 + x^8*xi^8 + x^8*xi^7 + 19*x^8*xi^6 + 17*x^8*xi^5 + 169*x^8*xi^4 + 137*x^8*xi^3 + 937*x^8*xi^2 + 693*x^8*xi + 3633*x^8 + x^7*xi^7 + x^7*xi^6 + 19*x^7*xi^5 + 17*x^7*xi^4 + 169*x^7*xi^3 + 137*x^7*xi^2 + 937*x^7*xi + 693*x^7 + x^6*xi^6 + x^6*xi^5 + 19*x^6*xi^4 + 17*x^6*xi^3 + 169*x^6*xi^2 + 137*x^6*xi + 937*x^6 + x^5*xi^5 + x^5*xi^4 + 19*x^5*xi^3 + 17*x^5*xi^2 + 169*x^5*xi + 137*x^5 + x^4*xi^4 + x^4*xi^3 + 19*x^4*xi^2 + 17*x^4*xi + 169*x^4 + x^3*xi^3 + x^3*xi^2 + 19*x^3*xi + 17*x^3 + x^2*xi^2 + x^2*xi + 19*x^2 + x*xi + x + 1) * hx

theorem cube37 {R : Type*} [CommRing R] (h2 : (2 : R) = 0) (t : R) (hpsi : psi37 t = 0) :
    v37 t ^ 3 = t := by
  unfold psi37 at hpsi
  unfold v37
  linear_combination (t^27 + t^26 + t^25 + t^24 + t^21 + t^18 + t^17 + t^16 + t^15 + t^13 + t^6 + t^5 + t^3 + t^2 + t) * hpsi + (-t^44 + 2*t^41 + 2*t^40 + 5*t^39 + 3*t^38 + 7*t^37 + 6*t^36 + 8*t^35 + 7*t^34 + 11*t^33 + 9*t^32 + 13*t^31 + 10*t^30 + 11*t^29 + 11*t^28 + 11*t^27 + 7*t^26 + 12*t^25 + 7*t^24 + 8*t^23 + 7*t^22 + 6*t^21 + 6*t^20 + 6*t^19 + 2*t^17 + t^16 + 2*t^14 + t^13 - t^12 - t^10 + t^9 + t^8 - t^7 - t^6 - t^5 - t^4 - t^3 - t^2 - t) * h2

theorem psi37_zero {z : K} (hz : z ^ 37 = 1) (hz1 : z ≠ 1) : psi37 (z + z⁻¹) = 0 := by
  have hz0 : z ≠ 0 := ne_zero_of_pow_eq_one (m := 37) hz
  have hs : ∑ i ∈ Finset.range 37, z ^ i = 0 := by
    have h := geom_sum_mul z 37
    rw [hz, sub_self] at h
    exact (mul_eq_zero.1 h).resolve_right (sub_ne_zero.2 hz1)
  have h := psi37_identity two_eq_zero_of_charTwo z z⁻¹ (mul_inv_cancel₀ hz0)
  rw [hs] at h
  exact (mul_eq_zero.1 h).resolve_right (pow_ne_zero _ hz0)

theorem t_frob {z : K} (hz : z ^ 37 = 1) : (z + z⁻¹) ^ 2 ^ 18 = z + z⁻¹ := by
  rw [inv_eq_pow36 hz, add_pow_char_pow, ← pow_mul, pow_mod37 hz (2 ^ 18),
    pow_mod37 hz (36 * 2 ^ 18), show 2 ^ 18 % 37 = 36 by norm_num,
    show 36 * 2 ^ 18 % 37 = 1 by norm_num, pow_one, add_comm]

theorem v37_frob {t : K} (ht : t ^ 2 ^ 18 = t) : v37 t ^ 2 ^ 18 = v37 t := by
  have hk : ∀ k : ℕ, (t ^ k) ^ 2 ^ 18 = t ^ k := fun k => by
    rw [← pow_mul, mul_comm, pow_mul, ht]
  unfold v37
  simp only [add_pow_char_pow, hk, ht]

/-- **Rule 90 at 37.** Every z + 1/z with z^37 = 1 is 0 or has order dividing 87381. -/
theorem r90_val {z : K} (hz : z ^ 37 = 1) : z + z⁻¹ = 0 ∨ (z + z⁻¹) ^ 87381 = 1 := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  by_cases hz1 : z = 1
  · left; rw [hz1, inv_one]; linear_combination h2
  by_cases ht0 : z + z⁻¹ = 0
  · exact Or.inl ht0
  right
  have hu3 := cube37 h2 _ (psi37_zero hz hz1)
  have hu0 : v37 (z + z⁻¹) ≠ 0 := by
    intro h; rw [h, zero_pow (by norm_num)] at hu3; exact ht0 hu3.symm
  have hu := (eq_zero_or_pow_eq_one (by norm_num) (v37_frob (t_frob hz))).resolve_left hu0
  rw [← hu3, ← pow_mul]
  norm_num at hu ⊢
  exact hu

/-- **Theorem.** The period of rule 90 on the 37 x 37 torus divides 87381 = (2^18 - 1)/3. -/
theorem period_r90_dvd : period 37 r90Offsets ∣ 87381 := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot (m := 37) ⟨18, rfl⟩
  rw [← isPeriod_iff_period_dvd, isPeriod_iff hζ]
  intro j _ k _
  rw [lam_eq_ev hζ.pow_eq_one, ev_r90, inv_inv]
  have hp : ((ζ ^ j)⁻¹) ^ 37 = 1 := by
    rw [inv_pow, ← pow_mul, mul_comm, pow_mul, hζ.pow_eq_one, one_pow, inv_one]
  have := r90_val hp
  rw [inv_inv, add_comm] at this
  exact this

theorem lcm_dvd_87381 {P : ℕ} (hP : P ∣ 87381) : Nat.lcm 511 P ∣ 87381 :=
  Nat.lcm_dvd (by norm_num) hP

/-- **The six rules at 37, unconditionally**: each period divides 87381, so every eigenvalue is a
cube in F(2^18). -/
theorem period_w_dvd_87381 : period 37 wOffsets ∣ 87381 :=
  period_w_dvd.trans (lcm_dvd_87381 period_r90_dvd)

theorem period_k8m8e4_dvd_87381 : period 37 k8m8e4Offsets ∣ 87381 :=
  period_k8m8e4_dvd.trans (lcm_dvd_87381 period_r90_dvd)

theorem period_c4l8m8_dvd_87381 : period 37 c4l8m8Offsets ∣ 87381 :=
  period_c4l8m8_dvd.trans (lcm_dvd_87381 period_r90_dvd)

theorem period_a4b4c4l8e4self_dvd_87381 : period 37 a4b4c4l8e4selfOffsets ∣ 87381 :=
  period_a4b4c4l8e4self_dvd.trans (lcm_dvd_87381 period_r90_dvd)

theorem period_v_dvd_87381 : period 37 vOffsets ∣ 87381 :=
  period_v_dvd.trans (lcm_dvd_87381 period_r90_dvd)

theorem period_tri_dvd_87381 : period 37 triOffsets ∣ 87381 :=
  period_tri_dvd.trans (lcm_dvd_87381 period_r90_dvd)

end Field

end Pilot

end LatticeProofs
