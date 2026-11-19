/*
 * Shortest planar forms of a bivariate bicycle code on the group G = Z_l x Z_m.
 *
 * A form is a homomorphism phi: Z^2 -> G (phi(x) = g1, phi(y) = g2) with integer triangles
 * {0, p, q} and {0, s, t} that phi carries onto A and B up to a translation of each:
 * phi(p) = a1 - a0, phi(q) = a2 - a0, phi(s) = b1 - b0, phi(t) = b2 - b0. A triangle's range is
 * the larger side of its bounding box, a form's range the larger of its two triangles' ranges.
 * For each code this prints the least range over every (g1, g2) in G^2 and every form attaining
 * it. A triangle of range <= r has a translate with p, q in [-r, r]^2, so searching the box of
 * radius R finds every form of range <= R; R doubles until a form is found.
 *
 * stdin:  one code per line: l m  a0x a0y a1x a1y a2x a2y  b0x b0y b1x b1y b2x b2y
 * stdout: per code, "R <range> <count>" then <count> lines "px py qx qy sx sy tx ty".
 *         <range> is -1 (and count 0) when no form exists up to RMAX.
 */
#include <stdio.h>
#include <stdlib.h>

#define RMAX 128
#define MAXPRE 4096

static int imax(int a, int b) { return a > b ? a : b; }
static int imin(int a, int b) { return a < b ? a : b; }

static int range3(int px, int py, int qx, int qy) {
    int sx = imax(0, imax(px, qx)) - imin(0, imin(px, qx));
    int sy = imax(0, imax(py, qy)) - imin(0, imin(py, qy));
    return imax(sx, sy);
}

typedef struct { int x, y; } pt;

static int *out;
static long nout, cap;

static void emit(pt p, pt q, pt s, pt t) {
    if (nout + 8 > cap) {
        cap = cap ? 2 * cap : 1 << 16;
        out = realloc(out, cap * sizeof(int));
        if (!out) { fprintf(stderr, "out of memory\n"); exit(2); }
    }
    out[nout++] = p.x; out[nout++] = p.y; out[nout++] = q.x; out[nout++] = q.y;
    out[nout++] = s.x; out[nout++] = s.y; out[nout++] = t.x; out[nout++] = t.y;
}

int main(void) {
    int l, m, a[6], b[6];
    static pt pre[4][MAXPRE];
    while (scanf("%d %d %d %d %d %d %d %d %d %d %d %d %d %d", &l, &m, &a[0], &a[1], &a[2],
                 &a[3], &a[4], &a[5], &b[0], &b[1], &b[2], &b[3], &b[4], &b[5]) == 14) {
        int tx[4], ty[4];
        tx[0] = ((a[2] - a[0]) % l + l) % l; ty[0] = ((a[3] - a[1]) % m + m) % m;
        tx[1] = ((a[4] - a[0]) % l + l) % l; ty[1] = ((a[5] - a[1]) % m + m) % m;
        tx[2] = ((b[2] - b[0]) % l + l) % l; ty[2] = ((b[3] - b[1]) % m + m) % m;
        tx[3] = ((b[4] - b[0]) % l + l) % l; ty[3] = ((b[5] - b[1]) % m + m) % m;
        int best = -1;
        for (int R = 2; R <= RMAX && best < 0; R *= 2) {
            int bound = R;
            nout = 0;
            for (int g1x = 0; g1x < l; g1x++) for (int g1y = 0; g1y < m; g1y++)
            for (int g2x = 0; g2x < l; g2x++) for (int g2y = 0; g2y < m; g2y++) {
                int np[4] = {0, 0, 0, 0}, full = 0;
                for (int i = -bound; i <= bound; i++) {
                    int ex = ((i * g1x - bound * g2x) % l + l) % l;
                    int ey = ((i * g1y - bound * g2y) % m + m) % m;
                    for (int j = -bound; j <= bound; j++) {
                        for (int u = 0; u < 4; u++)
                            if (ex == tx[u] && ey == ty[u]) {
                                if (np[u] < MAXPRE) { pre[u][np[u]].x = i; pre[u][np[u]].y = j; np[u]++; }
                                else full = 1;
                            }
                        ex += g2x; if (ex >= l) ex -= l;
                        ey += g2y; if (ey >= m) ey -= m;
                    }
                }
                if (full) { fprintf(stderr, "preimage table full\n"); return 2; }
                if (!np[0] || !np[1] || !np[2] || !np[3]) continue;
                int ra = RMAX + 1, rb = RMAX + 1;
                for (int i = 0; i < np[0]; i++) for (int j = 0; j < np[1]; j++)
                    ra = imin(ra, range3(pre[0][i].x, pre[0][i].y, pre[1][j].x, pre[1][j].y));
                if (ra > bound) continue;
                for (int i = 0; i < np[2]; i++) for (int j = 0; j < np[3]; j++)
                    rb = imin(rb, range3(pre[2][i].x, pre[2][i].y, pre[3][j].x, pre[3][j].y));
                int r = imax(ra, rb);
                if (r > bound) continue;
                if (best < 0 || r < best) { best = r; bound = r; nout = 0; }
                for (int i = 0; i < np[0]; i++) for (int j = 0; j < np[1]; j++) {
                    if (range3(pre[0][i].x, pre[0][i].y, pre[1][j].x, pre[1][j].y) > best) continue;
                    for (int c = 0; c < np[2]; c++) for (int d = 0; d < np[3]; d++) {
                        if (range3(pre[2][c].x, pre[2][c].y, pre[3][d].x, pre[3][d].y) > best) continue;
                        emit(pre[0][i], pre[1][j], pre[2][c], pre[3][d]);
                    }
                }
            }
        }
        if (best < 0) nout = 0;
        printf("R %d %ld\n", best, nout / 8);
        for (long i = 0; i < nout; i += 8)
            printf("%d %d %d %d %d %d %d %d\n", out[i], out[i+1], out[i+2], out[i+3], out[i+4],
                   out[i+5], out[i+6], out[i+7]);
        fflush(stdout);
    }
    return 0;
}
