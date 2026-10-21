"""Step 13. The registrable prediction list.  Each entry: a rule (with its construction, so anyone can rebuild the
exponent set with famlib / step12_evenreps), a size m, the predicted odd part of the period, the tier of the
reasoning, and whether it was computed here.  Only entries with compute=True are evaluated (the 'handful');
the rest are held out.  Writes predictions.json (the list, with results for the computed ones)."""
import json, sys, time
import famlib as L
from step12_evenreps import build

P = []


def add(rule, m, pred, tier, why, compute=False, construct=None):
    if construct and construct['kind'] == 'hex':
        assert (construct['q'] ** 2 + 3 * construct['p'] ** 2) % m == 0, (rule, m)
    P.append(dict(rule=rule, m=m, predicted_odd_part=pred, tier=tier, reasoning=why, computed=compute,
                  construct=construct))


T0 = ('T0: consequence of the proved reduction theorem plus the finite verification at this size '
      '(classification by k = ind_2(p) mod e and parity, step 8); tests the proof and the arithmetic')
# m = 37, hexagon members with p > 20 (radius 40-70)
for p, q in ((23, 2), (21, 34), (22, 19), (24, 23), (25, 30), (26, 9), (27, 25), (29, 20), (31, 22), (33, 27), (36, 21), (38, 16)):
    chi = L.legendre(p, 37)
    add('f_{%d,%d}' % (p, q), 37, 29127 if chi == -1 else 87381, T0,
        'q = +-16p mod 37; chi_37(p) = %+d -> %s' % (chi, 'ninth-confined (NR twist class)' if chi == -1 else 'cube only (QR class)'),
        compute=(p, q) == (23, 2), construct=dict(kind='hex', p=p, q=q))
# m = 13, the cube-level analogue
for p, q in ((24, 38), (21, 35), (21, 22), (23, 31), (24, 25), (28, 38), (28, 27), (31, 33), (32, 34), (37, 33)):
    if (q * q + 3 * p * p) % 13:
        continue
    chi = L.legendre(p, 13)
    same = (p - q) % 2 == 0
    add('f_{%d,%d}' % (p, q), 13, 21 if (chi == -1 and same) else 63, T0,
        'q = +-6p mod 13; chi_13(p) = %+d, %s parity -> %s' % (chi, 'same' if same else 'opposite',
                                                                'cube-confined' if chi == -1 and same else 'generic'),
        compute=(p, q) == (24, 38), construct=dict(kind='hex', p=p, q=q))
T1 = ('T1: other size; the 3-adic part follows from step 3 (the engine found no member of the family confined at '
      'this size), the non-3 part assumes the eigenvalue orders are otherwise generic (lcm = 2^e - 1)')
add('f_{2,7}  (61 = 7^2 + 3*2^2, the 4850 analogue)', 61, 2 ** 30 - 1, T1, 'symmetric field F(2^30); C fails at 1 of 5 T-orbits', True, dict(kind='hex', p=2, q=7))
add('f_{5,13}', 61, 2 ** 30 - 1, T1, 'another member at 61', False, dict(kind='hex', p=5, q=13))
add('f_{2,13} (181 = 13^2 + 12)', 181, 2 ** 90 - 1, T1, 'symmetric field F(2^90); 15 free T-orbits, 6 satisfy C(1)', False, dict(kind='hex', p=2, q=13))
add('f_{6,1}  (109 = 1 + 3*6^2)', 109, 2 ** 18 - 1, T1, 'same field as 37 (F(2^18)), 2 of index 3 mod 109', False, dict(kind='hex', p=6, q=1))
add('f_{4,7}  (97 = 7^2 + 3*4^2)', 97, 2 ** 24 - 1, T1, 'symmetric field F(2^24)', False, dict(kind='hex', p=4, q=7))
add('f_{8,1}  (193 = 1 + 3*8^2)', 193, 2 ** 48 - 1, T1, 'symmetric field F(2^48)', False, dict(kind='hex', p=8, q=1))
add('f_{1,21} (q = 21 p mod 111 = 3*37)', 111, 2 ** 36 - 1, T1, 'reduces to a QR member at 37; mixed characters (F(2^36)) unconfined', True, dict(kind='hex', p=1, q=21))
add('f_{2,69} (q = 21*2*... mod 111; NR mod 37)', 111, 2 ** 36 - 1, T1, 'NR member at 37 (its 37-part is ninth-confined) but mixed characters unconfined', False, dict(kind='hex', p=2, q=69))
T2 = ('T2: held-out size, not run through the engine; heuristic from step 6b (no mechanism beyond 13 and 37): mixed '
      'characters of a multiple of 37 behave generically')
