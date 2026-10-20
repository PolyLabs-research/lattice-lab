# Rule 4850 at m = 37: the dossier

Everything the project knows about rule 4850, for the deep dive. Paths are relative to
/home/user/lattice-lab unless they start with /home/user/pilot-37c-round2 (the seventh pilot's
sandbox, with its tools/, data/ and scratch/).

## The question

At m = 37, every nonzero eigenvalue of the symmetric square rule 4850 (radius 4) is a ninth power
in F(2^18)*: its period divides 29127 = (2^18 − 1)/9. None of the known mechanisms explains it.
Is there a mechanism (a condition on a rule and a size that forces this, provable), or is it
chance? If a mechanism, what is it, and does it also explain its relatives below?

## Setting

- **Rules.** The square family: rule n of radius r is the union of the D4-orbits (a, b),
  0 ≤ b ≤ a ≤ r, selected by the bits of n in the order of
  `examples/rule-4850/census.py: orbits(r)` (`census.rule(n, r)` gives the exponent set). A rule
  is a Laurent polynomial f(x, y) over GF(2); symmetric rules are polynomials in a = x + 1/x and
  b = y + 1/y.
- **The field at 37.** ord_37(2) = 36, so ζ (a primitive 37th root of 1) lies in F(2^36), and a
  symmetric rule's eigenvalues f(ζ^j, ζ^k) lie in F(2^18). 2 is a primitive root mod 37,
  2^9 ≡ −6 and 6^2 ≡ −1 (mod 37).
- **The group.** |F(2^18)*| = 262143 = 3^3 · 7 · 19 · 73.
  - The ninth powers form the subgroup of index 9, of order 29127; it equals F(2^9)* · μ3 · μ19.
  - So λ is a ninth power ⟺ its discrete log is ≡ 0 (mod 9) ⟺ λ^511 ∈ μ57, where
    λ^511 = λ̄/λ for the Frobenius x → x^(2^9).
  - F(2^9)* consists of 27th powers.
- **Classes.** The 1368 nonzero characters fall into 11 classes. Ninth-power-ness is constant on
  each, since λ(2c) = λ(c)^2 and the D4 symmetries apply. The census order of their
  representatives is (0,1), (1,1), (1,2), (1,3), (1,4), (1,5), (1,6), (1,7), (1,8), (1,10),
  (1,13).
  - Equivalently, (1, 2^i) for i = 0..9, plus the axis.
  - On the line through (1, k) the eigenvalues are the Frobenius conjugates of g_k(ζ), where
    g_k(x) = f(x, x^k).
- **Forced classes** (Fable, consultation round 2). For every symmetric rule:
  - class (1,6), that is i = 9, lies in F(2^9) and so is always a 27th power;
  - the axis class is F(0, t): for 4850 that is t^3, a ninth power because rule 90's values are
    cubes.

  The diagonal (1,1), i = 0, is F(t, t) = t^2(1 + t + t^2)^2 for 4850, explained by cyclotomic
  exponents. **So 4850's confinement is the statement that F(t, t^(2^i)) is a ninth power for
  i = 1..8, at t = t_1 = ζ + 1/ζ: eight conditions.**
- **Rule 90's class is the Legendre symbol** (Fable round 2, checked). As group-ring
  identities at 37:
  - t(x)^29127 = Σ_{u nonresidue} x^u, so t_j^29127 = ρ^((j/37)) with ρ of order 3;
  - (1 + t(x))^29127 = 1, so rule 150's values are ninth powers;
  - t(x)^87381 = 1 + J, where J = Σ x^k.

  Equivalently, 1 + ζ is a cube but not a ninth power in F(2^36)*.

## Rule 4850

- **Orbits:** (1,0), (2,1), (2,2), (3,0), (3,1), (3,3), (4,2).
- **As a polynomial:** F(a, b) = s^3 + P^2 s^2 + P^3 + P^2 + P, with s = a + b and P = ab. It is
  irreducible over GF(2), and so is x^4 y^4 f.
- **Its 45° rotation,** (x, y) → (xy, x/y), a map in GL2(Z/37) that permutes the eigenvalues, is
  rule 10491524 of radius 6. There it is a cube plus a square:

      F' = (ab)^3 + (a + b)^4 (1 + a)^2 (1 + b)^2 + (a + b)^2 = π^3 + σ^2 (1 + σ e)^2,

  with σ = a + b, π = ab and e = (1 + a)(1 + b). Here π is a cube and e is a ninth power (rule 7).
  - The seventh pilot also writes F' = N_{F(2^54)/F(2^18)}(π + c) with c^3 = Y^2, "without a
    visible reason".
