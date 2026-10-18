/-
The LLM-central pilot's target (CARD.md). Replace each `sorry` with a proof.

The mechanism, for n = 2^v m with m odd, m ≥ 3 and v ≥ 1, and R either triangle parity rule with
s its square's plane rule (`triSEOffsets`, `triSEVOVSOffsets`):

* **Two steps, then Frobenius, then restriction.** Two steps of R are one step of s on each layer
  (`gtriStep_twice`), 2^(v-1) steps of s are one step of 2^(v-1) s (`gstep_iterate_two_pow`), and
  that acts on each coset of 2^(v-1) G as s acts on the sub-torus G' = Z/2m × Z/m with
  (x, y) ↦ (x - y mod 2m, y mod m) (`triSubHom`), which multiplication by 2^(v-1) embeds onto
  2^(v-1) G (`triSubMul`). So 2^v p is a period of R on G exactly when p is a period of s on G'
  (`isEventualPeriod_atlasTri_iff`).
* **A Jordan block on G'.** With ζ a primitive m-th root of unity, ψ₁(a, b) = ζ^a ζ^b and
  ψ₂ = ψ₁ · [a even] satisfy adj ψ₁ = λ ψ₁ and adj ψ₂ = λ ψ₂ + μ ψ₁. For s_E, λ = 1 and
  μ = ζ + 1/ζ; for s_EVOVS, λ = μ = ζ² + 1/ζ². Both are nonzero once ζ² ≠ 1, that is m ≥ 3.
  `even_of_jordan` makes every period of s on G' even (`triSub_even`).
* P(m) is odd (`period_odd`), so it is not a period on G', and 2^v P(m) is not a period of R on
  G. With the library's bounds this leaves exactly 2^(v+1) P(m).
-/
import LatticeProofs
import LatticeProofs.HexTwoPart

namespace LatticeProofs

open Finset

/-! ### The sub-torus Z/2m × Z/m -/

/-- The torus Z/2m × Z/m with (x, y) ↦ (x - y mod 2m, y mod m). Multiplication by 2^(v-1)
carries it onto the subgroup 2^(v-1) G of the atlas's triangular torus G of side n = 2^v m. -/
def triSubHom (m : ℕ) : ℤ × ℤ →+ ZMod (2 * m) × ZMod m :=
  ((Int.castAddHom (ZMod (2 * m))).comp (AddMonoidHom.fst ℤ ℤ - AddMonoidHom.snd ℤ ℤ)).prod
    ((Int.castAddHom (ZMod m)).comp (AddMonoidHom.snd ℤ ℤ))

theorem triSubHom_apply (m : ℕ) (d : ℤ × ℤ) :
    triSubHom m d = (((d.1 - d.2 : ℤ) : ZMod (2 * m)), ((d.2 : ℤ) : ZMod m)) := by
  obtain ⟨a, b⟩ := d
  ext <;> simp [triSubHom]

/-- Multiplication by N from the sub-torus into the atlas's triangular torus of side n. -/
def triSubMul (m n N : ℕ) (h1 : n ∣ N * (2 * m)) (h2 : n / 2 ∣ N * m) :
    ZMod (2 * m) × ZMod m →+ TriCell n :=
  (zmodMul (2 * m) n N h1).prodMap (zmodMul m (n / 2) N h2)

theorem triSubMul_triSubHom {m n N : ℕ} (h1 : n ∣ N * (2 * m)) (h2 : n / 2 ∣ N * m)
    (d : ℤ × ℤ) : triSubMul m n N h1 h2 (triSubHom m d) = triHom n (N • d) := by
  obtain ⟨a, b⟩ := d
  rw [triSubHom_apply, Prod.smul_mk]
  simp only [triSubMul, AddMonoidHom.coe_prodMap, Prod.map_apply, zmodMul_intCast]
  ext
  · simp [triHom]
    ring
  · simp [triHom]

