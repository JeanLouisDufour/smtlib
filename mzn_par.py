import ply.yacc as yacc
import ply2yacc
import functools
# tokens : Get the token map from the lexer.  This is required.
# lexer : permit to force yacc to use the good lexer (in case of multiple parsers)
from mzn_lex import tokens, lexer

################

def make_seq_lr(p):
	""
	lp = len(p)
	if lp >= 3:
		p[1].append(p[lp-1])
		p[0] = p[1]
	elif lp >= 2:
		p[0] = [p[1]]
	else:
		p[0] = []
		
def make_seq_rr(p):
	""
	lp = len(p)
	if lp >= 3:
		p[0] = [p[1]]+p[lp-1]
	elif lp >= 2:
		p[0] = [p[1]]
	else:
		p[0] = []


def warning(s):
	print(s)

def flatten(ll):
	"[[1,2],[],[3,4]] ->  [1,2,3,4]"
	l = functools.reduce(lambda a, l: a+l, ll, [])
	return l	

start = 'model'  ## renvoie ...

dbg_print = print
dbg_print = lambda x: None

#######################################

def p_ann_expr(p):
	"""ann_expr : expr"""
	#
	"""ann_expr : IDENT
				| IDENT '(' expr_SEQ ')'
				| '[' expr_SEQ ']'
	"""
	p[0] = p[1]

def p_annotation(p):
	"""annotation : COCO IDENT
	| COCO IDENT '(' ann_expr_SEQ ')'
	"""
	p[0] = p[2] if len(p)==3 else [p[2],p[4]]

def p_annotation_item(p):
	"annotation_item : ANNOTATION"
	assert False

def p_array_ty_expr(p):
	"""array_ty_expr : ARRAY '[' ty_expr_SEQ ']' OF base_ty_expr
					| LIST OF base_ty_expr
	"""
	p[0] = ['list', p[3]] if len(p)==4 else ['array', p[3], p[6]]

def p_assign_item(p):
	"assign_item : IDENT '=' expr"
	p[0] = ['=', p[1], p[3]]

def p_base_ty_expr(p):
	"base_ty_expr : EITHER_VAR_OR_PAR_OPT OPT_OPT SET_OF_OPT base_ty_expr_tail"
	assert p[2] == None
	tmp = p[4]
	if p[3] is not None:
		tmp = ['set', tmp]
	if p[1] == 'var':
		tmp = ['var', tmp]
	p[0] = tmp

def p_base_ty_expr_tail(p):
	"""base_ty_expr_tail : IDENT
						| '$' IDENT
						| '{' expr_SEQ '}'
						| expr_unary DOTDOT expr_unary
	"""
	p[0] = p[1] if len(p)==2 else \
		p[1:] if len(p) == 3 else \
		p[1:3] if p[1] == '{' else \
		['..',p[1],p[3]]

def p_constraint_item(p):
	"constraint_item : CONSTRAINT IDENT '(' expr_SEQ ')' annotation_STAR"
	p[0] = p[1:3] + [p[4],p[6]]

def p_enum_item(p):
	"enum_item : ENUM IDENT '=' expr" # { id1, ... }
	pass

def p_expr(p):
	"""expr : expr_unary
			| expr_unary DOTDOT expr_unary
	"""
	p[0] = p[1] if len(p)==2 else ['..',p[1],p[3]]

def p_expr_unary(p):
	"""expr_unary : expr_atom
				| '-' expr_atom
	"""
	p[0] = p[1] if len(p)==2 else p[1:]

def p_expr_atom(p):
	"""expr_atom : IDENT
	| INT
	| FLOAT
	| STRING
	| '(' expr_SEQ ')'
	| '[' expr_SEQ_OPT ']'
	| '{' expr_SEQ_OPT '}'
	| IDENT '(' expr_SEQ ')'
	| IDENT '[' expr_SEQ ']'
	| LSBBAR expr_SEQ_SEQ BARRSB
	"""
	p[0] =  p[1] if len(p)==2 else \
			p[1:3] if len(p)==4 else \
			['.(.',p[1],p[3]] if p[2] == '(' else \
			['.[.',p[1],p[3]]

