# Next direction: from periods on the torus to quantum error-correcting codes

**Status: a plan, with its first step registered** (`examples/qec-bb`). Written 2026-10-20, after
the seventh pilot.

## What the project has actually built

Under the cellular-automaton framing, every result here is about one object: polynomials in two
variables over GF(2), taken modulo x^m − 1 and y^m − 1. That is the group ring of the m × m torus.
A linear rule is such a polynomial, and its period is set by the polynomial's values at the
torus's characters, its eigenvalues in F(2^s). Around that object the project has built:

- **exact instruments**: the eigenvalues of a rule in seconds (`eigen.py`), and censuses of
  millions of rules from class discrete logs (`rule-4850/census.py`), reduced by the symmetries
  of the torus (`image_of`, maps in GL2(Z/m));
- **structure theory**: when the eigenvalues are special and why. That covers splitting, powers,
  dilations and twisted pairs, half-Frobenius invariance, certificates, units times powers, and
  exponent bookkeeping (the seventh pilot);
- **a Lean bridge** from a polynomial to its eigenvalues to its period, so such statements can be
  machine-checked;
- **a research loop**: an agent proposes, an independent judge checks on held-out cases, and every
  test is registered before it is run.

The theorems themselves (cubes and ninth powers at m = 37) have no application. The object, the
instruments and the loop do.

## Where the same object is used

**Quantum LDPC codes.** A bivariate bicycle code (Bravyi et al., Nature 2024; IBM's [[144,12,12]]
"gross code") is a pair of polynomials A, B in GF(2)[x, y]/(x^l − 1, y^m − 1): this ring, on an
l × m torus. Its checks are H_X = [A | B] and H_Z = [B^T | A^T]. It has n = 2lm qubits and
k = 2 dim(ker A ∩ ker B) logical qubits.

- **k from the characters.** k is read off the torus's characters. The ring is a Frobenius
  algebra, so dim(ker A ∩ ker B) = dim R/(A, B), and R splits over the characters of the torus's
  odd part. At odd sizes, k is twice the number of characters where A and B both vanish: the
  zero eigenvalues this repository already computes. At even sizes each such character counts
  with its multiplicity in the 2-part, which is the even-size reduction the library already has.
- **Equivalent codes.** Maps of the torus send codes to equivalent codes. Our GL2 image test is
  a code-equivalence test, and it shrinks searches the same way it shrank the censuses.
- **Cheap logical gates.** A symmetry of the torus that preserves a code is an automorphism, and
  automorphisms are being studied as fault-tolerant logical gates done by permuting qubits. The
  half-Frobenius mechanism (pilot 4) is exactly invariance under a dilation (x, y) → (x^n, y^n).
- **Odd sizes in use.** The coprime bivariate bicycle codes (Wang and Mueller, 2024) live on odd
  tori, such as 3 × 5, 5 × 7 and 7 × 9, where the character count applies directly.

**Built-in self-test and pseudorandom generators.** Linear cellular automata (rule 90/150 hybrids)
are standard test-pattern generators in chip testing, and 2D versions appear in pseudorandom
generators and image-encryption schemes. A short cycle is a defect there, and the mechanisms here
predict exactly when the cycle collapses (rule 4850 at 37). A certified period checker is a modest
but real tool.

**Physics models.** In fracton and fractal spin models (Newman–Moore is built on the triangle
rule), ground-state counts and recurrence times are given by the same algebra. That is research,
not a product.

The codes are the strongest of the three: a live field, an industrial roadmap built on exactly
this ring, and a quantity, k, that the instruments here already compute.

## The path

1. **Rediscovery (registered: `examples/qec-bb`).**
   - **What it checks.** Compute k by the character method and by plain linear algebra over
     GF(2), for twelve published entries (the five original bivariate bicycle codes and the
     coprime codes, two of them in two published versions) and for 3,000 random codes at 20
     sizes, half of them even.
   - **Predictions.** The two methods agree everywhere, and they reproduce every published k.
   - **Why it matters.** It decides whether the bridge is real, including the even sizes where
     each character carries a multiplicity. It costs only local computation.
2. **A census of code families.** Sweep polynomial pairs at many sizes for high k, using the
   classes and symmetries to prune. Then measure distance, the hard and expensive part, with
   established tools:
   - exact integer programming for small codes;
   - randomized information-set methods for larger ones;
   - circuit-noise simulation (stim, BP-OSD decoders) for the logical error rates practitioners
     care about.

   This needs those packages installed and is where the compute goes.
3. **Pilots on codes.** Point the agent loop at structural questions with a code-level payoff. For
   example: which conditions on (A, B) force many logical qubits and a torus automorphism at once?
   The judge checks k exactly and distance independently, on held-out sizes registered in advance,
   as in the seven pilots so far.
4. **Certificates.** The Lean bridge extends to k and to automorphisms. Distance will mostly stay
   outside Lean, but a certified k and certified symmetries with independently checked distances
   are a stronger claim than most code-search papers make.

## Caveats

- **Competition.** Bivariate bicycle code search is active, with groups searching by brute force,
  by covering-graph constructions, and already with LLM-guided search. The contribution here
  would be the method (machine-checked structure, registered held-out tests), and any new
  families, not a head start.
- **Distance.** Distance decides whether a code is useful, and nothing in the project yet
  computes it.
- **Sources.** The published codes in step 1 were transcribed from search summaries of the
  papers, because arXiv is not reachable from this environment (`examples/qec-bb/codes.json`
  says so). A disagreement with a published k is first a question about the transcription.
