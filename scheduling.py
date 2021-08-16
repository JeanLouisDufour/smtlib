"""
chaque data a AU PLUS UN producteur :
- si elle a un producteur, elle est CO-LOCALISEE avec lui
- si non, soit sa loc est libre, soit elle est forcée

variables generees :
Dd_producer : [F]

"""

functions = {
"F1": [30, ["D2", "D3"],["D4","D6"]],
"F2": [20, [],[]],
}
datas = {
"D2" : 10,
"D3" : 5,
"D4" : 3,
}

