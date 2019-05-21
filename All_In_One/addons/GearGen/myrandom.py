#simple private pseudo random generator

_ri = 5
def seed(s):
    global _ri
    _ri = abs(int(s*(1<<15))) & ((1<<15)-1)
    
def random():
    global _ri
    
    _ri = (_ri*2342131 + 123242354) & ((1<<15)-1)
    return _ri / (1<<15)
