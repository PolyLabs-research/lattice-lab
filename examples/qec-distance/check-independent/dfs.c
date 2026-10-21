/*
 * Check-driven exhaustive search for the least weight of a nontrivial codeword (independent
 * checker's scratch tool). Input on stdin:
 *   n r k ub a0 a1
 *   r lines: w q_1 .. q_w          (the supports of the rows of Hc)
 *   n lines: label words (k bits as one or two hex u64: lo hi)
 * For every anchor a in [a0, a1) it searches codewords c of Hc (H c = 0) with min(supp c) = a
 * and |c| < best, branching on the qubits of an unsatisfied check (the one with fewest options),
 * excluding earlier siblings, pruning by |S| + ceil(unsat / maxcol) >= best. A zero syndrome is a
 * leaf: recorded if its label (c . L_j bits) is nonzero. Prints: best, nodes, then the witness.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 1200
#define MAXR 640
#define WN ((MAXN + 63) / 64)
#define WR ((MAXR + 63) / 64)

static int n, r, k, best, maxcol, anchor;
static int rowsz[MAXR], rows[MAXR][64];
static uint64_t colmask[MAXN][WR];
static uint64_t lab_lo[MAXN], lab_hi[MAXN];
static int S[64], bestS[64];
static long long nodes;
static int wr, wn;

static void rec(int size, const uint64_t *syn, uint64_t llo, uint64_t lhi, const uint64_t *excl) {
    nodes++;
    int u = 0;
    for (int w = 0; w < wr; w++) u += __builtin_popcountll(syn[w]);
    if (u == 0) {
        if ((llo | lhi) && size < best) {
            best = size;
            memcpy(bestS, S, sizeof(int) * size);
        }
        return;
    }
    if (size + (u + maxcol - 1) / maxcol >= best) return;
    /* choose the unsatisfied check with the fewest options */
    int bc = -1, bcount = 1 << 30;
    for (int w = 0; w < wr; w++) {
        uint64_t x = syn[w];
        while (x) {
            int b = __builtin_ctzll(x);
            x &= x - 1;
            int ch = w * 64 + b, cnt = 0;
            for (int t = 0; t < rowsz[ch]; t++) {
                int q = rows[ch][t];
                if (q > anchor && !((excl[q >> 6] >> (q & 63)) & 1)) cnt++;
            }
            if (cnt < bcount) {
                bcount = cnt;
                bc = ch;
                if (cnt == 0) return;
            }
        }
    }
    uint64_t ex[WN], ns[WR];
    memcpy(ex, excl, sizeof(uint64_t) * wn);
    for (int t = 0; t < rowsz[bc]; t++) {
        int q = rows[bc][t];
        if (q <= anchor || ((ex[q >> 6] >> (q & 63)) & 1)) continue;
        ex[q >> 6] |= 1ULL << (q & 63);
        for (int w = 0; w < wr; w++) ns[w] = syn[w] ^ colmask[q][w];
        S[size] = q;
        rec(size + 1, ns, llo ^ lab_lo[q], lhi ^ lab_hi[q], ex);
    }
}

int main(void) {
    int a0, a1;
    if (scanf("%d %d %d %d %d %d", &n, &r, &k, &best, &a0, &a1) != 6) return 1;
    if (n > MAXN || r > MAXR || best > 64) return 2;
    wr = (r + 63) / 64;
    wn = (n + 63) / 64;
    int colw[MAXN] = {0};
    for (int i = 0; i < r; i++) {
        if (scanf("%d", &rowsz[i]) != 1 || rowsz[i] > 64) return 3;
        for (int t = 0; t < rowsz[i]; t++) {
            int q;
            if (scanf("%d", &q) != 1) return 4;
            rows[i][t] = q;
            colmask[q][i >> 6] ^= 1ULL << (i & 63);
        }
    }
    for (int q = 0; q < n; q++) {
        unsigned long long lo, hi;
        if (scanf("%llx %llx", &lo, &hi) != 2) return 5;
        lab_lo[q] = lo;
        lab_hi[q] = hi;
        for (int w = 0; w < wr; w++) colw[q] += __builtin_popcountll(colmask[q][w]);
    }
    maxcol = 1;
    for (int q = 0; q < n; q++)
        if (colw[q] > maxcol) maxcol = colw[q];
    int start = best;
    for (anchor = a0; anchor < a1 && anchor < n; anchor++) {
        uint64_t syn[WR], ex[WN];
        memset(ex, 0, sizeof ex);
        ex[anchor >> 6] |= 1ULL << (anchor & 63);
        for (int w = 0; w < wr; w++) syn[w] = colmask[anchor][w];
        S[0] = anchor;
        rec(1, syn, lab_lo[anchor], lab_hi[anchor], ex);
    }
    printf("%d %lld\n", best, nodes);
    if (best < start)
        for (int i = 0; i < best; i++) printf("%d%c", bestS[i], i + 1 < best ? ' ' : '\n');
    return 0;
}