theorem triSubMul_injective {m n v : ℕ} [NeZero m] [NeZero (2 * m)] (hv : 1 ≤ v)
    (hn : n = 2 ^ v * m) (h1 : n ∣ 2 ^ (v - 1) * (2 * m)) (h2 : n / 2 ∣ 2 ^ (v - 1) * m) :
    Function.Injective (triSubMul m n (2 ^ (v - 1)) h1 h2) := by
  have hn' : n = 2 ^ (v - 1) * (2 * m) := by
    rw [hn, ← mul_assoc, ← pow_succ, Nat.sub_add_cancel hv]
  have i1 := zmodMul_injective h1 fun a ha => by
    rw [hn'] at ha
    exact Nat.dvd_of_mul_dvd_mul_left (by positivity) ha
  have i2 := zmodMul_injective h2 fun b hb => by
    rw [half_eq hv hn] at hb
    exact Nat.dvd_of_mul_dvd_mul_left (by positivity) hb
  exact i1.prodMap i2

/-- **The reduction to the sub-torus.** If two steps of R are one step of S on each layer, then
2^v p is a period of R on the atlas's triangular torus of side n = 2^v m exactly when p is a
period of S on the sub-torus. -/
theorem isEventualPeriod_atlasTri_iff {n v m : ℕ} [NeZero m] [NeZero (2 * m)] (hv : 1 ≤ v)
    (hn : n = 2 ^ v * m) {R : TriRule} {S : Finset (ℤ × ℤ)}
    (hR : ∀ c, gtriStep (triHom n) R (gtriStep (triHom n) R c) =
      Prod.map (gstep (triHom n) S) (gstep (triHom n) S) c) (p : ℕ) :
    IsEventualPeriod (gtriStep (triHom n) R) (2 ^ v * p) ↔
      IsEventualPeriod (gstep (triSubHom m) S) p := by
  have h1 : n ∣ 2 ^ (v - 1) * (2 * m) := by
    rw [hn, ← mul_assoc, ← pow_succ, Nat.sub_add_cancel hv]
  have h2 : n / 2 ∣ 2 ^ (v - 1) * m := by rw [half_eq hv hn]
  have hf : (gtriStep (triHom n) R)^[2] = Prod.map (gstep (triHom n) S) (gstep (triHom n) S) :=
    funext fun c => hR c
  rw [show 2 ^ v * p = 2 * (2 ^ (v - 1) * p) by
      rw [← mul_assoc, ← pow_succ', Nat.sub_add_cancel hv],
    ← isEventualPeriod_iterate_iff (by norm_num : 0 < 2), hf, isEventualPeriod_prodMap_iff,
    ← isEventualPeriod_iterate_iff (k := 2 ^ (v - 1)) (by positivity), gstep_iterate_two_pow]
  exact isEventualPeriod_restrict_iff (by positivity) (triSubMul_triSubHom h1 h2)
    (triSubMul_injective hv hn h1 h2) S p

/-! ### The Jordan block on the sub-torus -/

/-- **Every period of S on the sub-torus is even**, when λ = Σ c(d) and μ = Σ c(d) (x - y)(d)
are nonzero, where c(d) = ζ^-(d₁ - d₂) ζ^-d₂: the adjoint has a Jordan block at the character
ζ^a ζ^b, with the parity of a as the second weight. -/
theorem triSub_even {m : ℕ} [NeZero m] [NeZero (2 * m)] {ζ : AlgebraicClosure (ZMod 2)}
    (hζm : ζ ^ m = 1) {D : Finset (ℤ × ℤ)}
    (hlam0 : ∑ d ∈ D, ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2) ≠ 0)
    (hμ0 : ∑ d ∈ D, ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2) *
      ((-(d.1 - d.2) : ℤ) : AlgebraicClosure (ZMod 2)) ≠ 0) {p : ℕ}
    (hp : IsEventualPeriod (gstep (triSubHom m) D) p) : Even p := by
  have hζn : ζ ^ (2 * m) = 1 := by rw [pow_mul', hζm, one_pow]
  -- The weights: a character psi1 of the torus, and psi2 = psi1 on the cells with a even.
  let par : ZMod (2 * m) → AlgebraicClosure (ZMod 2) := fun t =>
    embed (AlgebraicClosure (ZMod 2)) (ZMod.castHom (dvd_mul_right 2 m) (ZMod 2) t)
  let ψ₁ : ZMod (2 * m) × ZMod m → AlgebraicClosure (ZMod 2) := fun w => ζ ^ w.1.val * ζ ^ w.2.val
  let ψ₂ : ZMod (2 * m) × ZMod m → AlgebraicClosure (ZMod 2) := fun w =>
    ζ ^ w.1.val * ζ ^ w.2.val * (1 + par w.1)
  -- psi1 at w - omega'(d), divided by psi1 at w.
  let c : ℤ × ℤ → AlgebraicClosure (ZMod 2) := fun d => ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2)
  have hsub : ∀ (w : ZMod (2 * m) × ZMod m) (d : ℤ × ℤ), w - triSubHom m d =
      (w.1 + ((-(d.1 - d.2) : ℤ) : ZMod (2 * m)), w.2 + ((-d.2 : ℤ) : ZMod m)) := by
    intro w d
    rw [triSubHom_apply]
    ext <;> simp [sub_eq_add_neg]
  have hψ₁ : ∀ w d, ψ₁ (w - triSubHom m d) = ψ₁ w * c d := by
    intro w d
    simp only [ψ₁, c, hsub, pow_val_add_intCast hζn, pow_val_add_intCast hζm]
    ring
  have hpar : ∀ (t : ZMod (2 * m)) (k : ℤ), par (t + (k : ZMod (2 * m))) = par t + (k : _) := by
    intro t k
    simp [par, map_add, map_intCast]
  have hψ₂ : ∀ w d, ψ₂ (w - triSubHom m d) =
      c d * ψ₂ w + c d * ((-(d.1 - d.2) : ℤ) : _) * ψ₁ w := by
    intro w d
    simp only [ψ₂, ψ₁, c, hsub, hpar, pow_val_add_intCast hζn, pow_val_add_intCast hζm]
    ring
  have h1 : adj (triSubHom m) D ψ₁ = (∑ d ∈ D, c d) • ψ₁ := by
    funext w
    show ∑ d ∈ D, ψ₁ (w - triSubHom m d) = (∑ d ∈ D, c d) * ψ₁ w
    rw [Finset.sum_congr rfl fun d _ => hψ₁ w d, Finset.sum_mul]
    exact Finset.sum_congr rfl fun d _ => mul_comm _ _
  have h2 : adj (triSubHom m) D ψ₂ = (∑ d ∈ D, c d) • ψ₂ +
      (∑ d ∈ D, c d * ((-(d.1 - d.2) : ℤ) : _)) • ψ₁ := by
    funext w
    show ∑ d ∈ D, ψ₂ (w - triSubHom m d) = (∑ d ∈ D, c d) * ψ₂ w +
      (∑ d ∈ D, c d * ((-(d.1 - d.2) : ℤ) : _)) * ψ₁ w
    rw [Finset.sum_congr rfl fun d _ => hψ₂ w d, Finset.sum_add_distrib, Finset.sum_mul,
      Finset.sum_mul]
  -- A single live cell at the origin pairs to 1 with psi1.
  have hc : pair ψ₁ (Pi.single 0 1) ≠ 0 := by
    simp [pair, Pi.single_apply, ψ₁]
  exact even_of_jordan hlam0 hμ0 h1 h2 hc hp

