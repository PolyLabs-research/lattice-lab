"""10491524 = pi^3 + Y^2, Y = s(1 + s e), s = a+b, pi = ab, e = (1+a)(1+b).  3-parts of the pieces."""
import collections
import ff18 as F
T = F.tvec()
cnt = collections.Counter()
ok = True
for j in range(1, 19):
    for k in range(1, 19):
        a, b = T[j], T[k]
        s = a ^ b; p = F.mul(a, b); e = F.mul(1 ^ a, 1 ^ b)
        Y = F.mul(s, 1 ^ F.mul(s, e))
        val = F.pw(p, 3) ^ F.mul(Y, Y)
        assert val == F.rule_value(10491524, 6, j, k)
        if Y == 0:
            cnt['Y=0'] += 1; continue
        W = F.mul(F.mul(Y, Y), F.inv(F.pw(p, 3)))
        cnt[('v27 Y mod 9', F.v27(Y) % 9, 'v27(1+W) mod 9', F.v27(1 ^ W) % 9)] += 1
print('identity F\' = pi^3 + Y^2 verified on all (j,k), j,k in 1..18')
for k, v in sorted(cnt.items(), key=str):
    print(k, v)