- **Lines** (pilot 7, `scratch/linefactor.py`):
  - k = 0, 1, 2 are exact cyclotomic products: t^3, t^2 Ψ5^2 and t^4 Ψ13;
  - k = 3 is t^2 times a quintic factor of Ψ31 times a septic factor of Ψ127;
  - the lines k = 4, 5, 7, 8, 10, 13 have irreducible factors of degrees 13, 13, 16, 19, 8+12+13
    and 11+35.
- **Eigenvalues.** No zero eigenvalue except at the trivial character. R(4850)^29127 =
  1 + J·J_y, and R(4850)^9709 ≠ that, so the eigenvalues are ninth powers but not all 27th
  powers.
- **Class logs mod 27,** in census order: [18, 9, 9, 18, 0, 9, 0, 9, 9, 9, 18].
- **Class logs mod 513** (log in F(2^18)* modulo F(2^9)*, using the generator of
  `/home/user/pilot-37c-round2/scratch/f18.py`): [18, 198, 9, 234, 162, 63, 0, 495, 9, 387, 180].

## Its relatives (radius ≤ 6, all ninth-power confined at 37, none explained)

| rule | radius | relation | logs mod 27 (census order) |
| --- | --- | --- | --- |
| 4850 | 4 | itself | 18 9 9 18 0 9 0 9 9 9 18 |
| 482758 | 5 | 4850 · (1+a)(1+b) exactly | 0 0 9 9 18 9 0 0 9 0 18 |
| 10491524 | 6 | 4850 rotated by 45° (an image under GL2(Z/37)) | 9 9 18 18 18 9 0 18 0 9 9 |
| 8438150 | 6 | 4850 · Φ3(xy) Φ3(x/y) exactly | 9 0 0 18 0 9 0 18 0 0 18 |
| 43250486 | 6 | 4850 · Φ3(x)^2 Φ3(y)^2 exactly | 9 18 9 0 9 9 0 18 9 18 18 |
| 20982139 | 6 | **none known**: same mod-27 pattern as 10491524 | 9 9 18 18 18 9 0 18 0 9 9 |
| 178279803 | 6 | **none known**: same mod-27 pattern as 10491524 | 9 9 18 18 18 9 0 18 0 9 9 |

Checked on 2026-10-20: the ratios 20982139/10491524 and 178279803/10491524 have logs
≡ 0 (mod 27) at every class (27th powers), but not ≡ 0 (mod 513). Their 19-parts, log/27 mod 19,
are [8, 17, 18, 11, 1, 4, 0, 7, 0, 16, 6] and [1, 3, 11, 12, 8, 13, 0, 18, 0, 14, 10]. So they are
not 10491524 times something F(2^9)-valued.

## The known mechanisms (what "explained" means)

1. A split into one-dimensional factors.
2. A power (f = g^q exactly).
3. A dilation.
4. A twisted power or twisted pair: C(x^a, y^a) C(x^b, y^b) with b ≡ ±2^k a.
5. Half-Frobenius confinement (pilot 4): f · N ≡ B (mod x^m − 1, y^m − 1), with B invariant under
   a dilation by 2^g (so B is F(2^g)-valued) and N a product of orbit units; at 37 B is
   F(2^9)-valued.
6. Cube certificates (pilot 5).
7. A unit times a power (pilot 6): f = U g^3.
8. Exponent bookkeeping on top of 5 and 7 (pilot 7): exact exponents of the line units. This
   explains 699738, 985232, 1431278 and 1968276 as ninth powers.

The atlas procedure (`examples/linear-atlas-3/atlas3.py: predict`) covers 1–4. The seventh
pilot's `condition` (`examples/llm-pilot-37c/submission/mechanism.py`, run from
/home/user/pilot-37c-round2) covers 5–8.

## What has been ruled out for 4850 (all at 37, by computation)

From the seventh pilot (`examples/llm-pilot-37c/submission/proposal.md` section 6, scripts in
/home/user/pilot-37c-round2/scratch):

