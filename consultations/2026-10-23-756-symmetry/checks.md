# Machine checks of the answer (fable, round 1)

Served by `claude-fable-5-1`, effort high, 64K task budget, code execution on; 226 s, 3 tool
calls, 12,066 output tokens, $1.12. The scripts are in `checks/` (development, not registered).

| Claim | Check | Outcome |
|---|---|---|
| 1a: the stabilizer of qubit 0 in the Tanner graph's automorphism group (check classes kept) is trivial | `check.py`: colour refinement with qubit 0 individualised | **confirmed**: 1512 cells of 1512 |
| 1b: the orbit of qubit 0 is the 378 left-block qubits, so the group is the 378 translations | `check.py`: the refinement is canonical and discrete, so an automorphism taking 0 to lm would be the colour-matching bijection; it fails the edge check. Translations are transitive on each block | **confirmed**: the group is exactly the translations |
| 1c: of the 648 torus automorphisms, with a shift and with or without the block swap, only the identity preserves the code | `aut.py`, written before the answer was read | **confirmed** (same 648; only the identity) |
| dim ker H_X = 394 (in 3d) | k_linalg: lm + k/2 | **wrong**: 386 |
| P1: the weight-6 words of rowspace(H_X) are exactly its rows (so no automorphism of the code beyond the Tanner graph's) | not checked | open |
| 2: deeper symmetry breaking with translations gains 2-5x at most | not checked | not pursued |
| 3a, P2: a packing bound (unsatisfied checks with pairwise disjoint candidate sets each need a new qubit) cuts nodes 10x or more at bounds 22-24 | `search_pack.c`, `bench.py` | **confirmed in development**: on [[756,16]] at bound 20, 130x fewer nodes and 24x less time on one core; on [[288,12,18]] at 18, 43x and 8x. Growth per 2 of bound falls from about 11x to about 7.9x. Agrees with enumeration on 150 random small codes (both anchor modes, 300 runs) and with the unpacked search on 24 codes up to d = 12 |
| 3a: unit propagation (a check with one candidate forces it) | the search already branches on the check of fewest candidates, so a single candidate is a single branch | **adds nothing** |
| 3b: meet in the middle | not checked | not pursued |
| 3c: the quotient torus is not a bound as stated | agrees with our own view | agreed |
| P3: Brouwer-Zimmermann with 16 information sets, enumeration to weight 5-6, certifies d >= 30 in days | greedy disjoint information sets of ker H_X have ranks 386, 362, 8: under two. With two, d >= 30 needs enumeration to about weight 26 in each; and ker H_X holds the weight-6 stabilizers, so a coset version is needed first | **refuted** |

**Outcome.** The packing cut was registered and tested in `examples/qec-open-distance-2`: it held
on every part, and it took [[756,16]] to d >= 30 (docs/code-distances.md, "The packing cut").
