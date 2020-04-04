import ctypes, gc
from time import perf_counter
import sat_util

"""
gcc -c -Wall sat_util.c
gcc -shared -o sat_util.dll sat_util.o
C:\ProgramData\Anaconda3\python.exe sat_wrapper.py
"""

def update_vec(ct_v, py_v):
	""
	ct_v[:] = py_v
	
def update_mat(ct_m, py_m):
	""
	assert len(ct_m) == len(py_m)
	for ct_v,py_v in zip(ct_m,py_m):
		ct_v[:] = py_v

test_3cnf = [ [1,2,3],[4,-5,-6]] ### en C : t[2][3] ; t[0] pointe sur la 1iere ligne (1,2,3)

Vec_3 = ctypes.c_int * 3  ## une ligne

mylib = ctypes.CDLL('./sat_util.dll')

test1d = mylib.test1d
test1d.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
test1d.restype = ctypes.c_int

p = [1,2,3]
#p_for_c = (ctypes.c_int * len(p))(*p)
p_for_c = Vec_3()
update_vec(p_for_c,p)
r = test1d(len(p),p_for_c)

print(r)
print(list(p_for_c))

##################

print('2D')
Matrix_2_3 = Vec_3 * 2
###### test_3cnf_for_c = Matrix_2_3(*test_3cnf) NE MARCHE PAS
#test_3cnf_for_c = Matrix_2_3(*(tuple(cl) for cl in test_3cnf))
test_3cnf_for_c = Matrix_2_3()
update_mat(test_3cnf_for_c, test_3cnf)

test2d = mylib.test2d
test2d.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.POINTER(Vec_3)] # Matrix_2_3
test2d.restype = ctypes.c_int

r = test2d(2,3, test_3cnf_for_c)
print(r)
print(list(list(x) for x in test_3cnf_for_c))

#####
# int truth_table(int M, int cnf[M][3], int N, int TWO_to_N, int tt[TWO_to_N])
#####
print('tt6')
tt_3cnf = mylib.tt_3cnf
tt_3cnf.argtypes = [ctypes.c_int, ctypes.POINTER(Vec_3), ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
tt_3cnf.restype = ctypes.c_int

tt6_for_c = (ctypes.c_int * 2**6)()
r = tt_3cnf(2, test_3cnf_for_c, 6, 2**6, tt6_for_c)

print(r)

####### int get_clusters(int TWO_to_N, int t[TWO_to_N], int t_cluster[TWO_to_N])
print('get_clusters')
get_clusters = mylib.get_clusters
get_clusters.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
get_clusters.restype = ctypes.c_int
t_cluster6_for_c = (ctypes.c_int * 2**6)()
r = get_clusters(2**6, tt6_for_c, t_cluster6_for_c)




print('OK')

if __name__ == '__main__':
	N = 10
	M = 10
	Nsamples = 1000
	t = [0] * 2**N
	f_for_c = (Vec_3 * M)()
	t_for_c = (ctypes.c_int * 2**N)()
	base = sat_util.generate_kcnf(3,N,10000)
	t0 = perf_counter()
	for _ in range(Nsamples):
		f = sat_util.select_kcnf(base, M)
		t,r = sat_util.truth_table(f,N,t)
	t0 = perf_counter() - t0
	print(t0)
	t0 = perf_counter()
	for _ in range(Nsamples):
		f = sat_util.select_kcnf(base, M)
		update_mat(f_for_c, f)
		r_from_c = tt_3cnf(M, f_for_c, N, 2**N, t_for_c)
	t0 = perf_counter() - t0
	print(t0)
