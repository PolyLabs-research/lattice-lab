# Problem card: why are the eigenvalues cubes at m = 37?

This card is the whole brief for the pilot's proposer. It states an open question, the data, and
the tools. **Nobody knows the answer**, including whoever wrote this card. A precise negative
result is also useful.

Paths below are relative to the root of this repository checkout (the sandbox).

## Setup, first

Run `./setup.sh > setup.log 2>&1` once, in the background. It makes a Python environment with
numpy and sympy (`./python`), installs the Lean toolchain, and builds mathlib from source (half an
hour to an hour). Lean is optional in this pilot; Python is ready within a minute.

## The setting

A **shell rule** of the atlas is a linear cellular automaton over GF(2) on the square, triangular
or hexagonal lattice: each cell becomes the sum mod 2 of the cells in a union of symmetric
neighbour shells, optionally with itself (`self`). On the square and hexagonal lattices a rule is a
Laurent polynomial f(x, y) over GF(2): the set of translations it reads. On the triangle it is a
2 × 2 matrix M with M² = s I, and s is the plane rule that governs it. `data/rules.json` lists all
1,274 shell rules with their polynomial (for the triangle, s) as exponent pairs, and
`data/shells.json` the shells.

**Periods and eigenvalues.** On the torus (Z/m)², m odd, a rule f acts diagonally in the
characters: its eigenvalues are f(ζ^j, ζ^k), for ζ a primitive m-th root of unity in F(2^d),
d = ord_m(2). The **odd part** of the rule's period is the lcm of the multiplicative orders of its
nonzero eigenvalues. (The Lean library proves this: `period_eq_eigenLcm` in `Bridge.lean`.) Every
shell rule is symmetric, so its eigenvalues lie in F(2^sord(m)), where sord(m) is the least j with
2^j ≡ ±1 (mod m), and the odd part divides the **full bound** 2^sord(m) − 1.

**What confines eigenvalues.** Over three registered rounds, the atlas found that a rule's odd
part reaches the full bound unless something confines its eigenvalues to a proper subgroup. The
known mechanisms, each proved:

1. **splitting**: f is a product of one-dimensional rules along lattice directions, so its
   eigenvalues are products of their values. Rule 90 (x + 1/x) is the basic one: its eigenvalues
   are t_j = ζ^j + ζ^−j, a = x + 1/x and b = y + 1/y on the square;
2. **powers**: f = g^k, so its eigenvalues are k-th powers;
3. **dilations**: f = h(x^p, y^p) with p dividing m, so f lives on the m/p torus;
4. **twisted powers**: f = g(x, y) g(x^d, y^d) with d ≡ ±2^k (mod m), so its eigenvalues are
   λ^(1+2^k). This is triangle VO + T13.

The `predicted` and `step` columns of `data/census37.csv` are the atlas procedure's call, which
applies 1 to 3. On top of these come **coincidences in small fields**: at m ≤ 25 rules with only a
handful of distinct eigenvalues sometimes have all of them in a subfield or in the cubes, as
chance allows.

## The question

**At m = 37**, d = ord_37(2) = 36 and sord(37) = 18. The full bound is 2^18 − 1 = 262143 = 3 ·
87381, and 87381 is rule 90's own period there: its eigenvalues t_j are all cubes in F(2^18).

Six rules, on which none of the four mechanisms acts, have **every nonzero eigenvalue a cube** at
37, and odd part exactly 87381 (`data/census37.csv`). With the number of distinct nonzero
eigenvalues up to Frobenius conjugacy:

| Rule | Translations | Distinct eigenvalues |
| --- | --- | --- |
| square A4 + K8 + B4 + self | 17 | 11 |
| triangle VS + T9 + T13 + self (its s, irreducible) | 43 | 9 |
| square K8 + M8 + E4 | 20 | 10 |
| square C4 + L8 + M8 | 20 | 10 |
| square C4 + L8 + M8 + E4 | 24 | 9 |
| square A4 + B4 + C4 + L8 + E4 + self | 25 | 11 |

Conjugates are cubes together, and a value is a cube one time in three, so by chance each rule
would be confined about once in 3^9 to 3^11 (20,000 to 180,000). Among 1,274 rules that is not
chance. **Each of the six reaches the full bound at every other odd m from 9 to 161**, including
95, 101 and 111, where rule 90 also falls short: 37 is its only shortfall. The first two were found
in registered tests; the other four by a census of all 1,274 rules.

**The census** (`data/unexplained.csv`) lists, for every odd m from 9 to 161 at which the cubes
form a proper subgroup (d even), every rule whose nonzero eigenvalues are all cubes although none
of the four mechanisms accounts for it. Below 37 the list holds the small-field coincidences.
Above it there are few entries.

