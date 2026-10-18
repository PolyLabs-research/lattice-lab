/-
The LLM-central pilot's target (CARD.md). Define the law, then prove it.

**The law.** On the atlas's triangular torus of side n = 2^v m, m odd, v ≥ 1, n ≥ 4, VO + T13 has
period 2^e P(m), where P(m) is the period of its square's plane rule s = `triSVOT13Offsets` on the
square torus of side m, and

* e = v + 1 when m ≥ 3,
* e = v - 1 when m = 1 (n = 2^v, v ≥ 2).

**The mechanism.** Two steps of VO + T13 are one step of s on each layer (`grp_triVOT13`).

* m ≥ 3: as for the edge rule (`TriTwoPart.lean`). On the sub-torus Z/2m × Z/m the characters
  ψ₁(a, b) = ζ^a ζ^b and ψ₂ = ψ₁ · [a even] form a Jordan block of s's adjoint with λ = 1 and
  ζ³ μ = (ζ² + 1)³, that is μ = (ζ + 1/ζ)³: the square factors as s_E(x, y) s_E(x³, y³)
  (`triangle_VOT13_twisted`), and s_E's μ is ζ + 1/ζ. So every period on the sub-torus is even
  and the period is exactly 2^(v+1) P(m).
* m = 1: there are no characters to separate, and the 2-part drops. The 49 translations of s fall
  an odd number of times only on 0 of Z/4 × Z/2 (`triSubHom 2`), so s is the identity there and
  2^(v-1) is a period. On Z/8 × Z/4 (`triSubHom 4`), s is an involution but not the identity, so
  1 is not a period there and 2^(v-2) is not a period on the torus of side 2^v (v ≥ 3). For v = 2
  the period is even by the parity swap. So the period is exactly 2^(v-1), and P(1) = 1.
-/
import LatticeProofs
import LatticeProofs.HexTwoPart
import LatticeProofs.TriTwoPart

namespace LatticeProofs

open Finset

/-- **Your law**: the exponent of 2 in VO + T13's period on the atlas's triangular torus of side
2^v m, m odd, so that the period is `2 ^ vot13TwoExp v m * period m triSVOT13Offsets`:
v + 1 when m ≥ 3, and v - 1 when m = 1. -/
def vot13TwoExp (v m : ℕ) : ℕ := if m = 1 then v - 1 else v + 1

/-! ### m ≥ 3: the Jordan block on the sub-torus -/

/-- VO + T13's square on the sub-torus Z/2m × Z/m: λ = 1 and ζ³ μ = (ζ² - 1)³. -/
theorem triSub_even_triSVOT13 {m : ℕ} [NeZero m] [NeZero (2 * m)] (hm : Odd m) (hm3 : 3 ≤ m)
    {p : ℕ} (hp : IsEventualPeriod (gstep (triSubHom m) triSVOT13Offsets) p) : Even p := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  have h2K : (2 : AlgebraicClosure (ZMod 2)) = 0 := two_eq_zero_of_charTwo
  have h0 : ζ ≠ 0 := ne_zero_of_pow_eq_one hζ.pow_eq_one
  have hsq : (ζ ^ 2 - 1) ^ 3 ≠ 0 := pow_ne_zero 3 fun h =>
    one_add_sq_ne_zero hm3 hζ (by linear_combination h + h2K)
  refine triSub_even hζ.pow_eq_one ?_ ?_ hp
  · have hlam : ∑ d ∈ triSVOT13Offsets, ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2) = 1 := by
      simp [triSVOT13Offsets]
      field_simp
      linear_combination (2 + 3 * ζ + 2 * ζ ^ 2 + 3 * ζ ^ 3 + 4 * ζ ^ 4 + 3 * ζ ^ 5 + 2 * ζ ^ 6 + 3 * ζ ^ 7 +
        2 * ζ ^ 8) * h2K
    rw [hlam]
    exact one_ne_zero
  · have hμ : (∑ d ∈ triSVOT13Offsets, ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2) *
        ((-(d.1 - d.2) : ℤ) : AlgebraicClosure (ZMod 2))) * ζ ^ 3 = (ζ ^ 2 - 1) ^ 3 := by
      simp [triSVOT13Offsets]
      field_simp
      linear_combination (-4 - 4 * ζ - 2 * ζ ^ 2 - 3 * ζ ^ 3 + 3 * ζ ^ 5 + 2 * ζ ^ 6 + 4 * ζ ^ 7 +
        4 * ζ ^ 8) * h2K
    intro h
    rw [h, zero_mul] at hμ
    exact hsq hμ.symm

