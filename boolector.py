import lisp
import numpy as np

def bvu2int(bv):
	""
	assert bv.startswith('#b')
	return int('0b'+bv[2:],2)

assert bvu2int('#b000') == 0
assert bvu2int('#b111') == 7
	
def bvs2int(bv):
	""
	assert bv.startswith('#b')
	v = int('0b'+bv[2:],2)
	if bv[2] == '1':
		nb = len(bv)-2
		assert (1 << (nb-1)) <= v < (1<<nb)
		v -= (1<<nb)
	return v

assert bvs2int('#b000') == 0
assert bvs2int('#b011') == 3
assert bvs2int('#b111') == -1
assert bvs2int('#b100') == -4
			  
if __name__ == "__main__":
	js = lisp.read('../ML/d8_n067532.txt')
	outputs = []
	for n,bv in js:
		if n[0] == 's':
			v = bvs2int(bv)
			print((n,v))
			outputs.append(v)
		elif n[0] == 'n':
			assert bv.startswith('#b')
			if any(c!='0' for c in bv[2:]):
				v = bvu2int(bv)
				print((n,v))
		else:
			assert False
	assert len(outputs) == 10
	print('argmax : {}'.format(np.argmax(outputs)))
		