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

Round 3's triangle rules, on the triangular torus of odd side m (`Triangle.lean`):

* `triPeriod_triE`, `triPeriod_triVOT13`: each has twice the period of its s, the square-torus
  rule its matrix squares to.
* `triPeriod_triE_dvd`: the edge rule's period divides 2 (2^r - 1) when 2^r = +-1 mod m.
* `triPeriod_twisted`: the twisted power. If 3 = +-2^k mod m and the edge rule has period 2P,
  then VO + T13 has period 2 (P / gcd(P, 1 + 2^k)).
-/
import LatticeProofs.Rules

namespace LatticeProofs

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
  rw [← isPeriod_iff_period_dvd, ← isPeriod_iff_period_dvd,
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
    ((isPeriod_iff_period_dvd _ _ _).1 ((key _).2 ((isPeriod_iff_period_dvd _ _ _).2 dvd_rfl)))
    ((isPeriod_iff_period_dvd _ _ _).1 ((key _).1 ((isPeriod_iff_period_dvd _ _ _).2 dvd_rfl)))

section TriangleMechanisms

variable {m : ℕ} [NeZero m] {K : Type*} [Field K] [CharP K 2] {ζ : K}

omit [CharP K 2] in
theorem pow_mul_inv_cancel (hζ : ζ ^ m = 1) (j : ℕ) : ζ ^ j * (ζ ^ j)⁻¹ = 1 :=
  mul_inv_cancel₀ (pow_ne_zero j (ne_zero_of_pow_eq_one hζ))

/-- The edge rule's cross eigenvalues multiply to its s's. -/
theorem lam_triE (hζ : ζ ^ m = 1) (j k : ℕ) :
    lam m ζ triUdEOffsets j k * lam m ζ triDuEOffsets j k = lam m ζ triSEOffsets j k := by
  rw [lam_eq_ev hζ, lam_eq_ev hζ, lam_eq_ev hζ, ev_triUdE, ev_triDuE, ev_triSE]
  linear_combination triangle_E_s two_eq_zero_of_charTwo _ _ _ _
    (pow_mul_inv_cancel hζ j) (pow_mul_inv_cancel hζ k)

/-- VO + T13's cross eigenvalues multiply to its s's. -/
theorem lam_triVOT13 (hζ : ζ ^ m = 1) (j k : ℕ) :
    lam m ζ triUdVOT13Offsets j k * lam m ζ triDuVOT13Offsets j k =
      lam m ζ triSVOT13Offsets j k := by
  rw [lam_eq_ev hζ, lam_eq_ev hζ, lam_eq_ev hζ, ev_triUdVOT13, ev_triDuVOT13, ev_triSVOT13]
  linear_combination triangle_VOT13_s two_eq_zero_of_charTwo _ _ _ _
    (pow_mul_inv_cancel hζ j) (pow_mul_inv_cancel hζ k)

/-- The twisted power at the characters: if zeta^3 = zeta^(2^k) or zeta^3 zeta^(2^k) = 1, every
eigenvalue of VO + T13's s is the edge rule's s's raised to 1 + 2^k. -/
theorem lam_triSVOT13 (hζ : ζ ^ m = 1) {k : ℕ} (h3 : ζ ^ 3 = ζ ^ 2 ^ k ∨ ζ ^ 3 * ζ ^ 2 ^ k = 1)
    (j l : ℕ) :
    lam m ζ triSVOT13Offsets j l = lam m ζ triSEOffsets j l ^ (1 + 2 ^ k) := by
  rw [lam_eq_ev hζ, lam_eq_ev hζ, ev_triSVOT13, ev_triSE]
  have hx := pow_mul_inv_cancel hζ j
  have hy := pow_mul_inv_cancel hζ l
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  have hs := triangle_VOT13_s h2 _ _ _ _ hx hy
  have hE : triSE (ζ ^ j) (ζ ^ j)⁻¹ (ζ ^ l) (ζ ^ l)⁻¹ = 1 + triVS (ζ ^ j) (ζ ^ j)⁻¹ (ζ ^ l) (ζ ^ l)⁻¹ := by
    linear_combination (triangle_E_square h2 _ _ _ _ hx hy) - (triangle_E_s h2 _ _ _ _ hx hy)
  rw [hE]
  rcases h3 with h3 | h3
  · have hp : ∀ i : ℕ, (ζ ^ i) ^ 3 = (ζ ^ i) ^ 2 ^ k := fun i => by
      rw [pow_right_comm, h3, pow_right_comm]
    linear_combination (triVOT13_value k _ _ _ _ hx hy (hp j) (hp l)) - hs
  · have hp : ∀ i : ℕ, (ζ ^ i) ^ 3 = (ζ ^ i)⁻¹ ^ 2 ^ k := fun i => by
      rw [inv_pow]
      refine eq_inv_of_mul_eq_one_left ?_
      rw [pow_right_comm, pow_right_comm ζ i (2 ^ k), ← mul_pow, h3, one_pow]
    linear_combination (triVOT13_value_neg k _ _ _ _ hx hy (hp j) (hp l)) - hs

end TriangleMechanisms

/-- The parities of the layers' live-cell counts swap under a rule whose cross neighbourhoods have
odd size and whose same-orientation ones are empty. -/
theorem card_ud_du {R : TriRule} (huu : R.uu = ∅) (hdd : R.dd = ∅) {a b : ℕ}
    (hud : R.ud.card = a) (hdu : R.du.card = b) (ha : (a : ZMod 2) = 1) (hb : (b : ZMod 2) = 1) :
    (R.uu.card : ZMod 2) = 0 ∧ (R.ud.card : ZMod 2) = 1 ∧ (R.du.card : ZMod 2) = 1 ∧
      (R.dd.card : ZMod 2) = 0 := by
  simp [huu, hdd, hud, hdu, ha, hb]

/-- **The edge rule on the triangular torus.** For odd m, its period is twice its s's. -/
theorem triPeriod_triE {m : ℕ} [NeZero m] (hm : Odd m) :
    triPeriod m triE = 2 * period m triSEOffsets := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  obtain ⟨huu, hud, hdu, hdd⟩ := card_ud_du (R := triE) rfl rfl triUdEOffsets_card
    triDuEOffsets_card (by decide) (by decide)
  exact triPeriod_eq_two_mul hm (triStep_triStep hζ rfl rfl (lam_triE hζ.pow_eq_one))
    huu hud hdu hdd

/-- **VO + T13 on the triangular torus.** For odd m, its period is twice its s's. -/
theorem triPeriod_triVOT13 {m : ℕ} [NeZero m] (hm : Odd m) :
    triPeriod m triVOT13 = 2 * period m triSVOT13Offsets := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  obtain ⟨huu, hud, hdu, hdd⟩ := card_ud_du (R := triVOT13) rfl rfl triUdVOT13Offsets_card
    triDuVOT13Offsets_card (by decide) (by decide)
  exact triPeriod_eq_two_mul hm (triStep_triStep hζ rfl rfl (lam_triVOT13 hζ.pow_eq_one))
    huu hud hdu hdd

/-- **The edge rule's bound.** For odd m with 2^r = +-1 mod m, the edge rule's period on the
triangular torus divides 2 (2^r - 1). -/
theorem triPeriod_triE_dvd {m : ℕ} [NeZero m] (hm : Odd m) {r : ℕ}
    (hr : (2 : ZMod m) ^ r = 1 ∨ (2 : ZMod m) ^ r = -1) :
    triPeriod m triE ∣ 2 * (2 ^ r - 1) := by
  rw [triPeriod_triE hm]
  refine Nat.mul_dvd_mul_left 2 ?_
  rcases hr with hr | hr
  · exact period_dvd_two_pow_sub_one hm _ hr
  · exact period_dvd_two_pow_sub_one_of_symm hm triSEOffsets_symm hr

/-- The twisted power on the square torus: if 3 = +-2^k mod m, the period of VO + T13's s is the
edge rule's s's divided by gcd(period, 1 + 2^k). -/
theorem period_triSVOT13 {m : ℕ} [NeZero m] (hm : Odd m) {k : ℕ}
    (h : (3 : ZMod m) = 2 ^ k ∨ (3 : ZMod m) = -2 ^ k) :
    period m triSVOT13Offsets =
      period m triSEOffsets / Nat.gcd (period m triSEOffsets) (1 + 2 ^ k) := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  have h1 := hζ.pow_eq_one
  have h3 : ζ ^ 3 = ζ ^ 2 ^ k ∨ ζ ^ 3 * ζ ^ 2 ^ k = 1 := by
    rcases h with h | h
    · exact Or.inl (pow_eq_pow_of_cast_eq h1 (by push_cast; exact h))
    · refine Or.inr ?_
      calc ζ ^ 3 * ζ ^ 2 ^ k = ζ ^ (3 + 2 ^ k) := (pow_add ζ 3 (2 ^ k)).symm
        _ = ζ ^ 0 := pow_eq_pow_of_cast_eq h1 (by push_cast; rw [h]; ring)
        _ = 1 := pow_zero ζ
  exact period_eq_of_lam_eq_pow hζ (by positivity) (lam_triSVOT13 h1 h3)

/-- **The twisted power, end to end (round 3).** On the triangular torus of odd side m with
3 = +-2^k mod m: if the edge rule E has period 2P, then VO + T13 has period
2 (P / gcd(P, 1 + 2^k)). When k is odd, 3 divides 1 + 2^k (`three_dvd_one_add_two_pow`). -/
theorem triPeriod_twisted {m : ℕ} [NeZero m] (hm : Odd m) {k : ℕ}
    (h : (3 : ZMod m) = 2 ^ k ∨ (3 : ZMod m) = -2 ^ k) :
    ∃ P, triPeriod m triE = 2 * P ∧ triPeriod m triVOT13 = 2 * (P / Nat.gcd P (1 + 2 ^ k)) :=
  ⟨period m triSEOffsets, triPeriod_triE hm, by rw [triPeriod_triVOT13 hm, period_triSVOT13 hm h]⟩

end LatticeProofs
