/-
The eigenvalue mechanisms of the linear-rule atlas (docs/linear-atlas.md, docs/proofs.md).

A shell rule on an n x n torus with n odd acts diagonally on the torus's characters. Its
eigenvalue at a character is the rule's Laurent polynomial evaluated at x = zeta^j, y = zeta^k,
for zeta a primitive n-th root of unity in a field of characteristic 2. Its period on the torus
is the lcm of the multiplicative orders of its nonzero eigenvalues.

That bridge, from periods to eigenvalue orders, is `Bridge.lean`, and `Periods.lean` combines the
two. What follows is the eigenvalue side, for any commutative ring of characteristic 2 and any
x, y with inverses xi, yi:

* raising to the k-th power divides an order by gcd(order, k) (`orderOf_pow_div`);
* the cube mechanism: N4 + K8 + C4 has the eigenvalues of N4 cubed (`sqN4K8C4_value`);
* the twisted power: wherever x^3 = x^(2^k) and y^3 = y^(2^k), the triangle rule VO + T13 has
  the eigenvalue of the edge rule raised to 1 + 2^k (`triVOT13_value`), and 3 divides 1 + 2^k
  when k is odd (`three_dvd_one_add_two_pow`).
-/
import LatticeProofs.Identities
import Mathlib.GroupTheory.OrderOfElement

namespace LatticeProofs

/-- Raising to the k-th power divides an element's order by gcd(order, k). -/
theorem orderOf_pow_div {G : Type*} [Monoid G] (g : G) {k : ℕ} (hk : k ≠ 0) :
    orderOf (g ^ k) = orderOf g / Nat.gcd (orderOf g) k :=
  orderOf_pow' g hk

theorem three_dvd_one_add_two_pow_odd : ∀ j : ℕ, 3 ∣ 1 + 2 ^ (2 * j + 1)
  | 0 => by norm_num
  | j + 1 => by
    have ih := three_dvd_one_add_two_pow_odd j
    have h : 2 ^ (2 * (j + 1) + 1) = 4 * 2 ^ (2 * j + 1) := by ring
    omega

/-- 3 divides 1 + 2^k when k is odd: then a twisted power is a cube as well. -/
theorem three_dvd_one_add_two_pow {k : ℕ} (hk : Odd k) : 3 ∣ 1 + 2 ^ k := by
  obtain ⟨j, rfl⟩ := hk
  exact three_dvd_one_add_two_pow_odd j

section Inverses

variable {R : Type*} [CommRing R]

/-- If x^a = x^b and x has inverse xi, then xi^a = xi^b. -/
theorem inv_pow_eq {x xi : R} (hx : x * xi = 1) {a b : ℕ} (h : x ^ a = x ^ b) :
    xi ^ a = xi ^ b := by
  have ha : x ^ a * xi ^ a = 1 := by rw [← mul_pow, hx, one_pow]
  have hb : x ^ b * xi ^ b = 1 := by rw [← mul_pow, hx, one_pow]
  calc xi ^ a = xi ^ a * (x ^ b * xi ^ b) := by rw [hb, mul_one]
    _ = (x ^ a * xi ^ a) * xi ^ b := by rw [h]; ring
    _ = xi ^ b := by rw [ha, one_mul]

theorem pow_mul_inv_pow {x xi : R} (hx : x * xi = 1) (d : ℕ) : x ^ d * xi ^ d = 1 := by
  rw [← mul_pow, hx, one_pow]

/-- If x^a = xi^b and x has inverse xi, then xi^a = x^b. -/
theorem inv_pow_eq_swap {x xi : R} (hx : x * xi = 1) {a b : ℕ} (h : x ^ a = xi ^ b) :
    xi ^ a = x ^ b := by
  have ha := pow_mul_inv_pow hx a
  have hb := pow_mul_inv_pow hx b
  calc xi ^ a = xi ^ a * (x ^ b * xi ^ b) := by rw [hb, mul_one]
    _ = x ^ b * (xi ^ a * xi ^ b) := by ring
    _ = x ^ b * (xi ^ a * x ^ a) := by rw [h]
    _ = x ^ b := by rw [mul_comm (xi ^ a), ha, mul_one]

/-- The shell VS is symmetric under x, y -> 1/x, 1/y. -/
theorem triVS_symm (x xi y yi : R) : triVS xi x yi y = triVS x xi y yi := by
  unfold triVS
  ring

end Inverses

section CharTwo

variable {R : Type*} [CommRing R] [CharP R 2]

theorem two_eq_zero_of_charTwo : (2 : R) = 0 := by
  exact_mod_cast CharP.cast_eq_zero R 2

/-- The cube mechanism: every eigenvalue of N4 + K8 + C4 is the cube of N4's. -/
theorem sqN4K8C4_value (x xi y yi : R) (hx : x * xi = 1) (hy : y * yi = 1) :
    sqN4K8C4 x xi y yi = sqN4 x xi y yi ^ 3 :=
  square_N4K8C4_cube two_eq_zero_of_charTwo x xi y yi hx hy

/-- So its order is N4's divided by gcd(order, 3). -/
theorem sqN4K8C4_order (x xi y yi : R) (hx : x * xi = 1) (hy : y * yi = 1) :
    orderOf (sqN4K8C4 x xi y yi) =
      orderOf (sqN4 x xi y yi) / Nat.gcd (orderOf (sqN4 x xi y yi)) 3 := by
  rw [sqN4K8C4_value x xi y yi hx hy]
  exact orderOf_pow_div _ (by norm_num)

