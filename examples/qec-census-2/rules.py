"""
The rules of stage 2 of the code census (study.py): what each part predicts, computed from l and
m and stage-1 results only, and the class-level tests that the job and decide apply to codes.

Everything here is arithmetic on l and m (odd parts, gcds of GF(2) polynomials, orders of 2,
divisors), look-ups of stage-1 results (../qec-census/summary.json, and data/ for H9's stage-1
bests), or a function of a code's polynomials and its common zeros that some caller has already
computed. Nothing here computes a code, k, a class or a distance, so nothing here calls
census.guard; the registration's predictions are made from the first two kinds only. The
sections of docs/code-census.md that each rule comes from are named in its docstring ("result
N" is that section's numbered result).

Notation (docs/code-census.md, Structure): l', m' are the odd parts of l and m, 2^s and 2^t
their 2-parts, N = lcm(l', m'). A character χ = (α, β) of the odd part Z_l' x Z_m' is written as
bb.local_terms writes it, (j, k): α = ζ^(j N / l'), β = ζ^(k N / m') for a primitive N-th root
of unity ζ; its type is (ord α, ord β). A common zero is a character with a nonzero local term
(bb.local_terms), and the census's rows store them as "characters".
"""

from __future__ import annotations

import functools
import json
import math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
CENSUS = HERE.parent / "qec-census"
HOLDOUT = CENSUS / "holdout.json"
SUMMARY = CENSUS / "summary.json"

# ---------------------------------------------------------------- the tori


@functools.cache
def holdout() -> dict:
    return json.loads(HOLDOUT.read_text())


def _tori(key: str) -> list[tuple[int, int]]:
    return [(int(a), int(b)) for a, b in holdout()[key]]


def held_out_random() -> list[tuple[int, int]]:
    return _tori("held_out_random")


def held_out_extrapolation() -> list[tuple[int, int]]:
    return _tori("held_out_extrapolation")


def held_out() -> list[tuple[int, int]]:
    """The 122 held-out tori, l <= m, in holdout.json's order (random, then extrapolation)."""
    return held_out_random() + held_out_extrapolation()


def stage1_tori() -> list[tuple[int, int]]:
    return _tori("stage1_tori")


def torus_type(ell: int, m: int) -> tuple[int, ...]:
    """The isomorphism type of Z_l x Z_m: its prime-power cyclic factors, sorted (the rule of
    distance.torus_type, repeated here so that this module imports nothing that computes)."""
    out = []
    for n in (ell, m):
        p = 2
        while n > 1:
            if n % p == 0:
                q = 1
                while n % p == 0:
                    n //= p
                    q *= p
                out.append(q)
            p += 1
    return tuple(sorted(out))


