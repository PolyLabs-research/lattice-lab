/*
 * isd.c: window.c (examples/qec-open-distance) with Lee-Brickell's p = 2 and a fixed number of
 * iterations, for census stage 4b's probabilistic distances (isd.py). Integer arithmetic only.
 *
 * Input on stdin, as window.c's but for its header:
 *   n r k seed iterations target   qubits, checks, logical labels (k <= 128), the seed of the
 *                                  random permutations, the number of iterations, and a weight
 *   r rows: w q_1..q_w             the support of each check (w <= 64)
 *   n labels: lo hi                for each qubit, the bits j of the logicals L_j containing it
 *   watch w q_1..q_w               (optional) a codeword whose meetings with the information set
 *                                  are counted, to calibrate isd.py's model
 * Output, each line flushed at once:
 *   "dim K"                        the dimension of the kernel of the checks
 *   "best w q_1 .. q_w"            each time a lighter nontrivial codeword is found
 *   "done iterations hits"         at the end: hits is the number of iterations that found a
 *                                  nontrivial codeword of weight <= target
 *   "watch m1 m2"                  with a watch: the iterations whose information set meets
 *                                  it in exactly 1 and exactly 2 positions
 *
 * One iteration: a uniformly random order of the columns; Gauss-Jordan elimination of a basis of
 * the kernel, taking pivots in that order (as window.c); then every row and every sum of two
 * rows whose label is nonzero is a nontrivial codeword, and is weighed. A codeword is found
 * when its support meets the information set (the pivots) in one or two positions, since a
 * codeword is the sum of the rows at the pivots in its support.
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
#include <time.h>

#define MAXN 1024
#define MAXR 1024
#define MAXW 64
#define WN (MAXN / 64)

static int n, r, wn;
static uint64_t H[MAXR][WN];        /* the checks */
static uint64_t G[MAXN][WN];        /* a basis of the kernel */
static uint64_t glo[MAXN], ghi[MAXN];
static uint64_t lab_lo[MAXN], lab_hi[MAXN];
static uint64_t rng;

static uint64_t next(void) { /* splitmix64 */
    uint64_t z = (rng += 0x9e3779b97f4a7c15ULL);
    z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL;
    z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL;
    return z ^ (z >> 31);
}

static int bit(const uint64_t *v, int q) { return (int)((v[q >> 6] >> (q & 63)) & 1); }

static int fail(const char *why) {
    fprintf(stderr, "window: %s\n", why);
    return 1;
}

/* A basis of {v : H v = 0}: reduce H to reduced row echelon form, then one vector per free
 * column. Returns its dimension. */
static int kernel(void) {
    static int pivot_of_row[MAXR], is_pivot[MAXN];
    int rank = 0;
    for (int c = 0; c < n && rank < r; c++) {
        int p = -1;
        for (int i = rank; i < r; i++)
            if (bit(H[i], c)) {
                p = i;
                break;
            }
        if (p < 0) continue;
        for (int w = 0; w < wn; w++) {
            uint64_t t = H[p][w];
            H[p][w] = H[rank][w];
            H[rank][w] = t;
        }
        for (int i = 0; i < r; i++)
            if (i != rank && bit(H[i], c))
                for (int w = 0; w < wn; w++) H[i][w] ^= H[rank][w];
        pivot_of_row[rank] = c;
        is_pivot[c] = 1;
        rank++;
    }
    int dim = 0;
    for (int f = 0; f < n; f++) {
        if (is_pivot[f]) continue;
        memset(G[dim], 0, sizeof G[dim]);
        G[dim][f >> 6] |= 1ULL << (f & 63);
        for (int i = 0; i < rank; i++)
            if (bit(H[i], f)) G[dim][pivot_of_row[i] >> 6] |= 1ULL << (pivot_of_row[i] & 63);
        dim++;
    }
    return dim;
}

