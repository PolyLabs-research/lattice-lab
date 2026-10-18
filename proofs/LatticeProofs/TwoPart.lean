/-
The XOR law's 2-part, exactly (docs/proofs.md).

`Tori.lean` reduces the 2-part at every even size to the single size 2m: if P(2m) = 2 P(m), then
P(2^v m) = 2^v P(m). Here is the size 2m.

A weight psi on cells gives a linear functional on configurations, `pair psi`. A step of the rule
turns it into the functional of the adjoint weight (`pair_gstep`). Suppose two weights form a
Jordan block: adj psi1 = lam psi1 and adj psi2 = lam psi2 + mu psi1, with lam, mu nonzero. Then
every period of the rule is even (`even_of_jordan`). Along the orbit of a configuration, the
second functional grows by t lam^(t-1) mu, and t is only periodic mod 2.

For the XOR rule B1357/S1357, and for N4, take weights that depend only on the cell's y
coordinate. The x-neighbours cancel in pairs, so on them the rule acts as rule 90 along y
(`sqN4D4_proj`, `sqN4_proj`). On a cycle of even length 2m, rule 90 has such a block: at a
primitive m-th root of unity zeta, the weights zeta^y and zeta^y [y even] have
lam = mu = zeta + 1/zeta, which is nonzero for odd m > 1.

* `period_two_mul_of_proj`: so P(2m) = 2 P(m) for every rule that acts as rule 90 along y;
* `period_sqN4D4`: **the XOR law's 2-part**. For n = 2^v m with m odd, m > 1 and v >= 1,
  P(n) = 2^v P(m);
* `period_sqN4D4_dvd`: with the bound, P(n) divides 2^v (2^s - 1) whenever 2^s = +-1 mod m.
-/
import LatticeProofs.Rules
import LatticeProofs.Tori

namespace LatticeProofs

open Finset

section Jordan

variable {G : Type*} [AddCommGroup G] [Fintype G] (ω : ℤ × ℤ →+ G) {K : Type*} [Field K]
  [CharP K 2]

/-- The linear functional on configurations with weight psi. -/
def pair (ψ : G → K) (c : G → ZMod 2) : K := ∑ v, embed K (c v) * ψ v

omit [Fintype G] [CharP K 2] in
/-- The adjoint of the rule D, acting on weights. -/
def adj (D : Finset (ℤ × ℤ)) (ψ : G → K) : G → K := fun w => ∑ d ∈ D, ψ (w - ω d)

/-- A step of the rule turns the functional of psi into that of adj psi. -/
theorem pair_gstep (D : Finset (ℤ × ℤ)) (ψ : G → K) (c : G → ZMod 2) :
    pair ψ (gstep ω D c) = pair (adj ω D ψ) c := by
  simp only [pair, gstep, adj, map_sum, Finset.sum_mul, Finset.mul_sum]
  rw [Finset.sum_comm]
  conv_rhs => rw [Finset.sum_comm]
  refine Finset.sum_congr rfl fun d _ => ?_
  exact Fintype.sum_equiv (Equiv.addRight (ω d)) _ _ fun v => by simp

omit [AddCommGroup G] in
theorem pair_add (ψ ψ' : G → K) (c : G → ZMod 2) : pair (ψ + ψ') c = pair ψ c + pair ψ' c := by
  simp [pair, mul_add, Finset.sum_add_distrib]

omit [AddCommGroup G] in
theorem pair_smul (a : K) (ψ : G → K) (c : G → ZMod 2) : pair (a • ψ) c = a * pair ψ c := by
  simp [pair, Finset.mul_sum, mul_left_comm]

variable {ω}