**What has been tried:** a search for a factorisation of these rules into rule-90 values along
linear forms (up to four factors, coefficients up to 3) found none. A full search over the
torus's changes of coordinates was too slow.

**Find the mechanism**: a condition on a rule f and an odd m that forces every nonzero eigenvalue
of f at m to be a cube (or, more generally, a q-th power), that holds for these rules at 37, and
that you can prove. Say which of the census's entries it explains, and where else it predicts
confinement, including sizes and rules the census has not looked at.

## Deliverables

1. **`mechanism.py`**, defining

   ```python
   def condition(f: frozenset[tuple[int, int]], m: int) -> int
   ```

   for f a rule's polynomial as in `data/rules.json` and m odd. Return q > 1 if your mechanism
   proves that every nonzero eigenvalue of f at m is a q-th power in F(2^d)*, d = ord_m(2), with
   q dividing 2^d − 1; return 1 when it makes no claim. It must decide from the structure your
   mechanism names, not by computing the eigenvalues and testing them; the judge reads it. It
   must take at most about a minute for all 1,274 rules at one m ≤ 300.
2. **`proposal.md`**: the mechanism, the proof that your condition implies the claim, how you
   found it, which entries of the census it explains and which not, and where else it predicts
   confinement.
3. **`proposal.py`**: numerical checks of the mechanism with the tools. It prints what it checked
   and whether each check held.
4. **Optional, Lean**: any formal results in `proofs/LatticeProofs/Pilot.lean` (or files under
   `proofs/LatticeProofs/Pilot/`). The judge builds them and lists each theorem's axioms.
5. **`report.md`**: what you found, what you tried, what failed, and what you are unsure of.
   Write it last: the judge starts when it appears on your branch.

Scratch files go under `scratch/`. Commit and push your work to your branch as you go.

## How it is judged

- **Explains**: `condition` on the six rules at 37.
- **Sound**: the judge runs `condition` on all 1,274 rules at every odd m in a grid that goes
  beyond the census, and checks each claim with its own eigenvalue computation. One false claim
  refutes the mechanism as stated. You are not told the grid's results.
- **Reach**: how many confinements the condition accounts for, inside and outside the census,
  and how many the four known mechanisms do not.
- **Proof**: the orchestrator reads the argument in `proposal.md`; Lean results count for more.

## Tools (`tools/`)

- `eigen.py`: `Field(m)`, eigenvalues, Frobenius orbits, orders, `is_power`, `odd_part`,
  `full_bound`.
- `gf2.py`: the finite fields themselves.
- `tori.py`: small tori and exact periods by simulation, for spot checks.

sympy is available for polynomial algebra over GF(2) (factoring, Gröbner bases, resultants). Run
Python with `./python` (after setup).

## The Lean library (`proofs/LatticeProofs/`), if you want it

Lean 4 with mathlib v4.35.0, namespace `LatticeProofs`. `Bridge.lean` has the square torus,
`period`, characters `chi`, eigenvalues `lam`, `isPeriod_iff`, `period_eq_eigenLcm` and
`exists_primitiveRoot`; `Eigen.lean` has order lemmas in characteristic 2; `Periods.lean` proves
the cube and twisted-power mechanisms for particular rules (for example `period_sqN4K8C4`,
`period_triSVOT13`); `Rules.lean` has generated rules. The rules of this question are not in
`Rules.lean`; define what you need in `Pilot.lean`.

## Rules

- **Stay in this checkout.** Work only inside this repository's directory. Do not read, list or
  search anything outside it, except the Lean toolchain under `~/.elan` and
  `~/lean-toolchains`, which setup.sh installs.
- **This branch only.** Do not fetch, check out, list or read any other branch, tag or commit of
  this repository, or any other repository (no `git fetch`, `git log --all`, `git ls-remote`,
  `add_repo`, `git clone`). Push only to your own branch.
- **No network** beyond what setup.sh does: no web search, no web fetch, no downloads. (The
  literature may know this; the pilot measures what you can find without it.)
- **No other sessions.** Do not list, read or message other Claude sessions, and do not start
  subagents: the pilot audits this session's own transcript, so all the work must be in it.
- Do not change any existing file except `proofs/LatticeProofs/Pilot.lean`. The judge compares
  the others with the base commit and with `manifest.json`.
- In Lean: no `sorry` in what you claim, no new `axiom`, no `native_decide`.
- **Build** (if you use Lean):

      cd proofs
      export PATH=$HOME/.elan/bin:$PATH ELAN_TOOLCHAIN=v4.35.0-local
      lake build LatticeProofs.Pilot
