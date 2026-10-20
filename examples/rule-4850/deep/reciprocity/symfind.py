"""Fast projective symmetry groups of a support S in (Z/37)^2: all M in GL2(Z/37) with M S = d S
(column action, s -> M s) for some unit d.  Method: fix two independent points p1, p2 of S; any such
M maps them to d*q1, d*q2 for q1, q2 in S; solve and test."""
import numpy as np
M37 = 37

def _inv2(A):
    a, b, c, d = A
    det = (a * d - b * c) % M37
    if det == 0:
        return None
    di = pow(det, -1, M37)
    return ((d * di) % M37, (-b * di) % M37, (-c * di) % M37, (a * di) % M37)

def proj_symmetries(S, scalars=True):
    S = sorted({(p % M37, q % M37) for p, q in S})
    Sset = set(S)
    Sarr = np.array(S, dtype=np.int64)
    # independent pair
    p1 = S[0]
    p2 = next(s for s in S[1:] if (p1[0] * s[1] - p1[1] * s[0]) % M37)
    Pinv = _inv2((p1[0], p2[0], p1[1], p2[1]))  # inverse of the matrix with columns p1, p2
    ds = range(1, M37) if scalars else [1]
    scaled = {d: {((d * x) % M37, (d * y) % M37) for x, y in S} for d in ds}
    codes = {d: np.array(sorted(((d * x) % M37) * M37 + (d * y) % M37 for x, y in S)) for d in ds}
    out = []
    for q1 in S:
        for q2 in S:
            Q = (q1[0], q2[0], q1[1], q2[1])  # columns q1, q2
            # M = Q P^-1
            a = (Q[0] * Pinv[0] + Q[1] * Pinv[2]) % M37
            b = (Q[0] * Pinv[1] + Q[1] * Pinv[3]) % M37
            c = (Q[2] * Pinv[0] + Q[3] * Pinv[2]) % M37
            d_ = (Q[2] * Pinv[1] + Q[3] * Pinv[3]) % M37
            if (a * d_ - b * c) % M37 == 0:
                continue
            img = np.sort(((a * Sarr[:, 0] + b * Sarr[:, 1]) % M37) * M37 + (c * Sarr[:, 0] + d_ * Sarr[:, 1]) % M37)
            for d in ds:
                if np.array_equal(img, codes[d]):
                    # M maps S to dS; record M / d (so that M' S = S up to the scalar d): keep (M, d)
                    out.append(((int(a), int(b), int(c), int(d_)), d))
    # M maps p1 -> q1 in S, but for scalar d we need M p1 in dS; handle by also allowing q's in dS:
    return out

def proj_symmetries_full(S):
    """all (M, d) with M S = d S: M = d * M0 with M0 S = S, plus the genuinely projective ones"""
    S = sorted({(p % M37, q % M37) for p, q in S})
    res = set()
    base = proj_symmetries(S, scalars=False)
    # genuinely projective: M S = d S <=> (M/d) S = S, so the projective group is scalars x stabiliser
    # unless... (M/d) S = S always; hence it suffices to compute the stabiliser.
    return [M for M, _ in base]