add('f_{19,29} (q = 201 p mod 481 = 13*37; NR mod 13 and mod 37, same parity)', 481, 2 ** 18 - 1, T2,
    '2^18 = -1 mod 481 so symmetric values lie in F(2^18); the 13- and 37-subtori are confined (21, 29127) but the mixed characters are not',
    False, dict(kind='hex', p=19, q=29))
add('f_{23,35} (q = 243 p mod 703 = 19*37; NR mod 37, same parity)', 703, 2 ** 36 - 1, T2,
    '-1 not in <2> mod 703: symmetric values in F(2^36); 37-subtorus ninth-confined, mixed characters generic', False, dict(kind='hex', p=23, q=35))
T3 = ('T3: two-orbit numerators at 37 (step 9 found W(c) + W_3(7c) and W_3(2c) + W_6(5c) ninth-level relative to pi), '
      'diagonal removed by even representatives (step 12); the twist rule A -> A s multiplies the 3-adic log by 2^ind(s)')
for A in (3, 4, 7, 9, 10, 11, 12, 16):
    add('even-rep (hex(%d) + L3(%d))/s' % (A, 7 * A % 37), 37, 29127, T3, 'A = %d is a QR mod 37 -> ninth' % A, False,
        dict(kind='even_sum', parts=[(A, A), (7 * A % 37, 21 * A % 37)]))
for A in (2, 5):
    add('even-rep (hex(%d) + L3(%d))/s' % (A, 7 * A % 37), 37, 87381, T3, 'A = %d is a NR mod 37 -> cube only' % A, False,
        dict(kind='even_sum', parts=[(A, A), (7 * A % 37, 21 * A % 37)]))
add('even-rep (L3(2) + L6(5))/s', 37, 29127, T3, 'computed in step 12', True, dict(kind='even_sum', parts=[(2, 6), (5, 30)]))
add('even-rep (hex(1) + L3(7))/s', 37, 29127, T3, 'computed in step 12', True, dict(kind='even_sum', parts=[(1, 1), (7, 21)]))
T4 = ('T4: the closest analogues of 37 (prime, 2 primitive, m = 13 mod 24, rule 90 cube-confined, 9 | 2^e - 1), not '
      'computed: no hexagon-family member is confined.  Registered quantity: the 3-part of the odd part of f_{2,q} '
      '(q^2 = -12 mod m) equals the 3-part of 2^e - 1 (exact odd part conjectured to be 2^e - 1)')
import sympy
for m in (709, 757, 829, 877, 1213, 1861):
    q = min(x for x in range(1, m) if (x * x + 12) % m == 0)
    e = (m - 1) // 2
    add('f_{2,%d}' % q, m, '2^%d - 1 (3-part 3^%d)' % (e, sympy.multiplicity(3, 2 ** e - 1)), T4,
        'rule 90 level %s at %d; ~%d independent T-orbit conditions' % ('>=1', m, (m - 1) // 12), False, dict(kind='hex', p=2, q=q))

if __name__ == '__main__':
    for x in P:
        if not x['computed']:
            continue
        c = x['construct']
        t0 = time.time()
        f = L.hex_rule(c['p'], c['q']) if c['kind'] == 'hex' else build([tuple(t) for t in c['parts']], x['m'], {37: 16}[x['m']])
        op = L.odd_part(f, x['m'])
        x['result'] = op
        x['agrees'] = op == x['predicted_odd_part']
        x['terms'] = len(f)
        print(x['rule'], 'm =', x['m'], 'predicted', x['predicted_odd_part'], 'computed', op, 'agree', x['agrees'],
              '(%.0f s)' % (time.time() - t0), flush=True)
    json.dump(P, open('predictions.json', 'w'), indent=1)
    print(len(P), 'predictions,', sum(x['computed'] for x in P), 'computed')
