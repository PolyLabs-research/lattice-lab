/*
 * examples/qec-distance/search.c with one addition, the split (below); otherwise unchanged.
 *
 * The least weight of a nontrivial codeword, by an exhaustive check-driven search whose bound is
 * raised one at a time (iterative deepening). distance.py (distance_search) builds the input,
 * runs this program and states why the search is exact. Integer arithmetic only: no LP, no
 * floating point.
 *
 * Input on stdin, whitespace separated:
 *   n r k first bound a  qubits, checks, logical labels (k <= 128), the first and the last
 *                        search bounds (1 <= first <= bound <= 64), and the number of anchors
 *   a anchors            the qubits to search from, each in turn as the least qubit of a codeword
 *   r rows: w q_1..q_w   the support of each check (w <= 64)
 *   n labels: lo hi      for each qubit, the bits j of the logicals L_j that contain it, as two
 *                        hexadecimal 64-bit words
 * Output, each line flushed at once, so that a run stopped from outside keeps what it found:
 *   "best w q_1 .. q_w"  each time a lighter nontrivial codeword is found;
 *   "pass b nodes ms"    when the pass with bound b ends without finding one, so that none has
 *                        weight below b (the pass's nodes and milliseconds of wall clock);
 *   "done nodes"         when the search ends (the nodes of every pass).
 *
 * The passes run with bounds b = first, first + 1, ..., bound, and stop after the first pass
 * that finds a nontrivial codeword. `proven` is the weight that no nontrivial codeword is known
 * to be below: 1 at the start (a nontrivial codeword is nonzero), then b after a pass with bound
 * b that found none. The search ends at once when a find's weight equals it. With first = bound
 * there is one pass, which keeps lowering its bound to each find.
 *
 * A pass with bound b, for an anchor a, grows a set S from {a}. While S has a nonzero syndrome
 * it takes the unsatisfied check with the fewest candidates (qubits above a, not in S, not
 * excluded) and branches on each candidate in turn, excluding it from the later branches. A set
 * with zero syndrome is a leaf, recorded when its label is nonzero and it is lighter than the
 * best so far (b at the start of the pass). A branch stops when |S| + ceil(unsatisfied / maxcol)
 * reaches the best so far (maxcol: the most checks any qubit is in).
 *
 * A split (three arguments: depth, parts, part) shares a pass among parts processes. A node
 * whose set S has `depth` qubits is searched only by the part that a hash of its qubits, in the
 * order they were added, picks; the nodes above that depth are searched by every part. The hash
 * depends on the node alone, not on the order of the traversal, so the parts' subtrees at that
 * depth are disjoint and together are all of them, whatever each part's best so far.
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
#define WR (MAXR / 64)

static int n, r, best, proven, stop, maxcol, anchor, wn, wr;
static int rowsz[MAXR], rows[MAXR][MAXW];
static uint64_t colmask[MAXN][WR];
static uint64_t lab_lo[MAXN], lab_hi[MAXN];
static int S[MAXW];
static long long nodes;
static int split_depth, split_parts = 1, split_part;

static int excluded(const uint64_t *ex, int q) { return (int)((ex[q >> 6] >> (q & 63)) & 1); }

static long long milliseconds(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (long long)t.tv_sec * 1000 + t.tv_nsec / 1000000;
}

static void record(int size) {
    best = size;
    printf("best %d", size);
    for (int i = 0; i < size; i++) printf(" %d", S[i]);
    printf("\n");
    fflush(stdout);
    if (size <= proven) stop = 1; /* nothing lighter exists */
}

static int other_part(int size) {
    uint64_t h = 1469598103934665603ULL; /* FNV-1a over the qubits of S, in order */
    for (int i = 0; i < size; i++) {
        h ^= (uint64_t)S[i];
        h *= 1099511628211ULL;
    }
    return (int)(h % (uint64_t)split_parts) != split_part;
}

static void search(int size, const uint64_t *syn, uint64_t llo, uint64_t lhi, const uint64_t *ex) {
    if (split_parts > 1 && size == split_depth && other_part(size)) return;
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
    for (int t = 0; t < rowsz[check] && !stop; t++) {
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

int main(int argc, char **argv) {
    int k, first, bound, count;
    if (argc == 4) {
        split_depth = atoi(argv[1]);
        split_parts = atoi(argv[2]);
        split_part = atoi(argv[3]);
        if (split_depth < 2 || split_parts < 1 || split_part < 0 || split_part >= split_parts)
            return fail("bad split");
    } else if (argc != 1)
        return fail("usage: search [depth parts part]");
#ifdef __linux__
    prctl(PR_SET_PDEATHSIG, SIGKILL); /* die with the process that started the search */
#endif
    if (scanf("%d %d %d %d %d %d", &n, &r, &k, &first, &bound, &count) != 6)
        return fail("bad header");
    if (n < 1 || n > MAXN || r < 0 || r > MAXR || k < 0 || k > 128 || first < 1 ||
        first > bound || bound > MAXW)
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
    long long total = 0;
    proven = 1;
    for (int b = first; b <= bound; b++) {
        long long start = milliseconds();
        best = b;
        nodes = 0;
        for (int i = 0; i < count && !stop; i++) {
            uint64_t syn[WR], ex[WN];
            anchor = anchors[i];
            memset(ex, 0, sizeof ex);
            ex[anchor >> 6] |= 1ULL << (anchor & 63);
            memcpy(syn, colmask[anchor], sizeof syn);
            S[0] = anchor;
            search(1, syn, lab_lo[anchor], lab_hi[anchor], ex);
        }
        total += nodes;
        if (best < b) break; /* a pass that finds a codeword ends at the least weight */
        proven = b;
        printf("pass %d %lld %lld\n", b, nodes, milliseconds() - start);
        fflush(stdout);
    }
    printf("done %lld\n", total);
    free(anchors);
    return 0;
}
