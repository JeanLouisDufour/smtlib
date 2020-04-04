# import numpy as np
import random

def nb_of_vars(f):
	""
	maxi = mini = 0
	for cl in f:
		for l in cl:
			assert isinstance(l,int) and l != 0
			if l > maxi: maxi = l
			if l < mini: mini = l
	return max(maxi, -mini)

def satisfy(a,c):
	""
	return any(l in a for l in c)

def nb_cl_sat_by(f,a):
	""
	return sum(satisfy(a,c) for c in f)
	
def is_sat_by(f,a):
	""
	return nb_cl_sat_by(f,a) == len(f)

def i2a(i, N, a = None):
	"ATTENTION : ordre inverse"
	# s = np.binary_repr(i,N)
	if a is None:
		a = [None] * N
	for j in range(N):
		# a[j] = j+1 if s[j] == '1' else -(j+1)
		a[j] = j+1 if i & 1 else -(j+1) ; i >>= 1
	return a

def truth_table(f, N = None, t = None):
	""
	if N is None:
		N = nb_of_vars(f)
	a = [0] * N
	# t = np.zeros(2**N, dtype = np.bool)
	if t is None:
		t = [None] * 2**N
	else:
		assert len(t) == 2**N
	r = 0
	for i in range(2**N):
		i2a(i, N, a)
		t[i] = nb = nb_cl_sat_by(f,a)
		r += nb == len(f)
	return t, r

def randinv(cl):
	""
	for i, b in enumerate(random.choices([False,True], k = len(cl))):
		if b:
			cl[i] = -cl[i]
	return cl

def generate_kcnf(K, N, M):
	""
	RN = range(1,N+1)
	return [randinv(random.sample(RN,K)) for _ in range(M)]

def select_kcnf(base, M):
	""
	idx = random.randint(0, len(base) - M) # a <= N <= b
	return base[idx:idx+M]

if __name__ == '__main__':
	f = [ [-1,-2,-3],[-4,5,6]]
	t,r = truth_table(f)
	print(r)
	print(t)

	