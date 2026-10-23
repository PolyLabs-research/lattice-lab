/*
 * Two fast routines for the census (census.py builds the input, runs this program and checks it
 * against bb.py and examples/qec-distance-2's equivalence_key). Integer arithmetic only.
 *
 *   census k L M [check]
 *     For every raw code of the published form on the L x M torus, A = x^a + y^b + y^c and
 *     B = y^d + x^e + x^f with b < c in Z_M and e < f in Z_L, in the order
 *       for a < L, for b < c < M, for d < M, for e < f < L
 *     (the order of census.raw_parameters), write rank_GF2(H_X) as one byte to stdout, where
 *     H_X = [A | B] in bb.py's convention: row (i, j) of A has a 1 in column (i - p, j - q) for
 *     each monomial x^p y^q, repeated monomials cancelling (A = x^0 + y^0 + y^c is y^c). With
 *     "check" it writes two bytes per code, rank H_X and rank H_Z, H_Z = [B^T | A^T] (row (i, j)
 *     of A^T has its 1s in columns (i + p, j + q)). k = 2LM - rank H_X - rank H_Z.
 *     The rank is Gaussian elimination on bitset rows of 2LM <= 320 bits: each row is reduced by
 *     its leading bit against the pivots kept so far, and kept when something remains.
 *
 *   census canon L M
 *     stdin: the number of automorphisms of Z_L x Z_M, then each as the images (g0 g1 h0 h1) of
 *     (1, 0) and (0, 1); then the number of codes, then each code as three monomials of A and
 *     three of B, "p q" each (six distinct-within-each-polynomial pairs). For each code it
 *     writes one line: the canonical key as six indices p M + q, then the number of
 *     automorphisms phi with phi(A) ~ A and phi(B) ~ B, then the number with phi(A) ~ B and
 *     phi(B) ~ A, where P ~ Q means Q is a translate of P (a monomial times P).
 *     The key is equivalence_key's: the least translate T(P) of a set P of three monomials is
 *     the least, as a sorted triple of indices, of P - u over the monomials u of P (some least
 *     translate contains 0, so it is one of these); and the key is the least, over the
 *     automorphisms phi, of the sorted pair (T(phi A), T(phi B)), compared as six indices.
 *     Indices order monomials as equivalence_key's (p, q) pairs do, since 0 <= q < M.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAXLM 160
#define WORDS 5 /* 2 LM <= 320 bits */
_Static_assert(64 * WORDS >= 2 * MAXLM, "WORDS must hold 2 MAXLM bits");

static int L, M, LM, W;

static int idx(int p, int q) { return (((p % L) + L) % L) * M + (((q % M) + M) % M); }

/* rank over GF(2) of `count` rows of W words each; the rows are consumed */
static int rank_rows(uint64_t rows[][WORDS], int count) {
    static uint64_t piv[2 * MAXLM][WORDS];
    static unsigned char have[2 * MAXLM];
    memset(have, 0, sizeof have);
    int rank = 0;
    for (int r = 0; r < count; r++) {
        uint64_t *v = rows[r];
        for (;;) {
            int w = W - 1;
            while (w >= 0 && !v[w]) w--;
            if (w < 0) break;
            int top = w * 64 + 63 - __builtin_clzll(v[w]);
            if (!have[top]) {
                memcpy(piv[top], v, sizeof(uint64_t) * WORDS);
                have[top] = 1;
                rank++;
                break;
            }
            for (int t = 0; t <= w; t++) v[t] ^= piv[top][t];
        }
    }
    return rank;
}

static void flip(uint64_t *row, int bit) { row[bit >> 6] ^= 1ULL << (bit & 63); }

/* the rows of [P | Q] (transpose = 0) or [P^T | Q^T] (transpose = 1), monomials as (p, q) */
static void build(uint64_t rows[][WORDS], const int P[3][2], const int Q[3][2], int transpose) {
    int sign = transpose ? 1 : -1;
    for (int i = 0; i < L; i++)
        for (int j = 0; j < M; j++) {
            uint64_t *row = rows[i * M + j];
            memset(row, 0, sizeof(uint64_t) * WORDS);
            for (int t = 0; t < 3; t++) {
                flip(row, idx(i + sign * P[t][0], j + sign * P[t][1]));
                flip(row, LM + idx(i + sign * Q[t][0], j + sign * Q[t][1]));
            }
        }
}

static int k_mode(int check) {
    static uint64_t rows[MAXLM][WORDS];
    size_t cap = 1 << 16, used = 0;
    unsigned char *out = malloc(cap);
    for (int a = 0; a < L; a++)
        for (int b = 0; b < M; b++)
            for (int c = b + 1; c < M; c++)
                for (int d = 0; d < M; d++)
                    for (int e = 0; e < L; e++)
                        for (int f = e + 1; f < L; f++) {
                            int A[3][2] = {{a, 0}, {0, b}, {0, c}};
                            int B[3][2] = {{0, d}, {e, 0}, {f, 0}};
                            if (used + 2 > cap) {
                                cap *= 2;
                                out = realloc(out, cap);
                            }
                            /* H_X = [A | B]; H_Z = [B^T | A^T] */
                            build(rows, A, B, 0);
                            out[used++] = (unsigned char)rank_rows(rows, LM);
                            if (check) {
                                build(rows, B, A, 1);
                                out[used++] = (unsigned char)rank_rows(rows, LM);
                            }
                            if (used >= (1 << 15)) {
                                fwrite(out, 1, used, stdout);
                                used = 0;
                            }
                        }
    fwrite(out, 1, used, stdout);
    free(out);
    return 0;
}

