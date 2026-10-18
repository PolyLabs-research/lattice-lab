/-
Rules on any torus, through the group ring (docs/proofs.md).

A torus is a finite abelian group G with a homomorphism omega from Z^2, the lattice's
translations, to it. On the square torus of side n, G = (Z/n)^2 and omega is reduction mod n.
The atlas's hexagonal and triangular tori are other G (`Tori.lean`). A rule with neighbourhood D
makes every cell v the sum mod 2 of the cells v + omega(d) (`gstep`).

The Laurent polynomials over GF(2) are the group ring F2[Z^2] (`Laurent`), and a neighbourhood is
one of them (`grp D`). The group ring acts on the configurations of every torus by translations
(`act`), and `act_grp` says that `grp D` acts as one step of the rule. So an identity between
Laurent polynomials is an identity between rules on every torus at once. In particular:

* `gstep_eq_iterate`: if grp D = (grp E)^k, then a step of D is k steps of E;
* `gstep_iterate_two_pow`: Frobenius. 2^k steps of D are one step of the neighbourhood 2^k D.

Two facts about periods carry these to periods:

* `eventualPeriod_iterate`: f^[k] has period P / gcd(P, k), where P is f's;
* `isEventualPeriod_restrict_iff`: the restriction lemma. Let mu : G' -> G be injective with
  mu(omega'(d)) = omega(N d). Then the rule N D on G has the periods of D on G'.
-/
import LatticeProofs.Bridge
import Mathlib.Algebra.MonoidAlgebra.Basic

namespace LatticeProofs

open Finset AddMonoidAlgebra

section Iterate

variable {α : Type*} {f : α → α}

theorem isEventualPeriod_iterate_iff {k : ℕ} (hk : 0 < k) {p : ℕ} :
    IsEventualPeriod (f^[k]) p ↔ IsEventualPeriod f (k * p) := by
  constructor
  · rintro ⟨t, ht⟩
    refine ⟨k * t, ?_⟩
    rw [← Function.iterate_mul, ← Function.iterate_mul] at ht
    rwa [← mul_add]
  · rintro ⟨s, hs⟩
    refine ⟨s, ?_⟩
    rw [← Function.iterate_mul, ← Function.iterate_mul, mul_add]
    have hle : s ≤ k * s := Nat.le_mul_of_pos_left s hk
    have e := iterate_add_mul_eq hs (k * s - s) 1
    rwa [Nat.add_sub_cancel' hle, one_mul] at e

/-- f^[k] has period P / gcd(P, k), where P is f's. -/
theorem eventualPeriod_iterate [Finite α] {k : ℕ} (hk : 0 < k) :
    eventualPeriod (f^[k]) = eventualPeriod f / Nat.gcd (eventualPeriod f) k :=
  eq_div_gcd_of_dvd_iff hk fun p => by
    rw [← isEventualPeriod_iff_dvd, ← isEventualPeriod_iff_dvd, isEventualPeriod_iterate_iff hk]

/-- A map acting the same way on both factors of a product has the periods of its factor. -/
theorem isEventualPeriod_prodMap_iff {g : α → α} {p : ℕ} :
    IsEventualPeriod (Prod.map g g) p ↔ IsEventualPeriod g p := by
  constructor
  · rintro ⟨t, ht⟩
    refine ⟨t, funext fun s => ?_⟩
    rw [Prod.map_iterate, Prod.map_iterate] at ht
    exact congrArg Prod.fst (congrFun ht (s, s))
  · rintro ⟨t, ht⟩
    exact ⟨t, by rw [Prod.map_iterate, Prod.map_iterate, ht]⟩

theorem eventualPeriod_prodMap [Finite α] (g : α → α) :
    eventualPeriod (Prod.map g g) = eventualPeriod g :=
  Nat.dvd_antisymm
    (isEventualPeriod_iff_dvd.1 (isEventualPeriod_prodMap_iff.2 (eventualPeriod_spec g).2))
    (isEventualPeriod_iff_dvd.1 (isEventualPeriod_prodMap_iff.1 (eventualPeriod_spec _).2))

end Iterate

/-! ### The Laurent polynomials over GF(2) -/

/-- The Laurent polynomials over GF(2) in x and y: the group ring of the lattice's translations. -/
abbrev Laurent := AddMonoidAlgebra (ZMod 2) (ℤ × ℤ)

/-- A neighbourhood as a Laurent polynomial: the sum of its translations. -/
noncomputable def grp (D : Finset (ℤ × ℤ)) : Laurent := ∑ d ∈ D, single d 1

/-- The monomials x, 1/x, y and 1/y. -/
noncomputable def lx : Laurent := single (1, 0) 1
noncomputable def lxi : Laurent := single (-1, 0) 1
noncomputable def ly : Laurent := single (0, 1) 1
noncomputable def lyi : Laurent := single (0, -1) 1

theorem laurent_two : (2 : Laurent) = 0 := by
  rw [show (2 : Laurent) = ((2 : ℕ) : Laurent) by norm_num, natCast_def]
  rw [show ((2 : ℕ) : ZMod 2) = 0 by decide, single_zero]

theorem lx_mul_lxi : lx * lxi = 1 := by
  simp [lx, lxi, single_mul_single, one_def]
  rfl

theorem ly_mul_lyi : ly * lyi = 1 := by
  simp [ly, lyi, single_mul_single, one_def]
  rfl

theorem grp_empty : grp ∅ = 0 := by simp [grp]

theorem single_origin : (single (0, 0) 1 : Laurent) = 1 := rfl

instance : CharP Laurent 2 :=
  charP_of_injective_algebraMap (algebraMap (ZMod 2) Laurent).injective 2

/-- Frobenius: the 2^k-th power of a neighbourhood is the neighbourhood scaled by 2^k. -/
theorem grp_pow_two_pow (D : Finset (ℤ × ℤ)) (k : ℕ) :
    grp D ^ 2 ^ k = grp (D.image ((2 ^ k : ℕ) • ·)) := by
  rw [grp, sum_pow_char_pow, grp,
    Finset.sum_image fun a _ b _ h => smul_right_injective (ℤ × ℤ) (by positivity) h]
  simp [single_pow]

/-! ### Rules on a torus -/

section Torus

variable {G : Type*} [AddCommGroup G] (ω : ℤ × ℤ →+ G)

/-- One step of the rule with neighbourhood D on the torus (G, omega): every cell v becomes the
sum mod 2 of the cells v + omega(d). -/
def gstep (D : Finset (ℤ × ℤ)) (s : G → ZMod 2) : G → ZMod 2 :=
  fun v => ∑ d ∈ D, s (v + ω d)

/-- The period of the rule with neighbourhood D on the torus (G, omega). -/
noncomputable def gperiod (D : Finset (ℤ × ℤ)) : ℕ := eventualPeriod (gstep ω D)

/-- Translation by g, as a linear map of configurations. -/
def shift (g : G) : Module.End (ZMod 2) (G → ZMod 2) :=
  LinearMap.funLeft (ZMod 2) (ZMod 2) (· + g)

/-- The lattice's translations acting on configurations. -/
def shiftHom : Multiplicative (ℤ × ℤ) →* Module.End (ZMod 2) (G → ZMod 2) where
  toFun d := shift (ω (Multiplicative.toAdd d))
  map_one' := LinearMap.ext fun s => funext fun v => by
    simp [shift, LinearMap.funLeft_apply]
  map_mul' a b := LinearMap.ext fun s => funext fun v => by
    simp [shift, LinearMap.funLeft_apply, add_assoc]

/-- The group ring acting on the configurations of (G, omega), by translations. -/
noncomputable def act : Laurent →ₐ[ZMod 2] Module.End (ZMod 2) (G → ZMod 2) :=
  AddMonoidAlgebra.lift (ZMod 2) (Module.End (ZMod 2) (G → ZMod 2)) (ℤ × ℤ) (shiftHom ω)

/-- A neighbourhood's polynomial acts as one step of its rule. -/
theorem act_grp (D : Finset (ℤ × ℤ)) : ⇑(act ω (grp D)) = gstep ω D := by
  funext s v
  simp [act, grp, shiftHom, shift, gstep, LinearMap.funLeft_apply]

theorem gstep_iterate (D : Finset (ℤ × ℤ)) (k : ℕ) :
    (gstep ω D)^[k] = ⇑(act ω (grp D ^ k)) := by
  rw [map_pow, Module.End.coe_pow, act_grp]

/-- If grp D = (grp E)^k, a step of D is k steps of E, on every torus. -/
theorem gstep_eq_iterate {D E : Finset (ℤ × ℤ)} {k : ℕ} (h : grp D = grp E ^ k) :
    gstep ω D = (gstep ω E)^[k] := by
  rw [gstep_iterate, ← h, act_grp]

/-- If grp D = (grp E)^k with k > 0, D's period is E's divided by gcd(period, k). -/
theorem gperiod_eq_of_grp_eq_pow [Finite G] {D E : Finset (ℤ × ℤ)} {k : ℕ} (hk : 0 < k)
    (h : grp D = grp E ^ k) : gperiod ω D = gperiod ω E / Nat.gcd (gperiod ω E) k := by
  rw [gperiod, gstep_eq_iterate ω h]
  exact eventualPeriod_iterate hk

/-- Frobenius: 2^k steps of D are one step of 2^k D. -/
theorem gstep_iterate_two_pow (D : Finset (ℤ × ℤ)) (k : ℕ) :
    (gstep ω D)^[2 ^ k] = gstep ω (D.image ((2 ^ k : ℕ) • ·)) := by
  rw [gstep_iterate, grp_pow_two_pow, act_grp]

end Torus

/-! ### The square torus -/

/-- The square torus of side n: (Z/n)^2, with the lattice's translations reduced mod n. -/
def offsetHom (n : ℕ) : ℤ × ℤ →+ Cell n :=
  (Int.castAddHom (ZMod n)).prodMap (Int.castAddHom (ZMod n))

theorem offsetHom_apply (n : ℕ) (d : ℤ × ℤ) : offsetHom n d = offset n d := rfl

theorem step_eq_gstep (n : ℕ) [NeZero n] (D : Finset (ℤ × ℤ)) :
    step n D = gstep (offsetHom n) D := rfl

theorem period_eq_gperiod (n : ℕ) [NeZero n] (D : Finset (ℤ × ℤ)) :
    period n D = gperiod (offsetHom n) D := rfl

/-! ### Restriction to a sub-torus -/

section Restrict

variable {G G' : Type*} [AddCommGroup G] [AddCommGroup G'] (ω : ℤ × ℤ →+ G)
  (ω' : ℤ × ℤ →+ G') (μ : G' →+ G)

/-- A configuration of G read along the coset r + mu(G'). -/
def restrict (r : G) (c : G → ZMod 2) : G' → ZMod 2 := fun w => c (r + μ w)

variable {ω ω' μ} {N : ℕ}

theorem restrict_gstep (hN : 0 < N) (hμ : ∀ d, μ (ω' d) = ω (N • d)) (D : Finset (ℤ × ℤ))
    (r : G) (c : G → ZMod 2) :
    restrict μ r (gstep ω (D.image (N • ·)) c) = gstep ω' D (restrict μ r c) := by
  funext w
  simp only [restrict, gstep]
  rw [Finset.sum_image fun a _ b _ h => smul_right_injective (ℤ × ℤ) hN.ne' h]
  refine Finset.sum_congr rfl fun d _ => ?_
  rw [← hμ, map_add, add_assoc]

theorem restrict_iterate (hN : 0 < N) (hμ : ∀ d, μ (ω' d) = ω (N • d)) (D : Finset (ℤ × ℤ))
    (r : G) (k : ℕ) (c : G → ZMod 2) :
    restrict μ r ((gstep ω (D.image (N • ·)))^[k] c) = (gstep ω' D)^[k] (restrict μ r c) :=
  Function.Semiconj.iterate_right (f := restrict μ r) (fun c => restrict_gstep hN hμ D r c) k c

/-- **The restriction lemma.** If mu : G' -> G is injective and mu(omega'(d)) = omega(N d), the
rule N D on G has exactly the periods of D on G'. -/
theorem isEventualPeriod_restrict_iff (hN : 0 < N) (hμ : ∀ d, μ (ω' d) = ω (N • d))
    (hinj : Function.Injective μ) (D : Finset (ℤ × ℤ)) (p : ℕ) :
    IsEventualPeriod (gstep ω (D.image (N • ·))) p ↔ IsEventualPeriod (gstep ω' D) p := by
  constructor
  · rintro ⟨t, ht⟩
    refine ⟨t, funext fun s => ?_⟩
    have h := congrArg (restrict μ 0) (congrFun ht (Function.extend μ s 0))
    rw [restrict_iterate hN hμ, restrict_iterate hN hμ] at h
    have hs : restrict μ 0 (Function.extend μ s 0) = s :=
      funext fun w => by simp [restrict, hinj.extend_apply]
    rwa [hs] at h
  · rintro ⟨t, ht⟩
    refine ⟨t, funext fun c => funext fun r => ?_⟩
    have h := congrFun (congrFun ht (restrict μ r c)) 0
    rw [← restrict_iterate hN hμ, ← restrict_iterate hN hμ] at h
    simpa [restrict] using h

theorem eventualPeriod_restrict [Finite G] [Finite G'] (hN : 0 < N)
    (hμ : ∀ d, μ (ω' d) = ω (N • d)) (hinj : Function.Injective μ) (D : Finset (ℤ × ℤ)) :
    gperiod ω (D.image (N • ·)) = gperiod ω' D :=
  Nat.dvd_antisymm
    (isEventualPeriod_iff_dvd.1 ((isEventualPeriod_restrict_iff hN hμ hinj D _).2
      (eventualPeriod_spec _).2))
    (isEventualPeriod_iff_dvd.1 ((isEventualPeriod_restrict_iff hN hμ hinj D _).1
      (eventualPeriod_spec _).2))

end Restrict

/-! ### Multiplication by N between cyclic groups -/

/-- Multiplication by N, from Z/m' to Z/n, which is well defined when n divides N m'. -/
def zmodMul (m' n N : ℕ) (h : n ∣ N * m') : ZMod m' →+ ZMod n :=
  ZMod.lift m' ⟨AddMonoidHom.mk' (fun k : ℤ => ((N * k : ℤ) : ZMod n)) fun a b => by
    push_cast; ring, by
    simp only [AddMonoidHom.mk'_apply]
    exact_mod_cast (ZMod.natCast_eq_zero_iff _ _).2 h⟩

theorem zmodMul_intCast {m' n N : ℕ} (h : n ∣ N * m') (k : ℤ) :
    zmodMul m' n N h (k : ZMod m') = ((N * k : ℤ) : ZMod n) :=
  ZMod.lift_coe m' _ k

theorem zmodMul_injective {m' n N : ℕ} [NeZero m'] (h : n ∣ N * m')
    (h2 : ∀ a : ℕ, n ∣ N * a → m' ∣ a) : Function.Injective (zmodMul m' n N h) := by
  refine (injective_iff_map_eq_zero _).2 fun a ha => ?_
  have hz : zmodMul m' n N h (((a.val : ℕ) : ℤ) : ZMod m') = 0 := by
    rwa [Int.cast_natCast, ZMod.natCast_zmod_val]
  rw [zmodMul_intCast] at hz
  have hd : n ∣ N * a.val := (ZMod.natCast_eq_zero_iff _ _).1 (by exact_mod_cast hz)
  have hv : a.val = 0 := Nat.eq_zero_of_dvd_of_lt (h2 _ hd) (ZMod.val_lt a)
  exact (ZMod.val_eq_zero a).1 hv

end LatticeProofs
