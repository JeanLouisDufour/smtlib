def ty(t):
	""
	if isinstance(t,str):
		return t
	elif t[0] == 'var':
		assert len(t) == 2, t
		s1 = ty(t[1])
		return 'var '+s1
	elif t[0] == 'set':
		assert len(t) == 2, t
		s1 = ty(t[1])
		return 'set of '+s1
	elif t[0] == 'array':
		assert len(t) == 3, t
		s1 = ty(t[2])
		il = [ty(u) for u in t[1]]
		return f"array [{','.join(il)}] of " + s1
	elif t[0] == '..':
		assert len(t) == 3, t
		return expr(t[1]) + '..' + expr(t[2])
	else:
		assert False, t

def decl(d):
	""
	[v,t] = d
	s = f'{ty(t)}: {v}'
	return s

def expr(e):
	""
	if isinstance(e,str):
		s = e
	elif isinstance(e,int):
		s = str(e)
	elif isinstance(e, list):
		k = e[0]
		if k == '-':
			if len(e)==2:
				s = '-'+expr(e[1])
			else:
				assert False, e
		elif k == '[':
			assert len(e) == 2, e
			s = '[' + ','.join(expr(e1) for e1 in e[1]) + ']'
		elif k == '..':
			assert len(e) == 3, e
			s = expr(e[1]) + '..' + expr(e[2])
		else:
			assert False, e
	else:
		assert False, e
	return s

def annot(a):
	""
	if isinstance(a, str):
		return a
	elif isinstance(a, list):
		assert len(a)==2
		s = a[0] + '(' + ','.join(expr(e) for e in a[1]) + ')'
		return s
	else:
		assert False, a

def to_sl(l):
	""
	sl = []
	for item_i, item in enumerate(l, start=1): # fzn auto-genere : 1 item / ligne
		if not isinstance(item,list):
			assert False, item
		k = item[0]
		if k == '%':
			assert len(item)==2
			s = '%'+item[1]
		elif k == 'constraint':
			# "constraint_item : CONSTRAINT IDENT '(' expr_SEQ ')' annotation_STAR"
			# p[0] = p[1:3] + [p[4],p[6]]
			s = f"constraint {item[1]}({','.join(expr(e) for e in item[2])})"
			for a in item[3]:
				s += f":: {annot(a)}"
		elif k == 'decl':
			# var_decl_item : tid annotation_STAR
			#	| tid annotation_STAR '=' expr
			# p[0] = ['decl', id, ty, p[2], p[4] if len(p)==5 else None]
			s = ty(item[2]) + ': ' + item[1]
			for a in item[3]:
				s += f":: {annot(a)}"
			if item[-1] is not None:
				s += ' = ' + expr(item[-1])
		elif k == 'predicate':
			# predicate_item : PREDICATE IDENT '(' pred_param_tid_SEQ ')'
			s = f"predicate {item[1]}({','.join(decl(d) for d in item[2])})"
		elif k == 'solve':
			s = 'solve '
			for a in item[1]:
				s += f":: {annot(a)}"
			s += ' ' + item[2]
			if len(s) == 4:
				s += ' ' + expr(item[3])
		else:
			assert False, k
		s += ';'
		sl.append(s)
	return sl

if __name__ == "__main__":
	import glob
	import mzn_par
	fn = r'G:\audit_egnos\archi\egnos_base.fzn'
	fd = open(fn, 'r',encoding='utf-8')
	fs = fd.read()
	fd.close()
	js = mzn_par.parse_str(fs)
	sl = to_sl(js)
	for i,s in enumerate(sl):
		if i > 10:
			break
		print(s)
	fs_lines = fs.splitlines()
	assert len(fs_lines) == len(sl)
	for i, (s1,s2) in enumerate(zip(fs_lines, sl), start=1):
		if s1.replace(' ','') != s2.replace(' ',''):
			print(f'{i}: {s1} != {s2}')
			break
	