static void sort3(int *v) {
    int t;
    if (v[0] > v[1]) t = v[0], v[0] = v[1], v[1] = t;
    if (v[1] > v[2]) t = v[1], v[1] = v[2], v[2] = t;
    if (v[0] > v[1]) t = v[0], v[0] = v[1], v[1] = t;
}

static int less3(const int *x, const int *y) {
    for (int t = 0; t < 3; t++)
        if (x[t] != y[t]) return x[t] < y[t];
    return 0;
}

static int same3(const int *x, const int *y) { return x[0] == y[0] && x[1] == y[1] && x[2] == y[2]; }

/* the least translate of three monomials (p, q), as sorted indices */
static void least_translate(const int P[3][2], int *out) {
    int first = 1;
    for (int u = 0; u < 3; u++) {
        int v[3];
        for (int t = 0; t < 3; t++) v[t] = idx(P[t][0] - P[u][0], P[t][1] - P[u][1]);
        sort3(v);
        if (first || less3(v, out)) memcpy(out, v, sizeof v), first = 0;
    }
}

static void image(const int P[3][2], const int *f, int Q[3][2]) {
    for (int t = 0; t < 3; t++) {
        Q[t][0] = ((P[t][0] * f[0] + P[t][1] * f[2]) % L + L) % L;
        Q[t][1] = ((P[t][0] * f[1] + P[t][1] * f[3]) % M + M) % M;
    }
}

static int canon_mode(void) {
    int count;
    if (scanf("%d", &count) != 1 || count < 1) return fprintf(stderr, "census: bad automorphisms\n"), 1;
    int *aut = malloc(sizeof(int) * 4 * count);
    for (int i = 0; i < 4 * count; i++)
        if (scanf("%d", &aut[i]) != 1) return fprintf(stderr, "census: bad automorphism\n"), 1;
    int codes;
    if (scanf("%d", &codes) != 1 || codes < 0) return fprintf(stderr, "census: bad code count\n"), 1;
    for (int c = 0; c < codes; c++) {
        int A[3][2], B[3][2];
        for (int t = 0; t < 3; t++)
            if (scanf("%d %d", &A[t][0], &A[t][1]) != 2) return fprintf(stderr, "census: bad code\n"), 1;
        for (int t = 0; t < 3; t++)
            if (scanf("%d %d", &B[t][0], &B[t][1]) != 2) return fprintf(stderr, "census: bad code\n"), 1;
        int ta[3], tb[3], best[6], fixes = 0, swaps = 0, have = 0;
        least_translate(A, ta);
        least_translate(B, tb);
        for (int i = 0; i < count; i++) {
            int PA[3][2], PB[3][2], ua[3], ub[3], key[6];
            image(A, &aut[4 * i], PA);
            image(B, &aut[4 * i], PB);
            least_translate(PA, ua);
            least_translate(PB, ub);
            fixes += same3(ua, ta) && same3(ub, tb);
            swaps += same3(ua, tb) && same3(ub, ta);
            if (less3(ub, ua)) {
                memcpy(key, ub, sizeof ub);
                memcpy(key + 3, ua, sizeof ua);
            } else {
                memcpy(key, ua, sizeof ua);
                memcpy(key + 3, ub, sizeof ub);
            }
            int smaller = !have;
            for (int t = 0; t < 6 && have; t++)
                if (key[t] != best[t]) {
                    smaller = key[t] < best[t];
                    break;
                }
            if (smaller) memcpy(best, key, sizeof key), have = 1;
        }
        printf("%d %d %d %d %d %d %d %d\n", best[0], best[1], best[2], best[3], best[4], best[5],
               fixes, swaps);
    }
    free(aut);
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 4) return fprintf(stderr, "usage: census k|canon L M [check]\n"), 1;
    L = atoi(argv[2]);
    M = atoi(argv[3]);
    LM = L * M;
    if (L < 1 || M < 1 || LM > MAXLM)
        return fprintf(stderr, "census: size out of range: %d x %d has lm = %d, census.c holds "
                       "lm <= MAXLM = %d (WORDS = %d words of 64 bits for 2 lm bits)\n",
                       L, M, LM, MAXLM, WORDS), 1;
    W = (2 * LM + 63) / 64;
    if (!strcmp(argv[1], "k")) return k_mode(argc > 4 && !strcmp(argv[4], "check"));
    if (!strcmp(argv[1], "canon")) return canon_mode();
    return fprintf(stderr, "census: unknown mode %s\n", argv[1]), 1;
}