# Exposure (docs/code-census.md, "Exposure the registration should record", and holdout.json).
# Each exposed torus with the reasons it is exposed. Their results are computed and reported
# beside the verdict, which rests on the other held-out tori. "Published form" is this family's
# form (A = x^a + y^b + y^c, B = y^d + x^e + x^f), which examples/qec-distance calls trinomial.
NAMED_EXPOSURE = {
    (12, 12): "the published [[288,12,18]] is on 12 x 12 (../qec-bb/codes.json), and its d was "
    "computed in docs/code-distances.md; (T)'s main table (arXiv:2606.02418) gives codes of "
    "this family's form on 12 x 12 with their polynomials and distances, read in the stage-1 "
    "frontier analysis and while drafting docs/code-census.md",
    (8, 18): "(T)'s main table has a weight-8 code on 8 x 18",
    (6, 24): "(T)'s catalog files list codes on 6 x 24",
    (9, 16): "(T)'s catalog files list codes on 9 x 16",
    (2, 48): "(L) (unitaryfoundation/qldpc-challenge) has a record on a group isomorphic to "
    "Z_2 x Z_48",
    (3, 29): "(L) has a record on a group isomorphic to Z_3 x Z_29",
    (8, 11): "examples/qec-distance-2's run computed the toric code's distance here (its part "
    "(e), a registered size, TORIC_SIZES), which holdout.json's development_sizes_mentioned "
    "omits although its note counts toric-only mentions; the toric code is not of this "
    "family's form, and the family has no code here (l' = 1, the power-of-2 lemma)",
    (10, 13): "examples/qec-distance-2's run computed the toric code's distance here (part (e), "
    "TORIC_SIZES), which holdout.json omits as at 8 x 11; not of this family's form, and the "
    "family has no code here (criterion 1)",
}
EXPOSED_EXTRAPOLATION_REASON = (
    "holdout.json's exposed_extrapolation: earlier development (examples/qec-distance, "
    "examples/qec-distance-2, check-independent's devcodes) mentions this size "
    "(holdout.json's development_sizes_mentioned)"
)
# What the earlier studies' excluded_seen and runs record on each torus of exposed_extrapolation
# (examples/qec-distance/study.py and examples/qec-distance-2/study.py; "k of N draws" means k
# only, no distance). Where nothing of this family is recorded, the family has no code there.
_K300 = "examples/qec-distance: k only of 300 published-form draws ('tier yield')"
_KDRAWS = "examples/qec-distance: k only of published-form draws (program-timing seeds)"
DEVELOPMENT_ON_EXPOSED = {
    (6, 17): "examples/qec-distance-2: k only of 3,000 published-form draws (all k = 0; the "
    "family has no code here, criterion 1), and in its part (c) weight-3 codes of another form "
    "with their distances",
    (6, 18): f"{_K300}; its registered part 1 (c): 3 published-form codes with their distances "
    "(the program and the search), two of them the stalled codes rerun in "
    "examples/qec-distance-2",
    (6, 20): f"{_K300}; the toric code (the independent checker)",
    (6, 21): _K300,
    (6, 24): "examples/qec-distance (program timing): the program's bounds on its first 16 "
    "published-form codes with k >= 4 (15 s each), and longer runs (up to 1,100 s) of 7 of them",
    (7, 15): f"{_K300}; examples/qec-distance-2: k only of 3,000 published-form draws, and in "
    "its part (c) 2 published-form codes with their distances (the program and both searches)",
    (7, 16): "the toric code (examples/qec-distance's run); the family has no code here",
    (8, 13): "the toric code (the independent checker); the family has no code here",
    (8, 18): f"{_KDRAWS}; the family has no code here",
    (9, 12): "examples/qec-distance (program timing, as 12 x 9): the program's bounds on its "
    "first 16 published-form codes with k >= 4 (15 s each), longer runs (up to 1,100 s) of 3 of "
    "them, and formulation variants on a fourth",
    (9, 13): f"{_K300}; the family has no code here",
    (9, 14): _K300,
    (9, 15): _K300,
    (9, 16): f"{_KDRAWS}; the toric code (program timing, the independent checker); the family "
    "has no code here",
    (10, 12): f"{_K300}, at 10 x 12 and at 12 x 10",
    (10, 14): f"{_KDRAWS}; the toric code (examples/qec-distance's run); the family has no code "
    "here",
    (10, 15): _K300,
    (11, 11): "the toric code (the independent checker); the family has no code here",
    (11, 12): "the toric code (examples/qec-distance's run); the family has no code here",
    (11, 13): f"{_KDRAWS}; the family has no code here",
    (12, 12): "the published [[288,12,18]] and its d (examples/qec-distance and part (d) of "
    "examples/qec-distance-2); the distances (12) of random published-form codes in "
    "examples/qec-distance's feasibility probe (seeds not recorded), and k only of its draws at "
    "seeds 0 to 59; the toric code",
}
# Not a torus: docs/code-census.md's exposure section also says that (L)'s list of weight-6
# [[n,k,d]] up to n = 200 includes the n of held-out tori.
L_LIST_EXPOSURE = (
    "(L)'s list of weight-6 [[n,k,d]] up to n = 200, read for stage 1's comparison with other "
    "sources (docs/code-census.md, 'Against other sources'), includes the n of held-out tori: "
    "the held_out_random tori have n = 112 to 200, among them the two with codes of this "
    "family, 3x21 (n = 126) and 3x31 (n = 186). (L) gives [[n,k,d]] (d mostly as an upper "
    "bound) of weight-6 codes of various forms; whether any entry is a code of this family on a "
    "held-out torus was not checked, and no prediction here uses (L). Treatment: the "
    "held_out_random tori are judged as clean; this is recorded so that a reader can weigh it."
)
ISOMORPHIC_NOTE = (
    "what development computed on the exposed twin of a torus judged as 'isomorphic' "
    "(DEVELOPMENT_ON_EXPOSED): 3x36 is isomorphic to 9x12, where the program bounded 16 codes "
    "of this family's form (as 12 x 9); 3x35 and 5x21 to 7x15, where 2 codes of the family had "
    "their distances computed; 3x42 to 6x21, 3x45 to 9x15, 5x30 to 10x15 and 7x18 to 9x14, "
    "where only k of draws was computed; the other 11 (2x51, 2x60, 2x63, 2x65, 2x70, 2x72, "
    "3x34, 3x44, 4x30, 4x33, 5x26) have no code of the family"
)