/-- **VO + T13's 2-part for m ≥ 3.** On the atlas's triangular torus of side n = 2^v m, with m odd,
m ≥ 3 and v ≥ 1, VO + T13 has period exactly 2^(v+1) P(m). -/
theorem atlasTriPeriod_triVOT13_exact {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm3 : 3 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    atlasTriPeriod n triVOT13 = 2 ^ (v + 1) * period m triSVOT13Offsets := by
  have : NeZero (2 * m) := ⟨by positivity⟩
  obtain ⟨a, ha, hP⟩ := atlasTriPeriod_triVOT13 hm hv hn
  exact atlasTriPeriod_exact_of_even hm hv hn
    (gtriStep_twice_of_cross (triHom n) rfl rfl grp_triVOT13)
    (fun _ hp => triSub_even_triSVOT13 hm hm3 hp) (by omega : a + 1 ≤ v + 1) hP

/-! ### m = 1: the tori Z/4 × Z/2 and Z/8 × Z/4 -/

/-- A rule whose translations fall an odd number of times on 0 and an even number of times on
every other cell of the torus is the identity there. -/
theorem gstep_eq_self_of_fibers {G : Type*} [AddCommGroup G] [Fintype G] [DecidableEq G]
    (ω : ℤ × ℤ →+ G) (D : Finset (ℤ × ℤ))
    (h : ∀ g : G, ((D.filter (fun d => ω d = g)).card : ZMod 2) = if g = 0 then 1 else 0)
    (c : G → ZMod 2) : gstep ω D c = c := by
  funext v
  simp only [gstep]
  rw [← Finset.sum_fiberwise' D (fun d => ω d) (fun g => c (v + g))]
  simp only [Finset.sum_const, nsmul_eq_mul, h, ite_mul, one_mul, zero_mul,
    Finset.sum_ite_eq', Finset.mem_univ, ite_true, add_zero]

/-- s is the identity on Z/4 × Z/2. -/
theorem gstep_triSub_two (c : ZMod (2 * 2) × ZMod 2 → ZMod 2) :
    gstep (triSubHom 2) triSVOT13Offsets c = c :=
  gstep_eq_self_of_fibers _ _ (by decide) c

/-- s is an involution on Z/8 × Z/4. -/
theorem gstep_triSub_four_twice (c : ZMod (2 * 4) × ZMod 4 → ZMod 2) :
    gstep (triSubHom 4) triSVOT13Offsets (gstep (triSubHom 4) triSVOT13Offsets c) = c := by
  have h := congrFun (gstep_iterate_two_pow (triSubHom 4) triSVOT13Offsets 1) c
  rw [pow_one, Function.iterate_succ_apply, Function.iterate_one] at h
  rw [h]
  exact gstep_eq_self_of_fibers _ _ (by decide) c

/-- s is not the identity on Z/8 × Z/4: from a single live cell at 0, the cell (6, 0) is live. -/
theorem gstep_triSub_four_ne :
    gstep (triSubHom 4) triSVOT13Offsets (Pi.single 0 1) ≠ Pi.single 0 1 := by
  intro h
  have := congrFun h (6, 0)
  revert this
  decide

/-- So 1 is not a period of s on Z/8 × Z/4. -/
theorem not_isEventualPeriod_triSub_four_one :
    ¬ IsEventualPeriod (gstep (triSubHom 4) triSVOT13Offsets) 1 := by
  rintro ⟨t, ht⟩
  set f := gstep (triSubHom 4) triSVOT13Offsets
  have hinv : Function.Involutive f := gstep_triSub_four_twice
  have h := congrFun ht (Pi.single 0 1)
  rw [Function.iterate_succ_apply] at h
  exact gstep_triSub_four_ne ((hinv.injective.iterate t) h)

/-- **VO + T13 on the atlas's triangular torus of side 2^v**, v ≥ 2: its period is 2^(v-1). -/
theorem atlasTriPeriod_triVOT13_two_pow {n v : ℕ} [NeZero n] [NeZero (n / 2)] (hv : 2 ≤ v)
    (hn : n = 2 ^ v) : atlasTriPeriod n triVOT13 = 2 ^ (v - 1) := by
  have hR := gtriStep_twice_of_cross (triHom n) (R := triVOT13) rfl rfl grp_triVOT13
  -- 2^(v-1) is a period: s is the identity on Z/4 × Z/2.
  have hup : atlasTriPeriod n triVOT13 ∣ 2 ^ (v - 1) := by
    have hn' : n = 2 ^ (v - 1) * 2 := by
      rw [hn, ← pow_succ, Nat.sub_add_cancel (by omega)]
    have h1 : IsEventualPeriod (gstep (triSubHom 2) triSVOT13Offsets) 1 :=
      ⟨0, funext fun c => by simpa using gstep_triSub_two c⟩
    have := (isEventualPeriod_atlasTri_iff (m := 2) (by omega) hn' hR 1).2 h1
    rw [mul_one] at this
    exact isEventualPeriod_iff_dvd.1 this
  obtain ⟨a, ha, hP⟩ := (Nat.dvd_prime_pow Nat.prime_two).1 hup
  rw [hP]
  congr 1
  -- The period is even.
  have heven : 2 ∣ atlasTriPeriod n triVOT13 := by
    rw [atlasTriPeriod, gtriPeriod_triVOT13]
    exact dvd_mul_right 2 _
  have ha1 : 1 ≤ a := by
    rcases Nat.eq_zero_or_pos a with h0 | h0
    · rw [hP, h0, pow_zero] at heven
      exact absurd (Nat.le_of_dvd one_pos heven) (by norm_num)
    · exact h0
  by_contra hne
  -- Otherwise v ≥ 3 and 2^(v-2) is a period, so 1 is a period of s on Z/8 × Z/4.
  have hv3 : 3 ≤ v := by omega
  have hn' : n = 2 ^ (v - 2) * 4 := by
    rw [hn, show (4 : ℕ) = 2 ^ 2 by norm_num, ← pow_add, Nat.sub_add_cancel (by omega)]
  have hdvd : atlasTriPeriod n triVOT13 ∣ 2 ^ (v - 2) * 1 := by
    rw [hP, mul_one]
    exact Nat.pow_dvd_pow 2 (by omega)
  rw [atlasTriPeriod, gtriPeriod, ← isEventualPeriod_iff_dvd,
    isEventualPeriod_atlasTri_iff (m := 4) (by omega) hn' hR] at hdvd
  exact not_isEventualPeriod_triSub_four_one hdvd

/-- On the square torus of side 1, every rule has period 1. -/
theorem period_one (D : Finset (ℤ × ℤ)) : period 1 D = 1 :=
  Nat.dvd_one.1 (period_dvd_two_pow_sub_one (r := 1) odd_one D (Subsingleton.elim _ _))

/-! ### The law -/

/-- **VO + T13's period law** on the atlas's triangular torus of every even side n ≥ 4. -/
theorem atlasTriPeriod_triVOT13_law {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) (h4 : 4 ≤ n) :
    atlasTriPeriod n triVOT13 = 2 ^ vot13TwoExp v m * period m triSVOT13Offsets := by
  by_cases hm1 : m = 1
  · subst hm1
    simp only [vot13TwoExp, ↓reduceIte, period_one, mul_one]
    rw [mul_one] at hn
    have hv2 : 2 ≤ v := by
      by_contra h
      have : v = 1 := by omega
      subst this
      omega
    exact atlasTriPeriod_triVOT13_two_pow hv2 hn
  · have hm3 : 3 ≤ m := by
      obtain ⟨k, rfl⟩ := hm
      omega
    simp only [vot13TwoExp, hm1, ↓reduceIte]
    exact atlasTriPeriod_triVOT13_exact hm hm3 hv hn

end LatticeProofs
