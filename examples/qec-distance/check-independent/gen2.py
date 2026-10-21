"""More development codes (weight-6): trinomials and 3+3 general monomials, k > 0, allowed sizes."""
import json, random
import mydist as M

SIZES = [(3, 9), (5, 6), (6, 7), (3, 13), (7, 7), (7, 8), (6, 10), (5, 12), (9, 9), (7, 12), (6, 14),
         (7, 13), (9, 11), (10, 10), (3, 11), (4, 10), (6, 8), (8, 10)]
out = []
for ell, m in SIZES:
    rng = random.Random(f"checker-independent w6 {ell}x{m}")
    got = {"tri": 0, "w3": 0}
    for _ in range(3000):
        form = rng.choice(["tri", "w3"])
        if form == "tri":
            a, e, f = rng.sample(range(ell), 3)
            d, b, c = rng.sample(range(m), 3)
            A, B = [(a, 0), (0, b), (0, c)], [(0, d), (e, 0), (f, 0)]
        else:
            cells = [(i, j) for i in range(ell) for j in range(m)]
            A, B = rng.sample(cells, 3), rng.sample(cells, 3)
        M.guard(A, B, ell, m)
        k = M.k_of(A, B, ell, m)
        if k and got[form] < 3:
            got[form] += 1
            out.append({"l": ell, "m": m, "A": A, "B": B, "k": k, "form": form})
        if min(got.values()) >= 3:
            break
    print(ell, m, got, flush=True)
json.dump(out, open("devcodes2.json", "w"))
print(len(out))