/-- 1 + ζ² is nonzero for a primitive m-th root of unity ζ with m ≥ 3. -/
theorem one_add_sq_ne_zero {m : ℕ} (hm3 : 3 ≤ m) {ζ : AlgebraicClosure (ZMod 2)}
    (hζ : IsPrimitiveRoot ζ m) : 1 + ζ ^ 2 ≠ 0 := by
  have h2K : (2 : AlgebraicClosure (ZMod 2)) = 0 := two_eq_zero_of_charTwo
  intro h
  exact hζ.pow_ne_one_of_pos_of_lt (by norm_num : 2 ≠ 0) (by omega) (by linear_combination h - h2K)

/-- The edge rule's square on the sub-torus: λ = 1 and ζ μ = 1 + ζ². -/
theorem triSub_even_triSE {m : ℕ} [NeZero m] [NeZero (2 * m)] (hm : Odd m) (hm3 : 3 ≤ m) {p : ℕ}
    (hp : IsEventualPeriod (gstep (triSubHom m) triSEOffsets) p) : Even p := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  have h2K : (2 : AlgebraicClosure (ZMod 2)) = 0 := two_eq_zero_of_charTwo
  have h0 : ζ ≠ 0 := ne_zero_of_pow_eq_one hζ.pow_eq_one
  have hsq : ζ ^ 2 - 1 ≠ 0 := by
    intro h
    exact one_add_sq_ne_zero hm3 hζ (by linear_combination h + h2K)
  refine triSub_even hζ.pow_eq_one ?_ ?_ hp
  · have hlam : ∑ d ∈ triSEOffsets, ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2) = 1 := by
      simp [triSEOffsets]
      field_simp
      linear_combination (ζ ^ 2 + ζ + 1) * h2K
    rw [hlam]
    exact one_ne_zero
  · have hμ : (∑ d ∈ triSEOffsets, ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2) *
        ((-(d.1 - d.2) : ℤ) : AlgebraicClosure (ZMod 2))) * ζ = ζ ^ 2 - 1 := by
      simp [triSEOffsets]
      field_simp
      ring
    intro h
    rw [h, zero_mul] at hμ
    exact hsq hμ.symm