/-- **A Jordan block forces even periods.** If adj psi1 = lam psi1 and
adj psi2 = lam psi2 + mu psi1 with lam and mu nonzero, and some configuration has
pair psi1 c != 0, then every eventual period of the rule is even. -/
theorem even_of_jordan {D : Finset (ℤ × ℤ)} {ψ₁ ψ₂ : G → K} {lam μ : K} (hlam : lam ≠ 0)
    (hμ : μ ≠ 0) (h1 : adj ω D ψ₁ = lam • ψ₁) (h2 : adj ω D ψ₂ = lam • ψ₂ + μ • ψ₁)
    {c : G → ZMod 2} (hc : pair ψ₁ c ≠ 0) {p : ℕ} (hp : IsEventualPeriod (gstep ω D) p) :
    Even p := by
  have e1 : ∀ t, pair ψ₁ ((gstep ω D)^[t] c) = lam ^ t * pair ψ₁ c := by
    intro t
    induction t with
    | zero => simp
    | succ t ih => rw [Function.iterate_succ_apply', pair_gstep, h1, pair_smul, ih, pow_succ]; ring
  have e2 : ∀ t : ℕ, lam * pair ψ₂ ((gstep ω D)^[t] c) =
      lam ^ (t + 1) * pair ψ₂ c + t * lam ^ t * μ * pair ψ₁ c := by
    intro t
    induction t with
    | zero => simp
    | succ t ih =>
      rw [Function.iterate_succ_apply', pair_gstep, h2, pair_add, pair_smul, pair_smul, e1 t]
      push_cast
      linear_combination lam * ih
  obtain ⟨t, ht⟩ := hp
  have hA : lam ^ t * (lam ^ p - 1) * pair ψ₁ c = 0 := by
    have := (e1 (t + p)).symm.trans ((congrArg (fun f => pair ψ₁ (f c)) ht).trans (e1 t))
    linear_combination this
  have hlp : lam ^ p = 1 := by
    have := mul_eq_zero.1 hA
    rcases this with h | h
    · rcases mul_eq_zero.1 h with h' | h'
      · exact absurd h' (pow_ne_zero t hlam)
      · exact sub_eq_zero.1 h'
    · exact absurd h hc
  have hX := congrArg (fun f => pair ψ₂ (f c)) ht
  have key : (p : K) * (lam ^ t * μ * pair ψ₁ c) = 0 := by
    have e := e2 (t + p)
    have e' := e2 t
    rw [hX] at e
    have hpow : lam ^ (t + p) = lam ^ t := by rw [pow_add, hlp, mul_one]
    have hpow' : lam ^ (t + p + 1) = lam ^ (t + 1) := by rw [pow_succ, hpow, pow_succ]
    rw [hpow, hpow'] at e
    push_cast at e
    linear_combination e' - e
  have hne : lam ^ t * μ * pair ψ₁ c ≠ 0 := mul_ne_zero (mul_ne_zero (pow_ne_zero t hlam) hμ) hc
  have hp0 : (p : K) = 0 := (mul_eq_zero.1 key).resolve_right hne
  exact even_iff_two_dvd.2 ((CharP.cast_eq_zero_iff K 2 p).1 hp0)

end Jordan

/-! ### Rules that act as rule 90 along y -/

section RuleNinety

variable {K : Type*} [Field K] [CharP K 2]

/-- The XOR rule on weights that depend only on y: rule 90 along y. -/
theorem sqN4D4_proj {n : ℕ} (g : ZMod n → K) (w : Cell n) :
    ∑ d ∈ sqN4D4Offsets, g ((w - offsetHom n d).2) = g (w.2 + 1) + g (w.2 - 1) := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  simp [sqN4D4Offsets, offsetHom_apply, offset, sub_eq_add_neg]
  linear_combination (g (w.2 + 1) + g w.2 + g (w.2 + -1)) * h2

/-- N4 on weights that depend only on y: rule 90 along y. -/
theorem sqN4_proj {n : ℕ} (g : ZMod n → K) (w : Cell n) :
    ∑ d ∈ sqN4Offsets, g ((w - offsetHom n d).2) = g (w.2 + 1) + g (w.2 - 1) := by
  have h2 : (2 : K) = 0 := two_eq_zero_of_charTwo
  simp [sqN4Offsets, offsetHom_apply, offset, sub_eq_add_neg]
  linear_combination g w.2 * h2

omit [CharP K 2] in
theorem pow_val_add_intCast {n : ℕ} [NeZero n] {ζ : K} (hζ : ζ ^ n = 1) (t : ZMod n) (k : ℤ) :
    ζ ^ (t + (k : ZMod n)).val = ζ ^ t.val * ζ ^ k := by
  have h0 := ne_zero_of_pow_eq_one hζ
  rw [show t + (k : ZMod n) = (((t.val : ℤ) + k : ℤ) : ZMod n) by
    push_cast; rw [ZMod.natCast_zmod_val], pow_val_intCast hζ, zpow_add₀ h0, zpow_natCast]

/-- **P(2m) = 2 P(m)** for a rule that acts as rule 90 along y, at odd m > 1. -/
theorem period_two_mul_of_proj {m : ℕ} [NeZero m] [NeZero (2 * m)] (hm : Odd m) (hm1 : 1 < m)
    {D : Finset (ℤ × ℤ)}
    (hproj : ∀ (g : ZMod (2 * m) → AlgebraicClosure (ZMod 2)) (w : Cell (2 * m)),
      ∑ d ∈ D, g ((w - offsetHom (2 * m) d).2) = g (w.2 + 1) + g (w.2 - 1)) :
    period (2 * m) D = 2 * period m D := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  have h2K : (2 : AlgebraicClosure (ZMod 2)) = 0 := two_eq_zero_of_charTwo
  have hζn : ζ ^ (2 * m) = 1 := by rw [pow_mul', hζ.pow_eq_one, one_pow]
  have h0 : ζ ≠ 0 := ne_zero_of_pow_eq_one hζn
  -- The two weights: zeta^y, and zeta^y when y is even.
  let par : ZMod (2 * m) → AlgebraicClosure (ZMod 2) := fun t =>
    embed (AlgebraicClosure (ZMod 2)) (ZMod.castHom (dvd_mul_right 2 m) (ZMod 2) t)
  let g₁ : ZMod (2 * m) → AlgebraicClosure (ZMod 2) := fun t => ζ ^ t.val
  let g₂ : ZMod (2 * m) → AlgebraicClosure (ZMod 2) := fun t => ζ ^ t.val * (1 + par t)
  set b : AlgebraicClosure (ZMod 2) := ζ + ζ⁻¹
  have hup : ∀ t : ZMod (2 * m), ζ ^ (t + 1).val = ζ ^ t.val * ζ := fun t => by
    have := pow_val_add_intCast hζn t 1
    rwa [Int.cast_one, zpow_one] at this
  have hdown : ∀ t : ZMod (2 * m), ζ ^ (t - 1).val = ζ ^ t.val * ζ⁻¹ := fun t => by
    have := pow_val_add_intCast hζn t (-1)
    rwa [Int.cast_neg, Int.cast_one, ← sub_eq_add_neg, zpow_neg_one] at this
  have hpar_up : ∀ t, par (t + 1) = par t + 1 := fun t => by simp [par]
  have hpar_down : ∀ t, par (t - 1) = par t - 1 := fun t => by simp [par]
  have h1 : adj (offsetHom (2 * m)) D (fun v => g₁ v.2) = b • fun v => g₁ v.2 := by
    funext w
    show ∑ d ∈ D, g₁ ((w - offsetHom (2 * m) d).2) = b * g₁ w.2
    rw [hproj g₁ w]
    simp only [g₁, hup, hdown, b]
    ring
  have h2 : adj (offsetHom (2 * m)) D (fun v => g₂ v.2) =
      b • (fun v => g₂ v.2) + b • fun v => g₁ v.2 := by
    funext w
    show ∑ d ∈ D, g₂ ((w - offsetHom (2 * m) d).2) = b * g₂ w.2 + b * g₁ w.2
    rw [hproj g₂ w]
    simp only [g₁, g₂, hup, hdown, hpar_up, hpar_down, b]
    linear_combination (-(ζ ^ w.2.val * ζ⁻¹)) * h2K
  -- b = zeta + 1/zeta is nonzero: otherwise zeta^2 = 1 and m divides 2.
  have hb : b ≠ 0 := by
    intro hb0
    have hsq : ζ ^ 2 = 1 := by
      have : ζ * b = 0 := by rw [hb0, mul_zero]
      have e : ζ * b = ζ ^ 2 + 1 := by simp only [b]; rw [mul_add, mul_inv_cancel₀ h0, sq]
      linear_combination e.symm.trans this - h2K
    have hdvd := (hζ.pow_eq_one_iff_dvd 2).1 hsq
    have := Nat.le_of_dvd (by norm_num) hdvd
    obtain rfl : m = 2 := by omega
    exact absurd hm (by decide)
  -- A single live cell at the origin pairs to 1 with the first weight.
  have hc : pair (fun v : Cell (2 * m) => g₁ v.2) (Pi.single 0 1) ≠ 0 := by
    simp [pair, Pi.single_apply, g₁]
  have heven : Even (period (2 * m) D) :=
    even_of_jordan hb hb h1 h2 hc (eventualPeriod_spec (step (2 * m) D)).2
  obtain ⟨a, ha, hP⟩ := period_eq_two_pow_mul (v := 1) (by ring : 2 * m = 2 ^ 1 * m) D
  have hodd := period_odd hm D
  interval_cases a
  · rw [pow_zero, one_mul] at hP
    rw [hP] at heven
    exact absurd heven (Nat.not_even_iff_odd.2 hodd)
  · rw [hP, pow_one]

end RuleNinety

/-- **The XOR law's 2-part.** On the square torus of side n = 2^v m, with m odd, m > 1 and v >= 1,
the eight-neighbour parity rule B1357/S1357 has period exactly 2^v P(m). -/
theorem period_sqN4D4 {n v m : ℕ} [NeZero n] [NeZero m] (hm : Odd m) (hm1 : 1 < m) (hv : 1 ≤ v)
    (hn : n = 2 ^ v * m) : period n sqN4D4Offsets = 2 ^ v * period m sqN4D4Offsets := by
  have : NeZero (2 * m) := ⟨by positivity⟩
  exact period_eq_two_pow_mul_of_double hv hn _
    (period_two_mul_of_proj hm hm1 fun g w => sqN4D4_proj g w)

/-- The same for N4 (the sigma automaton). -/
theorem period_sqN4 {n v m : ℕ} [NeZero n] [NeZero m] (hm : Odd m) (hm1 : 1 < m) (hv : 1 ≤ v)
    (hn : n = 2 ^ v * m) : period n sqN4Offsets = 2 ^ v * period m sqN4Offsets := by
  have : NeZero (2 * m) := ⟨by positivity⟩
  exact period_eq_two_pow_mul_of_double hv hn _
    (period_two_mul_of_proj hm hm1 fun g w => sqN4_proj g w)

/-- **The XOR law's bound at every size.** With n = 2^v m as above and 2^s = +-1 mod m, the period
divides 2^v (2^s - 1). The XOR law says it equals 2^v (2^sord(m) - 1). With `period_sqN4D4`, that
law holds at every n exactly when it holds at every odd part m. -/
theorem period_sqN4D4_dvd {n v m s : ℕ} [NeZero n] [NeZero m] (hm : Odd m) (hm1 : 1 < m)
    (hv : 1 ≤ v) (hn : n = 2 ^ v * m) (hs : (2 : ZMod m) ^ s = 1 ∨ (2 : ZMod m) ^ s = -1) :
    period n sqN4D4Offsets ∣ 2 ^ v * (2 ^ s - 1) := by
  rw [period_sqN4D4 hm hm1 hv hn]
  refine Nat.mul_dvd_mul_left _ ?_
  rcases hs with hs | hs
  · exact period_dvd_two_pow_sub_one hm _ hs
  · exact period_dvd_two_pow_sub_one_of_symm hm sqN4D4Offsets_symm hs

end LatticeProofs
