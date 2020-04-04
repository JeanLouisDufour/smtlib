#include "sat_util.h"
#if 1
#	include <stdio.h>
#else
#	define printf(a, ...)
#endif

/****
gcc -c -Wall sat_util.c
gcc -shared -o sat_util.dll sat_util.o
****/
	
int test1d(int n, int p[/*n*/]) { /* ctypes.POINTER(ctypes.c_int) */
	int i, s = 0;
	printf("*** test 1D %d ****\n",n);
	for (i = 0; i < n; i++) {
		s += p[i];
		p[i] = -p[i];
	}
	printf("*** %d ***\n", s);
	return s;
}

int test2d(int li, int co, int p[/*li*/][co]) { /* ctypes.POINTER(Vec_3) */
	int i, j, s = 0;
	printf("*** test 2D %d %d ****\n",li,co);
	for (i = 0; i < li; i++) {
		for (j = 0; j < co; j++) {
			s += p[i][j];
			p[i][j] = -p[i][j];
		}
	}
	printf("*** %d ***\n", s);
	return s;
}

int tt_3cnf(int M, int cnf[M][3], int N, int TWO_to_N, int tt[TWO_to_N]) {
	/***
		tt[i] est le nombre de clauses unsat par i
	***/
	if (TWO_to_N != (1<<N)) return -1;
	int K = 3;
	int i, r=0;
	for (i=0; i < TWO_to_N; i++) {
		int m, cl_sat = 0;
		for (m=0; m < M; m++) {
			int k, is_sat = 0;
			for (k=0; k<K; k++) {
				int lit = cnf[m][k];
				if (i==0 && (lit == 0 || lit > N || lit < -N)) return -1;
				if (lit > 0) {
					if (i & (1 << (lit-1))) {
						is_sat = 1;
						break;
					}
				} else {
					if ((~i) & (1 << ((-lit)-1))) {
						is_sat = 1;
						break;
					}
				}
			}
			if (is_sat) cl_sat++;
		}
		tt[i] = M - cl_sat;
		if (cl_sat == M) r++;
	}
	return r;
}

int get_clusters(int TWO_to_N, int t[TWO_to_N], int t_cluster[TWO_to_N]) {
	/****
		t[i] est le nombre de clauses unsat par i
		t_cluster[i] est le numero de cluster de i (<=i)
	***/
	int N = 0;
	while ((1<<N) < TWO_to_N) N++;
	int i;
	for (i=0; i<TWO_to_N; i++) {
		t[i] = -t[i];
		if (t[i] < 0) {
			t_cluster[i] = t[i];
			continue;
		}
		else{
			if (t[i]) return -1;
		}
		int j, nb=0, neighbors[N];
		for (j=0; j<N; j++) {
			int neighb = i ^ (1<<j);
			if (neighb > i) continue;
			if (t[neighb] == 0) neighbors[nb++] = neighb;
		}
		/* soudure */
		if (nb >= 2) {
			int neighb_cid_l[nb], neighb_cid_min = 1<<30;
			for (j=0; j<nb; j++) {
				int tmp = neighb_cid_l[j] = t_cluster[neighbors[j]];
				if (tmp < neighb_cid_min) {
					neighb_cid_min = tmp;
				}
			}
			t_cluster[i] = neighb_cid_min;
			for (j=0; j<i; j++) {
				int tmp = t_cluster[j];
				if (tmp < 0) continue;
				int is_in = 0;
				for(int k=0; k<nb; k++) {
					if (tmp == neighb_cid_l[k]) {
						is_in = 1;
						break;
					}
				}
				if (is_in) t_cluster[j] = neighb_cid_min;
			}
		} else if (nb == 1) {
			t_cluster[i] = t_cluster[neighbors[0]];
		} else {
			t_cluster[i] = i;
		}
	}
	return 0;
}
