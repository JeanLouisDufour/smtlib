from smtlib import smtlib

smtobj = smtlib('QF_BV')
smtobj.setOption(':produce-models','true')

smtobj.defineFun('foo',[],('_','BitVec',3),'#b001')
smtobj.Assert(['=','#b1',[['_', 'extract', 0, 0],'foo']])
smtobj.Assert(['=','#b00',[['_', 'extract', 2, 1],'foo']])
smtobj.Assert(['=','#b100',['bvmul','#b010','#b010']])
			   
smtobj.declareConst('x',('_','BitVec',3))
smtobj.declareConst('y',('_','BitVec',3))
smtobj.declareConst('z',('_','BitVec',3))
# assoc : x(y+z) = xy+xz
smtobj.defineFun('xy',[],('_','BitVec',6), ('bvmul',('concat','#b000','x'),('concat','#b000','y')))
smtobj.defineFun('xz',[],('_','BitVec',6), ('bvmul',('concat','#b000','x'),('concat','#b000','z')))
smtobj.defineFun('xyPxz',[],('_','BitVec',7), ('bvadd',('concat','#b0','xy'),('concat','#b0','xz')))
smtobj.defineFun('yPz',[],('_','BitVec',4), ('bvadd',('concat','#b0','y'),('concat','#b0','z')))
smtobj.defineFun('x_yPz',[],('_','BitVec',7), ('bvmul',('concat','#b0000','x'),('concat','#b000','yPz')))
smtobj.Assert(['=', 'xyPxz', 'x_yPz'])
			 
smtobj.checkSat()

smtobj.to_file('bv_test')
