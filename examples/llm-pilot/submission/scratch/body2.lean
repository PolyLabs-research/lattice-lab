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
  set ι := ζ⁻¹ with hιdef
  have hι : ζ * ι = 1 := mul_inv_cancel₀ h0
  have hlam : (∑ d ∈ hexH1Offsets, c d) * ζ ^ 3 = (1 + ζ) * (1 + ζ ^ 2) * (1 + ζ ^ 3) := by
    simp only [c, hexH1Offsets]
    simp [inv_pow]
    linear_combination (ζ ^ 2 + ζ * (ζ * ι + 1) + (ζ * ι) ^ 2 + ζ * ι + 1) * hι - ζ ^ 3 * h2K
  have hμ : (∑ d ∈ hexH1Offsets, c d * ((-(d.1 + 2 * d.2) : ℤ) : _)) * ζ ^ 2 =
      (1 + ζ) * (1 + ζ ^ 3) := by
    simp only [c, hexH1Offsets]
    simp [inv_pow]
    linear_combination (-((ζ * ι + 1) * (1 + 2 * ι) + ζ)) * hι + (ζ ^ 5 - ζ - ι - 1) * h2K
  -- 1 + zeta^k is nonzero for 0 < k < m.
  have hne : ∀ k, 0 < k → k < m → 1 + ζ ^ k ≠ 0 := fun k hk hkm h =>
    hζ.pow_ne_one_of_pos_of_lt hk hkm (by linear_combination h - h2K)
  have hlam0 : (∑ d ∈ hexH1Offsets, c d) ≠ 0 := by
    intro h
    rw [h, zero_mul] at hlam
    exact mul_ne_zero (mul_ne_zero (hne 1 (by norm_num) (by omega))
      (hne 2 (by norm_num) (by omega))) (hne 3 (by norm_num) (by omega)) hlam.symm
  have hμ0 : (∑ d ∈ hexH1Offsets, c d * ((-(d.1 + 2 * d.2) : ℤ) : _)) ≠ 0 := by
    intro h
    rw [h, zero_mul] at hμ
    exact mul_ne_zero (hne 1 (by norm_num) (by omega)) (hne 3 (by norm_num) (by omega)) hμ.symm
  -- A single live cell at the origin pairs to 1 with psi1.
  have hc : pair ψ₁ (Pi.single 0 1) ≠ 0 := by
    simp [pair, Pi.single_apply, ψ₁]
  exact even_of_jordan hlam0 hμ0 h1 h2 hc hp
