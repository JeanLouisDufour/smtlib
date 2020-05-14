import re

re_corresp = re.compile(r'c\s+(\w+)\s+-->\s+(\d+|\[.+\])\s*')
re_descr = re.compile(r'p\s+cnf\s+')

def read(fn):
	""
	nv = nc = None
	corresp = []
	cnf = []
	fd = open(fn)
	for line in fd: #
		if line == '' or line.isspace(): continue
		if line[0] == 'c':
			m = re_corresp.fullmatch(line)
			if m:
				src,dst = m.groups()
				if dst[0] == '[':
					assert dst[-1] == ']', line
					dst = [int(x) for x in dst[1:-1].split()]
				else:
					dst = int(dst)
				corresp.append([src,dst])
			continue
		if line[0] == 'p':
			assert line.startswith('p cnf ')
			nv, nc = (int(x) for x in line[6:].split())
			continue
		# ligne de clause
		clause = line.split()
		assert clause[-1] == '0', line
		clause = [int(x) for x in clause[:-1]]
		assert all(1<=abs(x)<=nv for x in clause), line
		cnf.append(clause)
	fd.close()
	assert len(cnf) == nc
	for _src,dst in corresp:
		if isinstance(dst,int):
			assert 1<=dst<=nv
		else:
			assert all(1<=abs(x)<=nv for x in dst)
	return corresp, nv, nc, cnf

def read_sol(s):
	""
	pass

if __name__ == "__main__":
	fn = '../ML/tmp.cnf'
	js = read(fn)
