"""Own GF(2) check of the published [[360,12]] BB code: k, connectivity, group, stored witness."""
import json, math
import numpy as np

l, m = 30, 6
A = [(9, 0), (0, 1), (0, 2)]          # x^9 + y + y^2
B = [(0, 3), (25, 0), (26, 0)]        # y^3 + x^25 + x^26
N = l * m


def mat(P):
    M = np.zeros((N, N), dtype=np.uint8)
    for i in range(l):
        for j in range(m):
            r = i * m + j
            for (a, b) in P:
                M[r, ((i + a) % l) * m + (j + b) % m] ^= 1
    return M


def rank2(M):
    M = M.copy() % 2
    r = 0
    rows, cols = M.shape
    for c in range(cols):
        p = np.nonzero(M[r:, c])[0]
        if len(p) == 0:
            continue
        p = p[0] + r
        M[[r, p]] = M[[p, r]]
        nz = np.nonzero(M[:, c])[0]
        nz = nz[nz != r]
        M[nz] ^= M[r]
        r += 1
        if r == rows:
            break
    return r


Am, Bm = mat(A), mat(B)
HX = np.hstack([Am, Bm])
HZ = np.hstack([Bm.T, Am.T])
assert not ((HX.astype(int) @ HZ.T.astype(int)) % 2).any(), "HX HZ^T != 0"
rX, rZ = rank2(HX), rank2(HZ)
k = 2 * N - rX - rZ
print("n =", 2 * N, "rank HX =", rX, "rank HZ =", rZ, "k =", k)

# connectivity: differences within A and within B generate Z_l x Z_m
steps = {((p[0] - q[0]) % l, (p[1] - q[1]) % m) for P in (A, B) for p in P for q in P}
reach = {(0, 0)}; fr = [(0, 0)]
while fr:
    x = fr.pop()
    for g in steps:
        y = ((x[0] + g[0]) % l, (x[1] + g[1]) % m)
        if y not in reach:
            reach.add(y); fr.append(y)
print("connected:", len(reach) == N, "| group: Z%d x Z%d" % (math.gcd(l, m), l * m // math.gcd(l, m)))
print("score k d^2/n at d=24:", k * 24 ** 2 / (2 * N))

# stored witness from examples/qec-open-distance/records.jsonl (window job, kind Z)
w = None
for line in open("/home/user/lattice-lab/examples/qec-open-distance/records.jsonl"):
    r = json.loads(line)
    if r.get("code") == "360" and r.get("job") == "window" and r.get("witness"):
        w = r["witness"]; break
v = np.zeros(2 * N, dtype=np.uint8); v[w] = 1
print("witness weight:", int(v.sum()))
for name, H, G in (("ker HX, not in rowspace HZ", HX, HZ), ("ker HZ, not in rowspace HX", HZ, HX)):
    in_ker = not ((H.astype(int) @ v) % 2).any()
    nontriv = rank2(np.vstack([G, v])) > rank2(G)
    print(f"  {name}: in kernel={in_ker}, outside stabiliser space={nontriv}")

# try the other index conventions (y-major index, transposed blocks)
def mat2(P, idx):
    M = np.zeros((N, N), dtype=np.uint8)
    for i in range(l):
        for j in range(m):
            for (a, b) in P:
                M[idx(i, j), idx((i + a) % l, (j + b) % m)] ^= 1
    return M
for iname, idx in (("i*m+j", lambda i, j: i * m + j), ("j*l+i", lambda i, j: j * l + i)):
    for tname, T in (("M", lambda M: M), ("M^T", lambda M: M.T.copy())):
        Am2, Bm2 = T(mat2(A, idx)), T(mat2(B, idx))
        HX2 = np.hstack([Am2, Bm2]); HZ2 = np.hstack([Bm2.T, Am2.T])
        for name, H, G in (("ker HX", HX2, HZ2), ("ker HZ", HZ2, HX2)):
            in_ker = not ((H.astype(int) @ v) % 2).any()
            if in_ker:
                nontriv = rank2(np.vstack([G, v])) > rank2(G)
                print(f"  convention {iname}, {tname}: witness in {name}, nontrivial logical={nontriv}")