1. **Units times an F(2^9)-valued rule.** Linear algebra mod 171 in the exponent of t_1 has no
   solution for:
   - symmetric orbit products of up to three orbits of radius ≤ 2, or two of radius ≤ 4, with any
     exponents;
   - any three directions of (Z/37)^2, with any exponents.

   The same holds modulo 19 or 9 alone, and for F(2^3)- and F(2^6)-valued targets.
2. **g^3 · U · (F(2^9)-valued)** for every g of radius ≤ 6 and seven units U.
3. **A twisted pair or power.** At 37 every dilation is a Frobenius power, so a twisted pair is a
   power of C. The symmetric cube roots are dense: the lightest has 440 of 1369 terms.
4. **Line-by-line certificates.**
   - Fable's first-round certificate (`consultations/2026-10-20-rule-4850`) is vacuous: ⟨1 + ζ⟩
     meets F(2^18)* in exactly the cubes.
   - The congruence R(4850)·D10·D26 = D8·D6·D23 in Fable's round-2 JSON should be checked for
     vacuity too.
5. **Order-9 Gauss sums times ninth powers.** The Gauss sums of order 9 of F37* lie in F(2^18)
   and are primitive 27th roots of 1. 4850's eigenvalues have a nontrivial μ19-part, and λ̄/λ
   has order 57 on most lines.
6. **Other sizes.** It is not confined at 101, 109, 185 or 197; 109 and 185 are the other s = 18
   sizes.

From Fable's second consultation (`consultations/2026-10-20-rule-4850/round-1/fable-r2.md`):

7. **Factorizations within the family.** None: f ≡ g·h or g·h^2.
8. **f ≡ U·g^3** with g any cube-confined unit of the family: U has minimum weight 392, which is
   not sparse.
9. **Rule-150 units in all 684 directions.**
10. **No genuinely mod-37 transport** to a small box.

## Chance calibration so far

- **Fable** (round 2): the per-class rates over the radius-4 family are:
  - classes i = 1..8 are ninth powers about 1/9 of the time each, independently;
  - class 0 about 0.47 of the time;
  - classes 9 and the axis are forced.

  So a random rule is ninth-confined with probability about 1.1e-8, about 4e-4 expected among
  the 32,767 rules: "about 1 in 3000".
- **The registered radius-5 census** (`examples/rule-4850/`): 5 unexplained new ninth-power
  rules against 0.0066 expected. Pilot 7 then explained 4 of them; the fifth is 482758, a
  multiple of 4850.
- **The registered radius-6 census** (`examples/llm-pilot-37c/records.jsonl`, held-out for
  pilot 7): 83 ninth-power rules, 37 not explained by mechanisms 1–4. Pilot 7's condition covers
  35 of the 37; the two left are 20982139 and 178279803.
- **The open question is therefore 4850 and these two.**

## Tools and data

- **`examples/rule-4850/census.py`:** the fast census at 37. It reads class values from orbit
  coordinates and a discrete-log table **mod 27 only** (255 = zero). Functions: `class_logs(r)`
  (all rules of radius r × 11 classes), `confined`, `rule`, `orbits`, `points`, `characters`,
  `coord`, `log_table`, `power`, `mul`.
- **`/home/user/pilot-37c-round2/scratch/f18.py`:** full discrete logs in F(2^18)*: `log(v)`,
  `value(f, j, k)`, `line_logs`, `class_logs`, `t(j)`. It is built on
  `/home/user/pilot-37c-round2/tools/census37.py`, whose F is F(2^36) with ζ = F.zeta. Building
  its table takes about a minute.
- **`examples/linear-atlas-3/eigen.py`:** `odd_part(rule, m)`, the independent eigenvalue
  checker, for any m.
- **Pilot 7's tools,** in /home/user/pilot-37c-round2/tools: `halffrob.py`, `certificate.py`,
  `unitpower.py`, `census37.py` and `eigen.py`; its condition is
  /home/user/pilot-37c-round2/mechanism.py.
- **Records with class logs:**
  - `examples/llm-pilot-37c/records.jsonl` (the radius-6 census hits);
  - `examples/llm-pilot-37c/data/ninth37.json` (radius 4 and 5);
  - `examples/rule-4850/records.jsonl`.
- **Python:** `/home/user/lattice-lab/.venv/bin/python` (numpy, sympy). The machine has 4 cores
  shared by two investigators at a time.
