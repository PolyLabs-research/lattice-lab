# Noise simulation of the census's best codes (scoping, not registered)

**Question.** Do the census's high-k·d²/n codes protect information better per physical qubit
than the published bivariate bicycle codes, once the noise is realistic? Distance is a proxy.
The quantity people build for is the logical error rate under circuit-level noise, with a real
decoder.

## The codes

| Role | Code | Torus | k·d²/n | Source |
|---|---|---|---|---|
| reference | [[144,12,12]] | 12 x 6 | 12.0 | Bravyi et al. (the gross code) |
| reference | [[288,12,18]] | 12 x 12 | 13.5 | Bravyi et al. |
| reference | [[360,12,24]] | 30 x 6 | 19.2 | Bravyi et al.; d = 24 by this project's registered study |
| census | [[294,10,20]] | 3 x 49 | 13.6 | stage 3b; second-method tier (spot-check) |
| census | [[288,8,22]] | 3 x 48 | 13.4 | stage 3b; second-method tier |
| census | [[310,10,22]] | 5 x 31 | 15.6 | stage 4; second method and second implementation |
| census | [[372,10,24]] | 2 x 93 | 15.5 | stage 4; search only so far |
| census | [[378,12,22]] | 3 x 63 | 15.4 | stage 4; search only so far |
| census | [[340,16,18]] | 2 x 85 | 15.3 | stage 4; search only so far |

The final list is fixed when stage 4 ends: the top codes by k·d²/n, plus the published codes
nearest each in n.

## What gets measured

1. **Code capacity.** Independent X and Z flips at rate p on data qubits only, with perfect
   syndromes, decoded by BP-OSD. This is cheap and runs here. It shows whether d translates
   into low logical error rates at moderate p before any circuit is involved.
2. **Circuit-level noise** (the headline). One syndrome cycle per round, d rounds, with
   standard circuit noise at rate p on every gate, idle, preparation and measurement:
   - the depth-8 syndrome circuit of Bravyi et al., which uses the A = A1 + A2 + A3,
     B = B1 + B2 + B3 structure that every code in this family shares;
   - a decoder over the detector error model: BP-OSD (the `ldpc` package), with BP+LSD as
     a faster alternative.
3. **The figure of merit.** The logical error rate per round, per logical qubit (to set
   k = 10 against k = 12 fairly), plotted against p. Also each code's total qubit count:
   n data qubits plus n ancillas.

## Risks, and how the plan handles them

- **The circuit can lower the distance.** Hook errors in a syndrome circuit can make the
  circuit-level distance smaller than d. Bravyi et al. checked their CNOT order for their own
  codes only. Before any sampling, each code's circuit gets stim's
  `search_for_undetectable_logical_errors`, which gives an upper bound on the circuit-level
  distance. A code whose circuit distance falls short of d is reported as such, and the CNOT
  order is searched, before it is compared.
- **The interesting error rates cannot be sampled directly.** At p = 10^-3 a code with d >= 20
  has a logical error rate far below 10^-9 per round. Like Bravyi et al., the sampling is done
  at higher p (about 2 x 10^-3 to 6 x 10^-3), where failures are frequent enough to count, and
  extrapolated with the standard fit, LER ~ A (p / p0)^(d_c / 2) with d_c the circuit
  distance. The comparison that needs no extrapolation is between codes at the same p.
- **Decoding cost.** BP-OSD on a d-round circuit for n ~ 300 is slow, around 0.1 to 1 s per
  shot. A point with about 100 failures needs 10^4 to 10^6 shots. That is roughly 10 to 300
  core-hours per (code, p) point, so this runs on a 32-vCPU pod. BP+LSD or relay-BP can cut
  it if accuracy holds on the small codes.
- **Decoder fairness.** Every code uses the same decoder and settings. The gross code's
  published curve (Bravyi et al.) is the check that the pipeline reproduces known results
  before anything new is claimed.

## Order of work

1. **Pipeline** (here, about a day). Build the BB stim circuit for any (A, B, l, m). Confirm:
   - the code-capacity curves on the gross code;
   - the circuit-level gross-code point at p = 3 x 10^-3 against Bravyi et al.'s published
     value.
2. **Circuit distances** (here). Run stim's undetectable-error search on every listed code.
   Drop or fix any code whose circuit distance is below its d.
3. **Registration.** Fix the codes, p grid, rounds, decoder and shot budgets. Register the
   predictions, for example: at each sampled p, [[310,10,22]]'s logical error rate per round
   per logical qubit is below [[288,12,18]]'s.
4. **Run** on a pod (estimated 1 to 3 days on 32 vCPU), then write up with the curves.

## Tools

stim (circuits, sampling, detector error models), sinter (sampling orchestration), and ldpc
(BP-OSD and BP+LSD), all on PyPI, installed in their own environment. The circuit builder and
decoder wrapper will live in this directory, with tests against the gross code.
