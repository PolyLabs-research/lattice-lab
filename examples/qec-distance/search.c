/*
 * The least weight of a nontrivial codeword, by an exhaustive check-driven search. distance.py
 * (distance_search) builds the input, runs this program and states why the search is exact.
 * Integer arithmetic only: no LP, no floating point.
 *
 * Input on stdin, whitespace separated:
 *   n r k bound a      qubits, checks, logical labels (k <= 128), the search bound (at most 64),
 *                      and the number of anchors
 *   a anchors          the qubits to search from, each in turn as the least qubit of a codeword
 *   r rows: w q_1..q_w the support of each check (w <= 64)
 *   n labels: lo hi    for each qubit, the bits j of the logicals L_j that contain it, as two
 *                      hexadecimal 64-bit words
 * Output: "best w q_1 .. q_w" each time a lighter nontrivial codeword is found (flushed at once,
 * so a run stopped from outside keeps its best), then "done nodes" when every anchor is searched.
 *
 * For an anchor a, the search grows a set S from {a}. While S has a nonzero syndrome it takes the
 * unsatisfied check with the fewest candidates (qubits above a, not in S, not excluded) and
 * branches on each candidate in turn, excluding it from the later branches. A set with zero
 * syndrome is a leaf, recorded when its label is nonzero and it is lighter than the best so far.
 * A branch stops when |S| + ceil(unsatisfied / maxcol) reaches the best so far (maxcol: the most
 * checks any qubit is in).
 */
#ifdef __linux__
#define _GNU_SOURCE
#include <signal.h>
#include <sys/prctl.h>
#endif
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXN 2048
#define MAXR 1024
#define MAXW 64
#define WN (MAXN / 64)
#define WR (MAXR / 64)

static int n, r, best, maxcol, anchor, wn, wr;
static int rowsz[MAXR], rows[MAXR][MAXW];
static uint64_t colmask[MAXN][WR];
static uint64_t lab_lo[MAXN], lab_hi[MAXN];
static int S[MAXW];
static long long nodes;

static int excluded(const uint64_t *ex, int q) { return (int)((ex[q >> 6] >> (q & 63)) & 1); }

static void record(int size) {
    best = size;
    printf("best %d", size);
    for (int i = 0; i < size; i++) printf(" %d", S[i]);
    printf("\n");
    fflush(stdout);
}

static void search(int size, const uint64_t *syn, uint64_t llo, uint64_t lhi, const uint64_t *ex) {
    nodes++;
    int u = 0;
    for (int w = 0; w < wr; w++) u += __builtin_popcountll(syn[w]);
    if (u == 0) {
        if ((llo | lhi) && size < best) record(size);
        return;
    }
    if (size + (u + maxcol - 1) / maxcol >= best) return;
    int check = -1, fewest = MAXW + 1;
    for (int w = 0; w < wr; w++) {
        for (uint64_t x = syn[w]; x; x &= x - 1) {
            int c = w * 64 + __builtin_ctzll(x), count = 0;
            for (int t = 0; t < rowsz[c]; t++) {
                int q = rows[c][t];
                count += q > anchor && !excluded(ex, q);
            }
            if (count == 0) return;
            if (count < fewest) {
                fewest = count;
                check = c;
            }
        }
    }
    uint64_t child_ex[WN], child_syn[WR];
    memcpy(child_ex, ex, sizeof(uint64_t) * wn);
    for (int t = 0; t < rowsz[check]; t++) {
        int q = rows[check][t];
        if (q <= anchor || excluded(child_ex, q)) continue;
        child_ex[q >> 6] |= 1ULL << (q & 63);
        for (int w = 0; w < wr; w++) child_syn[w] = syn[w] ^ colmask[q][w];
        S[size] = q;
        search(size + 1, child_syn, llo ^ lab_lo[q], lhi ^ lab_hi[q], child_ex);
    }
}

static int fail(const char *why) {
    fprintf(stderr, "search: %s\n", why);
    return 1;
}

int main(void) {
    int k, count;
#ifdef __linux__
    prctl(PR_SET_PDEATHSIG, SIGKILL); /* die with the process that started the search */
#endif
    if (scanf("%d %d %d %d %d", &n, &r, &k, &best, &count) != 5) return fail("bad header");
    if (n < 1 || n > MAXN || r < 0 || r > MAXR || k < 0 || k > 128 || best < 1 || best > MAXW)
        return fail("size out of range");
    if (count < 0 || count > n) return fail("bad anchor count");
    int *anchors = malloc(sizeof(int) * (count ? count : 1));
    for (int i = 0; i < count; i++)
        if (scanf("%d", &anchors[i]) != 1 || anchors[i] < 0 || anchors[i] >= n)
            return fail("bad anchor");
    wn = (n + 63) / 64;
    wr = (r + 63) / 64;
    for (int i = 0; i < r; i++) {
        if (scanf("%d", &rowsz[i]) != 1 || rowsz[i] < 0 || rowsz[i] > MAXW)
            return fail("bad row weight");
        for (int t = 0; t < rowsz[i]; t++) {
            int q;
            if (scanf("%d", &q) != 1 || q < 0 || q >= n) return fail("bad row entry");
            rows[i][t] = q;
            colmask[q][i >> 6] ^= 1ULL << (i & 63);
        }
    }
    maxcol = 1;
    for (int q = 0; q < n; q++) {
        unsigned long long lo, hi;
        if (scanf("%llx %llx", &lo, &hi) != 2) return fail("bad label");
        lab_lo[q] = lo;
        lab_hi[q] = hi;
        int column = 0;
        for (int w = 0; w < wr; w++) column += __builtin_popcountll(colmask[q][w]);
        if (column > maxcol) maxcol = column;
    }
    for (int i = 0; i < count; i++) {
        uint64_t syn[WR], ex[WN];
        anchor = anchors[i];
        memset(ex, 0, sizeof ex);
        ex[anchor >> 6] |= 1ULL << (anchor & 63);
        memcpy(syn, colmask[anchor], sizeof syn);
        S[0] = anchor;
        search(1, syn, lab_lo[anchor], lab_hi[anchor], ex);
    }
    printf("done %lld\n", nodes);
    free(anchors);
    return 0;
}
