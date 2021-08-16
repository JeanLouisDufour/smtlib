# http://optimathsat.disi.unitn.it/pages/fznreference.html

opti = { # fully supported
		 'array_bool_and', 'array_bool_element', 'array_bool_or', 'array_bool_xor', 
		 'array_float_element', 'array_int_element', 'array_set_element', 
		 'array_var_bool_element', 'array_var_float_element', 'array_var_int_element', 
		 'array_var_set_element', 'bool_and', 'bool_clause', 'bool_eq', 'bool_eq_reif', 
		 'bool_le', 'bool_le_reif', 'bool_lin_eq', 'bool_lin_le', 'bool_lt', 'bool_lt_reif', 
		 'bool_not', 'bool_or', 'bool_xor', 'float_abs', 'float_eq', 'float_eq_reif', 
		 'float_le', 'float_le_reif', 'float_lt', 'float_lt_reif', 'float_max', 'float_min', 
		 'float_ne', 'float_ne_reif', 'float_plus', 'float_times', 'float_div', 'int_abs',
		 'int_eq', 'int_eq_reif', 'int_le', 'int_le_reif', 'int_lt', 'int_lt_reif', 'int_max',
		 'int_min', 'int_ne', 'int_ne_reif', 'int_plus', 'set_card', 'set_diff', 'set_eq',
		 'set_eq_reif', 'set_in', 'set_in_reif', 'set_intersect', 'set_le', 'set_lt', 'set_ne',
		 'set_ne_reif', 'set_subset', 'set_subset_reif', 'set_symdiff', 'set_union', 'bool2int', 
		 'int2tfloat',
		 # supported only as long as no non-linearity is introduced
		 'ind_div', 'int_mod', 'int_times', 'int_lin_eq', 'int_lin_eq_reif', 'int_lin_le',
		 'int_lin_le_reif', 'int_lin_ne', 'int_lin_ne_reif', 'float_lin_eq', 
		 'float_lin_eq_reif', 'float_lin_le', 'float_lin_le_reif', 'float_lin_lt', 
		 'float_lin_lt_reif', 'float_lin_ne', 'float_lin_ne_reif'
}

opti2 = { # OptiMathSAT has an optional special handling for some global constraints:
		 'among', 'alldifferent_except_0', 'alldifferent_int', 'alldifferent_set', 
		 'at_least_int', 'at_least_set', 'at_most_int', 'at_most_set', 'atmost1', 'count_eq', 
		 'count_geq', 'count_gt', 'count_leq', 'count_lt', 'count_neq', 'exactly_int', 
		 'exactly_set'
}

	
constraints = set()
predicates = set()

if __name__ == "__main__":
	import glob
	import mzn_par
	fn = r'G:\audit_egnos\archi\egnos_base.fzn'
	fd = open(fn, 'r',encoding='utf-8')
	fs = fd.read()
	fd.close()
	js = mzn_par.parse_str(fs)
	for item_i,item in enumerate(js):
		k = item[0]
		p = item[1]
		if k == 'constraint':
			constraints.add(p)
		elif k == 'predicate':
			predicates.add(p)
			
	assert predicates <= constraints, predicates-constraints
	constraints_imp = {p for p in constraints if p.endswith('_imp')}
	constraints_new = (constraints - constraints_imp) | {p[:-3]+'reif' for p in constraints_imp}
	constraints_ok = constraints_new & opti
	print(constraints_ok)
	constraints_ko = constraints_new - opti
	print(constraints_ko)
		