def exposure() -> dict[tuple[int, int], list[str]]:
    """The exposed held-out tori (l <= m), each with its reasons: every torus of holdout.json's
    exposed_extrapolation, with what the earlier studies record computing there
    (DEVELOPMENT_ON_EXPOSED), and those that docs/code-census.md's exposure section names or
    that holdout.json missed (NAMED_EXPOSURE)."""
    out: dict[tuple[int, int], list[str]] = {}
    for t in _tori("exposed_extrapolation"):
        reason = EXPOSED_EXTRAPOLATION_REASON
        if t in DEVELOPMENT_ON_EXPOSED:
            reason += f"; recorded there: {DEVELOPMENT_ON_EXPOSED[t]}"
        out.setdefault(t, []).append(reason)
    for t, why in NAMED_EXPOSURE.items():
        out.setdefault(t, []).append(why)
    return dict(sorted(out.items()))


def isomorphic_to_exposed() -> dict[tuple[int, int], list[tuple[int, int]]]:
    """Held-out tori that are not exposed but are isomorphic as groups to an exposed one, with
    those exposed tori. Codes on isomorphic tori correspond (distance.torus_type); what was seen
    on an exposed torus concerns particular codes there, most of whose images are not of this
    family's form, so these tori are judged with the clean ones, and decide() also reports each
    part on the tori that are neither exposed nor isomorphic to an exposed torus ("strict")."""
    exposed = exposure()
    out = {}
    for t in held_out():
        if t in exposed:
            continue
        twins = [e for e in exposed if torus_type(*e) == torus_type(*t)]
        if twins:
            out[t] = twins
    return out


# ---------------------------------------------------------------- odd parts, GF(2) polynomials


def two_part(n: int) -> tuple[int, int]:
    """n = 2^a n' with n' odd: (2^a, n')."""
    t = n & -n
    return t, n // t


def odd(n: int) -> int:
    return two_part(n)[1]


def v2(n: int) -> int:
    """The exponent of 2 in n."""
    return two_part(n)[0].bit_length() - 1


def _gf2_mulmod(a: int, b: int, mod: int) -> int:
    """a b mod `mod`, GF(2) polynomials as ints (bit i is the coefficient of x^i)."""
    dm, out = mod.bit_length() - 1, 0
    while b:
        if b & 1:
            out ^= a
        b >>= 1
        a <<= 1
        if a >> dm & 1:
            a ^= mod
    return out


def _gf2_mod(a: int, mod: int) -> int:
    dm = mod.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= mod << (a.bit_length() - 1 - dm)
    return a


def gf2_gcd(a: int, b: int) -> int:
    while b:
        a, b = b, _gf2_mod(a, b)
    return a


def passes(q: int, n: int) -> bool:
    """Whether μ_q holds some ζ != 1 with 1 + ζ in μ_N, N = n: whether gcd(x^q + 1,
    (x + 1)^N + 1) is nontrivial over GF(2) (q odd). A common root ζ of the two is a q-th root
    of unity with (1 + ζ)^N = 1, and ζ = 1 is not one ((1 + 1)^N + 1 = 1). (x + 1)^N is
    reduced mod x^q + 1 first, which keeps the gcd."""
    mod = (1 << q) | 1
    power, base, e = 1, _gf2_mod(0b11, mod), n
    while e:
        if e & 1:
            power = _gf2_mulmod(power, base, mod)
        base = _gf2_mulmod(base, base, mod)
        e >>= 1
    return gf2_gcd(mod, power ^ 1).bit_length() > 1


def criterion(ell: int, m: int) -> bool:
    """Result 1 (proved): the family has a code with k > 0 on l x m exactly when μ_m' has some
    ζ != 1 with 1 + ζ in μ_N and μ_l' has some ξ != 1 with 1 + ξ in μ_N. l' = 1 or m' = 1 fails
    (μ_1 has no element but 1): the power-of-2 lemma."""
    lo, mo = odd(ell), odd(m)
    n = math.lcm(lo, mo)
    return passes(mo, n) and passes(lo, n)


