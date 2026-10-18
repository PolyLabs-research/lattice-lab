import LatticeProofs
namespace LatticeProofs
example (ζ : AlgebraicClosure (ZMod 2)) (h0 : ζ ≠ 0) : (∑ d ∈ triSEVOVSOffsets, ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2)) * ζ ^ 2 = (1 + ζ ^ 2) ^ 2 := by
  have h2K : (2 : AlgebraicClosure (ZMod 2)) = 0 := two_eq_zero_of_charTwo
  simp [triSEVOVSOffsets]
  field_simp
  linear_combination (2 * ζ ^ 3 + 2 * ζ) * h2K
example (ζ : AlgebraicClosure (ZMod 2)) (h0 : ζ ≠ 0) : (∑ d ∈ triSEVOVSOffsets, ζ ^ (-(d.1 - d.2)) * ζ ^ (-d.2) * ((-(d.1 - d.2) : ℤ) : AlgebraicClosure (ZMod 2))) * ζ ^ 2 = (1 + ζ ^ 2) ^ 2 := by
  have h2K : (2 : AlgebraicClosure (ZMod 2)) = 0 := two_eq_zero_of_charTwo
  simp [triSEVOVSOffsets]
  field_simp
  linear_combination (0:AlgebraicClosure (ZMod 2)) * h2K
end LatticeProofs
