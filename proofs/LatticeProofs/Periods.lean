/-
The atlas's mechanisms as theorems about periods (docs/proofs.md).

The rules are the atlas's own neighbourhoods (`Rules.lean`, generated). Two routes lead from the
identities of `Identities.lean` to periods:

* through the group ring (`GroupRing.lean`), at every torus size: an identity between Laurent
  polynomials is an identity between rules on every torus;
* through the bridge (`Bridge.lean`), at odd sizes, where the rules' eigenvalues decide the
  period. Only the twisted power needs it, because it holds at the characters, not as a polynomial
  identity.

Round 2's square rules, on the square torus of every side n:

* `period_sqN4K8C4`: the cube. N4 + K8 + C4 has the period of N4 divided by gcd(period, 3).
* `period_sqA4K8C4self`: the cube again, for A4 + K8 + C4 + self and N4 + self.
* `period_sqC4self`: the dilation. C4 + self has the period of N4 + self on the torus of side
  n / gcd(n, 3).

Round 3's triangle rules, on every triangular torus (`Triangle.lean`):

* `gtriPeriod_triE`, `gtriPeriod_triVOT13`: each has exactly twice the period of its s, the plane
  rule its matrix squares to.
* `gtriPeriod_triEVOVS`: the general 2 x 2 case. E + VO + VS has P / gcd(P, 2) = P(s).
* `triPeriod_twisted`: the twisted power on the rhombic torus of odd side m. If 3 = +-2^k mod m and
  the edge rule has period 2P, then VO + T13 has period 2 (P / gcd(P, 1 + 2^k)).
* `atlasTriPeriod_twisted`: the same on the atlas's own triangular torus of side n = 2^v m, for the
  odd parts of the periods: those are what the atlas registered.

And the hexagon (`hexPeriod_eq_two_pow_mul`): on the atlas's hexagonal torus of side n = 2^v m, a
rule's period is 2^a times its period on the square torus of side m, with a <= v + 1.
-/
import LatticeProofs.Rules
import LatticeProofs.Tori

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

end Mechanisms

/-! ### The identities, in the group ring -/

section Laurent

theorem lxi_mul_lx : lxi * lx = 1 := by rw [mul_comm]; exact lx_mul_lxi

theorem lyi_mul_ly : lyi * ly = 1 := by rw [mul_comm]; exact ly_mul_lyi

theorem grp_sqN4K8C4_eq : grp sqN4K8C4Offsets = grp sqN4Offsets ^ 3 := by
  rw [grp_sqN4K8C4, grp_sqN4]
  exact square_N4K8C4_cube laurent_two _ _ _ _ lx_mul_lxi ly_mul_lyi

theorem grp_sqA4K8C4self_eq : grp sqA4K8C4selfOffsets = grp sqN4selfOffsets ^ 3 := by
  rw [grp_sqA4K8C4self, grp_sqN4self,
    square_A4K8C4self_cube laurent_two _ _ _ _ lx_mul_lxi ly_mul_lyi]
  unfold sqN4 sqN4self
  ring

/-- C4 + self is N4 + self with every translation tripled. -/
theorem sqC4selfOffsets_eq : sqC4selfOffsets = sqN4selfOffsets.image (fun d => (3 : ℕ) • d) := by
  decide

theorem grp_triE : grp triUdEOffsets * grp triDuEOffsets = grp triSEOffsets := by
  rw [grp_triUdE, grp_triDuE, grp_triSE]
  linear_combination triangle_E_s laurent_two _ _ _ _ lxi_mul_lx lyi_mul_ly

theorem grp_triVOT13 : grp triUdVOT13Offsets * grp triDuVOT13Offsets = grp triSVOT13Offsets := by
  rw [grp_triUdVOT13, grp_triDuVOT13, grp_triSVOT13]
  linear_combination triangle_VOT13_s laurent_two _ _ _ _ lxi_mul_lx lyi_mul_ly

theorem grp_triEVOVS_up :
    grp triEVOVS.uu * grp triEVOVS.uu + grp triEVOVS.ud * grp triEVOVS.du = grp triSEVOVSOffsets := by
  simp only [triEVOVS]
  rw [grp_triUuEVOVS, grp_triUdEVOVS, grp_triDuEVOVS, grp_triSEVOVS]
  linear_combination triangle_EVOVS_s_up laurent_two _ _ _ _ lxi_mul_lx lyi_mul_ly

theorem grp_triEVOVS_ud :
    grp triEVOVS.uu * grp triEVOVS.ud + grp triEVOVS.ud * grp triEVOVS.dd = 0 := by
  simp only [triEVOVS]
  rw [grp_triUuEVOVS, grp_triUdEVOVS, grp_triDdEVOVS]
  linear_combination triangle_EVOVS_s_ud laurent_two _ _ _ _ lxi_mul_lx lyi_mul_ly

theorem grp_triEVOVS_du :
    grp triEVOVS.du * grp triEVOVS.uu + grp triEVOVS.dd * grp triEVOVS.du = 0 := by
  simp only [triEVOVS]
  rw [grp_triUuEVOVS, grp_triDuEVOVS, grp_triDdEVOVS]
  linear_combination triangle_EVOVS_s_du laurent_two _ _ _ _ lxi_mul_lx lyi_mul_ly