int main(void) {
    int k, target;
    unsigned long long seed;
    long long budget;
#ifdef __linux__
    prctl(PR_SET_PDEATHSIG, SIGKILL);
#endif
    if (scanf("%d %d %d %llu %lld %d", &n, &r, &k, &seed, &budget, &target) != 6)
        return fail("bad header");
    if (n < 1 || n > MAXN || r < 0 || r > MAXR || k < 0 || k > 128 || budget < 0)
        return fail("size");
    wn = (n + 63) / 64;
    for (int i = 0; i < r; i++) {
        int w;
        if (scanf("%d", &w) != 1 || w < 0 || w > MAXW) return fail("bad row weight");
        for (int t = 0; t < w; t++) {
            int q;
            if (scanf("%d", &q) != 1 || q < 0 || q >= n) return fail("bad row entry");
            H[i][q >> 6] ^= 1ULL << (q & 63);
        }
    }
    for (int q = 0; q < n; q++) {
        unsigned long long lo, hi;
        if (scanf("%llx %llx", &lo, &hi) != 2) return fail("bad label");
        lab_lo[q] = lo;
        lab_hi[q] = hi;
    }
    static int watched[MAXN];
    int nwatch = 0;
    char word[16];
    if (scanf("%15s", word) == 1) {
        if (strcmp(word, "watch") != 0 || scanf("%d", &nwatch) != 1 || nwatch < 1 || nwatch > n)
            return fail("bad watch");
        for (int t = 0; t < nwatch; t++)
            if (scanf("%d", &watched[t]) != 1 || watched[t] < 0 || watched[t] >= n)
                return fail("bad watch entry");
    }
    int dim = kernel();
    printf("dim %d\n", dim);
    fflush(stdout);
    for (int i = 0; i < dim; i++)
        for (int q = 0; q < n; q++)
            if (bit(G[i], q)) {
                glo[i] ^= lab_lo[q];
                ghi[i] ^= lab_hi[q];
            }
    rng = seed;
    static int order[MAXN], weight[MAXN];
    int best = n + 1;
    long long iterations = 0, hits = 0, meet1 = 0, meet2 = 0;
    static unsigned char pivot[MAXN];
    uint64_t sum[WN];
    while (iterations < budget) {
        for (int q = 0; q < n; q++) order[q] = q;
        for (int q = n - 1; q > 0; q--) { /* Fisher-Yates */
            int j = (int)(next() % (uint64_t)(q + 1)), t = order[q];
            order[q] = order[j];
            order[j] = t;
        }
        int rank = 0;
        memset(pivot, 0, (size_t)n);
        for (int t = 0; t < n && rank < dim; t++) {
            int c = order[t], p = -1;
            for (int i = rank; i < dim; i++)
                if (bit(G[i], c)) {
                    p = i;
                    break;
                }
            if (p < 0) continue;
            if (p != rank) {
                for (int w = 0; w < wn; w++) {
                    uint64_t x = G[p][w];
                    G[p][w] = G[rank][w];
                    G[rank][w] = x;
                }
                uint64_t x = glo[p];
                glo[p] = glo[rank];
                glo[rank] = x;
                x = ghi[p];
                ghi[p] = ghi[rank];
                ghi[rank] = x;
            }
            for (int i = 0; i < dim; i++)
                if (i != rank && bit(G[i], c)) {
                    for (int w = 0; w < wn; w++) G[i][w] ^= G[rank][w];
                    glo[i] ^= glo[rank];
                    ghi[i] ^= ghi[rank];
                }
            pivot[c] = 1;
            rank++;
        }
        if (nwatch) {
            int meet = 0;
            for (int t = 0; t < nwatch; t++) meet += pivot[watched[t]];
            meet1 += meet == 1;
            meet2 += meet == 2;
        }
        int hit = 0;
        for (int i = 0; i < dim; i++) {
            int w = 0;
            for (int x = 0; x < wn; x++) w += __builtin_popcountll(G[i][x]);
            weight[i] = w;
            if (!(glo[i] | ghi[i])) continue;
            if (w <= target) hit = 1;
            if (w < best) {
                best = w;
                printf("best %d", w);
                for (int q = 0; q < n; q++)
                    if (bit(G[i], q)) printf(" %d", q);
                printf("\n");
                fflush(stdout);
            }
        }
        /* p = 2: the sums of two rows; a sum has weight >= |w_i - w_j|, so a pair that cannot
         * reach below both min(best, target + 1) is skipped */
        for (int i = 0; i < dim; i++)
            for (int j = i + 1; j < dim; j++) {
                if (!((glo[i] ^ glo[j]) | (ghi[i] ^ ghi[j]))) continue;
                int bound = best < target + 1 ? target + 1 : best;
                if (abs(weight[i] - weight[j]) >= bound) continue;
                int w = 0;
                for (int x = 0; x < wn; x++) {
                    sum[x] = G[i][x] ^ G[j][x];
                    w += __builtin_popcountll(sum[x]);
                }
                if (w <= target) hit = 1;
                if (w < best) {
                    best = w;
                    printf("best %d", w);
                    for (int q = 0; q < n; q++)
                        if (bit(sum, q)) printf(" %d", q);
                    printf("\n");
                    fflush(stdout);
                }
            }
        hits += hit;
        iterations++;
    }
    if (nwatch) printf("watch %lld %lld\n", meet1, meet2);
    printf("done %lld %lld\n", iterations, hits);
    return 0;
}
