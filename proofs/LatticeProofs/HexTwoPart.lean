/-
The LLM-central pilot's target (examples/llm-pilot/card.md): the hexagon law's 2-part.

`hexPeriod_eq_two_pow_mul` gives P = 2^a P(m) with a ≤ v + 1, where P is H1's period on the
hexagonal torus G of side n = 2^v m. It remains to rule out a ≤ v, that is P | 2^v P(m).

* **Frobenius and restriction.** 2^v steps of H1 are one step of 2^v H1, which acts on each coset
  of 2^v G as H1 acts on the sublattice torus G' = Z/2m × Z/m with (q, r) ↦ (q + 2r, r)
  (`hexSubHom`). Multiplication by 2^v embeds G' onto 2^v G (`hexSubMul`). So P | 2^v p exactly
  when p is a period of H1 on G'.
* **A Jordan block on G'.** G' ≅ Z/2 × (Z/m)², and the Z/2 coordinate is q mod 2. Take a
  primitive m-th root of unity ζ, the character ψ₁(a, b) = ζ^a ζ^b and ψ₂ = ψ₁ · [a even]. Then
  adj ψ₁ = λ ψ₁ and adj ψ₂ = λ ψ₂ + μ ψ₁, with λ = ζ^±1 + ζ^±2 + ζ^±3 (H1's eigenvalue at
  x = 1/ζ, y = 1/ζ³) and μ = ζ^±1 + ζ^±2 (the part of λ from the four translations with odd q).
  In characteristic 2, ζ³ λ = (1 + ζ)(1 + ζ²)(1 + ζ³) and ζ² μ = (1 + ζ)(1 + ζ³), so both are
  nonzero once ζ, ζ², ζ³ ≠ 1, that is m ≥ 5. `even_of_jordan` makes every period on G' even.
* P(m) is odd (`period_odd`), so it is not a period on G', and a = v + 1.
-/
import LatticeProofs

namespace LatticeProofs

open Finset

/-! ### The sublattice torus Z/2m × Z/m -/

/-- The torus Z/2m × Z/m with (q, r) ↦ (q + 2r mod 2m, r mod m). Multiplication by 2^v carries
it onto the subgroup 2^v G of the hexagonal torus G of side n = 2^v m. -/
def hexSubHom (m : ℕ) : ℤ × ℤ →+ ZMod (2 * m) × ZMod m :=
  ((Int.castAddHom (ZMod (2 * m))).comp (AddMonoidHom.fst ℤ ℤ + 2 • AddMonoidHom.snd ℤ ℤ)).prod
    ((Int.castAddHom (ZMod m)).comp (AddMonoidHom.snd ℤ ℤ))

theorem hexSubHom_apply (m : ℕ) (d : ℤ × ℤ) :
    hexSubHom m d = (((d.1 + 2 * d.2 : ℤ) : ZMod (2 * m)), ((d.2 : ℤ) : ZMod m)) := by
  obtain ⟨a, b⟩ := d
  ext <;> simp [hexSubHom, two_mul]

/-- Multiplication by N from the sublattice torus into the hexagonal torus of side n. -/
def hexSubMul (m n N : ℕ) (h1 : 2 * n ∣ N * (2 * m)) (h2 : n / 2 ∣ N * m) :
    ZMod (2 * m) × ZMod m →+ HexCell n :=
  (zmodMul (2 * m) (2 * n) N h1).prodMap (zmodMul m (n / 2) N h2)

theorem hexSubMul_hexSubHom {m n N : ℕ} (h1 : 2 * n ∣ N * (2 * m)) (h2 : n / 2 ∣ N * m)
    (d : ℤ × ℤ) : hexSubMul m n N h1 h2 (hexSubHom m d) = hexHom n (N • d) := by
  obtain ⟨a, b⟩ := d
  rw [hexSubHom_apply, Prod.smul_mk]
  simp only [hexSubMul, AddMonoidHom.coe_prodMap, Prod.map_apply, zmodMul_intCast]
  ext
  · simp [hexHom]
    ring
  · simp [hexHom]

theorem hexSubMul_injective {m n v : ℕ} [NeZero m] [NeZero (2 * m)] (hm : Odd m) (hv : 1 ≤ v)
    (hn : n = 2 ^ v * m) (h1 : 2 * n ∣ 2 ^ v * (2 * m)) (h2 : n / 2 ∣ 2 ^ v * m) :
    Function.Injective (hexSubMul m n (2 ^ v) h1 h2) := by
  have i1 := zmodMul_injective h1 fun a ha => by
    rw [hn, show 2 * (2 ^ v * m) = 2 ^ v * (2 * m) by ring] at ha
    exact Nat.dvd_of_mul_dvd_mul_left (by positivity) ha
  have i2 := zmodMul_injective h2 fun b hb => by
    rw [half_eq hv hn, show 2 ^ v * b = 2 ^ (v - 1) * (b * 2) by
      rw [mul_comm b, ← mul_assoc, ← pow_succ, Nat.sub_add_cancel hv]] at hb
    exact (Nat.coprime_two_right.2 hm).dvd_of_dvd_mul_right
      (Nat.dvd_of_mul_dvd_mul_left (by positivity) hb)
  exact i1.prodMap i2

