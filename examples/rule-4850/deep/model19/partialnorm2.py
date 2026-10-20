"""Is N_x(lambda)(j, k) = prod_{h in {1,27,26}} lambda(h j, k) independent of j (exactly)?
Test on the relatives, on 4850 in its own frame, and on all ninth-power rules in the records."""
import json, random
import ff18 as F

H3 = [1, 27, 26]


def lamfun(n, r):
    cache = {}
    def f(j, k):
        key = (j % 37, k % 37)
        if key not in cache:
            cache[key] = F.rule_value(n, r, *key)
        return cache[key]
    return f


def partial_norm_profile(n, r, include_axis=True):
    L = lamfun(n, r)
    js = range(0 if include_axis else 1, 37)
    indep = True
    A = {}
    for k in range(1, 37):
        vals = set()
        for j in js:
            v = 1
            for h in H3:
                v = F.mul(v, L(h * j, k))
            vals.add(v)
        if len(vals) > 1:
            indep = False
        A[k] = vals
    return indep, A


if __name__ == '__main__':
    out = {}
    for n, r in [(10491524, 6), (20982139, 6), (178279803, 6), (4850, 4), (482758, 5), (8438150, 6), (43250486, 6)]:
        ind_all, A = partial_norm_profile(n, r, True)
        ind_off, A2 = partial_norm_profile(n, r, False)
        L = lamfun(n, r)
        cube_axis = all(A2[k] == {F.pw(L(0, k), 3)} for k in range(1, 37)) if ind_off else None
        out[n] = dict(j_independent_incl_axis=ind_all, j_independent_off_axis=ind_off, equals_axis_cubed=cube_axis)
        print(n, out[n])
    json.dump(out, open('partialnorm2.json', 'w'), indent=1)