theorem grp_triEVOVS_down :
    grp triEVOVS.du * grp triEVOVS.ud + grp triEVOVS.dd * grp triEVOVS.dd =
      grp triSEVOVSOffsets := by
  simp only [triEVOVS]
  rw [grp_triUdEVOVS, grp_triDuEVOVS, grp_triDdEVOVS, grp_triSEVOVS]
  linear_combination triangle_EVOVS_s_down laurent_two _ _ _ _ lxi_mul_lx lyi_mul_ly

end Laurent

/-! ### Round 2, on the square torus of every side -/

/-- **The cube.** On the square torus of every side n, N4 + K8 + C4 has the period of N4 divided
by gcd(period, 3). -/
theorem period_sqN4K8C4 {n : ℕ} [NeZero n] :
    period n sqN4K8C4Offsets = period n sqN4Offsets / Nat.gcd (period n sqN4Offsets) 3 :=
  gperiod_eq_of_grp_eq_pow (offsetHom n) (by norm_num) grp_sqN4K8C4_eq

/-- **The cube (round 2's first failure).** On the square torus of every side n,
A4 + K8 + C4 + self has the period of N4 + self divided by gcd(period, 3). -/
theorem period_sqA4K8C4self {n : ℕ} [NeZero n] :
    period n sqA4K8C4selfOffsets =
      period n sqN4selfOffsets / Nat.gcd (period n sqN4selfOffsets) 3 :=
  gperiod_eq_of_grp_eq_pow (offsetHom n) (by norm_num) grp_sqA4K8C4self_eq

/-- **The dilation.** On the square torus of every side n, C4 + self has the period of N4 + self
on the torus of side n' = n / gcd(n, 3): the same torus when 3 does not divide n, and the torus
a third the size when it does. -/
theorem period_sqC4self {n n' : ℕ} [NeZero n] [NeZero n'] (hn' : n' = n / Nat.gcd n 3) :
    period n sqC4selfOffsets = period n' sqN4selfOffsets := by
  rw [sqC4selfOffsets_eq]
  exact period_image_smul (by norm_num) hn' sqN4selfOffsets

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

/-! ### Round 3, on every triangular torus -/

section EveryTriangularTorus

variable {G : Type*} [AddCommGroup G] [Fintype G] [DecidableEq G] (ω : ℤ × ℤ →+ G)

/-- **The edge rule.** On every triangular torus its period is exactly twice its s's. -/
theorem gtriPeriod_triE : gtriPeriod ω triE = 2 * gperiod ω triSEOffsets := by
  obtain ⟨huu, hud, hdu, hdd⟩ := card_ud_du (R := triE) rfl rfl triUdEOffsets_card
    triDuEOffsets_card (by decide) (by decide)
  exact gtriPeriod_eq_two_mul ω (gtriStep_twice_of_cross ω rfl rfl grp_triE) huu hud hdu hdd

/-- **VO + T13.** On every triangular torus its period is exactly twice its s's. -/
theorem gtriPeriod_triVOT13 : gtriPeriod ω triVOT13 = 2 * gperiod ω triSVOT13Offsets := by
  obtain ⟨huu, hud, hdu, hdd⟩ := card_ud_du (R := triVOT13) rfl rfl triUdVOT13Offsets_card
    triDuVOT13Offsets_card (by decide) (by decide)
  exact gtriPeriod_eq_two_mul ω (gtriStep_twice_of_cross ω rfl rfl grp_triVOT13) huu hud hdu hdd

omit [Fintype G] [DecidableEq G] in
/-- **The general 2 x 2 case: E + VO + VS** (LatticeLife's B1,3,...,11/S1,3,...,11). Its matrix has
all four entries, and squares to s I. On every triangular torus its period P satisfies
P / gcd(P, 2) = P(s). -/
theorem gtriPeriod_triEVOVS [Finite G] :
    gtriPeriod ω triEVOVS / Nat.gcd (gtriPeriod ω triEVOVS) 2 = gperiod ω triSEVOVSOffsets :=
  gtriPeriod_div_two ω (gtriStep_twice ω grp_triEVOVS_up grp_triEVOVS_ud grp_triEVOVS_du
    grp_triEVOVS_down)

end EveryTriangularTorus

/-- The edge rule on the rhombic torus of every side m. -/
theorem triPeriod_triE {m : ℕ} [NeZero m] : triPeriod m triE = 2 * period m triSEOffsets :=
  gtriPeriod_triE (offsetHom m)

/-- VO + T13 on the rhombic torus of every side m. -/
theorem triPeriod_triVOT13 {m : ℕ} [NeZero m] :
    triPeriod m triVOT13 = 2 * period m triSVOT13Offsets :=
  gtriPeriod_triVOT13 (offsetHom m)

/-- **The edge rule's bound.** For odd m with 2^r = +-1 mod m, the edge rule's period on the
triangular torus divides 2 (2^r - 1). -/
theorem triPeriod_triE_dvd {m : ℕ} [NeZero m] (hm : Odd m) {r : ℕ}
    (hr : (2 : ZMod m) ^ r = 1 ∨ (2 : ZMod m) ^ r = -1) :
    triPeriod m triE ∣ 2 * (2 ^ r - 1) := by
  rw [triPeriod_triE]
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
  ⟨period m triSEOffsets, triPeriod_triE, by rw [triPeriod_triVOT13, period_triSVOT13 hm h]⟩

/-! ### The atlas's own tori -/

/-- **The edge rule on the atlas's triangular torus** of side n = 2^v m, with m odd and v >= 1. Its
period is 2^(a+1) P(s_E, m) for some a <= v, so its odd part is P(s_E, m). -/
theorem atlasTriPeriod_triE {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m] (hm : Odd m)
    (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    ∃ a ≤ v, atlasTriPeriod n triE = 2 ^ (a + 1) * period m triSEOffsets := by
  obtain ⟨a, ha, h⟩ := eq_two_pow_mul_of_div_gcd (triPeriod_div_gcd hm hv hn triSEOffsets)
  exact ⟨a, ha, by rw [atlasTriPeriod, gtriPeriod_triE, h, pow_succ]; ring⟩

/-- **VO + T13 on the atlas's triangular torus** of side n = 2^v m: its period is
2^(a+1) P(s, m) for some a <= v. -/
theorem atlasTriPeriod_triVOT13 {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m] (hm : Odd m)
    (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    ∃ a ≤ v, atlasTriPeriod n triVOT13 = 2 ^ (a + 1) * period m triSVOT13Offsets := by
  obtain ⟨a, ha, h⟩ := eq_two_pow_mul_of_div_gcd (triPeriod_div_gcd hm hv hn triSVOT13Offsets)
  exact ⟨a, ha, by rw [atlasTriPeriod, gtriPeriod_triVOT13, h, pow_succ]; ring⟩

/-- **E + VO + VS on the atlas's triangular torus** of side n = 2^v m: its period is
2^a P(s, m) for some a <= v + 1, so its odd part is P(s, m). -/
theorem atlasTriPeriod_triEVOVS {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m] (hm : Odd m)
    (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    ∃ a ≤ v + 1, atlasTriPeriod n triEVOVS = 2 ^ a * period m triSEVOVSOffsets := by
  obtain ⟨a, ha, h⟩ := eq_two_pow_mul_of_div_gcd (triPeriod_div_gcd hm hv hn triSEVOVSOffsets)
  have h2 : atlasTriPeriod n triEVOVS / Nat.gcd (atlasTriPeriod n triEVOVS) (2 ^ 1) =
      gperiod (triHom n) triSEVOVSOffsets := by
    rw [pow_one]; exact gtriPeriod_triEVOVS (triHom n)
  obtain ⟨b, hb, h'⟩ := eq_two_pow_mul_of_div_gcd h2
  exact ⟨b + a, by omega, by rw [h', h, pow_add, mul_assoc]⟩

/-- **The twisted power on the atlas's own torus (round 3).** On the triangular torus of side
n = 2^v m with m odd, v >= 1 and 3 = +-2^k mod m: the edge rule's period has odd part some P, and
VO + T13's has odd part P / gcd(P, 1 + 2^k). These odd parts are what round 3 registered. -/
theorem atlasTriPeriod_twisted {n v m k : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m] (hm : Odd m)
    (hv : 1 ≤ v) (hn : n = 2 ^ v * m) (h : (3 : ZMod m) = 2 ^ k ∨ (3 : ZMod m) = -2 ^ k) :
    ∃ P, Odd P ∧ (∃ a ≤ v, atlasTriPeriod n triE = 2 ^ (a + 1) * P) ∧
      ∃ b ≤ v, atlasTriPeriod n triVOT13 = 2 ^ (b + 1) * (P / Nat.gcd P (1 + 2 ^ k)) := by
  refine ⟨period m triSEOffsets, period_odd hm _, atlasTriPeriod_triE hm hv hn, ?_⟩
  obtain ⟨b, hb, e⟩ := atlasTriPeriod_triVOT13 hm hv hn
  exact ⟨b, hb, by rw [e, period_triSVOT13 hm h]⟩

/-- **The hexagon's odd part and 2-part bound.** On the atlas's hexagonal torus of side n = 2^v m,
with m odd and v >= 1, a rule's period is 2^a P(m) for some a <= v + 1. Here P(m) is its period
on the square torus of side m, in axial coordinates. For H1 (B135/S135) the law
2 * 2^v(n) * R(m) has a = v + 1; this gives a <= v + 1 and the odd part. -/
theorem hexPeriod_eq_two_pow_mul {n v m : ℕ} [NeZero (2 * n)] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) (D : Finset (ℤ × ℤ)) :
    ∃ a ≤ v + 1, hexPeriod n D = 2 ^ a * period m D :=
  eq_two_pow_mul_of_div_gcd (hexPeriod_div_gcd hm hv hn D)

end LatticeProofs
