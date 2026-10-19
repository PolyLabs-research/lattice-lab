import LatticeProofs
import LatticeProofs.HexTwoPart
import LatticeProofs.TriTwoPart
import LatticeProofs.VOT13Law
import LatticeProofs.Cubes37

-- `lake env lean Axioms.lean`: the axioms each result rests on. Lean's standard three
-- (propext, Classical.choice, Quot.sound) and nothing else; no sorryAx.
#print axioms LatticeProofs.hexagon_two_steps
#print axioms LatticeProofs.square_N4K8C4_cube
#print axioms LatticeProofs.square_A4K8C4self_cube
#print axioms LatticeProofs.triangle_VOT13_twisted
#print axioms LatticeProofs.sqN4K8C4_order
#print axioms LatticeProofs.triVOT13_value
#print axioms LatticeProofs.triVOT13_order
#print axioms LatticeProofs.three_dvd_one_add_two_pow
#print axioms LatticeProofs.isPeriod_iff
#print axioms LatticeProofs.period_eq_eigenLcm
#print axioms LatticeProofs.isPeriod_iff_period_dvd
#print axioms LatticeProofs.period_sqN4K8C4
#print axioms LatticeProofs.period_sqA4K8C4self
#print axioms LatticeProofs.period_sqC4self
#print axioms LatticeProofs.isEventualPeriod_iff_dvd
#print axioms LatticeProofs.period_dvd_two_pow_sub_one_of_symm
#print axioms LatticeProofs.period_odd
#print axioms LatticeProofs.gtriPeriod_eq_two_mul
#print axioms LatticeProofs.triPeriod_triE
#print axioms LatticeProofs.triPeriod_triE_dvd
#print axioms LatticeProofs.triPeriod_twisted
#print axioms LatticeProofs.isEventualPeriod_restrict_iff
#print axioms LatticeProofs.gstep_iterate_two_pow
#print axioms LatticeProofs.period_div_gcd_two_pow
#print axioms LatticeProofs.period_eq_two_pow_mul
#print axioms LatticeProofs.period_eq_two_pow_mul_of_double
#print axioms LatticeProofs.period_image_smul
#print axioms LatticeProofs.gtriStep_twice
#print axioms LatticeProofs.gtriPeriod_triEVOVS
#print axioms LatticeProofs.triPeriod_div_gcd
#print axioms LatticeProofs.atlasTriPeriod_twisted
#print axioms LatticeProofs.atlasTriPeriod_triEVOVS
#print axioms LatticeProofs.hexPeriod_eq_two_pow_mul
#print axioms LatticeProofs.even_of_jordan
#print axioms LatticeProofs.period_two_mul_of_proj
#print axioms LatticeProofs.period_sqN4D4
#print axioms LatticeProofs.period_sqN4
#print axioms LatticeProofs.period_sqN4D4_dvd
#print axioms LatticeProofs.hexPeriod_hexH1_exact
#print axioms LatticeProofs.atlasTriPeriod_triE_exact
#print axioms LatticeProofs.atlasTriPeriod_triEVOVS_exact
#print axioms LatticeProofs.atlasTriPeriod_triVOT13_law
#print axioms LatticeProofs.Cubes37.period_r90_dvd
#print axioms LatticeProofs.Cubes37.period_w_dvd_87381
#print axioms LatticeProofs.Cubes37.period_k8m8e4_dvd_87381
#print axioms LatticeProofs.Cubes37.period_c4l8m8_dvd_87381
#print axioms LatticeProofs.Cubes37.period_a4b4c4l8e4self_dvd_87381
#print axioms LatticeProofs.Cubes37.period_v_dvd_87381
#print axioms LatticeProofs.Cubes37.period_tri_dvd_87381
