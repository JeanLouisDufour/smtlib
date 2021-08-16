### minizinc file : utf-8

import ply.lex as lex

fatal_error = False

literals = "$=><+-*/^:,;[](){}|"  # . ne passe pas au parsing # on vire '

reserved = {k:k.upper() for k in [
	"annotation",
	"array",
	"constraint",
	"diff",
	"div",
	"enum",
	"function",
	"in",
	"include",
	"intersect",
	"list",
	"maximize",
	"minimize",
	"mod",
	"not",
	"of",
	"opt",
	"output",
	"par",
	"predicate",
	"set",
	"satisfy",
	"solve",
	"subset",
	"superset",
	"symdiff",
	"test",
	"union",
	"var",
	"where",
	"xor",
]}

tokens = (
	'IDENT', 'USER_OP',
	'INT',
	'FLOAT', 'STRING',
	
	'AND', 'OR', 'LSBBAR', 'BARRSB',
	
	'COCO', 'DOT', 'DOTDOT', 'EQEQ','GTEQ', 'LTEQ',
	'LTMI', 'LTMIGT', 'MIGT',
	'NEQ',
	'PLPL',
	) \
	+ tuple(reserved.values())

t_OR = r'\\\/'
t_AND = '\\/\\\\'

t_COCO = r'::'
t_DOT = r'\.'
t_DOTDOT = r'\.\.'
t_EQEQ = r'=='
t_GTEQ = r'>='
t_LTEQ = r'<='
t_LTMI = r'<-'
t_LTMIGT = r'<->'
t_MIGT = r'->'
t_NEQ = r'!='
t_PLPL = r'\+\+'

t_LSBBAR = r'\[\|'
t_BARRSB = r'\|\]'

# t_ignore_space = r'\s+' # '[ \t]+'  ## \r pour Py27
## cette regle a masque SP CR LF
def t_space(t):
	r'\s+'
	tv = t.value
	t.lexer.lineno += tv.count('\n') + tv.count('\r') - tv.count('\r\n')

def t_comment(t):
	r'/\*(.|\n)*?\*/'
	tv = t.value
	t.lexer.lineno += tv.count('\n') + tv.count('\r') - tv.count('\r\n')

def t_comment_2(t):
	r'%.*'
	pass

def t_comment_3(t):
	r'//.*'
	pass
 
# track line numbers
# def t_newline(t):
	# r'\n'
	# t.lexer.lineno += 1 # len(t.value)

# def t_newline_2(t):
	# r'\r\n'
	# t.lexer.lineno += 1 # len(t.value)

# def t_abbrev1(t):
# 	r's\.|subj\ '
# 	t.type = 'SUBJECT'
# 	return t

# def t_abbrev2(t):
#  	r't\.'
#  	t.type = 'TO'
#  	return t

def t_IDENT(t):
	r'[a-zA-Z_][a-zA-Z_0-9]*'
	t.type = reserved.get(t.value,'IDENT')
	return t

def t_USER_OP(t):
	r'`[a-zA-Z_][a-zA-Z_0-9]*`'
	return t

def t_FLOAT(t):
	r'\d*\.\d+([eE][+-]?\d+)?'
	t.value = float(t.value)
	return t

def t_FLOAT2(t):
	r'\d+\.(?!\.)' # r'\d+\.\s'
	# voir le regex-howto 'Negative lookahead assertion'
	t.type = 'FLOAT'
	return t

def t_INT(t):
	r'\d+'
	t.value = int(t.value)
	return t

def t_STRING(t):
	r'"[^"]*"'
	return t

def t_STRING2(t):
	r"'[^']*'"
	t.type = "STRING"
	return t

def t_error(t):
	ch = t.value[0]
	if fatal_error:
		assert False, (ch, ord(ch))
	else:
		print("********* Bad char '{}' ({}) ************".format(ch, ord(ch)))
		t.lexer.skip(1)
	
lexer = lex.lex(optimize=0)
#lexer = lex.lex(optimize=0, reflags=re.UNICODE | re.VERBOSE)

if __name__ == '__main__':
	s = """
/***
!Test
expected:
- !Result
  solution: !Solution
    puzzle:
    - [5, 9, 3, 7, 6, 2, 8, 1, 4]
    - [2, 6, 8, 4, 3, 1, 5, 7, 9]
    - [7, 1, 4, 9, 8, 5, 2, 3, 6]
    - [3, 2, 6, 8, 5, 9, 1, 4, 7]
    - [1, 8, 7, 3, 2, 4, 9, 6, 5]
    - [4, 5, 9, 1, 7, 6, 3, 2, 8]
    - [9, 4, 2, 6, 1, 8, 7, 5, 3]
    - [8, 3, 5, 2, 4, 7, 6, 9, 1]
    - [6, 7, 1, 5, 9, 3, 4, 8, 2]
***/

%
%-----------------------------------------------------------------------------%
% Sudoku for squares of arbitrary size N = (S x S)
%-----------------------------------------------------------------------------%

int: S;
int: N = S * S;


array[1..N,1..N] of var 1..N: puzzle;


include "alldifferent.mzn";

    % All cells in a row, in a column, and in a subsquare are different.
constraint
    forall(i in 1..N)( alldifferent(j in 1..N)( puzzle[i,j] ))
    /\
    forall(j in 1..N)( alldifferent(i in 1..N)( puzzle[i,j] ))
    /\
    forall(i,j in 1..S)
        ( alldifferent(p,q in 1..S)( puzzle[S*(i-1)+p, S*(j-1)+q] ));


solve satisfy;


output [ "sudoku:\n" ] ++
    [ show(puzzle[i,j]) ++
        if j = N then
            if i mod S = 0 /\ i < N then "\n\n" else "\n" endif
        else
            if j mod S = 0 then "  " else " " endif
        endif
    | i,j in 1..N ];

%-----------------------------------------------------------------------------%
%
% The data for the puzzle that causes satz to make 1 backtrack (normally none
% are made).
%

S=3;
puzzle=[|
_, _, _, _, _, _, _, _, _|
_, 6, 8, 4, _, 1, _, 7, _|
_, _, _, _, 8, 5, _, 3, _|
_, 2, 6, 8, _, 9, _, 4, _|
_, _, 7, _, _, _, 9, _, _|
_, 5, _, 1, _, 6, 3, 2, _|
_, 4, _, 6, 1, _, _, _, _|
_, 3, _, 2, _, 7, 6, 9, _|
_, _, _, _, _, _, _, _, _|
|];
"""
	lexer.input(s)
	#for i in range(15):
	#	print(lexer.token())
	#for t in lexer:
	#	print(t)
	l = list(lexer)

	import glob
	for f in glob.glob(r"C:\Users\F074018\Documents\optim\libminizinc-master\tests\**\*.[mdf]zn", recursive=True):
		print(f)
		fd = open(f,'r',encoding='utf8')
		s = fd.read()
		fd.close()
		lexer.input(s)
		l = list(lexer)
		