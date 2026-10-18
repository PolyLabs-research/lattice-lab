/-
The bridge from periods to eigenvalues (docs/proofs.md).

A linear rule on the m x m torus has a neighbourhood D, a finite set of integer offsets: each cell
becomes the sum mod 2 of the cells at its offsets. Take a field K of characteristic 2 with a
primitive m-th root of unity zeta; one exists exactly when m is odd. The rule acts diagonally on
the torus's characters chi_{j,k}(v) = zeta^(j v_1 + k v_2), with eigenvalue
lam_{j,k} = sum over d in D of chi_{j,k}(-d).

* `hat_step`: one step multiplies the transform at (j, k) by lam_{j,k}.
* `inversion`: a configuration is recovered from its transform, because m is a unit in K.
* `isPeriod_iff`: p is a period exactly when every eigenvalue is 0 or a p-th root of unity.
* `period_eq_eigenLcm`: the period is the lcm of the multiplicative orders of the nonzero
  eigenvalues, and `isPeriod_iff_period_dvd`: every period is a multiple of it.
* `lam_eq_ev`: lam_{j,k} is the rule's Laurent polynomial at x = zeta^-j, y = zeta^-k.
* `exists_primitiveRoot`: for odd m, the algebraic closure of GF(2) is such a field.
* `period_dvd_two_pow_sub_one`, `period_dvd_two_pow_sub_one_of_symm`: the bound. The period
  divides 2^r - 1 when 2^r = 1 mod m, and for a symmetric rule also when 2^r = -1 mod m.
* `period_odd`: on an odd torus the period is odd.

`IsEventualPeriod` and `isEventualPeriod_iff_dvd` hold for any map of a finite set: its eventual
periods are the multiples of the least one.
-/
import LatticeProofs.Eigen
import Mathlib.Algebra.Field.GeomSum
import Mathlib.Data.ZMod.Basic
import Mathlib.FieldTheory.Finite.Basic
import Mathlib.RingTheory.RootsOfUnity.AlgebraicallyClosed
import Mathlib.RingTheory.RootsOfUnity.PrimitiveRoots

namespace LatticeProofs

open Finset

section Eventual

variable {α : Type*} (f : α → α)

/-- p is an eventual period of f: from some time t on, f^[t + p] = f^[t]. -/
def IsEventualPeriod (p : ℕ) : Prop := ∃ t, f^[t + p] = f^[t]

/-- The least positive eventual period. -/
noncomputable def eventualPeriod : ℕ := sInf {p | 0 < p ∧ IsEventualPeriod f p}

/-- On a finite set, some positive p is an eventual period. -/
theorem exists_isEventualPeriod [Finite α] : ∃ p, 0 < p ∧ IsEventualPeriod f p := by
  obtain ⟨a, b, hab, h⟩ := Finite.exists_ne_map_eq_of_infinite fun n : ℕ => f^[n]
  rcases Nat.lt_or_gt_of_ne hab with hlt | hlt
  · exact ⟨b - a, by omega, a, by rw [Nat.add_sub_of_le hlt.le]; exact h.symm⟩
  · exact ⟨a - b, by omega, b, by rw [Nat.add_sub_of_le hlt.le]; exact h⟩

theorem eventualPeriod_spec [Finite α] :
    0 < eventualPeriod f ∧ IsEventualPeriod f (eventualPeriod f) :=
  Nat.sInf_mem (exists_isEventualPeriod f)

variable {f}

/-- A period from time t is a period from every later time, and so is each of its multiples. -/
theorem iterate_add_mul_eq {t p : ℕ} (h : f^[t + p] = f^[t]) (s q : ℕ) :
    f^[t + s + q * p] = f^[t + s] := by
  induction q with
  | zero => simp
  | succ q ih =>
    rw [show t + s + (q + 1) * p = (s + q * p) + (t + p) by ring, Function.iterate_add, h,
      ← Function.iterate_add, show s + q * p + t = t + s + q * p by ring, ih]

