import matplotlib.pyplot as plt
import math, random
from sat_util import randinv, truth_table as tt

K = 3
N = 10
Alpha_min, Alpha_max = 1,6 
Nsample_f = 10

M = 36

####

Mmin = math.floor(Alpha_min*N)
Mmax = math.ceil(Alpha_max*N)
Mrange = range(Mmin, Mmax+1)
alpha_range = [m/N for m in Mrange]

RNpy = range(1,N+1)
Giant_sz = min(1000000, Mmax*Nsample_f)
Giant_f = [randinv(random.sample(RNpy,K)) for _ in range(Giant_sz)]

def gray(n):
	return n ^ n >> 1

HAM = [[1<<i for i in range(N)] for N in range(129)]

# f = [randinv(random.sample(RNpy,K)) for _ in range(M)]

print('sat ratio : {}/{}'.format(sum(t),len(t)))

def get_clusters(t, t_cluster = None):
	""
	N = int(math.log2(len(t)))
	assert len(t) == 2**N
	if t_cluster is None:
		t_cluster = [None] * len(t)
	else:
		assert len(t_cluster) == len(t)
	# t_cluster[:] = (i if ti else None for i,ti in enumerate(t))
	ham = HAM[N]
	for i,ti in enumerate(t):
		if not ti:
			t_cluster[i] = None
			continue
		neighbors = []
		for h in ham:
			neighb = i ^ h
			if neighb > i: continue
			if t[neighb]:
				neighbors.append(neighb)
		# soudure des candidates
		if len(neighbors) >= 2:
			neighb_cid_l = [t_cluster[a] for a in neighbors]
			neighb_cid_min = min(neighb_cid_l)
			t_cluster[i] = neighb_cid_min
			for j in range(i):
				if t_cluster[j] in neighb_cid_l:
					t_cluster[j] = neighb_cid_min
		elif neighbors:
			[a] = neighbors
			t_cluster[i] = t_cluster[a]
		else:
			t_cluster[i] = i
	return t_cluster

mean_nb_sat_l = []
mean_nb_cluster_l = []

t = [None] * 2**N
t_cluster = [None] * 2**N
nb_sat_l = [0] * Nsample_f
nb_cluster_l = [0] * Nsample_f
sz_cluster_l = [0] * Nsample_f
for M in Mrange:
	print(M)
	for sample_i in range(Nsample_f):
		idx = random.randint(0, Giant_sz - M) # a <= N <= b
		f = Giant_f[idx:idx+M]
		tt(f, N, t)
		nb_sat = sum(t)
		nb_sat_l[sample_i] = nb_sat
		get_clusters(t, t_cluster)
		nb_cluster = len(set(t_cluster) - {None})
		assert (nb_sat==0) == (nb_cluster==0)
		nb_cluster_l[sample_i] = nb_cluster
		sz_cluster_l[sample_i] = nb_sat / nb_cluster if nb_cluster else None
	nb_f_sat = sum(nb_sat != 0 for nb_sat in nb_sat_l)
	mean_nb_sat_l.append(sum(nb_sat_l) / nb_f_sat / 2**N if nb_f_sat else None)
	mean_nb_cluster_l.append(sum(nb_cluster_l) / nb_f_sat if nb_f_sat else None)

plt.plot(alpha_range, mean_nb_sat_l, alpha_range, mean_nb_cluster_l)
plt.figure()
	
N1 = math.floor(N/2) ; N2 = math.ceil(N/2)
assert N == N1+N2

x = [gray(i>>N1) for i in range(2**N) if t[i]]
y = [gray(i&((1<<N1)-1)) for i in range(2**N) if t[i]]
plt.scatter(x,y)
