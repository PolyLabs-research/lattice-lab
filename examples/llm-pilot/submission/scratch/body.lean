  let par : ZMod (2 * m) → AlgebraicClosure (ZMod 2) := fun t =>
    embed (AlgebraicClosure (ZMod 2)) (ZMod.castHom (dvd_mul_right 2 m) (ZMod 2) t)
  let ψ₁ : ZMod (2 * m) × ZMod m → AlgebraicClosure (ZMod 2) := fun w => ζ ^ w.1.val * ζ ^ w.2.val
  let ψ₂ : ZMod (2 * m) × ZMod m → AlgebraicClosure (ZMod 2) := fun w =>
    ζ ^ w.1.val * ζ ^ w.2.val * (1 + par w.1)
  let c : ℤ × ℤ → AlgebraicClosure (ZMod 2) := fun d => ζ ^ (-(d.1 + 2 * d.2)) * ζ ^ (-d.2)
  let lam : AlgebraicClosure (ZMod 2) := ∑ d ∈ hexH1Offsets, c d
  let μ : AlgebraicClosure (ZMod 2) := ∑ d ∈ hexH1Offsets, c d * ((-(d.1 + 2 * d.2) : ℤ) : _)
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
    have e := hψ₁ w d
    simp only [ψ₁] at e
    simp only [ψ₂, ψ₁, e, hsub, hpar]
    rw [hsub] at e
    sorry
  have hlam : lam = 0 := by
    simp [lam, c, hexH1Offsets]
    sorry
  have hμ : μ = 0 := by
    simp [μ, c, hexH1Offsets]
    sorry
  sorry
