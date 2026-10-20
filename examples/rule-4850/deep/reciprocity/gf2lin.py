"""Small dense GF(2) linear algebra (numpy uint8): kernel of a matrix (columns = unknowns)."""
import numpy as np

def kernel(A):
    """basis of {x : A x = 0} over GF(2); A is (rows, cols) uint8"""
    A = (A % 2).astype(np.uint8).copy()
    rows, cols = A.shape
    piv_cols = []
    r = 0
    for c in range(cols):
        if r >= rows:
            break
        nz = np.flatnonzero(A[r:, c])
        if len(nz) == 0:
            continue
        p = r + nz[0]
        if p != r:
            A[[r, p]] = A[[p, r]]
        mask = A[:, c].astype(bool)
        mask[r] = False
        A[mask] ^= A[r]
        piv_cols.append(c)
        r += 1
    free = [c for c in range(cols) if c not in set(piv_cols)]
    basis = []
    for f in free:
        x = np.zeros(cols, dtype=np.uint8)
        x[f] = 1
        for i, pc in enumerate(piv_cols):
            if A[i, f]:
                x[pc] = 1
        basis.append(x)
    return basis