/-- The edge rule's square, s_E = 1 + VS, commutes with Frobenius. -/
theorem sE_frobenius (k : ℕ) (x xi y yi : R) :
    (1 + triVS x xi y yi) ^ 2 ^ k =
      1 + triVS (x ^ 2 ^ k) (xi ^ 2 ^ k) (y ^ 2 ^ k) (yi ^ 2 ^ k) := by
  unfold triVS
  simp only [add_pow_char_pow, mul_pow, one_pow]

/-- The twisted power of round 3. Wherever x^3 = x^(2^k) and y^3 = y^(2^k), as at a character of
an m-torus with 3 = 2^k mod m, the eigenvalue of the triangle rule VO + T13 is the edge rule's
raised to 1 + 2^k. -/
theorem triVOT13_value (k : ℕ) (x xi y yi : R) (hx : x * xi = 1) (hy : y * yi = 1)
    (h3x : x ^ 3 = x ^ 2 ^ k) (h3y : y ^ 3 = y ^ 2 ^ k) :
    triDuVOT13 x xi y yi * triUdVOT13 x xi y yi = (1 + triVS x xi y yi) ^ (1 + 2 ^ k) := by
  have h2 : (2 : R) = 0 := two_eq_zero_of_charTwo
  have hE := triangle_E_square h2 x xi y yi hx hy
  have hE3 := triangle_E_square h2 (x ^ 3) (xi ^ 3) (y ^ 3) (yi ^ 3)
    (pow_mul_inv_pow hx 3) (pow_mul_inv_pow hy 3)
  calc triDuVOT13 x xi y yi * triUdVOT13 x xi y yi
      = (triDuE x xi y yi * triUdE x xi y yi) *
          (triDuE (x ^ 3) (xi ^ 3) (y ^ 3) (yi ^ 3) * triUdE (x ^ 3) (xi ^ 3) (y ^ 3) (yi ^ 3)) := by
        rw [triangle_VOT13_twisted h2 x xi y yi hx hy]; ring
    _ = (1 + triVS x xi y yi) * (1 + triVS (x ^ 3) (xi ^ 3) (y ^ 3) (yi ^ 3)) := by
        rw [hE, hE3]
    _ = (1 + triVS x xi y yi) * (1 + triVS x xi y yi) ^ 2 ^ k := by
        rw [h3x, h3y, inv_pow_eq hx h3x, inv_pow_eq hy h3y, sE_frobenius]
    _ = (1 + triVS x xi y yi) ^ (1 + 2 ^ k) := by ring

/-- The twisted power with the other sign. Wherever x^3 = xi^(2^k) and y^3 = yi^(2^k), as at a
character of an m-torus with 3 = -2^k mod m, the eigenvalue of VO + T13 is again the edge rule's
raised to 1 + 2^k, because s_E is symmetric. -/
theorem triVOT13_value_neg (k : ℕ) (x xi y yi : R) (hx : x * xi = 1) (hy : y * yi = 1)
    (h3x : x ^ 3 = xi ^ 2 ^ k) (h3y : y ^ 3 = yi ^ 2 ^ k) :
    triDuVOT13 x xi y yi * triUdVOT13 x xi y yi = (1 + triVS x xi y yi) ^ (1 + 2 ^ k) := by
  have h2 : (2 : R) = 0 := two_eq_zero_of_charTwo
  have hE := triangle_E_square h2 x xi y yi hx hy
  have hE3 := triangle_E_square h2 (x ^ 3) (xi ^ 3) (y ^ 3) (yi ^ 3)
    (pow_mul_inv_pow hx 3) (pow_mul_inv_pow hy 3)
  calc triDuVOT13 x xi y yi * triUdVOT13 x xi y yi
      = (triDuE x xi y yi * triUdE x xi y yi) *
          (triDuE (x ^ 3) (xi ^ 3) (y ^ 3) (yi ^ 3) * triUdE (x ^ 3) (xi ^ 3) (y ^ 3) (yi ^ 3)) := by
        rw [triangle_VOT13_twisted h2 x xi y yi hx hy]; ring
    _ = (1 + triVS x xi y yi) * (1 + triVS (x ^ 3) (xi ^ 3) (y ^ 3) (yi ^ 3)) := by
        rw [hE, hE3]
    _ = (1 + triVS x xi y yi) * (1 + triVS x xi y yi) ^ 2 ^ k := by
        rw [h3x, h3y, inv_pow_eq_swap hx h3x, inv_pow_eq_swap hy h3y, sE_frobenius,
          triVS_symm (x ^ 2 ^ k)]
    _ = (1 + triVS x xi y yi) ^ (1 + 2 ^ k) := by ring

/-- So its order is the edge rule's divided by gcd(order, 1 + 2^k); for odd k, 3 divides
1 + 2^k (`three_dvd_one_add_two_pow`). -/
theorem triVOT13_order (k : ℕ) (x xi y yi : R) (hx : x * xi = 1) (hy : y * yi = 1)
    (h3x : x ^ 3 = x ^ 2 ^ k) (h3y : y ^ 3 = y ^ 2 ^ k) :
    orderOf (triDuVOT13 x xi y yi * triUdVOT13 x xi y yi) =
      orderOf (1 + triVS x xi y yi) / Nat.gcd (orderOf (1 + triVS x xi y yi)) (1 + 2 ^ k) := by
  rw [triVOT13_value k x xi y yi hx hy h3x h3y]
  exact orderOf_pow_div _ (by positivity)

end CharTwo

end LatticeProofs
