import io, json, os, re, sys, time

re_tok = re.compile(r'\s+|\(|\)|"[^"]*"|[#&]?\w+|-\d+|;.*')
### remplace .isidentifier() en Py2 (sachant que ce n'est pas un nombre)
re_identifier = re.compile(r'^\w+$',re.UNICODE)

def read(fn):
	"fn est soit un nom de fichier, soit un descripteur"
	if isinstance(fn, str):
		fd = open(fn, 'r')
	else:
		fd = fn
	t = time.time()
	stack = []
	current = []
	for linenum, line in enumerate(fd, start=1): # tokens = re_sep.split(line) # re.split('(\s+|\(|\)|"[^"]*")', line)
		#tokens = re.findall(r'(\s+|\(|\)|"[^"]*"|\w+)', line)
		tokens = re_tok.findall(line)
		if sum(len(t) for t in tokens) != len(line):
			print(line)
			print(tokens)
			assert False, str(linenum)
		for tok in tokens:
			if tok.isspace() or tok[0]==';': continue
			if tok == '(':
				stack.append(current)
				current = []
			elif tok == ')':
				c = current
				current = stack.pop()
				current.append(c)
			elif tok[0] == '"':
				assert tok[-1] == '"'
				current.append(tok)
			elif tok[0] == '-' or tok.isnumeric():
				current.append(int(tok))
			elif tok.startswith('#b'):
				assert all(c in '01' for c in tok[2:])
				current.append(tok)
			else:
				if tok[0] == '&':
					assert re_identifier.match(tok[1:]) # tok[1:].isidentifier()
				else:
					assert re_identifier.match(tok), tok # tok.isidentifier()
				current.append(tok)
	
	assert stack == []
	assert len(current) == 1
	print('{} lignes en {} secs'.format(linenum, time.time() - t))
	if isinstance(fn, str):
		fd.close()
	return current[0]

if __name__ == "__main__":
	read('../ML/d4_n067.txt')