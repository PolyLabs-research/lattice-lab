/-
Round 2's mechanisms as theorems about periods (docs/proofs.md).

Through the bridge (`Bridge.lean`), the eigenvalue identities become statements about the rules'
periods on the m x m torus, for every odd m. The field is the algebraic closure of GF(2), which
has a primitive m-th root of unity for every odd m. The rules are the atlas's own neighbourhoods
(`Rules.lean`, generated).

* `period_sqN4K8C4`: the cube. N4 + K8 + C4 has the period of N4 divided by gcd(period, 3).
* `period_sqA4K8C4self`: the cube again. A4 + K8 + C4 + self has the period of N4 + self divided
  by gcd(period, 3).
* `period_sqC4self`: the dilation. C4 + self has the period of N4 + self on the torus of side
  m / gcd(m, 3).
-/
import LatticeProofs.Rules
import Mathlib.RingTheory.RootsOfUnity.AlgebraicallyClosed

namespace LatticeProofs

/-- For odd m, the algebraic closure of GF(2) has a primitive m-th root of unity. -/
theorem exists_primitiveRoot {m : ℕ} [NeZero m] (hm : Odd m) :
    ∃ ζ : AlgebraicClosure (ZMod 2), IsPrimitiveRoot ζ m := by
  have : NeZero ((m : ℕ) : ZMod 2) :=
    ⟨by rw [ZMod.natCast_eq_one_iff_odd.2 hm]; exact one_ne_zero⟩
  exact HasEnoughRootsOfUnity.exists_isPrimitiveRoot _ m

section Mechanisms

variable {m : ℕ} [NeZero m] {K : Type*} [Field K] [CharP K 2] {ζ : K}

omit [CharP K 2] in
theorem inv_pow_ne_zero (hζ : ζ ^ m = 1) (j : ℕ) : (ζ ^ j)⁻¹ ≠ 0 :=
  inv_ne_zero (pow_ne_zero j (ne_zero_of_pow_eq_one hζ))

/-- If every eigenvalue of D is the n-th power of D₀'s, then p is a period of D exactly when
n p is a period of D₀. -/
theorem isPeriod_iff_of_lam_eq_pow (hζ : IsPrimitiveRoot ζ m) {D D₀ : Finset (ℤ × ℤ)} {n : ℕ}
    (hn : n ≠ 0) (h : ∀ j k, lam m ζ D j k = lam m ζ D₀ j k ^ n) (p : ℕ) :
    IsPeriod m D p ↔ IsPeriod m D₀ (n * p) := by
  simp only [isPeriod_iff hζ, h, pow_eq_zero_iff hn, ← pow_mul]

/-- If every eigenvalue of D is the n-th power of D₀'s, then D's period is D₀'s divided by
gcd(period, n). -/
theorem period_eq_of_lam_eq_pow (hζ : IsPrimitiveRoot ζ m) {D D₀ : Finset (ℤ × ℤ)} {n : ℕ}
    (hn : n ≠ 0) (h : ∀ j k, lam m ζ D j k = lam m ζ D₀ j k ^ n) :
    period m D = period m D₀ / Nat.gcd (period m D₀) n := by
  refine eq_div_gcd_of_dvd_iff (Nat.pos_of_ne_zero hn) fun p => ?_
  rw [← isPeriod_iff_period_dvd hζ, ← isPeriod_iff_period_dvd hζ,
    isPeriod_iff_of_lam_eq_pow hζ hn h]

/-- Every eigenvalue of N4 + K8 + C4 is the cube of N4's. -/
theorem lam_sqN4K8C4 (hζ : ζ ^ m = 1) (j k : ℕ) :
    lam m ζ sqN4K8C4Offsets j k = lam m ζ sqN4Offsets j k ^ 3 := by
  rw [lam_eq_ev hζ, lam_eq_ev hζ, ev_sqN4K8C4, ev_sqN4]
  exact sqN4K8C4_value _ _ _ _ (mul_inv_cancel₀ (inv_pow_ne_zero hζ j))
    (mul_inv_cancel₀ (inv_pow_ne_zero hζ k))

/-- Every eigenvalue of A4 + K8 + C4 + self is the cube of N4 + self's. -/
theorem lam_sqA4K8C4self (hζ : ζ ^ m = 1) (j k : ℕ) :
    lam m ζ sqA4K8C4selfOffsets j k = lam m ζ sqN4selfOffsets j k ^ 3 := by
  rw [lam_eq_ev hζ, lam_eq_ev hζ, ev_sqA4K8C4self, ev_sqN4self,
    square_A4K8C4self_cube two_eq_zero_of_charTwo _ _ _ _
      (mul_inv_cancel₀ (inv_pow_ne_zero hζ j)) (mul_inv_cancel₀ (inv_pow_ne_zero hζ k))]
  unfold sqN4 sqN4self
  ring

