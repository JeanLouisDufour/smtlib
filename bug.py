import sys

#sys.setrecursionlimit(10**6)
rec_lim = sys.getrecursionlimit()
print('rec lim : {}'.format(rec_lim))

def depth(t):
	""
	if isinstance(t,(list,tuple)) and t:
		d = max(depth(ti) for ti in t)+1
	else:
		d = 0
	return d

if len(sys.argv) == 2:
	lim = int(sys.argv[1])
else:
	lim = 30000 # rec_lim//3 -2

e = 'foo'
for i in reversed(range(lim)): # 984 OK
	e = [i,e]

print('lim : {}'.format(lim))
try:
	d = depth(e)
	print(d)
except RecursionError:
	print('RecursionError')
e = [-1,e]
print('lim : {}'.format(lim+1))
try:
	d = depth(e)
	print(d)
except RecursionError:
	print('RecursionError')
