import LatticeProofs.Pilot

-- The pinned statement. It must elaborate against the pilot's theorem exactly as written in
-- examples/llm-pilot-vot13/Pilot.lean, with the agent's own `vot13TwoExp`, so the theorem cannot
-- have been weakened.
example {n v m : ℕ} [NeZero n] [NeZero (n / 2)] [NeZero m]
    (hm : Odd m) (hv : 1 ≤ v) (hn : n = 2 ^ v * m) (h4 : 4 ≤ n) :
    LatticeProofs.atlasTriPeriod n LatticeProofs.triVOT13 =
      2 ^ LatticeProofs.vot13TwoExp v m * LatticeProofs.period m LatticeProofs.triSVOT13Offsets :=
  LatticeProofs.atlasTriPeriod_triVOT13_law hm hv hn h4

#print axioms LatticeProofs.atlasTriPeriod_triVOT13_law
