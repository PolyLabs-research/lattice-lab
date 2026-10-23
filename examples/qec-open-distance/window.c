/*
 * Light nontrivial codewords by random information sets (the random-window method of
 * Dumer, Kovalev and Pryadko): an upper bound on the distance, with its witness, and nothing
 * about a lower bound. parts.py (window) builds the input and checks every witness.
 * Integer arithmetic only.
 *
 * Input on stdin, whitespace separated, in search.c's format but for its header:
 *   n r k seed seconds   qubits, checks, logical labels (k <= 128), the seed of the random
 *                        permutations, and the wall-clock seconds to run for
 *   r rows: w q_1..q_w   the support of each check (w <= 64)
 *   n labels: lo hi      for each qubit, the bits j of the logicals L_j that contain it
 * Output, each line flushed at once:
 *   "dim K"              the dimension of the kernel of the checks
 *   "best w q_1 .. q_w"  each time a lighter nontrivial codeword is found
 *   "done iterations"    when the time is up
 *
 * One iteration: a uniformly random order of the columns; Gauss-Jordan elimination of a basis of
 * the kernel, taking pivots in that order, so that each row is the kernel's unique vector that is
 * 1 at its pivot and 0 at every other pivot; each row whose label is nonzero is a nontrivial
 * codeword. A codeword of weight w is a row of some iteration when its support meets the
 * information set (the pivots) in exactly one position.
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

#define MAXN 2048
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

static double seconds_now(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (double)t.tv_sec + t.tv_nsec / 1e9;
}

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
    int k;
    unsigned long long seed;
    double limit;
#ifdef __linux__
    prctl(PR_SET_PDEATHSIG, SIGKILL);
#endif
    if (scanf("%d %d %d %llu %lf", &n, &r, &k, &seed, &limit) != 5) return fail("bad header");
    if (n < 1 || n > MAXN || r < 0 || r > MAXR || k < 0 || k > 128) return fail("size");
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
    static int order[MAXN];
    int best = n + 1;
    long long iterations = 0;
    double start = seconds_now();
    while (seconds_now() - start < limit) {
        for (int q = 0; q < n; q++) order[q] = q;
        for (int q = n - 1; q > 0; q--) { /* Fisher-Yates */
            int j = (int)(next() % (uint64_t)(q + 1)), t = order[q];
            order[q] = order[j];
            order[j] = t;
        }
        int rank = 0;
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
            rank++;
        }
        for (int i = 0; i < dim; i++) {
            if (!(glo[i] | ghi[i])) continue;
            int w = 0;
            for (int x = 0; x < wn; x++) w += __builtin_popcountll(G[i][x]);
            if (w < best) {
                best = w;
                printf("best %d", w);
                for (int q = 0; q < n; q++)
                    if (bit(G[i], q)) printf(" %d", q);
                printf("\n");
                fflush(stdout);
            }
        }
        iterations++;
    }
    printf("done %lld\n", iterations);
    return 0;
}