/-! ### The Jordan block on the sublattice torus -/

/-- **Every period of H1 on the sublattice torus is even**, for odd m ≥ 5: its adjoint has a
Jordan block at the character ζ^a ζ^b, with the parity of a as the second weight. -/
theorem hexSub_even {m : ℕ} [NeZero m] [NeZero (2 * m)] (hm : Odd m) (hm5 : 5 ≤ m) {p : ℕ}
    (hp : IsEventualPeriod (gstep (hexSubHom m) hexH1Offsets) p) : Even p := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  have h2K : (2 : AlgebraicClosure (ZMod 2)) = 0 := two_eq_zero_of_charTwo
  have hζm : ζ ^ m = 1 := hζ.pow_eq_one
  have hζn : ζ ^ (2 * m) = 1 := by rw [pow_mul', hζm, one_pow]
  have h0 : ζ ≠ 0 := ne_zero_of_pow_eq_one hζm
  -- The weights: a character psi1 of the torus, and psi2 = psi1 on the cells with q even.
  let par : ZMod (2 * m) → AlgebraicClosure (ZMod 2) := fun t =>
    embed (AlgebraicClosure (ZMod 2)) (ZMod.castHom (dvd_mul_right 2 m) (ZMod 2) t)
  let ψ₁ : ZMod (2 * m) × ZMod m → AlgebraicClosure (ZMod 2) := fun w => ζ ^ w.1.val * ζ ^ w.2.val
  let ψ₂ : ZMod (2 * m) × ZMod m → AlgebraicClosure (ZMod 2) := fun w =>
    ζ ^ w.1.val * ζ ^ w.2.val * (1 + par w.1)
  -- psi1 at w - omega'(d), divided by psi1 at w.
  let c : ℤ × ℤ → AlgebraicClosure (ZMod 2) := fun d => ζ ^ (-(d.1 + 2 * d.2)) * ζ ^ (-d.2)
  have hsub : ∀ (w : ZMod (2 * m) × ZMod m) (d : ℤ × ℤ), w - hexSubHom m d =
      (w.1 + ((-(d.1 + 2 * d.2) : ℤ) : ZMod (2 * m)), w.2 + ((-d.2 : ℤ) : ZMod m)) := by
    intro w d
    rw [hexSubHom_apply]
    ext <;> simp [sub_eq_add_neg]
  have hψ₁ : ∀ w d, ψ₁ (w - hexSubHom m d) = ψ₁ w * c d := by
    intro w d
    simp only [ψ₁, c, hsub, pow_val_add_intCast hζn, pow_val_add_intCast hζm]
    ring
  have hpar : ∀ (t : ZMod (2 * m)) (k : ℤ), par (t + (k : ZMod (2 * m))) = par t + (k : _) := by
    intro t k
    simp [par, map_add, map_intCast]
  have hψ₂ : ∀ w d, ψ₂ (w - hexSubHom m d) =
      c d * ψ₂ w + c d * ((-(d.1 + 2 * d.2) : ℤ) : _) * ψ₁ w := by
    intro w d
    simp only [ψ₂, ψ₁, c, hsub, hpar, pow_val_add_intCast hζn, pow_val_add_intCast hζm]
    ring
  -- The Jordan block.
  have h1 : adj (hexSubHom m) hexH1Offsets ψ₁ = (∑ d ∈ hexH1Offsets, c d) • ψ₁ := by
    funext w
    show ∑ d ∈ hexH1Offsets, ψ₁ (w - hexSubHom m d) = (∑ d ∈ hexH1Offsets, c d) * ψ₁ w
    rw [Finset.sum_congr rfl fun d _ => hψ₁ w d, Finset.sum_mul]
    exact Finset.sum_congr rfl fun d _ => mul_comm _ _
  have h2 : adj (hexSubHom m) hexH1Offsets ψ₂ = (∑ d ∈ hexH1Offsets, c d) • ψ₂ +
      (∑ d ∈ hexH1Offsets, c d * ((-(d.1 + 2 * d.2) : ℤ) : _)) • ψ₁ := by
    funext w
    show ∑ d ∈ hexH1Offsets, ψ₂ (w - hexSubHom m d) = (∑ d ∈ hexH1Offsets, c d) * ψ₂ w +
      (∑ d ∈ hexH1Offsets, c d * ((-(d.1 + 2 * d.2) : ℤ) : _)) * ψ₁ w
    rw [Finset.sum_congr rfl fun d _ => hψ₂ w d, Finset.sum_add_distrib, Finset.sum_mul,
      Finset.sum_mul]
  -- lam and mu, explicitly: zeta^3 lam = (1 + zeta)(1 + zeta^2)(1 + zeta^3) and
  -- zeta^2 mu = (1 + zeta)(1 + zeta^3).
  set ι := ζ⁻¹
  have hι : ζ * ι = 1 := mul_inv_cancel₀ h0
  have hlam : (∑ d ∈ hexH1Offsets, c d) * ζ ^ 3 = (1 + ζ) * (1 + ζ ^ 2) * (1 + ζ ^ 3) := by
    simp only [c, hexH1Offsets]
    simp
    linear_combination (ζ ^ 2 + ζ * (ζ * ι + 1) + (ζ * ι) ^ 2 + ζ * ι + 1) * hι - ζ ^ 3 * h2K
  have hμ : (∑ d ∈ hexH1Offsets, c d * ((-(d.1 + 2 * d.2) : ℤ) : _)) * ζ ^ 2 =
      (1 + ζ) * (1 + ζ ^ 3) := by
    simp only [c, hexH1Offsets]
    simp
    linear_combination (-((ζ * ι + 1) * (1 + 2 * ι) + ζ)) * hι + (ζ ^ 5 - ζ - ι - 1) * h2K
  -- 1 + zeta^k is nonzero for 0 < k < m.
  have hne : ∀ k, k ≠ 0 → k < m → 1 + ζ ^ k ≠ 0 := fun k hk hkm h =>
    hζ.pow_ne_one_of_pos_of_lt hk hkm (by linear_combination h - h2K)
  have hne1 : 1 + ζ ≠ 0 := by simpa using hne 1 (by norm_num) (by omega)
  have hlam0 : (∑ d ∈ hexH1Offsets, c d) ≠ 0 := by
    intro h
    rw [h, zero_mul] at hlam
    exact mul_ne_zero (mul_ne_zero hne1 (hne 2 (by norm_num) (by omega)))
      (hne 3 (by norm_num) (by omega)) hlam.symm
  have hμ0 : (∑ d ∈ hexH1Offsets, c d * ((-(d.1 + 2 * d.2) : ℤ) : _)) ≠ 0 := by
    intro h
    rw [h, zero_mul] at hμ
    exact mul_ne_zero hne1 (hne 3 (by norm_num) (by omega)) hμ.symm
  -- A single live cell at the origin pairs to 1 with psi1.
  have hc : pair ψ₁ (Pi.single 0 1) ≠ 0 := by
    simp [pair, Pi.single_apply, ψ₁]
  exact even_of_jordan hlam0 hμ0 h1 h2 hc hp

/-- **The hexagon law's 2-part.** On the atlas's hexagonal torus of side n = 2^v m, with m odd,
m ≥ 5 and v ≥ 1, the parity rule H1 (B135/S135) has period exactly 2^(v+1) P(m), where P(m) is
its period on the square torus of side m in axial coordinates. -/
theorem hexPeriod_hexH1_exact {n v m : ℕ} [NeZero (2 * n)] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hm5 : 5 ≤ m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) :
    hexPeriod n hexH1Offsets = 2 ^ (v + 1) * period m hexH1Offsets := by
  have : NeZero (2 * m) := ⟨by positivity⟩
  obtain ⟨a, ha, hP⟩ := hexPeriod_eq_two_pow_mul hm hv hn hexH1Offsets
  suffices hav : ¬ a ≤ v by rw [hP, show a = v + 1 by omega]
  intro hav
  have h1 : 2 * n ∣ 2 ^ v * (2 * m) := ⟨1, by rw [hn]; ring⟩
  have h2 : n / 2 ∣ 2 ^ v * m := by
    rw [half_eq hv hn]
    exact Nat.mul_dvd_mul_right (Nat.pow_dvd_pow 2 (Nat.sub_le v 1)) m
  have hdvd : hexPeriod n hexH1Offsets ∣ 2 ^ v * period m hexH1Offsets := by
    rw [hP]; exact Nat.mul_dvd_mul_right (Nat.pow_dvd_pow 2 hav) _
  rw [hexPeriod, gperiod, ← isEventualPeriod_iff_dvd,
    ← isEventualPeriod_iterate_iff (k := 2 ^ v) (by positivity), gstep_iterate_two_pow,
    isEventualPeriod_restrict_iff (by positivity) (hexSubMul_hexSubHom h1 h2)
      (hexSubMul_injective hm hv hn h1 h2)] at hdvd
  exact (Nat.not_even_iff_odd.2 (period_odd hm hexH1Offsets)) (hexSub_even hm hm5 hdvd)

end LatticeProofs