def admissible(p: int, q: int) -> bool:
    """A character type (p, q) is admissible (docs/code-census.md, Structure: it can be a common
    zero of some code of the form) when it passes criterion 1's test with p and q in place of l'
    and m': ζ = β^(c-b) lies in μ_q, 1 + ζ = α^a β^-b in μ_lcm(p, q), and likewise for B."""
    n = math.lcm(p, q)
    return p > 1 and q > 1 and passes(q, n) and passes(p, n)


def order_of_two(n: int) -> int:
    """The multiplicative order of 2 mod n (n odd; 1 for n = 1)."""
    if n == 1:
        return 1
    e, x = 1, 2 % n
    while x != 1:
        x = (2 * x) % n
        e += 1
    return e


def orbit_size(p: int, q: int) -> int:
    """The size of the Frobenius orbit (χ -> χ^2) of a character of type (p, q): the order of 2
    mod the character's order lcm(p, q)."""
    return order_of_two(math.lcm(p, q))


def divisors(n: int) -> list[int]:
    return [d for d in range(1, n + 1) if n % d == 0]


def types(ell: int, m: int) -> list[tuple[int, int]]:
    """The character types (p, q) of the odd part with p > 1 and q > 1 (p | l', q | m')."""
    return [(p, q) for p in divisors(odd(ell)) for q in divisors(odd(m)) if p > 1 and q > 1]


def admissible_types(ell: int, m: int) -> list[tuple[int, int]]:
    return [t for t in types(ell, m) if admissible(*t)]


# ---------------------------------------------------------------- stage-1 look-ups


@functools.cache
def _stage1() -> str:
    s = json.loads(SUMMARY.read_text())
    return json.dumps(
        {f"{t['l']}x{t['m']}": sorted(int(k) for k in t["classes_by_k"]) for t in s["tori"]}
    )


def stage1_ksets() -> dict[tuple[int, int], list[int]]:
    """Each stage-1 torus's k-set (the k > 0 of its classes, summary.json's classes_by_k): the
    116 tori with files, [] where the family has no code with k > 0."""
    return {tuple(map(int, key.split("x"))): ks for key, ks in json.loads(_stage1()).items()}


def stage1_kset(ell: int, m: int) -> list[int] | None:
    """The stage-1 k-set of l x m in either orientation, None if it is not a stage-1 torus with
    a file."""
    return stage1_ksets().get((min(ell, m), max(ell, m)))


def stage1_best(ell: int, m: int) -> dict | None:
    """A stage-1 torus's best class by k d^2 (its least index among ties), from its data file
    (../qec-census/data/LxM.jsonl, the search's exact d of every class): class, k, d and
    score = k d^2. None where the torus has no class (or no file)."""
    path = CENSUS / "data" / f"{ell}x{m}.jsonl"
    if not path.is_file():
        return None
    best = None
    for line in path.read_text().splitlines()[1:]:
        r = json.loads(line)
        d = r["search"]["d"]
        if r["search"]["status"] != "complete" or d is None:
            raise RuntimeError(f"{ell}x{m} class {r['class']}: no exact d in stage 1")
        score = r["k"] * d * d
        if best is None or score > best["score"]:
            best = {"class": r["class"], "k": r["k"], "d": d, "score": score}
    return best


def stage1_at(n: int) -> dict[str, dict]:
    """The stage-1 tori with codes at n = 2lm, each with its best class (stage1_best) and its
    kind ("three" where 3 | l and 3 | m, else "other"). The largest score over them must be
    summary.json's frontier best at n, which is checked."""
    out = {}
    for (ell, m), ks in sorted(stage1_ksets().items()):
        if 2 * ell * m == n and ks:
            best = stage1_best(ell, m)
            kind = "three" if ell % 3 == 0 and m % 3 == 0 else "other"
            out[f"{ell}x{m}"] = {**best, "kind": kind}
    frontier = {f["n"]: f for f in json.loads(SUMMARY.read_text())["frontier"]}
    if out:
        top = frontier[n]["best"][0]
        if max(v["score"] for v in out.values()) != top["k"] * top["d"] ** 2:
            raise RuntimeError(f"stage-1 bests at n = {n} disagree with summary.json")
    return out


