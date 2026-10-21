"""Development codes for the independent check: allowed sizes only (guarded)."""
import json, random
import mydist as M

SIZES = [(1, 7), (1, 9), (2, 7), (4, 4), (2, 9), (1, 22), (2, 11), (2, 13), (3, 9), (4, 7), (5, 6),
         (4, 8), (3, 11), (3, 13), (4, 10), (6, 7), (4, 11), (6, 8), (7, 7), (5, 10), (7, 8),
         (6, 10), (8, 8), (7, 11), (8, 10), (9, 9), (7, 12), (7, 13), (8, 12), (10, 10)]

def draw(ell, m, rng, form):
    if form == "tri":
        a, e, f = rng.sample(range(ell), 3) if ell >= 3 else [rng.randrange(ell) for _ in range(3)]
        d, b, c = rng.sample(range(m), 3) if m >= 3 else [rng.randrange(m) for _ in range(3)]
        return [(a, 0), (0, b), (0, c)], [(0, d), (e, 0), (f, 0)]
    if form == "gen":
        return ([(rng.randrange(ell), rng.randrange(m)) for _ in range(rng.choice([2, 3, 4, 3, 2]))],
                [(rng.randrange(ell), rng.randrange(m)) for _ in range(rng.choice([2, 3, 4, 3, 2]))])
    if form == "raw":  # unreduced exponents, repeats, cancellations
        return ([(rng.randrange(-ell, 2 * ell), rng.randrange(-m, 2 * m)) for _ in range(rng.randint(1, 6))],
                [(rng.randrange(-ell, 2 * ell), rng.randrange(-m, 2 * m)) for _ in range(rng.randint(1, 6))])

out = []
for ell, m in SIZES:
    rng = random.Random(f"checker-independent {ell}x{m}")
    got = {"tri": 0, "gen": 0, "raw": 0, "k0": 0}
    for _ in range(4000):
        form = rng.choice(["tri", "tri", "gen", "raw"])
        A, B = draw(ell, m, rng, form)
        if M.is_toric(A, B, ell, m):
            continue
        M.guard(A, B, ell, m)
        k = M.k_of(A, B, ell, m)
        if k == 0:
            if got["k0"] < 1:
                got["k0"] += 1
                out.append({"l": ell, "m": m, "A": A, "B": B, "k": k, "form": form})
            continue
        if got[form] < 2:
            got[form] += 1
            out.append({"l": ell, "m": m, "A": A, "B": B, "k": k, "form": form})
        if all(v >= (2 if f != "k0" else 1) for f, v in got.items()):
            break
    print(ell, m, got)
json.dump(out, open("devcodes.json", "w"))
print(len(out))
