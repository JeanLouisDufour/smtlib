from collections import OrderedDict, ChainMap
from math import frexp, log10, floor
class smtlib:
	"""
	set-logic : logic
	set-option : option_d
	declare-sort : sort_od
	
	pour tester, 3 possibilites :
	f:/software/mathsat/mathsat-5.5.2-win64-msvc/bin/mathsat.exe foo.smt2 --> renvoie une AL
	f:/software/yices/yices-2.6.0/bin/yices-smt2.exe foo.smt2             --> renvoie (= var val)* 
	f:/software/z3/z3-4.6.0-x64-win/bin/z3.exe -smt2 foo.smt2             --> renvoie (model universe* define-fun*)
	f:/software/cvc4/cvc4-1.6-win64-opt.exe --lang=smt2.6 foo.smt2        --> renvoie (model ...)
	CVC4 est special :
		QF_NIRA ne supporte pas les user-sort
		par contre QF_DTNIRA supporte (declare-datatype Color ( (red) (green ) (blue ) ))
	f:/software/cvc4/cvc4-1.6-win64-opt.exe --lang=smt2.6 foo.smt2
		(error "Parse Error: foo.smt2:3.13: Free sort symbols not allowed in QF_NIRA")
	"""
	predef_obj_d = {'false':'Bool','true':'Bool'}
	
	def __init__(self, logic=''):
		""
		self.enum_d = {} ## {'false':'Bool','true':'Bool'}
		self.non_enum_od = OrderedDict()
		self.obj_od = ChainMap(self.non_enum_od, self.enum_d)
		self.assert_l = []
		self.check_l = []
		self.get_l = []
		self.option_d = {}
		self.logic = logic
		self.predef_sort_l = ['Bool']
		if 'I' in logic:
			self.predef_sort_l.append('Int')
		if 'R' in logic:
			self.predef_sort_l.append('Real')
		if 'I' in logic and 'R' in logic:
			2+2 ## to_int, to_real, is_int
		self.sort_od = OrderedDict((s,0) for s in self.predef_sort_l)

	############
	
	def Assert(self, term):
		"'A' car 'assert' est un mot-cle"
		assert self.isTerm(term)
		self.assert_l.append(term)
	
	def checkSat(self):
		""
		self.check_l.append([])
	
	def checkSatAssuming(self, lit_l):
		""
		for lit in lit_l:
			if isinstance(lit,str):
				assert lit in self.obj_od
			else:
				foo,bar = lit
				assert foo == 'not' and bar in self.obj_od
		self.check_l.append(lit_l)
	
	def declareConst(self, symb, sort='Bool'):
		""
		assert symb not in self.obj_od, symb
		assert sort in self.sort_od, sort
		self.obj_od[symb] = sort
	
	def declareDatatype(self, symb, datatype, typevars=()):
		"RESTREINT : enum ou record"
		assert symb not in self.sort_od
		assert isinstance(datatype,(list,tuple))
		if datatype and all(isinstance(s, str) for s in datatype): ### enum
			assert typevars == ()
			for s in datatype:
				assert s not in self.enum_d and s not in ('false','true')
				self.enum_d[s] = symb
			self.sort_od[symb] = ('enum', datatype)
		elif all(isinstance(t, (list,tuple)) for t in datatype): ### record
			for fn,fs in datatype:
				assert (fn.isidentifier() or '.' in fn) and (fs in self.sort_od or fs in typevars), (fn,fs)
			self.sort_od[symb] = ('record', (typevars, datatype))
		else:
			assert False
	
	def declareFun(self, symb, sort_l, sort):
		""
		assert symb not in self.obj_od
		assert sort in self.sort_od
		assert all(s in self.sort_od for s in sort_l)
		self.obj_od[symb] = (sort_l, sort, None)
	
	def declareSort(self, symb, num=0):
		"nouvelle sort ; ne pas confondre avec define-sort"
		assert symb not in self.sort_od
		assert isinstance(num,int)
		self.sort_od[symb] = num
	
	def defineFun(self, symb, sortedVar_l, sort, term):
		assert symb not in self.obj_od, symb
		assert sort in self.sort_od
		for xn,xt in sortedVar_l:
			assert xt in self.sort_od, xt
		assert self.isTerm(term)
		self.obj_od[symb] = (sortedVar_l, sort, term)

	def defineSort(self, symb, typevars, sort_expr):
		"RESTREINT : alias ; ne pas confondre avec declare-sort"
		assert symb not in self.sort_od
		assert typevars == ()
		assert sort_expr in self.sort_od
		self.sort_od[symb] = ('alias', (typevars, sort_expr))

	def echo(self,s):
		assert self.check_l != [] and isinstance(s,str)
		self.get_l.append(['echo', '"'+s+'"'])
	
	def getModel(self):
		""
		assert self.check_l != []
		self.get_l.append(['get-model'])

	def getValue(self, sl):
		""
		assert self.check_l != [] and all(s in self.obj_od for s in sl)
		self.get_l.append(['get-value', sl])

	def setOption(self, on, ov):
		""
		self.option_d[on] = ov

	###############################
	
	def defineMax(self,n,t):
		""
		assert 2 <= n and t in self.sort_od
		pars = [('x{}'.format(i),t) for i in range(n)]
		expr = ['ite',['>', 'x{}'.format(n-1), 'm{}'.format(n-2)], 'x{}'.format(n-1), 'm{}'.format(n-2)]
		for i in reversed(range(n-1)):
			comp = 'x0' if i==0 else ['ite',['>', 'x{}'.format(i), 'm{}'.format(i-1)], 'x{}'.format(i), 'm{}'.format(i-1)]
			expr = ['let',[['m{}'.format(i),comp]], expr]
		self.defineFun('max{}'.format(n), pars, t, expr)
	
	###############################

	def isSort(self, symb):
		""
		return symb in self.sort_od

	def isObj(self, symb):
		""
		return symb in self.obj_od

	def objSort(self, symb):
		"renvoie 'Real' ou ('Int','Real')"
		r = self.obj_od.get(symb)
		if isinstance(r,tuple):
			svl, r, _term = r
			if svl:
				r = (s for n,s in  svl) + (r,)
		return r

	def isTerm(self, t):
		""
		if isinstance(t, str):
			2+2
		else:
			2+2
		return True ## TBC
	
	def assertRelation(self, rn, sl):
		""
		for s in sl:
			assert s[0] == '#' or s in self.sig_d
		self.rel_a.append((rn,sl))
	
	def to_json(self):
		""
		return {
			'prefix': self.prefix,
			'filename': self.filename,
			'sig_a': self.sig_a,
			'rel_a': self.rel_a,
			'sys_in': self.sys_in,
			'sys_out': self.sys_out,
		}
	
	def term2str(t):
		""
		if isinstance(t,str):
			s = t
		elif isinstance(t, bool):
			s = 'true' if t else 'false'
		elif isinstance(t, int):
			if t >= 0:
				s = '{}'.format(t)
			else:                        ### pour mathsat et yices
				s = '(- {})'.format(-t)
		elif isinstance(t, float):
			tabs = t if t >= 0 else -t
			l10 = log10(tabs) if tabs else 17
			if l10 >= 17:
				precision = 1
			else:
				precision = 18-floor(l10)
			precision = '{:.' + str(precision) + 'f}'
			if t >= 0:
				s = precision.format(tabs)
			else:
				s = ('(- '+precision+')').format(tabs) 
		elif isinstance(t, (list,tuple)):
			s = '(' + ' '.join(smtlib.term2str(t1) for t1 in t) + ')'
		else:
			assert False, t
		return s
	
	def z3(self, t):
		""
		ret = t
		if isinstance(t, (list,tuple)):
			if t[0] == 'match':
				_, x, [[pat,y]] = t
				constr = pat[0]
				assert constr[0] == constr[-1] == '_', t
				ty = constr[1:-1]
				assert isinstance(x,str)
				pat_expl = [z.split('.',maxsplit=1) for z in pat[1:]]
				assert all(z[0] == x for z in pat_expl), t
				# print(t)
				b = [(z, (fn, x)) for z,(_,fn) in zip(pat[1:], pat_expl)]
				y_z3 = self.z3(y)
				ret = ['let', b, y_z3]
			else:
				ret = [self.z3(x) for x in t]
		return ret
	
	def ys(self, t):
		""
		ret = t
		if isinstance(t, (list,tuple)):
			if t[0] == 'match':
				_, x, [[pat,y]] = t
				constr = pat[0]
				assert constr[0] == constr[-1] == '_', t
				ty = constr[1:-1]
				assert isinstance(x,str)
				pat_expl = [z.split('.',maxsplit=1) for z in pat[1:]]
				assert all(z[0] == x for z in pat_expl), t
				# print(t)
				b = [(z, ('select', x,i)) for i, (z,(_,fn)) in enumerate(zip(pat[1:], pat_expl), start=1)]
				y_ys = self.ys(y)
				ret = ['let', b, y_ys]
			else:
				ret = [self.ys(x) for x in t]
		return ret
	
	ae_alias = {}
	
	def ae_id(s):
		""
		alias = smtlib.ae_alias.get(s)
		if alias: return alias
		s = s.lower().replace('.',"'").replace('@',"'")
		if '*' in s:
			s = s.replace('*',"mul")
		elif '+' in s:
			s = s.replace('+',"add")
		elif '-' in s:
			s = s.replace('-',"sub")
		return s
	
	def ae_expr(t):
		""
		r = None
		if isinstance(t, (int,float)): ## cas bool a faire ; verifier que float est OK
			r = str(t)
		elif isinstance(t, str):
			if t[0].isdigit():
				r = t
			else:
				r = smtlib.ae_id(t)
		elif isinstance(t,list):
			op = t[0] # and div to_int to_real
			if op == 'let':
				_, bl, e = t
				binders = ' , '.join('{} = {}'.format(smtlib.ae_id(x),smtlib.ae_expr(y)) for x,y in bl)
				r = 'let {} in {}'.format(binders, smtlib.ae_expr(e))
			elif op == 'match':
				_, c, [[pat, e]] = t
				ty = pat[0]
				bl = [x.split('.', maxsplit=1) for x in pat[1:]]
				assert all(y == c for y,_ in bl)
				binders = ''.join('let {} = {} in '.format(smtlib.ae_id(x),y.lower()+'.'+smtlib.ae_id(f)) for x,(y,f) in zip(pat[1:],bl))
				r = '{}{}'.format(binders, smtlib.ae_expr(e))
			elif op == 'ite':
				_,c,e1,e2 = t
				r = 'if {} then {} else {}'.format(smtlib.ae_expr(c),smtlib.ae_expr(e1),smtlib.ae_expr(e2))
			elif op == '-':
				if len(t) == 2:
					r = '-({})'.format(smtlib.ae_expr(t[1]))
				else:
					r0,r1 = [smtlib.ae_expr(e) for e in t[1:]]
					r = '({}) {} ({})'.format(r0, op, r1)
			elif op in ('and','or','xor','=>'):
				if op == '=>': op = 'imp'
				rl = [smtlib.ae_expr(e) for e in t[1:]]
				if len(t) == 2:
					assert op in ('and','or')
					r = rl[0]
				elif len(t) == 3:
					r = "bool'"+op+'('+' , '.join(rl)+')'
				elif len(t) == 4:
					assert False, t
					r = "bool'"+op+'('+' , '.join(rl[1:])+')'
					r = "bool'"+op+'('+' , '.join([rl[0],r])+')'
				else:
					assert False, t
			elif op == 'not':
				assert len(t)==2
				r1 = smtlib.ae_expr(t[1])
				r = "bool'not("+r1+')'
			elif op in ('<','<=','>','>='):
				assert len(t) == 3, t
				rl = [smtlib.ae_expr(e) for e in t[1:]]
				if op == '<': op = 'lt'
				elif op == '<=': op = 'le'
				elif op == '>': op = 'gt'
				elif op == '>=': op = 'ge'
				else: assert False
				r = "bool'"+op+'('+' , '.join(rl)+')'
			elif op in ('=','distinct'):
				assert len(t) >= 3, t
				if op == '=': op = 'eq'
				elif op == 'distinct': op = 'ne'
				else: assert False 
				rl = [smtlib.ae_expr(e) for e in t[1:]]
				cl = ["bool'"+op+'('+r1+','+r2+')' for r1,r2 in zip(rl[:-1],rl[1:])]
				r = cl[0]
				for c in cl[1:]:
					r = "bool'and("+r+','+c+')'
			elif op in ('*','/','+','div','mod'):
				assert len(t) == 3 or op=='+', op ### TBC
				rl = [smtlib.ae_expr(e) for e in t[1:]]
				if op == 'div': op = '/'
				elif op == 'mod': op = '%'
				r = '({}) {} ({})'.format(rl[0], op, rl[1])
			else: ## inclus div, mod
				rl = [smtlib.ae_expr(e) for e in t[1:]]
				r = '{}({})'.format(smtlib.ae_id(op), ' , '.join(rl))
			2+2
		else:
			assert False, t
		return r
	
	solver_conf = {
		"alt-ergo": {
			"lib": "logic bool'eq, bool'ne, bool'le, bool'lt, bool'ge, bool'gt : 'a, 'a -> bool" \
				+ " logic bool'and, bool'or, bool'imp : bool, bool -> bool" \
				+ " logic bool'not : bool -> bool" \
				+ " logic to_int: real -> int logic to_real: int -> real" \
				+ " logic abs: real -> real"
			},
		"cvc4": {
			"suffix": "6",
			"options": [':produce-models'],
			},
		"yices": {},
		"z3": {
			"suffix": "z3",
			"options" : [],
			}
	}
	
	def to_file(self, f, solvers={"cvc4"}):
		""
		#sc = smtlib.solver_conf[solver]
		assert solvers <= set(smtlib.solver_conf)
		if "cvc4" in solvers:
			fn = f + '.smt26' #  + sc['suffix']
			fd = open(fn,'w')
			print('writing {}'.format(fn))
		else:
			fd = None
		if "alt-ergo" in solvers:
			fn_ae = f + '.why' #  + sc['suffix']
			fd_ae = open(fn_ae,'w')
			print('writing {}'.format(fn_ae))
		else:
			fd_ae = None
		if "z3" in solvers:
			fn_z3 = f + '.smt2z3'
			fd_z3 = open(fn_z3,'w')
			print('writing {}'.format(fn_z3))
		else:
			fd_z3 = None
		if "yices" in solvers:
			fn_ys = f + '.ys'
			fd_ys = open(fn_ys,'w')
			print('writing {}'.format(fn_ys))
		else:
			fd_ys = None
		for on in sorted(self.option_d):
			# if on not in sc['options']: continue
			ov = self.option_d[on]
			if fd: fd.write('(set-option {} {})\n'.format(on,ov))
			lib_ae = smtlib.solver_conf['alt-ergo']['lib']
			if fd_ae: fd_ae.write('{} (* (set-option {} {}) *)\n'.format(lib_ae,on,ov))
			if fd_z3: fd_z3.write('(set-option {} {})\n'.format(on,ov))
			if fd_ys: fd_ys.write('(define-type Bool bool) (define-type Int int) (define-type Real real) ;(set-option {} {})\n'.format(on,ov))
		if self.logic:
			if fd: fd.write('(set-logic {})\n'.format(self.logic))
			if fd_ae: fd_ae.write('(* (set-logic {}) *)\n'.format(self.logic))
			if fd_z3: fd_z3.write(';(set-logic {})\n'.format(self.logic))
			if fd_ys: fd_ys.write('(define to_int :: (-> Real Real) (lambda (x :: Real) (floor x))) (define to_real :: (-> Real Real) (lambda (x :: Real) x)) ;(set-logic {})\n'.format(self.logic))
		for sn, sa in self.sort_od.items():
			if sn in self.predef_sort_l: continue
			# fd.write('(declare-sort {} {})\n'.format(sn,sa))
			if isinstance(sa,int):
				s_z3 = s = '(declare-sort {} {})\n'.format(sn,sa)
				if fd: fd.write(s)
				if fd_z3: fd_z3.write(s_z3)
				assert sa==0
				if fd_ys: fd_ys.write('(define-type {})\n'.format(sn))
				if fd_ae: fd_ae.write('type {}\n'.format(smtlib.ae_id(sn)))
			else:
				kind, decl = sa
				if kind == 'enum':
					decl_str = ' '.join('({})'.format(s) for s in decl)
					decl_str_ys = decl_str_z3 = ' '.join(decl)
					pattern_ys = '(define-type {} (scalar {}))\n'
					decl_str_ae = ' | '.join(smtlib.ae_id(s) for s in decl)
					pattern_ae = 'type {} = {}\n'
				elif kind == 'record':
					tvl, decl = decl
					if len(tvl)==0:
						decl_str = ' '.join('({} {})'.format(fn,fs) for fn,fs in decl)
						decl_str_z3 = decl_str = '(_{}_ {})'.format(sn, decl_str)
						decl_str_ys = ' '.join(fs for fn,fs in decl) # ty_l
						pattern_ys = '(define-type {} (tuple {})) '
						if fd_ys: fd_ys.write(pattern_ys.format(sn, decl_str_ys))
						bs = ' '.join('{}::{}'.format(fn,fs) for fn,fs in decl)
						fs = ' '.join(fn for fn,fs in decl)
						pattern_ys = '(define _{0}_ :: (-> {1} {0}) (lambda ({2}) (mk-tuple {3})))\n'.format('{0}', '{1}', bs, fs)
						decl_str_ae = ' ; '.join('{}:{}'.format(smtlib.ae_id(fn),smtlib.ae_id(fs)) for fn,fs in decl)
						decl_str_ae = '{ '+decl_str_ae+' }'
						pattern_ae = 'type {} = {} '
						if fd_ae: fd_ae.write(pattern_ae.format(smtlib.ae_id(sn), decl_str_ae))
						pattern_ae = "logic _{0}_ : {1} -> {0}\n"
						decl_str_ae = ' , '.join(smtlib.ae_id(fs) for fn,fs in decl)
					else:
						assert False
				elif kind == 'alias':
					tvl, decl = decl
					assert decl in self.predef_sort_l or self.sort_od[decl][0] == 'enum', decl
					if len(tvl)==0:
						pass
					else:
						assert False
					s_z3 = s = '(define-sort {} () {})\n'.format(sn, decl) 
					if fd: fd.write(s)
					if fd_z3: fd_z3.write(s_z3)
					if fd_ys: fd_ys.write('(define-type {} {})\n'.format(sn, decl))
					assert sn not in smtlib.ae_alias
					smtlib.ae_alias[sn] = smtlib.ae_id(decl)
					if fd_ae: fd_ae.write('(* type {} = {} *)\n'.format(sn, smtlib.ae_id(decl)))
					continue
				else:
					assert False
				if fd: fd.write('(declare-datatype {} ({}))\n'.format(sn,decl_str))
				if fd_z3: fd_z3.write('(declare-datatypes () (({} {})))\n'.format(sn,decl_str_z3))
				if fd_ys: fd_ys.write(pattern_ys.format(sn, decl_str_ys))
				if fd_ae: fd_ae.write(pattern_ae.format(smtlib.ae_id(sn), decl_str_ae))
		for on, ov in self.non_enum_od.items(): # self.obj_od.items():
			if isinstance(ov, str):
				s_z3 = s = '(declare-const {} {})\n'.format(on,ov)
				if fd: fd.write(s)
				if fd_z3: fd_z3.write(s_z3)
				if fd_ys: fd_ys.write('(define {} :: {})\n'.format(on,ov))
				if fd_ae: fd_ae.write('logic {} : {}\n'.format(smtlib.ae_id(on),smtlib.ae_id(ov)))
			else:
				pl, sort, t = ov
				if t != None:
					pl_s = smtlib.term2str(pl)
					t_s = smtlib.term2str(t)
					s = '(define-fun {} {} {} {})\n'.format(on,pl_s,sort,t_s)
					t_z3 = self.z3(t)
					t_z3_s = smtlib.term2str(t_z3)
					s_z3 = '(define-fun {} {} {} {})\n'.format(on,pl_s,sort,t_z3_s)
					t_ys = self.ys(t)
					t_ys_s = smtlib.term2str(t_ys)
					if pl:
						tl_s = ' '.join([t for _,t in pl]+[sort])
						pl_ys_s = ' '.join('{} :: {}'.format(pn,ps) for pn,ps in pl)
						s_ys = '(define {} :: (-> {}) (lambda ({}) {}))\n'.format(on, tl_s, pl_ys_s, t_ys_s)
					else:
						s_ys = '(define {} :: {} {})\n'.format(on, sort, t_ys_s)
					pl_ae_s = ' , '.join('{} : {}'.format(pn.lower(),smtlib.ae_id(ps)) for pn,ps in pl)
					s_ae = 'function {} ({}) : {} = {}\n'.format(smtlib.ae_id(on), pl_ae_s, smtlib.ae_id(sort), smtlib.ae_expr(t))
					if fd: fd.write(s)
					if fd_z3: fd_z3.write(s_z3)
					if fd_ys: fd_ys.write(s_ys)
					if fd_ae: fd_ae.write(s_ae)
				else:
					assert False
					sl_s = smtlib.term2str(pl)
					s_z3 = s = '(declare-fun {} {} {})\n'.format(on,sl_s,sort)
					if fd: fd.write(s)
					if fd_z3: fd_z3.write(s_z3)
		for a in self.assert_l:
			s_ys = s_z3 = s = '(assert {})\n'.format(smtlib.term2str(a))
			if fd: fd.write(s)
			if fd_z3: fd_z3.write(s_z3)
			if fd_ys: fd_ys.write(s_ys)
		for c in self.check_l:
			if c:
				assert False
			else:
				if fd: fd.write('(check-sat)\n')
				if fd_z3: fd_z3.write('(check-sat)\n')
				if fd_ys: fd_ys.write('(check)\n')
				# ae ?
		for g in self.get_l:
			k = g[0]
			if k == 'get-model':
				[_] = g
				if fd: fd.write('(get-model)\n')
				if fd_z3: fd_z3.write('(get-model)\n')
				if fd_ys: fd_ys.write('(show-model)\n')
				if fd_ae: fd_ae.write('goal G1: true\n')
			elif k == 'echo':
				_,s = g
				if fd: fd.write('(echo {})\n'.format(s))
				if fd_z3: fd_z3.write('(echo {})\n'.format(s))
				if fd_ys: fd_ys.write('(echo {})\n'.format(s))
				if fd_ae: fd_ae.write('(echo {})\n'.format(s))
			elif k == 'get-value':
				_,sl = g
				if fd: fd.write('(get-value ({}))\n'.format(' '.join(sl)))
				if fd_z3: fd_z3.write('(get-value ({}))\n'.format(' '.join(sl)))
				if fd_ys: fd_ys.write('(get-value ({}))\n'.format(' '.join(sl)))
				if fd_ae: fd_ae.write('(get-value ({}))\n'.format(' '.join(sl)))
			else:
				assert False, k
		if fd: fd.close()
		if fd_ae: fd_ae.close()
		if fd_z3: fd_z3.close()
		if fd_ys: fd_ys.close()
	
################