def p_function_item(p):
	"function_item : FUNCTION"
	assert False

def p_include_item(p):
	"include_item : INCLUDE STRING"
	p[0] = p[1:]

def p_index(p):
	"""index : INT DOTDOT INT
				| IDENT
	"""
	p[0] = p[1] if len(p)==2 else ['..', p[1],p[3]]

def p_item(p):
	"""item : include_item
          | var_decl_item
          | enum_item
          | assign_item
          | constraint_item
          | solve_item
          | output_item
          | predicate_item
          | test_item
          | function_item
          | annotation_item
	"""
	p[0] = p[1]

def p_model(p):
	"""model : item_SCSEQ
			|  item_SCSEQ ';'
	"""
	p[0] = p[1]

def p_output_item(p):
	"output_item : OUTPUT"
	assert False

def p_pred_param_tid(p):
	"pred_param_tid : pred_param_type ':' IDENT"
	p[0] = [p[3],p[1]]

def p_pred_param_type(p):
	"""pred_param_type : pred_param_type_basic
				| ARRAY '[' index_SEQ ']' OF pred_param_type_basic
	
	"""
	p[0] = p[1] if len(p)==2 else ['array', p[3], p[6]]

def p_pred_param_type_basic(p):
	"""pred_param_type_basic : IDENT
							| SET OF IDENT
							| VAR IDENT
							| VAR SET OF IDENT
	"""
	p[0] =  p[1] if len(p)==2 else \
			p[1:] if len(p)==3 else \
			[p[1],p[3]] if len(p)==4 else \
			['var',['set',p[4]]]

def p_predicate_item(p):
	"predicate_item : PREDICATE IDENT '(' pred_param_tid_SEQ ')'"
	p[0] = [p[1], p[2], p[4]]

def p_solve_item(p):
	"""solve_item : SOLVE annotation_STAR SATISFY
				| SOLVE annotation_STAR MAXIMIZE expr
				| SOLVE annotation_STAR MINIMIZE expr
	"""
	p[0] = p[1:]

def p_test_item(p):
	"test_item : TEST"
	assert False

def p_tid(p):
	"tid : ty_expr ':' IDENT"
	p[0] = p[1:]

def p_ty_expr(p):
	"""ty_expr : base_ty_expr
				| array_ty_expr
	"""
	p[0] = p[1]

def p_var_decl_item(p):
	"""var_decl_item : tid annotation_STAR
				| tid annotation_STAR '=' expr
	"""
	[ty,_,id] = p[1]
	p[0] = ['decl', id, ty, p[2], p[4] if len(p)==5 else None]

	
######## auto #############

def p_ann_expr_SEQ(p):
	"""ann_expr_SEQ : ann_expr
	| ann_expr_SEQ ',' ann_expr
	"""
	make_seq_lr(p)

def p_annotation_STAR(p):
	"""annotation_STAR : 
		| annotation_STAR annotation
	"""
	make_seq_lr(p)

def p_COMMA_OPT(p):
	"""COMMA_OPT :
		| ','
	"""
	p[0] = p[1] if len(p) > 1 else None

def p_EITHER_VAR_OR_PAR(p):
	"""EITHER_VAR_OR_PAR : VAR
						| PAR
	"""
	p[0]= p[1]

def p_EITHER_VAR_OR_PAR_OPT(p):
	"""EITHER_VAR_OR_PAR_OPT :
		| EITHER_VAR_OR_PAR
	"""
	p[0] = p[1] if len(p) > 1 else None

def p_expr_SEQ(p):
	"""expr_SEQ : expr
	| expr_SEQ ',' expr
	"""
	make_seq_lr(p)

def p_expr_SEQ_OPT(p):
	"""expr_SEQ_OPT :
		| expr_SEQ
	"""
	p[0] = p[1] if len(p) > 1 else []

# def p_expr_SEQ_SEQ(p):
# 	"""expr_SEQ_SEQ : expr_SEQ
# 		| expr_SEQ_SEQ '|' expr_SEQ
# 		| expr_SEQ_SEQ ',' '|' expr_SEQ
# 	"""
# 	make_seq_lr(p)

