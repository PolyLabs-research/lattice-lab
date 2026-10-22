# lattice-lab

A law-discovery loop over two existing projects. It asks "how does quantity y depend on setting
x" for a cellular-automaton rule, and answers with a named law, its constants with error bars,
and a verdict from experiments the fit never saw. Each prediction is recorded before the run
that tests it, in an append-only, hash-chained ledger.

- [LatticeLife](https://github.com/PolyLabs-research/gameoflife_advanced) runs the experiments
  and says what their numbers mean, including when a number is only a bound.
- [Kepler](https://github.com/PolyLabs-research/kepler) fits, ranks and predicts closed-form laws
  with error bars.
- lattice-lab owns what belongs to neither: the questions, the candidate laws, choosing the next
  experiment, pre-registered predictions, verdicts, and the record of every result.

Neither library imports lattice-lab or the other. See [docs/design.md](docs/design.md) for the
architecture, the loop step by step, and the milestones.

The loop began with settling times. Most of the work since is on linear rules, whose periods can
be computed exactly and proved: period laws for the parity rules, an atlas of rules built from
neighbour shells, the mechanisms behind it proved in Lean, and seven pilots in which a fresh LLM
agent, given a problem card, proves a law or finds and proves a mechanism, with Lean as the
judge of the proof. The latest results explain why every nonzero eigenvalue of rule 4850 at
m = 37 is a ninth power, with a proof that three independent checkers found stands with repairs,
and classify the hexagon family it belongs to, confirmed by a registered test. The ring all of
this lives in is also the ring of bivariate bicycle quantum codes, the proposed next direction
([docs/next-direction.md](docs/next-direction.md)).

The public website, [polylabs-research.net](https://polylabs-research.net), is built from
`site/`; [site/README.md](site/README.md) says how to rebuild and deploy it.

## Findings so far

**Picking this up?** [docs/STATUS.md](docs/STATUS.md) says where things stand: the three
repositories, how to resume, what is established, and what is open.

Every finding below was tested by predictions written to a ledger, committed and pushed before the
runs that test them. `uv run lattice-lab verify --lab examples/<study>` checks the order. Where
reasoning after the fact went beyond the tools, the write-up says so.

| Finding | Status | Write-up | Studies |
| --- | --- | --- | --- |
| Square parity rule B1357/S1357: period 2^v(n) (2^sord(m) - 1) | confirmed in advance at every n up to 200; the 2-part proved in Lean at every size (odd part > 1); the odd part settled by machine up to 999 except ten | [xor-periods.md](docs/xor-periods.md), [proof](docs/xor-periods-proof.md), [proofs.md](docs/proofs.md) | `xor-periods*` |
| Hexagon parity rule B135/S135: period 2 * 2^v(n) R(m), R = rule 90's period | the first law was refuted at 3 of 70 sizes; the corrected law was confirmed at 100 and **proved for every even n**; its 2-part also proved in Lean, by an LLM agent | [parity-lattices.md](docs/parity-lattices.md), [llm-pilot.md](docs/llm-pilot.md) | `parity-lattices*`, `llm-pilot` |
| Triangle parity rules: period 2 * 2^v(n) (2^sord(m) - 1) | confirmed at 154 sizes; the factor 2 * 2^v(n) is proved, and also in Lean, by an LLM agent; the odd part is checked by machine for odd parts up to 999 except ten | [parity-lattices.md](docs/parity-lattices.md), [llm-pilot.md](docs/llm-pilot.md) | `parity-lattices*`, `llm-pilot-triangle` |
| Kepler, given rule periods in its vocabulary, finds the hexagon law itself | confirmed in a registered replay (8 of 8 expectations) | [parity-lattices.md](docs/parity-lattices.md#kepler-with-a-wider-vocabulary) | `kepler-rediscovery` |
| Periods of 42 linear rules built from neighbour shells, 38 never studied | blind: all 34 rules that got a law kept a registered one at 1,930 new pairs, and again at 624 harder pairs up to n = 400 | [linear-atlas.md](docs/linear-atlas.md) | `linear-atlas`, `linear-atlas-2` |
| A rule that factors into 1D passes has a 1D period; any other reaches the full bound | registered on 116 new rules and **refuted** (7 of 113 predictions failed). Three failed rules were cubes or a dilation, mechanisms then predicted exactly; of the other four failures, two are explained (eigenvalues in F(8) at n = 13), and the one at n = 37 was explained later by the fourth pilot | [linear-atlas.md](docs/linear-atlas.md#round-2-the-pattern-registered) | `linear-atlas-2` |
| The refined statement: the full bound unless splitting, an odd power or a dilation confines the eigenvalues | registered on 344 new rules and **refuted**: 43 of 11,358 predictions failed (0.4%). Every dilation and power held; a third mechanism, a twisted power, showed up and its expectation, written first, matched all 34 sizes; the rest are small-field coincidences, and one case at m = 37, since explained by the fourth pilot | [linear-atlas.md](docs/linear-atlas.md#round-3-the-refined-statement-registered) | `linear-atlas-3` |
| B2/S34 settling time on the hexagon grows like log L | found by the loop; replicated on tori up to 1024, where the power law is rejected | [settling-time.md](docs/settling-time.md) | `lab-b2s34`, `settling-time-replication` |
| Settling-time fluctuations are universal, with extreme-value (Gumbel) shape and ratio | eight random rules on four lattice types; a first apparent miss for B2/S34 was a low draw | [settling-time.md](docs/settling-time.md) | `settling-universality`, `settling-time-local` |
| Cumulative births under B1357/S1357 are always even | found in the data, then proved | [capabilities.md](docs/capabilities.md) | `capabilities` |
| Six rules have every eigenvalue a cube at m = 37 because a dilation by 6 acts there as half a Frobenius, combined with rule 90's own confinement | **answered by an LLM agent**, on a question the orchestrator could not answer, and **proved in Lean** for all six, unconditionally; the agent's general condition held at 633 claims, 180 of them at held-out sizes registered before it started, none false | [llm-pilot.md](docs/llm-pilot.md#pilot-4-the-cubes-at-m--37) | `llm-pilot-37` |
| Five of seventeen rules have every eigenvalue a cube at m = 25: two by cube certificates (f (t(x) t(y))^3 is invariant under x7, and 2^5 = 7 mod 25), three as twisted pairs C(x, y) C(x^3, y^3) | **found and proved in Lean by an LLM agent**; its condition held at 1,381 claims, 414 at held-out sizes, none false. Twelve remain unexplained, and the registered held-out census found 16 new confinements at m = 37 that no mechanism then known explained, the sixth pilot's question (next row) | [llm-pilot.md](docs/llm-pilot.md#pilot-5-the-cubes-at-m--25) | `llm-pilot-25` |
| Nine square-family rules are a unit times a cube, f = U g^3 with U a product of rule-90 or Psi_3 factors, so every eigenvalue is a cube at m = 37 (and three of them at 61) | **found and proved in Lean by an LLM agent**, which also showed the census's chance model undercounts at 37; the registered census at 17 new sizes found these nine at exactly the three sizes predicted, and nothing else unexplained | [llm-pilot.md](docs/llm-pilot.md#pilot-6-the-square-family-at-m--37) | `llm-pilot-37b` |
| For a prime p = 5 (mod 8) with 2 a primitive root, rule 90 is confined to the cubes at p exactly when eps^h lies in Z[sqrt p] (eps, h: the fundamental unit and class number of Q(sqrt p)); at p = i^2 + 1 the pyramid rule with rings at radii 2, 4, ..., i/2 - 1 is then confined too | **proposed by Claude Fable in a consultation**, with an argument that, filled in with Dirichlet's class number formula, is a proof; registered and confirmed at all 405 such primes from 302 to 20,000 and at the 4 pyramid primes below 10,000, none wrong | [consultations.md](docs/consultations.md) | `fable-units` |
| At m = 37, five symmetric rules have every nonzero eigenvalue a ninth power that none of the seven mechanisms then known explains: 4850 (radius 4) and 699738, 985232, 1431278, 1968276 (radius 5) | chance **refuted** by a registered census of 2,064,384 radius-5 rules (4 independent such rules against 0.0066 expected), from a test Claude Fable proposed in a consultation; each is confined at 37 and at no other odd m from 11 to 101. All five are explained since (next two rows) | [consultations.md](docs/consultations.md) | `rule-4850` |
| Four of them (699738, 985232, 1431278, 1968276) are line units times pilot 4's half-Frobenius cores, and the units' exact exponents add the third factor of 3 | **found by an LLM agent (Claude Fable)** in the seventh pilot, its condition sound at all 1,715 claims (533 at held-out sizes) and covering 35 of the 37 unexplained ninth-power rules of the registered radius-6 census, which the agent had computed itself; its Lean failed to build in round 1 and was fixed in a second round over the API (`Ninth37.lean`); 4850 itself was explained afterwards by the deep dive (next row) | [llm-pilot.md](docs/llm-pilot.md#pilot-7-the-ninth-powers-at-m--37) | `llm-pilot-37c` |
| Rule 4850 itself: (x + 1/x + y + 1/y)·4850 is two hexagons sharing a 120° rotation mod 37 (5² + 3·2² = 37), its eigenvalues off the diagonals are W⁴/(t t) with W a Kloosterman-type sum over μ6, and a Gauss-period norm formula puts every norm to F64 in F8* | **explained, with a proof**: three independent checkers found it stands with repairs, which they supplied, and the orchestrator rechecked the chain; not yet written as one document, and not in Lean. The hexagon family's classification at 37 (p a non-residue gives ninth powers, a residue cubes) passed a registered held-out test: 35 of 35 tested predictions correct; the six at the largest sizes were not tested | [deep dive report](examples/rule-4850/deep/REPORT.md) | `rule-4850/deep`, `hexagon-family` |
| A bivariate bicycle quantum code's logical qubits k are read off the torus's characters (common zeros of A and B, with 2-part multiplicities at even sizes) | **confirmed by a registered test**: agrees with linear algebra on 3,000 of 3,000 random codes and reproduces all 12 published k, IBM's gross code included | [next-direction.md](docs/next-direction.md) | `qec-bb` |
| The 12 published codes' distances, d = 18 for [[288,12,18]] included | **reproduced by a registered test**, blind to the published values, by an exhaustive search built here (the gross code in 0.2 s, [[288,12,18]] in 3 minutes); an integer program agrees on 11. Its registered method check **failed** once, through a SCIP fault; the fault was traced and fixed, and a second registered test on fresh codes found both instruments hold, while SCIP's unfixed defaults failed on 3 of its codes | [code-distances.md](docs/code-distances.md) | `qec-distance`, `qec-distance-2` |
| An LLM agent, given only a problem card and the Lean library, finds a mechanism and proves it | three pilots, each on the first attempt: the hexagon and triangle laws' 2-parts, and VO + T13's law, which the agent had to find from data. **Accepted by Lean**, not by the agent's account, with pinned statements and standard axioms; the registered predictions held at 15 of 15, 40 of 40 and 20 of 20, and the third agent's own law at 20 of 20 sizes it never saw. The last two ran in their own containers, with their transcripts audited. The laws were within reach of known techniques and, for the third, of one division per data row. Pilots 4 to 7, on open questions, are in the rows above | [llm-pilot.md](docs/llm-pilot.md) | `llm-pilot*` |
| The atlas's mechanisms, formally | **proved in Lean** (mathlib, standard axioms only): the 18 identities behind them; the bridge, that a rule's period on an odd torus is the lcm of its nonzero eigenvalues' orders; the reduction from even sizes to odd parts on the square and the atlas's own triangular and hexagonal tori; round 2's cube and dilation at every size; round 3's twisted power on the atlas's own triangular torus; the XOR law's 2-part at every size; the hexagon and triangle laws' 2-parts and VO + T13's law (proved by LLM agents, the last also found by one); the confinements that pilots 4 to 7 found and proved, to the cubes at m = 25, 37 and 61 and to the ninth powers at 37; and the full bound, that the period divides 2^sord(m) - 1 | [proofs.md](docs/proofs.md) | `proofs/` |

## Install

```bash
uv sync                      # LatticeLife and Kepler at the commits pinned in pyproject.toml
uv run pytest
```

Python 3.12 or 3.13 (LatticeLife's bound). To work against local checkouts of the libraries,
run `uv pip install -e ../gameoflife_advanced -e ../kepler` after `uv sync`, then use
`uv run --no-sync`; the ledger records their commits and whether they had uncommitted changes.

## Use

```bash
uv run lattice-lab ask questions/settling-time-hexagon-B2S34.toml --lab lab --workers 8
uv run lattice-lab verify --lab lab --rerun 5     # chain, order, and records rerun byte for byte
uv run lattice-lab report --lab lab               # rebuild the latest report from the ledger
uv run lattice-lab selfcheck --out docs/selfcheck.md
uv run lattice-lab laws
```

To put a question to other models (Claude Fable and ChatGPT) and record their answers verbatim,
see [docs/consultations.md](docs/consultations.md#running-a-consultation):

```bash
uv sync --group consult            # the two API clients
uv run lattice-lab consult ask 2026-10-21-next-steps --preset direction --dry-run
uv run lattice-lab consult ask 2026-10-21-next-steps --preset direction
uv run lattice-lab consult review 2026-10-21-next-steps
```

`ask` prints a JSON summary and writes `lab/reports/<id>-<n>.md`. The verdict is one of:

| Verdict | Meaning |
| --- | --- |
| found | One law passed its held-out test, no rival as simple is within 6 BIC points on all the data, and the verdict survives dropping the smallest sizes and each size in turn |
| fragile | A law passed, but the verdict changes when some fitted size is left out |
| inconclusive | Laws that passed are too close to call, or nothing could be tested (seeds unsettled at every cap, no budget, no sizes left) |
| none fits | Every candidate's held-out predictions were rejected, or none fits the data at all |

### A question

```toml
id = "settling-time-hexagon-B2S34"
rule = "B2/S34"
shape = "hexagon"            # square, hexagon, triangle (+ triangle_mode)
density = 0.5
seeds = 20
fit_sizes = [8, 10, 12, 16, 20, 24, 32]
heldout_pool = [40, 48, 64, 96, 128]   # "24x26" for a rectangular torus
```

Defaults (all overridable): `heldout_per_round = 3`, `max_rounds = 2`, `cap = 2000` and
`max_cap = 64000` generations, `laws` = constant, logarithmic, linear, power, exponential,
exponential in the area, `space = "auto"` (log when every value is positive), `alpha = 0.01`,
`decisive_bic = 6`, `budget_cell_steps = 2e11`. Version 1 asks one quantity, `settling_time`:
the median generation at which a soup's final cycle begins, against the torus size (for a
rectangle, the square root of its cells).

### The lab directory

```
lab/
  ledger.jsonl          every question, run, observation, plan, prediction and verdict
  records/<id>-<n>.jsonl  LatticeLife's raw records for that question
  reports/<id>-<n>.md   the report, rebuilt from the ledger by `report`
```

Keep a lab directory as data, apart from this code. Reports state how many questions the
ledger holds, since scanning many rules turns up chance fits.

## Example: B2/S34 on the hexagon lattice

`examples/lab-b2s34/` is a complete lab from `uv run lattice-lab ask
questions/settling-time-hexagon-B2S34.toml` on the pinned commits: the ledger, LatticeLife's 200
records and [the report](examples/lab-b2s34/reports/settling-time-hexagon-B2S34-0.md).
`uv run lattice-lab verify --lab examples/lab-b2s34` checks it.

Its answer is not the prototype's. Fitted on L = 8 to 32 and tested at 64, 96 and 128, the
verdict is **found: logarithmic**, T(L) = 37.6 log L − 36.3 (± 2.7 and ± 8.3, all sizes). A
power law also passed its held-out test (p = 0.09), but on all ten sizes it is 8.4 BIC points
worse. The verdict holds with the smallest sizes dropped and with each size left out. The
prototype reported T ≈ 27·L^0.35. Before the run, the plan said these sizes and seeds could
not be expected to separate the two (an expected BIC difference of 3.9 against a margin of 6;
about 1.5× the seeds would), so the margin seen is more than the design promised: treat this
as one answer to replicate with more seeds or larger tori, not a settled fact. It has since been
replicated, in a registered study on tori up to 1024 with 100 seeds each, where the power law was
rejected ([docs/settling-time.md](docs/settling-time.md)).

## Beyond settling time: what else Kepler finds in LatticeLife data

[docs/capabilities.md](docs/capabilities.md) runs each of Kepler's newer tools on real
LatticeLife simulations (`uv run python examples/capabilities/run.py`):

- survival windows and how their edges move with torus size (a binomial likelihood, one fit over
  density and size);
- times that are only bounds (a censored likelihood);
- whether a law depends on the starting density (shared constants);
- relaxation and damage over time, with seed-to-seed error bars;
- distributions of object sizes;
- exact formulas for periods (the studies below);
- conserved quantities (a parity of births, found from data and then proved);
- whether a fitted constant is a known number.

The loop itself still asks only about settling time; these studies are ready to become question
types.

## Periods of the parity rules

The parity rule sets each cell to the parity of its live neighbours. It is linear over GF(2), so
its period on an n x n torus can be both measured and proved. Write n = 2^v(n) m with m odd, and
sord(m) for the least j with 2^j = +-1 modulo m. In each study Kepler found the law from
simulations, the law's predictions were registered in a ledger before the sizes were computed,
and the proofs came afterwards.

| Rule | Law | Tested in advance | Proved |
| --- | --- | --- | --- |
| B1357/S1357, square ([write-up](docs/xor-periods.md)) | 2^v(n) (2^sord(m) - 1) | confirmed at 45 sizes by simulation and at all 198 from 3 to 200 exactly; the rival (rule 90's period) refuted at all ten sizes where it differs | reduced to odd sizes; settled by machine for every odd part up to 999 except ten ([proof](docs/xor-periods-proof.md)) |
| B135/S135, hexagon ([write-up](docs/parity-lattices.md)) | first 2 * 2^v(n) (2^sord(m) - 1); corrected to 2 * 2^v(n) R(m), R(m) = rule 90's period on m cells | first law refuted at 3 of 70 sizes (74, 148, 190, by a factor of 3); corrected law confirmed at all 100 sizes from 202 to 400 | **the whole law, for every even n**; the key step is that two hexagon generations are three passes of rule 90. The 2-part is also in Lean, proved by an LLM agent ([pilot](docs/llm-pilot.md)) |
| B13/S13 and B1,3,...,11/S1,3,...,11, triangle ([write-up](docs/parity-lattices.md)) | 2 * 2^v(n) (2^sord(m) - 1) | confirmed at all 154 sizes registered | the factor 2 * 2^v(n) for every even n, also in Lean, proved by an LLM agent ([pilot](docs/llm-pilot.md)); the odd part checked by machine for every odd part up to 999 except ten |

What is new, as far as a web search went:

- **Known before.** The square rule's odd sizes up to 23 were published by McLaughlin, and the
  structure of these laws is Martin, Odlyzko and Wolfram's for rule 90 (1984). Vadali and Turner
  (2025) proved the four-neighbour square rule has rule 90's cycle lengths.
- **Not found in the literature:** the square eight-neighbour rule escapes rule 90's shortfalls,
  the hexagonal rule shares them exactly, and the triangular rules escape them. The identity
  behind the hexagon result is elementary, and a specialist may know it.
- **Who did what.** Kepler found each law from data. The registered tests showed where the
  hexagon's was wrong, and the corrected law and the proofs were reasoning added afterwards.
  Since then Kepler's vocabulary includes the periods of the 1D linear rules. A registered replay
  (`examples/kepler-rediscovery`) shows it now lists the corrected law on the discovery data,
  names n = 74 as the size that decides, and on data up to 200 keeps the right law on every
  lattice, predicting all 98 hexagon periods at 202 to 400. That shows capability in hindsight;
  it is not a fresh discovery.

**A blind atlas** ([write-up](docs/linear-atlas.md), `examples/linear-atlas`). Kepler then
proposed laws for all 42 rules built from symmetric neighbour shells on the three lattices, 38
of them unstudied. The laws came from tori up to 60. Every law, tied rivals included, was
registered at each new size before any was computed. On exact checks at 1,930 (rule, size) pairs
up to n = 160:
- **all 34 rules that got a law kept one at every size**;
- no rule had every law refuted;
- Kepler's first choice held for 19 rules, and a registered rival for the other 15;
- 8 rules got no law, and each is a quadratic in its lattice's nearest-neighbour rule.

Afterwards, not registered: the laws split into two families, and the rules' polynomials sort
them into those families without exception among the 32.
- **Rules that factor into passes of 1D rules along lattice directions** have that rule's period
  and inherit its shortfalls.
- **Rules that do not factor** reach the full bound.

This includes rule-150 analogues of Vadali and Turner's theorem and of the hexagon theorem.

**Round 2 registered the pattern** (`examples/linear-atlas-2`) and made 5,048 exact checks.
- **The atlas laws:** all 34 held at all 624 new sizes, which were chosen where the two families
  part, up to n = 400.
- **New rules:** for 112 square rules nobody had computed, plus the four without a law, the
  pattern predicted each period at odd n from the factorisation alone. **106 of the 113
  predictions held, and 7 failed, so the pattern as registered is refuted.**
- **Three of the failed rules** are confined without splitting: two are perfect cubes and one is a
  rule in x^3, y^3. After the first failure of each kind, the sizes and periods where they must
  fail were committed before those sizes were computed. All 55 came out as written.
- **The other four** fail at one small size each (n = 13 or 37). Two are explained since: at
  n = 13 they are sums of one 1D polynomial along each axis, and it sends every rule-90 value
  into the subfield F(8) (`examples/linear-atlas-2/subfield.py`). The n = 37 one, with every
  eigenvalue a cube, was explained later by the fourth LLM pilot (below).

**Round 3** (`examples/linear-atlas-3`, registered in `223e56f`) wrote the refined statement as a
fixed procedure, `atlas3.predict`: dilation, odd prime power, a complete 1D split, and otherwise
the full bound. It predicts the odd part of each period from the polynomial alone. It was
registered for 344 new rules on all three lattices, with nine new shells, at odd parts from 9 to
141, small sizes included: 11,358 predictions. Before registration it reproduced 7,746 of the
7,750 earlier data points. The run was stopped at a two-hour limit and finished by the harness's
new `resume` step; an independent eigenvalue computation agrees with all 11,662 records.
- **43 predictions failed (0.4%)**, so both registered hypotheses are refuted: strict, and
  "failures only at m <= 61, at most 1%".
- **Every dilation (1,017) and perfect-power (272) prediction held**, and 164 of 165 splits.
- **Seven failures are one rule, triangle VO+T13.** Its polynomial is the edge rule's times its
  own dilation by 3, which is a disguised power wherever 3 = +-2^k modulo m. An expectation built
  on that was written during the run, before 29 of its 34 sizes, and matched all 34.
- **The other 36 are at m = 13, 15, 21, 25 and 37.** There the rules have only 3 to 9 distinct
  eigenvalues, all inside a subfield or the cube subgroup; that is chance in small fields. The
  m = 37 case is not chance, and neither is round 2's one at 37. A census found six such rules
  at 37, and the fourth LLM pilot's agent explained and proved all six
  ([llm-pilot.md](docs/llm-pilot.md#pilot-4-the-cubes-at-m--37)).

Each study is a directory under `examples/`. The ones with ledgers check with
`uv run lattice-lab verify --lab <dir>`.

| Directory | What it holds |
| --- | --- |
| `xor-periods` | square rule, round 1: simulations of 45 registered sizes |
| `xor-periods-algebra` | square rule, round 2: exact periods for n = 3..200 |
| `xor-periods-proof` | square rule: the odd-size machine check up to 999 |
| `parity-lattices` | hexagon and triangles: discovery, the exact engine, round 1 (210 predictions) |
| `parity-lattices-hexagon` | round 2: the corrected hexagon law at 100 sizes, the triangles at 7 |
| `parity-lattices-proof` | triangles: the odd-part machine check up to 999, with the hexagon as control |
| `settling-time-replication` | B2/S34 settling times on hexagon tori up to 1024 (registered) |
| `settling-universality` | eight random rules on four lattice types: settling-time laws and their fluctuations (registered) |
| `settling-time-local` | B2/S34's local settling times on 256 and 1024 tori: round 2 (registered) |
| `kepler-rediscovery` | Kepler's search, with 1D linear-rule periods, replayed on the period data (registered) |
| `linear-atlas` | 42 shell-built linear rules: exact engine, discovery, Kepler's laws judged at 1,930 new pairs (registered), factorisation analysis |
| `linear-atlas-2` | the factorisation pattern registered: the 34 laws at 624 decisive pairs, and 116 square rules predicted from their factorisation (registered); the cubes and dilation found afterwards |
| `linear-atlas-3` | the refined statement registered: 11,358 predictions of odd parts for 344 new rules on all three lattices (registered; resumed once); the eigenvalue cross-check and the failure analysis |
| `llm-pilot` | the LLM-central pilot: problem card, tools, sandbox, judge, the agent's submission, and the hexagon law at 15 new sizes (registered) |
| `llm-pilot-triangle` | the second pilot, on the triangle laws' 2-part, run in a separate container: card, setup, judge, transcript audit, the agent's submission and transcript, and both triangle laws at 20 new sizes (registered) |
| `llm-pilot-vot13` | the third pilot: the agent finds VO + T13's law from data and proves it; card, data, judge (with the law evaluated at unseen sizes), audit, the agent's submission and transcript, and the law at 20 new sizes (registered) |
| `llm-pilot-37` | the fourth pilot, on an open question: why six rules have only cube eigenvalues at m = 37. The census of all 1,274 rules, card, data, judge (the agent's condition run on every rule at 94 sizes and checked by eigenvalues), the held-out census (registered), audit, the agent's submission and transcript |
| `llm-pilot-25` | the fifth pilot, on the cubes at m = 25: the square family, card, data, tools, judge (the agent's condition on the atlas at 94 sizes and on the family at 16), the family's census at 14 held-out sizes (registered; chance refuted at 6), audit, the agent's submission and transcript |
| `llm-pilot-37b` | the sixth pilot, on the 16 square-family rules confined at m = 37 that pilot 5's census found: the pre-check, card, data, both earlier conditions as tools, judge, the family's census at 17 held-out sizes (registered), audit, the agent's submission and transcript |
| `llm-pilot-37c` | the seventh pilot, on Claude Fable, on the five ninth-power rules at m = 37: card, data, all three earlier conditions and a fast census as tools, judge, the registered radius-6 census, audit, the agent's submission and transcript, and the second round over the API that fixed its Lean (`round2.py`) |
| `hexagon-family` | the registered held-out test of the hexagon-family classification from the rule-4850 deep dive: 41 predicted period odd parts at 37, 13 and other sizes (the classification holds: 35 of 35 tested, 6 untested) |
| `qec-bb` | the first step toward quantum codes ([next-direction.md](docs/next-direction.md)): a bivariate bicycle code's logical qubits from the torus's characters, against linear algebra and twelve published codes (registered; both predictions held) |
| `qec-distance` | the published codes' distances by two exact instruments, an integer program (SCIP) and an exhaustive search in C, with method checks on random, toric and trinomial codes (registered; all 12 reproduced, one method check failed; [write-up](docs/code-distances.md)); `check-independent/`, the independent checker's development records |
| `qec-distance-2` | the re-test of both instruments as fixed (SCIP's XOR presolving and rapid learning off; the search with iterative deepening), on fresh codes, the known fault cases, the published codes and a power test with SCIP's defaults as control (registered; the instruments hold) |
| `census-remainder` | the 45 census entries pilot 4 left, sorted: forced subfields, a chance model and its calibration (all 32,768 symmetric square rules within distance 4 at m = 21 and 25), hidden symmetries mod m; pilot 5 later explained 19 of them, and pilot 7's condition covers 27, among them 10 that no earlier condition covered ([write-up](docs/census-remainder.md)) |
| `fable-units` | a registered test of Claude Fable's unit criterion and pyramid rules from a consultation: predictions from the fundamental unit and class number alone, decided by direct computation in GF(2)[x]/Phi_p ([write-up](docs/consultations.md)) |
| `consult-budget` | what a consultation's effort is worth: two answered questions put to Fable at three settings, every claim checked by machine, rubrics graded blind; cost per verified answer, and two findings ([write-up](docs/consultations.md)) |
| `rule-4850` | rule 4850's ninth powers at m = 37: the pre-check, the consultation's question, a fast census by discrete logs, and the registered radius-5 census that refuted chance ([write-up](docs/consultations.md)); `deep/`, the multi-agent deep dive that explained it, with its investigators', verifiers' and checkers' scripts and [the report](examples/rule-4850/deep/REPORT.md) |

## Settling times: a replication and a universality test

[docs/settling-time.md](docs/settling-time.md) takes the loop's own B2/S34 answer to rules with no
exact theory. It uses two registered studies, both built on `lattice_lab.study`: a harness that
writes a study's predictions to the ledger and refuses to run it until they are committed and
pushed.

- **Replication** (`examples/settling-time-replication`). On hexagon tori up to 1024, B2/S34's
  median settling time stays logarithmic in the size, and the power law is rejected. Two
  extreme-value mechanisms predicted the fluctuations from each law's constants. The heavy-tailed
  one failed outright. The light-tailed one (Gumbel) got the shape and constancy right but the
  size wrong.
- **Universality** (`examples/settling-universality`). Eight rules were drawn at random on the
  square, hexagon and both triangular lattices. For all eight, the log law held and the power law
  failed. The fluctuations share one shape and one ratio of spread to growth on every lattice.
  Both match the Gumbel values for the largest of about L^2 independent times: 0.177 +- 0.023
  against 0.2215, and 0.765 +- 0.029 against 0.786. This is extreme-value universality, not
  a critical point's. At these error bars, Kepler's identify cannot yet name the class blind.
- **Round 2** (`examples/settling-time-local`) tested a post-hoc idea for Study A's miss, on
  B2/S34's local settling times (when each block of the torus settles; a new LatticeLife
  instrument). They are the same on every torus size but not independent: late regions cluster.
  The miss itself was a low draw. With all the data, B2/S34's ratio is 0.765 +- 0.042, the same
  as the eight rules'.

## Trusting the answers

- **Self-check.** `selfcheck` runs the loop on synthetic data from every law, with the sizes,
  seed spreads and censoring of real runs. It compares the outcome with pass marks committed in
  `thresholds.toml` before its first run and never edited to pass. The latest result is in
  [docs/selfcheck.md](docs/selfcheck.md); [docs/selfcheck-history.md](docs/selfcheck-history.md)
  records every full run, including the first, which failed, and what changed in the loop.
- **Known rules.** The empty rule `B/S` gives a constant. A linear rule's transients and periods
  match an independent GF(2) computation (`tests/test_known_rules.py`).
- **Order.** `verify` checks every verdict's predictions were written before its run started,
  and every held-out record was appended after that.
- **Reproducibility.** `verify --rerun N` reruns records from their seeds and settings and
  compares the bytes.
- **The prototype's traps** are regression tests (`tests/test_traps.py`): a zero starting
  constant must not vanish; a verdict must survive dropping the smallest sizes; an unsettled run
  must never count against a law.