# ---------------------------------------------------------------- k: the per-torus predictions


def min_k(ell: int, m: int) -> int | None:
    """Result 5 (the bound proved, equality a pattern, 35 of 35): twice the smallest Frobenius
    orbit among the admissible character types; None where none is admissible."""
    sizes = [orbit_size(*t) for t in admissible_types(ell, m)]
    return 2 * min(sizes) if sizes else None


def max_k(ell: int, m: int) -> dict:
    """Results 2 and 3 (proved): max k = 2^(s+t) M(l', m'), M the odd torus's max k, and
    k <= 8lm/9 for every code, with equality when 3 | l and 3 | m. `value` is the predicted max
    k where a rule fixes it: 0 where criterion 1 fails; 2^(s+t) M with M from stage 1 where
    l' x m' (either orientation) is a stage-1 torus ("lookup"); 8lm/9 where 3 | l and 3 | m
    ("8lm/9"; both rules, where both apply, must agree, which the tests check on stage 1).
    Otherwise `value` is None ("open"): the registered prediction is then only the bound and
    the structure, `multiple` = 2^(s+t) (max k is 2^(s+t) times an even M, so a multiple of
    2^(s+t+1)), and `odd_torus`, l' x m', whose max k this run computes when it is held out."""
    (s2, lo), (t2, mo) = two_part(ell), two_part(m)
    bound = 8 * ell * m // 9  # an upper bound (k <= 8lm/9 and k is an integer)
    out = {"bound": bound, "multiple": s2 * t2, "odd_torus": [min(lo, mo), max(lo, mo)]}
    if not criterion(ell, m):
        return {**out, "value": 0, "rule": "criterion 1 fails"}
    values = {}
    kset = stage1_kset(lo, mo)
    if kset is not None:
        values["lookup"] = s2 * t2 * (max(kset) if kset else 0)
    if ell % 3 == 0 and m % 3 == 0:
        values["8lm/9"] = 8 * ell * m // 9
    if not values:
        return {**out, "value": None, "rule": "open"}
    if len(set(values.values())) != 1:
        raise RuntimeError(f"the max-k rules disagree at {ell}x{m}: {values}")
    return {**out, "value": next(iter(values.values())), "rule": ", ".join(sorted(values))}


def lifted_kset(kset, ell: int, m: int) -> list[int]:
    """Result 4: the k values of a torus with exactly one even side, from those of its odd torus
    l' x m': each times 2^j for j = 0, ..., s + t."""
    e = v2(ell) + v2(m)
    return sorted({k << j for k in kset for j in range(e + 1)})


def kset_rule(ell: int, m: int) -> dict:
    """Result 4 (proved) as a prediction: on a torus with exactly one even side, the k-set is the
    odd torus's times 2^j, j = 0..s+t. `source` says where the odd torus's k-set comes from:
    "stage 1" (with `kset`, the predicted set), "this run" (the odd torus is held out too; decide
    reads its k-set from its record), or "not tested" (neither). None where not exactly one side
    is even or criterion 1 fails (no codes: H1 covers it)."""
    if (ell % 2 == 0) == (m % 2 == 0) or not criterion(ell, m):
        return None
    lo, mo = odd(ell), odd(m)
    odd_torus = (min(lo, mo), max(lo, mo))
    base = stage1_kset(*odd_torus)
    if base is not None:
        return {
            "odd_torus": list(odd_torus),
            "source": "stage 1",
            "kset": lifted_kset(base, ell, m),
        }
    if odd_torus in set(held_out()):
        return {"odd_torus": list(odd_torus), "source": "this run", "kset": None}
    return {"odd_torus": list(odd_torus), "source": "not tested", "kset": None}


# ---------------------------------------------------------------- the linear law (H7)