/-- On a finite set, the eventual periods are exactly the multiples of the least one. -/
theorem isEventualPeriod_iff_dvd [Finite α] {p : ℕ} :
    IsEventualPeriod f p ↔ eventualPeriod f ∣ p := by
  obtain ⟨hP, t', ht'⟩ := eventualPeriod_spec f
  set P := eventualPeriod f
  constructor
  · rintro ⟨t, ht⟩
    obtain ⟨q, r, hrP, hpq⟩ : ∃ q r, r < P ∧ r + P * q = p :=
      ⟨p / P, p % P, Nat.mod_lt p hP, Nat.mod_add_div p P⟩
    have hr : f^[(t + t') + r] = f^[t + t'] := by
      calc f^[(t + t') + r] = f^[t' + (t + r) + q * P] := by
            rw [iterate_add_mul_eq ht' (t + r) q]; congr 1; ring
        _ = f^[t + t' + 1 * p] := by congr 1; rw [← hpq]; ring
        _ = f^[t + t'] := iterate_add_mul_eq ht t' 1
    rcases Nat.eq_zero_or_pos r with h0 | hr0
    · exact ⟨q, by rw [← hpq, h0, zero_add]⟩
    · have hle : P ≤ r := Nat.sInf_le ⟨hr0, t + t', hr⟩
      exact absurd hle (not_le.2 hrP)
  · rintro ⟨c, rfl⟩
    refine ⟨t', ?_⟩
    simpa [mul_comm] using iterate_add_mul_eq ht' 0 c

end Eventual

section Torus

variable (m : ℕ) [NeZero m]

/-- A cell of the m x m torus. -/
abbrev Cell := ZMod m × ZMod m

/-- A configuration: a value in GF(2) at every cell. -/
abbrev Config := Cell m → ZMod 2

/-- The cell an integer offset reaches from the origin. -/
def offset (d : ℤ × ℤ) : Cell m := ((d.1 : ZMod m), (d.2 : ZMod m))

/-- One step of the linear rule with neighbourhood D: every cell becomes the sum mod 2 of the
cells at its offsets. -/
def step (D : Finset (ℤ × ℤ)) (s : Config m) : Config m :=
  fun v => ∑ d ∈ D, s (v + offset m d)

/-- p is a period of the rule on the m-torus: from some time on, every configuration recurs
after p steps. -/
def IsPeriod (D : Finset (ℤ × ℤ)) (p : ℕ) : Prop := IsEventualPeriod (step m D) p

/-- Some positive p is a period: there are only finitely many maps of configurations. -/
theorem exists_isPeriod (D : Finset (ℤ × ℤ)) : ∃ p, 0 < p ∧ IsPeriod m D p :=
  exists_isEventualPeriod _

/-- The period of the rule on the m-torus: its least positive period. -/
noncomputable def period (D : Finset (ℤ × ℤ)) : ℕ := eventualPeriod (step m D)

/-- Every period is a multiple of the period. -/
theorem isPeriod_iff_period_dvd (D : Finset (ℤ × ℤ)) (p : ℕ) : IsPeriod m D p ↔ period m D ∣ p :=
  isEventualPeriod_iff_dvd

omit [NeZero m] in
theorem step_empty (s : Config m) : step m ∅ s = 0 := by
  funext v
  simp [step]

end Torus

/-- If x^m = 1, then x^a depends only on a mod m. -/
theorem pow_eq_pow_of_cast_eq {M : Type*} [Monoid M] {m : ℕ} {x : M} (hx : x ^ m = 1) {a b : ℕ}
    (h : (a : ZMod m) = b) : x ^ a = x ^ b := by
  have h' := (ZMod.natCast_eq_natCast_iff' a b m).1 h
  rw [← Nat.div_add_mod a m, ← Nat.div_add_mod b m, pow_add, pow_add, pow_mul, pow_mul, hx,
    one_pow, one_pow, h']

/-- n divides k p exactly when n / gcd(n, k) divides p. -/
theorem dvd_mul_iff_div_gcd_dvd {n k : ℕ} (hk : 0 < k) (p : ℕ) :
    n ∣ k * p ↔ n / Nat.gcd n k ∣ p := by
  have hg : 0 < Nat.gcd n k := Nat.gcd_pos_of_pos_right n hk
  have hn : n / Nat.gcd n k * Nat.gcd n k = n := Nat.div_mul_cancel (Nat.gcd_dvd_left n k)
  have hk' : k / Nat.gcd n k * Nat.gcd n k = k := Nat.div_mul_cancel (Nat.gcd_dvd_right n k)
  constructor
  · intro h
    apply (Nat.coprime_div_gcd_div_gcd hg).dvd_of_dvd_mul_left
    apply Nat.dvd_of_mul_dvd_mul_right hg
    calc n / Nat.gcd n k * Nat.gcd n k = n := hn
      _ ∣ k * p := h
      _ = k / Nat.gcd n k * p * Nat.gcd n k := by
        conv_lhs => rw [← hk']
        ring
  · intro h
    calc n = n / Nat.gcd n k * Nat.gcd n k := hn.symm
      _ ∣ p * k := Nat.mul_dvd_mul h (Nat.gcd_dvd_right n k)
      _ = k * p := mul_comm p k

/-- If the multiples of P₁ are the p with P₀ dividing k p, then P₁ = P₀ / gcd(P₀, k). -/
theorem eq_div_gcd_of_dvd_iff {P₁ P₀ k : ℕ} (hk : 0 < k) (h : ∀ p, P₁ ∣ p ↔ P₀ ∣ k * p) :
    P₁ = P₀ / Nat.gcd P₀ k :=
  Nat.dvd_antisymm ((h _).2 ((dvd_mul_iff_div_gcd_dvd hk _).2 dvd_rfl))
    ((dvd_mul_iff_div_gcd_dvd hk _).1 ((h _).1 dvd_rfl))

section Characters

variable {m : ℕ} [NeZero m] {K : Type*} [Field K]

/-- The character (j, k) of the torus, with values in K. -/
def chi (ζ : K) (j k : ℕ) (v : Cell m) : K := ζ ^ (j * v.1.val + k * v.2.val)

/-- The eigenvalue of the rule with neighbourhood D at the character (j, k). -/
def lam (m : ℕ) [NeZero m] (ζ : K) (D : Finset (ℤ × ℤ)) (j k : ℕ) : K :=
  ∑ d ∈ D, chi ζ j k (-offset m d)

variable {ζ : K}

theorem chi_add (hζ : ζ ^ m = 1) (j k : ℕ) (v w : Cell m) :
    chi ζ j k (v + w) = chi ζ j k v * chi ζ j k w := by
  unfold chi
  rw [← pow_add]
  apply pow_eq_pow_of_cast_eq hζ
  simp only [Nat.cast_add, Nat.cast_mul, ZMod.natCast_zmod_val, Prod.fst_add, Prod.snd_add]
  ring

omit [NeZero m] in
theorem chi_zero (j k : ℕ) : chi ζ j k (0 : Cell m) = 1 := by
  simp [chi]

/-- The sum of a character of Z/m over Z/m. -/
theorem sum_pow_val (hζ : IsPrimitiveRoot ζ m) (u : ZMod m) :
    ∑ j ∈ range m, ζ ^ (j * u.val) = if u = 0 then (m : K) else 0 := by
  split_ifs with hu
  · simp [hu]
  · have h1 : ζ ^ u.val ≠ 1 := by
      rw [Ne, hζ.pow_eq_one_iff_dvd]
      intro hd
      exact hu ((ZMod.val_eq_zero u).1 (Nat.eq_zero_of_dvd_of_lt hd (ZMod.val_lt u)))
    have hm1 : (ζ ^ u.val) ^ m = 1 := by
      rw [← pow_mul, mul_comm, pow_mul, hζ.pow_eq_one, one_pow]
    simp_rw [mul_comm _ u.val, pow_mul]
    rw [geom_sum_eq h1, hm1, sub_self, zero_div]

/-- The sum of a character of the torus over all characters. -/
theorem sum_chi (hζ : IsPrimitiveRoot ζ m) (u : Cell m) :
    ∑ j ∈ range m, ∑ k ∈ range m, chi ζ j k u = if u = 0 then (m : K) ^ 2 else 0 := by
  simp only [chi, pow_add]
  simp_rw [← Finset.mul_sum, ← Finset.sum_mul]
  rw [sum_pow_val hζ, sum_pow_val hζ]
  rcases u with ⟨a, b⟩
  by_cases ha : a = 0 <;> by_cases hb : b = 0 <;> simp [ha, hb, sq, Prod.mk_eq_zero]

theorem sum_comm3 {α β γ M : Type*} [AddCommMonoid M] (s : Finset α) (t : Finset β)
    (u : Finset γ) (F : α → β → γ → M) :
    ∑ a ∈ s, ∑ b ∈ t, ∑ c ∈ u, F a b c = ∑ c ∈ u, ∑ a ∈ s, ∑ b ∈ t, F a b c :=
  calc _ = ∑ a ∈ s, ∑ c ∈ u, ∑ b ∈ t, F a b c := Finset.sum_congr rfl fun _ _ => Finset.sum_comm
    _ = _ := Finset.sum_comm

/-- A neighbourhood's Laurent polynomial, evaluated at x, y in K. -/
def ev (D : Finset (ℤ × ℤ)) (x y : K) : K := ∑ d ∈ D, x ^ d.1 * y ^ d.2

theorem ne_zero_of_pow_eq_one {x : K} (hx : x ^ m = 1) : x ≠ 0 := by
  rintro rfl
  rw [zero_pow (NeZero.ne m)] at hx
  exact zero_ne_one hx

theorem zpow_emod_of_pow_eq_one {x : K} (hx : x ^ m = 1) (a : ℤ) : x ^ (a % (m : ℤ)) = x ^ a := by
  have hx0 := ne_zero_of_pow_eq_one hx
  conv_rhs => rw [← Int.emod_add_mul_ediv a m]
  rw [zpow_add₀ hx0, zpow_mul, zpow_natCast, hx, one_zpow, mul_one]

theorem pow_val_intCast {x : K} (hx : x ^ m = 1) (a : ℤ) : x ^ (a : ZMod m).val = x ^ a := by
  rw [← zpow_natCast, ZMod.val_intCast, zpow_emod_of_pow_eq_one hx]

/-- The eigenvalue at (j, k) is the rule's Laurent polynomial at x = zeta^-j, y = zeta^-k. -/
theorem lam_eq_ev (hζ : ζ ^ m = 1) (D : Finset (ℤ × ℤ)) (j k : ℕ) :
    lam m ζ D j k = ev D (ζ ^ j)⁻¹ (ζ ^ k)⁻¹ := by
  have hj : (ζ ^ j) ^ m = 1 := by rw [← pow_mul, mul_comm, pow_mul, hζ, one_pow]
  have hk : (ζ ^ k) ^ m = 1 := by rw [← pow_mul, mul_comm, pow_mul, hζ, one_pow]
  unfold lam ev
  refine Finset.sum_congr rfl fun d _ => ?_
  simp only [chi, offset, Prod.fst_neg, Prod.snd_neg, pow_add, pow_mul, ← Int.cast_neg,
    pow_val_intCast hj, pow_val_intCast hk, inv_zpow']

end Characters

section Fourier

variable {m : ℕ} [NeZero m] {K : Type*} [Field K] [CharP K 2] {ζ : K}

/-- GF(2) inside K. -/
def embed (K : Type*) [Field K] [CharP K 2] : ZMod 2 →+* K := ZMod.castHom (dvd_refl 2) K

theorem embed_injective : Function.Injective (embed K) := ZMod.castHom_injective K

variable (ζ) in
/-- The transform of a configuration at the character (j, k). -/
def hat (s : Config m) (j k : ℕ) : K := ∑ v, embed K (s v) * chi ζ j k v

/-- One step multiplies the transform by the eigenvalue. -/
theorem hat_step (hζ : ζ ^ m = 1) (D : Finset (ℤ × ℤ)) (s : Config m) (j k : ℕ) :
    hat ζ (step m D s) j k = lam m ζ D j k * hat ζ s j k := by
  unfold hat lam step
  simp only [map_sum, Finset.sum_mul]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl fun d _ => ?_
  rw [Finset.mul_sum]
  refine Fintype.sum_equiv (Equiv.addRight (offset m d)) _ _ fun v => ?_
  have h : chi ζ j k (-offset m d) * chi ζ j k (v + offset m d) = chi ζ j k v := by
    rw [← chi_add hζ]; congr 1; abel
  simp only [Equiv.coe_addRight]
  rw [← h]
  ring

/-- So t steps multiply it by the eigenvalue's t-th power. -/
theorem hat_iterate (hζ : ζ ^ m = 1) (D : Finset (ℤ × ℤ)) (s : Config m) (j k t : ℕ) :
    hat ζ ((step m D)^[t] s) j k = lam m ζ D j k ^ t * hat ζ s j k := by
  induction t with
  | zero => simp
  | succ t ih => rw [Function.iterate_succ_apply', hat_step hζ, ih, pow_succ]; ring

/-- Fourier inversion: a configuration is recovered from its transform. -/
theorem inversion (hζ : IsPrimitiveRoot ζ m) (s : Config m) (a : Cell m) :
    ∑ j ∈ range m, ∑ k ∈ range m, hat ζ s j k * chi ζ j k (-a) =
      (m : K) ^ 2 * embed K (s a) := by
  have h1 := hζ.pow_eq_one
  have h : ∀ j k, hat ζ s j k * chi ζ j k (-a) = ∑ v, embed K (s v) * chi ζ j k (v + -a) := by
    intro j k
    rw [hat, Finset.sum_mul]
    refine Finset.sum_congr rfl fun v _ => ?_
    rw [chi_add h1, mul_assoc]
  simp_rw [h]
  rw [sum_comm3]
  simp_rw [← Finset.mul_sum, sum_chi hζ, add_neg_eq_zero, mul_ite, mul_zero]
  simp [mul_comm]

/-- The transform of a single live cell at the origin is 1 everywhere. -/
theorem hat_single (j k : ℕ) : hat ζ (Pi.single (0 : Cell m) (1 : ZMod 2)) j k = 1 := by
  rw [hat, Finset.sum_eq_single (0 : Cell m)]
  · simp [chi_zero]
  · intro v _ hv
    simp [hv]
  · intro h
    exact absurd (Finset.mem_univ _) h

/-- **The bridge.** p is a period of the rule on the m-torus exactly when every eigenvalue is
either 0 or a p-th root of unity. -/
theorem isPeriod_iff (hζ : IsPrimitiveRoot ζ m) (D : Finset (ℤ × ℤ)) (p : ℕ) :
    IsPeriod m D p ↔ ∀ j < m, ∀ k < m, lam m ζ D j k = 0 ∨ lam m ζ D j k ^ p = 1 := by
  have h1 := hζ.pow_eq_one
  constructor
  · rintro ⟨t, ht⟩ j _ k _
    have h := congrArg (fun f => hat ζ (f (Pi.single (0 : Cell m) (1 : ZMod 2))) j k) ht
    simp only [hat_iterate h1, hat_single, mul_one, pow_add] at h
    by_cases hl : lam m ζ D j k = 0
    · exact Or.inl hl
    · exact Or.inr ((mul_eq_left₀ (pow_ne_zero t hl)).1 h)
  · intro h
    refine ⟨1, funext fun s => funext fun a => ?_⟩
    have hm : (m : K) ^ 2 ≠ 0 := pow_ne_zero 2 hζ.neZero'.out
    apply embed_injective (K := K)
    apply mul_left_cancel₀ hm
    rw [← inversion hζ ((step m D)^[1 + p] s) a, ← inversion hζ ((step m D)^[1] s) a]
    refine Finset.sum_congr rfl fun j hj => Finset.sum_congr rfl fun k hk => ?_
    rw [hat_iterate h1, hat_iterate h1]
    rcases h j (Finset.mem_range.1 hj) k (Finset.mem_range.1 hk) with h0 | hp
    · simp [h0]
    · rw [pow_add, hp, mul_one]

/-- The bridge with orders: p is a period exactly when it is a multiple of the order of every
nonzero eigenvalue. -/
theorem isPeriod_iff_orderOf_dvd (hζ : IsPrimitiveRoot ζ m) (D : Finset (ℤ × ℤ)) (p : ℕ) :
    IsPeriod m D p ↔ ∀ j < m, ∀ k < m, lam m ζ D j k ≠ 0 → orderOf (lam m ζ D j k) ∣ p := by
  rw [isPeriod_iff hζ]
  simp only [orderOf_dvd_iff_pow_eq_one, ne_eq, or_iff_not_imp_left]

open Classical in
/-- The lcm of the multiplicative orders of the nonzero eigenvalues. -/
noncomputable def eigenLcm (m : ℕ) [NeZero m] (ζ : K) (D : Finset (ℤ × ℤ)) : ℕ :=
  ((range m ×ˢ range m).filter fun jk => lam m ζ D jk.1 jk.2 ≠ 0).lcm
    fun jk => orderOf (lam m ζ D jk.1 jk.2)

theorem isPeriod_iff_eigenLcm_dvd (hζ : IsPrimitiveRoot ζ m) (D : Finset (ℤ × ℤ)) (p : ℕ) :
    IsPeriod m D p ↔ eigenLcm m ζ D ∣ p := by
  rw [isPeriod_iff_orderOf_dvd hζ, eigenLcm, Finset.lcm_dvd_iff]
  simp only [Finset.mem_filter, Finset.mem_product, Finset.mem_range, Prod.forall]
  constructor
  · rintro h j k ⟨⟨hj, hk⟩, hl⟩
    exact h j hj k hk hl
  · intro h j hj k hk hl
    exact h j k ⟨⟨hj, hk⟩, hl⟩

/-- **The period is the lcm of the multiplicative orders of the nonzero eigenvalues.** -/
theorem period_eq_eigenLcm (hζ : IsPrimitiveRoot ζ m) (D : Finset (ℤ × ℤ)) :
    period m D = eigenLcm m ζ D :=
  Nat.dvd_antisymm
    ((isPeriod_iff_period_dvd m D _).1 ((isPeriod_iff_eigenLcm_dvd hζ D _).2 dvd_rfl))
    ((isPeriod_iff_eigenLcm_dvd hζ D _).1 ((isPeriod_iff_period_dvd m D _).2 dvd_rfl))

theorem hat_add (s s' : Config m) (j k : ℕ) :
    hat ζ (s + s') j k = hat ζ s j k + hat ζ s' j k := by
  simp only [hat, Pi.add_apply, map_add, add_mul, Finset.sum_add_distrib]

/-- Two configurations with the same transform are equal. -/
theorem eq_of_hat_eq (hζ : IsPrimitiveRoot ζ m) {s s' : Config m}
    (h : ∀ j < m, ∀ k < m, hat ζ s j k = hat ζ s' j k) : s = s' := by
  funext a
  have hm : (m : K) ^ 2 ≠ 0 := pow_ne_zero 2 hζ.neZero'.out
  apply embed_injective (K := K)
  apply mul_left_cancel₀ hm
  rw [← inversion hζ s a, ← inversion hζ s' a]
  refine Finset.sum_congr rfl fun j hj => Finset.sum_congr rfl fun k hk => ?_
  rw [h j (Finset.mem_range.1 hj) k (Finset.mem_range.1 hk)]

end Fourier

/-- For odd m, the algebraic closure of GF(2) has a primitive m-th root of unity. -/
theorem exists_primitiveRoot {m : ℕ} [NeZero m] (hm : Odd m) :
    ∃ ζ : AlgebraicClosure (ZMod 2), IsPrimitiveRoot ζ m := by
  have : NeZero ((m : ℕ) : ZMod 2) :=
    ⟨by rw [ZMod.natCast_eq_one_iff_odd.2 hm]; exact one_ne_zero⟩
  exact HasEnoughRootsOfUnity.exists_isPrimitiveRoot _ m

section Bound

variable {m : ℕ} [NeZero m] {K : Type*} [Field K] [CharP K 2] {ζ : K}

/-- Frobenius: if 2^r = 1 mod m, every eigenvalue is fixed by the 2^r-th power. -/
theorem lam_pow_two_pow (hζ : ζ ^ m = 1) (D : Finset (ℤ × ℤ)) (j k : ℕ) {r : ℕ}
    (hr : (2 : ZMod m) ^ r = 1) : lam m ζ D j k ^ 2 ^ r = lam m ζ D j k := by
  unfold lam
  rw [sum_pow_char_pow]
  refine Finset.sum_congr rfl fun d _ => ?_
  unfold chi
  rw [← pow_mul]
  apply pow_eq_pow_of_cast_eq hζ
  rw [Nat.cast_mul, Nat.cast_pow, Nat.cast_ofNat, hr, mul_one]

/-- If 2^s = -1 mod m and the neighbourhood is symmetric, every eigenvalue is fixed by the
2^s-th power. -/
theorem lam_pow_two_pow_of_symm (hζ : ζ ^ m = 1) {D : Finset (ℤ × ℤ)}
    (hD : ∀ d ∈ D, -d ∈ D) (j k : ℕ) {s : ℕ} (hs : (2 : ZMod m) ^ s = -1) :
    lam m ζ D j k ^ 2 ^ s = lam m ζ D j k := by
  unfold lam
  rw [sum_pow_char_pow]
  refine Finset.sum_nbij' Neg.neg Neg.neg hD hD (fun d _ => neg_neg d) (fun d _ => neg_neg d)
    fun d _ => ?_
  unfold chi
  rw [← pow_mul]
  apply pow_eq_pow_of_cast_eq hζ
  simp only [Nat.cast_mul, Nat.cast_add, Nat.cast_pow, Nat.cast_ofNat, hs, ZMod.natCast_zmod_val,
    offset, Prod.fst_neg, Prod.snd_neg, Prod.fst_neg, Int.cast_neg, neg_neg]
  ring

omit [CharP K 2] in
theorem eq_zero_or_pow_eq_one {a : K} {n : ℕ} (hn : n ≠ 0) (h : a ^ n = a) :
    a = 0 ∨ a ^ (n - 1) = 1 := by
  by_cases ha : a = 0
  · exact Or.inl ha
  · exact Or.inr ((mul_eq_right₀ ha).1 (by rw [pow_sub_one_mul hn, h]))

end Bound

/-- **The bound.** On the m x m torus with m odd, if 2^r = 1 mod m, the period divides
2^r - 1. -/
theorem period_dvd_two_pow_sub_one {m : ℕ} [NeZero m] (hm : Odd m) (D : Finset (ℤ × ℤ)) {r : ℕ}
    (hr : (2 : ZMod m) ^ r = 1) : period m D ∣ 2 ^ r - 1 := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  rw [← isPeriod_iff_period_dvd, isPeriod_iff hζ]
  intro j _ k _
  exact eq_zero_or_pow_eq_one (by positivity) (lam_pow_two_pow hζ.pow_eq_one D j k hr)

/-- **The bound for a symmetric rule.** If D = -D and 2^s = -1 mod m, the period divides
2^s - 1. -/
theorem period_dvd_two_pow_sub_one_of_symm {m : ℕ} [NeZero m] (hm : Odd m)
    {D : Finset (ℤ × ℤ)} (hD : ∀ d ∈ D, -d ∈ D) {s : ℕ} (hs : (2 : ZMod m) ^ s = -1) :
    period m D ∣ 2 ^ s - 1 := by
  obtain ⟨ζ, hζ⟩ := exists_primitiveRoot hm
  rw [← isPeriod_iff_period_dvd, isPeriod_iff hζ]
  intro j _ k _
  exact eq_zero_or_pow_eq_one (by positivity) (lam_pow_two_pow_of_symm hζ.pow_eq_one hD j k hs)

/-- On an odd torus every period is odd. -/
theorem period_odd {m : ℕ} [NeZero m] (hm : Odd m) (D : Finset (ℤ × ℤ)) : Odd (period m D) := by
  have hr : (2 : ZMod m) ^ Nat.totient m = 1 := by
    have h := (ZMod.natCast_eq_natCast_iff _ _ _).2
      (Nat.ModEq.pow_totient (Nat.coprime_two_left.2 hm))
    simpa using h
  have hpos : Nat.totient m ≠ 0 := (Nat.totient_pos.2 hm.pos).ne'
  refine Odd.of_dvd_nat ?_ (period_dvd_two_pow_sub_one hm D hr)
  exact Nat.Even.sub_odd Nat.one_le_two_pow (Nat.even_pow.2 ⟨even_two, hpos⟩) odd_one

end LatticeProofs