/-- Every eigenvalue of C4 + self on the m-torus is an eigenvalue of N4 + self at zeta^3. -/
theorem lam_sqC4self (hζ : ζ ^ m = 1) {m' : ℕ} [NeZero m'] (hζ' : (ζ ^ 3) ^ m' = 1) (j k : ℕ) :
    lam m ζ sqC4selfOffsets j k = lam m' (ζ ^ 3) sqN4selfOffsets j k := by
  rw [lam_eq_ev hζ, lam_eq_ev hζ', ev_sqC4self, ev_sqN4self,
    square_C4self_dilation two_eq_zero_of_charTwo _ _ _ _
      (mul_inv_cancel₀ (inv_pow_ne_zero hζ j)) (mul_inv_cancel₀ (inv_pow_ne_zero hζ k))]
  simp only [inv_pow, ← pow_mul, mul_comm j 3, mul_comm k 3]
  unfold sqN4 sqN4self
  ring

end Mechanisms

/-- **The cube, end to end.** On the m x m torus with m odd, the period of N4 + K8 + C4 is the
period of N4 divided by gcd(period, 3). -/
theorem period_sqN4K8C4 {m : ℕ} [NeZero m] (hm : Odd m) :
    period m sqN4K8C4Offsets = period m sqN4Offsets / Nat.gcd (period m sqN4Offsets) 3 := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  exact period_eq_of_lam_eq_pow hζ (by norm_num) (lam_sqN4K8C4 hζ.pow_eq_one)

/-- **The cube, end to end (round 2's first failure).** On the m x m torus with m odd, the period
of A4 + K8 + C4 + self is the period of N4 + self divided by gcd(period, 3). -/
theorem period_sqA4K8C4self {m : ℕ} [NeZero m] (hm : Odd m) :
    period m sqA4K8C4selfOffsets =
      period m sqN4selfOffsets / Nat.gcd (period m sqN4selfOffsets) 3 := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  exact period_eq_of_lam_eq_pow hζ (by norm_num) (lam_sqA4K8C4self hζ.pow_eq_one)

/-- **The dilation, end to end.** On the m x m torus with m odd, C4 + self has the period of
N4 + self on the torus of side m' = m / gcd(m, 3): the same torus when 3 does not divide m, and
the torus a third the size when it does. -/
theorem period_sqC4self {m m' : ℕ} [NeZero m] [NeZero m'] (hm : Odd m)
    (hm' : m' = m / Nat.gcd m 3) :
    period m sqC4selfOffsets = period m' sqN4selfOffsets := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  have hζ' : IsPrimitiveRoot (ζ ^ 3) m' := by
    have h := IsPrimitiveRoot.orderOf (ζ ^ 3)
    rwa [orderOf_pow' ζ (by norm_num : (3 : ℕ) ≠ 0), ← hζ.eq_orderOf, ← hm'] at h
  have hle : m' ≤ m := hm' ▸ Nat.div_le_self m _
  have hpos : 0 < m' := Nat.pos_of_ne_zero (NeZero.ne m')
  -- The eigenvalues at (j, k) depend only on j and k mod m'.
  have hmod : ∀ (D : Finset (ℤ × ℤ)) (j k : ℕ),
      lam m' (ζ ^ 3) D j k = lam m' (ζ ^ 3) D (j % m') (k % m') := by
    intro D j k
    rw [lam_eq_ev hζ'.pow_eq_one, lam_eq_ev hζ'.pow_eq_one,
      pow_eq_pow_of_cast_eq hζ'.pow_eq_one (ZMod.natCast_mod j m').symm,
      pow_eq_pow_of_cast_eq hζ'.pow_eq_one (ZMod.natCast_mod k m').symm]
  have key : ∀ p, IsPeriod m sqC4selfOffsets p ↔ IsPeriod m' sqN4selfOffsets p := by
    intro p
    simp only [isPeriod_iff hζ, isPeriod_iff hζ', lam_sqC4self hζ.pow_eq_one hζ'.pow_eq_one]
    constructor
    · intro h j hj k hk
      exact h j (lt_of_lt_of_le hj hle) k (lt_of_lt_of_le hk hle)
    · intro h j _ k _
      rw [hmod]
      exact h _ (Nat.mod_lt j hpos) _ (Nat.mod_lt k hpos)
  exact Nat.dvd_antisymm
    ((isPeriod_iff_period_dvd hζ _ _).1 ((key _).2 ((isPeriod_iff_period_dvd hζ' _ _).2 dvd_rfl)))
    ((isPeriod_iff_period_dvd hζ' _ _).1 ((key _).1 ((isPeriod_iff_period_dvd hζ _ _).2 dvd_rfl)))

end LatticeProofs
