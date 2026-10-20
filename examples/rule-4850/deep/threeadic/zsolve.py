"""Solvability of A x = b over Z/p^k (Smith-form elimination with valuation pivoting)."""
import numpy as np


def _val(a, p, k):
    a %= p**k
    if a == 0:
        return k
    v = 0
    while a % p == 0:
        a //= p
        v += 1
    return v


def solvable(A, b, p, k):
    """True iff A x = b has a solution mod p^k.  A: (r, c) ints, b: (r,) ints."""
    q = p**k
    A = np.array(A, dtype=np.int64) % q
    b = np.array(b, dtype=np.int64) % q
    r, c = A.shape
    if c == 0:
        return bool(np.all(b == 0))
    row = 0
    for col in range(min(r, c)):
        # pivot of minimal valuation in the submatrix A[row:, col:]
        best = None
        for i in range(row, r):
            for j in range(col, c):
                if A[i, j]:
                    v = _val(int(A[i, j]), p, k)
                    if best is None or v < best[0]:
                        best = (v, i, j)
                        if v == 0:
                            break
            if best is not None and best[0] == 0:
                break
        if best is None:
            break
        v, i, j = best
        A[[row, i]] = A[[i, row]]
        b[[row, i]] = b[[i, row]]
        A[:, [col, j]] = A[:, [j, col]]
        piv = int(A[row, col])
        unit = piv // p**v
        uinv = pow(unit, -1, q)
        # eliminate below/above in column (row operations, also on b)
        for i2 in range(r):
            if i2 != row and A[i2, col]:
                f = (int(A[i2, col]) // p**v) * uinv % q
                A[i2] = (A[i2] - f * A[row]) % q
                b[i2] = (b[i2] - f * b[row]) % q
        # eliminate in row (column operations: do not touch b)
        for j2 in range(c):
            if j2 != col and A[row, j2]:
                f = (int(A[row, j2]) // p**v) * uinv % q
                A[:, j2] = (A[:, j2] - f * A[:, col]) % q
        row += 1
    # now A is diagonal on the first `row` rows
    for i in range(r):
        if i < row:
            v = _val(int(A[i, i]), p, k)
            if _val(int(b[i]), p, k) < v:
                return False
        else:
            if b[i] % q:
                return False
    return True


if __name__ == "__main__":
    import itertools
    rng = np.random.default_rng(0)
    # brute-force cross-check on small random systems mod 9
    for trial in range(300):
        r, c = rng.integers(1, 5), rng.integers(1, 4)
        A = rng.integers(0, 9, (r, c)) * rng.integers(0, 2, (r, c)) * 3 ** rng.integers(0, 2, (r, c))
        b = rng.integers(0, 9, r) * 3 ** rng.integers(0, 2, r)
        brute = any(np.all((A @ np.array(x) - b) % 9 == 0) for x in itertools.product(range(9), repeat=c))
        assert brute == solvable(A, b, 3, 2), (A, b)
    print("zsolve: 300 random systems mod 9 agree with brute force")