/-- E + VO + VS's square on the sub-torus: ζ² λ = ζ² μ = (1 + ζ²)². -/
theorem triSub_even_triSEVOVS {m : ℕ} [NeZero m] [NeZero (2 * m)] (hm : Odd m) (hm3 : 3 ≤ m)
    {p : ℕ} (hp : IsEventualPeriod (gstep (triSubHom m) triSEVOVSOffsets) p) : Even p := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  have h2K : (2 : AlgebraicClosure (ZMod 2)) = 0 := two_eq_zero_of_charTwo
  have h0 : ζ ≠ 0 := ne_zero_of_pow_eq_one hζ.pow_eq_one
  have hsq : (1 + ζ ^ 2) ^ 2 ≠ 0 := pow_ne_zero 2 (one_add_sq_ne_zero hm3 hζ)
  refine triSub_even hζ.pow_eq_one ?_ ?_ hp
  · have hlam : (∑ d ∈ triSEVOVSOffsets, ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2)) * ζ ^ 2 =
        (1 + ζ ^ 2) ^ 2 := by
      simp [triSEVOVSOffsets]
      field_simp
      linear_combination (2 * ζ ^ 3 + 2 * ζ) * h2K
    intro h
    rw [h, zero_mul] at hlam
    exact hsq hlam.symm
  · have hμ : (∑ d ∈ triSEVOVSOffsets, ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2) *
        ((-(d.1 - d.2) : ℤ) : AlgebraicClosure (ZMod 2))) * ζ ^ 2 = (1 + ζ ^ 2) ^ 2 := by
      simp [triSEVOVSOffsets]
      field_simp
      linear_combination (-1 - ζ - ζ ^ 2 + ζ ^ 3) * h2K
    intro h
    rw [h, zero_mul] at hμ
    exact hsq hμ.symm

/-! ### The theorems -/

/-- If the period of R on the atlas's torus is 2^a P(m) with a ≤ v + 1, P(m) odd, and every
period of S on the sub-torus is even, then a = v + 1. -/
theorem atlasTriPeriod_exact_of_even {n v m a : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    [NeZero (2 * m)] (hm : Odd m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) {R : TriRule}
    {S : Finset (ℤ × ℤ)}
    (hR : ∀ c, gtriStep (triHom n) R (gtriStep (triHom n) R c) =
      Prod.map (gstep (triHom n) S) (gstep (triHom n) S) c)
    (heven : ∀ p, IsEventualPeriod (gstep (triSubHom m) S) p → Even p)
    (ha : a ≤ v + 1) (hP : atlasTriPeriod n R = 2 ^ a * period m S) :
    atlasTriPeriod n R = 2 ^ (v + 1) * period m S := by
  suffices hav : ¬ a ≤ v by rw [hP, show a = v + 1 by omega]
  intro hav
  have hdvd : atlasTriPeriod n R ∣ 2 ^ v * period m S := by
    rw [hP]; exact Nat.mul_dvd_mul_right (Nat.pow_dvd_pow 2 hav) _
  rw [atlasTriPeriod, gtriPeriod, ← isEventualPeriod_iff_dvd,
    isEventualPeriod_atlasTri_iff hv hn hR] at hdvd
  exact (Nat.not_even_iff_odd.2 (period_odd hm S)) (heven _ hdvd)

/-- **The edge rule's 2-part.** On the atlas's triangular torus of side n = 2^v m, with m odd,
m ≥ 3 and v ≥ 1, the triangle parity rule B13/S13 (`triE`) has period exactly 2^(v+1) P(m),
where P(m) is the period of its square's plane rule on the square torus of side m. -/
theorem atlasTriPeriod_triE_exact {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm3 : 3 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    atlasTriPeriod n triE = 2 ^ (v + 1) * period m triSEOffsets := by
  have : NeZero (2 * m) := ⟨by positivity⟩
  obtain ⟨a, ha, hP⟩ := atlasTriPeriod_triE hm hv hn
  exact atlasTriPeriod_exact_of_even hm hv hn
    (gtriStep_twice_of_cross (triHom n) rfl rfl grp_triE)
    (fun _ hp => triSub_even_triSE hm hm3 hp) (by omega) hP

/-- **The edge+vertex rule's 2-part.** The same for B1,3,...,11/S1,3,...,11 (`triEVOVS`). -/
theorem atlasTriPeriod_triEVOVS_exact {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm3 : 3 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    atlasTriPeriod n triEVOVS = 2 ^ (v + 1) * period m triSEVOVSOffsets := by
  have : NeZero (2 * m) := ⟨by positivity⟩
  obtain ⟨a, ha, hP⟩ := atlasTriPeriod_triEVOVS hm hv hn
  exact atlasTriPeriod_exact_of_even hm hv hn
    (gtriStep_twice (triHom n) grp_triEVOVS_up grp_triEVOVS_ud grp_triEVOVS_du
      grp_triEVOVS_down)
    (fun _ hp => triSub_even_triSEVOVS hm hm3 hp) ha hP

end LatticeProofs