def forced_types(ell: int, m: int) -> list[dict]:
    """The instances of docs/code-census.md's linear distance law on l x m (Patterns; result 9
    for the forced form): on 3 x m every admissible type (3, q) with q | m', q > 1 and 3 not
    dividing q; on 5 x m and 7 x m the type (l, 3), if 3 | m' and it is admissible. Each with
    its value 2m/q, and whether m/q is odd (then d <= 2m/q is proved, result 9)."""
    out = []
    if ell == 3:
        for q in divisors(odd(m)):
            if q > 1 and q % 3 and admissible(3, q):
                out.append({"type": [3, q], "value": 2 * m // q, "odd": (m // q) % 2 == 1})
    elif ell in (5, 7) and odd(m) % 3 == 0 and admissible(ell, 3):
        out.append({"type": [ell, 3], "value": 2 * m // 3, "odd": (m // 3) % 2 == 1})
    return out


def type_is_class_invariant(ell: int, m: int) -> bool:
    """Whether every class's common zeros have the same types at every one of its codes, so
    that "a class with a zero of type (p, q)" does not depend on the representative: true when
    gcd(l, m) = 1, since the automorphisms of Z_l x Z_m are then x -> x^u, y -> y^v, which keep
    each character's (ord α, ord β), and monomial factors and swapping A and B keep the common
    zeros. Otherwise an automorphism can mix the factors (on 3 x 15, x -> x, y -> xy turns a
    zero of type (3, 5) into one of type (3, 15)), and the census's classes do mix them: on the
    stage-1 tori 3x15, 5x15 and 3x30, 5, 1 and 44 classes have codes with a zero of the law's
    type, (3, 5) or (5, 3), while their representatives have none (development, on those tori)."""
    return math.gcd(ell, m) == 1


def frontier_torus(ell: int, m: int) -> bool:
    """Whether l x m is one of H8's tori: 3 | l, 3 | m and lm >= 27 (docs/code-census.md,
    Patterns, "The best codes reduce to one small code")."""
    return ell % 3 == 0 and m % 3 == 0 and ell * m >= 27


# ---------------------------------------------------------------- characters and zeros


def character_order(j: int, k: int, ell: int, m: int) -> tuple[int, int]:
    """The type (ord α, ord β) of the character (j, k)."""
    lo, mo = odd(ell), odd(m)
    return lo // math.gcd(j, lo), mo // math.gcd(k, mo)


def zero_types(zeros, ell: int, m: int) -> dict[tuple[int, int], int]:
    """The number of common zeros of each type; `zeros` as (j, k) or (j, k, term)."""
    return dict(sorted(Counter(character_order(z[0], z[1], ell, m) for z in zeros).items()))


def has_type(zeros, p: int, q: int, ell: int, m: int) -> bool:
    return (p, q) in zero_types(zeros, ell, m)


def chi_exponent(j: int, k: int, g, ell: int, m: int) -> int:
    """e with χ(g) = ζ^e, for g = (g0, g1) in Z_l x Z_m (χ(x) = α, χ(y) = β; α has odd order
    dividing l, so α^g0 is well defined for g0 mod l)."""
    lo, mo = odd(ell), odd(m)
    n = math.lcm(lo, mo)
    return (j * (n // lo) * g[0] + k * (n // mo) * g[1]) % n


# ---------------------------------------------------------------- polynomials as sets


def monomials(poly, ell: int, m: int) -> frozenset:
    """The monomials of a GF(2) polynomial on the torus, repeats cancelling in pairs."""
    count = Counter((p % ell, q % m) for p, q in poly)
    return frozenset(t for t, c in count.items() if c % 2)


def _shift(points, g, ell: int, m: int) -> frozenset:
    return frozenset(((p + g[0]) % ell, (q + g[1]) % m) for p, q in points)


def translate_of(P: frozenset, Q: frozenset, ell: int, m: int):
    """Some g with Q = P + g, or None."""
    if len(P) != len(Q) or not P:
        return None
    p0 = min(P)
    for q in sorted(Q):
        g = ((q[0] - p0[0]) % ell, (q[1] - p0[1]) % m)
        if _shift(P, g, ell, m) == Q:
            return g
    return None


def stabilizer(P: frozenset, ell: int, m: int) -> list[tuple[int, int]]:
    """The nonzero translations g with P + g = P."""
    if not P:
        return []
    p0 = min(P)
    out = []
    for q in sorted(P):
        g = ((q[0] - p0[0]) % ell, (q[1] - p0[1]) % m)
        if g != (0, 0) and _shift(P, g, ell, m) == P:
            out.append(g)
    return out


# ---------------------------------------------------------------- result 7: when d = 2


def condition_i(A, B, ell: int, m: int) -> bool:
    """Result 7 (i): B is a translate of A."""
    return translate_of(monomials(A, ell, m), monomials(B, ell, m), ell, m) is not None


def condition_ii(A, B, zeros, ell: int, m: int) -> bool:
    """Result 7 (ii): a nonzero translation g fixes A or B, and χ(g) != 1 at some common
    zero χ."""
    for P in (A, B):
        for g in stabilizer(monomials(P, ell, m), ell, m):
            if any(chi_exponent(z[0], z[1], g, ell, m) for z in zeros):
                return True
    return False


# ---------------------------------------------------------------- result 8: the quotient bound


@functools.cache
def odd_subgroups(ell: int, m: int) -> tuple:
    """Every subgroup H of Z_l x Z_m of odd order, as a sorted tuple of its elements, the
    smallest first (the trivial subgroup first). They are the subgroups of the odd part
    {(2^s u, 2^t v)} = Z_l' x Z_m', enumerated as the lattices L with l'Z x m'Z <= L <= Z^2 in
    Hermite normal form, rows (d1, x) and (0, d2) with d1 | l', d2 | m', 0 <= x < d2 and
    (l', l' x / d1) in L."""
    (s2, lo), (t2, mo) = two_part(ell), two_part(m)
    out = set()
    for d1 in divisors(lo):
        for d2 in divisors(mo):
            for x in range(d2):
                if ((lo // d1) * x) % d2:
                    continue
                elements = {
                    ((i * d1) % lo, (i * x + j * d2) % mo)
                    for i in range(lo // d1)
                    for j in range(mo // d2)
                }
                out.add(tuple(sorted(((s2 * u) % ell, (t2 * v) % m) for u, v in elements)))
    return tuple(sorted(out, key=lambda h: (len(h), h)))


def _coset(g, H, ell: int, m: int) -> tuple[int, int]:
    """The least element of g + H."""
    return min(((g[0] + h[0]) % ell, (g[1] + h[1]) % m) for h in H)


def _image(P: frozenset, H, ell: int, m: int) -> frozenset:
    """P's image in GF(2)[G/H], as least coset elements (cosets hit an even number of times
    cancel)."""
    count = Counter(_coset(t, H, ell, m) for t in P)
    return frozenset(t for t, c in count.items() if c % 2)


def _qshift(points, g, H, ell: int, m: int) -> frozenset:
    return frozenset(_coset(((p + g[0]) % ell, (q + g[1]) % m), H, ell, m) for p, q in points)


def _index(t, ell: int, m: int, block: int) -> int:
    return block * ell * m + t[0] * m + t[1]


def quotient_bound(A, B, zeros, ell: int, m: int) -> dict | None:
    """Result 8 (proved): the least 2|H| over the subgroups H of odd order (the trivial one
    included, which is result 7's "if" direction) and the forms below, with an explicit
    logical of that weight; None if no form applies. Over G/H, with Ā and B̄ the images:
      "B": a translation ḡ != 0 fixes B̄, and some common zero χ is trivial on H with
           χ(g) != 1; the logical is (0, (1 + g) Σ_H);
      "A": the same with A; the logical is ((1 + g) Σ_H, 0);
      "translate": B̄ = ḡ Ā, and some common zero is trivial on H; the logical is
           (g Σ_H, Σ_H).
    Each is in ker H_X (B̄ + ḡ B̄ = 0, or ḡ Ā + B̄ = 0, over G/H), has weight 2|H| (g not in H
    for the first two), and is not in the rowspace of H_Z: its block at the B side (A side) has,
    at χ, a residue (1 + χ(g)) [χ trivial on H] (or 1), nonzero, while H_Z's rows (B w, A w)
    have residues in the maximal ideal at a common zero. Returns bound (2|H|), order (|H|), form,
    g, and the logical's support (qubit indices, left block then right, i m + j). The subgroups
    are tried smallest first, then the forms in the order above, then g in sorted order."""
    mons = (monomials(A, ell, m), monomials(B, ell, m))
    for H in odd_subgroups(ell, m):
        on_h = [z for z in zeros if all(chi_exponent(z[0], z[1], h, ell, m) == 0 for h in H)]
        if not on_h:
            continue
        abar, bbar = (_image(P, H, ell, m) for P in mons)
        for form, P in (("B", bbar), ("A", abar)):
            if not P:
                continue
            p0 = min(P)
            for q in sorted(P):
                g = ((q[0] - p0[0]) % ell, (q[1] - p0[1]) % m)
                if _coset(g, H, ell, m) == _coset((0, 0), H, ell, m):
                    continue
                if _qshift(P, g, H, ell, m) != P:
                    continue
                if not any(chi_exponent(z[0], z[1], g, ell, m) for z in on_h):
                    continue
                block = 1 if form == "B" else 0
                support = sorted(
                    {_index(h, ell, m, block) for h in H}
                    | {_index(((h[0] + g[0]) % ell, (h[1] + g[1]) % m), ell, m, block) for h in H}
                )
                return {
                    "bound": 2 * len(H),
                    "order": len(H),
                    "form": form,
                    "g": list(g),
                    "support": support,
                }
        if abar and len(abar) == len(bbar):
            a0 = min(abar)
            for b in sorted(bbar):
                g = ((b[0] - a0[0]) % ell, (b[1] - a0[1]) % m)
                if _qshift(abar, g, H, ell, m) == bbar:
                    support = sorted(
                        {_index(((h[0] + g[0]) % ell, (h[1] + g[1]) % m), ell, m, 0) for h in H}
                        | {_index(h, ell, m, 1) for h in H}
                    )
                    return {
                        "bound": 2 * len(H),
                        "order": len(H),
                        "form": "translate",
                        "g": list(g),
                        "support": support,
                    }
    return None


# ---------------------------------------------------------------- result 9: the forced form


def forced_bounds(A, B, zeros, ell: int, m: int) -> list[dict]:
    """Result 9: on l = 3, a common zero of type (3, q) with 3 not dividing q forces
    B = y^d + x + x^2 with q | d, and (0, (1 + x) Σ_H), H = <y^q> of order m/q, is in ker H_X;
    on l = 5 or 7, a zero of type (l, 3) forces A = 1 + y^b + y^c with {b, c} = {1, 2} mod 3, and
    ((1 + y) Σ_H, 0), H = <y^3>, is. Each such type with its value 2m/q, whether m/q is odd (then
    the vector is a logical, so d <= 2m/q is proved; with m/q even it may or may not be, and the
    job checks it with verify_witness), and the vector's support."""
    out = []
    found = zero_types(zeros, ell, m)
    if ell == 3:
        wanted = [(3, q) for _, q in found if q > 1 and q % 3 and (3, q) in found]
    elif ell in (5, 7):
        wanted = [(ell, 3)] if (ell, 3) in found else []
    else:
        wanted = []
    for p, q in sorted(set(wanted)):
        H = [(0, (q * i) % m) for i in range(m // q)]
        if ell == 3:  # (0, (1 + x) Σ_H)
            support = sorted(
                {_index(h, ell, m, 1) for h in H} | {_index((1, h[1]), ell, m, 1) for h in H}
            )
        else:  # ((1 + y) Σ_H, 0)
            support = sorted(
                {_index(h, ell, m, 0) for h in H}
                | {_index((0, (h[1] + 1) % m), ell, m, 0) for h in H}
            )
        out.append(
            {"type": [p, q], "value": 2 * m // q, "proved": (m // q) % 2 == 1, "support": support}
        )
    return out


# ---------------------------------------------------------------- H8: the [[18,8,2]] base


def reduces_to_base(A, B, ell: int, m: int) -> bool:
    """Whether the code reduces mod (3, 3) to the [[18,8,2]] base, A = 1 + y + y^2,
    B = 1 + x + x^2 (docs/code-census.md, Patterns): A's three monomials reduce to three distinct
    points of F_3^2 on a line (three distinct points are collinear exactly when they sum to 0),
    and so do B's, on a line of another direction. An automorphism of Z_3^2 carries the two
    directions to (0, 1) and (1, 0), and translations fix the lines, so the reduction is then
    equivalent to the base; conversely an equivalent code has that form. Requires 3 | l and
    3 | m."""
    if ell % 3 or m % 3:
        raise ValueError(f"{ell}x{m}: the reduction mod (3, 3) needs 3 | l and 3 | m")

    def line(poly):
        pts = [(p % 3, q % 3) for p, q in poly]
        if len(pts) != 3 or len(set(pts)) != 3:
            return None
        if sum(p for p, _ in pts) % 3 or sum(q for _, q in pts) % 3:
            return None
        d = ((pts[1][0] - pts[0][0]) % 3, (pts[1][1] - pts[0][1]) % 3)
        return min(d, ((-d[0]) % 3, (-d[1]) % 3))

    a, b = line(monomials(A, ell, m)), line(monomials(B, ell, m))
    return a is not None and b is not None and a != b