### la recursion gauche n'arrive pas a traiter :
### libminizinc-master\docs\es\examples\simple-prod-planning-data_es.dzn
"""
consumption= [| 250, 2, 75, 100, 0,
              | 200, 0, 150, 150, 75 |];
"""

def p_expr_SEQ_SEQ(p):
	"""expr_SEQ_SEQ : expr_SEQ
		| expr_SEQ '|' expr_SEQ_SEQ
		| expr_SEQ ',' '|' expr_SEQ_SEQ
	"""
	make_seq_rr(p)
	
def p_index_SEQ(p):
	"""index_SEQ : index
				| index_SEQ ',' index
	"""
	make_seq_lr(p)

def p_item_SCSEQ(p):
	"""item_SCSEQ :   item
					| item_SCSEQ ';' item
	"""
	make_seq_lr(p)

def p_OPT_OPT(p):
	"""OPT_OPT :
		| OPT
	"""
	p[0] = p[1] if len(p) > 1 else None

def p_pred_param_tid_SEQ(p):
	"""pred_param_tid_SEQ : pred_param_tid
	| pred_param_tid_SEQ ',' pred_param_tid
	"""
	make_seq_lr(p)

def p_SET_OF(p):
	"SET_OF : SET OF"
	p[0] = p[1]
	
def p_SET_OF_OPT(p):
	"""SET_OF_OPT : 
		| SET_OF
	"""
	p[0] = p[1] if len(p) > 1 else None

def p_ty_expr_SEQ(p):
	"""ty_expr_SEQ : ty_expr
					| ty_expr_SEQ  ',' ty_expr
	"""
	make_seq_lr(p)














#############################################
# Error rule for syntax errors
def p_error(p):
	# p est un ply.lex.LexToke,
	print('Syntax error at token ' + str(p))
	print('parser.symstack : ' + str(parser.symstack))
	print('parser.statestack : ' + str(parser.statestack))
	assert False

############################################
import json, time
def to_json(fn, js_file=None):
	""
	print('PARSING '+fn)
	t0 = time.time()
	fd = open(fn, 'r') # codecs.open(fn, 'r')
	prg = fd.read()
	fd.close()
	t1 = time.time()
	print(t1-t0)
	try:
		lexer.lineno = 1
		result = parser.parse(prg, lexer)
	except:
		### exception dans une action
		result = None
		print("BEGIN DUMP")
		print('parser.symstack : ' + str(parser.symstack))
		print('parser.statestack : ' + str(parser.statestack))
		print("END DUMP")
		raise
	t2 = time.time()
	print(t2-t1)
	if js_file == None:
		js_file = fn+'.json'
	print('SAVING '+js_file)
	fd = open(js_file, 'w')
	json.dump(result, fd, indent='\t')
	fd.close()
	t3 = time.time()
	print(t3-t2)
	return result
	
# Build the parser
parser = yacc.yacc(optimize=0, debug=False)
ply2yacc.yacc(optimize=0, debug=False)

def parse_str(s):
	""
	lexer.lineno = 1
	result = parser.parse(s, debug = False)
	return result

def parse_file(fn, save_json = False, data=False):
	""
	print('**  {}  **'.format(fn))
	encoding = 'utf-8'
	fd = open(fn, 'r',encoding=encoding)
	s = fd.read()
	fd.close()
	if s == "": # flatzinc_from_ortools\map2.fzn
		js = []
	else:
		js = parse_str(s)
	return js
	
if __name__ == "__main__":
	import glob
	i = 0
	#for fn in glob.glob(r"C:\Users\F074018\Documents\optim\libminizinc-master\tests\**\*.[f]zn", recursive=True):
	for fn in glob.glob(r"C:\Users\F074018\Documents\optim\**\*.[fd]zn", recursive=True):
		if fn.endswith((r'\egnos.fzn',r'\egnos_serie3f.dzn')):
			continue
		result = parse_file(fn)
		i += 1
		if i >= 1e9:
			break
